#!/bin/sh
# gera os STL (stl/) e os 3MF de toda a Turma esculpida
cd "$(dirname "$0")"
for n in boo gosminha olhinho caveirinha morceguinho; do
  python3 $n.py 0.2 > /dev/null || exit 1
  python3 -c "
import trimesh,os
s=trimesh.Scene()
for c in ['c1','c2','c3','c4']:
    f='stl/${n}_'+c+'.stl'
    if os.path.exists(f): s.add_geometry(trimesh.load(f),node_name='${n}_'+c,geom_name='${n}_'+c)
open('${n}.3mf','wb').write(trimesh.exchange.threemf.export_3MF(s))"
  echo ok $n
done
