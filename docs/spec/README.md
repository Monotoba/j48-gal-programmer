# Programming specification

One file per device family, written before the firmware that implements it. Each file covers:

- pin roles in programming mode (see `../pin-map/` for the ZIF-28 positions)
- fuse-map layout and JEDEC fuse numbering
- programming, verify, erase and security sequences, with timing and voltages
- sources, cited for every fact

Planned files: `16v8.md`, `18v10.md`, `20v8.md`, `22v10.md`, `20xv10.md`, `750.md`, `600x.md`, `26cv12.md`, `atf150x-jtag.md`.
