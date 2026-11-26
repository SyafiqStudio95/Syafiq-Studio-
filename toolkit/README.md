# Toolkit suntingan video (Syafiq Studio)

Aliran kerja yang digunakan untuk `alfu-sanatin/`, dijadikan skrip supaya video seterusnya lebih cepat.
Dalam Claude Code, taip **`/edit-video`** dan kongsi link folder Google Drive — Claude akan ikut langkah dalam
`.claude/skills/edit-video/SKILL.md`.

| Langkah | Skrip |
| --- | --- |
| 1. Projek baru | `toolkit/new_project.sh <nama>` |
| 2. Muat turun folder Drive | `python3 -I toolkit/fetch_drive.py <link folder> <folder muat turun>` |
| 3. Normalisasi klip (1080×1920, 30 fps) | `toolkit/prep.sh <folder muat turun> <nama>` |
| 4. Transcribe + kesan jeda | `python3 -I toolkit/transcribe.py <nama> --lang ms --prompt "nama, istilah"` |
| 5. Pilih frasa → potongan | tulis `<nama>/keep.txt`, kemudian `python3 toolkit/make_edl.py <nama>` |
| 6. Grade, bake A-roll, bina composition | `cd <nama> && python3 tools/make_lut.py && python3 tools/cut.py && python3 tools/build.py` |
| 7. Preview (tanpa render) | `toolkit/preview.sh <nama>` → publish `preview/index.html` |
| 8. Render akhir + versi media sosial | `toolkit/finish.sh <nama> <nama-fail>` |

Rujukan lengkap: `alfu-sanatin/edit.json` (hook, kad, caption, SFX, grade) dan `alfu-sanatin/EDIT.md`.

**Gaya hook:** suara bermula dari saat pertama; footage hook (2–3 shot, ~2 saat) dimainkan di atas ayat pembuka dan teks hook ikut ayat tu (`"overVoice": true`, lalai).

Untuk affiliate TikTok: hantar versi tanpa muzik, kemudian tambah lagu dari Commercial Music Library dalam app TikTok.
