// Máscaras 2D do fundo da bandeja esculpida (coordenadas do centro do fundo, em mm).
// PARTE: gravura (sigilo + anel de runas, gravados) | moldura (encaixe da torre, em relevo)
include <../kit/kit_rpg.scad>
PARTE = "gravura";
TEMA = "paranormal";
TORRE = [101, 80];     // pegada da torre com folga
TORRE_Y = 37;          // centro da torre no fundo (para trás)
SIGILO_Y = -40;        // centro do sigilo (na frente, onde os dados param)
if (PARTE == "gravura") linear_extrude(1) translate([0, SIGILO_Y]) {
  sigilo2d(22);
  difference() { circle(r = 33, $fn = 96); circle(r = 31.8, $fn = 96); }
  for (k = [0:21]) rotate(k * 360 / 22) translate([0, 27.5]) runa2d(k + 50, 3.2);
}
if (PARTE == "moldura") linear_extrude(1) translate([0, TORRE_Y]) difference() {
  offset(r = 2) square(TORRE, center = true);
  square(TORRE, center = true);
  translate([-26, -TORRE[1] / 2 - 4]) square([52, 8]);
}
