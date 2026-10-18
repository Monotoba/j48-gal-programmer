# J48 Programmer hardware

| Rev | Change |
| --- | --- |
| I | J5 expansion header: VPP, VCC_SKT, VSYS, +5V, SPI bus, 595 latch and output enable, and the end of the 595 chain (U9 Q7′) for adapter boards; see `docs/expansion.md` |
| H | ZIF-28 with every device head-aligned; GAL26CV12/26V12 support; second 74HC595 (U9); per-size GND switches (Q1, Q4, Q5) and VCC switches (Q6, Q7); PA3 reads 26CV12 SDOUT; BOOST_EN moved to U9 |
| G | 5 V / 3.3 V logic supply (J4, U8); DAC at 1× gain, R26 75k; 2.500 V ADC reference, R16 68k; Q1 AO3400 |
| F | All-SPI design: MCP4821 DAC, 23LC1024 SRAM, on-board MIC2288 boost |

## Before ordering PCBs

- [ ] Run ERC in KiCad and assign footprints (the generated schematic has none)
- [ ] Cross-check the 26CV12 programming pinout against published sources
- [ ] Confirm the AVR DU's VDDDIV10 ADC input and USB operation at 3.3 V in the datasheet (DS40002576)
- [ ] Confirm the C14 (VUSB) value and crystal-less USB
- [ ] Check the LM358 VPP loop for oscillation at 5 V and 16.5 V
- [ ] Breadboard on the SPDIP-28 AVR16DU28

The schematic in `drawings/` marks Rev I changes in purple. The ZIF-28 pin map is unchanged from Rev H.
