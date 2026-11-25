"""Monta os vídeos verticais de gancho (Reels / TikTok / Shorts) a partir dos giros renderizados.
Uso: python3 videos/montar.py [nome ...]    (precisa de ffmpeg; rode antes videos/giros.py)
Saída: videos/<nome>.mp4 (1080x1920, 30 fps, ~10 s, sem áudio: coloque o áudio do momento no app)
       videos/<nome>_capa.jpg (capa) e site/vid/<nome>.mp4 (laço curto sem texto para o site)."""
import glob, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = os.path.join(R, "videos", ".quadros")
FONTE = os.path.join(R, "models", "decor", "fontes", "Fredoka.ttf")
W, H, FPS, DUR = 1080, 1920, 30, 10.0
TINTA, CREME, AMARELO, PAPEL = (33, 23, 46), (255, 246, 232), (255, 207, 63), (251, 247, 240)
SITE = "ateliedomestre.vercel.app"

VIDEOS = {
    "boo": dict(gancho=["POV: seu fantasma", "tentou virar mago"], pontos=["Chapéu torto e d20 da sorte", "Língua de fora, claro", "4 cores direto da impressora"],
                nome="Boo, o fantasminha", preco="R$ 39,90"),
    "monstrinho": dict(gancho=["Ele come canetas.", "Sério."], pontos=["A boca é o porta-trecos", "Dentões e um olho desconfiado", "Cabe caneta, pincel e dado"],
                       nome="Monstrinho Porta-Trecos", preco="R$ 69,90"),
    "gatinho": dict(gancho=["Seu celular precisa", "de um gatinho"], pontos=["O celular encaixa nas costas", "O rostinho fica à mostra", "Tem canal pro carregador"],
                    nome="Gatinho Suporte de Celular", preco="R$ 59,90"),
    "porta_chaves": dict(gancho=["Onde fica a chave?", "Na boca do mímico."], pontos=["As chaves penduram nos dentes", "Baú com madeira e rebites", "2 parafusos e pronto"],
                         nome="Porta-Chaves Mímico", preco="R$ 59,90"),
    "cores": dict(gancho=["Escolhe a cor", "que eu imprimo"], pontos=["Preto, branco ou vermelho", "Laranja ou rosa", "Até 4 cores na mesma peça"],
                  nome="A Turma do Ateliê", preco="a partir de R$ 29,90",
                  fotos=[f"turma_{b}_{c}.webp" for b in ("fantasminha", "gosminha", "morceguinho", "caveirinha", "olhinho")
                         for c in ("branco", "rosa", "laranja", "preto", "vermelho")], troca=0.4),
    "dado": dict(gancho=["Mão inquieta?", "6 texturas pra ela"], pontos=["Escamas, bolhas e ondas", "Espiral pra seguir com o dedo", "32 mm: cabe no bolso"],
                 nome="Dado Sensorial", preco="R$ 19,90"),
}


def fonte(tam, peso="Bold"):
    f = ImageFont.truetype(FONTE, tam)
    f.set_variation_by_name(peso)
    return f


def suave(t):  # 0..1 com saída macia
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def pulo(t):  # entra passando um pouquinho do tamanho e volta
    t = max(0.0, min(1.0, t))
    return 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2 if t < 1 else 1.0


def etiqueta(linhas, tam, fundo, cor, borda=TINTA, pad=(34, 18), raio=26, inclina=0):
    """bloco de texto com fundo arredondado, borda de tinta e sombra de brinquedo (como os botões do site)."""
    f = fonte(tam)
    larg = max(f.getbbox(l)[2] for l in linhas)
    alt_l = int(tam * 1.12)
    w, h = larg + 2 * pad[0], alt_l * len(linhas) + 2 * pad[1]
    im = Image.new("RGBA", (w + 8, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 10, w + 4, h + 10), raio, fill=borda)                      # sombra
    d.rounded_rectangle((4, 2, w + 4, h + 2), raio, fill=fundo, outline=borda, width=5)
    for i, l in enumerate(linhas):
        lw = f.getbbox(l)[2]
        d.text((4 + (w - lw) / 2, 2 + pad[1] + i * alt_l - tam * 0.12), l, font=f, fill=cor)
    return im.rotate(inclina, resample=Image.BICUBIC, expand=True) if inclina else im


def colar(base, im, cx, cy, escala=1.0, alfa=1.0):
    if escala <= 0.01 or alfa <= 0.01:
        return
    if escala != 1.0:
        im = im.resize((max(1, int(im.width * escala)), max(1, int(im.height * escala))), Image.BICUBIC)
    if alfa < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alfa))
        im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def logo(tam):
    s = tam / 64
    im = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hexa = [(32 * s, 4 * s), (56 * s, 18 * s), (56 * s, 46 * s), (32 * s, 60 * s), (8 * s, 46 * s), (8 * s, 18 * s)]
    d.polygon(hexa, fill=CREME)
    mask = Image.new("L", (tam, tam), 0); ImageDraw.Draw(mask).polygon(hexa, fill=255)
    faixas = Image.new("RGBA", (tam, tam), (0, 0, 0, 0)); df = ImageDraw.Draw(faixas)
    for i in range(5):
        df.rectangle((0, (10 + i * 11) * s, tam, (14 + i * 11) * s), fill=AMARELO)
    im.paste(faixas, (0, 0), Image.composite(faixas.getchannel("A"), Image.new("L", (tam, tam), 0), mask))
    d.polygon([(32 * s, 17 * s), (45 * s, 41 * s), (19 * s, 41 * s)], fill=TINTA)
    return im


def montar(nome):
    cfg = VIDEOS[nome]
    quadros = sorted(glob.glob(os.path.join(Q, nome, "*.png")))
    if cfg.get("fotos"):
        quadros = [os.path.join(R, "site", "img", f) for f in cfg["fotos"]]
    if not quadros:
        print("sem quadros:", nome); return
    n = len(quadros)
    cache = {}
    def fundo(i):
        k = i % n
        if k not in cache:
            im = Image.open(quadros[k]).convert("RGB")
            ec = max(W / im.width, H / im.height)                                             # fundo contínuo (cobre a tela)
            capa = im.resize((int(im.width * ec) + 1, int(im.height * ec) + 1), Image.BILINEAR)
            capa = capa.crop(((capa.width - W) // 2, (capa.height - H) // 2, (capa.width - W) // 2 + W, (capa.height - H) // 2 + H))
            base = capa.filter(ImageFilter.GaussianBlur(40))
            e = 0.84 * W / im.width                                                            # proporção original
            menor = im.resize((int(im.width * e), int(im.height * e)), Image.LANCZOS)
            m = Image.new("L", menor.size, 0)
            ImageDraw.Draw(m).rectangle((90, 90, menor.width - 90, menor.height - 90), fill=255)
            m = m.filter(ImageFilter.GaussianBlur(55))
            base.paste(menor, (int((W - menor.width) / 2), 250 if menor.height > H * 0.7 else 420), m)
            cache[k] = base
        return cache[k]
    gancho = etiqueta(cfg["gancho"], 92, AMARELO, TINTA, inclina=-2)
    pontos = [etiqueta([p], 54, PAPEL, TINTA, raio=22, pad=(28, 14)) for p in cfg["pontos"]]
    # cartão final
    cartao = Image.new("RGBA", (W - 120, 530), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cartao)
    dc.rounded_rectangle((0, 14, cartao.width, cartao.height), 40, fill=(0, 0, 0, 255))
    dc.rounded_rectangle((0, 0, cartao.width, cartao.height - 14), 40, fill=TINTA + (255,))
    cartao.alpha_composite(logo(96), (48, 44))
    dc.text((164, 56), "Ateliê do Mestre", font=fonte(58), fill=CREME)
    dc.text((48, 168), cfg["nome"], font=fonte(54, "SemiBold"), fill=CREME)
    dc.text((48, 238), cfg["preco"], font=fonte(84), fill=AMARELO)
    dc.rounded_rectangle((48, 352, cartao.width - 48, 432), 40, fill=AMARELO)
    cta = "Peça pelo WhatsApp · link na bio"
    f = fonte(40); cw = f.getbbox(cta)[2]
    dc.text(((cartao.width - cw) / 2, 368), cta, font=f, fill=TINTA)
    f2 = fonte(34, "Medium"); sw = f2.getbbox(SITE)[2]
    dc.text(((cartao.width - sw) / 2, 456), SITE, font=f2, fill=CREME)
    marca = etiqueta([SITE], 34, PAPEL, TINTA, raio=18, pad=(20, 10))

    saida = os.path.join(R, "videos", f"{nome}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    total = int(DUR * FPS)
    for k in range(total):
        t = k / FPS
        quadro = fundo(int(t / cfg["troca"]) if cfg.get("troca") else int(t * 20)).convert("RGBA")   # giro: 20 quadros/s, 1 volta a cada 4 s
        # gancho: entra pulando, fica, sobe e diminui quando chegam os pontos
        if t < 7.2:
            e = pulo((t - 0.1) / 0.45)
            sobe = suave((t - 2.6) / 0.5)
            colar(quadro, gancho, W / 2, 330 - 60 * sobe, e * (1 - 0.25 * sobe), 1 - suave((t - 6.8) / 0.4))
        for i, p in enumerate(pontos):
            t0 = 2.9 + i * 1.1
            if t0 <= t < 7.2:
                e = suave((t - t0) / 0.35)
                colar(quadro, p, W / 2 + (1 - e) * 140 * (1 if i % 2 else -1), 1330 + i * 122, 1.0, e * (1 - suave((t - 6.8) / 0.4)))
        if t >= 7.0:
            e = suave((t - 7.0) / 0.45)
            colar(quadro, cartao, W / 2, 1300 + (1 - e) * 600, 1.0, 1.0)
        ff.stdin.write(quadro.convert("RGB").tobytes())
        if k == int(1.4 * FPS):
            quadro.convert("RGB").save(os.path.join(R, "videos", f"{nome}_capa.jpg"), quality=88)
    ff.stdin.close(); ff.wait()
    if cfg.get("fotos"):
        print("ok", nome, saida, round(os.path.getsize(saida) / 1e6, 1), "MB", flush=True); return
    # laço curto sem texto para o site (1 volta, 540x960, leve)
    os.makedirs(os.path.join(R, "site", "vid"), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "20", "-i", os.path.join(Q, nome, "%04d.png"),
                    "-vf", "scale=540:960", "-c:v", "libx264", "-crf", "28", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-an", os.path.join(R, "site", "vid", f"{nome}.mp4")], check=True)
    Image.open(quadros[0]).convert("RGB").resize((540, 960), Image.LANCZOS).save(os.path.join(R, "site", "img", f"giro_{nome}.webp"), quality=82)
    print("ok", nome, saida, round(os.path.getsize(saida) / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    for nome in sys.argv[1:] or list(VIDEOS):
        montar(nome)
