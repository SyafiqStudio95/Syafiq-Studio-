#!/usr/bin/env python3
"""Make a packaged preview play smoothly: bake an FFmpeg approximation of each clip's
grade into its 540p proxy and drop data-color-grading from preview/film/index.html, so
the browser plays plain video instead of running the WebGL grade shader every frame
(that shader is what makes the live preview stutter, especially on phones).
The final render still uses the real HyperFrames grade.

    python3 toolkit/smooth_preview.py <project>      (after toolkit/preview.sh)
"""
import html, json, os, re, subprocess, sys
P = os.path.abspath(sys.argv[1]); PV = os.path.join(P, "preview", "film")
idx = open(os.path.join(PV, "index.html"), encoding="utf8").read()
done = set()
for m in re.finditer(r'<video [^>]*src="(assets/video/[^"]+)"[^>]*data-color-grading="([^"]+)"', idx):
    src, g = m.group(1), json.loads(html.unescape(m.group(2)))
    if src in done: continue
    done.add(src)
    a = g.get("adjust", {}); k = g.get("intensity", 1)
    ex, co = a.get("exposure", 0) * k, a.get("contrast", 0) * k
    sat = 1 + (a.get("saturation", 0) + 0.6 * a.get("vibrance", 0)) * k
    gamma = 1 + 0.5 * (a.get("shadows", 0) - a.get("blacks", 0)) * k
    temp = a.get("temperature", 0) * k
    vig = g.get("details", {}).get("vignette", 0)
    vf = [f"eq=brightness={0.10 * ex:.4f}:contrast={1 + co:.3f}:saturation={sat:.3f}:gamma={gamma:.3f}"]
    if temp: vf.append(f"colorbalance=rm={0.25 * temp:.3f}:bm={-0.25 * temp:.3f}:rh={0.2 * temp:.3f}:bh={-0.2 * temp:.3f}")
    if vig > 0.02: vf.append(f"vignette=angle={0.35 + vig:.3f}")
    full = os.path.join(P, src); out = os.path.join(PV, src)
    A = ["-an"]
    if subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", full],
                      capture_output=True, text=True).stdout.strip():
        A = ["-c:a", "aac", "-b:a", "96k", "-ac", "1"]
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", full, "-vf", "scale=540:960:flags=lanczos," + ",".join(vf),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-maxrate", "1600k", "-bufsize", "3200k", "-g", "15",
                    "-pix_fmt", "yuv420p", *A, "-movflags", "+faststart", out], check=True)
    print("baked", src, vf)
idx = re.sub(r' data-color-grading="[^"]*"', "", idx)
open(os.path.join(PV, "index.html"), "w", encoding="utf8").write(idx)
print("grading attributes removed from preview/film/index.html")
