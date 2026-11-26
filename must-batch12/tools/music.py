#!/usr/bin/env python3
"""Synthesise a soft cinematic underscore (royalty-free, made here): warm pad + felt-piano arpeggio,
low strings join at ~44 s (emotional part), swell at ~90 s, resolve on the logo. -> assets/audio/music.wav"""
import numpy as np, soundfile as sf, os
SR=44100; T=112.0; N=int(SR*T); rng=np.random.default_rng(3)
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def hz(m): return 440*2**((m-69)/12)
BAR=60/72*4  # 72 bpm, 4/4 -> 3.333 s per bar
# D major: D  Bm  G  A | D/F#  Em  G  A   (midi roots + triads)
CH=[[50,62,66,69],[47,62,66,71],[43,62,67,71],[45,61,64,69],[42,62,66,69],[40,59,64,67],[43,62,67,71],[45,61,64,69]]
t=np.arange(N)/SR; L=np.zeros(N); R=np.zeros(N)
def env(n,a,r):
    e=np.ones(n); a=int(a*SR); r=int(r*SR); e[:a]=np.linspace(0,1,a); e[-r:]*=np.linspace(1,0,r); return e
def intensity(x):  # arrangement curve
    return np.interp(x,[0,8,55,75,90,100,106,112],[0.55,0.7,0.8,0.95,1.0,1.0,0.8,0.0])
nbars=int(np.ceil(T/BAR))
for b in range(nbars):
    ch=CH[b%8]; s=int(b*BAR*SR); n=min(int(BAR*SR*1.25),N-s)
    if n<=0: break
    tt=np.arange(n)/SR; e=env(n,1.2,1.4)
    for k,m in enumerate(ch[1:]):  # pad: detuned soft saws via few harmonics
        for det,pan in((-0.07,0.3),(0.07,0.7)):
            f=hz(m)*(1+det/100*12/12)
            w=sum(np.sin(2*np.pi*f*h*tt+rng.uniform(0,6))/h**1.6 for h in range(1,6))
            L[s:s+n]+=w*e*0.020*(1-pan); R[s:s+n]+=w*e*0.020*pan
    # bass / low strings from ~44 s
    f=hz(ch[0]); w=np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*2*f*tt)+0.12*np.sin(2*np.pi*3*f*tt)
    g=0.05 if b*BAR>=54 else 0.022
    L[s:s+n]+=w*e*g; R[s:s+n]+=w*e*g
    # piano arpeggio (8ths)
    arp=[ch[1]+12,ch[2]+12,ch[3]+12,ch[2]+12,ch[1]+24,ch[3]+12,ch[2]+12,ch[3]]
    step=BAR/8
    for j,m in enumerate(arp):
        st=b*BAR+j*step
        if st>=106.0: break
        ss=int(st*SR); nn=min(int(2.4*SR),N-ss); ttt=np.arange(nn)/SR; f=hz(m)
        w=(np.sin(2*np.pi*f*ttt)+0.3*np.sin(2*np.pi*2*f*ttt)*np.exp(-ttt*3)+0.08*np.sin(2*np.pi*3*f*ttt)*np.exp(-ttt*6))
        w*=np.exp(-ttt*1.9)*np.minimum(1,ttt/0.004); vel=0.05*(0.85+0.3*rng.random())*(1.0 if j%2==0 else 0.75)
        pan=0.35+0.3*rng.random(); L[ss:ss+nn]+=w*vel*(1-pan); R[ss:ss+nn]+=w*vel*pan
# final chord on logo
s=int(102.3*SR); n=N-s; tt=np.arange(n)/SR
for m in [38,50,57,62,66,69,74]:
    w=np.sin(2*np.pi*hz(m)*tt)*np.exp(-tt*0.45)*0.05; L[s:s+n]+=w; R[s:s+n]+=w
g=intensity(t); L*=g; R*=g
# simple reverb: convolve with decaying noise
from scipy.signal import fftconvolve
ir_n=int(2.6*SR); ir=rng.standard_normal((2,ir_n))*np.exp(-np.arange(ir_n)/SR*2.6); ir[:, :int(0.02*SR)]=0
L2=L+0.25*fftconvolve(L,ir[0])[:N]/30; R2=R+0.25*fftconvolve(R,ir[1])[:N]/30
y=np.stack([L2,R2],1); y/=np.abs(y).max(); y*=0.9
fo=int(3.6*SR); y[-fo:]*=np.linspace(1,0,fo)[:,None]
sf.write(f"{ROOT}/assets/audio/music.wav",y,SR,subtype="PCM_16"); print("music.wav", y.shape[0]/SR)
