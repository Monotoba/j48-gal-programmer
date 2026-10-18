"""Build the Rev G schematic SVG from Rev F by targeted edits plus a new supply-select section."""
import re, sys

SRC, DST = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()

# make it renderable everywhere and grow the canvas for the new section
EXTRA = 294  # bottom group is translated +40
s = s.replace('width="100%" viewBox="0 0 1920 1590"', f'width="1920" height="{1590+EXTRA}" viewBox="0 0 1920 {1590+EXTRA}"')
s = s.replace(' style="max-width:100%;height:auto"', '')
s = s.replace('<rect x="0" y="0" width="1920" height="1590" fill="#ffffff"/>',
              f'<rect x="0" y="0" width="1920" height="{1590+EXTRA}" fill="#ffffff"/>')
s = s.replace('<rect x="8" y="8" width="1904" height="1574" rx="0"',
              f'<rect x="8" y="8" width="1904" height="{1574+EXTRA}" rx="0"')

CHG = "#7b2fa8"   # colour for anything changed in Rev G
FONT = 'font-family="DejaVu Sans Mono, Consolas, monospace"'
count = {"n": 0}

def sub_text(x, y, old, new, recolor=True):
    """Replace the content of the <text> at (x,y) whose content is `old`."""
    pat = re.compile(r'(<text x="%s" y="%s"[^>]*?fill=")([^"]*)(">)%s(</text>)' % (re.escape(str(x)), re.escape(str(y)), re.escape(old)))
    m = pat.search(s_holder[0])
    if not m:
        raise SystemExit(f"text not found: {x},{y} {old!r}")
    fill = CHG if recolor else m.group(2)
    s_holder[0] = s_holder[0][:m.start()] + m.group(1) + fill + m.group(3) + new + m.group(4) + s_holder[0][m.end():]
    count["n"] += 1

s_holder = [s]

# ---- +5V -> VSYS on the logic rail (keep +5V on USB VBUS / F1 / C12) ----
VSYS_LABELS = [(170, 164), (80, 589), (700, 234), (700, 254), (700, 484), (700, 504),
               (790, 559), (790, 589), (70, 734), (340, 1112), (1650, 1154)]
VSYS_FLAGS = [(510, 545), (650, 545), (1875, 985), (1866, 1131)]
for (x, y) in VSYS_LABELS:
    t = s_holder[0]
    m = re.search(r'<text x="%s" y="%s"[^>]*>\+5V</text>' % (x, y), t)
    if not m:
        raise SystemExit(f"+5V label not found at {x},{y}")
    # widen the polygon right before it by one character (6.6 px) on its open side
    pstart = t.rfind('<polygon', 0, m.start())
    pend = t.find('/>', pstart) + 2
    poly = t[pstart:pend]
    pts = re.search(r'points="([^"]+)"', poly).group(1)
    xy = [tuple(map(float, p.split(','))) for p in pts.split()]
    anchor_end = 'text-anchor="end"' in m.group(0)
    if anchor_end:
        mn = min(p[0] for p in xy)
        xy = [((px - 6.6) if px == mn else px, py) for px, py in xy]
    else:
        mx = max(p[0] for p in xy)
        xy = [((px + 6.6) if px == mx else px, py) for px, py in xy]
    newpts = " ".join(f"{round(px,1):g},{round(py,1):g}" for px, py in xy)
    poly2 = poly.replace(pts, newpts)
    t = t[:pstart] + poly2 + t[pend:]
    s_holder[0] = t
    sub_text(x, y, "+5V", "VSYS", recolor=False)
for (x, y) in VSYS_FLAGS:
    sub_text(x, y, "+5V", "VSYS", recolor=False)

# ---- titles / footer ----
sub_text(30, 44, "AVR16DU28 GAL / PLD Programmer — Schematic (Rev F: all-SPI, on-board MIC2288 boost)",
         "AVR16DU28 GAL / PLD Programmer — Schematic (Rev G: 5 V / 3.3 V logic supply, J4)", recolor=False)
sub_text(30, 66, "Native USB · one SPI bus: 74HC595, MCP4821 DAC, 23LC1024 SRAM · ground switch on 595 Q6. Nets connect by name: labels with the same name are joined.",
         "Native USB · one SPI bus: 74HC595, MCP4821 DAC, 23LC1024 SRAM · VSYS = 5 V or 3.3 V (J4) · purple = changed in Rev G. Labels with the same name are joined.", recolor=False)
sub_text(1572, 1497, "Rev F  ·  Sheet 1/1  ·  2026-10-17", "Rev G  ·  Sheet 1/1  ·  2026-10-17", recolor=False)

# ---- MCU block ----
sub_text(380, 132, "SPDIP-28, VDD = 5 V", "SPDIP-28, VDD = VSYS (5 / 3.3 V)")
sub_text(40, 615, "Internal ADC reference 4.096 V (no AREF pin used).",
         "Internal ADC reference 2.500 V (valid at 3.3 V and 5 V).")

# ---- DAC: 1x gain ----
sub_text(910, 372, "12-bit SPI DAC, int. 2.048 V ref, 2× gain", "12-bit SPI DAC, int. 2.048 V ref, 1× gain")
sub_text(930, 430, "0 … 4.096 V", "0 … 2.048 V")
sub_text(930, 444, "1 mV / LSB", "0.5 mV / LSB")

# ---- VPP generator ----
sub_text(490, 674, "VPP generator: MIC2288 boost → DAC → op-amp → pass transistor (0 … 17.6 V)",
         "VPP generator: MIC2288 boost → DAC → op-amp → pass transistor (0 … 17.4 V)")
sub_text(610.0, 1014, "R26 33k 1%", "R26 75k 1%")
sub_text(1222, 1081.0, "47k 1%", "68k 1%")
sub_text(500, 1130, "VPP = DAC × (1 + R26/R27) = DAC × 4.3", "VPP = DAC × (1 + R26/R27) = DAC × 8.5")
sub_text(500, 1146, "4.095 V full scale → 17.6 V; 1 LSB ≈ 4.3 mV", "2.047 V full scale → 17.4 V; 1 LSB ≈ 4.25 mV")
sub_text(500, 1162, "idle (normal mode) on pin 2: DAC 1.163 V → 5.0 V", "idle on pin 2 = VSYS: DAC 0.588 V → 5.0 V, 0.388 V → 3.3 V")

# ---- ground switch ----
sub_text(1495, 810, "2N7000 /", "AO3400")
sub_text(1495, 823, "AO3400", "(not 2N7000)")

# ---- socket power ----
sub_text(40, 912, "SW1 OFF to insert / remove chips. C2/C3 at ZIF pin 24.",
         "SW1: VSYS → VCC_SKT. OFF to insert/remove. C2/C3 at pin 24.")

# ---- SPI notes / numbered notes ----
sub_text(40, 1428, "starts at 0 V; firmware writes the 5 V idle code (≈1163) at boot.",
         "starts at 0 V; firmware writes the idle code (1176 @5 V, 776 @3.3 V) at boot.")
sub_text(40, 1444, "Max SCK from the AVR at 24 MHz is 12 MHz, inside all three parts' limits.",
         "Max SCK 12 MHz at 5 V; at 3.3 V keep SCK ≤ 8 MHz for the 74HC595.")
sub_text(776, 1372, "7. MCP4821 internal reference: trim the DAC code against the PD1 ADC readback (internal 4.096 V ref).",
         "7. MCP4821 internal reference: trim the DAC code against the PD1 ADC readback (internal 2.500 V ref).")
sub_text(776, 1452, "11. U7 holds the fuse map (lifts the 2 KB limit). ZIF23 stays on 595 Q7; all 19 MCU pins are used.",
         "11. U7 holds the fuse map (lifts the 2 KB limit). ZIF23 stays on 595 Q7; all 19 MCU pins are used.", recolor=False)

s = s_holder[0]

# ======================= new section: supply select =======================
out = []
def line(x1, y1, x2, y2, w=1.6, c="#000", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>')
def text(x, y, t, size=10, anchor="start", bold=False, fill="#000"):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out.append(f'<text x="{x}" y="{y}" {FONT} font-size="{size}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}" fill="{fill}">{t}</text>')
def rect(x, y, w, h, fill="none", stroke="#000", sw=1.4, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def dot(x, y):
    out.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#000"/>')
def gnd(x, y):
    line(x, y, x, y + 10)
    line(x - 10, y + 10, x + 10, y + 10, 2); line(x - 6, y + 14, x + 6, y + 14, 2); line(x - 2, y + 18, x + 2, y + 18, 2)
def cap(x, y1, ref, val, y2):
    """vertical cap from node y1 down to ground at y2"""
    line(x, y1, x, y1 + 21); line(x, y1 + 29, x, y2)
    line(x - 11, y1 + 21, x + 11, y1 + 21, 2.4); line(x - 11, y1 + 29, x + 11, y1 + 29, 2.4)
    text(x + 15, y1 + 23, ref, bold=True, fill=CHG); text(x + 15, y1 + 36, val, fill=CHG)
    gnd(x, y2)
def label_left(xtip, y, name, power=False):
    """label pointing right (connection at xtip), text to the left"""
    w = len(name) * 6.6 + 10
    col = "#b3261e" if power else "#1a4fa0"
    out.append(f'<polygon points="{xtip},{y} {xtip-7},{y-8} {xtip-7-w:g},{y-8} {xtip-7-w:g},{y+8} {xtip-7},{y+8}" fill="#eef3fb" stroke="{col}" stroke-width="1.2"/>')
    text(xtip - 10, y + 4, name, 11, "end", True, col)
def label_right(xtail, y, name, power=False):
    w = len(name) * 6.6 + 10
    col = "#b3261e" if power else "#1a4fa0"
    out.append(f'<polygon points="{xtail},{y} {xtail+7},{y-8} {xtail+7+w:g},{y-8} {xtail+7+w:g},{y+8} {xtail+7},{y+8}" fill="#eef3fb" stroke="{col}" stroke-width="1.2"/>')
    text(xtail + 10, y + 4, name, 11, "start", True, col)
def flag(x, y, name):
    """power flag: bar with name above, wire goes down from y"""
    line(x - 9, y, x + 9, y, 2.2, "#b3261e")
    text(x, y - 5, name, 11, "middle", True, "#b3261e")

Y0 = 1544
rect(24, Y0, 1872, 284, dash="7 5", stroke="#8a8a8a", sw=1.2, rx=6)
text(34, Y0 + 18, "Logic supply select (new in Rev G): VSYS = 5 V or 3.3 V", 13, bold=True, fill="#444")

# --- U8 LDO ---
yL = 1625
flag(80, 1600, "+5V"); line(80, 1600, 80, yL)
line(80, yL, 200, yL); dot(130, yL)
cap(130, yL, "C17", "1µ", 1680)
rect(200, 1598, 120, 66, fill="#fffbe6", sw=1.8)
text(200, 1590, "U8", 13, bold=True, fill=CHG)
text(320, 1590, "LDL1117S33", 13, "end", True, CHG)
text(206, yL + 4, "VIN", 11); text(194, yL - 4, "3", 9, "end", fill="#666")
text(314, yL + 4, "VOUT", 11, "end"); text(326, yL - 4, "2,tab", 9, fill="#666")
text(260, 1658, "GND", 11, "middle"); text(266, 1676, "1", 9, fill="#666")
line(260, 1664, 260, 1680); gnd(260, 1680)
line(320, yL, 420, yL); dot(380, yL)
cap(380, yL, "C18", "4.7µ", 1680)
flag(420, 1600, "+3V3"); line(420, 1600, 420, yL)
text(34, 1724, "SOT-223, 1.2 A, stable with ceramic caps.", 10, fill="#666")
text(34, 1738, "C17/C18 values per the LDL1117 datasheet.", 10, fill="#666")

# --- J4 2x3 header ---
xs = [560, 620, 680]
yA, yB = 1630, 1666
rect(538, 1612, 164, 72, fill="#fffbe6", sw=1.8)
text(538, 1604, "J4", 13, bold=True, fill=CHG)
text(538, 1770, "5V: shunts 1–3 + 2–4", 9, fill=CHG)
text(538, 1782, "3V3: shunts 3–5 + 4–6", 9, fill="#1a7f37")
text(708, 1652, "2×3", 11, "start", True, CHG); text(708, 1666, "header", 11, "start", True, CHG)
for i, x in enumerate(xs):
    out.append(f'<circle cx="{x}" cy="{yA}" r="4" fill="#fff" stroke="#000" stroke-width="1.4"/>')
    out.append(f'<circle cx="{x}" cy="{yB}" r="4" fill="#fff" stroke="#000" stroke-width="1.4"/>')
    text(x + 8, yA + 4, str(2 * i + 1), 9, fill="#666")
    text(x + 8, yB + 4, str(2 * i + 2), 9, fill="#666")
# shunt positions
# row A up to flags
line(560, yA - 4, 560, 1612); line(560, 1612, 560, 1590); flag(560, 1590, "+5V")
line(620, yA - 4, 620, 1612); line(620, 1612, 620, 1590); flag(620, 1590, "VSYS")
line(680, yA - 4, 680, 1612); line(680, 1612, 680, 1590); flag(680, 1590, "+3V3")
# row B down
line(560, yB + 4, 560, 1700)
line(554, 1694, 566, 1706, 1.6, "#b3261e"); line(566, 1694, 554, 1706, 1.6, "#b3261e")
text(560, 1720, "NC", 10, "middle", fill="#666")
line(620, yB + 4, 620, 1712)
out.append(f'<polygon points="620,1712 612,1719 612,1731 628,1731 628,1719" fill="#eef3fb" stroke="#b3261e" stroke-width="1.2"/>')
text(620, 1745, "VUSB", 11, "middle", True, "#b3261e")
line(680, yB + 4, 680, 1712)
out.append(f'<polygon points="680,1712 672,1719 672,1731 688,1731 688,1719" fill="#eef3fb" stroke="#b3261e" stroke-width="1.2"/>')
text(680, 1745, "VSYS", 11, "middle", True, "#b3261e")

# --- position table ---
tx = 760
text(tx, 1580, "Position", 11, bold=True); text(tx + 90, 1580, "Shunts", 11, bold=True)
text(tx + 200, 1580, "VSYS", 11, bold=True); text(tx + 270, 1580, "VUSB (U1 pin 6)", 11, bold=True)
line(tx, 1586, tx + 1110, 1586, 1, "#999")
text(tx, 1604, "5V", 11, fill=CHG); text(tx + 90, 1604, "1–3, 2–4", 11)
text(tx + 200, 1604, "+5V", 11); text(tx + 270, 1604, "from U1's internal USB regulator (USBVREG = 1), as Rev F", 11)
text(tx, 1622, "3V3", 11, fill="#1a7f37"); text(tx + 90, 1622, "3–5, 4–6", 11)
text(tx + 200, 1622, "+3V3", 11); text(tx + 270, 1622, "tied to VDD; firmware writes SYSCFG.VUSBCTRL.USBVREG = 0", 11)
text(tx, 1650, "VSYS feeds: U1 VDD (pins 18, 24), U2, U3, U7, J3 pin 2, the R12/R15/R32/R33 pull-ups,", 10, fill="#444")
text(tx, 1664, "and SW1 → VCC_SKT (ZIF pin 24 and the U4 boost input). +5V (VBUS after F1) now feeds only J4 and U8.", 10, fill="#444")

# --- Rev G notes ---
notes = [
 "13. Move the J4 shunts only with USB unplugged, and keep both on the same side (silkscreen \"5V | 3V3\"). Mixed positions put the wrong voltage on VUSB.",
 "14. 3.3 V mode is the datasheet's external-3.3 V power configuration (VDD = VUSB). USB needs VDD ≥ 3.0 V. Check C14 against that configuration.",
 "15. No MCU pin is free for a sense line: firmware measures VDD with the ADC at boot (VDDDIV10 input; confirm the DU has it) and refuses 5 V-only parts at 3.3 V.",
 "16. 3.3 V mode is for low-voltage parts (e.g. ATF16LV8C, ATF22LV10C) and needs Afterburner support for them. GAL16V8/20V8/22V10 and ATF16V8B/22V10C are 5 V only.",
 "17. Firmware changes: U3 at 1× gain (GA bit = 1); VPP = DAC × 8.5; ADC on the 2.500 V reference (R16 68k keeps VPP_SENSE ≤ 2.7 V at maximum VBOOST, below VSYS).",
 "18. Q1 must be a logic-level FET (AO3400, rated at Vgs 2.5 V). In 3.3 V mode U8 also feeds the MIC2288 (≈0.2 A at the 30 mA VPP limit): check U8's temperature.",
]
for i, n in enumerate(notes):
    text(760, 1700 + i * 18, n, 10, fill=CHG if False else "#000")

s = s.replace("</g>\n</svg>", "\n".join(out) + "\n</g>\n</svg>")
open(DST, "w", encoding="utf-8").write(s)
print("text edits:", count["n"], "new elements:", len(out))
