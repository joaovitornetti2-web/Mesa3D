#!/usr/bin/env bash
# Gera os relicários (Morte, Sangue, Medo): STL, 3MF de 1 e 2 cores, prévia e checagem.
set -e
cd "$(dirname "$0")"
CHK=../../.claude/skills/mesa3d-print/scripts/check_mesh.py
mkdir -p saida
for e in sangue morte medo; do
  echo "== $e"
  SVG=""
  if [ -f simbolos/$e.png ] && [ ! -f simbolos/$e.svg ]; then python3 -I simbolos/trace_png.py simbolos/$e.png simbolos/$e.svg; fi
  if [ -f simbolos/$e.svg ]; then SVG="simbolos/$e.svg"; echo "  usando símbolo próprio: $SVG"; fi
  for p in corpo tampa selo tampa_simples; do
    openscad -q -o saida/${e}_$p.stl -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D "PARTE=\"$p\"" relicario.scad
  done
  for p in corpo tampa tampa_simples; do
    python3 $CHK saida/${e}_$p.stl | grep -E "Tamanho|Custo|AVISO|ERRO|RESULTADO" | sed "s/^/  $p: /"
  done
  openscad -q -o saida/${e}_corpo.3mf -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D 'PARTE="corpo"' relicario.scad
  openscad -q -o saida/${e}_tampa_simples.3mf -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D 'PARTE="tampa_simples"' relicario.scad
  python3 - "$e" <<'PY'
import sys, trimesh
e = sys.argv[1]
c = trimesh.Scene()
c.add_geometry(trimesh.load(f"saida/{e}_tampa.stl"), node_name=f"{e}_tampa_cor1", geom_name=f"{e}_tampa_cor1")
c.add_geometry(trimesh.load(f"saida/{e}_selo.stl"), node_name=f"{e}_selo_cor2", geom_name=f"{e}_selo_cor2")
c.export(f"saida/{e}_tampa_2cores.3mf")
print("  3mf 2 cores:", len(trimesh.load(f"saida/{e}_tampa_2cores.3mf").geometry), "objetos")
PY
  xvfb-run -a openscad -q -o saida/${e}_preview.png --imgsize=1000,1000 --colorscheme=Tomorrow \
    --camera=0,0,22,58,0,25,250 -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D 'PARTE="preview"' relicario.scad
done
python3 - <<'PY'
from PIL import Image
els = ["sangue", "morte", "medo"]
ims = [Image.open(f"saida/{e}_preview.png") for e in els]
w, h = ims[0].size
W = Image.new("RGB", (w * 3, h), "white")
for i, im in enumerate(ims): W.paste(im, (i * w, 0))
W.save("saida/relicarios_preview.png")
PY
