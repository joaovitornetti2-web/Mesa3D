# Mesa3D

Peças de impressão 3D para mesa de RPG (tiles, terreno, conectores), feitas para a **Bambu Lab A1 Combo** (FDM, PLA).

- `models/` – modelos OpenSCAD (`.scad`), arquivos prontos para o Bambu Studio (`.3mf`) e prévias (`.png`).
- `.claude/skills/mesa3d-print/` – skill do Claude com o perfil da impressora, biblioteca OpenSCAD e checagem de malha.

## Primeiro passo: calibrar
Imprima `models/calibracao/gauge_tolerancia.3mf` (PLA, camada 0.2, sem suporte, ~20 g).
Teste o pino em cada furo e um ímã 6×3 nos furos de trás, e conte ao Claude:
em qual número o pino entra justo, em qual gira solto e em qual diâmetro o ímã entra firme.

## Quando a impressora chegar
1. Monte a A1 e o AMS lite seguindo o guia da Bambu, e faça a calibração automática que ela pede no primeiro uso.
2. Instale o **Bambu Studio** no computador e escolha: impressora *Bambu Lab A1*, bico *0.4*, filamento *PLA* (ex.: Bambu PLA Basic).
3. Primeira impressão: `models/calibracao/gauge_tolerancia.3mf` – camada 0.2, sem suporte.
4. Teste o pino e um ímã 6×3 e conte ao Claude os números (veja "Primeiro passo: calibrar"). Ele atualiza
   `.claude/skills/mesa3d-print/printer-profile.json` e `lib/mesa3d.scad`.
5. Depois: `models/calibracao/tile_teste_2x2.3mf` para conferir a grade de 25.4 mm com uma miniatura.

## Pendências (decidir depois)
- Como unir os tiles: clipe impresso, ímãs numa chapa de aço, ou tiles soltos.
- Multicolor com o AMS lite: ainda não testado.
