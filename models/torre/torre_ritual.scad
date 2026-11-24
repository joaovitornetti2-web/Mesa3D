// Torre do Ritual – bandeja da torre esculpida (torre: ritual/torre_ritual.stl, gerada por torre_meshy.py).
// Desenho próprio, inspirado no horror paranormal; sigilo e runas originais.
// PARTE: ritual_bandeja | ritual_montado  (nomes próprios: o kit incluído também lê PARTE)
include <../kit/kit_rpg.scad>
PARTE = "ritual_bandeja";
TEMA = "paranormal";

TORRE = [101, 80];         // pegada da torre esculpida (mm), com folga
BX = 160; BY = 178; BHT = 16; BWD = 4; BFD = 3; RC = 8;
TOR_Y = BY - BWD - 1 - TORRE[1] / 2;   // centro da torre (ao fundo)
PARADA_Y = 46;                          // onde os dados param

module ret(w, d, r) { hull() for (x = [r, w - r], y = [r, d - r]) translate([x, y]) circle(r = r, $fn = 32); }

module bandeja_ritual() {
  difference() {
    linear_extrude(BHT) ret(BX, BY, RC);
    translate([BWD, BWD, BFD]) linear_extrude(BHT) ret(BX - 2 * BWD, BY - 2 * BWD, RC - BWD / 2);
    // pedras nas laterais externas
    for (r = [0, 180]) translate([BX / 2, BY / 2, 0]) rotate(r) translate([-BX / 2 + RC, -BY / 2, 2]) pedras_face(BX - 2 * RC, BHT - 4, 6, 18);
    for (r = [90, 270]) translate([BX / 2, BY / 2, 0]) rotate(r) translate([-BY / 2 + RC, -BX / 2, 2]) pedras_face(BY - 2 * RC, BHT - 4, 6, 18);
    // sigilo e anel de runas gravados onde os dados param
    translate([BX / 2, PARADA_Y, BFD - 0.8]) linear_extrude(1) {
      sigilo2d(24);
      difference() { circle(r = 36, $fn = 96); circle(r = 34.8, $fn = 96); }
      for (k = [0:23]) rotate(k * 15) translate([0, 30]) runa2d(k + 50, 3.2);
    }
  }
  // moldura baixa onde a torre encaixa (aberta na frente, para a porta)
  translate([BX / 2, TOR_Y, BFD]) difference() {
    linear_extrude(1.6) offset(r = 2) square(TORRE, center = true);
    translate([0, 0, -1]) linear_extrude(4) square(TORRE, center = true);
    translate([-26, -TORRE[1] / 2 - 4, -1]) cube([52, 8, 4]);
  }
}

if (PARTE == "ritual_bandeja") bandeja_ritual();
if (PARTE == "ritual_montado") {
  color("#1a1a1a") bandeja_ritual();
  color("#2a2a2a") translate([BX / 2, TOR_Y, BFD]) import("ritual/torre_ritual.stl");
}
