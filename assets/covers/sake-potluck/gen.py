# -*- coding: utf-8 -*-
"""日本酒持ち寄り会 イベント表紙（1200x1600 / 3:4）を SVG で生成する"""
import json

W, H = 1200, 1600
TABLE_TOP = 1195

C = dict(
    night_top="#121a33", night_mid="#1d2747", night_low="#28324f",
    cream="#f7f1e4", amber="#ffc266", amber_deep="#f2913c",
    red="#cf4a43", red_dark="#a8352f",
    wood="#a9743f", wood_dark="#7d5029", wood_edge="#65401f",
    ink="#1b2340",
)
SKIN  = ["#f3cdab", "#eec09b", "#e3b088", "#f6d6b8"]
SKIN_S= ["#e0b691", "#dbaa84", "#cf9a74", "#e5c2a1"]
HAIR  = ["#1f1714", "#2b201b", "#3a2a20", "#241b18", "#463125"]
CLOTH = [("#4a6f96", "#3a5878"), ("#c0614a", "#9d4a36"), ("#6e8a6a", "#566e53"),
         ("#8a6e9e", "#6f567f"), ("#d09a4e", "#ae7c39"), ("#4d7f7d", "#3b6462")]

def esc(t):
    return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---------------------------------------------------------------- 髪型
def hair(style, col):
    """(後ろ髪, 前髪) を返す。後ろ髪は体より先に描く。"""
    back, front = "", ""
    if style == "short":
        front = (f'<path d="M -40,2 C -43,-34 -22,-49 0,-49 C 22,-49 43,-34 40,2 '
                 f'C 35,-18 26,-27 12,-28 C 0,-15 -19,-12 -31,-19 C -36,-13 -38,-5 -40,2 Z" fill="{col}"/>')
    elif style == "quiff":
        front = (f'<path d="M -40,0 C -44,-37 -19,-52 4,-51 C 26,-50 43,-35 40,0 '
                 f'C 33,-21 23,-31 6,-29 C -8,-20 -25,-16 -33,-23 C -37,-14 -38,-6 -40,0 Z" fill="{col}"/>')
    elif style == "bob":
        back = (f'<path d="M -47,52 C -50,-18 -35,-55 0,-55 C 35,-55 50,-18 47,52 '
                f'C 34,58 30,40 31,22 C 20,34 -20,34 -31,22 C -30,40 -34,58 -47,52 Z" fill="{col}"/>')
        front = (f'<path d="M -41,-6 C -39,-38 -21,-51 0,-51 C 21,-51 39,-38 41,-6 '
                 f'C 34,-26 19,-33 0,-31 C -17,-29 -34,-23 -41,-6 Z" fill="{col}"/>')
    elif style == "long":
        back = (f'<path d="M -45,190 C -54,60 -52,-18 -38,-40 C -26,-57 26,-57 38,-40 '
                f'C 52,-18 54,60 45,190 C 25,176 -25,176 -45,190 Z" fill="{col}"/>')
        front = (f'<path d="M -41,-8 C -40,-40 -22,-52 0,-52 C 22,-52 40,-40 41,-8 '
                 f'C 32,-30 14,-34 -4,-30 C -20,-26 -34,-22 -41,-8 Z" fill="{col}"/>')
    elif style == "ponytail":
        back = (f'<path d="M -34,-26 C -60,-28 -76,-2 -70,34 C -65,64 -44,62 -44,40 '
                f'C -44,16 -38,-4 -34,-26 Z" fill="{col}"/>')
        front = (f'<path d="M -40,-2 C -42,-36 -21,-50 0,-50 C 21,-50 42,-36 40,-2 '
                 f'C 33,-24 18,-31 0,-30 C -18,-29 -33,-22 -40,-2 Z" fill="{col}"/>')
    elif style == "bun":
        back = (f'<circle cx="0" cy="-58" r="17" fill="{col}"/>')
        front = (f'<path d="M -40,0 C -42,-35 -21,-49 0,-49 C 21,-49 42,-35 40,0 '
                 f'C 34,-22 19,-30 0,-29 C -19,-28 -34,-22 -40,0 Z" fill="{col}"/>')
    return back, front

# ---------------------------------------------------------------- 小物
def ochoko(x, y, sc=1.0):
    return (f'<g transform="translate({x},{y}) scale({sc})">'
            f'<path d="M -17,-11 L 17,-11 L 12,12 Q 0,18 -12,12 Z" fill="{C["cream"]}"/>'
            f'<ellipse cx="0" cy="-11" rx="17" ry="5" fill="#e9dcc4"/>'
            f'<ellipse cx="0" cy="-10" rx="13" ry="3.6" fill="#f0b45e"/>'
            f'<path d="M -13,-2 L 13,-2" stroke="#3f6fa8" stroke-width="2.4" opacity=".65"/>'
            f'</g>')

def bottle(x, y, sc=1.0, body="#22412f", label="純米", tall=False):
    hgt = 150 if tall else 96
    return (f'<g transform="translate({x},{y}) scale({sc})">'
            f'<path d="M -34,0 L 34,0 L 34,{-hgt+34} C 34,{-hgt+16} 12,{-hgt+8} 12,{-hgt-6} '
            f'L 12,{-hgt-34} L -12,{-hgt-34} L -12,{-hgt-6} C -12,{-hgt+8} -34,{-hgt+16} -34,{-hgt+34} Z" fill="{body}"/>'
            f'<path d="M -26,{-hgt+40} L -26,-10" stroke="#ffffff" stroke-width="7" opacity=".16" stroke-linecap="round"/>'
            f'<rect x="-13" y="{-hgt-42}" width="26" height="12" rx="3" fill="{C["red"]}"/>'
            f'<rect x="-27" y="{-hgt+44}" width="54" height="{hgt-58}" rx="3" fill="{C["cream"]}"/>'
            f'<text x="0" y="{-hgt+66}" text-anchor="middle" font-family="Noto Serif JP" font-weight="900" '
            f'font-size="19" fill="{C["ink"]}" writing-mode="tb" letter-spacing="3">{esc(label)}</text>'
            f'</g>')

def tokkuri(x, y, sc=1.0):
    return (f'<g transform="translate({x},{y}) scale({sc})">'
            f'<path d="M 0,0 C -30,0 -38,-16 -36,-34 C -34,-52 -14,-56 -13,-70 L -13,-86 '
            f'C -13,-94 13,-94 13,-86 L 13,-70 C 14,-56 34,-52 36,-34 C 38,-16 30,0 0,0 Z" fill="#f4efe3"/>'
            f'<path d="M -34,-28 C -12,-20 12,-20 34,-28" stroke="#3f6fa8" stroke-width="4" fill="none" opacity=".7"/>'
            f'<path d="M -13,-80 L 13,-80" stroke="#3f6fa8" stroke-width="4" opacity=".7"/>'
            f'<path d="M -24,-42 C -20,-52 -12,-58 -8,-60" stroke="#ffffff" stroke-width="5" fill="none" opacity=".8" stroke-linecap="round"/>'
            f'</g>')

def masu(x, y, sc=1.0):
    return (f'<g transform="translate({x},{y}) scale({sc})">'
            f'<path d="M -34,-40 L 34,-40 L 27,6 L -27,6 Z" fill="#d8b27c"/>'
            f'<path d="M -34,-40 L 0,-52 L 34,-40 L 0,-28 Z" fill="#e8c795"/>'
            f'<path d="M -27,-37 L 0,-46 L 27,-37 L 0,-28 Z" fill="#efd9a0"/>'
            f'<path d="M -22,-35 L 0,-42 L 22,-35 L 0,-28 Z" fill="#f3e2b7"/>'
            f'</g>')

def edamame(x, y, sc=1.0):
    pods = ""
    for i, (dx, dy, rot) in enumerate([(-22,-8,-18),(2,-14,8),(20,-2,26),(-6,2,-4)]):
        pods += (f'<g transform="translate({dx},{dy}) rotate({rot})">'
                 f'<rect x="-19" y="-7" width="38" height="14" rx="7" fill="#6f9b4a"/>'
                 f'<circle cx="-8" cy="0" r="4.2" fill="#8fbb66"/><circle cx="4" cy="0" r="4.2" fill="#8fbb66"/>'
                 f'</g>')
    return (f'<g transform="translate({x},{y}) scale({sc})">'
            f'<ellipse cx="0" cy="6" rx="58" ry="19" fill="#efe7d6"/>'
            f'<ellipse cx="0" cy="2" rx="50" ry="15" fill="#e2d6be"/>{pods}</g>')

# ---------------------------------------------------------------- 人物
def person(hx, hy, s, i, style, cloth_i, skin_i, hair_i, torso_len,
           raise_side=1, hold="cup", eyes="smile", tilt=0.0, blush=True, low_arm=True):
    sk, sks = SKIN[skin_i], SKIN_S[skin_i]
    hc = HAIR[hair_i]
    cl, cld = CLOTH[cloth_i]
    hb, hf = hair(style, hc)
    L = torso_len
    o = -raise_side  # 下ろしている腕の側

    g  = f'<g transform="translate({hx},{hy}) scale({s})">'
    g += hb
    # 体
    g += (f'<path d="M -78,{L} C -78,120 -70,80 -34,66 L 34,66 C 70,80 78,120 78,{L} Z" fill="{cl}"/>')
    g += f'<path d="M -22,60 Q 0,94 22,60 Q 11,55 0,55 Q -11,55 -22,60 Z" fill="{cld}"/>'
    # 下ろした腕
    if low_arm:
        aw = min((TABLE_TOP - 34 - hy) / s, L - 56)
        g += (f'<path d="M {o*60},92 C {o*84},{92+(aw-92)*0.45:.0f} {o*86},{92+(aw-92)*0.78:.0f} {o*84},{aw:.0f}" '
              f'stroke="{cl}" stroke-width="27" fill="none" stroke-linecap="round"/>'
              f'<circle cx="{o*85}" cy="{aw+13:.0f}" r="14" fill="{sk}"/>')
    # 首
    g += f'<path d="M -13,20 L 13,20 L 13,62 L -13,62 Z" fill="{sks}"/>'
    # 頭
    g += f'<g transform="rotate({tilt})">'
    g += f'<circle cx="-37" cy="6" r="9" fill="{sks}"/><circle cx="37" cy="6" r="9" fill="{sks}"/>'
    g += f'<ellipse cx="0" cy="0" rx="38" ry="42" fill="{sk}"/>'
    g += hf
    if eyes == "smile":
        for sd in (-1, 1):
            g += (f'<path d="M {sd*14-9},-2 q 9,-12 18,0" stroke="#33231d" stroke-width="4.6" '
                  f'fill="none" stroke-linecap="round"/>')
    else:
        for sd in (-1, 1):
            g += f'<ellipse cx="{sd*14}" cy="-3" rx="4.6" ry="6.2" fill="#33231d"/>'
            g += f'<circle cx="{sd*14+1.6}" cy="-5.4" r="1.7" fill="#ffffff" opacity=".9"/>'
    if blush:
        g += (f'<ellipse cx="-26" cy="12" rx="11" ry="6.4" fill="#e8756a" opacity=".38"/>'
              f'<ellipse cx="26" cy="12" rx="11" ry="6.4" fill="#e8756a" opacity=".38"/>')
    g += f'<path d="M -12,15 Q 0,32 12,15 Q 0,22 -12,15 Z" fill="#7a4038"/>'
    g += '</g>'
    # 上げた腕
    r = raise_side
    g += (f'<path d="M {r*56},88 C {r*98},76 {r*104},44 {r*100},22" stroke="{cl}" '
          f'stroke-width="28" fill="none" stroke-linecap="round"/>'
          f'<path d="M {r*100},26 C {r*98},-8 {r*94},-26 {r*92},-42" stroke="{sk}" '
          f'stroke-width="21" fill="none" stroke-linecap="round"/>'
          f'<circle cx="{r*92}" cy="-46" r="15" fill="{sk}"/>')
    if hold == "cup":
        g += ochoko(r*92, -64, 0.95)
    elif hold == "masu":
        g += masu(r*92, -50, 0.62)
    else:  # bottle
        g += bottle(r*92, -52, 0.52, body="#5c3a22", label="純米")
    g += '</g>'
    return g

# ---------------------------------------------------------------- 背景
def bg():
    s  = f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    s += f'<rect width="{W}" height="{H}" fill="url(#seigaiha)" opacity=".055"/>'
    # 提灯
    for cx, cy, sc in [(128, 150, 1.0), (1078, 226, 0.88), (952, 78, 0.52)]:
        s += (f'<line x1="{cx}" y1="0" x2="{cx}" y2="{cy-58*sc}" stroke="#0d1527" stroke-width="3"/>'
              f'<g transform="translate({cx},{cy}) scale({sc})">'
              f'<ellipse cx="0" cy="0" rx="86" ry="86" fill="{C["amber"]}" opacity=".16"/>'
              f'<rect x="-20" y="-62" width="40" height="12" rx="3" fill="#2a2a2a"/>'
              f'<path d="M 0,-52 C 46,-52 56,-26 56,0 C 56,26 46,52 0,52 C -46,52 -56,26 -56,0 C -56,-26 -46,-52 0,-52 Z" fill="{C["red"]}"/>'
              f'<g stroke="{C["red_dark"]}" stroke-width="2.6" opacity=".55">'
              f'<path d="M -55,-20 C -20,-14 20,-14 55,-20"/><path d="M -57,0 C -20,6 20,6 57,0"/>'
              f'<path d="M -55,20 C -20,26 20,26 55,20"/></g>'
              f'<rect x="-18" y="46" width="36" height="12" rx="3" fill="#2a2a2a"/>'
              f'<text x="0" y="14" text-anchor="middle" font-family="Noto Serif JP" font-weight="900" '
              f'font-size="44" fill="{C["cream"]}">酒</text></g>')
    # 灯りのにじみ
    s += f'<circle cx="600" cy="880" r="470" fill="url(#glow)"/>'
    return s

def table():
    s  = f'<rect x="-20" y="{TABLE_TOP}" width="{W+40}" height="108" fill="{C["wood"]}"/>'
    s += f'<rect x="-20" y="{TABLE_TOP}" width="{W+40}" height="14" fill="#c08a52"/>'
    for gx in range(-10, W + 40, 63):
        s += (f'<path d="M {gx},{TABLE_TOP+16} L {gx+9},{TABLE_TOP+106}" stroke="{C["wood_edge"]}" '
              f'stroke-width="2" opacity=".18"/>')
    s += f'<rect x="-20" y="{TABLE_TOP+108}" width="{W+40}" height="46" fill="{C["wood_dark"]}"/>'
    s += f'<rect x="-20" y="{TABLE_TOP+154}" width="{W+40}" height="10" fill="{C["wood_edge"]}" opacity=".8"/>'
    return s

# ---------------------------------------------------------------- 組み立て
def build(fonts):
    faces = ""
    for f in fonts:
        faces += (f"@font-face{{font-family:'{f['family']}';font-style:normal;"
                  f"font-weight:{f['weight']};src:url(data:font/woff2;base64,{f['b64']}) format('woff2');}}\n")

    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-kerning="none">')
    o.append(f'<defs><style type="text/css"><![CDATA[\n{faces}]]></style>')
    o.append(f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{C["night_top"]}"/>'
             f'<stop offset=".55" stop-color="{C["night_mid"]}"/>'
             f'<stop offset="1" stop-color="{C["night_low"]}"/></linearGradient>')
    o.append(f'<radialGradient id="glow"><stop offset="0" stop-color="#ffb457" stop-opacity=".34"/>'
             f'<stop offset=".6" stop-color="#ff9f43" stop-opacity=".12"/>'
             f'<stop offset="1" stop-color="#ff9f43" stop-opacity="0"/></radialGradient>')
    o.append(f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{C["night_top"]}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{C["night_top"]}" stop-opacity=".75"/></linearGradient>')
    o.append('<radialGradient id="vignette" cx=".5" cy=".54" r=".72">'
             '<stop offset=".45" stop-color="#0a1024" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#0a1024" stop-opacity=".46"/></radialGradient>')
    o.append('<pattern id="seigaiha" width="80" height="40" patternUnits="userSpaceOnUse">'
             '<g fill="none" stroke="#ffffff" stroke-width="2.2">'
             '<circle cx="40" cy="40" r="36"/><circle cx="40" cy="40" r="26"/><circle cx="40" cy="40" r="16"/>'
             '<circle cx="0" cy="40" r="36"/><circle cx="0" cy="40" r="26"/><circle cx="0" cy="40" r="16"/>'
             '<circle cx="80" cy="40" r="36"/><circle cx="80" cy="40" r="26"/><circle cx="80" cy="40" r="16"/>'
             '<circle cx="20" cy="20" r="36"/><circle cx="60" cy="20" r="36"/>'
             '</g></pattern>')
    o.append('</defs>')

    o.append(bg())

    # --- 後列（3人）
    o.append(person(318, 730, .86, 0, "bun",      2, 3, 1, 600, raise_side= 1, eyes="smile", tilt=-4, low_arm=False))
    o.append(person(600, 714, .88, 1, "short",    5, 1, 0, 590, raise_side=-1, eyes="open",  tilt= 3, low_arm=False))
    o.append(person(886, 734, .86, 2, "ponytail", 3, 0, 2, 600, raise_side=-1, eyes="smile", tilt= 4, low_arm=False))
    o.append(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')

    # --- 前列（4人）
    o.append(person(192,  884, 1.04, 3, "bob",   0, 2, 0, 340, raise_side= 1, eyes="smile", tilt=-5))
    o.append(person(466,  900, 1.04, 4, "quiff", 1, 1, 4, 325, raise_side=-1, eyes="open",  tilt= 4))
    o.append(person(740,  888, 1.04, 5, "long",  4, 3, 1, 335, raise_side= 1, eyes="smile", tilt=-3,
                    hold="bottle"))
    o.append(person(1010, 904, 1.04, 6, "short", 2, 0, 3, 325, raise_side=-1, eyes="smile", tilt= 5))

    # --- テーブル
    o.append(table())
    o.append(bottle(118, 1238, 1.0, body="#22412f", label="純米", tall=True))
    o.append(tokkuri(292, 1240, 1.05))
    o.append(ochoko(392, 1234, 1.25))
    o.append(edamame(560, 1222, 1.05))
    o.append(ochoko(700, 1236, 1.2))
    o.append(masu(812, 1244, 1.15))
    o.append(bottle(980, 1240, 0.95, body="#6a4124", label="純米"))
    o.append(ochoko(1102, 1232, 1.25))

    # --- テーブル下のタグ帯
    tags = ["持ち寄り歓迎", "飲みくらべ", "はじめまして歓迎"]
    xs = [286, 600, 914]
    for tx, tg in zip(xs, tags):
        o.append(f'<text x="{tx}" y="1424" text-anchor="middle" font-family="Noto Sans JP" '
                 f'font-weight="700" font-size="30" letter-spacing="2" fill="{C["cream"]}" '
                 f'opacity=".92">{esc(tg)}</text>')
    for dx in (443, 757):
        o.append(f'<circle cx="{dx}" cy="1415" r="5" fill="{C["amber"]}" opacity=".8"/>')

    # --- 文字まわり
    o.append(f'<rect x="0" y="0" width="{W}" height="620" fill="url(#fade)" '
             f'transform="translate(0,620) scale(1,-1)"/>')
    o.append(f'<g font-family="Noto Sans JP" font-weight="700" fill="{C["amber"]}">'
             f'<text x="600" y="158" text-anchor="middle" font-size="27" letter-spacing="9">SAKE POTLUCK NIGHT</text></g>')
    o.append(f'<path d="M 440,186 L 760,186" stroke="{C["amber"]}" stroke-width="2" opacity=".55"/>')
    o.append(f'<text x="600" y="330" text-anchor="middle" font-family="Noto Serif JP" font-weight="900" '
             f'font-size="126" letter-spacing="2" fill="{C["cream"]}">日本酒持ち寄り会</text>')
    o.append(f'<g opacity=".9"><path d="M 372,392 L 828,392" stroke="{C["amber_deep"]}" stroke-width="3"/>'
             f'<circle cx="600" cy="392" r="9" fill="{C["amber"]}"/></g>')
    o.append(f'<text x="600" y="462" text-anchor="middle" font-family="Noto Sans JP" font-weight="400" '
             f'font-size="39" letter-spacing="2" fill="{C["cream"]}" opacity=".93">'
             f'好きな一本を持ち寄って、ゆるく乾杯</text>')

    # --- フッター
    o.append(f'<rect x="0" y="1470" width="{W}" height="130" fill="{C["cream"]}"/>')
    o.append(f'<rect x="0" y="1470" width="{W}" height="6" fill="{C["amber_deep"]}"/>')
    o.append(f'<text x="600" y="1528" text-anchor="middle" font-family="Noto Sans JP" font-weight="700" '
             f'font-size="34" fill="{C["ink"]}">ひとりでの参加も大丈夫です</text>')
    o.append(f'<text x="600" y="1574" text-anchor="middle" font-family="Noto Sans JP" font-weight="400" '
             f'font-size="27" fill="#5a6280">20歳以上／飲酒の強要はしません</text>')

    o.append('</svg>')
    return "\n".join(o)

fonts = json.load(open("fonts.json"))
svg = build(fonts)
open("cover.svg", "w").write(svg)
open("cover.html", "w").write(
    "<style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}"
    "svg{display:block;position:absolute;top:0;left:0}</style>" + svg)
print("svg bytes:", len(svg))
