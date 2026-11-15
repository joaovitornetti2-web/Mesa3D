// Caixa para um conjunto de dados de RPG (7 dados: d4, d6, d8, d10, d%, d12, d20)
// com tampa de encaixe e emblema temático. Emblemas ORIGINAIS inspirados nos
// elementos – não são os símbolos oficiais de nenhum jogo.
//
// PARTE:
//   "caixa"          – base (igual para todos os elementos)
//   "tampa"          – tampa com o emblema embutido (rebaixo para a cor 2)
//   "emblema"        – só o emblema, para imprimir em outra cor dentro da tampa
//   "tampa_simples"  – tampa de uma cor só, com o emblema gravado
// A tampa já sai virada para imprimir: face de cima apoiada na mesa (fica lisa), sem suporte.
include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>

ELEMENTO = "sangue";   // sangue | morte | conhecimento | energia | medo
PARTE    = "caixa";

// ---- medidas (mm) ----
INT = [84, 54, 24];    // espaço interno: cabe um jogo de 7 dados de ~16-22 mm
PAREDE = 2.0;
FUNDO  = 2.0;
RAIO   = 4;            // canto arredondado externo
TAMPA_TOPO = 3.0;
LABIO_ALT  = 5;        // borda da tampa que entra na caixa
LABIO_PAREDE = 1.6;
INLAY = 0.6;           // profundidade do emblema colorido (3 camadas de 0.2)
EXT = [INT[0] + 2 * PAREDE, INT[1] + 2 * PAREDE];

module ret_arred(tam, r) {
  hull() for (x = [r, tam[0] - r], y = [r, tam[1] - r]) translate([x, y]) circle(r = r);
}

// ---------------- emblemas (2D, centrados, ~38 mm) ----------------
module anel(r = 19, w = 1.6) { difference() { circle(r = r); circle(r = r - w); } }
module gota(s = 1) { hull() { circle(d = 6 * s); translate([0, 6.5 * s]) circle(d = 0.9); } }

module em_sangue() {
  anel();
  gota(1.5);
  for (a = [-1, 1]) rotate(a * 40) translate([0, -11]) rotate(-a * 40) gota(0.9);
  for (a = [-1, 1]) translate([a * 9.5, 7]) gota(0.6);
}
module em_morte() {
  anel();
  // ampulheta
  polygon([[-8, 11], [8, 11], [1.2, 0.8], [8, -11], [-8, -11], [-1.2, -0.8]]);
  for (y = [-12.5, 12.5]) translate([-10, y - 0.9]) square([20, 1.8]);
}
module em_conhecimento() {
  anel();
  difference() {
    intersection() { translate([0, -9]) circle(r = 14); translate([0, 9]) circle(r = 14); }
    intersection() { translate([0, -9]) circle(r = 12.4); translate([0, 9]) circle(r = 12.4); }
  }
  circle(r = 3.6);
  for (a = [-50, -25, 0, 25, 50]) rotate(a) translate([-0.6, 7.5]) square([1.2, 5]);
}
module em_energia() {
  anel();
  polygon([[3, 14], [-7, -1], [-0.5, -1], [-4, -14], [7, 2.5], [0.5, 2.5]]);
}
module em_medo() {
  difference() { anel(); for (a = [0:72:359]) rotate(a + 18) translate([-1.2, 14]) square([2.4, 6]); }
  difference() { circle(r = 6); circle(r = 4.4); }
  for (a = [0:72:359]) rotate(a) polygon([[-1.3, 7], [1.3, 7], [0, 15]]);
}
module emblema2d(e) {
  if (e == "sangue") em_sangue();
  else if (e == "morte") em_morte();
  else if (e == "conhecimento") em_conhecimento();
  else if (e == "energia") em_energia();
  else if (e == "medo") em_medo();
}
function nome(e) = e == "conhecimento" ? "CONHECIMENTO" : e == "sangue" ? "SANGUE"
  : e == "morte" ? "MORTE" : e == "energia" ? "ENERGIA" : "MEDO";

// Arte completa da tampa (emblema + nome), em coordenadas da face de cima da tampa.
module arte2d(e) {
  translate([EXT[0] / 2, EXT[1] / 2 + 5]) scale(0.95) emblema2d(e);
  translate([EXT[0] / 2, 6.5])
    text(nome(e), size = e == "conhecimento" ? 5 : 5.5, halign = "center", valign = "center",
         font = "Liberation Sans:style=Bold", spacing = 1.1);
}

// ---------------- peças ----------------
module caixa() {
  difference() {
    linear_extrude(FUNDO + INT[2]) ret_arred(EXT, RAIO);
    translate([PAREDE, PAREDE, FUNDO]) linear_extrude(INT[2] + 1) ret_arred([INT[0], INT[1]], RAIO - PAREDE);
    // rebaixo para pegar a tampa com o dedo
    translate([EXT[0] / 2, -1, FUNDO + INT[2]]) rotate([-90, 0, 0]) cylinder(r = 7, h = EXT[1] + 2);
  }
}

// Tampa já na posição de impressão: z=0 é a face de cima (visível) da tampa.
// A arte é espelhada em X para ser lida corretamente quando a tampa for virada.
module tampa_corpo() {
  lab = [INT[0] - 2 * FOLGA_JUSTA, INT[1] - 2 * FOLGA_JUSTA];
  linear_extrude(TAMPA_TOPO) ret_arred(EXT, RAIO);
  translate([PAREDE + FOLGA_JUSTA, PAREDE + FOLGA_JUSTA, TAMPA_TOPO - 0.01])
    linear_extrude(LABIO_ALT) difference() {
      ret_arred(lab, RAIO - PAREDE);
      translate([LABIO_PAREDE, LABIO_PAREDE]) ret_arred(lab - [2, 2] * LABIO_PAREDE, max(0.5, RAIO - PAREDE - LABIO_PAREDE));
    }
}
module arte_impressao(e) { translate([EXT[0], 0]) mirror([1, 0]) arte2d(e); }

// Cores sugeridas com os filamentos disponíveis (preto, branco, vermelho): [caixa/tampa, emblema]
function cores(e) = e == "sangue" ? ["#1a1a1a", "#c0141c"] : e == "morte" ? ["#1a1a1a", "#f2f2f2"]
  : e == "conhecimento" ? ["#f2f2f2", "#1a1a1a"] : e == "energia" ? ["#c0141c", "#1a1a1a"] : ["#f2f2f2", "#c0141c"];

if (PARTE == "preview") {
  c = cores(ELEMENTO);
  color(c[0]) caixa();
  // virar a tampa = girar 180° no eixo Y (como na mão), não espelhar
  translate([EXT[0], 0, FUNDO + INT[2] + TAMPA_TOPO]) rotate([0, 180, 0]) {
    color(c[0]) difference() { tampa_corpo(); translate([0, 0, -0.01]) linear_extrude(INLAY + 0.01) arte_impressao(ELEMENTO); }
    color(c[1]) translate([0, 0, -0.02]) linear_extrude(INLAY + 0.02) arte_impressao(ELEMENTO);
  }
}
if (PARTE == "caixa") caixa();
if (PARTE == "tampa") difference() { tampa_corpo(); translate([0, 0, -0.01]) linear_extrude(INLAY + 0.01) arte_impressao(ELEMENTO); }
if (PARTE == "emblema") linear_extrude(INLAY) arte_impressao(ELEMENTO);
if (PARTE == "tampa_simples") difference() { tampa_corpo(); translate([0, 0, -0.01]) linear_extrude(0.81) arte_impressao(ELEMENTO); }
