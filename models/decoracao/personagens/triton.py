#!/usr/bin/env python3
"""Arte do personagem -> 3 níveis (preto/vermelho/branco) para placa em relevo de 3 cores.
Gera <nome>_niveis.png (0,1,2) no tamanho final da placa, já com detalhes mínimos imprimíveis."""
import sys, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
from pathlib import Path

ORIG = Path(__file__).resolve().parent.parent / "simbolos" / "originais" / "personagens"
PX_MM = 0.15                 # resolução da placa (mm por pixel)
LARG_MM, ALT_MM = 34.8, 59.2 # placa = arco da parede de 50 dados menos 0.2 mm de folga
MIN_MM = 0.5                 # menor detalhe que o bico 0.4 imprime

# recorte (frações da imagem: x0, y0, x1, y1) e fundo a remover
CONF = {
    # retratos da cintura para cima: lêem muito melhor numa placa de 33x57 mm
    "rubens":    {"crop": (0.20, 0.02, 0.84, 1.00), "fundo": "azul"},
    "balu":      {"crop": (0.33, 0.02, 0.72, 0.62), "fundo": "escuro"},
    "labirinto": {"crop": (0.20, 0.00, 0.80, 0.86), "fundo": None},
    "guizo":     {"crop": (0.15, 0.00, 0.85, 0.42), "fundo": "claro"},
    "chico":     {"crop": (0.15, 0.00, 0.85, 0.62), "fundo": "escuro"},
}


def processa(nome):
    c = CONF[nome]
    im = Image.open(next(ORIG.glob(nome + ".*"))).convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = c["crop"]
    im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    W, H = int(LARG_MM / PX_MM), int(ALT_MM / PX_MM)
    # encaixa sem distorcer (preenche e corta o excesso)
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((l, t, l + W, t + H))
    rgb = np.asarray(im).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    L = np.asarray(im.convert("L").filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.7))).astype(float)
    L_bruto = L.copy()   # para separar o fundo
    # contraste local (CLAHE): rosto escuro ao lado de roupa clara não some
    from skimage import exposure
    L = exposure.equalize_adapthist(L / 255.0, kernel_size=max(8, L.shape[1] // 4), clip_limit=0.012) * 255
    fundo = np.zeros(L.shape, bool)
    if c["fundo"] == "azul":
        fundo = (hsv[..., 0] > 135) & (hsv[..., 0] < 185) & (hsv[..., 1] > 70)
    elif c["fundo"] == "escuro":
        fundo = L_bruto < 38
    elif c["fundo"] == "claro":
        fundo = L_bruto > 240
    fundo = ndi.binary_opening(fundo, iterations=2)
    # só o fundo ligado à borda
    lab, n = ndi.label(fundo)
    borda = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(borda))
    fig = ~fundo
    t1, t2 = np.percentile(L[fig], [38, 78]) if fig.any() else (85, 170)
    niv = np.where(L < t1, 0, np.where(L < t2, 1, 2)).astype(np.uint8)
    # contornos de quadrinho: linhas escuras viram preto
    linhas = (L < ndi.uniform_filter(L, 7) - 22)
    niv[linhas] = 0
    niv[fundo] = 0
    # contorno vermelho em volta da silhueta (roupa escura não some no fundo escuro)
    if c["fundo"]:
        aro = ndi.binary_dilation(fig, iterations=4) & ~ndi.binary_erosion(fig, iterations=0 or 1) & fundo
        niv[aro] = 1
    # detalhes mínimos imprimíveis: tira ilhas/furos menores que MIN_MM
    r = max(1, round(MIN_MM / 2 / PX_MM))
    for k in (2, 1):
        m = niv >= k
        m = ndi.binary_opening(m, iterations=r)
        m = ndi.binary_closing(m, iterations=1)
        lab, n = ndi.label(m)
        if n:
            a = ndi.sum(m, lab, range(1, n + 1))
            m = np.isin(lab, [i + 1 for i, x in enumerate(a) if x * PX_MM ** 2 >= MIN_MM ** 2 * 2])
        niv = np.where(m, np.maximum(niv, k), np.minimum(niv, k - 1)).astype(np.uint8)
    Image.fromarray(niv).save(f"{nome}_niveis.png")
    cores = np.array([[21, 21, 21], [192, 20, 28], [240, 240, 240]], np.uint8)
    Image.fromarray(cores[niv]).resize((W * 2, H * 2), Image.NEAREST).save(f"{nome}_preview.png")
    return nome


if __name__ == "__main__":
    for n in (sys.argv[1:] or CONF):
        print(processa(n))
