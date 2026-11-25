#!/bin/sh
# Gera STL de foto (stl/), STL de impressão (stl_imprimir/, quando a peça tem arrumação própria) e o 3MF de cada peça
# da coleção Masmorra & Dragão. Limite de memória para não derrubar a sessão (a torre usa ~3 GB em 0,6 mm).
cd "$(dirname "$0")"
ulimit -v 10000000
set -e
for p in "mimico 0.3" "prisao 0.3" "corujurso 0.22" "cubo 0.3" "dragaozinho 0.22" "bandeja_escudo 0.3" "barril 0.3" \
         "porta_copos 0.4" "iniciativa 0.22" "porta 0.22" "contador 0.22" "torre_dragao 0.6"; do
  set -- $p
  python3 "$1.py" "$2" > /dev/null
  echo "foto ok $1"
done
for p in "mimico 0.3" "porta_copos 0.4" "iniciativa 0.22" "contador 0.22"; do
  set -- $p
  python3 "$1.py" "$2" --imprimir > /dev/null
  echo "impressão ok $1"
done
python3 - <<'EOF'
import os, sys
sys.path.insert(0, "..")
from base import montar_3mf
aqui = os.path.abspath("x.py")
for n in ["mimico", "prisao", "corujurso", "cubo", "dragaozinho", "bandeja_escudo", "barril", "porta_copos", "iniciativa", "porta", "contador"]:
    print(montar_3mf(aqui, n))
for n in ["torre_dragao-torre", "torre_dragao-bandeja"]:   # torre e bandeja em arquivos separados
    print(montar_3mf(aqui, n, imprimir=False))
EOF
