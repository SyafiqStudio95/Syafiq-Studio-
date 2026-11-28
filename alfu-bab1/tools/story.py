"""Story layer for voice-only edits: full-frame motion-graphic scenes that carry the
picture while the narration plays (the source footage is black).

build.py calls make(E, T, fr, scene, esc, total) and gets back {cid: (start, dur, html)}.
edit.json:
  "story": [ {"id": .., "kind": quote|split|map|list|swap|letter|counter|date|cover, "in": cue, "out": cue, ...}, ... ]
  "watermark": {"text": "SYAFIQ STUDIO", "sub": "versi"}  (drawn on the background layer, whole film)
Cue = film seconds or [src, source seconds]. Beat times inside a scene are cues too.
Layout: visuals live in y 300-1040; captions sit below (bottom 690 px).
"""
import json

CSS_BASE = """
    .st { position: absolute; left: 0; right: 0; top: 0; height: 1920px; }
    .kick { position: absolute; left: 120px; right: 120px; text-align: center; font: 700 34px/1 var(--sans); letter-spacing: .38em;
            color: var(--gold); text-transform: uppercase; text-shadow: 0 2px 16px rgba(0,0,0,.7); }
    .big { position: absolute; left: 110px; right: 110px; text-align: center; font: 700 96px/1.04 var(--serif); color: var(--paper);
           text-wrap: balance; text-shadow: 0 8px 40px rgba(0,0,0,.65); }
    .big .w { display: inline-block; }
    .em { color: var(--gold); font-style: italic; }
    .red { color: #e0573a; }
    .stamp { position: absolute; padding: 14px 34px 10px; border: 7px solid #d2412a; border-radius: 14px; color: #d2412a;
             font: 700 92px/1 var(--serif); letter-spacing: .08em; text-transform: uppercase; transform: rotate(-9deg);
             background: rgba(20,6,4,.35); box-shadow: 0 0 40px rgba(210,65,42,.35); }
"""


def words(text):
    out = []
    for w in text.split(" "):
        cls = "w"
        if w.startswith("*") and w.endswith("*") and len(w) > 1:
            w, cls = w[1:-1], "w em"
        elif w.startswith("!") and len(w) > 1:
            w, cls = w[1:], "w red"
        out.append(f'<span class="{cls}">{w}</span>')
    return " ".join(out)


def make(E, T, fr, scene, esc, total):
    out = {}

    def rel(x, a):
        return fr(max(0.0, T(x) - a))

    def fade_out(sel, d):
        return f'    tl.to({json.dumps(sel)}, {{opacity: 0, filter: "blur(10px)", duration: 0.25, ease: "power2.in"}}, {fr(d - 0.27)});'

    def words_in(sel, t, stagger=0.06):
        return (f'    tl.fromTo("{sel} .w", {{opacity: 0, y: 26, filter: "blur(8px)"}}, '
                f'{{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "expo.out", stagger: {stagger}}}, {t});')

    for c in E.get("story", []):
        cid, k = c["id"], c["kind"]
        a, b = T(c["in"]), T(c["out"])
        d = fr(b - a)
        css, body, js = CSS_BASE, [], []

        if k == "quote":
            # lines: [{text, y, at, size?, style?}], optional stamp {text, at, x, y}
            for i, L in enumerate(c["lines"]):
                lid = f"{cid}-l{i}"
                size = L.get("size", 96)
                st = L.get("style", "big")
                cls = "kick" if st == "kick" else "big"
                body.append(f'    <div id="{lid}" class="{cls}" style="top:{L["y"]}px;{"font-size:%dpx" % size if cls == "big" else ""}">{words(esc(L["text"]).replace("&#x27;", "’"))}</div>')
                t = rel(L["at"], a)
                if cls == "kick":
                    js.append(f'    tl.fromTo("#{lid}", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, {t});')
                elif L.get("slam"):
                    js.append(f'    tl.fromTo("#{lid}", {{opacity: 0, scale: 1.35, filter: "blur(14px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "expo.out"}}, {t});')
                else:
                    js.append(words_in(f"#{lid}", t))
                if L.get("outAt") is not None:
                    js.append(f'    tl.to("#{lid}", {{opacity: 0.0, filter: "blur(8px)", duration: 0.25}}, {rel(L["outAt"], a)});')
            if c.get("stamp"):
                s = c["stamp"]
                body.append(f'    <div id="{cid}-stamp" class="stamp" style="left:{s.get("x", 300)}px; top:{s.get("y", 760)}px">{esc(s["text"])}</div>')
                js.append(f'    tl.fromTo("#{cid}-stamp", {{opacity: 0, scale: 2.4}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "power4.in"}}, {rel(s["at"], a)});')
                js.append(f'    tl.fromTo("#{cid}-stamp", {{x: -8}}, {{x: 0, duration: 0.25, ease: "elastic.out(1,0.3)"}}, {fr(rel(s["at"], a) + 0.22)});')
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "split":
            # big number + bar in two halves
            left, right = c["left"], c["right"]
            body.append(f"""    <div id="{cid}-num" class="big" style="top:330px; font-size:190px; color: var(--gold)">{esc(c["num"])}</div>
    <div id="{cid}-lab" class="kick" style="top:540px">{esc(c["label"])}</div>
    <div class="bar" style="top:650px">
      <div id="{cid}-L" class="half l"><b>{esc(left["n"])}</b><span>{esc(left["t"])}</span></div>
      <div id="{cid}-R" class="half r"><b>{esc(right["n"])}</b><span>{esc(right["t"])}</span></div>
    </div>""")
            css += """
    .bar { position: absolute; left: 130px; right: 130px; height: 250px; display: flex; gap: 14px; }
    .half { flex: 1; border-radius: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; transform-origin: 0 50%; }
    .half.l { background: linear-gradient(160deg, #f0c470, #b9832f); color: #1a1206; }
    .half.r { background: linear-gradient(160deg, #8e2a1c, #3a0d08); color: #fbe3d6; transform-origin: 100% 50%; box-shadow: 0 0 50px rgba(200,60,40,.35); }
    .half b { font: 700 110px/0.9 var(--serif); }
    .half span { font: 700 30px/1.2 var(--sans); letter-spacing: .14em; text-transform: uppercase; margin-top: 10px; text-align: center; }
"""
            js.append(f'    tl.fromTo("#{cid}-num", {{opacity: 0, scale: 1.4, filter: "blur(14px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out"}}, 0.02);')
            js.append(f'    tl.fromTo("#{cid}-lab", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, 0.2);')
            js.append(f'    tl.fromTo("#{cid}-L", {{scaleX: 0, opacity: 0}}, {{scaleX: 1, opacity: 1, duration: 0.5, ease: "expo.out"}}, {rel(left["at"], a)});')
            js.append(f'    tl.fromTo("#{cid}-R", {{scaleX: 0, opacity: 0}}, {{scaleX: 1, opacity: 1, duration: 0.5, ease: "expo.out"}}, {rel(right["at"], a)});')
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "map":
            # nodes: [{id, label, x, y, at, kind: origin|city|target}], links: [{from, to, at}]
            nodes = {n["id"]: n for n in c["nodes"]}
            svg = []
            for i, L in enumerate(c["links"]):
                p, q = nodes[L["from"]], nodes[L["to"]]
                mx, my = (p["x"] + q["x"]) / 2, (p["y"] + q["y"]) / 2 - 60
                svg.append(f'<path id="{cid}-k{i}" d="M{p["x"]},{p["y"]} Q{mx},{my} {q["x"]},{q["y"]}" class="lnk" pathLength="1"/>')
                js.append(f'    tl.fromTo("#{cid}-k{i}", {{strokeDashoffset: 1}}, {{strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut"}}, {rel(L["at"], a)});')
            html_nodes = []
            for n in c["nodes"]:
                nid = f'{cid}-n-{n["id"]}'
                html_nodes.append(f'      <div id="{nid}" class="mnode {n.get("kind", "city")}" style="left:{n["x"]}px; top:{n["y"]}px"><i></i><span style="{n.get("lstyle", "")}">{esc(n["label"])}</span></div>')
                t = rel(n["at"], a)
                js.append(f'    tl.fromTo("#{nid} i", {{scale: 0}}, {{scale: 1, duration: 0.45, ease: "back.out(2.2)"}}, {t});')
                js.append(f'    tl.fromTo("#{nid} span", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {fr(t + 0.06)});')
                if n.get("kind") == "target":
                    js.append(f'    tl.fromTo("#{nid} i", {{boxShadow: "0 0 0 0 rgba(224,87,58,.8)"}}, {{boxShadow: "0 0 0 40px rgba(224,87,58,0)", duration: 1.0, repeat: 2, ease: "power1.out"}}, {fr(t + 0.3)});')
            body.append(f"""    <div id="{cid}-title" class="kick" style="top:320px">{esc(c.get("title", ""))}</div>
    <div id="{cid}-board" class="board">
      <svg class="routes" viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(svg)}</svg>
{chr(10).join(html_nodes)}
    </div>""")
            css += """
    .board { position: absolute; inset: 0; }
    .board::before { content: ""; position: absolute; left: 110px; right: 110px; top: 390px; height: 640px; border-radius: 36px;
                     background: radial-gradient(80% 80% at 50% 45%, rgba(232,184,92,.10), rgba(232,184,92,0)), rgba(14,10,6,.55);
                     border: 1px solid rgba(232,184,92,.28); }
    .routes { position: absolute; left: 0; top: 0; }
    .lnk { fill: none; stroke: #e8b85c; stroke-width: 5; stroke-dasharray: 0.03 0.018; stroke-linecap: round;
           filter: drop-shadow(0 0 8px rgba(232,184,92,.6)); stroke-dashoffset: 1; }
    .mnode { position: absolute; width: 0; height: 0; }
    .mnode i { position: absolute; left: -17px; top: -17px; width: 34px; height: 34px; border-radius: 50%; background: var(--gold);
               border: 6px solid #160f08; box-shadow: 0 0 0 3px var(--gold); transform: scale(0); }
    .mnode.origin i { background: #e0573a; box-shadow: 0 0 0 3px #e0573a; }
    .mnode.target i { width: 46px; height: 46px; left: -23px; top: -23px; background: #f6ecd6; box-shadow: 0 0 0 3px #f6ecd6; }
    .mnode span { position: absolute; left: -150px; width: 300px; top: 26px; text-align: center; font: 700 40px/1.1 var(--serif); color: var(--paper);
                  text-shadow: 0 3px 14px rgba(0,0,0,.8); }
    .mnode.target span { font-size: 50px; color: var(--gold); }
"""
            # paths are drawn with dasharray on normalised length; use a solid reveal mask instead of dashes
            css = css.replace("stroke-dasharray: 0.03 0.018;", "stroke-dasharray: 1;")
            js.append(f'    tl.fromTo("#{cid}-title", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, 0);')
            js.append(f'    tl.fromTo("#{cid}-board", {{opacity: 0, scale: 1.06}}, {{opacity: 1, scale: 1, duration: 0.6, ease: "expo.out"}}, 0);')
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "list":
            # items: [{text, at, strikeAt?}]
            items = []
            for i, it in enumerate(c["items"]):
                iid = f"{cid}-i{i}"
                items.append(f'      <div id="{iid}" class="li"><span class="x">✕</span><span class="tx">{esc(it["text"])}</span><span id="{iid}-s" class="strike"></span></div>')
                js.append(f'    tl.fromTo("#{iid}", {{opacity: 0, x: -60}}, {{opacity: 1, x: 0, duration: 0.4, ease: "expo.out"}}, {rel(it["at"], a)});')
                if it.get("strikeAt") is not None:
                    ts = rel(it["strikeAt"], a)
                    js.append(f'    tl.fromTo("#{iid}-s", {{scaleX: 0}}, {{scaleX: 1, duration: 0.3, ease: "power3.out"}}, {ts});')
                    js.append(f'    tl.to("#{iid}", {{opacity: 0.55, duration: 0.3}}, {fr(ts + 0.1)});')
            body.append(f"""    <div id="{cid}-title" class="kick" style="top:330px">{esc(c["title"])}</div>
    <div class="list">
{chr(10).join(items)}
    </div>""")
            if c.get("footer"):
                f_ = c["footer"]
                body.append(f'    <div id="{cid}-foot" class="big" style="top:{f_.get("y", 900)}px; font-size:{f_.get("size", 76)}px">{words(esc(f_["text"]))}</div>')
                js.append(words_in(f"#{cid}-foot", rel(f_["at"], a)))
            css += """
    .list { position: absolute; left: 130px; right: 130px; top: 420px; display: flex; flex-direction: column; gap: 22px; }
    .li { position: relative; display: flex; align-items: center; gap: 26px; padding: 26px 34px; border-radius: 22px;
          background: rgba(30,10,6,.62); border: 1px solid rgba(224,87,58,.45); }
    .li .x { font: 700 44px/1 var(--sans); color: #e0573a; }
    .li .tx { font: 700 52px/1.1 var(--serif); color: var(--paper); }
    .strike { position: absolute; left: 24px; right: 24px; top: 50%; height: 6px; margin-top: -3px; background: var(--gold);
              border-radius: 3px; transform: scaleX(0); transform-origin: 0 50%; box-shadow: 0 0 14px rgba(232,184,92,.7); }
"""
            js.insert(0, f'    tl.fromTo("#{cid}-title", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, 0);')
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "swap":
            # from {label, name}, to {label, name, at}, optional result {text, at}
            fr_, to = c["from"], c["to"]
            body.append(f"""    <div id="{cid}-title" class="kick" style="top:330px">{esc(c["title"])}</div>
    <div id="{cid}-A" class="pcard" style="top:420px"><small>{esc(fr_["label"])}</small><b>{esc(fr_["name"])}</b></div>
    <div id="{cid}-arrow" class="arrow">↓</div>
    <div id="{cid}-B" class="pcard gold" style="top:720px"><small>{esc(to["label"])}</small><b>{esc(to["name"])}</b></div>""")
            css += """
    .pcard { position: absolute; left: 150px; right: 150px; padding: 30px 30px 34px; border-radius: 26px; text-align: center;
             background: rgba(14,10,6,.72); border: 1px solid rgba(232,184,92,.35); }
    .pcard small { display: block; font: 700 28px/1 var(--sans); letter-spacing: .2em; text-transform: uppercase; color: var(--gold); }
    .pcard b { display: block; margin-top: 14px; font: 700 64px/1.05 var(--serif); color: var(--paper); }
    .pcard.gold { background: linear-gradient(160deg, rgba(240,196,112,.95), rgba(185,131,47,.95)); }
    .pcard.gold small, .pcard.gold b { color: #1a1206; }
    .arrow { position: absolute; left: 0; right: 0; top: 618px; text-align: center; font: 700 80px/1 var(--sans); color: var(--gold); }
"""
            js += [f'    tl.fromTo("#{cid}-title", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, 0);',
                   f'    tl.fromTo("#{cid}-A", {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: 0.45, ease: "expo.out"}}, 0.05);',
                   f'    tl.fromTo("#{cid}-arrow", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.35, ease: "expo.out"}}, {fr(rel(to["at"], a) - 0.2)});',
                   f'    tl.fromTo("#{cid}-B", {{opacity: 0, y: 50, scale: 0.9}}, {{opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.6)"}}, {rel(to["at"], a)});']
            if c.get("result"):
                r = c["result"]
                body.append(f'    <div id="{cid}-res" class="big" style="top:1000px; font-size:64px">{words(esc(r["text"]))}</div>')
                js.append(f'    tl.to(["#{cid}-A", "#{cid}-arrow", "#{cid}-B", "#{cid}-title"], {{y: -110, duration: 0.5, ease: "power2.inOut"}}, {fr(rel(r["at"], a) - 0.1)});')
                js.append(words_in(f"#{cid}-res", fr(rel(r["at"], a) + 0.15)))
                css = css.replace("top:1000px", "top:960px")
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "letter":
            # parchment letter: head, lines [{text, at}], seal at, stamp {text, at}
            lines = []
            for i, L in enumerate(c["lines"]):
                lines.append(f'<p id="{cid}-p{i}">{words(esc(L["text"]))}</p>')
                js.append(f'    tl.fromTo("#{cid}-p{i} .w", {{opacity: 0}}, {{opacity: 1, duration: 0.12, stagger: 0.09, ease: "none"}}, {rel(L["at"], a)});')
            body.append(f"""    <div id="{cid}-title" class="kick" style="top:320px">{esc(c.get("title", ""))}</div>
    <div id="{cid}-paper" class="paper">
      <div class="hd">{esc(c.get("head", ""))}</div>
      {"".join(lines)}
      <div id="{cid}-seal" class="seal"><span>ع</span></div>
    </div>""")
            css += """
    .paper { position: absolute; left: 170px; right: 170px; top: 400px; height: 560px; padding: 56px 54px; border-radius: 8px;
             background: radial-gradient(120% 90% at 30% 20%, #f3e2bd, #d9bc84 70%, #b8925a); color: #3b2410;
             box-shadow: 0 30px 80px rgba(0,0,0,.6), inset 0 0 60px rgba(120,70,20,.35); transform: rotate(-2deg); }
    .paper .hd { font: 700 30px/1 var(--sans); letter-spacing: .24em; text-transform: uppercase; color: #7a4a1c; margin-bottom: 26px; }
    .paper p { font: italic 700 60px/1.15 var(--serif); margin-bottom: 14px; }
    .paper p .em { color: #9b2414; }
    .seal { position: absolute; right: 40px; bottom: 34px; width: 130px; height: 130px; border-radius: 50%;
            background: radial-gradient(circle at 35% 30%, #d0442c, #7d160c 70%); box-shadow: 0 6px 18px rgba(0,0,0,.45), inset 0 0 0 8px rgba(0,0,0,.18);
            display: flex; align-items: center; justify-content: center; }
    .seal span { font: 700 64px/1 var(--serif); color: rgba(255,220,200,.75); }
"""
            js.insert(0, f'    tl.fromTo("#{cid}-paper", {{opacity: 0, y: 120, rotation: -8}}, {{opacity: 1, y: 0, rotation: -2, duration: 0.7, ease: "expo.out"}}, 0);')
            js.insert(0, f'    tl.fromTo("#{cid}-title", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, 0);')
            if c.get("sealAt") is not None:
                js.append(f'    tl.fromTo("#{cid}-seal", {{opacity: 0, scale: 2.2}}, {{opacity: 1, scale: 1, duration: 0.25, ease: "power4.in"}}, {rel(c["sealAt"], a)});')
            else:
                js.append(f'    tl.set("#{cid}-seal", {{opacity: 1}}, 0);')
            if c.get("stamp"):
                s = c["stamp"]
                body.append(f'    <div id="{cid}-stamp" class="stamp" style="left:{s.get("x", 330)}px; top:{s.get("y", 600)}px; font-size:130px">{esc(s["text"])}</div>')
                js.append(f'    tl.fromTo("#{cid}-stamp", {{opacity: 0, scale: 2.6}}, {{opacity: 1, scale: 1, duration: 0.22, ease: "power4.in"}}, {rel(s["at"], a)});')
                js.append(f'    tl.to("#{cid}-paper", {{x: 10, duration: 0.05, yoyo: true, repeat: 3}}, {fr(rel(s["at"], a) + 0.22)});')
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "counter":
            # from n0 to n1 over [at, at+dur]; unit; subs [{text, at}]
            body.append(f"""    <div id="{cid}-num" class="big cnum" style="top:330px">{c["n0"]}</div>
    <div id="{cid}-unit" class="kick" style="top:640px; font-size:44px">{esc(c["unit"])}</div>""")
            for i, s in enumerate(c.get("subs", [])):
                body.append(f'    <div id="{cid}-s{i}" class="big" style="top:{s.get("y", 760)}px; font-size:{s.get("size", 72)}px">{words(esc(s["text"]))}</div>')
                js.append(words_in(f"#{cid}-s{i}", rel(s["at"], a)))
            css += """
    .cnum { font-size: 300px !important; line-height: 1 !important; color: var(--gold) !important; font-variant-numeric: tabular-nums; }
"""
            t0 = rel(c["at"], a)
            js.insert(0, f'    tl.fromTo("#{cid}-num", {{opacity: 0, scale: 1.3, filter: "blur(12px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out"}}, 0);')
            js.insert(1, f'    tl.fromTo("#{cid}-unit", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, 0.2);')
            js.append(f'    const {cid.replace("-", "_")}_c = {{v: {c["n0"]}}};')
            js.append(f'    tl.fromTo({cid.replace("-", "_")}_c, {{v: {c["n0"]}}}, {{v: {c["n1"]}, duration: {c.get("dur", 1.6)}, ease: "power2.out", '
                      f'onUpdate: () => {{ document.querySelector("#{cid}-num").textContent = Math.round({cid.replace("-", "_")}_c.v); }}}}, {t0});')
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "date":
            body.append(f"""    <div id="{cid}-kick" class="kick" style="top:360px">{esc(c["kicker"])}</div>
    <div id="{cid}-d" class="big" style="top:430px; font-size:170px; color: var(--paper)">{esc(c["day"])}</div>
    <div id="{cid}-m" class="big" style="top:620px; font-size:110px; color: var(--gold)">{esc(c["month"])}</div>
    <div id="{cid}-rule" class="rule"></div>""")
            css += """
    .rule { position: absolute; left: 340px; right: 340px; top: 780px; height: 4px; background: linear-gradient(90deg, transparent, #c4412a, transparent); }
"""
            js += [f'    tl.fromTo("#{cid}-kick", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, 0);',
                   f'    tl.fromTo("#{cid}-d", {{opacity: 0, scale: 1.5, filter: "blur(16px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, {rel(c["dayAt"], a)});',
                   f'    tl.fromTo("#{cid}-m", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, {fr(rel(c["dayAt"], a) + 0.3)});',
                   f'    tl.fromTo("#{cid}-rule", {{scaleX: 0}}, {{scaleX: 1, duration: 0.6, ease: "expo.out"}}, {fr(rel(c["dayAt"], a) + 0.4)});']
            for i, s in enumerate(c.get("subs", [])):
                body.append(f'    <div id="{cid}-s{i}" class="big" style="top:{s.get("y", 840)}px; font-size:{s.get("size", 64)}px">{words(esc(s["text"]))}</div>')
                js.append(words_in(f"#{cid}-s{i}", rel(s["at"], a)))
            js.append(fade_out(f"#{cid}-wrap", d))

        elif k == "cover":
            # book cover with slow push, glow; optional side labels [{text, at}]
            body.append(f"""    <div id="{cid}-glow" class="glow"></div>
    <div id="{cid}-book" class="book" style="top:{c.get("y", 330)}px"><img src="{c["image"]}" alt=""></div>""")
            for i, s in enumerate(c.get("lines", [])):
                body.append(f'    <div id="{cid}-s{i}" class="{s.get("style", "big")}" style="top:{s["y"]}px; {"font-size:%dpx" % s.get("size", 64) if s.get("style", "big") == "big" else ""}">{words(esc(s["text"]))}</div>')
                if s.get("style") == "kick":
                    js.append(f'    tl.fromTo("#{cid}-s{i}", {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, {rel(s["at"], a)});')
                else:
                    js.append(words_in(f"#{cid}-s{i}", rel(s["at"], a)))
            h = c.get("h", 640)
            css += f"""
    .glow {{ position: absolute; left: 140px; right: 140px; top: {c.get("y", 330) + 40}px; height: {h}px;
             background: radial-gradient(50% 50% at 50% 50%, rgba(232,160,80,.45), rgba(232,160,80,0)); filter: blur(30px); }}
    .book {{ position: absolute; left: 50%; height: {h}px; aspect-ratio: 941 / 1453; transform: translateX(-50%); border-radius: 8px; overflow: hidden;
             box-shadow: 0 40px 90px rgba(0,0,0,.7), 0 0 0 2px rgba(255,230,180,.25); }}
    .book img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
"""
            js.insert(0, f'    tl.fromTo("#{cid}-book", {{opacity: 0, y: 90, rotationY: -25, scale: 0.9}}, {{opacity: 1, y: 0, rotationY: 0, scale: 1, duration: 0.8, ease: "expo.out"}}, 0);')
            js.insert(1, f'    tl.fromTo("#{cid}-book img", {{scale: 1.0}}, {{scale: 1.06, duration: {d}, ease: "none"}}, 0);')
            js.insert(2, f'    tl.fromTo("#{cid}-glow", {{opacity: 0}}, {{opacity: 1, duration: 1.0}}, 0.2);')
            js.append(fade_out(f"#{cid}-wrap", d))

        else:
            raise SystemExit(f"unknown story kind {k}")

        inner = "\n".join(body)
        html = f'    <div id="{cid}-wrap" class="st">\n{inner}\n    </div>'
        out[cid] = (a, d, scene(cid, css, html, "\n".join(js), d))

    # ------------------------------------------------ background + watermark (whole film)
    wm = E.get("watermark", {"text": "SYAFIQ STUDIO"})
    dust = []
    for i in range(26):  # deterministic drifting motes
        x = (i * 397) % 1080
        y = (i * 683) % 1920
        s = 3 + (i * 7) % 6
        dust.append(f'<i class="mote" id="mote{i}" style="left:{x}px; top:{y}px; width:{s}px; height:{s}px; opacity:{0.15 + (i % 5) * 0.07:.2f}"></i>')
    bjs = [f'    tl.fromTo("#mote{i}", {{y: 0, x: 0}}, {{y: {-120 - (i * 37) % 160}, x: {((i * 53) % 80) - 40}, duration: {total}, ease: "none"}}, 0);' for i in range(26)]
    bjs.append(f'    tl.fromTo("#bg-pat", {{rotation: 0, scale: 1.0}}, {{rotation: 12, scale: 1.12, duration: {total}, ease: "none"}}, 0);')
    pat = "".join(
        f'<polygon points="{" ".join(f"{540 + r * __import__("math").cos(__import__("math").radians(a0 + k2 * 45)):.1f},{960 + r * __import__("math").sin(__import__("math").radians(a0 + k2 * 45)):.1f}" for k2 in range(8))}" />'
        for r in (220, 380, 560, 760, 980) for a0 in (0, 22.5))
    bg_body = f"""    <div class="bgc"></div>
    <svg id="bg-pat" class="pat" viewBox="0 0 1080 1920" width="1080" height="1920">{pat}</svg>
    <div class="dust">{"".join(dust)}</div>
    <div class="vig"></div>"""
    bg_css = """
    .bgc { position: absolute; inset: 0; background: radial-gradient(90% 60% at 50% 38%, #2a1a0e 0%, #140c07 55%, #070403 100%); }
    .pat { position: absolute; left: 0; top: 0; opacity: .10; transform-origin: 540px 960px; }
    .pat polygon { fill: none; stroke: #e8b85c; stroke-width: 2; }
    .dust { position: absolute; inset: 0; }
    .mote { position: absolute; border-radius: 50%; background: #f3cf8a; filter: blur(1px); }
    .vig { position: absolute; inset: 0; background: radial-gradient(100% 70% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.7) 100%); }
"""
    wm_css = """
    .wm { position: absolute; right: 200px; top: 200px; display: flex; align-items: center; gap: 12px; opacity: 0; }
    .wm .mk { width: 50px; height: 50px; border-radius: 12px; border: 2px solid rgba(246,236,214,.8); display: flex; align-items: center; justify-content: center;
              font: 700 24px/1 var(--serif); color: rgba(246,236,214,.9); letter-spacing: .02em; }
    .wm .nm { font: 700 24px/1 var(--sans); letter-spacing: .3em; color: rgba(246,236,214,.75); }
"""
    out["bg"] = (0, total, scene("bg", bg_css, bg_body, "\n".join(bjs), total))
    wm_body = f'    <div id="wm" class="wm"><span class="mk">SS</span><span class="nm">{esc(wm["text"])}</span></div>'
    out["wm"] = (0, total, scene("wm", wm_css, wm_body, '    tl.fromTo("#wm", {opacity: 0}, {opacity: 1, duration: 0.6}, 0.3);', total))
    return out
