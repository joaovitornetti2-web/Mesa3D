#!/usr/bin/env bash
# Gera todas as caixas de dados: STL de cada parte, 3MF de duas cores, prévias e checagem.
set -e
cd "$(dirname "$0")"
CHK=../../.claude/skills/mesa3d-print/scripts/check_mesh.py
mkdir -p saida
openscad -q -o saida/caixa.stl -D 'PARTE="caixa"' -D 'DECOR=true' caixa_elementos.scad
openscad -q -o saida/caixa.3mf -D 'PARTE="caixa"' -D 'DECOR=true' caixa_elementos.scad
python3 $CHK saida/caixa.stl | grep -E "Tamanho|Custo|AVISO|ERRO|RESULTADO"
for e in sangue morte conhecimento energia medo; do
  echo "== $e"
  for p in tampa emblema tampa_simples; do
    openscad -q -o saida/${e}_$p.stl -D "ELEMENTO=\"$e\"" -D "PARTE=\"$p\"" -D "NOME=false" -D "DECOR=true" caixa_elementos.scad
  done
  openscad -q -o saida/${e}_tampa_simples.3mf -D "ELEMENTO=\"$e\"" -D 'PARTE="tampa_simples"' -D "NOME=false" -D "DECOR=true" caixa_elementos.scad
  python3 $CHK saida/${e}_tampa.stl | grep -E "AVISO|ERRO|RESULTADO" | sed 's/^/  tampa: /'
  python3 $CHK saida/${e}_tampa_simples.stl | grep -E "AVISO|ERRO|RESULTADO" | sed 's/^/  simples: /'
  python3 - "$e" <<'PY'
import sys, trimesh
e = sys.argv[1]
cena = trimesh.Scene()
cena.add_geometry(trimesh.load(f"saida/{e}_tampa.stl"), node_name=f"{e}_tampa_cor1", geom_name=f"{e}_tampa_cor1")
cena.add_geometry(trimesh.load(f"saida/{e}_emblema.stl"), node_name=f"{e}_emblema_cor2", geom_name=f"{e}_emblema_cor2")
cena.export(f"saida/{e}_tampa_2cores.3mf")
volta = trimesh.load(f"saida/{e}_tampa_2cores.3mf")
print(f"  3mf 2 cores: {len(volta.geometry)} objetos")
PY
done
python3 - <<'PY'
import subprocess
from PIL import Image
els = ["sangue", "morte", "conhecimento", "energia", "medo"]
for e in els:
    subprocess.run(["xvfb-run", "-a", "openscad", "-q", "-o", f"saida/{e}_preview.png", "--imgsize=900,700",
                    "--colorscheme=Tomorrow", "--camera=44,29,14,55,0,20,250",
                    "-D", f'ELEMENTO="{e}"', "-D", 'PARTE="preview"', "caixa_elementos.scad"], check=True)
ims = [Image.open(f"saida/{e}_preview.png") for e in els]
w, h = ims[0].size
W = Image.new("RGB", (w * 3, h * 2), "white")
for i, im in enumerate(ims):
    W.paste(im, ((i % 3) * w, (i // 3) * h))
W.save("saida/todas_preview.png")
for e in els:
    __import__("os").remove(f"saida/{e}_preview.png")
PY
