// Gauge de tolerância para a Bambu A1 (PLA, bico 0.4, camada 0.2, sem suporte).
// Imprima a placa e o pino. Teste o pino em cada furo e anote:
//   - menor número em que o pino ENTRA apertado  -> folga "pressao"/"encaixe_justo"
//   - menor número em que ele GIRA solto          -> folga "deslizante"
// Números da fileira da frente = folga por lado em centésimos de mm (15 = 0.15 mm),
// do mais justo (esquerda, canto chanfrado) para o mais solto (direita).
// Fileira de trás: teste um ímã 6x3; o diâmetro do furo em mm está gravado ao lado.
include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>

PINO_D = 5;
folgas = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40];
imas_d = [6.1, 6.2, 6.3, 6.4];
ESP = 5; LARG = 15; LARG_TOT = LARG * len(folgas); ALT = 42;
PASSO_IMA = LARG_TOT / len(imas_d);

module placa() {
  difference() {
    cube([LARG_TOT, ALT, ESP]);
    // chanfro no canto do lado mais justo, para orientar a peça
    translate([0, 0, -1]) rotate([0, 0, 45]) cube([6, 6, ESP + 2], center = true);
    for (k = [0:len(folgas) - 1]) {
      translate([LARG * (k + 0.5), 9, -1]) cylinder(d = PINO_D + 2 * folgas[k], h = ESP + 2);
      translate([LARG * (k + 0.5), 19, 0]) gravar(str(round(folgas[k] * 100)), tam = 5, topo = ESP);
    }
    for (k = [0:len(imas_d) - 1]) {
      translate([PASSO_IMA * (k + 0.5) - 5, 33, ESP - IMA_H]) cylinder(d = imas_d[k], h = IMA_H + 1);
      translate([PASSO_IMA * (k + 0.5) + 4.5, 33, 0]) gravar(str(imas_d[k]), tam = 5, topo = ESP);
    }
  }
}

module pino() { translate([-12, 9, 0]) { cylinder(d = PINO_D, h = 12); cylinder(d = 9, h = 1.2); } }

placa();
pino();
