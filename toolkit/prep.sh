#!/usr/bin/env bash
# Normalise phone clips (HEVC, rotated, 60 fps) to 1080x1920 30 fps H.264 with 1 s keyframes,
# named c1.mp4, c2.mp4 ... in filename (= recording time) order. Writes sources.json.
#   toolkit/prep.sh <folder with originals> <project>
set -euo pipefail
SRC=${1:?folder}; PRJ=${2:?project}; OUT="$PRJ/assets/video"; mkdir -p "$OUT"
i=1; echo "{" > "$PRJ/sources.json"; first=1
while IFS= read -r f; do
  ffmpeg -nostdin -v error -y -i "$f" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 18 -g 30 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
    -c:a aac -b:a 192k -ar 48000 "$OUT/c$i.mp4"
  [ $first = 1 ] || echo "," >> "$PRJ/sources.json"; first=0
  printf ' "c%s": {"file": "assets/video/c%s.mp4", "original": "%s"}' "$i" "$i" "$(basename "$f")" >> "$PRJ/sources.json"
  echo "c$i <- $(basename "$f")"; i=$((i+1))
done < <(find "$SRC" -maxdepth 1 -iname '*.mp4' -o -maxdepth 1 -iname '*.mov' | sort)
echo "}" >> "$PRJ/sources.json"
for c in "$OUT"/c*.mp4; do
  printf '%s ' "$(basename "$c")"; ffmpeg -v error -i "$c" -vf "fps=1,scale=270:-1,signalstats,metadata=print:file=-" -f null - \
   | grep -o 'YAVG=[0-9.]*' | cut -d= -f2 | awk '{s+=$1;n++} END {printf "avg luma %.0f (use to set per-clip exposure)\n", s/n}'
done
