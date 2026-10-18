# J48 GAL / PAL Programmer

A small, inexpensive programmer for the most popular GALs and PALs, built around a single AVR16DU28 microcontroller with native USB. The board is the **J48 Programmer**; the host software is **Wingman**.

> **Status:** schematic at Rev H, not yet built or verified. Firmware and Wingman are not started. Breadboard the design (the AVR16DU28 comes in SPDIP-28) before ordering PCBs.

## Supported devices (planned)

| Family | Examples | Package | Socket position |
| --- | --- | --- | --- |
| 16V8 | GAL16V8, ATF16V8B | 20-pin DIP | ZIF 1–10, 19–28 |
| 18V10 | GAL18V10 | 20-pin DIP | ZIF 1–10, 19–28 |
| 20V8 | GAL20V8, ATF20V8B | 24-pin DIP | ZIF 1–12, 17–28 |
| 22V10 / 20XV10 / 750 | GAL22V10, ATF22V10C, GAL20XV10, ATF750C | 24-pin DIP | ZIF 1–12, 17–28 |
| 6001 / 6002 | GAL6001, GAL6002 | 24-pin DIP | ZIF 1–12, 17–28 |
| 26CV12 / 26V12 | GAL26CV12, GAL26V12 | 28-pin DIP | ZIF 1–28 |
| ATF150x (JTAG) | ATF1502AS, ATF1504AS | via 24-pin adapter | ZIF 1–12, 17–28 |

Every device sits **head-aligned** in a ZIF-28: chip pin 1 at ZIF pin 1, at the lever end. Ground and VCC are switched per chip size, and the socket is unpowered until the firmware selects a device type.

## Hardware highlights (Rev H)

- AVR16DU28 with native USB (no USB-serial chip), UPDI programming header
- Two chained 74HC595 shift registers for socket lines and switch control
- MCP4821 12-bit DAC driving an op-amp and pass transistor for VPP, 0–17.4 V, from an on-board MIC2288 boost converter
- 23LC1024 SPI SRAM for the fuse map
- Logic supply selectable at 5 V or 3.3 V (J4) for low-voltage parts

## Repository layout

```
hardware/
  kicad/       KiCad schematic (KiCad 9 format; KiCad 10 opens it)
  drawings/    schematic as SVG and PDF
  scripts/     generators for the drawings and schematic, plus a netlist check
firmware/      AVR16DU28 firmware (not started)
wingman/       host software (not started)
docs/
  pin-map/     ZIF-28 plan: per-pin roles for every device, switch settings, parts
  spec/        clean-room programming specification (to be written)
  CLEAN_ROOM.md
  why-j48.md   the story behind the name
```

## Building the drawings

```
pip install cairosvg sexpdata
sh hardware/scripts/build.sh
```

This regenerates the Rev H SVG, PDF and KiCad schematic, then checks the KiCad netlist against the intended connections.

## Acknowledgements

The J48 was inspired by [Afterburner](https://github.com/ole00/afterburner) by ole00, which in turn builds on ATFblast (Bruce Abbott), GALBLAST (Manfred Winterhoff) and GALmate (Yorck Thiele). The J48 firmware and Wingman are being written clean-room from public specifications; see [docs/CLEAN_ROOM.md](docs/CLEAN_ROOM.md).

## License

| Part | License |
| --- | --- |
| Hardware (`hardware/`) and docs | [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt) |
| Firmware and Wingman (`firmware/`, `wingman/`) | [GPL-3.0-only](LICENSES/GPL-3.0-only.txt) |

Both are reciprocal: anyone who distributes a modified board or modified software must share their changes under the same terms. See [LICENSE](LICENSE) for details.
