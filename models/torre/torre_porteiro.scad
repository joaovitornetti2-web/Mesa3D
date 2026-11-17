// Torre de dados – Torre do Porteiro de Santo Berço (O Segredo na Floresta) – uso pessoal.
// PARTE: bandeja | torre | telhado | sino | emblema_base | emblema_espiral | lapide_base | lapide_texto | montado
include <morte_params.scad>
PARTE = "montado";
$fn = 48;

// ---------- medidas (mm) ----------
B = 150; BH = 18; BW = 4; BF = 3;          // bandeja
T = 70; TW = 5; TH = 130;                  // torre (externo, parede, altura)
TI = T - 2 * TW;                           // canal interno 60
TX = (B - T) / 2; TY = B - BW - 1 - T;     // posição da torre na bandeja (fundo, centro)
FOLGA = 0.3;
ARCO_W = 40; ARCO_H = 38;                  // porta de saída
JAN_Z = 98; JAN_H = 30; JAN_W = 32;       // janelas do campanário (entrada dos dados)
DECK = 80; DECK_H = 6;

// ---------- utilitários ----------
module pedras_face(w, h, alt = 9, larg = 16, prof = 0.8) {
  // sulcos de pedra numa face (plano XZ, normal -Y), para subtrair
  for (j = [0:floor(h / alt)]) {
    translate([-1, -0.01, j * alt]) cube([w + 2, prof, 0.8]);
    off = (j % 2) * larg / 2;
    for (i = [0:floor(w / larg) + 1]) translate([i * larg - off, -0.01, j * alt]) cube([0.8, prof, alt]);
  }
}
module arco2d(w, h) { translate([-w / 2, 0]) square([w, h - w / 2]); translate([0, h - w / 2]) circle(d = w); }
module escorrido(comp, larg = 4) {   // gota de Lodo descendo pela parede (relevo, normal -Y)
  hull() { translate([-larg / 2, -1.4, -0.5]) cube([larg, 1.4, 0.5]); translate([0, -0.7, -comp]) sphere(d = larg * 0.7, $fn = 16); }
  translate([0, -0.9, -comp - larg * 0.35]) sphere(d = larg * 0.9, $fn = 16);
}

// ---------- TORRE ----------
module torre() {
  difference() {
    union() {
      cube([T, T, TH]);
      // faixa de madeira na base do campanário e no topo
      for (z = [JAN_Z - 6, TH - 4]) translate([-1.2, -1.2, z]) cube([T + 2.4, T + 2.4, 4]);
      // rodapé de pedra
      translate([-1.5, -1.5, 0]) cube([T + 3, T + 3, 8]);
    }
    translate([TW, TW, -1]) cube([TI, TI, TH + 2]);                 // canal
    // porta de saída na frente
    translate([T / 2, TW + 1, 0]) rotate([90, 0, 0]) linear_extrude(TW + 4) translate([0, -1]) arco2d(ARCO_W, ARCO_H + 1);
    // janelas do campanário nos 4 lados
    for (r = [0, 90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([0, -T / 2 + TW + 1, JAN_Z]) rotate([90, 0, 0]) linear_extrude(TW + 4) arco2d(JAN_W, JAN_H);
    // pedras nas 4 faces
    for (r = [0, 90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([-T / 2, -T / 2, 8]) pedras_face(T, JAN_Z - 16);
    // rebaixo da placa do Thiago Fritz (parede de trás)
    translate([T / 2, T - 1.5, 18]) rotate([90, 0, 180]) translate([0, 0, -0.01]) linear_extrude(3) ogiva(35.2, 59.6);
    // rebaixo do emblema da Morte (frente, acima da porta)
    translate([T / 2, 1.6, 70]) rotate([90, 0, 0]) cylinder(d = 30.4, h = 3);
  }
  // rampa 1: parede da frente, alta
  rampa(TW, 100, 1);
  // rampa 2: parede do fundo, meio
  rampa(T - TW, 76, -1);
  // piso inclinado: do fundo (z=40) até a porta (z=1.5)
  hull() {
    translate([TW, TW, 0]) cube([TI, 0.1, 1.5]);
    translate([TW, T - TW - 0.1, 0]) cube([TI, 0.1, 40]);
  }
  // Lodo escorrendo do topo
  for (r = [0, 90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([0, -T / 2 - 1.2, TH - 4])
    for (d = [[-28, 14], [-19, 26], [-9, 9], [3, 19], [13, 31], [24, 12]]) if (!(r == 0 && abs(d[0]) < 22)) translate([d[0] + r / 30, 0, 0]) escorrido(d[1]);
  // Lodo escorrendo das janelas
  for (r = [90, 180, 270]) translate([T / 2, T / 2, 0]) rotate(r) translate([0, -T / 2 - 0.1, JAN_Z - 6])
    for (d = [[-14, 18], [-4, 30], [8, 14], [16, 24]]) translate([d[0], 0, 0]) escorrido(d[1], 3.4);
}
module ogiva(w, h) {   // mesmo arco ogival das placas (r = 0.6 w)
  r = 0.6 * w; off = r - w / 2; ha = sqrt(r * r - off * off);
  translate([-w / 2, 0]) square([w, h - ha]);
  translate([0, h - ha]) intersection() { translate([off, 0]) circle(r = r, $fn = 96); translate([-off, 0]) circle(r = r, $fn = 96); translate([-w / 2, 0]) square([w, ha]); }
}
// rampa: de uma parede (y0) a 26 mm para dentro, descendo 31 mm (50°)
module rampa(y0, z0, s) {
  hull() {
    translate([TW, y0 - (s > 0 ? 0 : 0.1), z0 - 4]) cube([TI, 0.1, 4]);
    translate([TW, y0 + s * 26 - (s > 0 ? 0.1 : 0), z0 - 31 - 3]) cube([TI, 0.1, 3]);
  }
}

// ---------- BANDEJA ----------
module bandeja() {
  difference() {
    union() {
      cube([B, B, BH]);
    }
    translate([BW, BW, BF]) cube([B - 2 * BW, B - 2 * BW, BH]);
    for (r = [0, 90, 180, 270]) translate([B / 2, B / 2, 0]) rotate(r) translate([-B / 2, -B / 2, 2]) pedras_face(B, BH - 4, 6, 18);
    // encaixe do pino da lápide (canto frontal esquerdo)
    translate([26 - 6.3, 26 - 2.3, BF - 2]) cube([12.6, 4.6, 3]);
    // gravura do Labirinto Infinito no fundo da bandeja (sulco)
    translate([B / 2, 55, BF - 0.8]) linear_extrude(1) labirinto(22);
  }
  // moldura de encaixe da torre (2 mm de altura)
  translate([TX - FOLGA - 2, TY - FOLGA - 2, BF]) difference() {
    cube([T + 2 * FOLGA + 4, T + 2 * FOLGA + 4, 2]);
    translate([2, 2, -1]) cube([T + 2 * FOLGA, T + 2 * FOLGA, 4]);
    translate([(T + 4) / 2 - ARCO_W / 2 - 3, -1, -1]) cube([ARCO_W + 6, 4, 4]);   // abertura da frente
  }
}
module labirinto(r) {   // labirinto circular estilizado (anéis com aberturas)
  for (k = [0:3]) let(rr = r - k * 5) difference() {
    circle(r = rr); circle(r = rr - 1.2);
    rotate(k * 97) translate([0, rr - 3]) square([4, 8], center = true);
  }
  for (k = [0:2]) rotate(k * 120 + 40) translate([0, r - 12]) square([1.2, 5], center = true);
}

// ---------- TELHADO / PLATAFORMA ----------
module telhado() {
  difference() {
    union() {
      translate([-(DECK - T) / 2, -(DECK - T) / 2, 0]) cube([DECK, DECK, DECK_H]);
      // ameias (menos na frente, onde o Deus da Morte apoia os braços)
      for (s = [1, 2, 3]) translate([T / 2, T / 2, 0]) rotate(s * 90) for (i = [-2:2]) translate([i * 15 - 4 + 0.37 * s, -DECK / 2, DECK_H - 0.01]) cube([8, 6, 7]);
      // campanário do sino (fundo)
      translate([T / 2, T - 6, DECK_H - 0.01]) {
        for (x = [-15, 11]) translate([x, -3, 0]) cube([4, 6, 30]);
        translate([-17, -3.5, 28]) cube([34, 7, 5]);
        translate([0, 0, 33]) rotate([90, 0, 0]) linear_extrude(7, center = true) polygon([[-17, 0], [17, 0], [0, 9]]);
      }
    }
    // telhas (sulcos) no topo do deck
    for (i = [0:7]) translate([-(DECK - T) / 2 - 1, -(DECK - T) / 2 + 4 + i * 10, DECK_H - 0.6]) cube([DECK + 2, 0.8, 1]);
    translate([T / 2, T - 6, DECK_H + 24]) cylinder(d = 2.2, h = 6);   // furo do gancho do sino
  }
  // lábio que entra no topo da torre
  translate([TW + FOLGA, TW + FOLGA, -4]) difference() { cube([TI - 2 * FOLGA, TI - 2 * FOLGA, 4.01]); translate([2.5, 2.5, -1]) cube([TI - 2 * FOLGA - 5, TI - 2 * FOLGA - 5, 6]); }
}
module sino() {
  rotate_extrude($fn = 64) polygon([[0, 0], [7, 0], [6.6, 1.2], [5, 3], [4.2, 9], [3.2, 12], [0, 13]]);
  translate([0, 0, 12.5]) cylinder(d = 2, h = 5);
}

// ---------- EMBLEMA (espiral da Morte) ----------
module espiral2d() { s = 12.8 / MORTE_R; scale(s) translate(-MORTE_C) import("/home/user/Mesa3D/models/decoracao/simbolos/morte.svg"); }
module emblema_base() { cylinder(d = 30, h = 1.8, $fn = 96); }
module emblema_espiral() { translate([0, 0, 1.8 - 0.01]) linear_extrude(0.81) offset(r = 0.15) espiral2d(); }

// ---------- LÁPIDE do Thiago ----------
module lapide2d() {
  difference() {
    union() { translate([-16, 0]) square([32, 32]); translate([0, 32]) scale([1, 0.55]) circle(r = 16, $fn = 96); }
    translate([16, 34]) rotate(28) square([14, 30], center = true);   // canto quebrado
  }
}
module lapide_base() {
  linear_extrude(6) lapide2d();
  translate([-6, -2.5, 1]) cube([12, 3, 4]);   // pino (encaixa na bandeja)
}
module chama2d() {
  hull() { translate([0, 0]) circle(d = 5.5, $fn = 32); translate([0.6, 9]) circle(d = 0.8, $fn = 12); }
  translate([-1.8, 2.5]) hull() { circle(d = 2.6, $fn = 24); translate([-1.2, 4.6]) circle(d = 0.6, $fn = 12); }
}
module lapide_texto() {
  translate([0, 0, 5.99]) linear_extrude(0.81) {
    translate([0, 33]) chama2d();
    translate([0, 22]) text("THIAGO", size = 5.2, halign = "center", font = "Liberation Serif:style=Bold");
    translate([0, 14.5]) text("FRITZ", size = 5.2, halign = "center", font = "Liberation Serif:style=Bold");
    translate([-12, 10.5]) square([24, 0.9]);
  }
}

if (PARTE == "bandeja") bandeja();
if (PARTE == "torre") torre();
if (PARTE == "telhado") telhado();
if (PARTE == "sino") sino();
if (PARTE == "emblema_base") emblema_base();
if (PARTE == "emblema_espiral") emblema_espiral();
if (PARTE == "lapide_base") lapide_base();
if (PARTE == "lapide_texto") lapide_texto();
if (PARTE == "montado") {
  color("#1a1a1a") bandeja();
  color("#1a1a1a") translate([TX, TY, BF]) torre();
  color("#1a1a1a") translate([TX, TY, BF + TH]) telhado();
  color("#eeeeee") translate([TX + T / 2, TY + T - 6, BF + TH + DECK_H + 10]) sino();
  translate([TX + T / 2, TY - 0.1, BF + 70]) rotate([90, 0, 0]) { color("#1a1a1a") emblema_base(); color("#c0141c") emblema_espiral(); }
  translate([26, 26, BF - 2]) rotate([90, 0, 0]) translate([0, 2.5, -3]) { color("#eeeeee") lapide_base(); color("#c0141c") lapide_texto(); }
}
