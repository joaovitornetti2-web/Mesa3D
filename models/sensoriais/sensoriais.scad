// Brinquedos sensoriais do Ateliê do Mestre – desenho próprio, estilo rúnico.
// PARTE: s_spinner | s_spinner_tampa | s_pedra | s_pedra_c2 | s_pedra_c4 | s_serpente | s_serpente_c2 | s_serpente_c3 | s_serpente_c4 | s_dado | s_anel | s_piao | s_piao_haste | s_d20
// (nomes com s_ porque o kit incluído também lê PARTE). Cone espiral: cone_espiral.py.
include <../kit/kit_rpg.scad>
PARTE = "s_spinner";
TEMA = "paranormal";
FOLGA_PIP = 0.4;
DECOR = true;      // false: só a mecânica (a versão esculpida põe a decoração por cima)
ARO = 19;           // anel giratório: diâmetro interno (17 P, 19 M, 21 G)

// ---------------- SPINNER RÚNICO (rolamento 608: 22 × 8 × 7 mm) ----------------
SP_T = 7; SP_FURO = 22.15; SP_R = 31; SP_LOBO = 30;
module spinner2d() {
  for (a = [0:120:240]) hull() { circle(d = 30, $fn = 96); rotate(a) translate([SP_R, 0]) circle(d = SP_LOBO, $fn = 96); }
}
module spinner() {
  difference() {
    union() {
      translate([0, 0, 0.6]) linear_extrude(SP_T - 1.2) spinner2d();
      linear_extrude(0.6) offset(-0.6) spinner2d();
      translate([0, 0, SP_T - 0.6]) linear_extrude(0.6) offset(-0.6) spinner2d();
    }
    translate([0, 0, -1]) cylinder(d = SP_FURO, h = SP_T + 2, $fn = 96);
    for (a = [0:120:240]) rotate(a) translate([SP_R, 0, 0]) {
      translate([0, 0, -1]) cylinder(d = 15, h = SP_T + 2, $fn = 64);           // janela do lobo
      for (z = [SP_T - 0.6, -0.01]) translate([0, 0, z]) linear_extrude(0.61) difference() { circle(d = 24, $fn = 64); circle(d = 22.4, $fn = 64); }
    }
    for (z = [SP_T - 0.6, -0.01]) translate([0, 0, z]) linear_extrude(0.61)   // runas em volta do rolamento
      for (k = [0:11]) rotate(k * 30 + 15) translate([0, 14]) runa2d(k + 7, 2.2);
  }
}
module spinner_tampa() {   // 2 por spinner: botão que encaixa no furo de 8 mm do rolamento
  cylinder(d = 19, h = 1.6, $fn = 64);
  translate([0, 0, 1.59]) cylinder(d = 7.9, h = 3.2, $fn = 48);
  translate([0, 0, 1.59]) cylinder(d = 10.5, h = 0.6, $fn = 48);   // espaçador: só a pista interna encosta
}

// ---------------- PEDRA DE RUNAS (pedra de apertar) ----------------
module pedra() {
  difference() {
    intersection() {
      scale([28, 21, 11]) sphere(r = 1, $fn = 96);
      translate([-40, -40, -7]) cube([80, 80, 40]);           // base reta para imprimir
    }
    translate([0, 0, 15.5]) scale([1, 0.8, 1]) sphere(r = 12, $fn = 96);   // encaixe do polegar
    for (k = [0:13]) rotate(k * 360 / 14) translate([0, 0, 0]) {            // runas na encosta
      rotate([0, 0, 0]) translate([0, 0, 0]);
    }
  }
  // anel de runas em relevo em volta do encaixe
  intersection() {
    scale([28.4, 21.4, 11.4]) sphere(r = 1, $fn = 96);
    for (k = [0:13]) rotate(k * 360 / 14) translate([0, 16.5, -7]) linear_extrude(30) runa2d(k + 90, 3.4);
  }
}

// carinha da pedra: olhos fechados (cor 2) e bochechas (cor 4), na encosta da frente
function pedra_sup(x, z) = -21 * sqrt(max(0, 1 - (x / 28) * (x / 28) - (z / 11) * (z / 11)));
module pedra_det(cor) {
  if (cor == 2) for (s = [-1, 1]) for (t = [-70:14:70]) let(x = s * 8 + sin(t) * 3.4, z = 3.2 - (1 - cos(t)) * 1.6)
    translate([x, pedra_sup(x, z) + 0.15, z]) sphere(r = 0.75, $fn = 12);
  if (cor == 2) for (t = [-50:12:50]) let(x = sin(t) * 2.2, z = -0.6 - (1 - cos(t)) * 1.4) translate([x, pedra_sup(x, z) + 0.15, z]) sphere(r = 0.6, $fn = 12);
  if (cor == 4) for (s = [-1, 1]) let(x = s * 14, z = 1.2) translate([x, pedra_sup(x, z) + 0.4, z]) rotate([90, 0, 0]) scale([1.5, 0.9, 0.35]) sphere(r = 2.4, $fn = 24);
}

// ---------------- SERPENTE ARTICULADA (impressa já montada, pinos verticais, curva em S) ----------------
SG_N = 12; SG_W = 16; SG_H = 9; SG_L = 18; SG_RP = 4; SG_PINO = 3.2; G = FOLGA_PIP;
function sg_ang(i) = 28 * sin(i * 55);
function sg_dir(t) = [cos(t), sin(t)];
// lista de [centro, junta de trás, ângulo] de cada segmento (cabeça em i = 0)
function sg_lista(i = 0, c = [0, 0], acc = []) =
  i >= SG_N ? acc :
  let(t = sg_ang(i), j = c - SG_L / 2 * sg_dir(t), prox = j - SG_L / 2 * sg_dir(sg_ang(i + 1)))
  sg_lista(i + 1, prox, concat(acc, [[c, j, t]]));
SGL = sg_lista();
module em(p, z0, h, r) { translate([p[0], p[1], z0]) cylinder(r = r, h = h, $fn = 40); }
module segmento_s(i) {
  c = SGL[i][0]; j = SGL[i][1]; jf = i > 0 ? SGL[i - 1][1] : [0, 0];
  t3 = SG_H / 3;
  difference() {
    union() {
      em(c, 0, SG_H, SG_W / 2);
      if (i < SG_N - 1) hull() { em(j, t3 + G, t3 - 2 * G, SG_RP); em(c, t3 + G, t3 - 2 * G, 2); }      // língua (meio) para trás
      if (i > 0) for (z = [0, 2 * t3]) hull() { em(jf, z, t3, SG_RP); em(c, z, t3, 2); }                // garfo (cima e baixo) para a frente
    }
    if (i < SG_N - 1) {
      em(j, -1, SG_H + 2, SG_PINO / 2 + G);                                                             // furo da língua
      for (z = [-1, 2 * t3 - G]) em(j, z, t3 + 1 + G, SG_RP + G);                                     // espaço do garfo do próximo
    }
    if (i > 0) em(jf, t3, t3, SG_RP + G);                                                               // espaço da língua do anterior
    if (DECOR) translate([c[0], c[1], SG_H - 0.6]) linear_extrude(1) rotate(SGL[i][2]) runa2d(i * 3 + 11, 7);   // runa no topo
    if (DECOR && i == 0) for (s = [-1, 1]) let(o = c + 4.5 * sg_dir(SGL[0][2]) + s * 3.5 * sg_dir(SGL[0][2] + 90))
      translate([o[0], o[1], SG_H - 1]) cylinder(d = 2.6, h = 2, $fn = 20);                            // olhos
  }
  if (i > 0) em(jf, 0, SG_H, SG_PINO / 2);                                                              // pino do garfo
}
module serpente() { for (i = [0:SG_N - 1]) segmento_s(i); }
// olhos (cor 3 + pupila cor 2) e linguinha bifurcada (cor 4) na cabeça
module serpente_det(cor) {
  c = SGL[0][0]; t = SGL[0][2]; d = sg_dir(t); n = sg_dir(t + 90);
  for (s = [-1, 1]) let(o = c + 4.5 * d + s * 3.5 * n) translate([o[0], o[1], SG_H - 1.4]) {
    if (cor == 3) scale([1, 1, 0.75]) sphere(r = 2.6, $fn = 24);
    if (cor == 2) translate([1.1 * d[0], 1.1 * d[1], 1.2]) sphere(r = 1.3, $fn = 16);
  }
  if (cor == 4) let(p = c + (SG_W / 2 - 1) * d) translate([p[0], p[1], 3.4]) rotate(t) {
    translate([0, -0.8, 0]) cube([6, 1.6, 1.6]);
    for (s = [-1, 1]) translate([6, 0, 0]) rotate(s * 30) translate([0, -0.6, 0]) cube([3.5, 1.2, 1.6]);
  }
}

// ---------------- DADO SENSORIAL (uma textura por face) ----------------
DD = 30;
module dado() {
  difference() {
    minkowski() { cube(DD - 6, center = true); sphere(r = 3, $fn = 24); }
    // topo: anéis concêntricos
    for (r = [4:3:13]) translate([0, 0, DD / 2 - 0.8]) difference() { cylinder(r = r + 0.6, h = 2, $fn = 64); cylinder(r = r - 0.6, h = 2, $fn = 64); }
    // frente: ondas
    for (z = [-10:3:10]) translate([0, -DD / 2 + 0.8, z]) rotate([90, 0, 0]) linear_extrude(2) translate([-12, -0.6]) square([24, 1.2]);
    // atrás: sigilo
    translate([0, DD / 2 - 0.8, 0]) rotate([-90, 0, 0]) linear_extrude(2) sigilo2d(11);
    // lado direito: grade de covinhas
    for (y = [-9:6:9], z = [-9:6:9]) translate([DD / 2 + 1.2, y, z]) sphere(r = 2.2, $fn = 20);
    // embaixo: 6 pontos rasos (face apoiada na mesa)
    for (x = [-7, 7], y = [-7, 0, 7]) translate([x, y, -DD / 2 - 0.2]) cylinder(d = 4, h = 1, $fn = 24);
  }
  // lado esquerdo: bolinhas em relevo
  for (y = [-9:6:9], z = [-9:6:9]) translate([-DD / 2 + 0.5, y, z]) intersection() { sphere(r = 1.8, $fn = 20); translate([-3, -3, -3]) cube([3.4, 6, 6]); }
}

// ---------------- ANEL GIRATÓRIO (impresso já montado) ----------------
AN_W = 10;
module anel() {
  ri = ARO / 2; e = 1.6; g = 0.35;
  rotate_extrude($fn = 128) polygon([   // aro interno com crista em V
    [ri, 0], [ri + e, 0], [ri + e, AN_W / 2 - 2.2], [ri + e + 2.2, AN_W / 2], [ri + e, AN_W / 2 + 2.2], [ri + e, AN_W], [ri, AN_W]]);
  difference() {   // faixa externa com canal em V, gira em volta da crista
    rotate_extrude($fn = 128) polygon([
      [ri + e + g, 0], [ri + e + 3.6, 0], [ri + e + 3.6, AN_W], [ri + e + g, AN_W],
      [ri + e + g, AN_W / 2 + 2.2 + g], [ri + e + 2.2 + g, AN_W / 2], [ri + e + g, AN_W / 2 - 2.2 - g]]);
    if (DECOR) for (k = [0:15]) rotate(k * 360 / 16) translate([ri + e + 3.6 - 0.5, 0, 1.6]) rotate([0, 90, 0]) linear_extrude(1) rotate(90) runa2d(k + 200, 3.6);
  }
}

// ---------------- PIÃO RÚNICO (corpo + haste encaixada) ----------------
module piao() {   // impresso com a face de cima na mesa e a ponta para o alto
  difference() {
    rotate_extrude($fn = 128) polygon([[0, 0], [21, 0], [22, 2], [21, 5], [12, 13], [3, 24], [0, 26]]);
    translate([0, 0, -1]) cylinder(d = 6.3, h = 9, $fn = 32);              // furo da haste
    translate([0, 0, -0.01]) linear_extrude(0.6) {                            // sigilo e runas na face de cima
      difference() { circle(r = 18, $fn = 96); circle(r = 17.2, $fn = 96); }
      for (k = [0:11]) rotate(k * 30) translate([0, 13.5]) runa2d(k + 300, 2.6);
    }
  }
}
module piao_haste() { cylinder(d = 6.1, h = 8, $fn = 32); translate([0, 0, 7.99]) cylinder(d1 = 8, d2 = 7, h = 12, $fn = 32); }

// ---------------- CHAVEIRO D20 ----------------
module d20(r = 13) {
  t = (1 + sqrt(5)) / 2;
  v = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]];
  hull() for (p = v) translate(p * r / norm([1, t, 0])) sphere(r = 0.6, $fn = 8);
}
module chaveiro_d20() {
  difference() {
    union() {
      d20();
      translate([0, 0, 12]) rotate([90, 0, 0]) rotate_extrude($fn = 48) translate([4.5, 0]) circle(d = 3, $fn = 24);   // argola
    }
  }
}

if (PARTE == "s_spinner") spinner();
if (PARTE == "s_spinner_tampa") spinner_tampa();
if (PARTE == "s_pedra") difference() { pedra(); pedra_det(2); pedra_det(4); }
if (PARTE == "s_pedra_c2") pedra_det(2);
if (PARTE == "s_pedra_c4") pedra_det(4);
if (PARTE == "s_serpente") difference() { serpente(); serpente_det(2); serpente_det(3); }
if (PARTE == "s_serpente_par") for (i = [0:2:SG_N - 1]) segmento_s(i);
if (PARTE == "s_serpente_impar") for (i = [1:2:SG_N - 1]) segmento_s(i);
if (PARTE == "s_serpente_c2") serpente_det(2);
if (PARTE == "s_serpente_c3") serpente_det(3);
if (PARTE == "s_serpente_c4") serpente_det(4);
if (PARTE == "s_dado") dado();
if (PARTE == "s_anel") anel();
if (PARTE == "s_piao") piao();
if (PARTE == "s_piao_haste") piao_haste();
if (PARTE == "s_d20") chaveiro_d20();
