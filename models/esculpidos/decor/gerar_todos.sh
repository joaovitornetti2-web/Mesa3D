#!/bin/sh
# gera STL (stl/ = arrumação da foto) e 3MF de impressão de toda a decoração esculpida
cd "$(dirname "$0")"
python3 monstrinho.py 0.33 && python3 gatinho.py 0.33 && python3 lanterna.py 0.4 && python3 porta_chaves.py 0.3 \
  && python3 vaso.py 0.4 && python3 porta_copos.py 0.4 && python3 porta_copos.py 0.4 --imprimir || exit 1
for n in monstrinho gatinho lanterna porta_chaves vaso porta_copos; do
  d=stl; [ $n = porta_copos ] && d=stl_imprimir
  python3 -c "
import trimesh,os
s=trimesh.Scene()
for c in ['c1','c2','c3','c4']:
    f='$d/${n}_'+c+'.stl'
    if os.path.exists(f): s.add_geometry(trimesh.load(f),node_name='${n}_'+c,geom_name='${n}_'+c)
open('${n}.3mf','wb').write(trimesh.exchange.threemf.export_3MF(s))"
  echo ok $n
done
