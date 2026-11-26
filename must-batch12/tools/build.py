#!/usr/bin/env python3
"""Build index.html for the MUST Batch 12 film: b-roll track + VO + music + SFX + cards + captions.
   Inputs: assets/video/broll.mp4, assets/audio/{vo.wav,vo.json,music_mix.wav}, captions.json"""
import json, os, html
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO=json.load(open(f"{R}/assets/audio/vo.json")); CAP=json.load(open(f"{R}/captions.json"))["lines"]
TOTAL=112.0
def fr(x): return round(round(x*30)/30,4)
def esc(s): return html.escape(s,quote=True)
def words(s):
    out=[]
    for w in s.split():
        if w.startswith("*") and w.endswith("*") and len(w)>2: out.append(f'<span class="w em">{esc(w[1:-1])}</span>')
        else: out.append(f'<span class="w">{esc(w)}</span>')
    return " ".join(out)
# ---- captions: split each VO line into chunks timed by character share
caps=[]
for seg,txt in zip(VO,CAP):
    if not txt: continue
    ch=txt.split("|"); L=[len(c.replace("*","")) for c in ch]; tot=sum(L); t=seg["start"]; dur=seg["end"]-seg["start"]
    for c,l in zip(ch,L):
        d=dur*l/tot; caps.append((fr(t),fr(t+d),c)); t+=d
V=lambda i,k="start": VO[i][k]
# ---- cards (film times from VO lines)
CARDS=[]
def card(cid,start,end,body): CARDS.append((cid,fr(start),fr(end),body))
card("title",0.25,7.0,'''
  <div class="scrim top"></div>
  <div class="blk" style="top:300px">
    <div class="kick a">Madrasah Uthmaniyah Smart Tahfiz</div>
    <div class="rule a"></div>
    <div class="ttl a">Majlis Penghantaran</div>
    <div class="huge a">BATCH <span class="gold">KE-12</span></div>
    <div class="sub a">Malaysia &#8594; Isparta, Turki</div>
  </div>''')
card("stat",V(3)-0.1,V(4,"end")+0.2,'''
  <div class="scrim top"></div>
  <div class="blk" style="top:340px">
    <div class="num a">20</div>
    <div class="kick a">Pelajar Batch ke-12</div>
    <div class="row a"><div class="pill"><b>14</b> lelaki</div><div class="pill"><b>6</b> perempuan</div></div>
  </div>''')
card("misi",V(5)-0.1,V(5,"end")+0.4,'''
  <div class="plate a">
    <div class="pk">Misi</div>
    <div class="pt">Peperiksaan<br>Diploma Hafazan</div>
    <div class="ps">Kementerian Agama Islam Turki</div>
  </div>''')
card("nama1",V(6)-0.1,V(6,"end")+0.2,'''
  <div class="plate a">
    <div class="pk">Mengiringi rombongan</div>
    <div class="pt">Puan Hajah Siti Norbaya<br>binti Abd Rahman</div>
    <div class="ps">Ketua Pengurus Operasi MUST</div>
  </div>''')
card("nama2",V(7)-0.1,V(7,"end")+0.2,'''
  <div class="plate a">
    <div class="pk">Mengiringi rombongan</div>
    <div class="pt">Ustaz Wan Abdul Baith<br>Izzuddin bin Wan Mustafa</div>
    <div class="ps">Pengetua MUST</div>
  </div>''')
card("emosi",V(9)-0.2,V(9)+3.0,'''
  <div class="blk" style="top:310px"><div class="chip a">Detik Penuh Emosi</div></div>''')
card("doa",V(13)-0.1,V(13,"end")+0.25,'''
  <div class="plate a">
    <div class="pk">Bacaan Doa</div>
    <div class="pt">Ustaz Asem Abd Karim</div>
    <div class="ps">Memohon perjalanan dipermudahkan</div>
  </div>''')
card("berjuang",V(15)-0.15,V(15,"end")+0.5,'''
  <div class="scrim top"></div>
  <div class="blk" style="top:330px">
    <div class="ttl a">Selamat Berjuang,</div>
    <div class="huge a">BATCH <span class="gold">12!</span></div>
  </div>''')
# ending: MUST logo animation only, no text (user request)
LOGO_T=102.3
# ---- SFX
SFX=[("whoosh.mp3",0.05,0.57,0.35),("impact-bass-1.mp3",0.35,2.1,0.45),
     ("whoosh.mp3",V(3)-0.25,0.57,0.3),("impact-bass-2.mp3",V(3)-0.05,1.1,0.35),
     ("pop.mp3",V(5)-0.05,0.72,0.25),("pop.mp3",V(6)-0.05,0.72,0.25),("pop.mp3",V(7)-0.05,0.72,0.25),
     ("sparkle.mp3",V(9)-0.2,1.8,0.2),("pop.mp3",V(13)-0.05,0.72,0.25),
     ("whoosh.mp3",V(15)-0.4,0.57,0.3),("impact-bass-1.mp3",V(15)-0.15,2.1,0.4),
     ("sparkle.mp3",102.3,1.8,0.22)]
# ---- HTML
cards_html="\n".join(f'      <div id="card-{c}" class="card">{b}\n      </div>' for c,s,e,b in CARDS)
caps_html="\n".join(f'      <div id="cap{i}" class="cap"><div class="line">{words(t)}</div></div>' for i,(s,e,t) in enumerate(caps))
audio=[f'      <audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-duration="{round(TOTAL-0.06,2)}" data-media-start="0" data-volume="1" data-track-index="1"></audio>',
       f'      <audio id="music" class="clip" src="assets/audio/music_mix.wav" data-start="0" data-duration="{TOTAL}" data-media-start="0" data-volume="1" data-track-index="2"></audio>']
for i,(f,s,d,v) in enumerate(SFX):
    audio.append(f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{fr(s)}" data-duration="{d}" data-volume="{v}" data-track-index="{3+i%3}"></audio>')
js=[]
for c,s,e,b in CARDS:
    js.append(f'    tl.set("#card-{c}", {{opacity: 1}}, {s});')
    if "scrim" in b: js.append(f'    tl.fromTo("#card-{c} .scrim", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, {s});')
    js.append(f'    tl.fromTo("#card-{c} .a", {{opacity: 0, y: 26, filter: "blur(8px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.55, ease: "expo.out", stagger: 0.12}}, {s});')
    if "rule" in b: js.append(f'    tl.fromTo("#card-{c} .rule", {{scaleX: 0}}, {{scaleX: 1, duration: 0.7, ease: "expo.out"}}, {s+0.1});')
    if e<TOTAL-0.01:
        js.append(f'    tl.to("#card-{c}", {{opacity: 0, duration: 0.3, ease: "power2.in"}}, {fr(e-0.3)});')
for i,(s,e,t) in enumerate(caps):
    js.append(f'    tl.fromTo("#cap{i}", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.18, ease: "power2.out"}}, {s});')
    js.append(f'    tl.fromTo("#cap{i} .w", {{opacity: 0.35}}, {{opacity: 1, duration: 0.12, stagger: {round(max(0.04,(e-s)*0.6/max(1,len(t.split()))),3)}}}, {s});')
    js.append(f'    tl.set("#cap{i}", {{opacity: 0}}, {e});')
js.append(f'    tl.fromTo("#fadeout", {{opacity: 0}}, {{opacity: 1, duration: 0.8, ease: "power1.in"}}, {TOTAL-0.8});')
js.append(f'    tl.fromTo("#dip", {{opacity: 0}}, {{opacity: 1, duration: 0.4, ease: "power2.in"}}, {LOGO_T-0.4});')
js.append(f'    tl.to("#dip", {{opacity: 0, duration: 0.9, ease: "power2.out"}}, {LOGO_T});')
js.append('    tl.fromTo("#fadein", {opacity: 1}, {opacity: 0, duration: 0.5, ease: "power1.out"}, 0);')
CSS='''
      @font-face { font-family: "EB Garamond"; src: url("assets/fonts/EBGaramond-400.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "EB Garamond"; src: url("assets/fonts/EBGaramond-700.woff2") format("woff2"); font-weight: 700; }
      @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-400.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight: 700; }
      :root { --gold: #e9c277; --gold-deep: #b8893a; --paper: #fbf4e4; --green: #1f6b45;
              --serif: "EB Garamond", Georgia, serif; --sans: "Inter", Arial, sans-serif; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #0a0806; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; }
      #broll { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .card { position: absolute; inset: 0; opacity: 0; z-index: 10; pointer-events: none; }
      .scrim.top { position: absolute; left: 0; right: 0; top: 0; height: 1000px;
        background: linear-gradient(180deg, rgba(10,7,3,.78) 0%, rgba(10,7,3,.55) 50%, rgba(10,7,3,0) 100%); }
      .blk { position: absolute; left: 130px; right: 192px; text-align: center; }
      .kick { font: 700 28px/1.3 var(--sans); letter-spacing: .16em; text-transform: uppercase; color: var(--gold);
              text-shadow: 0 2px 14px rgba(0,0,0,.7); }
      .rule { width: 360px; height: 3px; margin: 22px auto; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
      .ttl { font: italic 400 76px/1.05 var(--serif); color: var(--paper); text-shadow: 0 6px 30px rgba(0,0,0,.7); }
      .huge { font: 700 112px/1.0 var(--serif); color: var(--paper); margin-top: 10px; letter-spacing: .02em;
              text-shadow: 0 8px 40px rgba(0,0,0,.7); }
      .gold { color: var(--gold); }
      .sub { font: 400 40px/1.2 var(--sans); color: var(--paper); margin-top: 22px; opacity: .95; text-shadow: 0 3px 18px rgba(0,0,0,.8); }
      .num { font: 700 300px/0.9 var(--serif); color: var(--gold); text-shadow: 0 10px 50px rgba(0,0,0,.7); }
      .row { display: flex; justify-content: center; gap: 22px; margin-top: 26px; }
      .pill { font: 400 36px/1 var(--sans); color: var(--paper); padding: 18px 30px; border-radius: 999px;
              background: rgba(12,9,4,.6); border: 2px solid rgba(233,194,119,.7); }
      .pill b { color: var(--gold); font-weight: 700; }
      .plate { position: absolute; left: 110px; right: 300px; bottom: 672px; padding: 26px 34px 30px; border-radius: 22px;
               background: rgba(12,9,4,.72); border-left: 6px solid var(--gold); text-align: left; }
      .pk { font: 700 28px/1 var(--sans); letter-spacing: .2em; text-transform: uppercase; color: var(--gold); }
      .pt { font: 700 44px/1.12 var(--serif); color: var(--paper); margin-top: 14px; }
      .ps { font: 400 30px/1.25 var(--sans); color: #eadfc6; margin-top: 12px; }
      .chip { display: inline-block; font: 700 30px/1 var(--sans); letter-spacing: .24em; text-transform: uppercase; color: var(--paper);
              padding: 18px 30px; border-radius: 999px; background: rgba(12,9,4,.62); border: 2px solid rgba(233,194,119,.75); }
      .tag { font: italic 400 58px/1.12 var(--serif); color: var(--paper); text-shadow: 0 6px 30px rgba(0,0,0,.8); }
      .cap { position: absolute; left: 100px; right: 300px; bottom: 672px; text-align: center; opacity: 0; z-index: 20; }
      .line { display: inline-flex; flex-wrap: wrap; justify-content: center; align-items: baseline; column-gap: 14px;
              padding: 14px 26px 18px; border-radius: 18px; background: rgba(10,7,3,.5); }
      .w { display: inline-block; font: 700 46px/1.2 var(--sans); color: #fffaf0; text-shadow: 0 3px 16px rgba(0,0,0,.6); }
      .w.em { font: italic 700 54px/1.05 var(--serif); color: var(--gold); }
      #fadeout, #fadein, #dip { position: absolute; inset: 0; background: #000; z-index: 50; opacity: 0; pointer-events: none; }
'''
doc=f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-fps="30" data-width="1080" data-height="1920">
      <video id="broll" class="clip footage" src="assets/video/broll.mp4" data-start="0" data-duration="{TOTAL}" data-media-start="0" data-track-index="0" muted playsinline></video>
{cards_html}
{caps_html}
      <div id="dip"></div>
      <div id="fadein"></div>
      <div id="fadeout"></div>
{chr(10).join(audio)}
    </div>
    <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f"{R}/index.html","w").write(doc); print("index.html", len(caps), "captions", len(CARDS), "cards")
