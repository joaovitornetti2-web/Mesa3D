#!/usr/bin/env bash
# Gera os relicários (Sangue, Morte, Medo) em paralelo: corpo, tampa, medalhão (1 e 2 cores) e checagem.
# Com simbolos/<elemento>.svg|png presente, usa o símbolo próprio e grava em saida_pessoal/ (fora do git).
set -e
cd "$(dirname "$0")"
CHK=../../.claude/skills/mesa3d-print/scripts/check_mesh.py
Z_COR=3.4   # = ASSENTO + 1.4 em relicario.scad
mkdir -p saida saida_pessoal
python3 -I gerar_texturas.py >/dev/null
[ -f simbolos/medo_vetor.scad ] && openscad -q -o simbolos/medo.svg simbolos/medo_vetor.scad

um_elemento() {
  e=$1; SVG=""; CEN="[0,0]"; ESC=1; OUT=saida
  if [ -f simbolos/$e.png ] && [ ! -f simbolos/$e.svg ]; then python3 -I simbolos/trace_png.py simbolos/$e.png simbolos/$e.svg >/dev/null; fi
  if [ -f simbolos/$e.svg ]; then
    SVG="$PWD/simbolos/$e.svg"; OUT=saida_pessoal
    echo "linear_extrude(1) import(\"$SVG\");" > /tmp/_sv_$e.scad && openscad -q -o /tmp/_sv_$e.stl /tmp/_sv_$e.scad
    read CEN ESC < <(python3 -c "
import trimesh, numpy as np
m = trimesh.load('/tmp/_sv_$e.stl'); c = m.bounds[:, :2].mean(0)
r = np.sqrt(((m.vertices[:, :2] - c) ** 2).sum(1)).max()
print(f'[{c[0]:.4f},{c[1]:.4f}]', f'{19.5 / r:.6f}')")
  fi
  D=(-D "ELEMENTO=\"$e\"" -D "SIMBOLO_SVG=\"$SVG\"" -D "SIMBOLO_CENTRO=$CEN" -D "SIMBOLO_ESCALA=$ESC")
  for p in corpo tampa medalhao; do
    openscad -q -o $OUT/${e}_$p.stl "${D[@]}" -D "PARTE=\"$p\"" relicario.scad
  done
  {
    echo "== $e  ($OUT/)"
    for p in corpo tampa medalhao; do
      python3 $CHK $OUT/${e}_$p.stl | grep -E "Tamanho|Custo|AVISO|ERRO|RESULTADO" | sed "s/^/  $p: /"
    done
    python3 -c "
import trimesh
for p in ['corpo', 'tampa']: trimesh.load('$OUT/${e}_' + p + '.stl').export('$OUT/${e}_' + p + '.3mf')"
    python3 dividir_cores.py $OUT/${e}_medalhao.stl $Z_COR $OUT/${e}_medalhao
  } > /tmp/_log_$e.txt 2>&1
}

for e in sangue morte medo; do um_elemento $e & done
wait
cat /tmp/_log_sangue.txt /tmp/_log_morte.txt /tmp/_log_medo.txt
