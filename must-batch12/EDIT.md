# MUST Batch 12 → Isparta, Turki — nota suntingan

- Sumber: folder Google Drive (19 klip iPhone HDR, 36 gambar HEIC, animasi logo MUST, skrip Google Doc).
  VO: rakaman pengguna sendiri (Drive `VID_20261126_233336.mp4`), disimpan di luar git.
- Durasi akhir 1:52 (112 s), 1080×1920, 30 fps. Render: `toolkit/finish.sh must-batch12 MUST-Batch12-Isparta`.
- Penutup: animasi logo sahaja (tanpa teks), dip-to-black dari shot terakhir.

## Bina semula
1. Muat turun Drive → `python3 -I toolkit/fetch_drive.py <folder> <src>`; HDR → SDR (zscale+tonemap hable) dan HEIC → JPG ke satu folder `<media>`.
2. Letak rakaman VO di `assets/audio/src/vo_user_raw.wav` (48 kHz mono) → `python3 tools/vo_user.py` (vo.wav + vo.json).
3. `python3 tools/broll.py <media>` (shots.json → broll.mp4, grade emas hangat dibakar).
4. `python3 tools/music.py && python3 tools/duck.py` (muzik sintesis, di-duck bawah VO).
5. `python3 tools/build.py` (kad, kapsyen dari captions.json, SFX) → `hyperframes check`.
6. Preview: `toolkit/preview.sh must-batch12`, publish preview/index.html dengan preview-files.json.

## Link
- Preview: https://claude.ai/artifact/XBV1oa53cZzNvY9vHuqYMu
- Halaman rakaman VO: https://claude.ai/artifact/RTRGd73VzHx8Dzy5FFMPv9
