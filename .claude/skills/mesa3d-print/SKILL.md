---
name: mesa3d-print
description: Criar, ajustar e checar peças para impressão 3D na Bambu Lab A1 Combo (FDM, PLA, AMS lite) do projeto Mesa3D – tiles e terreno de RPG, bases de miniatura, conectores, encaixes, caixas, suportes de dados, peças com ímã. Use sempre que o usuário pedir algo para imprimir, mencionar STL, 3MF, OpenSCAD, Bambu, fatiar, tile, miniatura, encaixe, tolerância, folga, ímã, cenário ou terreno de mesa, mesmo que não fale "impressão 3D" explicitamente.
---

# Mesa3D – impressão 3D na Bambu A1

O objetivo é entregar um arquivo que o usuário abre no Bambu Studio e imprime de primeira. Por isso tudo passa pelo perfil da impressora e pela checagem de malha antes de ser entregue.

## Arquivos desta skill
- `printer-profile.json` – mesa (256³ mm, margem 6 mm), bico 0.4, camadas, paredes mínimas, folgas, ímãs, grade de RPG (25.4 mm). **Leia antes de dimensionar qualquer coisa.** Valores com `"calibrado": false` são chutes iniciais; quando o usuário trouxer o resultado do gauge, atualize o JSON *e* as constantes de `lib/mesa3d.scad` (os dois precisam bater).
- `lib/mesa3d.scad` – constantes e módulos: `furo_ima()`, `gravar()`, `tile_chao(nx, ny, altura, sulco, imas)`.
- `scripts/preview.sh modelo.scad [3mf]` – gera STL (+3MF), PNG de prévia e roda a checagem.
- `scripts/check_mesh.py arquivo.stl` – malha fechada, normais, cabe na mesa (inclusive na diagonal), volume/peso, paredes finas. Código 1 = não imprimir.
- `models/calibracao/` (na raiz do repo) – gauge de tolerância e tile 2×2 de teste.

## Fluxo
1. **Entenda a peça e a escala.** Para RPG, 1 quadrado = 25.4 mm (5 pés), miniaturas 28–32 mm. Pergunte só o que muda a geometria (medida de algo que precisa encaixar, quantidade de quadrados).
2. **Modele em OpenSCAD** em `models/<categoria>/<nome>.scad`, com `include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>` e parâmetros no topo do arquivo, para o usuário poder mudar tamanhos sem saber programar. OpenSCAD é a primeira escolha porque medidas exatas e encaixes ficam reproduzíveis; Blender (`blender -b`) é para formas orgânicas ou converter malhas – ao exportar, selecione só objetos do tipo MESH, senão ele dá "Object does not have geometry data".
3. **Pense na impressão enquanto modela** (FDM imprime camada por camada de baixo para cima):
   - Face plana grande na mesa; evite balanços acima de 45° ou precise de suporte.
   - Paredes ≥ 1.2 mm (mínimo absoluto 0.8). Texto gravado ≥ 5 mm de altura, 0.6 mm de fundo.
   - Folga é por lado: furo = peça + 2×folga. Use `FOLGA_JUSTA` para encaixe firme, `FOLGA_DESL` para algo que gira/desliza.
   - Furos de ímã abertos por baixo (o usuário cola o ímã depois); peças com ímã precisam de polaridade consistente – avise.
   - Peça maior que ~244 mm: divida com encaixe em vez de escalar.
4. **Gere e cheque:** `.claude/skills/mesa3d-print/scripts/preview.sh models/.../peca.scad 3mf`. Olhe o PNG (abra com Read) para conferir que a peça é a que você pretendia. Se o checker reprovar, conserte antes de entregar; avisos de parede fina valem uma olhada no modelo.
5. **Entregue** o `.3mf` (abre direto no Bambu Studio) e o PNG, com: tamanho, peso aproximado, orientação na mesa, se precisa de suporte, camada sugerida (0.2 padrão, 0.12 para detalhes) e quais valores ainda não estão calibrados.

## Multicolor (AMS lite, até 4 cores)
Filamentos disponíveis: preto, branco e vermelho (ver `filamentos` no perfil). Só proponha cores que o usuário tem; se uma peça pedir outra cor, sugira imprimir em branco e pintar.
Ainda não testado neste projeto. Caminho provável: um corpo por cor exportado como objetos separados, atribuindo filamento a cada um no Bambu Studio. Diga ao usuário que é experimental até a primeira impressão confirmar.

## Sistema de encaixe dos tiles
Ainda não escolhido. Padrão atual: tile plano com sulcos de grade e opção de ímãs 6×3 (`tile_chao(..., imas=true)`). Não reproduza OpenLOCK, Dragonlock ou outro sistema de memória: as medidas e a licença precisam vir do modelo oficial, baixado e conferido.

## Calibração
Se o usuário ainda não imprimiu `models/calibracao/gauge_tolerancia.3mf`, sugira imprimir antes de peças com encaixe. Ao receber o resultado ("o pino entrou justo no 15, girou no 25, ímã no 6.2"), atualize `folgas_mm`, `imas` e as constantes do `.scad`, e marque `"calibrado": true`.
