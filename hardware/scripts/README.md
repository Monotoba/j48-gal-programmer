# Drawing and schematic generators

`build.sh` rebuilds everything in `../drawings` and `../kicad`.

| Script | Does |
| --- | --- |
| `make_revG_svg.py` | Applies the Rev G changes to the Rev F drawing (`inputs/J48_Schematic_RevF.svg`) |
| `make_revH_svg.py` | Applies the Rev H changes to the Rev G drawing |
| `make_revH_kicad.py` | Writes the Rev H KiCad schematic from its netlist, with a net label on every pin |
| `verify_kicad.py` | Parses the KiCad file back and checks every net against the intended netlist |

The KiCad schematic connects everything by net label, so parts can be moved freely in KiCad without breaking connections.
