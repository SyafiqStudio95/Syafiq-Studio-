#!/usr/bin/env bash
# Final render (only after the person approved the preview) + a social upload copy at -14 LUFS.
#   toolkit/finish.sh <project> <name>
set -euo pipefail
PRJ=${1:?project}; NAME=${2:?output name}; mkdir -p "$PRJ/renders"; cd "$PRJ"
hyperframes render --quality delivery --fps 30 --output "renders/$NAME-master.mp4"
ffmpeg -v error -y -i "renders/$NAME-master.mp4" -c:v libx264 -preset slow -crf 19 -maxrate 14M -bufsize 28M \
  -profile:v high -pix_fmt yuv420p -movflags +faststart -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 48000 "renders/$NAME-social.mp4"
ffmpeg -hide_banner -i "renders/$NAME-social.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E "I:|Peak:"
ls -la renders/
