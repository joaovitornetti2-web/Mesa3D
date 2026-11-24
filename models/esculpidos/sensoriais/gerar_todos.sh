#!/bin/sh
# gera STL (stl/) e 3MF de todos os brinquedos sensoriais esculpidos
cd "$(dirname "$0")"
M=../../sensoriais
for p in par impar; do openscad -q -o stl/serpente_mec_$p.stl -D "PARTE=\"s_serpente_$p\"" -D 'DECOR=false' $M/sensoriais.scad; done
for t in 17 19 21; do openscad -q -o stl/anel_mec_$t.stl -D 'PARTE="s_anel"' -D 'DECOR=false' -D "ARO=$t" $M/sensoriais.scad; done
python3 dado.py 0.12 && python3 pedra.py 0.15 && python3 piao.py 0.15 && python3 chaveiro.py 0.1 && python3 spinner.py 0.15 \
  && python3 cone.py 0.12 && python3 serpente.py 0.18 && python3 anel.py 0.07 17 && python3 anel.py 0.07 19 && python3 anel.py 0.07 21 || exit 1
python3 - <<'PY'
import trimesh, os
def tmf(nome, arquivos):
    s = trimesh.Scene()
    for rotulo, f in arquivos:
        if os.path.exists(f): s.add_geometry(trimesh.load(f), node_name=rotulo, geom_name=rotulo)
    open(nome, "wb").write(trimesh.exchange.threemf.export_3MF(s)); print(nome, round(os.path.getsize(nome) / 1e6, 1), "MB")
cores = lambda n, cs: [(f"{n}_{c}", f"stl/{n}_{c}.stl") for c in cs]
tmf("dado_sensorial.3mf", cores("dado", ["c1", "c2"]))
tmf("pedrinha_sonolenta.3mf", cores("pedra", ["c1", "c2", "c3", "c4"]))
tmf("piao_abobora.3mf", cores("piao", ["c1", "c2", "c4"]))
tmf("chaveiro_d20.3mf", cores("chaveiro", ["c1", "c2", "c3", "c4"]))
tmf("spinner_gatinhos.3mf", cores("spinner", ["c1", "c2"]) + [("spinner_bochechas", "stl/spinner_c4.stl")])
tmf("spinner_tampinha.3mf", [("tampinha (imprimir 2)", "stl/spinner_tampa.stl")])
tmf("chapeu_espiral.3mf", [("chapeu", "stl/cone_c1.stl")])
tmf("serpente_sibila.3mf", cores("serpente", ["c1", "c2", "c3", "c4"]))
for t, suf in ((17, "_17"), (19, ""), (21, "_21")):
    tmf(f"anel_{ {17: 'P', 19: 'M', 21: 'G'}[t] }_{t}mm.3mf".replace(" ", ""), [("aro", f"stl/anel{suf}_c1.stl"), ("faixa", f"stl/anel{suf}_c2.stl")])
PY
