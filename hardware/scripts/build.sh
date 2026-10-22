#!/bin/sh
# Regenerate the J48 drawings and KiCad schematic from source.
# Needs Python 3 with cairosvg (PDF) and sexpdata (netlist check): pip install cairosvg sexpdata
set -e
cd "$(dirname "$0")"
OUT=../drawings
mkdir -p "$OUT" ../kicad
TMP=$(mktemp -d)
python3 make_revG_svg.py inputs/J48_Schematic_RevF.svg "$TMP/RevG.svg"
python3 make_revH_svg.py "$TMP/RevG.svg" "$TMP/RevH.svg"
python3 make_revI_svg.py "$TMP/RevH.svg" "$OUT/J48_Schematic_RevI.svg"
rm -rf "$TMP"
python3 -c "import cairosvg; cairosvg.svg2pdf(url='$OUT/J48_Schematic_RevI.svg', write_to='$OUT/J48_Schematic_RevI.pdf')"
python3 make_zifmap.py "$OUT/J48_ZIF28_Pin_Map_RevH.svg"
python3 -c "import cairosvg; cairosvg.svg2pdf(url='$OUT/J48_ZIF28_Pin_Map_RevH.svg', write_to='$OUT/J48_ZIF28_Pin_Map_RevH.pdf')"
python3 make_revI_kicad.py ../kicad/J48_RevI.kicad_sch
python3 verify_kicad.py ../kicad/J48_RevI.kicad_sch
rm -f ../kicad/J48_RevI.kicad_sch.intended.json
