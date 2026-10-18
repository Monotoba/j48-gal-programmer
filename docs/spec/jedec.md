# JEDEC fuse files

Wingman reads and writes JEDEC fuse files (`.jed`), the standard format for programmable-logic fuse maps. This page covers only what Wingman needs; device fuse layouts are in each device's spec.

Sources: [S1] Data I/O, "JEDEC Standard Number 3A" implementation notes, https://download.dataio.com/appnotes/jedec2.txt · [S2] GALer documentation, "JEDEC File", https://k1.spdns.de/Develop/Projects/GalAsm/info/galer/jedecfile.html

## File structure

- ASCII text. Anything before the first `*` is a free-form header. [S2]
- The file is framed by `STX` (0x02) and `ETX` (0x03). A 4-digit hex transmission checksum follows `ETX`. [S1][S2]
- Each field starts with an identifying character and ends with `*`. [S2]

## Fields Wingman uses

| Field | Meaning | Source |
| --- | --- | --- |
| `QF<n>` | Number of fuses in the device. Must come before any `L` field. Sets how many fuses the checksum covers. | [S1] |
| `F0` / `F1` | Default state of fuses not listed in `L` fields. Comes after `QF`, before the first `L`. | [S1] |
| `L<addr> <bits>` | Fuse list: a decimal starting fuse number, then one `0`/`1` per consecutive fuse. A fuse given more than once takes its last value. | [S1][S2] |
| `C<hex>` | 16-bit fuse checksum (see below). If several are present, the last one counts. | [S1] |
| `G0` / `G1` | Security fuse: `G1` means program the security fuse after programming. | [S1][S2] |
| `N…` | Note or comment; may appear anywhere; ignored. | [S1] |
| `QP`, `V` | Pin count and test vectors. Not needed for programming. | [S1] |

## Fuse checksum (`C` field)

1. Group the fuses into 8-bit words: word 0 = fuses 0–7, word 1 = fuses 8–15, and so on. [S1]
2. In each word, the lowest-numbered fuse is the least significant bit. [S1]
3. Cover every fuse from 0 to `QF − 1`, including fuses not listed in `L` fields (they take the `F` default). [S1]
4. If the last word is partial, the unused high bits are 0. [S1]
5. Sum the words into a 16-bit value. [S1]

## Transmission checksum (after `ETX`)

The 16-bit sum of every character from `STX` through `ETX` inclusive, with the parity bit excluded. A value of `0000` is a dummy and should be accepted. [S1]

## Open questions

- [ ] [S1] describes the 16-bit sums as "modulo 65,535". Confirm against a known-good file whether this means wrap-around at 65,536 (ordinary 16-bit overflow), which is what its worked example implies.
