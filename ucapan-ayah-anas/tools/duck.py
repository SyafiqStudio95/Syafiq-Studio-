#!/usr/bin/env python3
"""Duck music under the father's speech: music 0.16 while he talks (film 0.0-46.3), 0.55 on the end card."""
import os,numpy as np,soundfile as sf
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
y,sr=sf.read(f"{R}/assets/audio/music.wav"); t=np.arange(len(y))/sr
g=np.interp(t,[0,0.15,46.2,47.0,50.55],[0.16,0.16,0.16,0.55,0.55])
sf.write(f"{R}/assets/audio/music_mix.wav",y*g[:,None],sr,subtype="PCM_16"); print("ok")
