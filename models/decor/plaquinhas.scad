// Plaquinhas de decoração do Ateliê do Mestre – 2 cores: base (cor 1) e texto/moldura/ícone em relevo (cor 2).
// A troca de cor é só no topo: quase sem purga no AMS. Furos escareados de 3,5 mm (prego/parafuso) ou fita dupla face.
// PARTE: <placa>_c1 | <placa>_c2
//   estilo do Ateliê: nao_perturbe, covil, criaturas
//   estilo do dia a dia: bem_vindos, home_office, nome   (NOME = texto da plaquinha personalizada)
include <../kit/kit_rpg.scad>
use <fontes/Fredoka.ttf>
PARTE = "nao_perturbe_c1";
TEMA = "paranormal";
NOME = "Quarto da Alice";
FONTE = "Fredoka:style=Bold";
W = 160; H = 60; E = 4; R = 1.2;
$fn = 48;

// ---------- formatos ----------
module forma(tipo) {
  if (tipo == "gotica") offset(r = 1.5) polygon([[8, 0], [W - 8, 0], [W, 8], [W, H - 8], [W - 8, H], [8, H], [0, H - 8], [0, 8]]);
  if (tipo == "pilula") hull() { translate([H / 2, H / 2]) circle(d = H); translate([W - H / 2, H / 2]) circle(d = H); }
  if (tipo == "nuvem") union() {
    hull() { translate([16, 16]) circle(r = 16); translate([W - 16, 16]) circle(r = 16); }
    for (p = [[28, 34, 20], [62, 40, 24], [100, 40, 22], [134, 34, 20]]) translate([p[0], p[1]]) circle(r = p[2]);
  }
}
module moldura(tipo, d = 3, l = 1.6) { difference() { offset(r = -d) forma(tipo); offset(r = -d - l) forma(tipo); } }

// ---------- ícones 2D ----------
module ico_fantasma(s = 1) { scale(s) difference() {
  union() { translate([0, 4]) circle(r = 8); translate([-8, -6]) square([16, 10]); for (x = [-5.3, 0, 5.3]) translate([x, -6]) circle(r = 2.7); }
  for (x = [-3, 3]) translate([x, 5]) circle(r = 1.6);
  translate([0, 0.5]) scale([1, 0.7]) circle(r = 1.5);
} }
module ico_coracao(s = 1) { scale(s) { hull() { translate([-3, 2]) circle(r = 3.4); translate([0, -5]) circle(r = 0.5); } hull() { translate([3, 2]) circle(r = 3.4); translate([0, -5]) circle(r = 0.5); } } }
module ico_xicara(s = 1) { scale(s) {
  hull() { translate([-7, 4]) square([14, 1]); translate([-5, -6]) square([10, 1]); }
  translate([8.2, -0.5]) difference() { circle(r = 3.8); circle(r = 2); }
  translate([-9, -8.2]) square([18, 1.6]);
  for (x = [-3, 1.5]) translate([x, 7]) hull() { circle(d = 1.2); translate([0.8, 4]) circle(d = 1.2); }
} }
module ico_estrela(s = 1) { scale(s) polygon([for (k = [0:9]) let(r = k % 2 ? 2.6 : 6.4, a = 90 + k * 36) [r * cos(a), r * sin(a)]]); }

module linha(t, tam, x, y) { translate([x, y]) text(t, size = tam, font = FONTE, halign = "center", valign = "center"); }

// ---------- cada plaquinha ----------
function tipo_de(n) = (n == "nao_perturbe" || n == "covil" || n == "criaturas") ? "gotica" : n == "bem_vindos" ? "nuvem" : "pilula";
module arte(n) {
  t = tipo_de(n);
  if (t == "gotica") { moldura(t, 3, 1.4); moldura(t, 6, 0.8); }
  else moldura(t, 3.5, 1.6);
  if (n == "nao_perturbe") { linha("NÃO PERTURBE", 10.5, W / 2 + 13, 36); linha("sessão em andamento", 7, W / 2 + 13, 19); translate([27, H / 2]) d20_2d(11); }
  if (n == "covil") { linha("COVIL", 15, W / 2 + 12, 38); linha("DO MESTRE", 10, W / 2 + 12, 18); translate([27, H / 2]) sigilo2d(13); }
  if (n == "criaturas") { linha("CUIDADO!", 13, W / 2 + 12, 36); linha("criaturas soltas", 7.5, W / 2 + 12, 18); translate([26, H / 2 - 1]) ico_fantasma(1.5); }
  if (n == "bem_vindos") { linha("Bem-vindos", 13, W / 2, 31); for (x = [27, W - 27]) translate([x, 31]) ico_coracao(0.9); }
  if (n == "home_office") { linha("Home Office", 11, W / 2 + 14, 36); linha("em reunião, volto já!", 6.2, W / 2 + 14, 19); translate([30, H / 2]) ico_xicara(1.25); }
  if (n == "nome") { linha(NOME, 10.5, W / 2, H / 2); for (x = [24, W - 24]) translate([x, H / 2]) ico_estrela(0.9); }
}
module placa(n, cor) {
  t = tipo_de(n);
  furos = t == "nuvem" ? [[18, 16], [W - 18, 16]] : [[t == "pilula" ? 10 : 9, H / 2], [W - (t == "pilula" ? 10 : 9), H / 2]];
  if (cor == 1) difference() {
    linear_extrude(E) forma(t);
    for (f = furos) translate([f[0], f[1], -1]) { cylinder(d = 3.5, h = E + 2); translate([0, 0, E - 0.2]) cylinder(d1 = 3.5, d2 = 6.5, h = 1.21); }
  }
  if (cor == 2) translate([0, 0, E - 0.01]) linear_extrude(R + 0.01) difference() {
    arte(n);
    for (f = furos) translate(f) circle(d = 7.5);   // não cobre os furos
  }
}
for (n = ["nao_perturbe", "covil", "criaturas", "bem_vindos", "home_office", "nome"], c = [1, 2])
  if (PARTE == str(n, "_c", c)) placa(n, c);
