#!/usr/bin/env bash
# Normalize the phone clips (HEVC, rotated, ~60fps) to 1080x1920 30fps H.264 with 1s keyframes.
# Usage: tools/prep_media.sh <folder with the VID_*.mp4 originals>
set -euo pipefail
SRC=${1:?folder}; OUT=$(dirname "$0")/../assets/video; mkdir -p "$OUT"; i=1
for f in VID_20261126_042810 VID_20261126_042928 VID_20261126_043035 VID_20261126_043225 VID_20261126_043359 VID_20261126_043406; do
  ffmpeg -v error -y -i "$SRC/$f.mp4" -vf "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 18 -g 30 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
    -c:a aac -b:a 192k -ar 48000 "$OUT/c$i.mp4"; i=$((i+1))
done
