# Mesa3D

Peças de impressão 3D para mesa de RPG (tiles, terreno, conectores), feitas para a **Bambu Lab A1 Combo** (FDM, PLA).

- `models/` – modelos OpenSCAD (`.scad`), arquivos prontos para o Bambu Studio (`.3mf`) e prévias (`.png`).
- `.claude/skills/mesa3d-print/` – skill do Claude com o perfil da impressora, biblioteca OpenSCAD e checagem de malha.

## Primeiro passo: calibrar
Imprima `models/calibracao/gauge_tolerancia.3mf` (PLA, camada 0.2, sem suporte, ~20 g).
Teste o pino em cada furo e um ímã 6×3 nos furos de trás, e conte ao Claude:
em qual número o pino entra justo, em qual gira solto e em qual diâmetro o ímã entra firme.
