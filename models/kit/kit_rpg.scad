// Kit RPG Mesa3D – peças funcionais (design próprio, pode vender).
// Torre de dados desmontável (bandeja + torre + telhado + sino + brasão) e anéis de condição.
// PARTE: bandeja | torre | telhado | sino | brasao_base | brasao_d20 | anel_base | anel_texto | aneis_base | aneis_texto | montado
PARTE = "montado";
TEMA = "fantasia";   // fantasia (d20, condições clássicas) | paranormal (sigilo original, condições de horror)
ANEL = 0;          // índice da condição (0..7) para anel_base/anel_texto
$fn = 48;

// ---------- medidas (mm) ----------
B = 150; BH = 18; BW = 4; BF = 3;          // bandeja 15×15
T = 70; TW = 5; TH = 130;                  // torre (externo, parede, altura)
TI = T - 2 * TW;                           // canal interno 60
TX = (B - T) / 2; TY = B - BW - 1 - T;     // torre ao fundo, centralizada
FOLGA = 0.3;
ARCO_W = 40; ARCO_H = 38;                  // porta de saída (cabe d20 de 26 mm com folga)
JAN_Z = 98; JAN_H = 30; JAN_W = 32;        // janelas do campanário (entrada dos dados)
DECK = 80; DECK_H = 6;

// ---------- utilitários ----------
module pedras_face(w, h, alt = 9, larg = 16, prof = 0.8) {
  for (j = [0:floor(h / alt)]) {
    translate([-1, -0.01, j * alt]) cube([w + 2, prof, 0.8]);
    off = (j % 2) * larg / 2;
    for (i = [0:floor(w / larg) + 1]) translate([i * larg - off, -0.01, j * alt]) cube([0.8, prof, alt]);
  }
}
module arco2d(w, h) { translate([-w / 2, 0]) square([w, h - w / 2]); translate([0, h - w / 2]) circle(d = w); }
module seteira(h) { hull() { translate([0, -0.01, 0]) cube([2.4, 3, 0.01], center = true); translate([0, -0.01, h]) rotate([90, 0, 0]) cylinder(d = 2.4, h = 3, center = true); } }
module hera(comp) {   // ramo de hera em relevo descendo pela parede (normal -Y)
  for (k = [0:floor(comp / 6)]) translate([sin(k * 70) * 2.5, -0.6, -k * 6]) {
    rotate([90, 0, 0]) cylinder(d = 1.6, h = 1.2, center = true);
    translate([(k % 2 ? 2.2 : -2.2), 0, -1.5]) rotate([90, 0, k * 40]) scale([1, 0.65, 1]) cylinder(d = 4.2, h = 1.2, center = true, $fn = 6);
  }
}
module d20_2d(r) {   // ícone de d20 (hexágono com triângulo central), contorno
  difference() { circle(r = r, $fn = 6); circle(r = r - 1.4, $fn = 6); }
  pts = [for (a = [90, 210, 330]) [cos(a), sin(a)] * r * 0.55];
  difference() { polygon(pts); offset(delta = -1.2) polygon(pts); }
  for (i = [0:2]) hull() { translate(pts[i]) circle(d = 1.2, $fn = 12); translate([cos(90 + i * 120 - 60), sin(90 + i * 120 - 60)] * (r - 0.8) * 0.98) circle(d = 1.2, $fn = 12); }
  for (i = [0:2]) hull() { translate(pts[i]) circle(d = 1.2, $fn = 12); translate([cos(90 + i * 120), sin(90 + i * 120)] * (r - 0.8)) circle(d = 1.2, $fn = 12); }
}

// ---------- TORRE ----------
module torre() {
  difference() {
    union() {
      cube([T, T, TH]);
      for (z = [JAN_Z - 6, TH - 4]) translate([-1.2, -1.2, z]) cube([T + 2.4, T + 2.4, 4]);   // faixas de madeira
      translate([-1.5, -1.5, 0]) cube([T + 3, T + 3, 8]);                                    // rodapé
      for (x = [0, T], y = [0, T]) translate([x, y, 0]) cylinder(d = 9, h = JAN_Z - 6, $fn = 8);   // contrafortes nos cantos
    }
    translate([TW, TW, -1]) cube([TI, TI, TH + 2]);
    translate([T / 2, TW + 1, 0]) rotate([90, 0, 0]) linear_extrude(TW + 4) translate([0, -1]) arco2d(ARCO_W, ARCO_H + 1);
    for (r = [0, 90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([0, -T / 2 + TW + 1, JAN_Z]) rotate([90, 0, 0]) linear_extrude(TW + 4) arco2d(JAN_W, JAN_H);
    for (r = [0, 90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([-T / 2, -T / 2, 8]) pedras_face(T, JAN_Z - 16);
    for (r = [90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([0, -T / 2 + 0.6, 50]) seteira(16);   // seteiras falsas
    translate([T / 2, 1.6, 70]) rotate([90, 0, 0]) linear_extrude(3) offset(delta = FOLGA) brasao2d();   // rebaixo do brasão
  }
  rampa(TW, 100, 1);
  rampa(T - TW, 76, -1);
  hull() { translate([TW, TW, 0]) cube([TI, 0.1, 1.5]); translate([TW, T - TW - 0.1, 0]) cube([TI, 0.1, 40]); }
}
module rampa(y0, z0, s) {   // de uma parede a 26 mm para dentro, descendo 31 mm (50°): sem suporte
  hull() {
    translate([TW, y0 - (s > 0 ? 0 : 0.1), z0 - 4]) cube([TI, 0.1, 4]);
    translate([TW, y0 + s * 26 - (s > 0 ? 0.1 : 0), z0 - 31 - 3]) cube([TI, 0.1, 3]);
  }
}

// ---------- BRASÃO (escudo com d20, encaixa na frente da torre) ----------
module brasao2d() { hull() { translate([-14, 6]) square([28, 14]); translate([0, -12]) circle(d = 4); } }
module brasao_base() { linear_extrude(2.6) brasao2d(); }
module brasao_d20() { translate([0, 4, 2.59]) linear_extrude(0.8) icone2d(9); }
// sigilo ORIGINAL (não é símbolo de nenhum jogo): anel quebrado, losango central, raios e marcas
module sigilo2d(r) {
  difference() { circle(r = r, $fn = 64); circle(r = r - max(0.9, r * 0.1), $fn = 64); for (a = [45:90:315]) rotate(a) translate([0, r * 0.9]) square([r * 0.22, r * 0.4], center = true); }
  for (a = [45:90:315]) rotate(a) translate([0, r * 0.9]) circle(d = max(1, r * 0.13), $fn = 12);
  difference() { circle(r = r * 0.62, $fn = 4); circle(r = r * 0.62 - max(0.9, r * 0.1), $fn = 4); }
  circle(r = r * 0.14, $fn = 24);
  for (a = [0:90:270]) rotate(a) translate([-max(0.45, r * 0.045), r * 0.62]) square([max(0.9, r * 0.09), r * 0.26]);
  for (a = [0:30:330]) if (a % 90 != 0 && a % 45 != 0) rotate(a) translate([-max(0.4, r * 0.035), r * 0.7]) square([max(0.8, r * 0.07), r * 0.12]);
}
module icone2d(r) { if (TEMA == "paranormal") sigilo2d(r); else d20_2d(r); }

// ---------- BANDEJA ----------
module bandeja() {
  difference() {
    cube([B, B, BH]);
    translate([BW, BW, BF]) cube([B - 2 * BW, B - 2 * BW, BH]);
    for (r = [0, 90, 180, 270]) translate([B / 2, B / 2, 0]) rotate(r) translate([-B / 2, -B / 2, 2]) pedras_face(B, BH - 4, 6, 18);
    translate([B / 2, 42, BF - 0.8]) linear_extrude(1) icone2d(20);   // ícone gravado onde os dados param
  }
  translate([TX - FOLGA - 2, TY - FOLGA - 2, BF]) difference() {   // moldura de encaixe da torre
    cube([T + 2 * FOLGA + 4, T + 2 * FOLGA + 4, 2]);
    translate([2, 2, -1]) cube([T + 2 * FOLGA, T + 2 * FOLGA, 4]);
    translate([(T + 4) / 2 - ARCO_W / 2 - 3, -1, -1]) cube([ARCO_W + 6, 4, 4]);
  }
}

// ---------- TELHADO ----------
module telhado() {
  difference() {
    union() {
      translate([-(DECK - T) / 2, -(DECK - T) / 2, 0]) cube([DECK, DECK, DECK_H]);
      for (s = [0, 1, 2, 3]) translate([T / 2, T / 2, 0]) rotate(s * 90) for (i = [-2:2]) translate([i * 15 - 4 + 0.37 * s, -DECK / 2, DECK_H - 0.01]) cube([8, 6, 7]);
      translate([T / 2, T / 2, DECK_H - 0.01]) {   // campanário central com telhado de 4 águas
        for (x = [-15, 11], y = [-15, 11]) translate([x, y, 0]) cube([4, 4, 26]);
        translate([-17, -17, 26]) cube([34, 34, 4]);
        translate([0, 0, 30]) cylinder(d1 = 50, d2 = 0, h = 24, $fn = 4);
        translate([0, 0, 52]) cylinder(d = 1.6, h = 8);   // mastro
        translate([0, 0.8, 55]) rotate([90, 0, 0]) linear_extrude(1.6) polygon([[0, 0], [10, 2], [0, 5]]);   // flâmula
      }
    }
    for (i = [0:7]) translate([-(DECK - T) / 2 - 1, -(DECK - T) / 2 + 4 + i * 10, DECK_H - 0.6]) cube([DECK + 2, 0.8, 1]);
    translate([T / 2, T / 2, DECK_H + 20]) cylinder(d = 2.2, h = 12);   // furo do gancho do sino
  }
  translate([TW + FOLGA, TW + FOLGA, -4]) difference() { cube([TI - 2 * FOLGA, TI - 2 * FOLGA, 4.01]); translate([2.5, 2.5, -1]) cube([TI - 2 * FOLGA - 5, TI - 2 * FOLGA - 5, 6]); }
}
module sino() {
  rotate_extrude($fn = 64) polygon([[0, 0], [7, 0], [6.6, 1.2], [5, 3], [4.2, 9], [3.2, 12], [0, 13]]);
  translate([0, 0, 12.5]) cylinder(d = 2, h = 5);
}

// ---------- ANÉIS DE CONDIÇÃO (base de 25 mm) ----------
CONDICOES = TEMA == "paranormal" ? ["MORRENDO", "SANGRANDO", "ABALADO", "APAVORADO", "CAÍDO", "CEGO", "ATORDOADO", "ENLOUQUECENDO"]
  : ["CAÍDO", "ATORDOADO", "CEGO", "ENVENENADO", "AGARRADO", "AMEDRONTADO", "INVISÍVEL", "PARALISADO"];
A_ID = 25.8; A_OD = 37; A_H = 2.4;
module anel_base() {
  if (TEMA == "paranormal")
    difference() {   // borda chanfrada e dois sulcos finos acompanhando o anel
      rotate_extrude($fn = 128) polygon([[A_ID / 2, 0], [A_OD / 2 - 0.6, 0], [A_OD / 2, 0.6], [A_OD / 2, A_H - 0.7], [A_OD / 2 - 0.7, A_H], [A_ID / 2 + 0.5, A_H], [A_ID / 2, A_H - 0.5]]);
      for (rr = [A_ID / 2 + 1.1, A_OD / 2 - 1.3]) translate([0, 0, A_H - 0.4]) rotate_extrude($fn = 128) translate([rr, 0]) square([0.45, 1]);
    }
  else difference() { cylinder(d = A_OD, h = A_H, $fn = 96); translate([0, 0, -1]) cylinder(d = A_ID, h = A_H + 2, $fn = 96); }
}
// runa original: 2-3 traços sorteados (semente fixa por índice)
module runa2d(k, t = 2.4) {
  v = rands(-1, 1, 12, k * 7 + 3);
  for (j = [0:2]) if (j < 2 || v[11] > 0) hull() { translate([v[j * 4] * t / 2, v[j * 4 + 1] * t / 2]) circle(d = 0.6, $fn = 8); translate([v[j * 4 + 2] * t / 2, v[j * 4 + 3] * t / 2]) circle(d = 0.6, $fn = 8); }
}
function larg_letra(c) = (c == "I" || c == "Í") ? 0.42 : (c == "M" || c == "W") ? 1.12 : (c == "C" || c == "D" || c == "G" || c == "O" || c == "N" || c == "A" || c == "V") ? 0.94 : 0.84;
function soma(v, n) = n <= 0 ? 0 : v[n - 1] + soma(v, n - 1);
module anel_texto(i = ANEL) {
  s = CONDICOES[i]; n = len(s); r = (A_ID + A_OD) / 4;
  w = [for (k = [0:n - 1]) larg_letra(s[k])];
  total = soma(w, n);
  grau = min(12.5 / 0.86, 205 / total);      // graus por unidade de largura
  translate([0, 0, A_H - 0.01]) linear_extrude(0.6) offset(delta = 0.01) {   // offset limpa o contorno 2D (evita malha aberta)
    for (k = [0:n - 1]) let(meio = soma(w, k) + w[k] / 2)
      rotate(90 + total * grau / 2 - meio * grau) translate([r, 0]) rotate(-90) text(s[k], size = 3.1, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
    if (TEMA == "paranormal") {   // runas em volta e sigilo embaixo
      rotate(-90) translate([r, 0]) rotate(90) sigilo2d(2.6);
      for (k = [0:9]) let(a = -90 + (k < 5 ? -1 : 1) * (18 + (k % 5) * 15)) rotate(a) translate([r, 0]) rotate(a + 90) runa2d(k + i * 10);
    } else
      for (a = [-90 - 34, -90, -90 + 34]) rotate(a) translate([r, 0]) circle(d = 1.6, $fn = 16);   // pontos decorativos embaixo
  }
}
module grade(f) { for (i = [0:7]) translate([(i % 4) * 42, floor(i / 4) * 42, 0]) f(i); }

if (PARTE == "bandeja") bandeja();
if (PARTE == "torre") torre();
if (PARTE == "telhado") telhado();
if (PARTE == "sino") sino();
if (PARTE == "brasao_base") brasao_base();
if (PARTE == "brasao_d20") brasao_d20();
if (PARTE == "anel_base") anel_base();
if (PARTE == "anel_texto") anel_texto();
if (PARTE == "aneis_base") for (i = [0:7]) translate([(i % 4) * 42, floor(i / 4) * 42, 0]) anel_base();
if (PARTE == "aneis_texto") for (i = [0:7]) translate([(i % 4) * 42, floor(i / 4) * 42, 0]) anel_texto(i);
if (PARTE == "montado") {
  color("#1a1a1a") bandeja();
  color("#1a1a1a") translate([TX, TY, BF]) torre();
  color("#1a1a1a") translate([TX, TY, BF + TH]) telhado();
  color("#eeeeee") translate([TX + T / 2, TY + T / 2, BF + TH + DECK_H + 7]) sino();
  translate([TX + T / 2, TY - 0.1, BF + 70]) rotate([90, 0, 0]) { color("#c0141c") brasao_base(); color("#eeeeee") brasao_d20(); }
  for (i = [0:2]) translate([25 + i * 40 + (i == 1 ? 0 : 0), 20, BF]) { color("#1a1a1a") anel_base(); color("#eeeeee") anel_texto(i); }
}
