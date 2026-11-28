"""Panels for Alfu Sanatin Bab 1 (writes edit.json 'panels' and 'sfx'). Cues: (src, t) source anchors."""
import json
def c(t, s="c1"): return [s, t]
R = lambda x, face="angry", at=None, **k: dict(t="person", kind="rebel", x=x, face=face, at=at, **k)
LIGHT = lambda x, y, at=None, label="Sayidina Uthman r.a.", s=0.7, **k: dict(t="light", x=x, y=y, s=s, at=at, label=label, labelStyle="solid", **k)
P = [
 ("hook", c(0), c(4.6), [dict(t="mushaf", x=600, s=1.2, at=c(0.1)), dict(t="fire", x=600, y=1150, s=0.85, at=c(0.5)),
     R(250, "angry", c(0.2), arm="point", label="Penghasut"), dict(t="glyph", ch="!", x=860, y=900, at=c(1.2), color="#c9472f")]),
 ("benar", c(4.6), c(6.0), [dict(t="person", kind="man", x=360, face="shock", at=c(4.7), label="Kita"), dict(t="glyph", ch="?", x=720, y=1000, s=1.4, at=c(4.9))]),
 ("dua-belas", c(6.0), c(12.0), [LIGHT(540, 700, c(6.1)),
     dict(t="split", y=930, left=dict(n="6", t="tahun kegemilangan", at=c(8.84)), right=dict(n="6", t="tahun fitnah", at=c(10.5)))]),
 ("saba", c(12.0), c(16.2), [dict(t="person", kind="saba", x=380, face="sly", at=c(12.6), label="Abdullah bin Saba'"),
     dict(t="tag", text="dari Yaman", style="line", x=760, y=900, at=c(14.6)), dict(t="glyph", ch="?", x=760, y=860, s=0.8, at=c(13.4), outAt=c(14.5))]),
 ("peta", c(16.2), c(28.0), [dict(t="map", top=560, h=740, at=c(16.2), nodes=[
        dict(id="ym", label="Yaman", x=640, y=1200, k="o", at=c(16.25)), dict(id="ms", label="Mesir", x=250, y=660, at=c(17.4)),
        dict(id="kf", label="Kufah", x=800, y=640, at=c(17.9)), dict(id="bs", label="Basrah", x=860, y=860, at=c(18.5)),
        dict(id="mk", label="Mekah", x=470, y=1080, at=c(24.0)), dict(id="md", label="Madinah", x=520, y=880, k="t", at=c(26.0))],
     links=[dict(**{"from": "ym", "to": "ms"}, at=c(17.2)), dict(**{"from": "ym", "to": "kf"}, at=c(17.7)), dict(**{"from": "ym", "to": "bs"}, at=c(18.3)),
            dict(**{"from": "ms", "to": "md"}, at=c(26.1)), dict(**{"from": "kf", "to": "md"}, at=c(26.3)), dict(**{"from": "bs", "to": "md"}, at=c(26.5))]),
     dict(t="tag", text="35 Hijrah · musim haji", style="solid", x=540, y=500, at=c(21.8))]),
 ("tuduhan", c(28.0), c(37.6), [R(200, "angry", c(28.1), arm="point", s=0.85), R(380, "angry", c(28.3), s=0.85, arm="point"),
     dict(t="coins", x=780, y=720, s=0.9, at=c(29.3), outAt=c(35.2), label="terlalu kaya", labelStyle="red"),
     dict(t="tag", text="nepotisme", style="red", x=780, y=840, at=c(31.6), outAt=c(35.2)),
     dict(t="mushaf", x=780, y=1300, s=0.75, at=c(32.4), outAt=c(35.2)), dict(t="fire", x=780, y=1130, s=0.6, at=c(32.6), outAt=c(35.2)),
     LIGHT(780, 960, c(35.3)), dict(t="glyph", ch="✓", x=780, y=760, color="#7fc89a", at=c(35.5)),
     ]),
 ("gabenor", c(37.6), c(44.7), [R(220, "angry", c(37.7), s=0.85, faces=[(c(41.7), "sly")]), R(400, "angry", c(37.8), s=0.85, faces=[(c(41.7), "sly")]),
     dict(t="card", x=540, y=560, w=760, head="Tuntutan", body="Tukar gabenor Mesir kepada [Muhammad bin Abu Bakar]", at=c(37.9)),
     dict(t="bubble", x=720, y=900, w=380, text="Mesti dia [tolak]!", tail="10%", at=c(41.8))]),
 ("setuju", c(44.7), c(51.75), [LIGHT(760, 1000, c(44.8)), R(220, "sly", c(44.8), s=0.85, faces=[(c(49.64), "shock")]), R(400, "sly", c(44.9), s=0.85, faces=[(c(49.64), "shock")]),
     dict(t="bubble", x=700, y=560, w=520, text="“Jika itu kehendak penduduk [Mesir].”", tail="60%", at=c(47.4))]),
 ("utusan", c(51.75), c(62.4), [dict(t="camel", x=650, s=0.95, at=c(51.9)), dict(t="person", kind="rider", x=640, y=1130, s=0.62, face="sly", at=c(52.6), arm="up"),
     dict(t="tag", text="utusan khalifah?", style="line", x=650, y=600, at=c(54.0)),
     R(200, "angry", c(57.4), s=0.8, arm="point", label="Rombongan Mesir")]),
 ("surat", c(62.4), c(67.25), [dict(t="letter", x=540, y=1050, s=1.5, at=c(62.5)), dict(t="tag", text="cop mohor khalifah", style="solid", x=540, y=1080, at=c(63.4)),
     dict(t="card", x=540, y=1150, w=620, head="Isi surat", body="[Tahan] mereka. [Hukum] mereka.", at=c(65.1))]),
 ("surat-ali", c(67.25), c(70.35), [dict(t="letter", x=420, y=1100, s=1.1, at=c(67.3)), dict(t="tag", text="kononnya dari Sayidina Ali", style="line", x=540, y=1130, at=c(68.3)),
     dict(t="glyph", ch="?", x=800, y=950, at=c(68.8))]),
 ("serentak", c(70.35), c(77.9), [dict(t="map", top=560, h=700, at=c(70.4), nodes=[
        dict(id="ms", label="Mesir", x=250, y=700, at=c(70.4)), dict(id="kf", label="Kufah", x=800, y=660, at=c(72.5)),
        dict(id="bs", label="Basrah", x=860, y=900, at=c(73.2)), dict(id="md", label="Madinah", x=520, y=1000, k="t", at=c(70.5))],
     links=[dict(**{"from": "ms", "to": "md"}, at=c(70.6)), dict(**{"from": "kf", "to": "md"}, at=c(73.6)), dict(**{"from": "bs", "to": "md"}, at=c(73.8))]),
     dict(t="tag", text="serentak?!", style="red", x=540, y=1180, at=c(74.3)), dict(t="glyph", ch="?", x=830, y=1200, s=0.7, at=c(75.6))]),
 ("sumpah", c(77.9), c(83.65), [dict(t="light", x=540, y=1150, s=0.9, at=c(78.0)),
     dict(t="bubble", x=540, y=560, w=720, text="“Demi Allah, aku tidak pernah [menulis] apa pun kepada kamu!”", tail="46%", at=c(78.2))]),
 ("palsu", c(83.65), c(87.2), [dict(t="letter", x=640, y=1000, s=1.2, at=c(83.7)), dict(t="tag", text="PALSU", style="red", x=650, y=760, at=c(84.1), shake=c(84.3)),
     dict(t="person", kind="saba", x=230, face="sly", s=0.85, at=c(85.2), label="Dirancang")]),
 ("kepung", c(87.2), c(94.7), [dict(t="house", x=540, s=1.1, at=c(87.3)), LIGHT(540, 980, c(87.5), s=0.5, label=None),
     R(190, "angry", c(87.8), s=0.75, arm="point"), R(890, "angry", c(88.0), s=0.75, arm="point", flip=True),
     dict(t="calendar", num="40", unit="HARI", x=260, y=880, s=0.85, at=c(88.7), outAt=c(90.9)), dict(t="nowater", x=820, y=880, s=0.8, at=c(89.6), outAt=c(90.9)),
     dict(t="card", x=540, y=560, w=700, head="Para sahabat", body="mahu [mempertahankan] beliau", at=c(91.0), outAt=c(93.05)),
     dict(t="card", x=540, y=560, w=700, head="Sayidina Uthman r.a.", body="beliau [menolak]", at=c(93.1))]),
 ("darah", c(94.7), c(97.6), [dict(t="drop", x=540, y=1150, s=1.6, at=c(94.8)), dict(t="tag", text="tiada pertumpahan darah", style="line", x=540, y=1180, at=c(95.6))]),
 ("tarikh", c(97.6), c(102.0), [dict(t="calendar", num="18", unit="ZULHIJAH", x=540, y=1180, s=1.4, at=c(97.7)), dict(t="tag", text="35 Hijrah", style="solid", x=540, y=1210, at=c(99.3))]),
 ("mushaf", c(102.0), c(108.1), [dict(t="mushaf", x=540, s=1.5, at=c(102.1)), LIGHT(540, 900, c(102.1), label=None, s=0.8, outAt=c(105.4)),
     dict(t="drop", x=470, y=1080, s=0.45, at=c(103.3)), dict(t="drop", x=600, y=1110, s=0.35, at=c(103.6))]),
 ("fitnah-besar", c(108.1), c(115.15), [dict(t="person", kind="man", x=230, face="worry", s=0.8, at=c(108.2)), dict(t="person", kind="crowd", x=400, face="worry", s=0.8, at=c(108.3)),
     dict(t="card", x=640, y=600, w=520, head="Sayidina Ali r.a.", body="terpaksa menerima [baiah]", at=c(109.8)),
     dict(t="crack", x=760, y=1100, s=1.1, at=c(112.2)), dict(t="tag", text="fitnah lebih besar", style="red", x=760, y=1140, at=c(112.4))]),
 ("buku", c(115.15), c(120.25), [dict(t="cover", image="assets/images/cover1.jpg", x=540, y=1300, h=700, at=c(115.2)),
     dict(t="tag", text="garis masa sejarah Islam", style="solid", x=540, y=500, at=c(117.1))]),
 ("garis-masa", c(120.25), c(127.95), [dict(t="map", top=600, h=520, at=c(120.3), nodes=[
        dict(id="a", label="Khalifah Uthman", x=270, y=860, k="o", at=c(120.4)), dict(id="b", label="Khilafah Uthmaniyyah", x=810, y=860, k="t", at=c(121.6))],
     links=[dict(**{"from": "a", "to": "b"}, at=c(120.9))])]),
 ("gaya", c(127.95), c(133.3), [dict(t="person", kind="man", x=250, face="smile", s=0.85, at=c(128.0), label="Pembaca"),
     dict(t="cover", image="assets/images/cover1.jpg", x=700, y=1300, h=430, at=c(128.1)),
     dict(t="tag", text="santai", style="solid", x=440, y=560, at=c(128.6)), dict(t="tag", text="padat", style="solid", x=700, y=560, at=c(129.6)),
     dict(t="tag", text="riwayat", style="line", x=440, y=650, at=c(130.9)), dict(t="tag", text="dekat zaman kita", style="line", x=720, y=650, at=c(131.9))]),
 ("cermin", c(133.3), c(139.95), [dict(t="person", kind="man", x=280, face="shock", s=0.9, at=c(133.4), faces=[(c(138.0), "angry")]),
     dict(t="letter", x=740, y=1000, s=0.85, at=c(135.0)), dict(t="tag", text="berita palsu", style="red", x=740, y=760, at=c(135.6)),
     dict(t="tag", text="taksub", style="red", x=640, y=1100, at=c(138.0)), dict(t="tag", text="melatah", style="red", x=860, y=1180, at=c(138.9))]),
 ("kenali", c(0.25, "c2"), c(7.3, "c2"), [dict(t="person", kind="man", x=260, face="smile", at=c(0.3, "c2"), wave=True),
     dict(t="cover", image="assets/images/cover1.jpg", x=700, y=1300, h=560, at=c(2.6, "c2"))]),
 ("wajib", c(7.3, "c2"), c(12.55, "c2"), [dict(t="cover", image="assets/images/trilogy.jpg", ar="2813 / 1453", x=540, y=1150, h=420, at=c(9.4, "c2")),
     dict(t="tag", text="wajib dimiliki", style="solid", x=540, y=1180, at=c(10.6, "c2"))]),
 ("cta", c(12.55, "c2"), 137.0, [dict(t="cta", y=560, name="Syafiq Studio", sub="Review buku · Alfu Sanatin", button="TEKAN BEG KUNING 🛒", at=c(12.6, "c2"), pulseAt=c(13.0, "c2")),
     dict(t="icons", x=540, y=1100, at=c(14.2, "c2"))
     ]),
]
panels, sfx = [], []
for pid, a, b, items in P:
    for it in items:
        if it.get("at") is None: it.pop("at", None)
    panels.append(dict(id=pid, **{"in": a, "out": b}, items=items))
    sfx.append(dict(file="whoosh.mp3", at=a, lead=0.13, dur=0.6, vol=0.18))
    for it in items:
        if it.get("at") and it["t"] in ("tag", "glyph", "calendar", "coins", "drop"):
            sfx.append(dict(file="pop.mp3", at=it["at"], lead=0.1, dur=0.4, vol=0.22))
for at in (c(84.1), c(88.7), c(112.2), c(1.2)):
    sfx.append(dict(file="impact-bass-1.mp3", at=at, lead=0.04, dur=1.2, vol=0.3))
E = json.load(open("edit.json"))
E["panels"], E["sfx"] = panels, sfx
json.dump(E, open("edit.json", "w"), ensure_ascii=False, indent=1)
print(len(panels), "panels", len(sfx), "sfx")
