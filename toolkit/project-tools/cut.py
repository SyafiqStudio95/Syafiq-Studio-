#!/usr/bin/env python3
"""Bake the A-roll: each run of consecutive cuts from one source becomes
assets/video/aroll_r<N>.mp4, with 12 ms audio fades at every cut so the
jump cuts don't click. Run after editing the `edl` in edit.json:

    python3 tools/cut.py && python3 tools/build.py
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(ROOT, "edit.json"), encoding="utf8"))
FPS = 30


def fr(t):
    return round(round(t * FPS) / FPS, 4)


runs = []
for s in E["edl"]:
    if runs and runs[-1][0] == s["src"]:
        runs[-1][1].append(s)
    else:
        runs.append((s["src"], [s]))

# optional smooth LUT baked into the footage (see tools/make_lut.py); "bakedLut": null for none
LUT = E["grade"].get("bakedLut")
VF_LUT = f"lut3d=file='{os.path.join(ROOT, LUT)}':interp=tetrahedral" if LUT else "null"

only = set(sys.argv[1:])  # optional: rebuild only these run numbers
for r, (src, segs) in enumerate(runs):
    if only and str(r) not in only:
        continue
    path = os.path.join(ROOT, E["sources"][src])
    out = os.path.join(ROOT, "assets", "video", f"aroll_r{r}.mp4")
    parts, labels = [], ""
    for k, s in enumerate(segs):
        a, b = fr(s["in"]), fr(s["out"])
        d = b - a
        parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{k}]")
        parts.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015[a{k}]")
        labels += f"[v{k}][a{k}]"
    parts.append(f"{labels}concat=n={len(segs)}:v=1:a=1[vc][a]")
    parts.append(f"[vc]{VF_LUT}[v]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", path, "-filter_complex", ";".join(parts),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-g", "30",
           "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"run {r}: {src} {len(segs)} cuts -> {os.path.relpath(out, ROOT)}")


# muted b-roll: hook shots and the tail shot, LUT baked the same way
broll = [(f"hook_{i}", h["src"], h["in"], h["out"]) for i, h in enumerate(E["hook"]["clips"])]
t = E["tail"]
broll.append(("tail", t["src"], t["in"], t["in"] + t["dur"]))
for name, src, a, b in broll:
    if only and name not in only:
        continue
    out = os.path.join(ROOT, "assets", "video", f"{name}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(fr(a)), "-i", os.path.join(ROOT, E["sources"][src]),
                    "-t", str(fr(b) - fr(a)), "-vf", VF_LUT, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                    "-g", "15", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-colorspace", "bt709", "-movflags", "+faststart", out], check=True)
    print(f"broll {name}: {src} {a}-{b} -> {os.path.relpath(out, ROOT)}")
