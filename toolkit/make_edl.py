#!/usr/bin/env python3
"""Turn a hand-picked keep list into the `edl` of <project>/edit.json.

    python3 toolkit/make_edl.py <project>

<project>/keep.txt, one kept phrase per line (copy lines from transcript/chunks.txt):
    c1 0.00 6.24 . | Siapa yang tengah|mencari bahan bacaan|*sejarah* *Islam?*
    c1 7.49 8.86   | Siri yang *pertama*
  src  start end  [. = sentence end]  | caption groups split by '|', *word* = gold emphasis
Pads each cut 0.05 s before and 0.08 s after (0.16 s at a sentence end), never into the
next kept phrase, and alternates punch-in framing 1.0 / 1.08 / 1.0 / 1.14 inside each source.
Existing edl fields you added by hand (punch, z) are kept when the same (src, a) comes back.
"""
import json, os, sys
P = sys.argv[1]
E = json.load(open(os.path.join(P, "edit.json"), encoding="utf8"))
old = {(s["src"], s.get("a")): s for s in E.get("edl", [])}
K = []
for ln in open(os.path.join(P, "keep.txt"), encoding="utf8"):
    ln = ln.strip()
    if not ln or ln.startswith("#"): continue
    head, _, cap = ln.partition("|")
    f = head.split()
    K.append((f[0], float(f[1]), float(f[2]), len(f) > 3 and f[3] == ".", cap.strip()))
edl, zs, zi = [], [1.0, 1.08, 1.0, 1.14], 0
for i, (s, a, b, end, cap) in enumerate(K):
    prev = K[i - 1] if i else None
    nxt = K[i + 1] if i + 1 < len(K) else None
    if not prev or prev[0] != s: zi = 0
    ia = max(0.0, a - 0.05)
    if prev and prev[0] == s: ia = max(ia, edl[-1]["out"])
    ob = b + (0.16 if end else 0.08)
    if nxt and nxt[0] == s and nxt[1] - 0.05 < ob: ob = max(b, nxt[1] - 0.05)
    seg = {"src": s, "in": round(ia, 2), "out": round(ob, 2), "a": a, "b": b, "z": zs[zi % 4], "note": cap.replace("|", " ").replace("*", ""), "cap": cap}
    if (s, a) in old:
        for k in ("punch", "z"):
            if k in old[(s, a)]: seg[k] = old[(s, a)][k]
    edl.append(seg); zi += 1
E["edl"] = edl
json.dump(E, open(os.path.join(P, "edit.json"), "w"), ensure_ascii=False, indent=1)
print(f"{len(edl)} cuts, {sum(e['out'] - e['in'] for e in edl):.1f}s of A-roll")
