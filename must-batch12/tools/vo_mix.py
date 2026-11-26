import sys,json,glob,numpy as np,soundfile as sf
lines=json.load(open(sys.argv[1])); d=sys.argv[2]; out=sys.argv[3]; SR=48000
from scipy.signal import resample_poly
t=0.6; segs=[]; prev=None; buf=np.zeros(int(92*SR))
for i,(sec,txt) in enumerate(lines):
    w,sr=sf.read(f"{d}/l{i:02d}.wav"); e=np.abs(w); thr=0.02*e.max(); idx=np.where(e>thr)[0]
    a=max(0,idx[0]-int(.03*sr)); b=min(len(w),idx[-1]+int(.1*sr)); w=w[a:b]
    w=resample_poly(w,3,1)  # 16k->48k
    n=len(w); f=int(.01*SR); w[:f]*=np.linspace(0,1,f); w[-f:]*=np.linspace(1,0,f)
    if prev is not None: t+= 0.85 if sec!=prev else 0.28
    if i==len(lines)-1: t=max(t, 86.2-n/SR)
    s=int(t*SR); buf[s:s+n]+=w; segs.append({"i":i,"sec":sec,"start":round(t,3),"end":round(t+n/SR,3)}); t+=n/SR; prev=sec
buf=buf/np.abs(buf).max()*0.89
sf.write(out,buf[:int(90*SR)],SR,subtype="PCM_16"); json.dump(segs,open(out.replace('.wav','.json'),'w'),indent=1)
for s in segs: print(s)
