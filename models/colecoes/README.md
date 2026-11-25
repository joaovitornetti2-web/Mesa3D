# Coleções temáticas do Ateliê do Mestre

Quatro coleções de 12 peças esculpidas por campos de distância (`base.py` usa a biblioteca `../esculpidos/sdf.py`).
Desenhos originais, inspirados nos estilos de fantasia medieval de masmorra, terror paranormal, fantasia épica brasileira e aventura anos 80.

- Gerar uma coleção inteira (STL de foto, STL de impressão e 3MF): `python3 gerar.py <coleção> [peça ...]`
- Prova rápida de render: `python3 prova.py <coleção>/<peça> [elevação azimute]`
- Fotos, preços e trecho do site: `python3 ../../site/colecoes.py imagens|precos|site`

Os STL ficam em `stl/` e `stl_imprimir/` (fora do git); o 3MF de cada peça tem um objeto por cor para escolher o filamento no Bambu Studio.
**Nada disto foi testado na impressora ainda**: folgas de tampas, pinos e encaixes usam os valores padrão do perfil (não calibrados).

## Masmorra & Dragão (`masmorra/`)

| Peça | Cores | Como imprimir |
|---|---|---|
| Torre do Dragão (`torre_dragao-torre.3mf` + `torre_dragao-bandeja.3mf`) | c1 pedra, c2 dragão, c3 chifres, dentes, garras e olhos, c4 barriga e asas | Impressão: torre em pé, suporte em árvore só sob a cabeça e as asas; bandeja deitada, sem suporte. |
| Mímico Porta-Dados (`mimico.3mf`) | c1 madeira, c2 cintas/rebites/pupilas, c3 dentes e olhos, c4 língua | Impressão (--imprimir): base em pé e tampa de boca para cima, lado a lado, sem suporte. |
| Prisão de Dados (`prisao.3mf`) | c1 pedra, c2 ferro, c3 caveira, c4 chama | Imprime em pé, sem suporte (tocha em balanço curto, 45°). |
| Cubo Gelatinoso Porta-Dados (`cubo.3mf`) | c1 gosma, c2 lâmina e pupilas, c3 caveira e olhos, c4 cabo da espada e moedas | Em pé, sem suporte. |
| Dragãozinho do Crítico (`dragaozinho.3mf`) | c1 dragão, c2 d20 e pupilas, c3 barriga, chifres e olhos, c4 membrana das asas | Em pé, suporte em árvore só sob as asas. |
| Corujurso (`corujurso.3mf`) | c1 pelo, c2 pupilas e garras, c3 disco facial e brilho, c4 bico | Imprime em pé, sem suporte. |
| Bandeja de Dados Escudo (`bandeja_escudo.3mf`) | c1 escudo, c2 borda de metal, c3 rebites, c4 brasão (só nas últimas camadas) | Deitada, sem suporte. Dica: cole feltro no fundo para o dado rolar sem barulho. |
| Contador de Vida (`contador.3mf`) | c1 suporte, c2 rodas, c3 números, c4 coração | Rodas deitadas, suporte em pé, sem suporte. |
| Estandartes de Iniciativa (`iniciativa.3mf`) | c1 base e mastro, c2 estandarte, c3 número, c4 ponteira | Em pé, sem suporte. Impressão (--imprimir): os 8 lado a lado. |
| Porta da Masmorra (`porta.3mf`) | c1 pedra, c2 ferro, c3 caveira, c4 chamas, c5 madeira | Em pé, sem suporte (chamas com balanço curto). |
| Barril da Taverna (`barril.3mf`) | c1 madeira, c2 cintas e torneira, c3 espuma, c4 caneca | Em pé, sem suporte. |
| Porta-copos Brasão (`porta_copos.3mf`) | c1 porta-copo e muralha, c2 brasão (só nas últimas camadas), c3 borda de corda | Impressão (--imprimir): porta-copos deitados, um por arquivo de cor; muralha em pé, sem suporte. |

## Arquivo Paranormal (`paranormal/`)

| Peça | Cores | Como imprimir |
|---|---|---|
| Torre do Ritual (`torre_ritual.3mf`) | c1 pedra, c2 runas, olho e correntes, c3 velas, c4 cera e chamas | Em pé, sem suporte. |
| Livro Proibido (`livro.3mf`) | c1 couro, c2 metal e pupila, c3 páginas e branco do olho, c4 íris | Impressão (--imprimir): corpo e tampa em pé, lado a lado (tampão da tampa na mesa), sem suporte. |
| Caveira Porta-Dados (`caveira.3mf`) | c1 osso, c2 fundo das órbitas e do nariz, c3 velas e cera, c4 chamas | Impressão (--imprimir): corpo e tampa em pé, lado a lado; suporte em árvore só sob o queixo e as órbitas. |
| Caixa de Evidências (`evidencias.3mf`) | c1 caixa, c2 letras, c3 etiqueta, c4 fita | Impressão (--imprimir): corpo e tampa em pé, sem suporte. |
| Medidor de Sanidade (`sanidade.3mf`) | c1 carcaça, c2 traços, letras e ponteiro, c3 fundo do mostrador, c4 zona vermelha | Impressão (--imprimir): medidor deitado de costas e o ponteiro ao lado, sem suporte. |
| Bandeja Círculo de Ritual (`bandeja_ritual.3mf`) | c1 bandeja, c2 círculo e runas (últimas camadas), c3 velas, c4 cera | Deitada, sem suporte. Dica: feltro no fundo. |
| Entidade das Sombras (`entidade.3mf`) | c1 manto, c2 vazio do capuz, c3 garras e máscara de osso, c4 olhos | Em pé, suporte em árvore só sob as mãos. |
| Olho Vigia (`olho.3mf`) | c1 base e garras, c2 pupila, c3 globo, c4 íris e veias | Em pé, sem suporte (globo autoportante; a abertura de baixo tem chanfro de 45°). |
| Velas de Ritual (`velas.3mf`) | c1 prato, c2 runas (incrustadas), c3 velas, c4 cera escorrida (c5: chama da velinha de LED, só na foto) | Em pé, sem suporte. |
| Mão do Além (`mao.3mf`) | c1 terra, c2 mão, c3 lápide e ossos, c4 unhas e manga rasgada | Em pé, sem suporte. |
| Gravador da Investigação (`gravador.3mf`) | c1 carcaça, c2 grade, teclas e janela, c3 etiqueta e carretéis, c4 tecla de gravar e luz | Em pé, sem suporte (alça com arco de 45°). |
| Máscara do Ritual (`mascara.3mf`) | c1 máscara, c2 marcas e rachaduras, c4 lágrimas | Deitada de costas, sem suporte. |

## Reinos da Tempestade (`tempestade/`)

| Peça | Cores | Como imprimir |
|---|---|---|
| Torre da Tempestade Rubra (`torre_tempestade.3mf`) | c1 pedra, c2 rachaduras e portão, c3 raios, c4 nuvem | Em pé, sem suporte (nuvem com balanço de 45°). |
| Minotauro Guerreiro (`minotauro.3mf`) | c1 pelo, c2 metal (machado, ombreira, argola), c3 chifres, olhos e cascos, c4 tanga e faixa | Em pé, suporte em árvore só sob a lâmina do machado. |
| Goblin Engenhoqueiro (`goblin.3mf`) | c1 pele, c2 metal (chave, engrenagens, óculos), c3 olhos, dentes e lentes, c4 avental e fumaça | Em pé; suporte em árvore só sob a chave inglesa (a fumaça encosta na chaminé). |
| Aberração da Tempestade (`aberracao.3mf`) | c1 carapaça, c2 juntas e mandíbulas, c3 olhos, c4 cristais e rachaduras | Em pé, sem suporte (patas apoiadas na base). |
| Baú do Tesouro (`bau.3mf`) | c1 madeira, c2 metal, c3 gema, c4 moedas | Em pé, sem suporte. |
| Elmo Guarda-Dados (`elmo.3mf`) | c1 elmo, c2 rebites, viseira e faixa, c3 chifres, c4 crista e base | Impressão (--imprimir): elmo em pé (boca para baixo, cúpula autoportante) e base deitada, lado a lado. |
| Moedas do Reino (`moedas.3mf`) | c1 moeda, c2 símbolo e número (últimas camadas) | Impressão (--imprimir): uma moeda de cada, deitadas (duplique no fatiador). |
| Bandeja Nuvem Rubra (`bandeja_nuvem.3mf`) | c1 bandeja, c2 rachaduras do céu, c3 raios, c4 nuvens da borda (vermelhas) | Deitada, sem suporte. |
| Pergaminho do Aventureiro (`pergaminho.3mf`) | c1 papel, c2 tinta (mapa/letras na lateral), c3 fita, c4 selo de cera | Deitado, sem suporte. |
| Dragão de Pedra (`gargula.3mf`) | c1 pedra, c2 pedestal (blocos), c3 chifres e garras, c4 olhos | Em pé, suporte em árvore só sob as pontas das asas e o queixo. |
| Árvore dos Sussurros (`arvore.3mf`) | c1 tronco, c2 olhos/boca e corvo, c3 cogumelos, c4 musgo do prato | Em pé, suporte em árvore só sob as pontas dos galhos mais abertos. |
| Machado do Campeão (`machado.3mf`) | c1 suporte, c2 lâmina, c3 runas e gema, c4 couro do cabo | Impressão (--imprimir): machado deitado de lado (sem suporte) e o suporte em pé, lado a lado. |

## Turma da Bicicleta (`bicicleta/`)

| Peça | Cores | Como imprimir |
|---|---|---|
| Torre Fliperama (`fliperama.3mf`) | c1 gabinete, c2 tela, painel e moldura, c3 pixels e letreiro, c4 botões, manche e raio | Em pé, sem suporte. |
| Walkie-Talkie Porta-Celular (`walkie.3mf`) | c1 carcaça, c2 grade, botões e antena, c3 etiqueta "CANAL 9", c4 luz e botão de falar | Em pé, sem suporte. |
| Fita Cassete Porta-Dados (`fita.3mf`) | c1 carcaça, c2 janela, carretéis e parafusos, c3 etiqueta, c4 faixa e letras da etiqueta | Impressão (--imprimir): corpo e tampa em pé, lado a lado, sem suporte. |
| Boombox Porta-Trecos (`boombox.3mf`) | c1 carcaça, c2 alto-falantes, deck e alça, c3 cones e fita, c4 botões e luzes | Em pé, sem suporte. |
| BMX da Turma (`bmx.3mf`) | c1 quadro, c2 pneus, banco e manoplas, c3 rodas, c4 placa de número e base | Em pé, sem suporte (rodas apoiadas na base). |
| Casa na Árvore (`casa_arvore.3mf`) | c1 tronco e galhos, c2 casa (tábuas), c3 telhado, c4 placa, escada e bicicletinha | Impressão (--imprimir): árvore com a casa em pé e o telhado ao lado; suporte em árvore só sob o piso da casa. |
| Barra de Vida (`barra_vida.3mf`) | c1 régua, c2 moldura pixelada e letras, c3 brilho dos corações, c4 corações | Impressão (--imprimir): régua e os 10 corações deitados. |
| Porta-copos Disquete (`disquete.3mf`) | c1 disquete e estojo, c2 janela de metal e trava, c3 etiqueta, c4 letras | Impressão (--imprimir): disquetes deitados (etiqueta para cima) e estojo em pé, sem suporte. |
| Mochila da Aventura (`mochila.3mf`) | c1 mochila, c2 zíperes, fivelas e lanterna, c3 broches, c4 bolso e alças | Em pé, sem suporte. |
| Lanterna da Investigação (`lanterna.3mf`) | c1 corpo, c2 anéis, botão e alça, c3 vidro/refletor, c4 faixa refletiva | Em pé, sem suporte. |
| Placa do Clube (`placa_clube.3mf`) | c1 tábuas, c2 letras, c3 pregos, c4 raio e faixa | Deitada, sem suporte. |
| Chaveiro Fita Cassete (`chaveiro_fita.3mf`) | c1 fita, c2 janela e carretéis, c3 etiqueta, c4 letras | Deitado, sem suporte. |
