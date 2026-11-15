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
    "joui":      {"crop": (0.45, 0.04, 0.78, 0.58), "fundo": "saturado"},
    "dante":     {"crop": (0.00, 0.00, 1.00, 1.00), "fundo": None},
    "pantheon":  {"crop": (0.36, 0.00, 0.70, 0.80), "fundo": "verde"},
    # medalhão redondo da tampa (Plautus sobre a pilha de corpos)
    "plautus":   {"crop": (0.12, 0.00, 0.95, 0.97), "fundo": None, "circulo": 66.6, "encaixar": True, "pct": [55, 86]},
}


def processa(nome):
    c = CONF[nome]
    im = Image.open(next(ORIG.glob(nome + ".*"))).convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = c["crop"]
    im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    if c.get("circulo"):
        W = H = int(c["circulo"] / PX_MM)
    else:
        W, H = int(LARG_MM / PX_MM), int(ALT_MM / PX_MM)
    # encaixa sem distorcer (preenche e corta o excesso)
    if c.get("encaixar"):   # cabe inteira (círculo: usa ~92% do diâmetro), sobra vira fundo preto
        s = min(W / im.width, H / im.height) * 0.98
        im2 = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        fundo_img = Image.new("RGB", (W, H), (0, 0, 0))
        ox, oy = (W - im2.width) // 2, (H - im2.height) // 2
        fundo_img.paste(im2, (ox, oy))
        im = fundo_img
        faixa = np.ones((H, W), bool); faixa[oy:oy + im2.height, ox:ox + im2.width] = False
    else:
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
    if c.get("encaixar"):
        fundo |= faixa
    if c["fundo"] == "azul":
        fundo = (hsv[..., 0] > 135) & (hsv[..., 0] < 185) & (hsv[..., 1] > 70)
    elif c["fundo"] == "escuro":
        fundo = L_bruto < (30 if c.get("sangue") else 38)
    elif c["fundo"] == "saturado":   # brilho vermelho/rosa saturado atrás do personagem
        fundo = (hsv[..., 1] > 120) & (L_bruto > 70) & ((hsv[..., 0] < 20) | (hsv[..., 0] > 215))
    elif c["fundo"] == "verde":      # céu/chuva verde-acinzentado
        fundo = (hsv[..., 0] > 60) & (hsv[..., 0] < 150) & (hsv[..., 2] < 140)
    elif c["fundo"] == "claro":
        fundo = L_bruto > 240
    fundo = ndi.binary_opening(fundo, iterations=2) | (faixa if c.get("encaixar") else False)
    # só o fundo ligado à borda
    lab, n = ndi.label(fundo)
    borda = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(borda))
    fig = ~fundo
    t1, t2 = np.percentile(L[fig], c.get("pct", [38, 78])) if fig.any() else (85, 170)
    niv = np.where(L < t1, 0, np.where(L < t2, 1, 2)).astype(np.uint8)
    # contornos de quadrinho: linhas escuras viram preto
    linhas = (L < ndi.uniform_filter(L, 7) - 22)
    niv[linhas] = 0
    niv[fundo] = 0
    if c.get("sangue"):   # sangue sempre vermelho
        sangue = ((hsv[..., 0] < 14) | (hsv[..., 0] > 240)) & (hsv[..., 1] > 110) & (L_bruto > 25)
        niv[ndi.binary_opening(sangue, iterations=1)] = 1
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
    if c.get("circulo"):
        yy, xx = np.mgrid[:H, :W]
        niv[(xx - W / 2) ** 2 + (yy - H / 2) ** 2 > (W / 2) ** 2] = 0
    Image.fromarray(niv).save(f"{nome}_niveis.png")
    cores = np.array([[21, 21, 21], [192, 20, 28], [240, 240, 240]], np.uint8)
    Image.fromarray(cores[niv]).resize((W * 2, H * 2), Image.NEAREST).save(f"{nome}_preview.png")
    return nome


if __name__ == "__main__":
    for n in (sys.argv[1:] or CONF):
        print(processa(n))
