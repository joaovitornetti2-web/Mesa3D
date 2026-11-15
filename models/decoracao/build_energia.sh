#!/usr/bin/env bash
# Relicário da Energia para ~50 dados (3 camadas de ~18, contando os vãos), medalhão em 3 cores.
set -e
cd "$(dirname "$0")"
CHK=../../.claude/skills/mesa3d-print/scripts/check_mesh.py
S=1.6        # escala xy: cavidade 112 mm
HU=51.75     # altura do corpo no modelo -> 82.8 mm reais, 70 mm úteis
python3 -I gerar_texturas.py >/dev/null
SVG=""; CEN="[0,0]"; ESC=1; OUT=saida/50_dados_energia
if [ -f simbolos/energia_vetor.scad ]; then
  openscad -q -o simbolos/energia.svg simbolos/energia_vetor.scad
  SVG="$PWD/simbolos/energia.svg"; OUT=saida_pessoal/50_dados_energia
  echo "linear_extrude(1) import(\"$SVG\");" > /tmp/_sv_en.scad && openscad -q -o /tmp/_sv_en.stl /tmp/_sv_en.scad
  read CEN ESC < <(python3 -c "
import trimesh, numpy as np
m = trimesh.load('/tmp/_sv_en.stl'); c = m.bounds[:, :2].mean(0)
r = np.sqrt(((m.vertices[:, :2] - c) ** 2).sum(1)).max()
print(f'[{c[0]:.4f},{c[1]:.4f}]', f'{19.5 / r:.6f}')")
fi
mkdir -p $OUT
D=(-D 'ELEMENTO="energia"' -D "SIMBOLO_SVG=\"$SVG\"" -D "SIMBOLO_CENTRO=$CEN" -D "SIMBOLO_ESCALA=$ESC")
openscad -q -o $OUT/_corpo.stl "${D[@]}" -D "H=$HU" -D 'PARTE="corpo"' relicario.scad &
openscad -q -o $OUT/energia_tampa.stl "${D[@]}" -D "ESCALA=$S" -D 'PARTE="tampa"' relicario.scad &
openscad -q -o $OUT/_medalhao.stl "${D[@]}" -D 'PARTE="medalhao"' relicario.scad &
wait
python3 - "$OUT" "$S" <<'PY'
import sys, trimesh
d, s = sys.argv[1], float(sys.argv[2])
for a, b in [("_corpo", "energia_corpo"), ("_medalhao", "energia_medalhao")]:
    m = trimesh.load(f"{d}/{a}.stl"); m.apply_scale(s); m.export(f"{d}/{b}.stl")
trimesh.load(f"{d}/energia_corpo.stl").export(f"{d}/energia_corpo.3mf")
trimesh.load(f"{d}/energia_tampa.stl").export(f"{d}/energia_tampa.3mf")
PY
rm -f $OUT/_corpo.stl $OUT/_medalhao.stl
echo "== energia – 50 dados ($OUT)"
for p in corpo tampa medalhao; do python3 $CHK $OUT/energia_$p.stl | grep -E "Tamanho|Custo|AVISO|ERRO|RESULTADO" | sed "s/^/  $p: /"; done
python3 dividir_cores.py $OUT/energia_medalhao.stl "$(python3 -c "print(round(3.4*$S,3))"),$(python3 -c "print(round(4.2*$S,3))")" $OUT/energia_medalhao
