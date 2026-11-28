"""Illustrated 'review bab' layer for voice-only edits (the footage is black).

Look: dark green board, thin gold inset frame, gold pill label at the top, a headline
(the edl captions, drawn by build.py in headline style) and flat stick-figure scenes on a
ground line. Sahabah are never drawn as figures: they appear as a soft light with a name tag.

build.py calls make(E, T, fr, scene, esc, total) -> {cid: (start, dur, html)}.
edit.json:
  "frame": {"pill": "BAB 1 · ALFU SANATIN", "watermark": "SYAFIQ STUDIO"}
  "panels": [{"id", "in", "out", "items": [item, ...]}]
  item: {"t": kind, "x": centre x, "y": bottom y (default ground), "s": scale, "at": cue, "outAt": cue,
         ...kind fields}. Cues are film seconds or [src, source seconds].
"""
import json, math

GROUND = 1330
INK = "#0f2a20"
LINE = "#efe2c4"
SKIN = "#efd6a8"
GOLD = "#d9a53f"
GREEN = "#3f7d62"
NAVY = "#47548f"
RED = "#c9472f"


def person(kind="man", body=None, faces=("smile",), label=None, arm="up"):
    """Stick figure, 300 x 640 box, feet at the bottom. One <g class=f-NAME> per face."""
    body = body or {"man": GREEN, "rebel": "#7a3a2c", "saba": "#2b2a33", "rider": NAVY, "crowd": "#6b4a36"}.get(kind, GREEN)
    p = []
    # legs
    p.append(f'<line x1="130" y1="440" x2="108" y2="636" class="ln"/><line x1="170" y1="440" x2="192" y2="636" class="ln"/>')
    # arms
    p.append('<line x1="92" y1="300" x2="40" y2="420" class="ln"/><circle cx="38" cy="426" r="15" class="hand"/>')
    if arm == "up":
        p.append('<g class="arm"><line x1="208" y1="300" x2="268" y2="210" class="ln"/><circle cx="270" cy="204" r="15" class="hand"/></g>')
    elif arm == "point":
        p.append('<g class="arm"><line x1="208" y1="300" x2="290" y2="292" class="ln"/><circle cx="294" cy="292" r="15" class="hand"/></g>')
    else:
        p.append('<line x1="208" y1="300" x2="262" y2="420" class="ln"/><circle cx="264" cy="426" r="15" class="hand"/>')
    # body
    p.append(f'<rect x="88" y="262" width="124" height="200" rx="58" fill="{body}" class="ol"/>')
    # head
    p.append(f'<circle cx="150" cy="180" r="78" fill="{SKIN}" class="ol"/>')
    if kind == "man":       # white kopiah
        p.append(f'<path d="M78,150 Q150,70 222,150 L222,160 Q150,140 78,160 Z" fill="#f7f2e6" class="ol"/>'
                 '<line x1="92" y1="128" x2="208" y2="128" stroke="#cfc6b0" stroke-width="5"/>')
    elif kind == "rebel":   # red headband
        p.append(f'<path d="M74,146 Q150,112 226,146 L226,170 Q150,138 74,170 Z" fill="{RED}"/>'
                 f'<path d="M222,156 L258,176 L246,196 Z" fill="{RED}"/>')
    elif kind == "crowd":
        p.append(f'<path d="M74,150 Q150,92 226,150 L226,162 Q150,132 74,162 Z" fill="#a8743f"/>')
    elif kind == "rider":   # turban
        p.append(f'<path d="M76,160 Q80,84 150,84 Q220,84 224,160 Q150,128 76,160 Z" fill="#e8d3a0" class="ol"/>'
                 '<path d="M96,118 Q150,96 204,118" stroke="#c9b27c" stroke-width="6" fill="none"/>')
    elif kind == "saba":    # hood, face in shadow
        p.append('<path d="M60,250 Q50,90 150,82 Q250,90 240,250 Q205,215 150,212 Q95,215 60,250 Z" fill="#2b2a33" class="ol"/>')
    faces_svg = []
    for i, f in enumerate(faces):
        g = []
        eye_y = 186
        if f == "angry":
            g.append('<line x1="108" y1="160" x2="136" y2="172" stroke="#3b2a1a" stroke-width="7" stroke-linecap="round"/>'
                     '<line x1="192" y1="160" x2="164" y2="172" stroke="#3b2a1a" stroke-width="7" stroke-linecap="round"/>')
        if f == "worry":
            g.append('<line x1="108" y1="168" x2="136" y2="160" stroke="#3b2a1a" stroke-width="6" stroke-linecap="round"/>'
                     '<line x1="192" y1="168" x2="164" y2="160" stroke="#3b2a1a" stroke-width="6" stroke-linecap="round"/>')
        if f == "sly":
            g.append('<line x1="110" y1="184" x2="134" y2="184" stroke="#3b2a1a" stroke-width="7" stroke-linecap="round"/>'
                     '<line x1="166" y1="184" x2="190" y2="184" stroke="#3b2a1a" stroke-width="7" stroke-linecap="round"/>')
        else:
            g.append(f'<circle cx="122" cy="{eye_y}" r="8" fill="#3b2a1a"/><circle cx="178" cy="{eye_y}" r="8" fill="#3b2a1a"/>')
        mouth = {"smile": '<path d="M124,214 Q150,238 176,214" stroke="#3b2a1a" stroke-width="7" fill="none" stroke-linecap="round"/>',
                 "worry": '<path d="M128,230 Q150,214 172,230" stroke="#3b2a1a" stroke-width="7" fill="none" stroke-linecap="round"/>',
                 "angry": '<path d="M126,232 Q150,212 174,232" stroke="#3b2a1a" stroke-width="7" fill="none" stroke-linecap="round"/>',
                 "shock": '<ellipse cx="150" cy="224" rx="13" ry="17" fill="#3b2a1a"/>',
                 "sly": '<path d="M124,218 Q156,232 180,210" stroke="#3b2a1a" stroke-width="7" fill="none" stroke-linecap="round"/>',
                 "flat": '<line x1="130" y1="222" x2="170" y2="222" stroke="#3b2a1a" stroke-width="7" stroke-linecap="round"/>'}[f]
        g.append(mouth)
        faces_svg.append(f'<g class="face f-{f}" style="opacity:{1 if i == 0 else 0}">{"".join(g)}</g>')
    p += faces_svg
    return 300, 640, "".join(p)


def svg_house(label=None):
    return 320, 300, (f'<path d="M20,130 L160,10 L300,130 Z" fill="{GOLD}" class="ol"/>'
                      f'<rect x="45" y="128" width="230" height="168" fill="{SKIN}" class="ol"/>'
                      '<rect x="135" y="190" width="54" height="106" fill="#8a5a2e"/>'
                      f'<rect x="66" y="160" width="46" height="42" fill="#cfe3d6" class="ol2"/><rect x="210" y="160" width="46" height="42" fill="#cfe3d6" class="ol2"/>')


def svg_mushaf():
    return 300, 230, ('<path d="M40,230 L150,150 L260,230" stroke="#8a5a2e" stroke-width="12" fill="none"/>'
                      '<path d="M150,160 L150,40 Q90,20 20,40 L20,150 Q90,132 150,160 Z" fill="#f4ead2" class="ol"/>'
                      '<path d="M150,160 L150,40 Q210,20 280,40 L280,150 Q210,132 150,160 Z" fill="#f4ead2" class="ol"/>'
                      + "".join(f'<line x1="40" y1="{60 + i * 18}" x2="132" y2="{56 + i * 18}" stroke="#9c8a62" stroke-width="4"/>'
                                f'<line x1="168" y1="{56 + i * 18}" x2="260" y2="{60 + i * 18}" stroke="#9c8a62" stroke-width="4"/>' for i in range(5)))


def svg_fire():
    return 220, 220, ('<path d="M110,215 C30,200 30,120 80,70 C80,110 100,120 108,96 C112,60 100,30 130,0 C140,50 200,90 190,150 C185,200 150,215 110,215 Z" fill="#e8743a"/>'
                      '<path d="M112,212 C70,200 72,150 98,124 C104,150 120,150 124,130 C150,150 162,180 150,200 C142,210 128,214 112,212 Z" fill="#f6c453"/>')


def svg_letter(text=""):
    return 330, 250, (f'<g transform="rotate(-6 165 125)"><rect x="10" y="10" width="310" height="230" rx="10" fill="#f1e1bd" class="ol"/>'
                      + "".join(f'<line x1="40" y1="{60 + i * 34}" x2="{270 - (i % 2) * 50}" y2="{60 + i * 34}" stroke="#a88a58" stroke-width="7" stroke-linecap="round"/>' for i in range(4))
                      + f'<circle cx="262" cy="190" r="34" fill="{RED}" class="ol"/><circle cx="262" cy="190" r="20" fill="none" stroke="#f1c7b5" stroke-width="4"/></g>')


def svg_camel():
    return 440, 400, ('<g fill="#b98a4a" class="ol">'
                      '<path d="M60,220 Q70,120 150,140 Q180,60 230,130 Q270,70 320,150 Q350,190 340,230 L80,240 Q50,240 60,220 Z"/>'
                      '<path d="M330,190 Q370,150 360,80 L390,60 Q420,62 420,80 L400,86 Q395,170 350,220 Z"/></g>'
                      + "".join(f'<line x1="{x}" y1="236" x2="{x + d}" y2="400" class="ln" stroke="#8a6232"/>' for x, d in ((100, -8), (130, 8), (280, -8), (310, 8))))


def svg_calendar(num="40", unit="HARI"):
    return 280, 300, (f'<rect x="10" y="30" width="260" height="262" rx="24" fill="#f4ead2" class="ol"/>'
                      f'<rect x="10" y="30" width="260" height="70" rx="24" fill="{RED}"/><rect x="10" y="70" width="260" height="30" fill="{RED}"/>'
                      '<rect x="66" y="8" width="16" height="50" rx="8" fill="#3b2a1a"/><rect x="198" y="8" width="16" height="50" rx="8" fill="#3b2a1a"/>'
                      f'<text x="140" y="220" text-anchor="middle" class="calnum">{num}</text>'
                      f'<text x="140" y="270" text-anchor="middle" class="calunit">{unit}</text>')


def svg_nowater():
    return 220, 260, ('<path d="M110,20 C150,90 190,130 190,175 C190,220 154,250 110,250 C66,250 30,220 30,175 C30,130 70,90 110,20 Z" fill="#6fb6d9" class="ol"/>'
                      f'<line x1="20" y1="240" x2="200" y2="40" stroke="{RED}" stroke-width="18" stroke-linecap="round"/>')


def svg_coins():
    return 260, 200, ("".join(f'<ellipse cx="{x}" cy="{y}" rx="60" ry="22" fill="{GOLD}" class="ol"/>' for x, y in ((90, 176), (90, 150), (90, 124), (180, 176), (180, 150)))
                      + f'<circle cx="190" cy="70" r="56" fill="{GOLD}" class="ol"/><text x="190" y="90" text-anchor="middle" class="coin">$</text>')


def svg_light():
    return 300, 360, ('<defs><radialGradient id="lg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff3c8"/>'
                      '<stop offset=".35" stop-color="#f3cd6a" stop-opacity=".85"/><stop offset="1" stop-color="#f3cd6a" stop-opacity="0"/></radialGradient></defs>'
                      '<circle cx="150" cy="170" r="150" fill="url(#lg)" class="pulse"/>'
                      '<circle cx="150" cy="170" r="46" fill="#fff6dc"/>')


def svg_glyph(ch, color=GOLD, size=200):
    return size, size, f'<text x="{size / 2}" y="{size * 0.82}" text-anchor="middle" fill="{color}" style="font: 800 {size * 0.9:.0f}px Poppins, sans-serif">{ch}</text>'


def svg_crack():
    return 260, 120, f'<path d="M0,60 L70,40 L110,80 L160,30 L200,70 L260,50" stroke="{RED}" stroke-width="10" fill="none" stroke-linejoin="round"/>'


def svg_drop():
    return 120, 160, f'<path d="M60,10 C80,60 110,90 110,115 C110,140 88,156 60,156 C32,156 10,140 10,115 C10,90 40,60 60,10 Z" fill="{RED}"/>'


def svg_moon():
    return 200, 200, (f'<path d="M120,20 A80,80 0 1 0 180,140 A64,64 0 1 1 120,20 Z" fill="#f4ead2"/>'
                      '<circle cx="40" cy="40" r="6" fill="#f4ead2"/><circle cx="180" cy="30" r="5" fill="#f4ead2"/>')


def svg_icons():
    """Like / komen / simpan / kongsi row."""
    icons = [("♥", "Like", "#e0573a"), ("…", "Komen", "#efe2c4"), ("⚑", "Simpan", GOLD), ("➦", "Kongsi", "#efe2c4")]
    g = []
    for i, (ch, lab, col) in enumerate(icons):
        x = 70 + i * 160
        g.append(f'<g class="ic" id="ICN{i}"><circle cx="{x}" cy="70" r="58" fill="#f4ead2"/>'
                 f'<text x="{x}" y="92" text-anchor="middle" fill="{col if col != "#efe2c4" else INK}" style="font: 800 58px Poppins, sans-serif">{ch}</text>'
                 f'<text x="{x}" y="170" text-anchor="middle" class="iclab">{lab}</text></g>')
    return 620, 190, "".join(g)


KINDS = {"house": svg_house, "mushaf": svg_mushaf, "fire": svg_fire, "letter": svg_letter, "camel": svg_camel,
         "calendar": svg_calendar, "nowater": svg_nowater, "coins": svg_coins, "light": svg_light, "glyph": svg_glyph,
         "crack": svg_crack, "drop": svg_drop, "moon": svg_moon, "icons": svg_icons}

CSS = f"""
    .it {{ position: absolute; transform-origin: 50% 100%; }}
    .it svg {{ display: block; overflow: visible; }}
    .ln {{ stroke: {LINE}; stroke-width: 11; stroke-linecap: round; }}
    .hand {{ fill: {SKIN}; stroke: {LINE}; stroke-width: 5; }}
    .ol {{ stroke: {LINE}; stroke-width: 7; }}
    .ol2 {{ stroke: {LINE}; stroke-width: 4; }}
    .calnum {{ font: 800 130px/1 Poppins, sans-serif; fill: {INK}; }}
    .calunit {{ font: 800 34px/1 Poppins, sans-serif; fill: {RED}; letter-spacing: .12em; }}
    .coin {{ font: 800 64px/1 Poppins, sans-serif; fill: #6b4a14; }}
    .iclab {{ font: 600 28px/1 Poppins, sans-serif; fill: #efe2c4; }}
    .tag {{ position: absolute; transform: translateX(-50%); white-space: nowrap; padding: 8px 18px 7px; border-radius: 10px;
            font: 800 26px/1 Poppins, sans-serif; letter-spacing: .06em; text-transform: uppercase; }}
    .tag.solid {{ background: #f4ead2; color: {INK}; }}
    .tag.line {{ border: 3px dashed {GOLD}; color: {GOLD}; background: rgba(15,42,32,.6); }}
    .tag.red {{ border: 4px solid {RED}; color: #ffb29e; background: rgba(30,6,3,.85); transform: translateX(-50%) rotate(-6deg); font-size: 34px; }}
    .bubble {{ position: absolute; transform: translateX(-50%); max-width: 520px; padding: 22px 28px; border-radius: 26px; background: #f4ead2; color: {INK};
               font: 800 36px/1.2 Poppins, sans-serif; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,.3); }}
    .bubble::after {{ content: ""; position: absolute; left: var(--tail, 30%); bottom: -22px; border: 14px solid transparent; border-top: 18px solid #f4ead2; }}
    .bubble b {{ color: {RED}; }}
    .card {{ position: absolute; transform: translateX(-50%); padding: 26px 30px; border-radius: 22px; border: 3px solid {GOLD};
             background: rgba(10,30,22,.85); color: #f4ead2; text-align: center; }}
    .card .h {{ font: 800 30px/1.2 Poppins, sans-serif; color: {GOLD}; letter-spacing: .06em; text-transform: uppercase; }}
    .card .b {{ font: 600 38px/1.25 Poppins, sans-serif; margin-top: 10px; }}
    .card .b em {{ font-style: normal; color: {GOLD}; font-weight: 800; }}
    .cover {{ position: absolute; transform: translateX(-50%); border-radius: 8px; overflow: hidden; box-shadow: 0 30px 70px rgba(0,0,0,.55), 0 0 0 4px #f4ead2; }}
    .cover img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    .split {{ position: absolute; left: 150px; right: 150px; display: flex; gap: 16px; }}
    .split > div {{ flex: 1; height: 230px; border-radius: 22px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    .split .a {{ background: {GOLD}; color: {INK}; transform-origin: 0 50%; }}
    .split .b {{ background: #8e2f1e; color: #fbe3d6; transform-origin: 100% 50%; }}
    .split b {{ font: 800 96px/1 Poppins, sans-serif; }}
    .split span {{ font: 800 24px/1.2 Poppins, sans-serif; letter-spacing: .06em; text-align: center; padding: 0 14px; text-transform: uppercase; margin-top: 8px; }}
    .mapb {{ position: absolute; left: 130px; right: 130px; border-radius: 30px; border: 2px solid rgba(217,165,63,.5); background: rgba(8,24,18,.45); }}
    .mlnk {{ fill: none; stroke: {GOLD}; stroke-width: 6; stroke-linecap: round; }}
    .mnode {{ position: absolute; width: 0; height: 0; }}
    .mnode i {{ position: absolute; left: -16px; top: -16px; width: 32px; height: 32px; border-radius: 50%; background: {GOLD}; border: 6px solid {INK}; box-shadow: 0 0 0 3px {GOLD}; }}
    .mnode.o i {{ background: {RED}; box-shadow: 0 0 0 3px {RED}; }}
    .mnode.t i {{ background: #f4ead2; box-shadow: 0 0 0 3px #f4ead2; width: 44px; height: 44px; left: -22px; top: -22px; }}
    .mnode span {{ position: absolute; left: -140px; width: 280px; top: 28px; text-align: center; font: 800 34px/1.1 Poppins, sans-serif; color: #f4ead2; }}
    .mnode.t span {{ color: {GOLD}; font-size: 42px; }}
    .cta {{ position: absolute; left: 160px; right: 160px; padding: 30px; border-radius: 28px; border: 4px solid {GOLD}; background: rgba(10,30,22,.85); }}
    .cta .row {{ display: flex; align-items: center; gap: 22px; }}
    .cta .av {{ width: 96px; height: 96px; border-radius: 50%; border: 4px solid {GOLD}; display: flex; align-items: center; justify-content: center;
                font: 800 36px/1 Poppins, sans-serif; color: {GOLD}; background: {INK}; }}
    .cta .nm {{ font: 800 40px/1.1 Poppins, sans-serif; color: #f4ead2; }}
    .cta .sm {{ font: 600 26px/1.2 Poppins, sans-serif; color: #b9c9bd; margin-top: 6px; }}
    .cta .btn {{ margin-top: 26px; padding: 22px; border-radius: 999px; background: #f2c230; color: #2a1d00; text-align: center;
                 font: 800 38px/1 Poppins, sans-serif; letter-spacing: .04em; }}
"""


def make(E, T, fr, scene, esc, total):
    out = {}

    def rel(x, a):
        return fr(max(0.0, T(x) - a))

    for P in E.get("panels", []):
        cid = P["id"]
        a, b = T(P["in"]), T(P["out"])
        d = fr(b - a)
        body, js = [], []
        for n, it in enumerate(P["items"]):
            iid = f"{cid}-{n}"
            t = it["t"]
            x = it.get("x", 540)
            y = it.get("y", GROUND)
            s = it.get("s", 1.0)
            at = rel(it.get("at", 0.0), a) if it.get("at") is not None else 0.0
            pop = True
            if t == "person":
                w, h, inner = person(it.get("kind", "man"), it.get("body"), tuple([it.get("face", "smile")] + [f for _, f in it.get("faces", [])]),
                                     arm=it.get("arm", "up"))
                flip = ' transform="translate(300,0) scale(-1,1)"' if it.get("flip") else ""
                html = f'<div id="{iid}" class="it" style="left:{x - w * s / 2:.0f}px; top:{y - h * s:.0f}px; width:{w * s:.0f}px; height:{h * s:.0f}px"><svg viewBox="0 0 {w} {h}" width="{w * s:.0f}" height="{h * s:.0f}"><g{flip}>{inner}</g></svg></div>'
                if it.get("label"):
                    html += f'<div id="{iid}-lab" class="tag solid" style="left:{x}px; top:{y - h * s - 56:.0f}px">{esc(it["label"])}</div>'
                    js.append(f'    tl.fromTo("#{iid}-lab", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {fr(at + 0.15)});')
                for k, (fc, f) in enumerate(it.get("faces", [])):
                    tf = rel(fc, a)
                    js.append(f'    tl.set("#{iid} .face", {{opacity: 0}}, {tf});')
                    js.append(f'    tl.set("#{iid} .face:nth-of-type({k + 2})", {{opacity: 1}}, {tf});')
                if it.get("wave"):
                    js.append(f'    tl.fromTo("#{iid} .arm", {{rotation: 0}}, {{rotation: -10, svgOrigin: "208 300", duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: {max(1, int(d / 0.45) - 1)}}}, {fr(at + 0.3)});')
                body.append(html)
            elif t in KINDS:
                args = {k2: it[k2] for k2 in ("text", "num", "unit", "ch", "color", "size") if k2 in it}
                w, h, inner = KINDS[t](**args)
                body.append(f'<div id="{iid}" class="it" style="left:{x - w * s / 2:.0f}px; top:{y - h * s:.0f}px; width:{w * s:.0f}px; height:{h * s:.0f}px"><svg viewBox="0 0 {w} {h}" width="{w * s:.0f}" height="{h * s:.0f}">{inner}</svg></div>')
                if it.get("label"):
                    body.append(f'<div id="{iid}-lab" class="tag {it.get("labelStyle", "line")}" style="left:{x}px; top:{y + 18}px">{esc(it["label"])}</div>')
                    js.append(f'    tl.fromTo("#{iid}-lab", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {fr(at + 0.15)});')
                if t == "light":
                    js.append(f'    tl.fromTo("#{iid} .pulse", {{scale: 0.9, transformOrigin: "50% 50%"}}, {{scale: 1.08, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: {max(1, int(d / 1.1))}}}, {at});')
                if t == "fire":
                    js.append(f'    tl.fromTo("#{iid} svg", {{scaleY: 0.92, transformOrigin: "50% 100%"}}, {{scaleY: 1.06, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: {max(1, int(d / 0.22))}}}, {at});')
                if t == "icons":
                    pop = False
                    for k in range(4):
                        js.append(f'    tl.fromTo("#{iid} #ICN{k}", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(2)"}}, {fr(at + k * 0.18)});')
            elif t == "tag":
                body.append(f'<div id="{iid}" class="tag {it.get("style", "line")}" style="left:{x}px; top:{y}px">{esc(it["text"])}</div>')
            elif t == "bubble":
                txt = esc(it["text"]).replace("[", "<b>").replace("]", "</b>")
                body.append(f'<div id="{iid}" class="bubble" style="left:{x}px; top:{y}px; width:{it.get("w", 460)}px; --tail:{it.get("tail", "30%")}">{txt}</div>')
            elif t == "card":
                bb = esc(it["body"]).replace("[", "<em>").replace("]", "</em>")
                body.append(f'<div id="{iid}" class="card" style="left:{x}px; top:{y}px; width:{it.get("w", 700)}px"><div class="h">{esc(it.get("head", ""))}</div><div class="b">{bb}</div></div>')
            elif t == "cover":
                hh = it.get("h", 520)
                body.append(f'<div id="{iid}" class="cover" style="left:{x}px; top:{y - hh}px; height:{hh}px; aspect-ratio: {it.get("ar", "941 / 1453")}"><img src="{it["image"]}" alt=""></div>')
                js.append(f'    tl.fromTo("#{iid} img", {{scale: 1.0}}, {{scale: 1.06, duration: {fr(d - at)}, ease: "none"}}, {at});')
            elif t == "split":
                L, R = it["left"], it["right"]
                body.append(f'<div class="split" style="top:{y}px"><div id="{iid}-a" class="a"><b>{esc(L["n"])}</b><span>{esc(L["t"])}</span></div>'
                            f'<div id="{iid}-b" class="b"><b>{esc(R["n"])}</b><span>{esc(R["t"])}</span></div></div>')
                js.append(f'    tl.fromTo("#{iid}-a", {{scaleX: 0, opacity: 0}}, {{scaleX: 1, opacity: 1, duration: 0.5, ease: "expo.out"}}, {rel(L["at"], a)});')
                js.append(f'    tl.fromTo("#{iid}-b", {{scaleX: 0, opacity: 0}}, {{scaleX: 1, opacity: 1, duration: 0.5, ease: "expo.out"}}, {rel(R["at"], a)});')
                pop = False
            elif t == "map":
                nodes = {nd["id"]: nd for nd in it["nodes"]}
                top, hgt = it.get("top", 560), it.get("h", 640)
                paths = []
                for k, L in enumerate(it["links"]):
                    p, q = nodes[L["from"]], nodes[L["to"]]
                    mx, my = (p["x"] + q["x"]) / 2, (p["y"] + q["y"]) / 2 - 70
                    paths.append(f'<path id="{iid}-k{k}" class="mlnk" d="M{p["x"]},{p["y"]} Q{mx},{my} {q["x"]},{q["y"]}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
                    js.append(f'    tl.fromTo("#{iid}-k{k}", {{strokeDashoffset: 1}}, {{strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut"}}, {rel(L["at"], a)});')
                nh = []
                for nd in it["nodes"]:
                    nid = f'{iid}-n{nd["id"]}'
                    nh.append(f'<div id="{nid}" class="mnode {nd.get("k", "")}" style="left:{nd["x"]}px; top:{nd["y"]}px"><i></i><span>{esc(nd["label"])}</span></div>')
                    tn = rel(nd["at"], a)
                    js.append(f'    tl.fromTo("#{nid} i", {{scale: 0}}, {{scale: 1, duration: 0.4, ease: "back.out(2.2)"}}, {tn});')
                    js.append(f'    tl.fromTo("#{nid} span", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {fr(tn + 0.06)});')
                body.append(f'<div id="{iid}" class="mapb" style="top:{top}px; height:{hgt}px"></div>'
                            f'<svg class="it" style="left:0; top:0" viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(paths)}</svg>{"".join(nh)}')
                js.append(f'    tl.fromTo("#{iid}", {{opacity: 0, scale: 0.96}}, {{opacity: 1, scale: 1, duration: 0.5, ease: "expo.out"}}, {at});')
                pop = False
            elif t == "cta":
                body.append(f'<div id="{iid}" class="cta" style="top:{y}px"><div class="row"><div class="av">SS</div><div><div class="nm">{esc(it["name"])}</div>'
                            f'<div class="sm">{esc(it.get("sub", ""))}</div></div></div><div id="{iid}-btn" class="btn">{esc(it["button"])}</div></div>')
                if it.get("pulseAt") is not None:
                    tp = rel(it["pulseAt"], a)
                    js.append(f'    tl.to("#{iid}-btn", {{scale: 1.08, duration: 0.18, ease: "power2.out", yoyo: true, repeat: 3}}, {tp});')
            else:
                raise SystemExit(f"unknown item {t}")
            if pop:
                js.append(f'    tl.fromTo("#{iid}", {{opacity: 0, y: 40, scale: 0.85}}, {{opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.7)"}}, {at});')
            if it.get("outAt") is not None:
                to = rel(it["outAt"], a)
                js.append(f'    tl.to(["#{iid}", "#{iid}-lab"], {{opacity: 0, duration: 0.25, ease: "power2.in"}}, {to});')
            if it.get("shake") is not None:
                tsh = rel(it["shake"], a)
                js.append(f'    tl.fromTo("#{iid}", {{x: -8}}, {{x: 8, duration: 0.06, yoyo: true, repeat: 5, ease: "none"}}, {tsh});')
                js.append(f'    tl.set("#{iid}", {{x: 0}}, {fr(tsh + 0.4)});')
        html = f'    <div id="{cid}-wrap" class="pw">\n' + "\n".join("      " + h for h in body) + "\n    </div>"
        js.append(f'    tl.to("#{cid}-wrap", {{opacity: 0, duration: 0.2, ease: "power2.in"}}, {fr(d - 0.2)});')
        out[cid] = (a, d, scene(cid, CSS + "\n    .pw { position: absolute; inset: 0; }\n", html, "\n".join(js), d))

    # ------------------------------------------------ board: background, frame, pill, ground, watermark
    F = E.get("frame", {})
    bg_body = f"""    <div class="board"></div>
    <div class="frame"></div>
    <div id="pill" class="pill">{esc(F.get("pill", ""))}</div>
    <div class="ground"></div>"""
    bg_css = f"""
    .board {{ position: absolute; inset: 0; background: radial-gradient(110% 70% at 50% 40%, #1d4a38 0%, #143728 55%, #0b2219 100%); }}
    .frame {{ position: absolute; left: 44px; right: 44px; top: 44px; bottom: 44px; border: 2px solid rgba(217,165,63,.55); border-radius: 8px; }}
    .frame::after {{ content: ""; position: absolute; inset: 10px; border: 1px solid rgba(217,165,63,.22); border-radius: 4px; }}
    .pill {{ position: absolute; left: 50%; top: 238px; transform: translateX(-50%); white-space: nowrap; padding: 15px 38px 14px; border-radius: 999px;
             background: linear-gradient(180deg, #dcae4c, #b8862c); color: #20160a; font: 800 30px/1 Poppins, sans-serif; letter-spacing: .05em; text-transform: uppercase;
             box-shadow: 0 6px 20px rgba(0,0,0,.3); }}
    .ground {{ position: absolute; left: 120px; right: 120px; top: {GROUND}px; height: 3px; background: rgba(160,200,180,.22); border-radius: 2px; }}
"""
    out["bg"] = (0, total, scene("bg", bg_css, bg_body, '    tl.fromTo("#pill", {opacity: 0, y: -20}, {opacity: 1, y: 0, duration: 0.5, ease: "expo.out"}, 0.05);', total))
    wm_body = f'    <div id="wm" class="wm"><span class="mk">SS</span><span class="nm">{esc(F.get("watermark", "SYAFIQ STUDIO"))}</span></div>'
    wm_css = """
    .wm { position: absolute; left: 0; right: 0; top: 1420px; display: flex; justify-content: center; align-items: center; gap: 14px; opacity: .8; }
    .wm .mk { width: 54px; height: 54px; border-radius: 14px; border: 3px solid #d9a53f; display: flex; align-items: center; justify-content: center;
              font: 800 24px/1 Poppins, sans-serif; color: #d9a53f; }
    .wm .nm { font: 800 28px/1 Poppins, sans-serif; letter-spacing: .28em; color: rgba(244,234,210,.8); }
"""
    out["wm"] = (0, total, scene("wm", wm_css, wm_body, "", total))
    return out
