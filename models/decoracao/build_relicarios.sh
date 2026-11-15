#!/usr/bin/env bash
# Gera os relicários (Morte, Sangue, Medo): STL, 3MF de 1 e 2 cores, prévia e checagem.
set -e
cd "$(dirname "$0")"
CHK=../../.claude/skills/mesa3d-print/scripts/check_mesh.py
mkdir -p saida saida_pessoal
USOU_SIMBOLO=0
for e in sangue morte medo; do
  echo "== $e"
  SVG=""; CEN="[0,0]"; ESC=1; OUT=saida
  if [ "$e" = medo ] && [ -f simbolos/medo_vetor.scad ]; then openscad -q -o simbolos/medo.svg simbolos/medo_vetor.scad; fi
  if [ -f simbolos/$e.png ] && [ ! -f simbolos/$e.svg ]; then python3 -I simbolos/trace_png.py simbolos/$e.png simbolos/$e.svg; fi
  if [ -f simbolos/$e.svg ]; then
    SVG="$PWD/simbolos/$e.svg"
    echo "linear_extrude(1) import(\"$SVG\");" > /tmp/_sv.scad && openscad -q -o /tmp/_sv.stl /tmp/_sv.scad
    read CEN ESC < <(python3 -c "
import trimesh, numpy as np
m = trimesh.load('/tmp/_sv.stl'); c = m.bounds[:, :2].mean(0)
r = np.sqrt(((m.vertices[:, :2] - c) ** 2).sum(1)).max()
print(f'[{c[0]:.4f},{c[1]:.4f}]', f'{19.5 / r:.6f}')")
    OUT=saida_pessoal; USOU_SIMBOLO=1
    echo "  usando símbolo próprio: $SVG (escala $ESC) -> $OUT/ (fora do git)"
  fi
  for p in corpo tampa selo tampa_simples; do
    openscad -q -o $OUT/${e}_$p.stl -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D "SIMBOLO_CENTRO=$CEN" -D "SIMBOLO_ESCALA=$ESC" -D "PARTE=\"$p\"" relicario.scad
  done
  for p in corpo tampa tampa_simples; do
    python3 $CHK $OUT/${e}_$p.stl | grep -E "Tamanho|Custo|AVISO|ERRO|RESULTADO" | sed "s/^/  $p: /"
  done
  openscad -q -o $OUT/${e}_corpo.3mf -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D "SIMBOLO_CENTRO=$CEN" -D "SIMBOLO_ESCALA=$ESC" -D 'PARTE="corpo"' relicario.scad
  openscad -q -o $OUT/${e}_tampa_simples.3mf -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D "SIMBOLO_CENTRO=$CEN" -D "SIMBOLO_ESCALA=$ESC" -D 'PARTE="tampa_simples"' relicario.scad
  python3 - "$e" "$OUT" <<'PY'
import sys, trimesh
e, out = sys.argv[1], sys.argv[2]
c = trimesh.Scene()
c.add_geometry(trimesh.load(f"{out}/{e}_tampa.stl"), node_name=f"{e}_tampa_cor1", geom_name=f"{e}_tampa_cor1")
c.add_geometry(trimesh.load(f"{out}/{e}_selo.stl"), node_name=f"{e}_selo_cor2", geom_name=f"{e}_selo_cor2")
c.export(f"{out}/{e}_tampa_2cores.3mf")
print("  3mf 2 cores:", len(trimesh.load(f"{out}/{e}_tampa_2cores.3mf").geometry), "objetos")
PY
  xvfb-run -a openscad -q -o $OUT/${e}_preview.png --imgsize=1000,1000 --colorscheme=Tomorrow \
    --camera=0,0,22,58,0,25,250 -D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D "SIMBOLO_CENTRO=$CEN" -D "SIMBOLO_ESCALA=$ESC" -D 'PARTE="preview"' relicario.scad
done
python3 - <<'PY'
from PIL import Image
els = ["sangue", "morte", "medo"]
import os
for out in ["saida", "saida_pessoal"]:
    feitos = [e for e in els if os.path.exists(f"{out}/{e}_preview.png")]
    if not feitos: continue
    ims = [Image.open(f"{out}/{e}_preview.png") for e in feitos]
    w, h = ims[0].size
    W = Image.new("RGB", (w * len(ims), h), "white")
    for i, im in enumerate(ims): W.paste(im, (i * w, 0))
    W.save(f"{out}/relicarios_preview.png")
    for e in feitos: os.remove(f"{out}/{e}_preview.png")
PY
