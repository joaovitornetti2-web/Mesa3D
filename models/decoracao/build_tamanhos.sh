#!/usr/bin/env bash
# Versões para 10, 15 e 20 dados (2 camadas de dados, contando os vãos entre eles).
# Conta: cada dado ocupa ~24x24 mm de chão (com vão) e uma camada precisa de ~22 mm de altura.
# Rode antes ./build_relicarios.sh (gera os medalhões base). Saída: <saida>/<N>_dados/
set -e
cd "$(dirname "$0")"
CHK=../../.claude/skills/mesa3d-print/scripts/check_mesh.py
#        N   escala(xy)  altura do corpo no modelo (antes da escala)
TAM=("10 0.92 55.8" "15 1.13 46.9" "20 1.25 43.2")

um() {
  e=$1; n=$2; s=$3; h=$4
  OUT=saida; [ -f simbolos/$e.svg ] && OUT=saida_pessoal
  D=$OUT/${n}_dados; mkdir -p $D
  openscad -q -o $D/_corpo_base.stl -D "ELEMENTO=\"$e\"" -D "H=$h" -D 'PARTE="corpo"' relicario.scad
  openscad -q -o $D/${e}_tampa.stl -D "ELEMENTO=\"$e\"" -D "ESCALA=$s" -D 'PARTE="tampa"' relicario.scad
  python3 - "$D" "$e" "$s" "$OUT" <<'PY'
import sys, trimesh
d, e, s, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
c = trimesh.load(f"{d}/_corpo_base.stl"); c.apply_scale(s); c.export(f"{d}/{e}_corpo.stl"); c.export(f"{d}/{e}_corpo.3mf")
trimesh.load(f"{d}/{e}_tampa.stl").export(f"{d}/{e}_tampa.3mf")
m = trimesh.load(f"{out}/{e}_medalhao.stl"); m.apply_scale(s); m.export(f"{d}/{e}_medalhao.stl")
PY
  rm -f $D/_corpo_base.stl
  {
    echo "== $e – $n dados ($D)"
    for p in corpo tampa medalhao; do python3 $CHK $D/${e}_$p.stl | grep -E "Tamanho|AVISO|ERRO|RESULTADO" | sed "s/^/  $p: /"; done
    python3 dividir_cores.py $D/${e}_medalhao.stl $(python3 -c "print(round(3.4*$s, 3))") $D/${e}_medalhao
  } > /tmp/_tam_${e}_$n.txt 2>&1
}

for t in "${TAM[@]}"; do
  set -- $t
  for e in sangue morte medo; do um $e $1 $2 $3 & done
  wait
done
for t in "${TAM[@]}"; do set -- $t; cat /tmp/_tam_sangue_$1.txt /tmp/_tam_morte_$1.txt /tmp/_tam_medo_$1.txt; done
