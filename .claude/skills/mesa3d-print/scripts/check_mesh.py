#!/usr/bin/env python3
"""Checa se um STL/3MF/OBJ está pronto para imprimir na impressora do printer-profile.json.

Uso: python3 check_mesh.py arquivo.stl [--perfil caminho.json] [--amostras 3000]
Sai com código 1 se algo bloqueia a impressão (malha aberta, não cabe na mesa).
Paredes finas viram AVISO, não erro: a medição por raios é aproximada.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

PERFIL_PADRAO = Path(__file__).resolve().parent.parent / "printer-profile.json"


def carregar(caminho):
    obj = trimesh.load(caminho, force="mesh")
    if isinstance(obj, trimesh.Scene):
        obj = obj.dump(concatenate=True)
    return obj


def espessura_local(mesh, n):
    """Lança raios para dentro a partir de pontos da superfície; a distância até a
    próxima face é a espessura local naquele ponto."""
    pts, faces = trimesh.sample.sample_surface(mesh, n, seed=0)
    normais = mesh.face_normals[faces]
    origens = pts - normais * 1e-3
    locs, idx_ray, _ = mesh.ray.intersects_location(origens, -normais, multiple_hits=False)
    if len(idx_ray) == 0:
        return np.array([])
    return np.linalg.norm(locs - pts[idx_ray], axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--perfil", default=str(PERFIL_PADRAO))
    ap.add_argument("--amostras", type=int, default=3000)
    a = ap.parse_args()

    perfil = json.loads(Path(a.perfil).read_text())
    imp = perfil["impressora"]
    limite = np.array(imp["volume_mm"]) - 2 * imp["margem_seguranca_mm"]
    parede_min = perfil["parede_minima_mm"]["valor"]

    mesh = carregar(a.arquivo)
    erros, avisos = [], []

    print(f"Arquivo: {a.arquivo}")
    print(f"Triângulos: {len(mesh.faces)}  |  Corpos separados: {mesh.body_count}")

    if not mesh.is_watertight:
        erros.append("Malha ABERTA (tem buracos) – o fatiador pode errar o preenchimento.")
    if not mesh.is_winding_consistent:
        erros.append("Normais inconsistentes (faces viradas do avesso).")
    if mesh.is_watertight and mesh.volume <= 0:
        erros.append("Volume negativo/zero – malha invertida.")

    ext = mesh.extents
    print(f"Tamanho (X×Y×Z mm): {ext[0]:.1f} × {ext[1]:.1f} × {ext[2]:.1f}")
    print(f"Área útil da mesa (com margem): {limite[0]:.0f} × {limite[1]:.0f} × {limite[2]:.0f}")
    a_, b_, c_ = np.sort(ext)
    if np.all(np.sort(ext) <= np.sort(limite)):
        pass
    elif a_ <= limite[2] and (b_ + c_) / np.sqrt(2) <= min(limite[0], limite[1]):
        avisos.append("Só cabe deitada na DIAGONAL da mesa (gire 45° no Bambu Studio).")
    else:
        erros.append("NÃO CABE na mesa nem girando – divida a peça ou reduza a escala.")
    if np.all(np.sort(ext) <= np.sort(limite)) and np.any(ext > limite):
        avisos.append("Não cabe na orientação atual, mas cabe girando no fatiador.")

    if mesh.is_watertight:
        gramas = mesh.volume / 1000 * 1.24
        print(f"Volume: {mesh.volume / 1000:.2f} cm³  (~{gramas:.1f} g de PLA se 100% sólido)")
        rs_g = perfil.get("filamentos", {}).get("custo_por_grama_reais")
        if rs_g:
            print(f"Custo de filamento: até R$ {gramas * rs_g:.2f} (teto, peça maciça; o Bambu Studio dá o peso real)")
        try:
            esp = espessura_local(mesh, a.amostras)
        except ImportError as e:
            esp = np.array([])
            avisos.append(f"Medição de parede pulada (falta biblioteca: {e.name}).")
        if len(esp):
            finas = np.mean(esp < parede_min) * 100
            print(f"Espessura local: mín≈{np.percentile(esp, 1):.2f} mm, mediana {np.median(esp):.2f} mm")
            if finas > 1:
                avisos.append(f"~{finas:.0f}% da superfície tem parede < {parede_min} mm (pode falhar ou sumir no fatiador).")

    for w in avisos:
        print("AVISO:", w)
    for e in erros:
        print("ERRO:", e)
    print("RESULTADO:", "REPROVADO" if erros else ("OK com avisos" if avisos else "OK"))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
