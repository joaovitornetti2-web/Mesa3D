// Decoração do Ateliê do Mestre – ambiente e dia a dia, nos dois estilos.
// Cores: c1 = corpo, c2 = detalhes escuros, c3 = branco (olhos, dentes), c4 = acento (bochecha, nariz).
// PARTE: <peça>_c<n>
//   estilo do Ateliê: lanterna (c1), monstrinho (c1 c2 c3), porta_chaves_runa (c1 c2)
//   dia a dia:        vaso (c1), porta_copos (c1 c2), gatinho (c1 c2 c3 c4)
include <../kit/kit_rpg.scad>
use <fontes/Fredoka.ttf>
PARTE = "lanterna_c1";
TEMA = "paranormal";
FONTE = "Fredoka:style=Bold";
$fn = 64;

// ---------------- LANTERNA RÚNICA (para vela de LED) ----------------
module lanterna() {
  D = 72; Hh = 96; P = 2.4;
  difference() {
    union() {
      cylinder(d = D, h = Hh);
      cylinder(d = D + 6, h = 5);                                   // base com aba
      translate([0, 0, Hh - 4]) cylinder(d = D + 4, h = 4);         // borda de cima
    }
    translate([0, 0, 3]) cylinder(d = D - 2 * P, h = Hh);           // oco (cabe vela de LED de 38 mm)
    for (fila = [0:2], k = [0:9]) let(z = 22 + fila * 25, a = k * 36 + fila * 18)   // janelas em forma de runa
      rotate(a) translate([D / 2 - P - 1, 0, z]) rotate([90, 0, 90]) linear_extrude(P + 3) offset(r = 0.6) runa2d(k + fila * 10 + 400, 11);
    for (k = [0:5]) rotate(k * 60 + 30) translate([D / 2 - P - 1, 0, 87]) rotate([90, 0, 90]) linear_extrude(P + 3) circle(d = 4);
  }
}

// ---------------- MONSTRINHO PORTA-TRECOS (canetas, pincéis, dados) ----------------
MD = 74; MH = 92;
function msup(x) = -sqrt(MD * MD / 4 - x * x);
module monstrinho_det(cor) {
  for (s = [-1, 1]) translate([s * 13, msup(s * 13) + 0.8, 52]) rotate([90, 0, 0]) {     // olhos
    if (cor == 3) scale([1, 1.15, 0.5]) sphere(r = 9);
    if (cor == 2) translate([s * 1.2, -1.5, 3]) scale([1, 1.1, 0.5]) sphere(r = 5);
    if (cor == 3) translate([s * 1.2 + 2, 0.6, 5]) sphere(r = 1.6);
  }
  if (cor == 2) translate([0, msup(0) + 0.6, 30]) rotate([90, 0, 0]) scale([1, 0.55, 0.5]) difference() { sphere(r = 16); translate([0, 20, 0]) cube(40, center = true); } // boca
  if (cor == 3) for (x = [-8, 8]) translate([x, msup(x) + 0.2, 28.6]) rotate([90, 0, 0]) linear_extrude(1.6) polygon([[-3, 0], [3, 0], [0, -5]]);              // dentinhos
}
module monstrinho_corpo() {
  difference() {
    union() {
      cylinder(d = MD, h = MH);
      for (s = [-1, 1]) translate([s * 22, 4, MH - 4]) rotate([0, s * 20, 0]) cylinder(r1 = 7, r2 = 1, h = 18);   // chifrinhos
      for (s = [-1, 1]) translate([s * (MD / 2 - 2), 0, 36]) rotate([0, s * 70, 0]) scale([1, 0.8, 1]) cylinder(r1 = 6, r2 = 3, h = 10); // bracinhos
    }
    translate([0, 0, 2.4]) cylinder(d = MD - 5, h = MH);
    for (c = [2, 3]) monstrinho_det(c);
  }
}

// ---------------- PORTA-CHAVES RÚNICO (de parede) ----------------
module porta_chaves_runa(cor) {
  W = 170; H = 70;
  module placa2d() { offset(r = 3) polygon([[10, 0], [W - 10, 0], [W, 10], [W, H - 10], [W - 10, H], [10, H], [0, H - 10], [0, 10]]); }
  if (cor == 1) {
    difference() {
      linear_extrude(5) placa2d();
      for (x = [14, W - 14]) translate([x, H - 14, -1]) { cylinder(d = 4, h = 7); translate([0, 0, 3.8]) cylinder(d1 = 4, d2 = 8, h = 2.21); }
    }
    for (k = [0:3]) translate([30 + k * 37, 14, 4.99]) {      // ganchos em forma de garra
      hull() { cylinder(d = 7, h = 2); translate([0, 0, 14]) sphere(d = 6); }
      translate([0, 0, 14]) hull() { sphere(d = 6); translate([0, 6, 3]) sphere(d = 4.6); }
    }
  }
  if (cor == 2) translate([0, 0, 4.99]) linear_extrude(1.2) {
    difference() { offset(r = -4) placa2d(); offset(r = -5.4) placa2d(); }
    translate([W / 2, H - 22]) text("CHAVES", size = 12, font = FONTE, halign = "center", valign = "center");
    for (x = [30, W - 30]) translate([x, H - 22]) sigilo2d(8);
  }
}

// ---------------- VASO TORCIDO (flores secas, artificiais ou vaso para plantinha com pote dentro) ----------------
module vaso() {
  module perfil(r) { offset(r = 2) polygon([for (k = [0:15]) let(rr = k % 2 ? r * 0.86 : r, a = k * 22.5) [rr * cos(a), rr * sin(a)]]); }
  Hv = 130;
  difference() {
    linear_extrude(Hv, twist = 90, slices = 60, scale = 1.25) perfil(38);
    translate([0, 0, 2.4]) linear_extrude(Hv, twist = 90 * (Hv - 2.4) / Hv, slices = 60, scale = 1.25) perfil(35.6);
  }
}

// ---------------- PORTA-COPOS (jogo com 4) ----------------
module porta_copo(cor, k = 0) {
  D = 96;
  if (cor == 1) difference() { cylinder(d = D, h = 4.6); translate([0, 0, 4]) cylinder(d = D - 6, h = 2); }
  if (cor == 2) translate([0, 0, 3.99]) linear_extrude(0.61) intersection() {
    circle(d = D - 8);
    if (k % 2 == 0) for (a = [0:30:330]) rotate(a) translate([0, 22]) scale([1, 2.2]) circle(r = 5.4);       // flor
    else for (r = [8:7:44]) difference() { circle(r = r + 1.4); circle(r = r); }                            // ondas
  }
}
module porta_copos(cor) { for (k = [0:2]) translate([k * 60 - 60, (k % 2) * 30, k * 4.7]) rotate(k * 25) porta_copo(cor, k); }

// ---------------- GATINHO SUPORTE DE CELULAR ----------------
GW = 80;
module gatinho_det(cor) {
  for (s = [-1, 1]) translate([s * 14, 28, 76]) rotate([90 - 20, 0, 0]) {     // olhos no encosto inclinado
    if (cor == 3) scale([1, 1.15, 0.5]) sphere(r = 6.4);
    if (cor == 2) translate([0, -1, 2.2]) scale([0.8, 1.1, 0.5]) sphere(r = 4);
    if (cor == 3) translate([1.6, 0.6, 3.6]) sphere(r = 1.1);
  }
  if (cor == 4) translate([0, 26.2, 66]) rotate([90 - 20, 0, 0]) scale([1.3, 0.9, 0.5]) sphere(r = 2.6);                 // nariz
  if (cor == 4) for (s = [-1, 1]) translate([s * 24, 26.6, 67]) rotate([90 - 20, 0, 0]) scale([1.4, 0.9, 0.3]) sphere(r = 3.4); // bochechas
  if (cor == 2) for (s = [-1, 1]) translate([s * 4, 25.6, 63]) rotate([90 - 20, 0, 0]) rotate_extrude(angle = 180) translate([3, 0]) circle(r = 0.8); // boquinha
}
module gatinho_corpo() {
  difference() {
    union() {
      hull() for (x = [-GW / 2 + 8, GW / 2 - 8], y = [-30, 32]) translate([x, y, 0]) cylinder(r = 8, h = 6);   // base
      translate([0, -26, 0]) hull() for (x = [-GW / 2 + 8, GW / 2 - 8]) translate([x, 0, 0]) cylinder(r = 4, h = 16); // aba da frente (segura o celular)
      translate([0, 18, 0]) rotate([-20, 0, 0]) hull() for (x = [-GW / 2 + 12, GW / 2 - 12], z = [10, 82]) translate([x, 0, z]) rotate([90, 0, 0]) cylinder(r = 12, h = 8, center = true); // encosto (cabeça)
      for (s = [-1, 1]) translate([s * 26, 18, 0]) rotate([-20, 0, 0]) translate([0, 0, 88]) rotate([0, s * 20, 0]) scale([1, 0.4, 1]) cylinder(r1 = 12, r2 = 1.5, h = 20); // orelhas
      translate([GW / 2 - 6, 30, 3]) rotate([0, 90, 0]) rotate_extrude(angle = 200) translate([16, 0]) circle(r = 3.5);      // rabinho
    }
    translate([0, -12, 6]) rotate([0, 90, 0]) cylinder(r = 3, h = GW + 2, center = true);   // canal do cabo
    translate([0, 0, -20]) cube([200, 200, 40], center = true);
    for (c = [2, 3, 4]) gatinho_det(c);
  }
}

module peca(n, c) {
  if (n == "lanterna" && c == 1) lanterna();
  if (n == "monstrinho") { if (c == 1) monstrinho_corpo(); else monstrinho_det(c); }
  if (n == "porta_chaves_runa") porta_chaves_runa(c);
  if (n == "vaso" && c == 1) vaso();
  if (n == "porta_copos") porta_copos(c);
  if (n == "gatinho") { if (c == 1) gatinho_corpo(); else gatinho_det(c); }
}
for (n = ["lanterna", "monstrinho", "porta_chaves_runa", "vaso", "porta_copos", "gatinho"], c = [1:4])
  if (PARTE == str(n, "_c", c)) peca(n, c);
