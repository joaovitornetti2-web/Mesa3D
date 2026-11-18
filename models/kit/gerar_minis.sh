#!/bin/bash
# Gera as 4 miniaturas do kit no Meshy: texto -> 4 vistas -> malha 3D sem textura (STL/GLB).
# Uso: bash models/kit/gerar_minis.sh   (precisa do meshy-cli logado)
cd "$(dirname "$0")/../.." || exit 1
M="npm exec --yes --package=meshy-cli@0.4.0 -- meshy"
OUT=models/kit/meshy
ESTILO="Tabletop RPG miniature figure, 32mm heroic scale, original generic fantasy design, single standing character on a round flat 25mm base, compact confident pose with arms and weapons held close to the body, chunky sturdy proportions, thick weapons, no thin or floating parts, highly detailed sculpt, unpainted grey plastic miniature, plain white background."
declare -A P
P[guerreiro]="A human warrior in plate and chainmail armor with a short cape, holding a broad sword resting against the shoulder and a round shield on the other arm."
P[maga]="A female mage in long flowing layered robes and a hood down, holding a thick gnarled wooden staff with a crystal, a spellbook hanging from the belt."
P[ladino]="A hooded rogue in a leather coat with a scarf over the face, holding two short daggers close to the chest, belt with pouches, crouching slightly ready to strike."
P[clerigo]="A dwarf cleric in heavy armor and a tabard with a sun emblem, holding a big flanged mace and a round holy symbol amulet, long braided beard."
gera() {
  n=$1; mkdir -p $OUT/$n
  $M text-to-image create --prompt "$ESTILO ${P[$n]}" --generate-multi-view true --save-json $OUT/$n/vistas.json > $OUT/$n/vistas.log 2>&1
  i=0; for u in $(grep -o 'https://assets[^"]*' $OUT/$n/vistas.json | grep -v thumbnail); do curl -sS -o $OUT/$n/v$i.png "$u"; i=$((i+1)); done
  imgs=$(ls $OUT/$n/v*.png | head -4 | paste -sd,)
  $M multi-image-to-3d create --image-urls "$imgs" --should-texture false --target-formats glb,stl --timeout 1500 --save-json $OUT/$n/malha.json > $OUT/$n/malha.log 2>&1
  u=$(grep -o 'https://assets[^"]*model\.stl[^"]*' $OUT/$n/malha.json | head -1); curl -sS -o $OUT/$n/$n.stl "$u"
  echo "$n: $(grep -h -o '"consumed_credits": [0-9]*' $OUT/$n/*.json | paste -sd' ') $(ls -la $OUT/$n/$n.stl 2>&1 | awk '{print $5}')"
}
for n in guerreiro maga ladino clerigo; do gera $n & done; wait
