#!/usr/bin/env python3
"""Build index.html: father's message (main.mp4 + vo.wav), music, SFX, title, name plate, advice chips, karaoke captions, end card."""
import json, os, html
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP=[c for c in json.load(open(f"{R}/captions.json"))["chunks"] if c["end"]>3.3];  # title card covers Bismillah + salam
TOTAL=50.55; SPEECH_END=46.55
def fr(x): return round(round(x*30)/30,4)
def esc(s): return html.escape(s,quote=True)
CARDS=[]
def card(cid,s,e,body,where="top"): CARDS.append((cid,fr(s),fr(e),body,where))
name_chars="".join(f'<span class="ch">{esc(c) if c!=" " else "&nbsp;"}</span>' for c in "Anas Farhan")
card("title",0.0,3.3,f'''
  <div class="scrim low"></div>
  <div class="blk tt" style="top:960px">
    <div class="chip gold a">Pesanan Ayah untuk</div>
    <div class="name1 a">Muhammad</div>
    <div class="name2">{name_chars}</div>
  </div>''')
card("ayah",3.3,10.0,'''
  <div class="plate a" style="top:300px">
    <div class="pk">Ayah</div>
    <div class="pt">En. Mohd Khairul Azmi<br>b. Hassan</div>
    <div class="ps">Ayah kepada Muhammad Anas Farhan</div>
  </div>''')
card("c1",14.25,17.75,'<div class="blk" style="top:330px"><div class="chip big a">Belajar rajin-rajin</div></div>')
card("c2",24.0,26.3,'<div class="blk" style="top:330px"><div class="chip big a"><i>Enjoy</i> student life</div></div>')
card("list",26.3,36.0,'''
  <div class="list" style="top:300px">
    <div class="li" id="li1"><span class="tick">&#10003;</span>Fokus pelajaran</div>
    <div class="li" id="li2"><span class="tick">&#10003;</span>Ikut disiplin</div>
    <div class="li" id="li3"><span class="tick">&#10003;</span>Sentiasa berhati-hati</div>
  </div>''')
card("c3",37.7,40.0,'<div class="blk" style="top:330px"><div class="chip big a">Sihat wal afiat</div></div>')
card("c4",42.0,45.6,'<div class="blk" style="top:330px"><div class="chip big a">Kembali dengan kejayaan</div></div>')
card("end",SPEECH_END,TOTAL,'''
  <div class="blk" style="top:470px">
    <div class="chip gold a">Pesanan Ayah</div>
    <div class="pre a">Selamat berjuang,</div>
    <div class="name1 big a">Anas!</div>
    <div class="rule"></div>
    <div class="sub a">Semoga kembali<br>dengan kejayaan</div>
    <div class="from a">En. Mohd Khairul Azmi b. Hassan</div>
    <div class="tiny a">MUST &#183; Batch ke-12<br>Isparta, Turki</div>
  </div>''')
# list item timings (film)
LIST=[("#li1",26.37),("#li2",28.93),("#li3",32.39)]
SFX=[("whoosh.mp3",0.0,0.57,0.35),("impact-bass-1.mp3",0.2,2.1,0.4),("sparkle.mp3",0.6,1.8,0.18),
     ("pop.mp3",3.3,0.72,0.25),("pop.mp3",14.2,0.72,0.28),("pop.mp3",23.95,0.72,0.28),
     ("pop.mp3",26.3,0.72,0.28),("pop.mp3",28.88,0.72,0.28),("pop.mp3",32.34,0.72,0.28),
     ("pop.mp3",37.65,0.72,0.28),("pop.mp3",41.95,0.72,0.28),
     ("whoosh.mp3",46.3,0.57,0.3),("impact-bass-2.mp3",46.5,1.1,0.35),("sparkle.mp3",46.7,1.8,0.25)]
def word_span(w):
    if w.startswith("*") and w.endswith("*"): return f'<span class="w em">{esc(w[1:-1])}</span>'
    return f'<span class="w">{esc(w)}</span>'
caps_html="\n".join(f'      <div id="cap{i}" class="cap"><div class="line">{" ".join(word_span(w) for w,_ in c["words"])}</div></div>' for i,c in enumerate(CAP))
cards_html="\n".join(f'      <div id="card-{c}" class="card">{b}\n      </div>' for c,s,e,b,_ in CARDS)
audio=[f'      <audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-duration="{TOTAL}" data-media-start="0" data-volume="1" data-track-index="1"></audio>',
       f'      <audio id="music" class="clip" src="assets/audio/music_mix.wav" data-start="0" data-duration="{TOTAL}" data-media-start="0" data-volume="1" data-track-index="2"></audio>']
for i,(f,s,d,v) in enumerate(SFX):
    audio.append(f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{fr(s)}" data-duration="{d}" data-volume="{v}" data-track-index="{3+i%3}"></audio>')
js=['    tl.fromTo("#cam", {scale: 1.0}, {scale: 1.07, duration: %s, ease: "none"}, 0);' % SPEECH_END,
    '    tl.fromTo("#fadein", {opacity: 1}, {opacity: 0, duration: 0.45, ease: "power1.out"}, 0);']
for c,s,e,b,_ in CARDS:
    js.append(f'    tl.set("#card-{c}", {{opacity: 1}}, {s});')
    if "scrim" in b: js.append(f'    tl.fromTo("#card-{c} .scrim", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, {s});')
    if ' a"' in b or ' a ' in b or 'class="a' in b:
        js.append(f'    tl.fromTo("#card-{c} .a", {{opacity: 0, y: 24, filter: "blur(8px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "back.out(1.6)", stagger: 0.12}}, {s+0.02});')
    if "rule" in b: js.append(f'    tl.fromTo("#card-{c} .rule", {{scaleX: 0}}, {{scaleX: 1, duration: 0.7, ease: "expo.out"}}, {s+0.3});')
    if "name2" in b: js.append(f'    tl.fromTo("#card-{c} .name2 .ch", {{opacity: 0, y: 40, rotate: 8}}, {{opacity: 1, y: 0, rotate: 0, duration: 0.45, ease: "back.out(2)", stagger: 0.045}}, {s+0.35});')
    if e<TOTAL-0.01: js.append(f'    tl.to("#card-{c}", {{opacity: 0, duration: 0.3, ease: "power2.in"}}, {fr(e-0.3)});')
for sel,t in LIST:
    js.append(f'    tl.fromTo("{sel}", {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: 0.45, ease: "back.out(1.8)"}}, {fr(t-0.05)});')
    js.append(f'    tl.fromTo("{sel} .tick", {{scale: 0}}, {{scale: 1, duration: 0.35, ease: "back.out(3)"}}, {fr(t+0.15)});')
js.append(f'    tl.to("#cam", {{filter: "brightness(0.85)", duration: 0.4}}, {SPEECH_END-0.2});')
for i,c in enumerate(CAP):
    s,e=fr(c["start"]),fr(c["end"])
    js.append(f'    tl.fromTo("#cap{i}", {{opacity: 0, y: 18, scale: 0.96}}, {{opacity: 1, y: 0, scale: 1, duration: 0.16, ease: "power2.out"}}, {s});')
    for j,(w,t) in enumerate(c["words"]):
        js.append(f'    tl.fromTo("#cap{i} .w:nth-child({j+1})", {{opacity: 0.42}}, {{opacity: 1, duration: 0.08, ease: "none"}}, {fr(max(s,t))});')
        js.append(f'    tl.fromTo("#cap{i} .w:nth-child({j+1})", {{scale: 1.14}}, {{scale: 1, duration: 0.28, ease: "back.out(2)"}}, {fr(max(s,t))});')
    js.append(f'    tl.set("#cap{i}", {{opacity: 0}}, {e});')
js.append(f'    tl.fromTo("#fadeout", {{opacity: 0}}, {{opacity: 1, duration: 0.7, ease: "power1.in"}}, {TOTAL-0.7});')
CSS='''
      @font-face { font-family: "EB Garamond"; src: url("assets/fonts/EBGaramond-400.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "EB Garamond"; src: url("assets/fonts/EBGaramond-700.woff2") format("woff2"); font-weight: 700; }
      @font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-600.woff2") format("woff2"); font-weight: 600; }
      @font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-800.woff2") format("woff2"); font-weight: 800; }
      @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight: 700; }
      :root { --gold: #f4c76b; --cream: #fff7e8; --green: #1f6b45; --ink: rgba(14,10,4,.72);
              --serif: "EB Garamond", Georgia, serif; --pop: "Poppins", Arial, sans-serif; --sans: "Inter", Arial, sans-serif; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #0b0905; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; }
      #cam { position: absolute; inset: 0; transform-origin: 50% 38%; }
      #main { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .card { position: absolute; inset: 0; opacity: 0; z-index: 10; pointer-events: none; }
      .scrim { position: absolute; left: 0; right: 0; top: 0; height: 1050px;
        background: linear-gradient(180deg, rgba(12,8,3,.86) 0%, rgba(12,8,3,.6) 55%, rgba(12,8,3,0) 100%); }
      .blk.tt { left: 100px; right: 300px; }
      .tt .name1 { font-size: 80px; margin-top: 14px; }
      .tt .name2 { font-size: 86px; }
      .tt .pre { margin-top: 16px; font-size: 44px; }
      .sub.sm { font-size: 27px; margin-top: 14px; }
      .scrim.low { top: auto; bottom: 0; height: 1300px; background: linear-gradient(0deg, rgba(12,8,3,.88) 0%, rgba(12,8,3,.7) 55%, rgba(12,8,3,0) 100%); }
      .blk { position: absolute; left: 130px; right: 192px; text-align: center; }
      .chip { display: inline-block; font: 800 30px/1 var(--pop); letter-spacing: .14em; text-transform: uppercase; color: var(--cream);
              padding: 16px 28px; border-radius: 999px; background: var(--ink); border: 2px solid rgba(244,199,107,.85); }
      .chip.gold { background: var(--gold); color: #2a1d05; border-color: var(--gold); }
      .chip.big { font: 800 46px/1.1 var(--pop); letter-spacing: 0; text-transform: none; padding: 22px 36px; border-radius: 26px;
                  box-shadow: 0 14px 40px rgba(0,0,0,.45); }
      .chip.big i { font-family: var(--serif); font-weight: 700; color: var(--gold); }
      .pre { font: italic 400 50px/1.1 var(--serif); color: var(--cream); margin-top: 26px; text-shadow: 0 4px 24px rgba(0,0,0,.8); }
      .name1 { font: 700 92px/1 var(--serif); color: var(--cream); margin-top: 6px; text-shadow: 0 8px 40px rgba(0,0,0,.75); }
      .name1.big { font-size: 150px; color: var(--gold); }
      .name2 { font: 700 104px/1.05 var(--serif); color: var(--gold); text-shadow: 0 8px 40px rgba(0,0,0,.75); white-space: nowrap; }
      .name2 .ch { display: inline-block; }
      .rule { width: 340px; height: 3px; margin: 22px auto; background: linear-gradient(90deg, transparent, var(--gold), transparent); }
      .sub { font: 600 34px/1.25 var(--pop); color: var(--cream); text-shadow: 0 3px 18px rgba(0,0,0,.85); }
      .from { font: italic 400 40px/1.2 var(--serif); color: var(--gold); margin-top: 26px; text-shadow: 0 3px 18px rgba(0,0,0,.85); }
      .tiny { font: 700 28px/1.2 var(--sans); letter-spacing: .12em; text-transform: uppercase; color: var(--cream); opacity: .85; margin-top: 16px; }
      .plate { position: absolute; left: 110px; right: 230px; padding: 24px 30px 28px; border-radius: 24px; background: var(--ink);
               border-left: 8px solid var(--gold); box-shadow: 0 14px 40px rgba(0,0,0,.4); }
      .pk { font: 800 28px/1 var(--pop); letter-spacing: .16em; text-transform: uppercase; color: var(--gold); }
      .pt { font: 700 52px/1.08 var(--serif); color: var(--cream); margin-top: 12px; }
      .ps { font: 600 30px/1.25 var(--pop); color: #f1e4c8; margin-top: 12px; }
      .list { position: absolute; left: 110px; right: 230px; display: grid; gap: 18px; }
      .li { display: flex; align-items: center; gap: 20px; font: 800 46px/1.1 var(--pop); color: var(--cream); padding: 18px 26px;
            border-radius: 22px; background: var(--ink); box-shadow: 0 12px 34px rgba(0,0,0,.4); opacity: 0; }
      .tick { flex: none; width: 58px; height: 58px; border-radius: 50%; background: var(--gold); color: #2a1d05; display: grid; place-items: center;
              font: 800 34px/1 var(--pop); }
      .cap { position: absolute; left: 100px; right: 290px; bottom: 672px; text-align: center; opacity: 0; z-index: 20; }
      .line { display: inline-flex; flex-wrap: wrap; justify-content: center; align-items: baseline; column-gap: 20px; row-gap: 4px;
              padding: 14px 24px 18px; border-radius: 22px; background: rgba(12,8,3,.55); }
      .w { display: inline-block; font: 800 56px/1.15 var(--pop); color: #ffffff; text-shadow: 0 4px 16px rgba(0,0,0,.6); opacity: .42; }
      .w.em { color: var(--gold); }
      #fadeout, #fadein { position: absolute; inset: 0; background: #000; z-index: 50; opacity: 0; pointer-events: none; }
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
      <div id="cam"><video id="main" class="clip footage" src="assets/video/main.mp4" data-start="0" data-duration="{TOTAL}" data-media-start="0" data-track-index="0" muted playsinline></video></div>
{cards_html}
{caps_html}
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
open(f"{R}/index.html","w").write(doc); print("index.html", len(CAP), "captions", len(CARDS), "cards")
