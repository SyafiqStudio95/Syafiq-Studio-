#!/usr/bin/env bash
# Scaffold a new promo-edit project next to alfu-sanatin/.
#   toolkit/new_project.sh <name>
# Gives: HyperFrames portrait project + tools/ (build, cut, make_lut) + fonts + bundled SFX + .gitignore
set -euo pipefail
NAME=${1:?project name}; HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(dirname "$HERE")
cd "$REPO"
hyperframes telemetry disable >/dev/null 2>&1 || true
hyperframes init "$NAME" --example blank --resolution portrait --non-interactive --skip-skills >/dev/null
mkdir -p "$NAME"/{tools,assets/video,assets/fonts,assets/sfx,grading,transcript}
cp "$HERE"/project-tools/*.py "$NAME/tools/"
cp "$REPO"/alfu-sanatin/assets/fonts/* "$NAME/assets/fonts/"
SFX=$(ls -d ~/.claude/skills/media-use/audio/assets/sfx 2>/dev/null || true)
if [ -n "$SFX" ]; then cp "$SFX"/{whoosh,impact-bass-1,impact-bass-2,pop,sparkle}.mp3 "$SFX/CREDITS.md" "$NAME/assets/sfx/"; \
else cp "$REPO"/alfu-sanatin/assets/sfx/* "$NAME/assets/sfx/"; fi
cp "$REPO/alfu-sanatin/.gitignore" "$NAME/.gitignore"
echo "created $NAME/  -> next: toolkit/prep.sh <downloaded folder> $NAME"
