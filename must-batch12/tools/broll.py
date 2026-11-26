#!/usr/bin/env python3
"""Bake the b-roll track: shots.json -> assets/video/broll.mp4 (1080x1920 30fps, graded, no audio).
   python3 tools/broll.py <folder with SDR mp4 + jpg>"""
import json,os,subprocess,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); MED=sys.argv[1]
J=json.load(open(f"{ROOT}/shots.json")); S=J["shots"]; FPS=30
GRADE=("eq=contrast=1.06:saturation=1.08:gamma=0.97,"
       "colorbalance=rs=0.015:bs=-0.04:rm=0.035:gm=0.012:bm=-0.045:rh=0.03:gh=0.01:bh=-0.04,"
       "vignette=angle=0.55")
tmp=f"{ROOT}/.broll"; os.makedirs(tmp,exist_ok=True); parts=[]
for i,s in enumerate(S):
    end=S[i+1]["t"] if i+1<len(S) else J["end"]; n=round((end-s["t"])*FPS); d=n/FPS
    src=s["src"]; vid=os.path.exists(f"{MED}/{src}.mp4"); out=f"{tmp}/s{i:02d}.mp4"
    kb=s.get("kb","in"); z0,z1=(1.0,1.07) if kb=="in" else (1.07,1.0)
    zexpr=f"{z0}+({z1}-{z0})*on/{n}"
    if vid:
        inp=["-ss",str(s.get("in",0)),"-i",f"{MED}/{src}.mp4"]
    else:
        inp=["-loop","1","-framerate",str(FPS),"-i",f"{MED}/{src}.jpg"]
    pad="tpad=stop_mode=clone:stop_duration=6," if vid else ""
    if s["mode"]=="logo":
        fc=(f"[0:v]{pad}scale=-2:1560,crop=1080:1560,setsar=1,fps={FPS},format=rgba,"
            f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,Y/260)'[fg];"
            f"color=c=0x0b0a09:s=1080x1920:r={FPS}[bg];[bg][fg]overlay=0:360:shortest=1,"
            f"{GRADE},format=yuv420p[v]")
    elif s["mode"]=="full":
        cx=s.get("cx",0.5)
        if vid:
            f=f"scale=-2:1920,crop=1080:1920:(iw-1080)*{cx}:0"
        else:
            f=(f"scale=-2:3840,crop=2160:3840:(iw-2160)*{cx}:0,"
               f"zoompan=z='{zexpr}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps={FPS}")
        fc=f"[0:v]{pad}{f},setsar=1,fps={FPS},{GRADE},format=yuv420p[v]"
    else:
        fg_w=1080
        if vid:
            fg=f"[a]scale={fg_w}:-2[fg]"
        else:
            fg=(f"[a]scale=2160:-2,zoompan=z='{zexpr}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:"
                f"s={fg_w}x{{H}}:fps={FPS}[fg]")
        # height of fg depends on image aspect
        if not vid:
            from PIL import Image
            w,h=Image.open(f"{MED}/{src}.jpg").size; H=round(fg_w*h/w/2)*2; fg=fg.replace("{H}",str(H))
        else: H=608
        y=max(330, 760-H//2)
        fc=(f"[0:v]{pad}setsar=1,fps={FPS},split[a][b];"
            f"[b]scale=-2:1920,crop=1080:1920,gblur=sigma=38,eq=brightness=-0.12:saturation=0.8[bg];{fg};"
            f"[bg][fg]overlay=0:{y},{GRADE},format=yuv420p[v]")
    cmd=["ffmpeg","-nostdin","-v","error","-y",*inp,"-filter_complex",fc,"-map","[v]","-frames:v",str(n),
         "-r",str(FPS),"-c:v","libx264","-preset","veryfast","-crf","17","-g","30",out]
    if os.environ.get("ONLY") and str(i) not in os.environ["ONLY"].split(","): parts.append(out); continue
    subprocess.run(cmd,check=True); parts.append(out); print(i,src,round(d,2),flush=True)
open(f"{tmp}/list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0","-i",f"{tmp}/list.txt","-c","copy",
  f"{ROOT}/assets/video/broll.mp4"],check=True)
print("broll.mp4 done")
