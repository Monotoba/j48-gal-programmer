"""Generate a KiCad schematic (.kicad_sch, KiCad 9 format; KiCad 10 opens and upgrades it)
for the GAL programmer Rev I. Connectivity is by net labels on short wire stubs at every pin,
matching the Rev F/G drawing convention (labels with the same name are joined)."""
import uuid, json, sys

OUT = sys.argv[1]
NS = uuid.UUID("6b1f3f52-2c1e-4e7a-9d55-0a1b2c3d4e5f")
_n = [0]
def U(tag=None):
    _n[0] += 1
    return str(uuid.uuid5(NS, f"{tag or ''}#{_n[0]}"))
ROOT = U("root")
G = 2.54

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
def f(v):
    return f"{round(v, 3):g}"
EFF = "(effects (font (size 1.27 1.27)))"
EFFH = "(effects (font (size 1.27 1.27)) (hide yes))"

# ---------------------------------------------------------------- symbols
LIB = {}     # name -> dict(pins=[(num,name,x,y,ang,len)], body=str, refprefix, refpos, valpos)

def two_pin(name, prefix, body, pinnames=("~", "~"), nums=("1", "2")):
    LIB[name] = dict(prefix=prefix, body=body, pins=[(nums[0], pinnames[0], 0, 3.81, 270, 1.27), (nums[1], pinnames[1], 0, -3.81, 90, 1.27)],
                     refpos=(2.54, -0.635), valpos=(2.54, 1.27), hide_pin_names=True)

stroke = "(stroke (width 0.254) (type default))"
two_pin("R", "R", f"(rectangle (start -1.016 2.54) (end 1.016 -2.54) {stroke} (fill (type none)))")
two_pin("C", "C", f"(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))"
                  f"(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))"
                  f"(polyline (pts (xy 0 2.54) (xy 0 0.762)) {stroke} (fill (type none)))"
                  f"(polyline (pts (xy 0 -2.54) (xy 0 -0.762)) {stroke} (fill (type none)))")
two_pin("CP", "C", LIB["C"]["body"] + f"(text \"+\" (at -1.27 1.778 0) {EFF})", nums=("1", "2"))
two_pin("L", "L", f"(rectangle (start -0.762 2.54) (end 0.762 -2.54) {stroke} (fill (type outline)))")
two_pin("F", "F", f"(rectangle (start -0.762 2.032) (end 0.762 -2.032) {stroke} (fill (type none)))"
                  f"(polyline (pts (xy 0 2.54) (xy 0 -2.54)) {stroke} (fill (type none)))")
# diodes: pin1 = K (top), pin2 = A (bottom); current flows up
two_pin("D", "D", f"(polyline (pts (xy -1.27 1.016) (xy 1.27 1.016)) {stroke} (fill (type none)))"
                  f"(polyline (pts (xy -1.27 -1.016) (xy 1.27 -1.016) (xy 0 1.016) (xy -1.27 -1.016)) {stroke} (fill (type none)))",
        pinnames=("K", "A"))
two_pin("LED", "D", LIB["D"]["body"] + f"(polyline (pts (xy 1.778 0.254) (xy 2.794 1.27)) {stroke} (fill (type none)))", pinnames=("K", "A"))
two_pin("SW", "SW", f"(polyline (pts (xy 0 2.54) (xy 0 1.016)) {stroke} (fill (type none)))"
                    f"(polyline (pts (xy 0 -2.54) (xy 0 -1.016) (xy 1.524 1.27)) {stroke} (fill (type none)))")

def box(name, prefix, left, right, top=(), bottom=(), width=None):
    """left/right: lists of (number, pinname) top->bottom; None = spacer."""
    n = max(len(left), len(right), 1)
    maxl = max([len(p[1]) for p in left if p] + [0]); maxr = max([len(p[1]) for p in right if p] + [0])
    w = width or max(10.16, round(((maxl + maxr) * 1.0 + 6) / G) * G)
    w = round(w / G) * G
    h = (n + 1) * G
    top_y = h / 2
    pins = []
    for i, p in enumerate(left):
        if p: pins.append((p[0], p[1], -w / 2 - 2.54, top_y - (i + 1) * G, 0, 2.54))
    for i, p in enumerate(right):
        if p: pins.append((p[0], p[1], w / 2 + 2.54, top_y - (i + 1) * G, 180, 2.54))
    for i, p in enumerate(top):
        pins.append((p[0], p[1], -((len(top) - 1) * G) / 2 + i * G, top_y + 2.54, 270, 2.54))
    for i, p in enumerate(bottom):
        pins.append((p[0], p[1], -((len(bottom) - 1) * G) / 2 + i * G, -top_y - 2.54, 90, 2.54))
    body = f"(rectangle (start {f(-w/2)} {f(top_y)}) (end {f(w/2)} {f(-top_y)}) {stroke} (fill (type background)))"
    LIB[name] = dict(prefix=prefix, body=body, pins=pins, refpos=(-w / 2, top_y + 1.27), valpos=(w / 2, top_y + 1.27),
                     hide_pin_names=False, h=h, w=w)

box("AVR16DU28", "U",
    left=[("18", "VDD"), ("24", "VDD"), ("6", "VUSB"), ("8", "DP"), ("7", "DM"), ("22", "PF6/~{RESET}"), ("23", "PF7/UPDI"),
          None, ("19", "GND"), ("25", "GND")],
    right=[("26", "PA0"), ("27", "PA1"), ("28", "PA2"), ("1", "PA3"), ("2", "PA4/MOSI"), ("3", "PA5/MISO"), ("4", "PA6/SCK"), ("5", "PA7"),
           ("9", "PC3"), ("10", "PD0"), ("11", "PD1/AIN1"), ("12", "PD2"), ("13", "PD3"), ("14", "PD4"), ("15", "PD5"), ("16", "PD6"),
           ("17", "PD7"), ("20", "PF0"), ("21", "PF1")])
box("74HC595", "U",
    left=[("14", "SER"), ("11", "SRCLK"), ("12", "RCLK"), ("13", "~{OE}"), ("10", "~{MR}"), ("16", "VCC"), ("8", "GND")],
    right=[("15", "Q0"), ("1", "Q1"), ("2", "Q2"), ("3", "Q3"), ("4", "Q4"), ("5", "Q5"), ("6", "Q6"), ("7", "Q7"), ("9", "Q7'")])
box("MCP4821", "U",
    left=[("2", "~{CS}"), ("3", "SCK"), ("4", "SDI"), ("5", "~{LDAC}"), ("6", "~{SHDN}"), ("1", "VDD"), ("7", "VSS")],
    right=[("8", "VOUT")])
box("23LC1024", "U",
    left=[("1", "~{CS}"), ("2", "SO/SIO1"), ("5", "SI/SIO0"), ("6", "SCK")],
    right=[("8", "VCC"), ("3", "SIO2"), ("7", "~{HOLD}"), ("4", "VSS")])
box("MIC2288", "U", left=[("5", "VIN"), ("4", "EN"), ("2", "GND")], right=[("1", "SW"), ("3", "FB")])
box("LDL1117S33", "U", left=[("3", "VIN"), ("1", "GND")], right=[("2", "VOUT")])
box("LM358", "U",
    left=[("3", "+A"), ("2", "-A"), ("5", "+B"), ("6", "-B"), None, ("8", "V+"), ("4", "V-")],
    right=[("1", "OUTA"), None, None, ("7", "OUTB")])
box("ZIF28", "J",
    left=[(str(i), str(i)) for i in range(1, 15)], right=[(str(i), str(i)) for i in range(28, 14, -1)], width=12.7)
box("USB_C_2.0", "J",
    left=[("A4", "VBUS"), ("A9", "VBUS"), ("B4", "VBUS"), ("B9", "VBUS"), ("A5", "CC1"), ("B5", "CC2"), ("A8", "SBU1"), ("B8", "SBU2")],
    right=[("A6", "D+"), ("B6", "D+"), ("A7", "D-"), ("B7", "D-"), ("A1", "GND"), ("A12", "GND"), ("B1", "GND"), ("B12", "GND")])
box("Conn_1x03", "J", left=[("1", "1"), ("2", "2"), ("3", "3")], right=[])
box("Conn_2x08", "J", left=[(str(i), str(i)) for i in range(1, 17, 2)], right=[(str(i), str(i)) for i in range(2, 17, 2)])
box("Conn_2x03", "J", left=[("1", "1"), ("3", "3"), ("5", "5")], right=[("2", "2"), ("4", "4"), ("6", "6")])
box("NPN_ECB", "Q", left=[("3", "B")], right=[("2", "C"), ("1", "E")])          # BD139: 1=E 2=C 3=B
box("NPN_CBE", "Q", left=[("2", "B")], right=[("1", "C"), ("3", "E")])          # BC547: 1=C 2=B 3=E
box("NMOS_GSD", "Q", left=[("1", "G")], right=[("3", "D"), ("2", "S")])         # AO3400 SOT-23: 1=G 2=S 3=D
box("PMOS_GSD", "Q", left=[("1", "G")], right=[("2", "S"), ("3", "D")])         # AO3401 SOT-23: 1=G 2=S 3=D

def lib_symbol(name):
    d = LIB[name]
    pn = "(pin_names (offset 0) (hide yes))" if d["hide_pin_names"] else "(pin_names (offset 1.016))"
    pins = ""
    for (num, pname, x, y, ang, ln) in d["pins"]:
        pins += (f"(pin passive line (at {f(x)} {f(y)} {ang}) (length {f(ln)}) "
                 f"(name {q(pname)} {EFF}) (number {q(num)} {EFF}))")
    return (f"(symbol {q('GALProg:' + name)} {pn} (exclude_from_sim no) (in_bom yes) (on_board yes)"
            f"(property \"Reference\" {q(d['prefix'])} (at 0 0 0) {EFF})"
            f"(property \"Value\" {q(name)} (at 0 0 0) {EFF})"
            f"(property \"Footprint\" \"\" (at 0 0 0) {EFFH})"
            f"(property \"Datasheet\" \"\" (at 0 0 0) {EFFH})"
            f"(property \"Description\" \"\" (at 0 0 0) {EFFH})"
            f"(symbol {q(name + '_0_1')} {d['body']})"
            f"(symbol {q(name + '_1_1')} {pins}))")

# ---------------------------------------------------------------- netlist (Rev H)
# part: ref -> (libname, value, {pin_number: net or None for no-connect}, note)
P = {}
def part(ref, lib, val, pins, desc=""):
    P[ref] = (lib, val, pins, desc)

ZIFR = {"R1": ("PC3", "ZIF19"), "R2": ("PD0", "ZIF3"), "R3": ("PD2", "ZIF8"), "R4": ("PD3", "ZIF9"), "R5": ("PD4", "ZIF10"),
        "R6": ("PD5", "ZIF11"), "R7": ("PD6", "ZIF17"), "R8": ("PD7", "ZIF18"), "R9": ("PF0", "ZIF20"), "R10": ("PF1", "ZIF26")}
part("U1", "AVR16DU28", "AVR16DU28-I/SP", {
    "18": "VSYS", "24": "VSYS", "6": "VUSB", "8": "USB_DP", "7": "USB_DM", "22": "RESET", "23": "UPDI", "19": "GND", "25": "GND",
    "26": "SRAM_CS", "27": "SR_OE", "28": "DAC_CS", "1": "MCU_PA3", "2": "SPI_MOSI", "3": "SPI_MISO", "4": "SPI_SCK", "5": "SR_RCLK",
    "9": "MCU_PC3", "10": "MCU_PD0", "11": "VPP_SENSE", "12": "MCU_PD2", "13": "MCU_PD3", "14": "MCU_PD4", "15": "MCU_PD5",
    "16": "MCU_PD6", "17": "MCU_PD7", "20": "MCU_PF0", "21": "MCU_PF1"}, "AVR DU, SPDIP-28; pin numbers per DS40002576 I/O multiplexing table")
for r, (port, z) in ZIFR.items():
    part(r, "R", "100", {"1": "MCU_" + port, "2": z})
part("R32", "R", "10k", {"1": "VSYS", "2": "RESET"})
part("C13", "C", "100n", {"1": "VSYS", "2": "GND"})
part("C14", "C", "per DS (VUSB)", {"1": "VUSB", "2": "GND"})

part("U2", "74HC595", "74HC595", {"14": "SPI_MOSI", "11": "SPI_SCK", "12": "SR_RCLK", "13": "SR_OE", "10": "VSYS", "16": "VSYS", "8": "GND",
     "15": "ZIF4", "1": "U2_Q1", "2": "ZIF6", "3": "ZIF5", "4": "ZIF25", "5": "ZIF24", "6": "GNDSW_EN", "7": "ZIF27", "9": "SR_CHAIN"})
part("C1", "C", "100n", {"1": "VSYS", "2": "GND"})
part("U3", "MCP4821", "MCP4821-E/P", {"2": "DAC_CS", "3": "SPI_SCK", "4": "SPI_MOSI", "5": "GND", "6": "VSYS", "1": "VSYS", "7": "GND", "8": "DAC_OUT"},
     "Rev G: run at 1x gain (GA bit = 1), 0-2.048 V")
part("R12", "R", "10k", {"1": "VSYS", "2": "SR_OE"})
part("R15", "R", "10k", {"1": "VSYS", "2": "DAC_CS"})
part("R13", "R", "100k", {"1": "DAC_OUT", "2": "GND"})

zif = {str(i): f"ZIF{i}" for i in range(1, 29)}
zif["2"] = "VPP"
part("J1", "ZIF28", "ZIF-28, 0.3/0.6in", zif, "Rev H: ZIF-28 (was ZIF-24); all devices head-aligned")

part("SW1", "SW", "latching push", {"1": "VSYS", "2": "VCC_SKT"}, "Rev G: switches VSYS (was +5V)")
part("R14", "R", "1k", {"1": "VCC_SKT", "2": "LED_A"})
part("D1", "LED", "LED", {"1": "GND", "2": "LED_A"})
part("C2", "CP", "10u", {"1": "VCC_SKT", "2": "GND"})
part("C3", "C", "100n", {"1": "VCC_SKT", "2": "GND"})
part("J2", "USB_C_2.0", "USB-C 2.0 receptacle", {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2",
     "A8": None, "B8": None, "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DM", "B7": "USB_DM", "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND"})
part("F1", "F", "500mA PTC", {"1": "VBUS", "2": "+5V"})
part("R30", "R", "5.1k", {"1": "CC1", "2": "GND"})
part("R31", "R", "5.1k", {"1": "CC2", "2": "GND"})
part("C12", "CP", "10u", {"1": "+5V", "2": "GND"})
part("J3", "Conn_1x03", "UPDI", {"1": "UPDI", "2": "VSYS", "3": "GND"})

part("U4", "MIC2288", "MIC2288YD5", {"5": "VCC_SKT", "4": "BOOST_EN", "2": "GND", "1": "SW_NODE", "3": "BFB"})
part("C16", "C", "2.2u", {"1": "VCC_SKT", "2": "GND"})
part("L1", "L", "10uH Isat>=1.5A", {"1": "VCC_SKT", "2": "SW_NODE"})
part("D2", "D", "SS14", {"1": "VBOOST", "2": "SW_NODE"})
part("C9", "C", "4.7u/50V", {"1": "VBOOST", "2": "GND"})
part("C11", "C", "100n/50V", {"1": "VBOOST", "2": "GND"})
part("R34", "R", "75k 1%", {"1": "VBOOST", "2": "BFB"})
part("R35", "R", "4.7k 1%", {"1": "BFB", "2": "GND"})
part("R36", "R", "100k", {"1": "BOOST_EN", "2": "GND"})
part("U6", "LM358", "LM358", {"3": "DAC_OUT", "2": "FBN", "1": "U6A_OUT", "5": "GND", "6": "U6B_OUT", "7": "U6B_OUT", "8": "VBOOST", "4": "GND"})
part("R24", "R", "470", {"1": "U6A_OUT", "2": "Q2_B"})
part("Q2", "NPN_ECB", "BD139", {"3": "Q2_B", "2": "VBOOST", "1": "Q2_E"})
part("R25", "R", "22", {"1": "Q2_E", "2": "VPP"})
part("Q3", "NPN_CBE", "BC547", {"2": "Q2_E", "1": "Q2_B", "3": "VPP"})
part("R26", "R", "75k 1%", {"1": "VPP", "2": "FBN"}, "Rev G: was 33k (gain 8.5)")
part("C10", "C", "1n", {"1": "VPP", "2": "FBN"})
part("R27", "R", "10k 1%", {"1": "FBN", "2": "GND"})
part("C4", "C", "1u/25V", {"1": "VPP", "2": "GND"})
part("C5", "C", "100n/50V", {"1": "VPP", "2": "GND"})
part("R28", "R", "4.7k", {"1": "VPP", "2": "GND"})
part("R16", "R", "68k 1%", {"1": "VPP", "2": "VPP_SENSE"}, "Rev G: was 47k (2.500 V ADC ref)")
part("R17", "R", "10k 1%", {"1": "VPP_SENSE", "2": "GND"})

part("Q1", "NMOS_GSD", "AO3400", {"1": "Q1_G", "3": "ZIF10", "2": "GND"}, "Rev G: logic-level FET required (not 2N7000)")
part("R18", "R", "100", {"1": "GNDSW_EN", "2": "Q1_G"})
part("R19", "R", "100k", {"1": "Q1_G", "2": "GND"})
for r, z in (("R20", "ZIF1"), ("R21", "ZIF21"), ("R22", "ZIF22"), ("R23", "ZIF23")):
    part(r, "R", "10k", {"1": z, "2": "GND"})
part("U7", "23LC1024", "23LC1024-I/P", {"1": "SRAM_CS", "2": "SPI_MISO", "5": "SPI_MOSI", "6": "SPI_SCK", "8": "VSYS", "3": "VSYS", "7": "VSYS", "4": "GND"})
part("R33", "R", "10k", {"1": "VSYS", "2": "SRAM_CS"})
part("C15", "C", "100n", {"1": "VSYS", "2": "GND"})

# Rev H additions: 28-pin GAL26CV12/26V12 support
part("U9", "74HC595", "74HC595", {"14": "SR_CHAIN", "11": "SPI_SCK", "12": "SR_RCLK", "13": "SR_OE", "10": "VSYS", "16": "VSYS", "8": "GND",
     "15": "U9_Q0", "1": "ZIF13", "2": "ZIF14", "3": "BOOST_EN", "4": "GND12_EN", "5": "GND21_EN", "6": "VCC28_EN", "7": "VCC7_EN", "9": "SR_CHAIN2"},
     "Rev H: chained from U2 Q7'; Rev I: Q7' to J5 pin 15")
part("C19", "C", "100n", {"1": "VSYS", "2": "GND"}, "Rev H: U9 decoupling")
part("Q4", "NMOS_GSD", "AO3400", {"1": "Q4_G", "3": "ZIF12", "2": "GND"}, "Rev H: ZIF12 ground switch (24-pin)")
part("Q5", "NMOS_GSD", "AO3400", {"1": "Q5_G", "3": "ZIF21", "2": "GND"}, "Rev H: ZIF21 ground switch (28-pin)")
part("Q6", "PMOS_GSD", "AO3401", {"1": "VCC28_EN", "2": "VCC_SKT", "3": "ZIF28"}, "Rev H: ZIF28 VCC switch (20/24-pin)")
part("Q7", "PMOS_GSD", "AO3401", {"1": "VCC7_EN", "2": "VCC_SKT", "3": "ZIF7"}, "Rev H: ZIF7 VCC switch (28-pin)")
part("R37", "R", "100", {"1": "GND12_EN", "2": "Q4_G"})
part("R38", "R", "100", {"1": "GND21_EN", "2": "Q5_G"})
part("R39", "R", "100k", {"1": "Q4_G", "2": "GND"})
part("R40", "R", "100k", {"1": "Q5_G", "2": "GND"})
part("R41", "R", "100k", {"1": "VCC_SKT", "2": "VCC28_EN"})
part("R42", "R", "100k", {"1": "VCC_SKT", "2": "VCC7_EN"})
part("R43", "R", "100", {"1": "U2_Q1", "2": "ZIF7"})
part("R44", "R", "100", {"1": "U9_Q0", "2": "ZIF12"})
part("R45", "R", "100", {"1": "MCU_PA3", "2": "ZIF15"})
part("R46", "R", "10k", {"1": "ZIF16", "2": "GND"})
part("R47", "R", "10k", {"1": "ZIF28", "2": "GND"})

# Rev I addition: J5 expansion header
part("J5", "Conn_2x08", "Expansion 2x8", {"1": "VPP", "2": "GND", "3": "VCC_SKT", "4": "GND", "5": "VSYS", "6": "GND",
     "7": "+5V", "8": "GND", "9": "SPI_SCK", "10": "GND", "11": "SPI_MOSI", "12": "SPI_MISO",
     "13": "SR_RCLK", "14": "SR_OE", "15": "SR_CHAIN2", "16": "GND"},
     "Rev I: expansion header for adapter boards; see docs/expansion.md")

# Rev G additions
part("U8", "LDL1117S33", "LDL1117S33R", {"3": "+5V", "1": "GND", "2": "+3V3"}, "Rev G: 3.3 V LDO, SOT-223 (tab = VOUT)")
part("C17", "C", "1u", {"1": "+5V", "2": "GND"}, "Rev G")
part("C18", "C", "4.7u", {"1": "+3V3", "2": "GND"}, "Rev G")
part("J4", "Conn_2x03", "VSYS select 2x3", {"1": "+5V", "3": "VSYS", "5": "+3V3", "2": None, "4": "VUSB", "6": "VSYS"},
     "Rev G: 5V = shunts 1-3 + 2-4; 3V3 = shunts 3-5 + 4-6")

# ---------------------------------------------------------------- placement (mm, A2 landscape)
PLACE = {
    "U9": (300, 60), "J5": (330, 300), "Q4": (540, 300), "Q5": (540, 330), "Q6": (470, 300), "Q7": (470, 330),
    "U1": (70, 75), "U2": (200, 60), "U3": (200, 125), "U7": (470, 245), "J1": (430, 70),
    "J2": (40, 245), "J3": (40, 300), "U4": (180, 200), "U6": (180, 260), "Q2": (260, 260), "Q3": (260, 295), "Q1": (380, 205),
    "U8": (90, 360), "J4": (200, 360),
}
def row(refs, x0, y0, dx=15.24):
    for i, r in enumerate(refs):
        PLACE[r] = (x0 + i * dx, y0)
row([f"R{i}" for i in range(1, 11)], 15, 155)
row(["R32", "C13", "C14", "C1", "R12", "R15", "R13"], 185, 155)
row(["SW1", "R14", "D1", "C2", "C3", "F1", "R30", "R31", "C12"], 15, 195)
row(["C16", "L1", "D2", "C9", "C11", "R34", "R35", "R36"], 230, 195)
row(["R24", "R25", "R26", "C10", "R27", "C4", "C5", "R28", "R16", "R17"], 300, 255)
row(["R18", "R19", "R20", "R21", "R22", "R23"], 420, 195)
row(["R33", "C15"], 520, 230)
row(["C17", "C18"], 125, 360)
row(["C19", "R37", "R38", "R39", "R40", "R41", "R42", "R43", "R44", "R45", "R46", "R47"], 255, 375)

# ---------------------------------------------------------------- emit
items = []
labels = []
wires = []
ncs = []
def snap(v):
    return round(v / 1.27) * 1.27

missing = [r for r in P if r not in PLACE]
assert not missing, missing
pin_ends = {}   # (ref,pin) -> sheet xy of pin end
for ref, (lib, val, pins, desc) in P.items():
    d = LIB[lib]
    X, Y = PLACE[ref]
    X, Y = snap(X), snap(Y)
    libpins = {p[0]: p for p in d["pins"]}
    assert set(libpins) == set(pins), (ref, set(libpins) ^ set(pins))
    rx, ry = d["refpos"]; vx, vy = d["valpos"]
    two = lib in ("R", "C", "CP", "L", "F", "D", "LED", "SW")
    if two:
        refat = f"(at {f(X + 2.54)} {f(Y - 0.635)} 0) (effects (font (size 1.27 1.27)) (justify left))"
        valat = f"(at {f(X + 2.54)} {f(Y + 1.27)} 0) (effects (font (size 1.27 1.27)) (justify left))"
    else:
        refat = f"(at {f(X + rx)} {f(Y - ry)} 0) (effects (font (size 1.27 1.27)) (justify left bottom))"
        valat = f"(at {f(X + vx)} {f(Y - vy)} 0) (effects (font (size 1.27 1.27)) (justify right bottom))"
    pinuuids = "".join(f"(pin {q(n)} (uuid {q(U())}))" for n in pins)
    items.append(
        f"(symbol (lib_id {q('GALProg:' + lib)}) (at {f(X)} {f(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)"
        f" (uuid {q(U(ref))})"
        f" (property \"Reference\" {q(ref)} {refat})"
        f" (property \"Value\" {q(val)} {valat})"
        f" (property \"Footprint\" \"\" (at {f(X)} {f(Y)} 0) {EFFH})"
        f" (property \"Datasheet\" \"\" (at {f(X)} {f(Y)} 0) {EFFH})"
        f" (property \"Description\" {q(desc)} (at {f(X)} {f(Y)} 0) {EFFH})"
        f" {pinuuids}"
        f" (instances (project \"J48_RevI\" (path {q('/' + ROOT)} (reference {q(ref)}) (unit 1)))))")
    for num, net in pins.items():
        _, pname, px, py, ang, ln = libpins[num]
        sx, sy = X + px, Y - py          # library y is up, sheet y is down
        pin_ends[(ref, num)] = (round(sx, 3), round(sy, 3))
        # outward direction = opposite of pin angle
        ox, oy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[ang]
        if net is None:
            ncs.append(f"(no_connect (at {f(sx)} {f(sy)}) (uuid {q(U())}))")
            continue
        ex, ey = sx + ox * 2.54, sy + oy * 2.54
        wires.append(f"(wire (pts (xy {f(sx)} {f(sy)}) (xy {f(ex)} {f(ey)})) (stroke (width 0) (type default)) (uuid {q(U())}))")
        if ox == -1:
            labels.append(f"(label {q(net)} (at {f(ex)} {f(ey)} 180) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid {q(U())}))")
        else:
            labels.append(f"(label {q(net)} (at {f(ex)} {f(ey)} 0) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {q(U())}))")

def note(x, y, t, size=1.27):
    items.append(f"(text {q(t)} (exclude_from_sim no) (at {f(x)} {f(y)} 0) (effects (font (size {size} {size})) (justify left bottom)) (uuid {q(U())}))")

note(15, 18, "J48 GAL / PAL Programmer (AVR16DU28) - Rev I: J5 expansion header", 2.54)
note(15, 24, "Connectivity is by net label on each pin stub. Footprints are not assigned. Generated from the Rev I netlist; run ERC after opening.")
note(255, 365, "ZIF-28 switching (new in Rev H): U9 595 drives SCLK/SDIN/STB, BOOST_EN and the GND/VCC switches. All switches off at reset.")
note(15, 340, "Logic supply select (new in Rev G): VSYS = 5 V or 3.3 V")
note(15, 395,
     "J4 5V position: shunts 1-3 + 2-4 -> VSYS = +5V, VUSB from U1's internal USB regulator (USBVREG = 1).\n"
     "J4 3V3 position: shunts 3-5 + 4-6 -> VSYS = +3V3, VUSB tied to VDD; firmware writes SYSCFG.VUSBCTRL.USBVREG = 0.\n"
     "Move shunts only with USB unplugged; both on the same side. Firmware reads VDD via the ADC at boot (no pin free for a sense line).\n"
     "Rev G value changes: U3 MCP4821 at 1x gain (GA = 1); R26 75k (VPP = DAC x 8.5); R16 68k with the 2.500 V ADC reference;\n"
     "Q1 must be logic-level (AO3400); at 3.3 V keep SPI SCK <= 8 MHz for the 74HC595.")

title = ("(title_block (title \"J48 GAL / PAL Programmer - AVR16DU28\") (date \"2026-10-18\") (rev \"I\")"
         " (comment 1 \"ZIF-28; J4 5 V / 3.3 V; J5 expansion header\") (comment 2 \"ZIF pin map derived from Afterburner (ole00)\"))")
used = sorted({P[r][0] for r in P})
doc = ("(kicad_sch (version 20250114) (generator \"eeschema\") (generator_version \"9.0\")"
       f" (uuid {q(ROOT)}) (paper \"A2\") {title}"
       f" (lib_symbols {''.join(lib_symbol(n) for n in used)})"
       f" {' '.join(wires)} {' '.join(labels)} {' '.join(ncs)} {' '.join(items)}"
       " (sheet_instances (path \"/\" (page \"1\"))) (embedded_fonts no))")

# light pretty-print: newline before each top-level item
for kw in ["(lib_symbols", "(symbol (lib_id", "(wire", "(label", "(no_connect", "(text ", "(sheet_instances", "(title_block", "(symbol \"GALProg:"]:
    doc = doc.replace(" " + kw, "\n  " + kw)
open(OUT, "w", encoding="utf-8").write(doc + "\n")

# write the intended netlist for verification
nets = {}
for ref, (lib, val, pins, desc) in P.items():
    for num, net in pins.items():
        if net: nets.setdefault(net, []).append(f"{ref}.{num}")
json.dump({"nets": nets, "pin_ends": {f"{k[0]}.{k[1]}": v for k, v in pin_ends.items()}}, open(OUT + ".intended.json", "w"), indent=1)
print(f"parts {len(P)}, nets {len(nets)}, labels {len(labels)}, no-connects {len(ncs)}")
