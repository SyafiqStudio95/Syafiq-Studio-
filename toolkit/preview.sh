#!/usr/bin/env bash
# Package a self-contained live preview (no render) of <project> into <project>/preview/:
# player + runtime + GSAP shipped beside the composition, videos as 540x960 proxies.
# Publish preview/index.html as an Artifact with every other file under preview/ in `files`.
#   toolkit/preview.sh <project>
set -euo pipefail
PRJ=$(cd "${1:?project}" && pwd); HERE=$(cd "$(dirname "$0")" && pwd)
DIST=$(npm root -g)/hyperframes/dist; PV="$PRJ/preview"
GSAP=$(grep -o 'gsap@[0-9.]*' "$PRJ/index.html" | head -1 | cut -d@ -f2)
rm -rf "$PV/film"; mkdir -p "$PV/film/assets/video" "$PV/film/assets/fonts" "$PV/film/assets/sfx" "$PV/film/compositions"
cp "$DIST/hyperframes-player.global.js" "$PV/player.js"; cp "$DIST/hyperframe.runtime.iife.js" "$PV/runtime.js"
TMP=$(mktemp -d); (cd "$TMP" && npm pack "gsap@$GSAP" --silent >/dev/null && tar xzf gsap-*.tgz); cp "$TMP/package/dist/gsap.min.js" "$PV/gsap.min.js"; rm -rf "$TMP"
cp "$PRJ"/compositions/*.html "$PV/film/compositions/"; cp "$PRJ"/assets/fonts/*.woff2 "$PV/film/assets/fonts/"
sed -e "s#<script src=\"https://cdn.jsdelivr.net/npm/gsap@$GSAP/dist/gsap.min.js\"></script>#<script src=\"../gsap.min.js\"></script>#" \
    -e '0,/<head>/s#<head>#<head>\n    <script src="../runtime.js"></script>#' "$PRJ/index.html" > "$PV/film/index.html"
for f in $(grep -o 'assets/sfx/[A-Za-z0-9_-]*\.mp3' "$PRJ/index.html" | sort -u); do cp "$PRJ/$f" "$PV/film/$f"; done
for f in $(grep -o 'assets/video/[A-Za-z0-9_]*\.mp4' "$PRJ/index.html" | sort -u); do
  A="-an"; ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$PRJ/$f" | grep -q . && A="-c:a aac -b:a 96k -ac 1"
  ffmpeg -v error -y -i "$PRJ/$f" -vf scale=540:960:flags=lanczos -c:v libx264 -preset slow -crf 27 -maxrate 1400k -bufsize 2800k \
    -g 15 -pix_fmt yuv420p $A -movflags +faststart "$PV/film/$f" &
done; wait
[ -f "$PV/index.html" ] || cp "$HERE/preview-page.html" "$PV/index.html"
find "$PV" -name '*.mp4' -size +15M -exec echo "WARNING over the 15 MB artifact file limit: {}" \;
du -sh "$PV"; echo "edit the chapter list + notes in $PV/index.html, then publish it"
