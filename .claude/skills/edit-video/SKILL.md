---
name: edit-video
description: Edit raw phone footage from a Google Drive folder into a vertical 9:16 promo with HyperFrames - transcribe, cut awkward pauses and repeats, add a strong hook, captions, motion graphics and sound effects, colour grade and light it, show a live preview, then render. Use when the user shares a Drive folder of clips and asks to edit, cut, caption, grade or promo a video (e.g. "edit video ni", "buang awkward pause", "letak hook", "color grade", "affiliate TikTok").
---

# Edit a promo video (Syafiq Studio workflow)

Proven on `alfu-sanatin/` (book-trilogy promo, Nov 2026). Reply to the user in Bahasa Melayu.
That project is the reference: copy its decisions, read its `edit.json`, `EDIT.md` and `compositions/`.

## The contract with the user

- **Preview before render.** Never run `hyperframes render` until the user has seen the live preview
  and clearly says to render. "Ya" / "Boleh" after a multi-option question is ambiguous: ask which.
- Ask before spending HeyGen credits. Generated music is a HyperFrames Pro feature (Free plan refuses it,
  nothing is charged). Catalog music needs the separate `heygen` CLI, not on npm.
- **TikTok affiliate = commercial**: tell them to deliver without music and add a track from TikTok's
  Commercial Music Library in the app (original sound ~100%, added sound ~15-20%). Do not bake in songs.

## Pipeline (scripts in `toolkit/`, run from the repo root)

1. **Environment.** Needs hosts: drive.google.com, drive.usercontent.google.com, docs.google.com,
   huggingface.co + us.aws.cdn.hf.co / eu.aws.cdn.hf.co / us.gcp.cdn.hf.co / transfer.xethub.hf.co /
   cas-server.xethub.hf.co / cas-bridge.xethub.hf.co, fonts.googleapis.com, fonts.gstatic.com
   (optional HeyGen: api.heygen.com, api2.heygen.com, app.heygen.com, hyperframes.heygen.com).
   The "Syafiq-Studio-" cloud environment already allows them and its setup script installs
   hyperframes + faster-whisper. If a tool is missing: `npm i -g hyperframes@0.9.96`, `pip install faster-whisper`.
   Node's fetch ignores the proxy: prefix HeyGen/`hyperframes auth` commands with `NODE_USE_ENV_PROXY=1`.
2. `toolkit/new_project.sh <name>` then `python3 -I toolkit/fetch_drive.py <drive folder url> /tmp/…/src`
   (put downloads in the scratchpad, not the repo) and `toolkit/prep.sh <src> <name>` → `c1.mp4…`, luma per clip.
   Read any Google Doc that came with it (synopsis, script): it is the best source for the hook line.
3. `python3 -I toolkit/transcribe.py <name> --lang ms --prompt "<names, terms>"` (~15 min CPU for 2.5 min of footage;
   run in the background). Then read `transcript/chunks.txt` — cut on chunk times, never on Whisper word times.
4. Contact sheets of every clip (1 frame / 3 s) so cards and hook shots match what is on screen.
5. Write `<name>/keep.txt` (format in `toolkit/make_edl.py`), dropping:
   repeated names/phrases, stumbles ("sejarah daripada sejarah"), restated lines, "emm" chunks, hallucinations,
   paper/handling noise, silent clips (use them as b-roll). When a boundary is ambiguous, keep the words
   rather than cut mid-word, and tell the user. Fix spelling in captions (takhta, empayar, Palestin, butang).
   `python3 toolkit/make_edl.py <name>`.
6. Fill the rest of `<name>/edit.json` like alfu-sanatin's: `hook` (2-3 muted shots, 3 kinetic lines ≤2.5 s),
   `cards` (title / chapter with era-line nodes / trilogy / cta), `sfx` (whoosh on source changes, pop on nodes,
   impact on hook + payoff; lead = file peak: whoosh 0.13, impact-bass-1 0.04, pop 0.1), `tail`, `grade`.
7. Grade: `python3 tools/make_lut.py` (smooth saturation-weighted teal-amber LUT, edit its numbers per footage),
   per-source `exposure` from the luma readout (darker clip → +0.1…0.2). Compare candidates with
   `hyperframes grade-compare` on real frames (cut a 600 px crop of dark detail too).
8. `python3 tools/cut.py && python3 tools/build.py`, `hyperframes check` until 0 errors,
   `hyperframes snapshot --at …` at every card and read the contact sheet.
9. `toolkit/preview.sh <name>`, edit chapters/notes in `preview/index.html`, publish it as a private
   Artifact (page + every file under preview/ in `files`, root = preview/). Test once in Playwright first.
10. On approval: `toolkit/finish.sh <name> <output-name>` → master + `-social.mp4` at about -14 LUFS. Send the social file.

## Gotchas already paid for

- HyperFrames **secondaries and hue curves blotch** dark and grey areas (macro-block patches): don't use them.
  Use adjust + wheels + details in `data-color-grading` and bake hue work into the LUT (cut.py does).
- The runtime did **not** load `.cube` files (`lut` key drops the whole grade): keep `grade.bakedLut`, not `grade.base.lut`.
- Tween `letterSpacing` → check error; use opacity/blur/y. Flex `column-gap` in **px** for caption words
  (em resolves against the container's 16 px). Card titles over cover art need the top scrim.
- Safe zone 1080×1920: text between y 288-1248 and x 120-888 (780 below y 840). Captions bottom ≤ y 1248.
- Whisper large-v3 on silence: "Terima kasih kerana menonton"; on repeats: invented news lines.
- The A-roll is baked per source run (12 ms audio fades per cut). Hook/tail b-roll are baked too.
- `git push` may 403 even after the user connects GitHub (session credentials are minted at start); the
  GitHub MCP tools can still write text files.
- Render: ~25 min for 105 s at delivery quality on 4 CPUs (software WebGL); master ≈ 430 MB, social ≈ 170 MB.
