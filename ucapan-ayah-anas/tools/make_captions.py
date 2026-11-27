#!/usr/bin/env python3
"""transcript/asr.json (Whisper word times) -> captions.json chunks (film time), with spelling fixes.
Edit captions.json by hand afterwards; build.py reads it. *word* = gold emphasis."""
import json, os, re
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); IN=19.95; END=46.55
A=json.load(open(f"{R}/transcript/asr.json"))
W=[]
for s in A:
    for a,b,w in s["words"]:
        w=w.strip()
        if a<IN-0.05 or a>IN+END: continue
        if W and (w.startswith("-") or w.startswith("'")):
            W[-1][2]+=w; W[-1][1]=b; continue
        W.append([a,b,w])
W=[w for w in W if w[2] not in ("Ok,",)]
FIX={"Mama":"Muhammad","sehat":"sihat","wafia":"wal afiat","Insya'Allah":"Insya-Allah","insya'Allah":"insya-Allah",
     "Insya'Allah.":"Insya-Allah.","insya'Allah.":"insya-Allah.","Right?":"right?"}
EM={"Muhammad","Anas","Farhan.","Farhan","Turki","Turki.","rajin-rajin.","Fokus","disiplin","berhati-hatilah","selamat.",
    "cemerlang","kejayaan","Alhamdulillah.","Bismillahirrahmanirrahim.","enjoy","life,","student","life","sihat","wal afiat"}
out=[]; cur=[]
for i,(a,b,w) in enumerate(W):
    w=FIX.get(w,w); t=round(a-IN,3)
    cur.append([("*"+w+"*") if w in EM else w, t])
    end=w.endswith((".",",","?","!")) or len(cur)>=4
    nxt=W[i+1][0] if i+1<len(W) else None
    if end or nxt is None or nxt-b>0.45:
        out.append({"start":cur[0][1],"end":round(min(b, nxt if nxt else b)-IN+0.15,3),"words":cur}); cur=[]
for k in range(len(out)-1): out[k]["end"]=min(out[k]["end"],out[k+1]["start"])
json.dump({"note":"film time = source - 19.95; edit words freely (keep [word, time] pairs)","chunks":out},open(f"{R}/captions.json","w"),ensure_ascii=False,indent=0)
for c in out: print(f'{c["start"]:6.2f}-{c["end"]:6.2f}', " ".join(w for w,_ in c["words"]))
