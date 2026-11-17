// Torre de dados "Caveira do Deus da Morte" – bandeja e lápide (uso pessoal).
// A caveira vem do Meshy (montada por preparar_caveira.py); aqui ficam as peças paramétricas.
// PARTE: bandeja | lapide_base | lapide_texto | montado
include <caveira_pegada.scad>
use <torre_porteiro.scad>
PARTE = "bandeja";
$fn = 48;

BX = 162; BY = 208; BH = 16; BW = 4; BF = 3;   // bandeja (largura, profundidade, altura, parede, fundo)
CX = BX / 2; CY = 136;                          // centro da caveira na bandeja
REB = 1.6; FOLGA = 0.4;                         // rebaixo do encaixe da caveira

module pegada2d() { for (p = PEGADA) polygon(p); }

module pedras(w, h) {   // sulcos de pedra numa face (normal -Y)
  for (j = [0:floor(h / 6)]) {
    translate([-1, -0.01, j * 6]) cube([w + 2, 0.8, 0.8]);
    for (i = [0:floor(w / 18) + 1]) translate([i * 18 - (j % 2) * 9, -0.01, j * 6]) cube([0.8, 0.8, 6]);
  }
}
module raizes() {   // raízes rasas saindo da caveira pelo chão (relevo 0,8 mm)
  for (a = [[-62, 30, 34], [-40, -2, 40], [40, 2, 38], [62, -30, 30], [-75, 60, 26], [75, -60, 24]])
    translate([CX, CY - 50, BF - 0.01]) rotate(a[0] - 90) linear_extrude(0.8, scale = 0.3) translate([0, 0]) polygon([[-2, 0], [2, 0], [0.8, a[2]], [-0.8, a[2]]]);
}

module bandeja() {
  difference() {
    hull() for (x = [6, BX - 6], y = [6, BY - 6]) translate([x, y, 0]) cylinder(r = 6, h = BH);
    translate([0, 0, BF]) hull() for (x = [6 + BW, BX - 6 - BW], y = [6 + BW, BY - 6 - BW]) translate([x, y, 0]) cylinder(r = 6 - BW / 2, h = BH);
    for (r = [0, 180]) translate([BX / 2, BY / 2, 0]) rotate(r) translate([-BX / 2, -BY / 2, 2]) pedras(BX, BH - 4);
    for (r = [90, 270]) translate([BX / 2, BY / 2, 0]) rotate(r) translate([-BY / 2, -BX / 2, 2]) pedras(BY, BH - 4);
    // encaixe da caveira (rebaixo com a forma da base)
    translate([CX, CY, BF - REB]) linear_extrude(REB + 1) offset(delta = FOLGA) pegada2d();
    // espiral da Morte gravada onde os dados param
    translate([CX, 38, BF - 0.8]) linear_extrude(1) espiral_morte(24);
    // encaixe do pino da lápide (canto frontal esquerdo)
    translate([20 - 6.3, 58 - 2.3, BF - 2]) cube([12.6, 4.6, 3]);
  }
  intersection() { raizes(); translate([BW + 1, BW + 1, 0]) cube([BX - 2 * BW - 2, CY - 70, 10]); }
}
module espiral_morte(r) {
  s = 2 * r / (2 * 224.312);
  scale(s) translate([-138.2, -223.47]) import("/home/user/Mesa3D/models/decoracao/simbolos/morte.svg");
}

if (PARTE == "bandeja") bandeja();
if (PARTE == "lapide_base") lapide_base();
if (PARTE == "lapide_texto") lapide_texto();
if (PARTE == "montado") {
  color("#1a1a1a") bandeja();
  translate([20, 58, BF - 2]) rotate([90, 0, 0]) translate([0, 2.5, -3]) { color("#eeeeee") lapide_base(); color("#c0141c") lapide_texto(); }
}
