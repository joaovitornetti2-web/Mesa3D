"""confere se alguma peça encosta na borda da grade (foto e impressão): python3 checa.py [col/peça ...]"""
import glob, os, subprocess, sys
RAIZ = os.path.dirname(os.path.abspath(__file__))
COD = r'''
import sys, numpy as np, importlib.util as u
sys.path.insert(0, RAIZ)
sp = u.spec_from_file_location("p", ARQ); m = u.module_from_spec(sp); sp.loader.exec_module(m)
import detalhe
passo = 0.7
if hasattr(m, "MN"):
    caixas = [(m.campo, m.MN, m.MX)]
else:
    caixas = [(m.torre, (-70, -62, 0), (70, 62, 200)), (m.bandeja, (-80, -102, 0), (80, 72, 22))]
for campo, mn, mx in caixas:
    mn = np.array(mn, float); mx = np.array(mx, float); n = np.ceil((mx - mn) / passo).astype(int) + 1
    detalhe._JOB.update(campo=campo, mn=mn, n=n, passo=passo, nx=int(n[0]))
    detalhe._fatia((0, int(n[0]) - 1))
'''
alvos = sys.argv[1:] or sorted(p[:-3] for p in glob.glob("*/*.py"))
for a in alvos:
    arq = os.path.join(RAIZ, a + ".py")
    for imp in ([], ["--imprimir"]):
        src = COD.replace("RAIZ", repr(RAIZ)).replace("ARQ", repr(arq))
        r = subprocess.run([sys.executable, "-c", src, "0.7"] + imp, capture_output=True, text=True, cwd=os.path.dirname(arq))
        avisos = sorted({l.split("em ")[1] for l in r.stdout.splitlines() if l.startswith("AVISO")})
        erro = r.stderr.strip().splitlines()[-1] if r.returncode else ""
        if avisos or erro:
            print(a, "imprimir" if imp else "foto", avisos, erro[:150], flush=True)
print("fim")
