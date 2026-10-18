"""Rev I drawing from the Rev H drawing: J5 expansion header (power, SPI bus, 595 chain end)."""
import re, sys
SRC, DST = sys.argv[1], sys.argv[2]
s = open(SRC, encoding="utf-8").read()
CHG = "#7b2fa8"
FONT = 'font-family="DejaVu Sans Mono, Consolas, monospace"'

# Rev H's change colour goes back to black; purple now marks Rev I changes
s = s.replace(f'fill="{CHG}"', 'fill="#000"').replace(f'stroke="{CHG}"', 'stroke="#000"')

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def edit_text(x, y, old, new, color=None):
    global s
    pat = re.compile(r'(<text x="%s" y="%s"[^>]*?fill=")([^"]*)("[^>]*>)%s(</text>)' % (re.escape(str(x)), re.escape(str(y)), re.escape(esc(old))))
    m = pat.search(s)
    if not m: raise SystemExit(f"text not found {x},{y} {old!r}")
    s = s[:m.start()] + m.group(1) + (color or m.group(2)) + m.group(3) + esc(new) + m.group(4) + s[m.end():]

def replace_once(old, new):
    global s
    if s.count(old) != 1: raise SystemExit(f"expected one match: {old[:60]!r} ({s.count(old)})")
    s = s.replace(old, new)

# ---- titles ----
edit_text(30, 44, "J48 GAL / PAL Programmer — Schematic (Rev H: ZIF-28, GAL26CV12/26V12 head-aligned)",
          "J48 GAL / PAL Programmer — Schematic (Rev I: J5 expansion header)")
edit_text(30, 66, "Native USB · SPI: 2× 74HC595, MCP4821 DAC, 23LC1024 SRAM · VSYS = 5 V / 3.3 V (J4) · ZIF-28 · purple = changed in Rev H. Same-name labels are joined.",
          "Native USB · SPI: 2× 74HC595, MCP4821 DAC, 23LC1024 SRAM · VSYS = 5 V / 3.3 V (J4) · ZIF-28 · J5 expansion · purple = changed in Rev I.")
edit_text(1572, 1497, "Rev H  ·  Sheet 1/1  ·  2026-10-17", "Rev I  ·  Sheet 1/1  ·  2026-10-18")

# ---- U9 Q7' : no-connect X becomes the SR_CHAIN2 label (end of the on-board 595 chain) ----
replace_once('<line x1="325" y1="2107" x2="335" y2="2117" stroke="#b3261e" stroke-width="1.6"/>\n'
             '<line x1="325" y1="2117" x2="335" y2="2107" stroke="#b3261e" stroke-width="1.6"/>',
             f'<polygon points="330,2112 337,2104 413.6,2104 413.6,2120 337,2120" fill="#eef3fb" stroke="{CHG}" stroke-width="1.2"/>\n'
             f'<text x="340" y="2116" {FONT} font-size="11" text-anchor="start" font-weight="bold" fill="{CHG}">SR_CHAIN2</text>')

# ---- grow the sheet and add the J5 section ----
H0 = int(re.search(r'width="1920" height="(\d+)"', s).group(1))
EX = 266
NH = H0 + EX
replace_once(f'width="1920" height="{H0}" viewBox="0 0 1920 {H0}"', f'width="1920" height="{NH}" viewBox="0 0 1920 {NH}"')
replace_once(f'<rect x="0" y="0" width="1920" height="{H0}" fill="#ffffff"/>', f'<rect x="0" y="0" width="1920" height="{NH}" fill="#ffffff"/>')
replace_once(f'<rect x="8" y="8" width="1904" height="{H0-16}" rx="0"', f'<rect x="8" y="8" width="1904" height="{NH-16}" rx="0"')

o = []
def text(x, y, t, size=11, anchor="start", bold=False, fill="#000"):
    o.append(f'<text x="{x}" y="{y}" {FONT} font-size="{size}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}" fill="{fill}">{esc(str(t))}</text>')
def line(x1, y1, x2, y2, w=1.6, c="#000"):
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>')
def rect(x, y, w, h, fill="none", stroke="#000", sw=1.4, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def lab_l(tip, y, name, power=False):
    w = len(name) * 6.6 + 11; c = "#b3261e" if power else "#1a4fa0"
    o.append(f'<polygon points="{tip},{y} {tip-7},{y-8} {tip-7-w:g},{y-8} {tip-7-w:g},{y+8} {tip-7},{y+8}" fill="#eef3fb" stroke="{c}" stroke-width="1.2"/>')
    text(tip - 10, y + 4, name, 11, "end", True, c)
def lab_r(tail, y, name, power=False):
    w = len(name) * 6.6 + 11; c = "#b3261e" if power else "#1a4fa0"
    o.append(f'<polygon points="{tail},{y} {tail+7},{y-8} {tail+7+w:g},{y-8} {tail+7+w:g},{y+8} {tail+7},{y+8}" fill="#eef3fb" stroke="{c}" stroke-width="1.2"/>')
    text(tail + 10, y + 4, name, 11, "start", True, c)
def gnd(x, y):
    line(x, y, x + 10, y); line(x + 10, y - 10, x + 10, y + 10, 2); line(x + 14, y - 6, x + 14, y + 6, 2); line(x + 18, y - 2, x + 18, y + 2, 2)
def gnd_l(x, y):
    line(x, y, x - 10, y); line(x - 10, y - 10, x - 10, y + 10, 2); line(x - 14, y - 6, x - 14, y + 6, 2); line(x - 18, y - 2, x - 18, y + 2, 2)

Y = H0 - 8
rect(24, Y, 1872, EX - 14, stroke="#8a8a8a", sw=1.2, dash="7 5", rx=6)
text(34, Y + 18, "J5 expansion header (new in Rev I): power, SPI bus and the end of the 595 chain for adapter boards", 13, bold=True, fill="#444")

# J5 2x8 symbol
bx, by = 260, Y + 44
rect(bx, by, 130, 172, fill="#fffbe6", sw=1.8)
text(bx, by - 8, "J5", 13, bold=True, fill=CHG); text(bx + 130, by - 8, "2×8 0.1\"", 12, "end", True, CHG)
odd = [(1, "VPP", True), (3, "VCC_SKT", True), (5, "VSYS", True), (7, "+5V", True),
       (9, "SPI_SCK", False), (11, "SPI_MOSI", False), (13, "SR_RCLK", False), (15, "SR_CHAIN2", False)]
even = [(2, None), (4, None), (6, None), (8, None), (10, None), (12, "SPI_MISO"), (14, "SR_OE"), (16, None)]
for i, (n, net, pw) in enumerate(odd):
    y = by + 20 + i * 20
    text(bx + 8, y + 4, n, 10, fill="#666"); line(bx - 40, y, bx, y); lab_l(bx - 40, y, net, pw)
for i, (n, net) in enumerate(even):
    y = by + 20 + i * 20
    text(bx + 122, y + 4, n, 10, "end", fill="#666"); line(bx + 130, y, bx + 170, y)
    if net: lab_r(bx + 170, y, net)
    else: gnd(bx + 170, y)
text(bx - 210, by + 190, "Power at one end, a GND beside each rail and next to SPI_SCK.", 10, fill="#444")

# signal table
tx, ty = 690, Y + 50
cols = [0, 120, 470]
for c, h in zip(cols, ["J5 pins", "Signal", "Notes"]): text(tx + c, ty, h, 11, bold=True)
line(tx, ty + 6, tx + 1180, ty + 6, 1, "#999")
rows = [
 ("1", "VPP", "Same net as ZIF pin 2: the ZIF socket must be empty when an adapter is in use."),
 ("3", "VCC_SKT", "Off when SW1 is off; the adapter switches it to its own socket."),
 ("5, 7", "VSYS, +5V", "VSYS follows J4 (5 V or 3.3 V); +5V is always 5 V for 5 V-only parts. Both stay live: plug in with USB off."),
 ("9, 11, 12", "SPI_SCK, MOSI, MISO", "Shared with U2, U3, U7 and U9. Adapter devices must release MISO when not selected."),
 ("13, 14", "SR_RCLK, SR_OE", "Latch and output enable for every 595 in the chain, on board and on the adapter."),
 ("15", "SR_CHAIN2", "End of the on-board chain (U9 Q7′). Feed the first adapter 595's SER from here."),
 ("2,4,6,8,10,16", "GND", ""),
]
for i, (p, sig, note) in enumerate(rows):
    y = ty + 24 + i * 19
    text(tx + cols[0], y, p, 11); text(tx + cols[1], y, sig, 11, bold=True); text(tx + cols[2], y, note, 10, fill="#444")
text(tx, ty + 24 + 7 * 19 + 8, "Adapters: 74HC595s on the chain for outputs, 74HC589s (3-state) for inputs over MISO, an SPI EEPROM for an adapter ID. See docs/expansion.md.", 10, fill=CHG)

s = s.replace("</svg>", "\n".join(o) + "\n</svg>")
open(DST, "w", encoding="utf-8").write(s)
print("ok", NH)
