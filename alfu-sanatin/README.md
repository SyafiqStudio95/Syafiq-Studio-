# Alfu Sanatin — promo trilogi (HyperFrames)

Vertical 1080×1920 promo edited from the six phone clips in the Google Drive folder "Alfu Sanatin".

## How it is built

| File | What it holds |
| --- | --- |
| `edit.json` | The whole edit: cut list (source in/out per phrase), hook, cards, captions, SFX, grade |
| `tools/make_lut.py` | Generates the smooth teal-amber LUT (`grading/teal-amber.cube`) |
| `tools/cut.py` | Bakes the A-roll (one file per source run, 12 ms audio fades per cut, LUT applied) and the hook/tail b-roll |
| `tools/build.py` | Writes `index.html` and `compositions/*.html` from `edit.json` |
| `transcript/` | Whisper large-v3 transcript, per-phrase chunks and measured pauses |
| `EDIT.md` | Readable cut sheet |
| `preview/` | Self-contained live preview (player + composition + 540p proxies) |

## Rebuild from scratch

```bash
tools/prep_media.sh <folder with VID_2026…mp4 originals>   # normalise to 1080x1920 30fps H.264
python3 tools/make_lut.py
python3 tools/cut.py
python3 tools/build.py
npx hyperframes check
npx hyperframes preview          # Studio
npx hyperframes render -o renders/alfu-sanatin.mp4   # final render (not run yet)
```
