"""Rev H drawing from the Rev G SVG: ZIF-28 socket, renumbered ZIF labels, U9 + VCC/GND switching section."""
import re, sys
SRC, DST = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
CHG = "#7b2fa8"
FONT = 'font-family="DejaVu Sans Mono, Consolas, monospace"'

# Rev G's change colour goes back to black; purple now marks Rev H changes
s = s.replace('fill="#7b2fa8"', 'fill="#000"').replace('stroke="#7b2fa8"', 'stroke="#000"')

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def edit_text(x, y, old, new, color=CHG):
    global s
    pat = re.compile(r'(<text x="%s" y="%s"[^>]*?fill=")([^"]*)("[^>]*>)%s(</text>)' % (re.escape(str(x)), re.escape(str(y)), re.escape(esc(old))))
    m = pat.search(s)
    if not m: raise SystemExit(f"text not found {x},{y} {old!r}")
    s = s[:m.start()] + m.group(1) + (color or m.group(2)) + m.group(3) + esc(new) + m.group(4) + s[m.end():]

def relabel(x, y, old, new):
    """rename a net label (text + its polygon, resized)"""
    global s
    m = re.search(r'<text x="%s" y="%s"[^>]*>%s</text>' % (re.escape(str(x)), re.escape(str(y)), re.escape(old)), s)
    if not m: raise SystemExit(f"label not found {x},{y} {old}")
    ps = s.rfind("<polygon", 0, m.start()); pe = s.find("/>", ps) + 2
    poly = s[ps:pe]
    pts = [tuple(map(float, p.split(","))) for p in re.search(r'points="([^"]+)"', poly).group(1).split()]
    tip = pts[0]
    w = len(new) * 6.6 + 11
    if 'text-anchor="end"' in m.group(0):
        npts = [tip, (tip[0]-7, tip[1]-8), (tip[0]-7-w, tip[1]-8), (tip[0]-7-w, tip[1]+8), (tip[0]-7, tip[1]+8)]
    else:
        npts = [tip, (tip[0]+7, tip[1]-8), (tip[0]+7+w, tip[1]-8), (tip[0]+7+w, tip[1]+8), (tip[0]+7, tip[1]+8)]
    newpoly = re.sub(r'points="[^"]+"', 'points="' + " ".join(f"{a:g},{b:g}" for a, b in npts) + '"', poly)
    newpoly = newpoly.replace('stroke="#1a4fa0"', f'stroke="{CHG}"')
    newtext = m.group(0).replace(f">{old}<", f">{new}<").replace('fill="#1a4fa0"', f'fill="{CHG}"')
    s = s[:ps] + newpoly + s[pe:m.start()] + newtext + s[m.end():]

# ---------------- titles ----------------
edit_text(30, 44, "AVR16DU28 GAL / PLD Programmer — Schematic (Rev G: 5 V / 3.3 V logic supply, J4)",
          "J48 GAL / PAL Programmer — Schematic (Rev H: ZIF-28, GAL26CV12/26V12 head-aligned)", color=None)
edit_text(1572, 1480, "GAL / PLD Programmer — AVR16DU28", "J48 GAL / PAL Programmer — AVR16DU28", color=None)
edit_text(30, 66, "Native USB · one SPI bus: 74HC595, MCP4821 DAC, 23LC1024 SRAM · VSYS = 5 V or 3.3 V (J4) · purple = changed in Rev G. Labels with the same name are joined.",
          "Native USB · SPI: 2× 74HC595, MCP4821 DAC, 23LC1024 SRAM · VSYS = 5 V / 3.3 V (J4) · ZIF-28 · purple = changed in Rev H. Same-name labels are joined.", color=None)
edit_text(1572, 1497, "Rev G  ·  Sheet 1/1  ·  2026-10-17", "Rev H  ·  Sheet 1/1  ·  2026-10-17", color=None)

# ---------------- MCU and 595 labels: ZIF-24 right side moves up by 4 ----------------
MCU = {(530, 324): ("ZIF15", "ZIF19"), (530, 464): ("ZIF13", "ZIF17"), (530, 484): ("ZIF14", "ZIF18"),
       (530, 504): ("ZIF16", "ZIF20"), (530, 524): ("ZIF22", "ZIF26")}
for (x, y), (o, n) in MCU.items():
    relabel(x, y, o, n)
relabel(480, 224, "BOOST_EN", "MCU_PA3")
SR = {(970, 174): ("ZIF7", "U2_Q1"), (970, 234): ("ZIF21", "ZIF25"), (970, 254): ("ZIF20", "ZIF24"), (970, 294): ("ZIF23", "ZIF27")}
for (x, y), (o, n) in SR.items():
    relabel(x, y, o, n)
# U2 Q7' : replace the no-connect X with a SR_CHAIN label
x1 = '<line x1="935" y1="305" x2="945" y2="315" stroke="#b3261e" stroke-width="1.6"/>\n<line x1="935" y1="315" x2="945" y2="305" stroke="#b3261e" stroke-width="1.6"/>'
assert x1 in s
s = s.replace(x1, '<line x1="940" y1="310" x2="960" y2="310" stroke="#000" stroke-width="1.6"/>\n'
              f'<polygon points="960,310 967,302 1034.6,302 1034.6,318 967,318" fill="#eef3fb" stroke="{CHG}" stroke-width="1.2"/>\n'
              f'<text x="970" y="314" {FONT} font-size="11" text-anchor="start" font-weight="bold" fill="{CHG}">SR_CHAIN</text>')
# pull-down block
relabel(1708, 724, "ZIF17", "ZIF21"); relabel(1776, 724, "ZIF18", "ZIF22"); relabel(1844, 724, "ZIF19", "ZIF23")
edit_text(1612, 674, "Pull-downs (ZIF 1, 17–19)", "Pull-downs (ZIF 1, 21–23)")

# ---------------- text edits ----------------
edit_text(40, 912, "SW1: VSYS → VCC_SKT. OFF to insert/remove. C2/C3 at pin 24.", "SW1: VSYS → VCC_SKT. OFF to insert/remove. C2/C3 by Q6/Q7.")
edit_text(40, 1286, "U2 74HC595", "U2+U9 74HC595")
edit_text(470, 1286, "outputs change only on latch rise", "16-bit chain, U9 byte first")
edit_text(40, 1380, "The 595 sees every SPI byte in its shift register, but its outputs move only when",
          "The 595 chain sees every SPI byte, but its outputs move only when PA7 is")
edit_text(40, 1396, "PA7 is pulsed, so firmware sends a full 595 byte right before each latch.",
          "pulsed, so firmware sends both 595 bytes (U9 first) right before each latch.")
edit_text(776, 1432, "10. BOOST_EN (PA3) low or floating (R36) = boost off: VBOOST ≈ VCC_SKT − 0.4 V, so VPP stays ≤ ~3 V.",
          "10. BOOST_EN (U9 Q3) low or Hi-Z (R36) = boost off: VBOOST ≈ VCC_SKT − 0.4 V, so VPP stays ≤ ~3 V.")
edit_text(776, 1452, "11. U7 holds the fuse map (lifts the 2 KB limit). ZIF23 stays on 595 Q7; all 19 MCU pins are used.",
          "11. U7 holds the fuse map (lifts the 2 KB limit). All 19 MCU pins are used; PA3 now reads SDOUT (ZIF15).")
edit_text(760, 1664, "and SW1 → VCC_SKT (ZIF pin 24 and the U4 boost input). +5V (VBUS after F1) now feeds only J4 and U8.",
          "and SW1 → VCC_SKT (ZIF 28 / ZIF 7 via Q6 / Q7, and the U4 boost input). +5V (VBUS after F1) feeds only J4 and U8.")

# ---------------- replace the socket block ----------------
a = s.index('<rect x="1136" y="82" width="760" height="560"')
b = s.index('<rect x="24" y="656"')
s = s[:a] + "@@SOCKET@@\n" + s[b:]

o = []
def text(x, y, t, size=11, anchor="start", bold=False, fill="#000", italic=False):
    it = ' font-style="italic"' if italic else ""
    o.append(f'<text x="{x}" y="{y}" {FONT} font-size="{size}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}" fill="{fill}"{it}>{esc(str(t))}</text>')
def line(x1, y1, x2, y2, w=1.6, c="#000"):
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>')
def rect(x, y, w, h, fill="none", stroke="#000", sw=1.4, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def dot(x, y): o.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#000"/>')
def gnd(x, y):
    line(x, y, x, y + 10); line(x - 10, y + 10, x + 10, y + 10, 2); line(x - 6, y + 14, x + 6, y + 14, 2); line(x - 2, y + 18, x + 2, y + 18, 2)
def lab_l(tip, y, name, power=False, col=None):
    w = len(name) * 6.6 + 11; c = col or ("#b3261e" if power else "#1a4fa0")
    o.append(f'<polygon points="{tip},{y} {tip-7},{y-8} {tip-7-w:g},{y-8} {tip-7-w:g},{y+8} {tip-7},{y+8}" fill="#eef3fb" stroke="{c}" stroke-width="1.2"/>')
    text(tip - 10, y + 4, name, 11, "end", True, c)
def lab_r(tail, y, name, power=False, col=None):
    w = len(name) * 6.6 + 11; c = col or ("#b3261e" if power else "#1a4fa0")
    o.append(f'<polygon points="{tail},{y} {tail+7},{y-8} {tail+7+w:g},{y-8} {tail+7+w:g},{y+8} {tail+7},{y+8}" fill="#eef3fb" stroke="{c}" stroke-width="1.2"/>')
    text(tail + 10, y + 4, name, 11, "start", True, c)
def flag(x, y, name):
    line(x - 9, y, x + 9, y, 2.2, "#b3261e"); text(x, y - 5, name, 11, "middle", True, "#b3261e")
def res_v(x, y1, y2, ref, val, col="#000"):
    m = (y1 + y2) / 2
    line(x, y1, x, m - 22); line(x, m + 22, x, y2)
    rect(x - 7, m - 22, 14, 44, fill="#fff"); text(x + 12, m - 2, ref, 10, bold=True, fill=col); text(x + 12, m + 11, val, 10, fill=col)
def res_h(x1, x2, y, label, col="#000"):
    m = (x1 + x2) / 2
    line(x1, y, m - 30, y); line(m + 30, y, x2, y)
    rect(m - 30, y - 7, 60, 14, fill="#fff"); text(m, y + 4, label, 9, "middle", fill=col)

# --- ZIF-28 block ---
rect(1136, 82, 760, 560, stroke="#8a8a8a", sw=1.2, dash="7 5", rx=6)
text(1146, 100, 'ZIF-28 socket (0.3"/0.6"), every chip head-aligned: pin 1 at ZIF 1', 13, bold=True, fill="#444")
rect(1440, 122, 160, 456, fill="#fffbe6", sw=1.8)
o.append('<path d="M 1508 122 A 12 12 0 0 0 1532 122" fill="none" stroke="#000" stroke-width="1.6"/>')
text(1440, 116, "J1", 13, bold=True, fill=CHG); text(1600, 116, "ZIF-28", 12, "end", True, CHG)
# roles per ZIF-28 position
R22 = ['-','EDIT','PV','RA0','RA1','RA2','RA3','RA4','RA5','SCLK','DIN','GND','STR','DOUT','-','-','-','-','-','-','-','-','-','VCC']
R20 = ['-','EDIT','RA1','RA2','RA3','-','-','RA4','RA5','SCLK','DIN','GND','STR','-','DOUT','-','-','-','-','-','RA0','PV','-','VCC']
R16 = ['-','EDIT','RA1','RA2','RA3','RA4','RA5','SCLK','DIN','GND',None,None,None,None,'STR','DOUT','-','-','-','-','-','RA0','PV','VCC']
R18 = ['-','EDIT','RA3','RA4','RA5','SCLK','DIN','STR','DOUT','GND',None,None,None,None,'-','-','-','-','-','RA2','RA1','RA0','PV','VCC']
R60 = ['-','EDIT','-','RA0','RA1','RA2','RA3','RA4','RA5','SCLK','DIN','GND','STR','DOUT','-','-','-','-','-','-','-','-','PV','VCC']
RJT = ['-','EDIT','TDI','-','-','-','-','-','-','-','-','GND','TMS','-','-','-','-','-','-','-','-','TDO','TCK','VCC']
R26 = {2:'EDIT',3:'PV',4:'RA0',5:'RA1',6:'RA2',7:'VCC',9:'RA3',10:'RA4',11:'RA5',12:'SCLK',13:'SDIN',14:'STB',15:'SDOUT',21:'GND'}
def roles(z):
    old = z if z <= 12 else (z - 4 if z >= 17 else None)
    out = []
    if old:
        for lst, tag in ((R22, ""), (R20, ""), (R16, "20"), (R18, "20"), (R60, ""), (RJT, "")):
            r = lst[old - 1]
            if r in (None, "-"): continue
            if r in ("GND", "VCC"):
                r = f"{r}({'20' if old == 10 else '24' if old == 12 else '20/24'})"
            if r not in out: out.append(r)
    r = R26.get(z)
    if r:
        r28 = f"{r}(28)"
        if r in ("VCC", "GND") or r not in [x.split("(")[0] for x in out]:
            out.append(r28)
    return " / ".join(out) if out else "L / undriven (all)"
ZNET = {2: ("VPP", True)}
y0, pitch = 146, 32
for z in range(1, 29):
    left = z <= 14
    row = (z - 1) if left else (28 - z)
    y = y0 + row * pitch
    name, power = ZNET.get(z, (f"ZIF{z}", False))
    new = z in (7, 12, 13, 14, 15, 16, 21, 28)
    col = CHG if (new and not power) else None
    if left:
        line(1400, y, 1440, y); lab_l(1400, y, name, power, col)
        text(1436, y - 5, z, 9, "end", fill="#666"); text(1446, y + 4, z, 11)
        text(1330, y + 4, roles(z), 9, "end", fill="#666", italic=True)
    else:
        line(1600, y, 1640, y); lab_r(1640, y, name, power, col)
        text(1604, y - 5, z, 9, fill="#666"); text(1594, y + 4, z, 11, "end")
        text(1706, y + 4, roles(z), 9, fill="#666", italic=True)
text(1516, 600, "grey text = programming role(s); (20)/(24)/(28) = only that chip size", 10, "middle", fill="#666", italic=True)
text(1516, 616, "20-pin: ZIF 1–10, 19–28 · 24-pin: ZIF 1–12, 17–28 · 28-pin: ZIF 1–28", 10, "middle", fill=CHG)
text(1516, 632, "GND/VCC are switched per size (see ZIF-28 switching, bottom)", 10, "middle", fill=CHG)
s = s.replace("@@SOCKET@@", "\n".join(o))

# ---------------- new bottom section ----------------
o = []
EX = 362
H0 = 1884
NH = H0 + EX
s = s.replace(f'width="1920" height="{H0}" viewBox="0 0 1920 {H0}"', f'width="1920" height="{NH}" viewBox="0 0 1920 {NH}"')
s = s.replace(f'<rect x="0" y="0" width="1920" height="{H0}" fill="#ffffff"/>', f'<rect x="0" y="0" width="1920" height="{NH}" fill="#ffffff"/>')
s = s.replace(f'<rect x="8" y="8" width="1904" height="{H0-16}" rx="0"', f'<rect x="8" y="8" width="1904" height="{NH-16}" rx="0"')
Y = H0 - 6
rect(24, Y, 1872, EX - 12, stroke="#8a8a8a", sw=1.2, dash="7 5", rx=6)
text(34, Y + 18, "ZIF-28 switching (new in Rev H): U9 second 595, GND and VCC switches, series resistors", 13, bold=True, fill="#444")

# U9
bx, by = 150, Y + 50
rect(bx, by, 150, 200, fill="#fffbe6", sw=1.8)
text(bx, by - 8, "U9", 13, bold=True, fill=CHG); text(bx + 150, by - 8, "74HC595", 13, "end", True, CHG)
lpins = [("SER", 14, "SR_CHAIN"), ("SRCLK", 11, "SPI_SCK"), ("RCLK", 12, "SR_RCLK"), ("/OE", 13, "SR_OE"), ("/MR", 10, "VSYS"), ("VCC", 16, "VSYS"), ("GND", 8, None)]
for i, (pn, num, net) in enumerate(lpins):
    y = by + 24 + i * 20
    text(bx + 6, y + 4, pn, 11); text(bx - 4, y - 3, num, 9, "end", fill="#666"); line(bx - 30, y, bx, y)
    if net: lab_l(bx - 30, y, net, power=(net == "VSYS"))
    else: line(bx - 30, y, bx - 30, y + 6); gnd(bx - 30, y + 6)
rpins = [("Q0", 15, "U9_Q0"), ("Q1", 1, "ZIF13"), ("Q2", 2, "ZIF14"), ("Q3", 3, "BOOST_EN"), ("Q4", 4, "GND12_EN"), ("Q5", 5, "GND21_EN"),
         ("Q6", 6, "VCC28_EN"), ("Q7", 7, "VCC7_EN"), ("Q7'", 9, None)]
for i, (pn, num, net) in enumerate(rpins):
    y = by + 24 + i * 20
    text(bx + 144, y + 4, pn, 11, "end"); text(bx + 154, y - 3, num, 9, fill="#666"); line(bx + 150, y, bx + 180, y)
    if net: lab_r(bx + 180, y, net, col=CHG)
    else:
        line(bx + 175, y - 5, bx + 185, y + 5, 1.6, "#b3261e"); line(bx + 175, y + 5, bx + 185, y - 5, 1.6, "#b3261e")
# C19
cx = 60; flag(cx, by + 214, "VSYS"); line(cx, by + 214, cx, by + 235)
line(cx - 11, by + 235, cx + 11, by + 235, 2.4); line(cx - 11, by + 243, cx + 11, by + 243, 2.4); line(cx, by + 243, cx, by + 262); gnd(cx, by + 262)
text(cx + 15, by + 238, "C19", 10, bold=True, fill=CHG); text(cx + 15, by + 251, "100n", 10, fill=CHG)
text(bx, by + 222, "SER from U2 Q7' (pin 9).", 10, fill="#444")
text(bx, by + 236, "Shares SCK, RCLK, /OE with U2.", 10, fill="#444")
text(bx, by + 250, "At reset /OE is high: all", 10, fill="#444")
text(bx, by + 264, "switches below are off.", 10, fill="#444")

# series resistors
sx = 470
text(sx, Y + 46, "Series resistors", 12, bold=True)
for i, (a, rlab, b) in enumerate([("U2_Q1", "R43 100Ω", "ZIF7"), ("U9_Q0", "R44 100Ω", "ZIF12"), ("MCU_PA3", "R45 100Ω", "ZIF15")]):
    y = Y + 76 + i * 34
    lab_l(sx + 70, y, a, col=CHG); res_h(sx + 70, sx + 200, y, rlab, CHG); lab_r(sx + 200, y, b, col=CHG)
text(sx, Y + 186, "R43: U2 Q1 still drives ZIF7 (RA3 for 22V10) but can't", 10, fill="#444")
text(sx, Y + 200, "fight Q7 when ZIF7 is the 26CV12's VCC (set Q1 high).", 10, fill="#444")
text(sx, Y + 214, "R44: ZIF12 is SCLK for 28-pin, GND (Q4) for 24-pin.", 10, fill="#444")
text(sx, Y + 228, "R45: PA3 (was BOOST_EN) reads 26CV12 SDOUT.", 10, fill="#444")
# pull-downs R46 R47
px0 = sx
text(px0, Y + 280, "Pull-downs:", 11, bold=True)
for i, (z, r) in enumerate([("ZIF16", "R46"), ("ZIF28", "R47")]):
    x = px0 + 110 + i * 120; y = Y + 276
    o.append(f'<polygon points="{x},{y-14} {x-8},{y-7} {x-8},{y+5} {x+8},{y+5} {x+8},{y-7}" fill="#eef3fb" stroke="{CHG}" stroke-width="1.2"/>')
    text(x, y - 18, z, 11, "middle", True, CHG)
    line(x, y + 5, x, y + 10); rect(x - 7, y + 10, 14, 34, fill="#fff"); line(x, y + 44, x, y + 50); gnd(x, y + 50)
    text(x + 12, y + 26, r, 10, bold=True, fill=CHG); text(x + 12, y + 39, "10k", 10, fill=CHG)

# FET switch drawings
def nfet(x, y, name, drain, gate_net, rg, rpd):
    """N-FET low-side switch; drain label at top, source to ground."""
    text(x + 24, y - 4, name, 11, bold=True, fill=CHG); text(x + 24, y + 9, "AO3400", 10, fill=CHG)
    line(x, y - 22, x, y + 22, 2)                       # channel
    line(x + 0, y - 18, x + 18, y - 18); line(x + 18, y - 18, x + 18, y - 44)   # drain
    line(x + 0, y + 18, x + 18, y + 18); line(x + 18, y + 18, x + 18, y + 50); gnd(x + 18, y + 50)
    line(x - 8, y - 16, x - 8, y + 16, 2)               # gate plate
    line(x - 8, y, x - 40, y)                            # gate lead
    o.append(f'<polygon points="{x+2},{y+18} {x+10},{y+14} {x+10},{y+22}" fill="#000"/>')
    o.append(f'<polygon points="{x+18},{y-44} {x+10},{y-51} {x+10},{y-63} {x+26},{y-63} {x+26},{y-51}" fill="#eef3fb" stroke="{CHG}" stroke-width="1.2"/>')
    text(x + 18, y - 67, drain, 11, "middle", True, CHG)
    dot(x - 40, y); res_h(x - 120, x - 40, y, rg, CHG); lab_l(x - 120, y, gate_net, col=CHG)
    line(x - 40, y, x - 40, y + 10); rect(x - 47, y + 10, 14, 34, fill="#fff"); line(x - 40, y + 44, x - 40, y + 52); gnd(x - 40, y + 52)
    text(x - 54, y + 26, rpd, 10, "end", True, CHG); text(x - 54, y + 39, "100k", 10, "end", fill=CHG)
def pfet(x, y, name, drain, gate_net, rpu):
    """P-FET high-side switch; source to VCC_SKT at top, drain label at bottom."""
    text(x + 26, y - 4, name, 11, bold=True, fill=CHG); text(x + 26, y + 9, "AO3401", 10, fill=CHG)
    line(x, y - 22, x, y + 22, 2)
    line(x, y - 18, x + 18, y - 18); line(x + 18, y - 18, x + 18, y - 52); flag(x + 18, y - 52, "VCC_SKT")
    line(x, y + 18, x + 18, y + 18); line(x + 18, y + 18, x + 18, y + 46)
    line(x - 8, y - 16, x - 8, y + 16, 2)
    o.append(f'<polygon points="{x+10},{y-18} {x+2},{y-22} {x+2},{y-14}" fill="#000"/>')
    o.append(f'<polygon points="{x+18},{y+46} {x+10},{y+53} {x+10},{y+65} {x+26},{y+65} {x+26},{y+53}" fill="#eef3fb" stroke="{CHG}" stroke-width="1.2"/>')
    text(x + 18, y + 79, drain, 11, "middle", True, CHG)
    line(x - 8, y, x - 60, y); dot(x - 40, y); lab_l(x - 60, y, gate_net, col=CHG)
    line(x - 40, y, x - 40, y - 8); rect(x - 47, y - 42, 14, 34, fill="#fff"); line(x - 40, y - 42, x - 40, y - 52)
    line(x - 40, y - 52, x + 18, y - 52)
    text(x - 54, y - 28, rpu, 10, "end", True, CHG); text(x - 54, y - 15, "100k", 10, "end", fill=CHG)

fy = Y + 142
nfet(1000, fy, "Q4", "ZIF12", "GND12_EN", "R37 100Ω", "R39")
nfet(1260, fy, "Q5", "ZIF21", "GND21_EN", "R38 100Ω", "R40")
pfet(1480, fy, "Q6", "ZIF28", "VCC28_EN", "R41")
pfet(1700, fy, "Q7", "ZIF7", "VCC7_EN", "R42")
text(840, Y + 46, "Ground switches (ON = high)", 12, bold=True)
text(1340, Y + 46, "VCC switches (ON = low, P-FET)", 12, bold=True)

# mode table
tx, ty = 840, Y + 250
cols = [0, 210, 330, 450, 570, 690, 810]
hdr = ["Chip size", "Q1 ZIF10", "Q4 ZIF12", "Q5 ZIF21", "Q6 ZIF28", "Q7 ZIF7", "Chip GND / VCC"]
for c, h in zip(cols, hdr): text(tx + c, ty, h, 11, bold=True)
line(tx, ty + 6, tx + 1040, ty + 6, 1, "#999")
modes = [("20-pin (16V8, 18V10)", ["ON", "off", "off", "ON", "off"], "ZIF 10 / ZIF 28"),
         ("24-pin (22V10, 20V8, 6001…)", ["off", "ON", "off", "ON", "off"], "ZIF 12 / ZIF 28"),
         ("28-pin (26CV12, 26V12)", ["off", "off", "ON", "off", "ON"], "ZIF 21 / ZIF 7")]
for i, (name, st, gv) in enumerate(modes):
    y = ty + 22 + i * 18
    text(tx, y, name, 11)
    for c, v in zip(cols[1:6], st): text(tx + c + 20, y, v, 11, bold=(v == "ON"), fill=CHG if v == "ON" else "#888")
    text(tx + cols[6], y, gv, 11)
text(tx, ty + 82, "Firmware interlock: one GND and one VCC switch per size; all off at reset. Never Q6 with Q7; never Q4 with a 28-pin chip.", 10, fill="#444")

s = s.replace("</svg>", "\n".join(o) + "\n</svg>")
open(DST, "w", encoding="utf-8").write(s)
print("ok", NH)
