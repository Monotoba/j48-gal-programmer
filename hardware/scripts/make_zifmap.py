"""J48 ZIF-28 socket pin map (Rev H): one socket drawing per device group with the chip overlaid,
plus a table of every ZIF pin's role per device and its Rev H connection."""
import sys
OUT = sys.argv[1]
FONT = 'font-family="DejaVu Sans Mono, Consolas, monospace"'
o = []
def esc(t): return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def text(x, y, t, size=11, anchor="start", bold=False, fill="#000", rot=None):
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    o.append(f'<text x="{x}" y="{y}" {FONT} font-size="{size}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}" fill="{fill}"{tr}>{esc(t)}</text>')
def rect(x, y, w, h, fill="none", stroke="#000", sw=1.4, dash=None, rx=0, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    fo = f' fill-opacity="{op}"' if op is not None else ""
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{fo} stroke="{stroke}" stroke-width="{sw}"{d}/>')
def line(x1, y1, x2, y2, c="#000", w=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>')
def circ(x, y, r, fill="#fff", stroke="#000", sw=1.2):
    o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

# ---------------- data (ZIF pin 1..24), from the Afterburner "ZIF SOCKET PIN MAP" ----------------
E = None   # no chip pin in this socket position (20-pin parts)
GROUPS = [
 dict(key="22V10", title="22V10 / 20XV10 / ATF750C", sub="24-pin", pins=24, roles=
   ['-','EDIT','PV','RA0','RA1','RA2','RA3','RA4','RA5','SCLK','DIN','GND','STR','DOUT','-','-','-','-','-','-','-','-','-','VCC']),
 dict(key="20V8", title="20V8", sub="24-pin", pins=24, roles=
   ['-','EDIT','RA1','RA2','RA3','-','-','RA4','RA5','SCLK','DIN','GND','STR','-','DOUT','-','-','-','-','-','RA0','PV','-','VCC']),
 dict(key="16V8", title="16V8 (incl. ATF16V8B)", sub="20-pin, top-justified", pins=20, roles=
   ['-','EDIT','RA1','RA2','RA3','RA4','RA5','SCLK','DIN','GND',E,E,E,E,'STR','DOUT','-','-','-','-','-','RA0','PV','VCC']),
 dict(key="18V10", title="18V10", sub="20-pin, top-justified", pins=20, roles=
   ['-','EDIT','RA3','RA4','RA5','SCLK','DIN','STR','DOUT','GND',E,E,E,E,'-','-','-','-','-','RA2','RA1','RA0','PV','VCC']),
 dict(key="6001", title="6001 / 6002", sub="24-pin", pins=24, roles=
   ['-','EDIT','-','RA0','RA1','RA2','RA3','RA4','RA5','SCLK','DIN','GND','STR','DOUT','-','-','-','-','-','-','-','-','PV','VCC']),
 dict(key="JTAG", title="JTAG: ATF150x", sub="via 24-pin adapter", pins=24, roles=
   ['-','EDIT','TDI','-','-','-','-','-','-','-','-','GND','TMS','-','-','-','-','-','-','-','-','TDO','TCK','VCC']),
]
def to28(r24):
    """ZIF-24 position list -> ZIF-28: left side unchanged, right side moves up by 4, ZIF 13-16 empty."""
    return r24[0:12] + [None] * 4 + r24[12:24]
for g in GROUPS:
    g["roles"] = to28(g["roles"])
R26 = {2:'EDIT',3:'PV',4:'RA0',5:'RA1',6:'RA2',7:'VCC',9:'RA3',10:'RA4',11:'RA5',12:'SCLK',13:'DIN',14:'STR',15:'DOUT',21:'GND'}
GROUPS.append(dict(key="26CV12", title="26CV12 / 26V12", sub="28-pin", pins=28, roles=[R26.get(z, '-') for z in range(1, 29)]))
# Rev G net / driver for each ZIF pin (replaced below by Rev H)
NET = {1: ("pull-down", "R20 10k"), 2: ("VPP", "VPP gen."), 3: ("U1 PD0", "MCU"), 4: ("U2 Q0", "595"), 5: ("U2 Q3", "595"),
       6: ("U2 Q2", "595"), 7: ("U2 Q1 + Q7", "595 / VCC sw"), 8: ("U1 PD2", "MCU"), 9: ("U1 PD3", "MCU"), 10: ("U1 PD4 + Q1", "MCU / GND sw"),
       11: ("U1 PD5", "MCU"), 12: ("U9 Q0 + Q4", "595 / GND sw"), 13: ("U9 Q1", "595"), 14: ("U9 Q2", "595"), 15: ("U1 PA3", "MCU"),
       16: ("pull-down", "R46 10k"), 17: ("U1 PD6", "MCU"), 18: ("U1 PD7", "MCU"), 19: ("U1 PC3", "MCU"), 20: ("U1 PF0", "MCU"),
       21: ("pull-down + Q5", "R21 / GND sw"), 22: ("pull-down", "R22 10k"), 23: ("pull-down", "R23 10k"),
       24: ("U2 Q5", "595"), 25: ("U2 Q4", "595"), 26: ("U1 PF1", "MCU"), 27: ("U2 Q7", "595"), 28: ("VCC_SKT via Q6", "VCC sw + R47")}

def role_color(r):
    if r in ("EDIT", "VCC"): return "#b3261e"
    if r == "GND": return "#444"
    if r and r.startswith("RA"): return "#1a4fa0"
    if r in ("SCLK", "DIN", "STR", "DOUT"): return "#1a7f37"
    if r == "PV": return "#7b2fa8"
    if r in ("TDI", "TDO", "TMS", "TCK"): return "#b35c00"
    return "#999"

def chip_pin(zif, n):
    """chip pin number at a ZIF position for an n-pin part, top-justified (pin 1 at ZIF 1)."""
    half = n // 2
    if zif <= 14:
        return zif if zif <= half else None
    k = 29 - zif            # rows from top on the right side: ZIF 28 -> 1
    return (n + 1 - k) if k <= half else None

# ---------------- sheet ----------------
W = 2160
PANEL_W, PANEL_H = 296, 540
TOP = 92
TAB_Y = TOP + PANEL_H + 30
ROWH = 22
TAB_H = 70 + 28 * ROWH + 170
H = TAB_Y + TAB_H + 20

rect(0, 0, W, H, fill="#ffffff", stroke="none", sw=0)
rect(8, 8, W - 16, H - 16, stroke="#000", sw=2)
text(30, 44, "J48 ZIF-28 socket pin map — every device is head-aligned (chip pin 1 at ZIF pin 1)", 22, bold=True)
text(30, 66, "20-pin parts use ZIF 1–10 and 19–28; 24-pin parts use ZIF 1–12 and 17–28; 28-pin parts fill the socket. GND and VCC are switched per size (Rev H).", 12, fill="#666")

pitch = 28
for gi, g in enumerate(GROUPS):
    px = 24 + gi * (PANEL_W + 6)
    rect(px, TOP - 10, PANEL_W, PANEL_H, stroke="#8a8a8a", sw=1.2, dash="7 5", rx=6)
    text(px + PANEL_W / 2, TOP + 10, g["title"], 13, "middle", True)
    text(px + PANEL_W / 2, TOP + 26, g["sub"], 10, "middle", fill="#666")
    # socket body
    cx = px + PANEL_W / 2
    sx0, sx1 = cx - 52, cx + 52            # pin columns (0.6" rows, drawn schematic-scale)
    y0 = TOP + 78                           # row 1 y
    body_top, body_bot = y0 - 30, y0 + 13 * pitch + 22
    rect(sx0 - 22, body_top, (sx1 - sx0) + 44, body_bot - body_top, fill="#f1f1f1", stroke="#000", sw=1.6, rx=4)
    # lever at the pin-1 end
    rect(sx0 - 22, body_top - 14, 64, 10, fill="#d9d9d9", stroke="#000", sw=1.2, rx=3)
    text(sx0 + 48, body_top - 5, "lever", 9, fill="#666")
    # chip overlay
    n = g["pins"]
    rows = n // 2
    ctop, cbot = y0 - 15, y0 + (rows - 1) * pitch + 15
    rect(sx0 - 12, ctop, (sx1 - sx0) + 24, cbot - ctop, fill="#fff3c4", stroke="#000", sw=1.8, op=0.95)
    o.append(f'<path d="M {cx-9} {ctop} A 9 9 0 0 0 {cx+9} {ctop}" fill="none" stroke="#000" stroke-width="1.6"/>')
    o.append(f'<circle cx="{sx0+8}" cy="{ctop+9}" r="2.6" fill="#000"/>')
    label = "ATF150x adapter" if g["key"] == "JTAG" else "GAL" + g["key"]
    text(cx, (ctop + cbot) / 2, label, 12, "middle", True, "#555", rot=-90)
    if rows < 14:
        # empty rows below a 20-pin part
        ey = cbot + 6
        rect(sx0 - 12, ey, (sx1 - sx0) + 24, body_bot - 8 - ey, stroke="#999", sw=1, dash="3 3")
        text(cx, (ey + body_bot - 8) / 2 + 4, "empty", 10, "middle", fill="#999")
    for z in range(1, 29):
        left = z <= 14
        r = (z - 1) if left else (28 - z)
        y = y0 + r * pitch
        x = sx0 if left else sx1
        role = g["roles"][z - 1]
        cp = chip_pin(z, n)
        filled = cp is not None
        circ(x, y, 5, fill="#000" if filled else "#fff", stroke="#000")
        # ZIF number outside the socket body
        zx = sx0 - 30 if left else sx1 + 30
        text(zx, y + 4, z, 10, "end" if left else "start", fill="#444")
        # chip pin number inside the chip outline
        if filled:
            text(x + (10 if left else -10), y + 4, cp, 9, "start" if left else "end", fill="#8a6d00")
        # role
        rx_ = sx0 - 56 if left else sx1 + 56
        if role is None:
            continue
        rtxt = role
        if role in ("GND", "VCC"):
            rtxt = role + "*"
        text(rx_, y + 4, rtxt, 11, "end" if left else "start", role not in ("-",), role_color(role))
    sw = {20: ("GND: ZIF 10 via Q1 (U2 Q6)", "VCC: ZIF 28 via Q6 (U9 Q6)"),
          24: ("GND: ZIF 12 via Q4 (U9 Q4)", "VCC: ZIF 28 via Q6 (U9 Q6)"),
          28: ("GND: ZIF 21 via Q5 (U9 Q5)", "VCC: ZIF 7 via Q7 (U9 Q7)")}[n]
    text(px + 12, TOP + PANEL_H - 34, "* " + sw[0], 9, fill="#444")
    text(px + 12, TOP + PANEL_H - 21, "* " + sw[1], 9, fill="#444")

# legend under the panels row
ly = TOP + PANEL_H + 10
items = [("EDIT", "VPP / edit-mode supply (ZIF 2)"), ("RA0", "row address"), ("SCLK", "serial clock, DIN/DOUT data, STR strobe"),
         ("PV", "program / verify"), ("TDI", "JTAG"), ("VCC", "switched VCC_SKT (* = switch, see panel notes)")]
lx = 30
for r, d in items:
    text(lx, ly + 8, r, 11, bold=True, fill=role_color(r)); text(lx + 44, ly + 8, d, 10, fill="#444")
    lx += 44 + len(d) * 6.2 + 26
text(W - 30, ly + 8, "●  chip pin present   ○  socket contact unused", 10, "end", fill="#444")

# ---------------- table ----------------
TX = 24
rect(TX, TAB_Y, W - 48, TAB_H, stroke="#8a8a8a", sw=1.2, dash="7 5", rx=6)
text(TX + 10, TAB_Y + 20, "ZIF-28 pin map: each device's role at every ZIF pin, and the Rev H connection", 13, bold=True, fill="#444")
cols = [("ZIF", 50), ("Rev G net", 150), ("driver", 120)] + [(g["title"], 0) for g in GROUPS]
xs = [TX + 20, TX + 70, TX + 220]
gx0, gw = TX + 360, (W - 48 - 360 - 20) / len(GROUPS)
xs += [gx0 + i * gw for i in range(len(GROUPS))]
hy = TAB_Y + 52
text(xs[0], hy, "ZIF", 12, bold=True); text(xs[1], hy, "Rev H net", 12, bold=True); text(xs[2], hy, "driven by", 12, bold=True)
for i, g in enumerate(GROUPS):
    text(xs[3 + i], hy - 15, g["title"], 12, bold=True)
    text(xs[3 + i], hy, g["sub"] + ("   (role · chip pin)" if g["pins"] < 28 else ""), 9, fill="#666")
line(TX + 14, hy + 8, W - 38, hy + 8, "#000", 1.2)
for z in range(1, 29):
    y = hy + 8 + z * ROWH - 6
    if z % 2 == 0:
        rect(TX + 14, y - 15, W - 52 - 14, ROWH, fill="#f6f6f6", stroke="none", sw=0)
    if z == 15:
        line(TX + 14, y - 15, W - 38, y - 15, "#000", 1.0)
    text(xs[0], y, z, 11, bold=True)
    net, drv = NET[z]
    text(xs[1], y, net, 11, fill="#b3261e" if net.startswith(("VPP", "VCC")) else "#1a4fa0" if net.startswith("U") else "#444")
    text(xs[2], y, drv, 10, fill="#666")
    for i, g in enumerate(GROUPS):
        role = g["roles"][z - 1]
        x = xs[3 + i]
        if role is None:
            text(x, y, "(no chip pin)", 10, fill="#bbb"); continue
        t = role if role != "-" else "–"
        if g["pins"] < 28:
            t = f"{t} · {chip_pin(z, g['pins'])}"
        if role in ("GND", "VCC"):
            t += {10: " (Q1)", 12: " (Q4)", 21: " (Q5)", 28: " (Q6)", 7: " (Q7)"}.get(z, "")
        text(x, y, t, 11, role != "-", role_color(role))
ny = hy + 8 + 28 * ROWH + 24
notes = [
 "Role names: EDIT = VPP pin in edit mode, PV = program/verify, STR = strobe, DIN/DOUT = serial data in/out, RA0–RA5 = row address. '–' = held low or undriven.",
 "Signals the MCU reads (DOUT, TDO) land on MCU pins: ZIF 9, 15, 18, 19, 20 and 26. ZIF 6 (18V10 SCLK), 12–14 (26CV12 SCLK, DIN, STR) and 27 (PV, JTAG TCK) go through a 74HC595 and change only on a latch pulse.",
 "GND and VCC are switched per chip size and all switches are off at reset: one GND switch (Q1, Q4 or Q5) and one VCC switch (Q6 or Q7) at a time. Never Q6 with Q7; never Q4 with a 28-pin part.",
 "ZIF 1, 16, 22, 23 and (when Q6 is off) 28 have pull-downs; ZIF 21's pull-down is shared with the Q5 ground switch.",
 "Chip pin for 24-pin parts: ZIF 1–12 = pins 1–12, ZIF 17–28 = pins 13–24. For 20-pin parts: ZIF 1–10 = pins 1–10, ZIF 19–28 = pins 11–20.",
]
for i, t in enumerate(notes):
    text(TX + 20, ny + i * 18, f"{i+1}. {t}", 10.5)

# title block
rect(W - 380, H - 92, 356, 62, fill="#f4f4f4", stroke="#000", sw=1.4)
text(W - 368, H - 72, "J48 GAL / PAL Programmer — AVR16DU28", 12, bold=True)
text(W - 368, H - 55, "Rev H  ·  ZIF-28 pin map  ·  2026-10-17", 10)
text(W - 368, H - 40, "Pin roles: published device pinouts", 10, fill="#666")

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{int(H)}" viewBox="0 0 {W} {int(H)}">\n' + "\n".join(o) + "\n</svg>\n"
open(OUT, "w", encoding="utf-8").write(svg)
print("size", W, H)
