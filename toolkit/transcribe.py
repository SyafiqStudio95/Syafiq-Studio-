#!/usr/bin/env python3
"""Transcribe clips for a cut-down edit: full transcript, measured pauses, and a
per-phrase transcript whose boundaries sit exactly on the real pauses.

    python3 -I toolkit/transcribe.py <project dir> [--lang ms] [--prompt "names, terms"]

Reads <project>/assets/video/c*.mp4 (from toolkit/prep.sh) and writes to <project>/transcript/:
  whisper_full.json   Whisper large-v3, word timestamps (words drift ~0.3-0.5 s: do not cut on them)
  pauses.json         quiet runs >= 0.22 s from a 20 ms energy envelope (noise floor + 35% of range)
  chunks.json / chunks.txt   each speech run between pauses transcribed on its own -> cut on these

Read chunks.txt before cutting. Known Whisper failures to look for:
  * "Terima kasih kerana menonton" / "Thank you for watching" over silence or room tone
  * news-like sentences ("Berita terkini ...") over a repeated or mumbled line
  * a 0.2-0.3 s chunk carrying a long phrase: usually an "emm" or breath (check its spectrum)
Needs: pip install faster-whisper ; hosts huggingface.co plus its CDNs (us.aws.cdn.hf.co ...).
"""
import argparse, glob, json, os, subprocess, wave
import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--lang", default="ms")
ap.add_argument("--prompt", default="")
ap.add_argument("--model", default="large-v3")
a = ap.parse_args()
P = os.path.abspath(a.project)
T = os.path.join(P, "transcript"); os.makedirs(os.path.join(T, "audio"), exist_ok=True)

def load(w):
    with wave.open(w) as f:
        return np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768

clips = sorted(glob.glob(os.path.join(P, "assets/video/c*.mp4")), key=lambda p: int(os.path.basename(p)[1:-4]))
wavs = {}
for c in clips:
    k = os.path.basename(c)[:-4]
    w = os.path.join(T, "audio", k + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c, "-vn", "-ac", "1", "-ar", "16000", w], check=True)
    wavs[k] = w

m = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
full, pauses, chunks, lines = {}, {}, {}, []
for k, w in wavs.items():
    x = load(w); dur = len(x) / 16000
    # 1. full pass
    segs, _ = m.transcribe(x, language=a.lang, word_timestamps=True, beam_size=5, initial_prompt=a.prompt or None)
    full[k] = [{"start": s.start, "end": s.end, "text": s.text,
                "words": [{"w": q.word, "s": q.start, "e": q.end} for q in s.words]} for s in segs]
    # 2. pauses from the energy envelope
    hop = 320; n = len(x) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-10))
    db = np.convolve(db, np.ones(3) / 3, "same")
    floor, speech = np.percentile(db, 10), np.percentile(db, 90)
    quiet = db < floor + 0.35 * (speech - floor)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.02 >= 0.22: runs.append((round(i * 0.02, 2), round(j * 0.02, 2)))
            i = j
        else:
            i += 1
    silent_clip = speech - floor < 6  # no speech at all: b-roll with room tone
    pauses[k] = {"floor_db": float(floor), "speech_db": float(speech), "pauses": runs, "silent": bool(silent_clip)}
    # 3. one transcription per speech run
    edges = [0.0] + [v for r in runs for v in r] + [dur]
    res, prev = [], ""
    lines.append(f"===== {k}  ({dur:.1f}s){'  [no speech: b-roll]' if silent_clip else ''}")
    if not silent_clip:
        for s0, s1 in [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2) if edges[i + 1] - edges[i] > 0.12]:
            seg = x[int(max(0, s0 - 0.05) * 16000):int(min(dur, s1 + 0.05) * 16000)]
            ss, _ = m.transcribe(seg, language=a.lang, beam_size=5, condition_on_previous_text=False,
                                 initial_prompt=((a.prompt + ". ") if a.prompt else "") + prev[-120:])
            txt = " ".join(s.text.strip() for s in ss)
            res.append({"a": s0, "b": s1, "text": txt}); prev += " " + txt
            lines.append(f"{s0:7.2f}-{s1:7.2f} | {txt}")
    chunks[k] = res
    print(f"{k}: {len(res)} chunks", flush=True)

json.dump(full, open(os.path.join(T, "whisper_full.json"), "w"), ensure_ascii=False, indent=1)
json.dump(pauses, open(os.path.join(T, "pauses.json"), "w"), indent=1)
json.dump(chunks, open(os.path.join(T, "chunks.json"), "w"), ensure_ascii=False, indent=1)
open(os.path.join(T, "chunks.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
print("wrote", os.path.relpath(T))
