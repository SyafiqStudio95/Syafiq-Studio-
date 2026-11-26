#!/usr/bin/env python3
"""Duck music under the VO: music.wav + vo.json -> music_mix.wav (0.24 under speech, 0.5 in gaps/intro/outro)."""
import json,os,numpy as np,soundfile as sf
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
y,sr=sf.read(f"{R}/assets/audio/music.wav"); segs=json.load(open(f"{R}/assets/audio/vo.json"))
g=np.full(len(y),0.5); 
for s in segs:
    a=int((s["start"]-0.25)*sr); b=int((s["end"]+0.35)*sr); g[max(a,0):b]=0.24
k=int(0.4*sr); g=np.convolve(g,np.ones(k)/k,mode="same")
sf.write(f"{R}/assets/audio/music_mix.wav",y*g[:,None],sr,subtype="PCM_16"); print("ok")
