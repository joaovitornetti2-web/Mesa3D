#!/usr/bin/env bash
# Gera STL + PNG de prévia de um .scad e roda a checagem de malha.
# Uso: preview.sh caminho/modelo.scad [3mf]
set -e
scad="$1"; base="${scad%.scad}"; dir="$(cd "$(dirname "$0")" && pwd)"
openscad -o "$base.stl" "$scad"
[ "$2" = "3mf" ] && openscad -o "$base.3mf" "$scad"
xvfb-run -a openscad -o "$base.png" --imgsize=900,650 --viewall --autocenter \
  --colorscheme=Tomorrow --camera=0,0,0,55,0,25,0 "$scad"
python3 "$dir/check_mesh.py" "$base.stl"
