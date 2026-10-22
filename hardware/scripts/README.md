# Drawing and schematic generators

`build.sh` rebuilds everything in `../drawings` and `../kicad`.

| Script | Does |
| --- | --- |
| `make_revG_svg.py` | Applies the Rev G changes to the Rev F drawing (`inputs/J48_Schematic_RevF.svg`) |
| `make_revH_svg.py` | Applies the Rev H changes to the Rev G drawing |
| `make_revI_svg.py` | Applies the Rev I changes (J5 expansion header) to the Rev H drawing |
| `make_zifmap.py` | Draws the ZIF-28 pin map: each device overlaid on the socket, plus a role table for every ZIF pin |
| `make_revI_kicad.py` | Writes the Rev I KiCad schematic from its netlist, with a net label on every pin |
| `verify_kicad.py` | Parses the KiCad file back and checks every net against the intended netlist |

The KiCad schematic connects everything by net label, so parts can be moved freely in KiCad without breaking connections.
