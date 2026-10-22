# J5 expansion header

J5 lets an adapter board add sockets or devices the J48 doesn't support on its own ZIF-28, such as a future 40-pin adapter. It carries power, the SPI bus and the end of the on-board 74HC595 chain, so an adapter needs no extra MCU pins: everything it does goes over SPI.

## Pinout (2×8, 0.1" pitch)

| Pin | Signal | Pin | Signal |
| --- | --- | --- | --- |
| 1 | VPP | 2 | GND |
| 3 | VCC_SKT | 4 | GND |
| 5 | VSYS | 6 | GND |
| 7 | +5V | 8 | GND |
| 9 | SPI_SCK | 10 | GND |
| 11 | SPI_MOSI | 12 | SPI_MISO |
| 13 | SR_RCLK | 14 | SR_OE |
| 15 | SR_CHAIN2 | 16 | GND |

Power sits at one end with a ground beside each rail, so a stray VPP short lands on ground rather than a logic line. SPI_SCK has a ground beside it.

## Signals

| Signal | What it is | Rules |
| --- | --- | --- |
| VPP | Programmable 0–17.4 V from the VPP generator | Same net as ZIF pin 2. The ZIF-28 must be empty while an adapter uses VPP. The adapter switches VPP to its own socket pins. |
| VCC_SKT | Socket supply after SW1 | Off when SW1 is off. The adapter switches it to its socket's VCC pin. |
| VSYS | Logic supply, 5 V or 3.3 V per J4 | Always on. Power for the adapter's logic. |
| +5V | USB 5 V after the fuse | Always on, and always 5 V regardless of J4. For 5 V-only target parts. |
| SPI_SCK, SPI_MOSI, SPI_MISO | SPI0 from the AVR16DU28 (mode 0, up to 12 MHz at 5 V; 8 MHz at 3.3 V) | Shared with U2, U3, U7 and U9. Any adapter device that drives MISO must release it when not selected. |
| SR_RCLK | Latch for every 74HC595 in the chain | A rising edge moves the shifted data to the outputs of all 595s at once. |
| SR_OE | Output enable for every 595 in the chain | High at reset (pulled up on the J48), so all chain outputs are off until firmware enables them. |
| SR_CHAIN2 | End of the on-board chain (U9 Q7′) | Connect to SER (pin 14) of the adapter's first 595. |

## Building an adapter

**Outputs: extend the 595 chain.** Chain 74HC595s from SR_CHAIN2: the first one's SER from SR_CHAIN2, each next one's SER from the previous one's Q7′. Tie SRCLK to SPI_SCK, RCLK to SR_RCLK and /OE to SR_OE. Each 595 adds 8 outputs. Use them for socket signals, chip selects, and the adapter's own VPP, VCC and GND switches. Give every switch a gate resistor that holds it off while /OE is high, as on the J48 (Q4–Q7).

**Inputs: 74HC589 over MISO.** For pins the firmware must read, use 74HC589 shift registers: they latch 8 parallel inputs and have a three-state serial output, so they release MISO when not selected. Drive their latch and output-enable from adapter 595 outputs. Avoid the 74HC165 here: its serial output is always driven and would fight the SRAM on MISO.

**Identification: an SPI EEPROM.** Fit a small SPI EEPROM (for example a 25AA010A) with its chip select from an adapter 595 output. Firmware reads it at power-up. Suggested contents:

| Bytes | Contents |
| --- | --- |
| 0–3 | `J48A` (marks an adapter) |
| 4 | Format version (1) |
| 5 | Number of 595s on the adapter (chain length added) |
| 6 | Bit position, in the adapter's chain, of the EEPROM chip select |
| 7–8 | Adapter type ID |
| 9–31 | Adapter name, ASCII, zero-padded |

The J48 can't know the EEPROM's chip-select position before reading it, so adapters should put it at a fixed place: **bit 0 of the adapter's first 595** (the first output after SR_CHAIN2), active low.

**Optional: chain loopback.** An adapter may route the Q7′ of its last 595 back to MISO through a three-state buffer (a 74HC125 gate) enabled by one of its own 595 outputs. Firmware can then shift a test pattern through the whole chain and read it back, which confirms the chain length and catches a missing or damaged adapter.

## Firmware rules

- **One socket at a time.** With an adapter attached, keep all ZIF-28 GND and VCC switches off and leave the ZIF-28 empty.
- **Update the whole chain every time.** Each latch moves every 595 at once, so firmware shifts the full chain (on-board plus adapter bytes, adapter bytes first) before each SR_RCLK pulse.
- **SPI traffic to other devices passes through the chain.** Bytes sent to the DAC, SRAM or adapter devices also shift through every 595, but outputs change only on a latch. Firmware must always re-send the full chain before the next latch.
- **Hot-plugging:** VSYS and +5V stay live on J5. Connect and disconnect adapters with USB unplugged.
