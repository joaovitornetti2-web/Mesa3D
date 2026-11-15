// Gauge de tolerância para a Bambu A1 (PLA, bico 0.4, camada 0.2).
// Imprima a placa e o pino. Teste o pino em cada furo e anote:
//   - menor folga em que o pino ENTRA apertado  -> folga "pressao"/"encaixe_justo"
//   - menor folga em que ele GIRA solto          -> folga "deslizante"
// Depois teste um ímã 6x3 nos furos da fileira de trás (diâmetro em mm gravado ao lado).
// Números da fileira da frente = folga por lado em centésimos de mm (15 = 0.15 mm).
include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>

PINO_D = 5;
folgas = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40];
imas_d = [6.1, 6.2, 6.3, 6.4];
ESP = 5; LARG = 15;

module placa() {
  difference() {
    cube([LARG * len(folgas), 38, ESP]);
    for (k = [0:len(folgas) - 1]) {
      translate([LARG * (k + 0.5), 9, -1]) cylinder(d = PINO_D + 2 * folgas[k], h = ESP + 2);
      translate([LARG * (k + 0.5), 18, 0]) gravar(str(folgas[k] * 100), tam = 3.5, topo = ESP);
    }
    for (k = [0:len(imas_d) - 1]) {
      translate([LARG * len(folgas) / len(imas_d) * (k + 0.5) - 3, 28, ESP - IMA_H]) cylinder(d = imas_d[k], h = IMA_H + 1);
      translate([LARG * len(folgas) / len(imas_d) * (k + 0.5) + 5, 28, 0]) gravar(str(imas_d[k]), tam = 2.8, topo = ESP);
    }
  }
}

module pino() { translate([0, -12, 0]) { cylinder(d = PINO_D, h = 12); cylinder(d = 9, h = 1.2); } }

placa();
pino();
