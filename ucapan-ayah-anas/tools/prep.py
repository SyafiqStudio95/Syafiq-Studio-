#!/usr/bin/env python3
"""Ayah's message: source .mov (432x864, content letterboxed to 320x640 after ~13 s)
-> assets/video/main.mp4 (src IN..OUT, 1080x1920, warm grade) + tail freeze (blurred) ; assets/audio/vo.wav (cleaned)."""
import os, subprocess
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=f"{R}/assets/audio/src/ayah_raw.mov"; IN=19.95; OUT=66.55; TAIL=3.95; FPS=30
GRADE=("eq=contrast=1.06:saturation=1.07:gamma=0.98,"
       "colorbalance=rs=0.02:bs=-0.03:rm=0.03:bm=-0.03:rh=0.02:bh=-0.02,vignette=angle=0.5")
V=("crop=320:640:56:112,scale=1080:2160:flags=lanczos,crop=1080:1920:0:110,unsharp=5:5:0.7:5:5:0.0,"+GRADE)
def ff(*a): subprocess.run(["ffmpeg","-nostdin","-v","error","-y",*a],check=True)
os.makedirs(f"{R}/assets/video",exist_ok=True)
n=round((OUT-IN)*FPS)
ff("-ss",str(IN),"-i",SRC,"-vf",V+",fps=30,format=yuv420p","-frames:v",str(n),"-an","-c:v","libx264","-preset","veryfast","-crf","17","-g","30",f"{R}/.broll_main.mp4")
ff("-ss",str(OUT-0.25),"-i",SRC,"-vf",V+f",fps=30,trim=end_frame=1,loop=loop={round(TAIL*FPS)}:size=1,gblur=sigma=22,eq=brightness=-0.08,format=yuv420p",
   "-frames:v",str(round(TAIL*FPS)),"-an","-c:v","libx264","-preset","veryfast","-crf","17","-g","30",f"{R}/.broll_tail.mp4")
open(f"{R}/.broll_list.txt","w").write(f"file '{R}/.broll_main.mp4'\nfile '{R}/.broll_tail.mp4'\n")
ff("-f","concat","-safe","0","-i",f"{R}/.broll_list.txt","-c","copy",f"{R}/assets/video/main.mp4")
TOTAL=round(n/FPS+TAIL,3)
ff("-ss",str(IN),"-t",str(OUT-IN+0.6),"-i",SRC,"-vn","-af",
   "highpass=f=90,afftdn=nr=10:nf=-45,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150:makeup=1.5,"
   "loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000,afade=t=in:d=0.05,afade=t=out:st="+str(OUT-IN+0.3)+":d=0.3,apad",
   "-t",str(TOTAL),"-ac","1","-c:a","pcm_s16le",f"{R}/assets/audio/vo.wav")
print("TOTAL",TOTAL)
