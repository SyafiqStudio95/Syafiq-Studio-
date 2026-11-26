#!/usr/bin/env python3
"""Build the Alfu Sanatin HyperFrames project from edit.json.

edit.json holds the edit decision list (source in/out points), captions,
motion-graphic cues and sound effects, all anchored to SOURCE time.
This script maps source time -> film time and writes index.html plus
the scene files in compositions/.

Run:  python3 tools/build.py   (from the project root)
"""
import json, html, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(ROOT, "edit.json"), encoding="utf8"))
FPS = 30
W, H = 1080, 1920


def fr(t):  # snap to frame grid
    return round(round(t * FPS) / FPS, 4)


# ---------------------------------------------------------------- timeline
# hook clips (muted b-roll), then the A-roll cuts, then a muted tail shot
hook_clips, t = [], 0.0
for i, s in enumerate(E["hook"]["clips"]):
    d = fr(fr(s["out"]) - fr(s["in"]))
    hook_clips.append({**s, "i": i, "start": fr(t), "dur": d})
    t = fr(t + d)
HOOK_DUR = t
OVER_VOICE = bool(E["hook"].get("overVoice"))  # hook visuals play over the opening voice line
if OVER_VOICE:
    t = 0.0
segs, runs = [], []
for i, s in enumerate(E["edl"]):
    d = fr(fr(s["out"]) - fr(s["in"]))
    seg = {**s, "i": i, "start": fr(t), "dur": d}
    segs.append(seg)
    if runs and runs[-1]["src"] == s["src"]:
        runs[-1]["segs"].append(seg)
        runs[-1]["dur"] = fr(runs[-1]["dur"] + d)
    else:
        runs.append({"src": s["src"], "start": fr(t), "dur": d, "segs": [seg]})
    t = fr(t + d)
AROLL_END = t
tail = E["tail"]
TAIL = {**tail, "start": t, "dur": fr(tail["dur"])}
TOTAL = fr(t + tail["dur"])


def at(src, st):
    """Film time for source time `st` in clip `src` (first kept segment that holds it)."""
    best = None
    for s in segs:
        if s["src"] != src:
            continue
        if s["in"] - 1e-6 <= st <= s["out"] + 1e-6:
            return fr(s["start"] + st - s["in"])
        if st < s["in"] and (best is None or s["in"] < best["in"]):
            best = s
    if best is None:
        raise SystemExit(f"source time {src}@{st} is not in the edit")
    return best["start"]


def T(x):
    """A cue time: number = film time, [src, t] = source anchor."""
    if isinstance(x, (int, float)):
        return fr(x)
    return at(x[0], x[1])


def esc(s):
    return html.escape(s, quote=True)


FONT_FACE = """
      @font-face { font-family: "EB Garamond"; src: url("assets/fonts/EBGaramond-400.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "EB Garamond"; src: url("assets/fonts/EBGaramond-700.woff2") format("woff2"); font-weight: 700; }
      @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-400.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight: 700; }"""

TOKENS = """
      :root {
        --ink: #0b1418;
        --paper: #f6ecd6;
        --gold: #e8b85c;
        --gold-deep: #b9832f;
        --ember: #c4512f;
        --serif: "EB Garamond", Georgia, serif;
        --sans: "Inter", Arial, sans-serif;
      }"""


TH = E.get("theme")
if TH:  # per-project fonts and colours: {"fonts": [[family, file, weight], ...], "tokens": {"--x": value}}
    FONT_FACE = "".join(f'\n      @font-face {{ font-family: "{f}"; src: url("{u}") format("woff2"); font-weight: {w}; }}' for f, u, w in TH["fonts"])
    TOKENS = "\n      :root {\n" + "".join(f"        {k}: {v};\n" for k, v in TH["tokens"].items()) + "      }"


def scene(cid, css, body, js, dur):
    return f"""<template>
  <style>{FONT_FACE}{TOKENS}
    #root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


scenes = {}  # cid -> (start, dur, html)

# ---------------------------------------------------------------- hook
hk = E["hook"]
hook_dur = HOOK_DUR
lines = hk["lines"]
body = []
js = []
for n, L in enumerate(lines):
    lid = f"hook-l{n}"
    cls = L.get("style", "kicker")
    words = L["text"].split(" ")
    spans = "".join(f'<span class="w">{esc(w)}</span> ' for w in words)
    body.append(f'    <div id="{lid}" class="hk {cls}" style="top:{L["y"]}px">{spans.strip()}</div>')
    a, b = fr(L["in"]), fr(L["out"])
    if cls == "slam":
        js.append(f'    tl.fromTo("#{lid}", {{opacity: 0, scale: 1.35, filter: "blur(14px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out"}}, {a});')
    else:
        js.append(f'    tl.fromTo("#{lid} .w", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out", stagger: 0.07}}, {a});')
    js.append(f'    tl.to("#{lid}", {{opacity: 0, filter: "blur(10px)", duration: 0.16, ease: "power2.in"}}, {fr(b - 0.16)});')
    js.append(f'    tl.set("#{lid}", {{opacity: 0}}, {b});')
css = """
    .hk { position: absolute; left: 120px; right: 120px; display: flex; flex-wrap: wrap; justify-content: center;
          column-gap: .26em; color: var(--paper); text-shadow: 0 6px 30px rgba(0,0,0,.55); }
    .hk .w { display: inline-block; }
    .kicker { font: 700 46px/1.1 var(--sans); letter-spacing: .32em; text-transform: uppercase; }
    .question { font: var(--em-style, italic) 700 112px/1.0 var(--serif); }
    .slam { font: 700 var(--slam-size, 210px)/0.95 var(--serif); color: var(--gold); letter-spacing: -.01em;
            text-shadow: 0 10px 50px rgba(0,0,0,.6), 0 0 80px rgba(232,184,92,.25); }
    .sub { font: var(--em-style, italic) 400 84px/1.05 var(--serif); }
    #hook-scrim { position: absolute; inset: 0;
      background: radial-gradient(120% 70% at 50% 40%, rgba(5,10,12,var(--hook-scrim, .15)), rgba(5,10,12,.78)); }
"""
body.insert(0, '    <div id="hook-scrim"></div>')
js.append(f'    tl.to("#hook-scrim", {{opacity: 0, duration: 0.25, ease: "power2.in"}}, {fr(hook_dur - 0.25)});')
scenes["hook"] = (0, hook_dur, scene("hook", css, "\n".join(body), "\n".join(js), hook_dur))

# ---------------------------------------------------------------- generic cards
def title_scene(cid, c):
    a, b = T(c["in"]), T(c["out"])
    d = fr(b - a)
    body = f"""    <div id="{cid}-scrim" class="topscrim"></div>
    <div id="{cid}-wrap" class="lock">
      <div id="{cid}-rule-l" class="rule"></div>
      <div id="{cid}-kick" class="kick">{esc(c["kicker"])}</div>
      <div id="{cid}-title" class="ttl">{" ".join('<span class="wd">' + "".join(f'<span class="ch">{esc(ch)}</span>' for ch in w) + '</span>' for w in c["title"].split())}</div>
      <div id="{cid}-sub" class="sub">{esc(c["sub"])}</div>
      <div id="{cid}-rule-r" class="rule"></div>
    </div>"""
    css = f"""
    .topscrim {{ position: absolute; left: 0; right: 0; top: 0; height: 1000px;
                 background: linear-gradient(180deg, rgba(5,10,12,.82) 0%, rgba(5,10,12,.62) 45%, rgba(5,10,12,0) 100%); }}
    .lock {{ position: absolute; left: 0; right: 0; top: {c.get("y", 330)}px; text-align: center; }}
    .kick {{ font: 700 34px/1 var(--sans); letter-spacing: .42em; color: var(--gold); text-transform: uppercase;
             text-shadow: 0 2px 16px rgba(0,0,0,.6); }}
    .ttl {{ font: 700 var(--title-size, 150px)/1.02 var(--serif); color: var(--paper); margin: 18px 120px 0; letter-spacing: .01em; text-wrap: balance;
            text-shadow: 0 8px 40px rgba(0,0,0,.65); }}
    .ttl .wd {{ display: inline-block; white-space: nowrap; }}
    .ttl .ch {{ display: inline-block; }}
    .sub {{ font: var(--em-style, italic) 400 54px/1.1 var(--serif); color: var(--paper); opacity: .92; margin-top: 14px;
            text-shadow: 0 4px 24px rgba(0,0,0,.7); }}
    .rule {{ width: 420px; height: 3px; margin: 22px auto; background: linear-gradient(90deg, transparent, var(--gold), transparent);
             transform-origin: 50% 50%; }}
"""
    js = f"""    tl.fromTo("#{cid}-scrim", {{opacity: 0}}, {{opacity: 1, duration: 0.35, ease: "power2.out"}}, 0.0);
    tl.to("#{cid}-scrim", {{opacity: 0, duration: 0.3, ease: "power2.in"}}, {fr(d - 0.3)});
    tl.fromTo("#{cid}-rule-l", {{scaleX: 0}}, {{scaleX: 1, duration: 0.5, ease: "expo.out"}}, 0.0);
    tl.fromTo("#{cid}-kick", {{opacity: 0, y: 16, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, 0.05);
    tl.fromTo("#{cid}-title .ch", {{opacity: 0.0, y: 26, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out", stagger: 0.035}}, 0.12);
    tl.fromTo("#{cid}-sub", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 0.92, filter: "blur(0px)", duration: 0.25, ease: "power4.out"}}, 0.55);
    tl.fromTo("#{cid}-rule-r", {{scaleX: 0}}, {{scaleX: 1, duration: 0.5, ease: "expo.out"}}, 0.5);
    tl.to("#{cid}-wrap", {{opacity: 0, filter: "blur(10px)", duration: 0.22, ease: "power2.in"}}, {fr(d - 0.24)});"""
    scenes[cid] = (a, d, scene(cid, css, body, js, d))


def chapter_scene(cid, c):
    """Volume card (top) + an animated era line with two or three nodes."""
    a, b = T(c["in"]), T(c["out"])
    d = fr(b - a)
    nodes = c["nodes"]
    n = len(nodes)
    X0, XW = 260, 510
    xs = [X0 + i * (XW / (n - 1)) for i in range(n)]
    node_html = []
    js = [
        f'    tl.fromTo("#{cid}-card", {{opacity: 0, y: -40}}, {{opacity: 1, y: 0, duration: 0.55, ease: "expo.out"}}, 0);',
        f'    tl.fromTo("#{cid}-num", {{opacity: 0, scale: 1.6, filter: "blur(10px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, 0.08);',
        f'    tl.fromTo("#{cid}-name", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out"}}, 0.25);',
        f'    tl.fromTo("#{cid}-tag", {{opacity: 0}}, {{opacity: 0.9, duration: 0.3, ease: "power2.out"}}, 0.4);',
        f'    tl.fromTo("#{cid}-rail", {{opacity: 0}}, {{opacity: 1, duration: 0.3, ease: "power2.out"}}, 0.35);',
    ]
    for i, nd in enumerate(nodes):
        nt = fr(max(0.45, T(nd["at"]) - a))
        node_html.append(
            f'      <div id="{cid}-n{i}" class="node" style="left:{xs[i]:.0f}px"><div class="dot"></div>'
            f'<div class="lbl"><b>{esc(nd["label"])}</b>{"<br>" + esc(nd["sub"]) if nd.get("sub") else ""}</div></div>')
        js.append(f'    tl.fromTo("#{cid}-n{i} .dot", {{scale: 0}}, {{scale: 1, duration: 0.45, ease: "back.out(2)"}}, {nt});')
        js.append(f'    tl.fromTo("#{cid}-n{i} .lbl", {{opacity: 0, y: 14, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out"}}, {fr(nt + 0.08)});')
        if i > 0:
            pt = fr(max(0.45, T(nodes[i - 1]["at"]) - a))
            frac0 = (xs[i - 1] - X0) / XW
            frac1 = (xs[i] - X0) / XW
            js.append(f'    tl.fromTo("#{cid}-fill", {{scaleX: {frac0:.3f}}}, {{scaleX: {frac1:.3f}, duration: {max(0.15, min(0.6, nt - pt - 0.02)):.2f}, ease: "power2.inOut", immediateRender: false}}, {fr(max(pt, nt - 0.6))});')
    js.append(f'    tl.to(["#{cid}-card", "#{cid}-rail"], {{opacity: 0, filter: "blur(10px)", duration: 0.22, ease: "power2.in"}}, {fr(d - 0.24)});')
    body = f"""    <div id="{cid}-card" class="card">
      {f'<div id="{cid}-num" class="num">{esc(c["num"])}</div>' if c.get("num") else f'<div id="{cid}-num"></div>'}
      <div class="meta">
        <div id="{cid}-name" class="name">{esc(c["name"])}</div>
        <div id="{cid}-tag" class="tag">{esc(c["tag"])}</div>
      </div>
    </div>
    <div id="{cid}-rail" class="rail">
      <div class="track"></div>
      <div id="{cid}-fill" class="fill"></div>
{chr(10).join(node_html)}
    </div>"""
    css = f"""
    .card {{ position: absolute; left: 110px; right: 190px; top: 300px; display: flex; align-items: center; gap: 34px;
             padding: 30px 40px; border-radius: 26px; background: rgba(9,16,19,.72); backdrop-filter: blur(22px);
             border: 1px solid rgba(232,184,92,.35); box-shadow: 0 20px 60px rgba(0,0,0,.35); }}
    .num {{ font: 700 112px/0.9 var(--serif); color: var(--gold); min-width: 120px; text-align: center; }}
    .name {{ font: 700 54px/1.05 var(--serif); color: var(--paper); }}
    .tag {{ font: 700 28px/1.3 var(--sans); letter-spacing: .16em; text-transform: uppercase; color: var(--gold); margin-top: 10px; opacity: .9; }}
    .rail {{ position: absolute; left: 0; right: 0; top: {c.get("railY", 560)}px; height: 220px; }}
    .track {{ position: absolute; left: 260px; width: 510px; top: 30px; height: 4px; background: rgba(246,236,214,.28); border-radius: 2px; }}
    .fill {{ position: absolute; left: 260px; width: 510px; top: 30px; height: 4px; border-radius: 2px; transform-origin: 0 50%;
             transform: scaleX(0); background: linear-gradient(90deg, var(--gold-deep), var(--gold)); box-shadow: 0 0 18px rgba(232,184,92,.6); }}
    .node {{ position: absolute; top: 14px; width: 0; }}
    .dot {{ position: absolute; left: -18px; top: 0; width: 36px; height: 36px; border-radius: 50%; background: var(--gold);
            border: 6px solid var(--ink); box-shadow: 0 0 0 3px var(--gold), 0 0 26px rgba(232,184,92,.7); transform: scale(0); }}
    .lbl {{ position: absolute; left: -112px; width: 224px; top: 54px; text-align: center; color: var(--paper);
            font: 400 28px/1.2 var(--sans); padding: 10px 8px 12px; border-radius: 14px; background: rgba(6,12,14,.62);
            backdrop-filter: blur(12px); }}
    .lbl b {{ font: 700 34px/1.1 var(--serif); color: var(--paper); }}
"""
    scenes[cid] = (a, d, scene(cid, css, body, "\n".join(js), d))


def trilogy_scene(cid, c):
    a, b = T(c["in"]), T(c["out"])
    d = fr(b - a)
    items, js = [], []
    for i, it in enumerate(c["items"]):
        it_t = fr(max(0, T(it["at"]) - a))
        items.append(f'      <div id="{cid}-i{i}" class="vol"><div class="r">{esc(it["num"])}</div><div class="l">{esc(it["label"])}</div></div>')
        js.append(f'    tl.fromTo("#{cid}-i{i}", {{opacity: 0, y: 60, scale: 0.7}}, {{opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.7)"}}, {it_t});')
    js.insert(0, f'    tl.fromTo("#{cid}-head", {{opacity: 0, y: 16, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, 0);')
    js.append(f'    tl.to("#{cid}-wrap", {{opacity: 0, filter: "blur(10px)", duration: 0.22, ease: "power2.in"}}, {fr(d - 0.24)});')
    body = f"""    <div id="{cid}-wrap" class="tri">
      <div id="{cid}-head" class="head">{esc(c["head"])}</div>
      <div class="row">
{chr(10).join(items)}
      </div>
    </div>"""
    css = """
    .tri { position: absolute; left: 0; right: 0; top: 320px; text-align: center; }
    .head { font: 700 36px/1 var(--sans); letter-spacing: .38em; color: var(--gold); text-transform: uppercase; text-shadow: 0 2px 16px rgba(0,0,0,.7); }
    .row { display: flex; justify-content: center; gap: 30px; margin-top: 34px; }
    .vol { width: 250px; padding: 26px 0 22px; border-radius: 22px; background: rgba(9,16,19,.74); backdrop-filter: blur(20px);
           border: 1px solid rgba(232,184,92,.4); box-shadow: 0 16px 50px rgba(0,0,0,.35); }
    .vol .r { font: 700 120px/0.9 var(--serif); color: var(--gold); }
    .vol .l { font: 700 30px/1.2 var(--sans); letter-spacing: .14em; color: var(--paper); text-transform: uppercase; margin-top: 12px; }
"""
    scenes[cid] = (a, d, scene(cid, css, body, "\n".join(js), d))


def cta_scene(cid, c):
    a = T(c["in"])
    d = fr(TOTAL - a)
    body = f"""    <div id="{cid}-scrim" class="scrim"></div>
    <div id="{cid}-wrap" class="cta">
      <div id="{cid}-kick" class="kick">{esc(c["kicker"])}</div>
      <div id="{cid}-title" class="ttl">{esc(c["title"])}</div>
      <div id="{cid}-by" class="by">{esc(c["by"])}</div>
      <div id="{cid}-btn" class="btn"><span>{esc(c["button"])}</span><svg viewBox="0 0 24 24" width="46" height="46"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
    </div>"""
    bt = fr(T(c["buttonAt"]) - a)
    pt = fr(T(c["pulseAt"]) - a)
    js = f"""    tl.fromTo("#{cid}-scrim", {{opacity: 0}}, {{opacity: 1, duration: 0.6, ease: "power2.inOut"}}, 0);
    tl.fromTo("#{cid}-kick", {{opacity: 0, y: 16, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}}, 0.1);
    tl.fromTo("#{cid}-title", {{opacity: 0, scale: 1.12, filter: "blur(12px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out"}}, 0.2);
    tl.fromTo("#{cid}-by", {{opacity: 0}}, {{opacity: 0.9, duration: 0.4, ease: "power2.out"}}, 0.55);
    tl.fromTo("#{cid}-btn", {{opacity: 0, y: 40, scale: 0.85}}, {{opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.8)"}}, {bt});
    tl.to("#{cid}-btn", {{scale: 1.12, duration: 0.16, ease: "power2.out"}}, {pt});
    tl.to("#{cid}-btn", {{scale: 1, duration: 0.4, ease: "power2.inOut"}}, {fr(pt + 0.16)});"""
    css = """
    .scrim { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(5,10,12,.78) 0%, rgba(5,10,12,.35) 42%, rgba(5,10,12,.15) 60%, rgba(5,10,12,.7) 100%); }
    .cta { position: absolute; left: 120px; right: 180px; top: 330px; text-align: center; }
    .kick { font: 700 34px/1 var(--sans); letter-spacing: .4em; color: var(--gold); text-transform: uppercase; }
    .ttl { font: 700 var(--cta-size, 150px)/0.95 var(--serif); color: var(--paper); margin-top: 22px; text-shadow: 0 10px 44px rgba(0,0,0,.6); }
    .by { font: var(--em-style, italic) 400 50px/1.1 var(--serif); color: var(--paper); margin-top: 14px; }
    .btn { display: inline-flex; align-items: center; gap: 18px; margin-top: 110px; padding: 30px 56px; border-radius: 999px;
           background: linear-gradient(180deg, var(--gold-hi, #f0c470), var(--gold-deep)); color: var(--btn-ink, var(--ink));
           font: 700 46px/1 var(--sans); letter-spacing: .12em; text-transform: uppercase;
           box-shadow: 0 18px 50px rgba(0,0,0,.45), 0 0 0 2px rgba(255,236,190,.5) inset; }
"""
    scenes[cid] = (a, d, scene(cid, css, body, js, d))


def feature_scene(cid, c):
    """Product cutaway: a rounded panel with a product image, a big stat and a short label."""
    a, b = T(c["in"]), T(c["out"])
    d = fr(b - a)
    stat = "".join(f'<span class="ch">{esc(ch) if ch != " " else "&nbsp;"}</span>' for ch in c["stat"])
    body = f"""    <div id="{cid}-scrim" class="fscrim"></div>
    <div id="{cid}-wrap" class="feat">
      <div id="{cid}-panel" class="panel"><img id="{cid}-img" src="{c["image"]}" alt="" style="object-position: {c.get("pos", "50% 60%")}"></div>
      <div id="{cid}-stat" class="stat">{stat}</div>
      <div id="{cid}-lbl" class="lbl">{esc(c["label"])}</div>
    </div>"""
    css = f"""
    .fscrim {{ position: absolute; inset: 0; background: radial-gradient(90% 60% at 50% 38%, rgba(6,14,22,.55), rgba(6,14,22,.82)); }}
    .feat {{ position: absolute; left: 120px; right: 240px; top: 300px; display: flex; flex-direction: column; align-items: center; }}
    .panel {{ width: var(--panel, 540px); height: var(--panel, 540px); border-radius: 40px; overflow: hidden; background: #eef3f8;
              box-shadow: 0 30px 80px rgba(0,0,0,.45), 0 0 0 3px rgba(255,255,255,.25); }}
    .panel img {{ width: 100%; height: 100%; object-fit: cover; display: block; transform-origin: 50% 50%; }}
    .stat {{ margin-top: 28px; font: 800 {c.get("statSize", 118)}px/1 var(--serif); color: var(--gold); letter-spacing: -.02em;
             text-shadow: 0 8px 30px rgba(0,0,0,.45); }}
    .stat .ch {{ display: inline-block; }}
    .lbl {{ margin-top: 14px; max-width: 640px; text-align: center; font: 600 44px/1.2 var(--serif); color: var(--paper);
            text-shadow: 0 4px 20px rgba(0,0,0,.6); }}
"""
    js = f"""    tl.fromTo("#{cid}-scrim", {{opacity: 0}}, {{opacity: 1, duration: 0.3, ease: "power2.out"}}, 0);
    tl.fromTo("#{cid}-panel", {{opacity: 0, y: 70, scale: 0.86, filter: "blur(10px)"}}, {{opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out"}}, 0.02);
    tl.fromTo("#{cid}-img", {{scale: 1.12}}, {{scale: 1.0, duration: {d}, ease: "power1.out"}}, 0);
    tl.fromTo("#{cid}-stat .ch", {{opacity: 0, y: 40, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "expo.out", stagger: 0.035}}, 0.22);
    tl.fromTo("#{cid}-lbl", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out"}}, 0.45);
    tl.to(["#{cid}-wrap", "#{cid}-scrim"], {{opacity: 0, filter: "blur(10px)", duration: 0.2, ease: "power2.in"}}, {fr(d - 0.22)});"""
    scenes[cid] = (a, d, scene(cid, css, body, js, d))


for c in E["cards"]:
    {"title": title_scene, "chapter": chapter_scene, "trilogy": trilogy_scene, "cta": cta_scene,
     "feature": feature_scene}[c["kind"]](c["id"], c)

# ---------------------------------------------------------------- captions
cap_start = hook_dur
cap_dur = fr(AROLL_END - cap_start)
# each edl cut carries "cap": "group one|group two" (*word* = emphasis).
# Group times are spread across the cut's speech by character count.
cap_groups = []
for s in segs:
    if not s.get("cap"):
        continue
    parts = [p.strip() for p in s["cap"].split("|") if p.strip()]
    sp_a = s["start"] + (s["a"] - fr(s["in"]))
    sp_b = s["start"] + (s["b"] - fr(s["in"]))
    total = sum(len(p) for p in parts)
    acc = 0
    for p in parts:
        ga = sp_a + (sp_b - sp_a) * acc / total
        acc += len(p)
        gb = sp_a + (sp_b - sp_a) * acc / total
        if gb <= hook_dur + 0.05:
            continue  # spoken under the hook: the hook's own lines carry it
        cap_groups.append([fr(max(s["start"], ga - 0.06, hook_dur)), fr(gb), p])
# a group holds until the next one opens (never past its cut + 0.35 s)
for k, g in enumerate(cap_groups):
    nxt = cap_groups[k + 1][0] if k + 1 < len(cap_groups) else AROLL_END
    g[1] = fr(min(nxt, max(g[1] + 0.12, min(nxt, g[1] + 0.35))))
groups, cjs = [], []
for gi, (ga, gb, text) in enumerate(cap_groups):
    a = fr(ga - cap_start)
    b = fr(gb - cap_start)
    if b <= a:
        raise SystemExit(f"caption {gi} has no time: {text}")
    spans = []
    for w in text.split(" "):
        is_em = "*" in w          # *word*, *word*, *word*. all mark emphasis
        w = w.replace("*", "")
        spans.append(f'<span class="{"w em" if is_em else "w"}">{esc(w)}</span>')
    gid = f"cap-{gi}"
    groups.append(f'    <div id="{gid}" class="grp"><div class="line">{" ".join(spans)}</div></div>')
    cjs.append(f'    tl.fromTo("#{gid}", {{opacity: 0}}, {{opacity: 1, duration: 0.01}}, {a});')
    cjs.append(f'    tl.fromTo("#{gid} .w", {{opacity: 0, y: 18, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.18, ease: "power4.out", stagger: 0.06}}, {a});')
    cjs.append(f'    tl.to("#{gid}", {{opacity: 0, duration: 0.1, ease: "power2.in"}}, {fr(b - 0.1)});')
    cjs.append(f'    tl.set("#{gid}", {{opacity: 0, visibility: "hidden"}}, {b});')
css = """
    .grp { position: absolute; left: 120px; right: var(--cap-right, 200px); bottom: 690px; text-align: center; opacity: 0; }
    .line { display: inline-flex; flex-wrap: wrap; justify-content: center; align-items: baseline; column-gap: 17px;
            padding: 14px 26px 18px; border-radius: 18px; background: rgba(6,12,14,.38); }
    .w { display: inline-block; font: 700 58px/1.18 var(--sans); color: #fffaf0; letter-spacing: -.01em;
         text-shadow: 0 3px 18px rgba(0,0,0,.55); }
    .w.em { font: var(--em-style, italic) 700 70px/1.0 var(--serif); color: var(--gold); letter-spacing: 0; }
"""
scenes["captions"] = (cap_start, cap_dur, scene("captions", css, "\n".join(groups), "\n".join(cjs), cap_dur))

# ---------------------------------------------------------------- write scenes
os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
for cid, (_, _, txt) in scenes.items():
    open(os.path.join(ROOT, "compositions", f"{cid}.html"), "w", encoding="utf8").write(txt)

# ---------------------------------------------------------------- root
SRC = E["sources"]
GRADE = E["grade"]
vids, wraps_js = [], []


def grade_attr(src):
    g = json.loads(json.dumps(GRADE["base"]))
    g.setdefault("adjust", {})["exposure"] = GRADE["exposure"].get(src, 0)
    return esc(json.dumps(g, separators=(",", ":")))


def cam(wid, vid, src_path, start, dur, mstart, audio, src_key, z=1.0, oy=46):
    vids.append(
        f'      <div id="{wid}" class="cam"><video id="{vid}" class="clip footage" src="{src_path}" '
        f'data-start="{start}" data-duration="{dur}" data-media-start="{mstart}" data-track-index="0" {audio} '
        f'data-color-grading="{grade_attr(src_key)}" playsinline></video></div>')
    wraps_js.append(f'    tl.set("#{wid}", {{scale: {z}, transformOrigin: "50% {oy}%"}}, 0);')


for h in hook_clips:
    wid = f"hookcam{h['i']}"
    cam(wid, f"hook{h['i']}", f"assets/video/hook_{h['i']}.mp4", h["start"], h["dur"], 0, "muted", h["src"], h.get("z", 1.0))
    if OVER_VOICE:
        vids[-1] = vids[-1].replace('class="cam"', 'class="cam hookcam"', 1)
    wraps_js.append(f'    tl.fromTo("#{wid}", {{scale: {h.get("z", 1.0) * 1.14:.3f}}}, {{scale: {h.get("z", 1.0)}, duration: 0.45, ease: "expo.out", immediateRender: false}}, {h["start"]});')

for r, run in enumerate(runs):
    wid = f"cam{r}"
    cam(wid, f"aroll{r}", f"assets/video/aroll_r{r}.mp4", run["start"], run["dur"], 0,
        'data-has-audio="true"', run["src"], run["segs"][0].get("z", 1.0))
    # entering a new source: a short settle from a push, caused by the whoosh on the cut
    wraps_js.append(f'    tl.fromTo("#{wid}", {{scale: {run["segs"][0].get("z", 1.0) * 1.12:.3f}, y: 70}}, {{scale: {run["segs"][0].get("z", 1.0)}, y: 0, duration: 0.5, ease: "expo.out", immediateRender: false}}, {run["start"]});')
    # jump cuts inside the run alternate framing so they read as edits, not glitches
    for s in run["segs"][1:]:
        wraps_js.append(f'    tl.set("#{wid}", {{scale: {s.get("z", 1.0)}}}, {s["start"]});')
    for s in run["segs"]:
        for p in s.get("punch", []):
            wraps_js.append(f'    tl.to("#{wid}", {{scale: {s.get("z", 1.0) * 1.07:.3f}, duration: 0.35, ease: "expo.out"}}, {T(p)});')

# overlays: kids-playing clips over the demo, muted, while the voice carries on
OV = E.get("overlays", [])
for i, o in enumerate(OV):
    st = fr(T(o["at"]))
    d = fr(o["dur"])
    wid = f"ov{i}"
    if o.get("mode", "pip") == "full":
        vids.append(f'      <div id="{wid}" class="cam ovfull"><video id="ovv{i}" class="clip footage" src="assets/video/ov_{i}.mp4" '
                    f'data-start="{st}" data-duration="{d}" data-media-start="0" data-track-index="1" muted '
                    f'data-color-grading="{grade_attr(o["src"])}" playsinline></video></div>')
        wraps_js.append(f'    tl.fromTo("#{wid}", {{scale: 1.12}}, {{scale: 1.0, duration: 0.5, ease: "expo.out", immediateRender: false}}, {st});')
    else:
        side = o.get("side", "left")
        x = 120 if side == "left" else 888 - 330 - 24  # TikTok-safe right edge, room for the tilt
        tag = f'<div class="pipTag">{esc(o["tag"])}</div>' if o.get("tag") else ""
        vids.append(f'      <div id="{wid}" class="pip" style="left:{x}px"><div class="pipFrame"><video id="ovv{i}" class="clip footage" src="assets/video/ov_{i}.mp4" '
                    f'data-start="{st}" data-duration="{d}" data-media-start="0" data-track-index="1" muted '
                    f'data-color-grading="{grade_attr(o["src"])}" playsinline></video></div>{tag}</div>')
        wraps_js.append(f'    tl.set("#{wid}", {{opacity: 0}}, 0);')
        wraps_js.append(f'    tl.fromTo("#{wid}", {{opacity: 0, scale: 0.6, rotation: {-6 if side == "left" else 6}, y: 40}}, {{opacity: 1, scale: 1, rotation: {-2 if side == "left" else 2}, y: 0, duration: 0.5, ease: "back.out(1.6)"}}, {st});')
        wraps_js.append(f'    tl.to("#{wid}", {{opacity: 0, scale: 0.85, duration: 0.22, ease: "power2.in"}}, {fr(st + d - 0.22)});')

cam("tailcam", "tail", "assets/video/tail.mp4", TAIL["start"], TAIL["dur"], 0, "muted", TAIL["src"], TAIL.get("z", 1.0))
wraps_js.append(f'    tl.fromTo("#tailcam", {{scale: 1.1}}, {{scale: 1.0, duration: {TAIL["dur"]}, ease: "power2.out", immediateRender: false}}, {TAIL["start"]});')

sfx, lane_end = [], []
for k, x in enumerate(sorted(E["sfx"], key=lambda x: T(x["at"]) - x.get("lead", 0))):
    st = fr(max(0, T(x["at"]) - x.get("lead", 0)))
    lane = next((i for i, e in enumerate(lane_end) if e <= st), None)
    if lane is None:
        lane_end.append(0); lane = len(lane_end) - 1
    lane_end[lane] = st + x["dur"]
    sfx.append(f'      <audio id="sfx{k:02d}" class="clip" src="assets/sfx/{x["file"]}" data-start="{st}" data-duration="{x["dur"]}" '
               f'data-volume="{x.get("vol", 0.35)}" data-track-index="{2 + lane}"></audio>')

hosts = []
for cid, (st, d, _) in scenes.items():
    kind = "captions" if cid == "captions" else "graphics"
    lane = 11 if cid == "captions" else 10
    hosts.append(f'      <div id="{cid}" class="layer" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                 f'data-start="{st}" data-duration="{d}" data-track-index="{lane}" data-track-kind="{kind}" data-width="{W}" data-height="{H}"></div>')

index = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{FONT_FACE}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #05090b; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .cam {{ position: absolute; inset: 0; }}
      .cam video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .layer {{ position: absolute; inset: 0; z-index: 10; }}
      .hookcam {{ z-index: 4; }}
      .ovfull {{ z-index: 2; }}
      .pip {{ position: absolute; top: 300px; width: 330px; z-index: 5; transform-origin: 50% 0%; }}
      .pipFrame {{ position: relative; width: 330px; height: 587px; border-radius: 28px; overflow: hidden;
                  border: 6px solid #fff; box-shadow: 0 24px 60px rgba(0,0,0,.45); background: #000; }}
      .pipFrame video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .pipTag {{ margin: -22px auto 0; position: relative; width: max-content; white-space: nowrap; padding: 10px 18px; border-radius: 999px;
                background: var(--pip-tag-bg, #ffd23f); color: var(--pip-tag-ink, #1d1400); font: 800 32px/1 "Poppins", Arial, sans-serif;
                box-shadow: 0 10px 24px rgba(0,0,0,.3); }}
      #captions {{ z-index: 20; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
      <!-- footage: one <video> per kept cut; wrappers carry punch-ins -->
{chr(10).join(vids)}
      <!-- motion graphics and captions -->
{chr(10).join(hosts)}
      <!-- sound effects -->
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(wraps_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w", encoding="utf8").write(index)

# a readable cut sheet
with open(os.path.join(ROOT, "EDIT.md"), "w", encoding="utf8") as f:
    f.write(f"# Alfu Sanatin — edit sheet\n\nFilm length: {TOTAL:.2f}s ({len(segs)} cuts)\n\n")
    f.write("| # | film in | dur | source | src in | src out | note |\n|---|---|---|---|---|---|---|\n")
    for s in segs:
        f.write(f"| {s['i']} | {s['start']:.2f} | {s['dur']:.2f} | {s['src']} | {s['in']:.2f} | {s['out']:.2f} | {s.get('note','')} |\n")
print(f"built: {TOTAL:.2f}s, {len(segs)} cuts in {len(runs)} runs, {len(scenes)} scenes, {len(cap_groups)} caption groups, {len(sfx)} sfx")
