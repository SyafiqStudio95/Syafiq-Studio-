#!/usr/bin/env python3
"""User-read VO (Drive: VID_20261126_233336.mp4) -> assets/audio/vo.wav (cleaned, film offset) + vo.json (line times in film).
Line times are VO-file times from a Whisper medium pass (word level); film = vo + OFFSET."""
import json, os, subprocess
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFSET=0.5; TOTAL=112.0
LINES=[  # (section, start, end) in the recording
 ("s1",0.00,4.12),("s1",4.28,9.16),("s1",9.46,17.00),
 ("s2",17.76,23.04),("s2",23.18,26.52),("s2",26.52,32.52),
 ("s3",34.10,41.52),("s3",41.52,46.78),("s3",46.78,53.74),
 ("s4",54.74,62.30),("s4",62.44,65.00),("s4",65.24,71.70),("s4",71.70,74.74),
 ("s5",75.98,80.74),("s5",81.02,89.16),
 ("s6",89.70,91.30),("s6",91.58,97.60),("s6",98.26,101.90),("s6",102.00,107.46)]
src=f"{R}/assets/audio/src/vo_user_raw.wav"
af=(f"highpass=f=80,afftdn=nr=8:nf=-55,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2,"
    f"loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000,adelay={int(OFFSET*1000)},apad")
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",src,"-af",af,"-t",str(TOTAL),"-ar","48000","-ac","1","-c:a","pcm_s16le",f"{R}/assets/audio/vo.wav"],check=True)
json.dump([{"i":i,"sec":s,"start":round(a+OFFSET,3),"end":round(b+OFFSET,3)} for i,(s,a,b) in enumerate(LINES)],
          open(f"{R}/assets/audio/vo.json","w"),indent=1)
print("vo.wav + vo.json written")
