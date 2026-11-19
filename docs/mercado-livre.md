# Vender no Mercado Livre – Mesa3D

## 1. Criar a conta de vendedor (você mesmo faz – leva ~10 min)
1. Acesse mercadolivre.com.br → **Crie a sua conta**. Use e-mail e celular que você vai manter.
2. Escolha **pessoa física (CPF)** para começar. Se as vendas crescerem, abra um **MEI** e troque para CNPJ – fica mais barato em impostos e permite emitir nota fiscal.
3. Valide o celular e o documento (o ML pede foto do RG/CNH e uma selfie).
4. Ative o **Mercado Pago** na mesma conta – é para onde vai o dinheiro das vendas.
5. Em **Minha conta → Vendas → Preferências**, cadastre o endereço de despacho e configure o **Mercado Envios**.

> Ninguém além de você deve digitar CPF, senha ou documento. Eu não crio a conta por você.

## 2. Antes de publicar
- **Espere a impressora e imprima as peças de amostra.** Anúncio com foto real da peça (de preferência com uma miniatura do lado para dar escala) vende muito mais e evita reclamação. As imagens de prévia daqui servem só como apoio.
- **Não anuncie com preço simbólico** (tipo R$ 1 "para orçamento"): o ML proíbe e pode pausar o anúncio. Use anúncios com preço real e **variações** (tamanho/quantidade).
- **Só modelos próprios ou com licença comercial.** Não venda cópias de miniaturas de marcas (Warhammer, personagens oficiais de D&D, etc.) nem modelos baixados que proíbem uso comercial – isso derruba a conta.
- Toda conversa com o cliente **dentro do ML** (perguntas e mensagens pós-venda). Passar WhatsApp ou pedir pagamento por fora é proibido.

## 3. Títulos sugeridos (até 60 caracteres)
- `Tiles Mapa Rpg 3d Grade 25mm Personalizado Dnd Tormenta`
- `Cenário Rpg Impresso 3d Personalizado Masmorra Miniatura`
- `Peça Personalizada Rpg Impressão 3d Sob Medida Pla`

## 4. Descrição (copie e ajuste os campos entre colchetes)

```
PEÇAS DE RPG IMPRESSAS EM 3D – FEITAS SOB MEDIDA PARA A SUA MESA

Criamos peças personalizadas para qualquer sistema de RPG: D&D, Tormenta20,
Ordem Paranormal, Pathfinder, Call of Cthulhu, sistemas próprios e o que mais
a sua mesa jogar. É só nos dar as especificações!

O QUE FAZEMOS
• Tiles e mapas modulares com grade de 1 quadrado = 25,4 mm (5 pés)
• Paredes, portas, pilares, escadas e terreno
• Bases para miniaturas (escala 28–32 mm)
• Marcadores de condição, iniciativa e área de efeito
• Porta-dados, organizadores e acessórios de mesa
• Projetos sob medida: descreva a ideia e a gente modela

COMO FUNCIONA
1. Antes de comprar, mande uma pergunta aqui no anúncio com o que você precisa
   (o que é a peça, tamanho, quantidade, cor, fotos ou desenhos de referência).
2. Respondemos com o preço e o prazo.
3. Você compra a variação combinada e manda os detalhes finais pelas mensagens
   do Mercado Livre.
4. Modelamos, imprimimos, conferimos e enviamos.

SOBRE O PREÇO
O preço varia bastante conforme o tamanho da peça, a quantidade de filamento,
o tempo de impressão e a complexidade do modelo. Peças pequenas e simples saem
baratas; cenários grandes ou muito detalhados custam mais. Peça seu orçamento
sem compromisso.

MATERIAL E CORES
• Impressão em PLA de alta qualidade (Bambu Lab A1)
• Cores disponíveis: preto, branco e vermelho (peças podem combinar cores)
• Peças em branco são ótimas para pintar com tinta acrílica
• Não exponha ao calor forte (ex.: carro ao sol): o PLA amolece perto de 55 °C

PRAZO
Produção em até [X] dias úteis após a confirmação dos detalhes, mais o frete.

IMPORTANTE
• Peças impressas em 3D podem ter linhas de camada leves – é característica do processo.
• Fazemos apenas modelos próprios ou com licença para venda.
```

## 5. Como calcular o preço
Filamento: **R$ 149 por carretel de 1 kg ≈ R$ 0,15 por grama** (confirme se o seu carretel é de 1 kg).

```
custo = filamento (gramas do Bambu Studio × 0,15)
      + energia (≈ R$ 0,10 a 0,20 por hora de impressão – estimativa)
      + 15% de margem para falhas
      + seu tempo (modelagem, acabamento, embalagem)
      + embalagem

preço = custo ÷ (1 − tarifa do ML)
```

- **Tarifa do ML:** cerca de 10–14% no anúncio Clássico e 15–19% no Premium, conforme a categoria, mais custo de envio/fixo em itens baratos. Os valores mudam – **confira no simulador oficial** da Central de Vendedores antes de fechar o preço.
- **O filamento é a parte barata.** Um tile 2×2 gasta só uns R$ 1,50–2,80 de plástico. O que pesa é o seu tempo e a tarifa. Cobre a modelagem de peças personalizadas à parte (ou embuta no preço da primeira unidade).
- Itens abaixo de ~R$ 79 sofrem mais com a tarifa fixa: prefira vender **kits** (ex.: 10 tiles, conjunto de paredes) em vez de peças avulsas.

## 6. Anúncios prontos com preço (copie e cole)

> **Estes preços são estimativas, ainda não testadas na impressora.** O peso vem do volume dos modelos (calculado com
> `check_mesh.py` e com o OpenSCAD), não do Bambu Studio. Assim que imprimir a amostra, troque pelo peso e tempo reais
> que o Bambu Studio mostra e refaça a conta. Confira as tarifas no **simulador oficial** antes de publicar.

**O que a conta considera:**
- Filamento a R$ 0,15/g + 15% de perda por falhas.
- Energia ≈ R$ 0,10 por hora de impressão.
- Seu tempo a **R$ 30/h** (acabamento, embalagem, ir aos Correios).
- Anúncio **Clássico, com tarifa de 14%** (o teto da faixa, para não ter surpresa).
- **Abaixo de R$ 79:** soma ~R$ 7 de custo adicional por venda (desde 2026 ele varia com peso e tamanho).
- **R$ 79 ou mais:** o frete grátis é obrigatório, e o vendedor paga uma parte. Estimei R$ 25 para caixa grande e R$ 15 para caixa pequena (depende da sua reputação).
- **Preço mínimo** é o valor que só empata. O **preço sugerido** já inclui o lucro.

| Produto | Peso est. | Tempo est. | Custo total* | Preço mínimo | **Preço sugerido** | Lucro por venda |
|---|---|---|---|---|---|---|
| Kit torre de dados desmontável (bandeja + torre + telhado + sino + brasão) | ~330 g | ~18 h | ~R$ 117 | R$ 136 | **R$ 199,90** | ~R$ 55 |
| Anéis de condição (8 un., 2 cores) | ~12 g | ~1,5 h | ~R$ 15 | R$ 18 | **R$ 34,90** | ~R$ 15 |
| Caixa de dados com tampa em 2 cores (cabe 7 dados) | ~40 g | ~3 h | ~R$ 25 | R$ 29 | **R$ 49,90** | ~R$ 18 |
| Mini quadro em relevo do seu desenho (personalizado, ~17×13 cm) | ~80 g | ~4 h | ~R$ 52 | R$ 60 | **R$ 89,90** | ~R$ 25 |
| Kit 10 tiles 2×2 para mapa de RPG | ~120 g | ~6 h | ~R$ 51 | R$ 59 | **R$ 69,90** | ~R$ 9 |

\* Custo total = filamento + perda + energia + seu tempo + embalagem + custo fixo ou frete. A tarifa de 14% já está no preço mínimo.

**Por que esses números:**
- A torre é o produto com mais lucro. Uma torre de marca (não impressa) custa ~R$ 300, então R$ 199,90 é competitivo. Ela ocupa a impressora por quase um dia, e o filamento é ~R$ 50 só nela.
- Os anéis e a caixa servem de "porta de entrada" baratos. Anuncie também um **combo torre + anéis + caixa por R$ 259,90**.
- Os tiles dão pouco lucro avulsos. Se quiser vender mais deles, faça kits de 20 por R$ 119,90.
- O quadro personalizado leva ~20 min de preparo do desenho por pedido, e isso já está no custo.

### Títulos (até 60 caracteres)
- `Torre De Dados Rpg Desmontável Impressão 3d Bandeja Dnd`
- `Anéis De Condição Rpg 8 Marcadores Miniatura 25mm Dnd`
- `Caixa Porta Dados Rpg 7 Dados Tampa 2 Cores Impressão 3d`
- `Quadro Personalizado Do Seu Desenho Em Relevo 3d Presente`
- `Kit 10 Tiles Mapa Rpg 3d Grade 25mm Masmorra Dnd`

> Na caixa de dados, **não use "Ordem Paranormal"** no título nem na descrição. É marca registrada, e os emblemas
> são originais e só *inspirados* nos elementos. Escreva "elementos paranormais" ou "Sangue, Morte, Medo…".

### Descrições curtas (adicione o bloco "Material e cores / Prazo / Importante" da seção 4)

**Torre de dados:**
```
TORRE DE DADOS DESMONTÁVEL PARA RPG – DESIGN EXCLUSIVO
• Bandeja 15 × 15 cm + torre de 13 cm com campanário, telhado, sino e brasão de d20
• Rampas internas que embaralham os dados; a saída cabe até d20 de 26 mm
• Desmonta em 5 peças e cabe na mochila. Não precisa de cola
• Fica ótima em PLA preto, ou em branco para pintar
```

**Anéis de condição:**
```
8 ANÉIS DE CONDIÇÃO PARA MINIATURAS (BASE 25 MM)
• Encaixe na base da miniatura e marque a condição na hora
• Texto em relevo em 2 cores: Atordoado, Caído, Cego, Envenenado, etc.
• Serve para D&D, Tormenta20, Pathfinder e outros sistemas
```

**Caixa de dados:**
```
CAIXA PORTA-DADOS COM TAMPA EM 2 CORES
• Cabe um jogo completo de 7 dados (interno 84 × 54 × 24 mm)
• Escolha o emblema: Sangue, Morte, Conhecimento, Energia ou Medo
• Tampa com encaixe por pressão
```

**Quadro em relevo:**
```
TRANSFORME UM DESENHO EM QUADRO 3D
• Desenho de filho, pet, logo ou assinatura vira um quadro em relevo de 2 cores
• Cerca de 17 × 13 cm, com moldura, furo para pendurar e suporte de mesa
• Depois da compra, envie a foto do desenho pelas mensagens do Mercado Livre
• Funciona melhor com desenho em linha escura sobre papel branco
```
