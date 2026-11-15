// Relicário octogonal decorativo (guarda um jogo de dados) – Morte, Sangue e Medo.
// Selos e runas ORIGINAIS na estética de horror ocultista; não copiam sigilos oficiais.
//
// PARTE: "corpo" | "tampa" (rebaixo p/ 2ª cor) | "selo" (só a 2ª cor) | "tampa_simples" | "preview"
// "tampa"/"selo"/"tampa_simples" já saem na posição de impressão (selo apoiado na mesa).
include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>

ELEMENTO = "sangue";   // sangue | morte | medo
PARTE    = "preview";
// Símbolo próprio (uso pessoal): caminho de um SVG que substitui o motivo central.
// O build preenche sozinho se existir simbolos/<elemento>.svg (ou .png).
SIMBOLO_SVG = "";
SIMBOLO_CENTRO = [0, 0];   // calculado pelo build
SIMBOLO_ESCALA = 1;
$fn = 72;

// ---- medidas (mm) ----
F_CORPO  = 76;   // octógono, de face a face
F_INT    = 70;   // cavidade
F_PLINTO = 82;   // base
F_MOLD   = 80;   // moldura do topo
F_TAMPA  = 83;   // aba da tampa (1.5 mm além da moldura, para pegar)
F_TOPO   = 67;   // face de cima da tampa
H        = 34;   // altura do corpo
FUNDO    = 3;
LABIO    = 5;
INLAY    = 0.6;
TRACO    = 1.0;  // espessura mínima de linha (bico 0.4 -> 2 linhas e meia)

module oct(f) rotate(22.5) circle(d = f / cos(22.5), $fn = 8);
module linha(pts, w = TRACO) for (i = [0:len(pts) - 2]) hull() { translate(pts[i]) circle(d = w, $fn = 16); translate(pts[i + 1]) circle(d = w, $fn = 16); }
module anel(r, w) difference() { circle(r = r); circle(r = r - w); }

// ---------------- runas procedurais ----------------
// grade 3x4; um tronco vertical + 3 traços aleatórios, determinístico pela semente
module runa(seed, w = 3.6, h = 5.4) {
  P = [for (j = [0:3], i = [0:2]) [i * w / 2 - w / 2, j * h / 3 - h / 2]];
  r = rands(0, 11.999, 8, seed);
  col = floor(rands(0, 2.999, 1, seed + 7)[0]);
  linha([P[col], P[col + 9]]);
  for (k = [0:2]) let(a = floor(r[2 * k]), b = floor(r[2 * k + 1])) if (a != b) linha([P[a], P[b]]);
}
module anel_runas(n, r, seed, h = 5.0) {
  for (i = [0:n - 1]) rotate(-i * 360 / n) translate([0, r]) runa(seed + i * 13, w = h * 0.66, h = h);
}

// ---------------- motivos dos elementos (raio <= 20) ----------------
module gota(d = 6, alt = 1.2) hull() { circle(d = d); translate([0, d * alt]) circle(d = 0.9, $fn = 12); }

module motivo_sangue() {
  // gota central com reflexo vazado
  difference() {
    translate([0, -3]) gota(13, 1.05);
    intersection() {
      difference() { translate([0, -3.5]) circle(d = 9); translate([1.5, -2.2]) circle(d = 9); }
      translate([-10, -10]) square([10, 20]);
    }
  }
  // coroa de espinhos
  for (i = [0:11]) rotate(i * 30 + 15) polygon([[-1.5, 20], [1.5, 20], [0, 15.2]]);
  // veias
  for (v = [[195, 1], [235, -1], [305, 1], [345, -1]])
    let(a = v[0], s = v[1]) linha([for (t = [0:6]) let(rr = 8 + t * 1.15, aa = a + s * 5 * sin(t * 60)) [rr * cos(aa), rr * sin(aa)]]);
  for (p = [[-9, 9.5, 0.55], [9.5, 8.5, 0.45]]) translate([p[0], p[1]]) scale(p[2]) gota(6);
}

module motivo_morte() {
  // espiral do tempo
  linha([for (t = [0:5:3.25 * 360]) let(rr = 1.6 + t / 360 * 4.2) [rr * cos(-t + 90), rr * sin(-t + 90)]], 1.2);
  circle(d = 2.4);
  // mostrador
  for (i = [0:23]) rotate(i * 15) translate([-(i % 3 == 0 ? 0.7 : 0.5), i % 3 == 0 ? 16 : 17]) square([i % 3 == 0 ? 1.4 : 1.0, i % 3 == 0 ? 3.6 : 2.6]);
}

module motivo_medo() {
  // anel quebrado
  difference() { anel(19, 1.3); for (a = [12, 70, 101, 158, 214, 236, 300, 333]) rotate(a) translate([-1.1, 15]) square([2.2, 6]); }
  // estrela irregular vazada
  E = [for (i = [0:17]) let(a = i * 20, rr = (i % 2 == 0 ? 15 : 7) + (i % 4 == 0 ? 1.5 : 0) - (i % 6 == 1 ? 1 : 0)) [rr * sin(a), rr * cos(a)]];
  difference() { polygon(E); offset(delta = -1.2) polygon(E); }
  // olho
  difference() {
    intersection() { translate([0, -4]) circle(r = 7); translate([0, 4]) circle(r = 7); }
    intersection() { translate([0, -4]) circle(r = 5.8); translate([0, 4]) circle(r = 5.8); }
  }
  circle(r = 2.1);
}

module motivo(e) {
  if (SIMBOLO_SVG != "") scale(SIMBOLO_ESCALA) translate(-SIMBOLO_CENTRO) import(SIMBOLO_SVG);
  else if (e == "sangue") motivo_sangue(); else if (e == "morte") motivo_morte(); else motivo_medo(); }
function semente(e) = e == "sangue" ? 11 : e == "morte" ? 23 : 37;

// selo completo (2D, centrado). Cabe no octógono do topo (raio inscrito 33.5).
module selo2d(e) {
  anel(30, 1.4);
  anel_runas(18, 25.2, semente(e), 4.6);
  anel(21.7, 1.1);
  motivo(e);
  for (a = [22.5:45:359]) rotate(a) translate([0, 31.6]) polygon([[0, -0.6], [1.4, 1.2], [0, 3.2], [-1.4, 1.2]]);
}

// ---------------- painéis laterais (2D: x ao longo da face, y para cima) ----------------
PW = 24; PH = 19.5;
module painel2d(e, i) {
  s = semente(e) * 100 + i * 7;
  if (e == "sangue") {
    for (k = [0:2]) translate([(k - 1) * 7, 5]) runa(s + k, 4, 6);
    for (d = [[-10, 5], [-6.5, 8], [-3, 3.5], [1, 6.5], [4.5, 9], [8, 4.5], [10.5, 6]])
      hull() { translate([d[0] - 1, PH - 0.5]) square([2, 0.5]); translate([d[0], PH - d[1]]) circle(d = 2.2, $fn = 20); }
  } else if (e == "morte") {
    for (k = [0:2]) translate([(k - 1) * 7, 5]) runa(s + k, 4, 6);
    translate([-PW / 2 + 1, 10.5]) square([PW - 2, 1]);
    translate([0, 15]) linha([for (t = [0:10:2 * 360]) let(rr = 0.8 + t / 360 * 1.6) [rr * cos(t), rr * sin(t)]], 0.9);
    for (x = [-8, 8]) translate([x, 15]) circle(d = 2.2);
  } else {
    for (k = [0:2]) translate([(k - 1) * 7, 14.5]) runa(s + k, 4, 6);
    for (p = [[-10.5, 6], [-7.5, 9], [-4.5, 5], [-1.5, 10], [1.5, 7], [4.5, 9.5], [7.5, 5.5], [10.5, 8]])
      polygon([[p[0] - 1.4, 0], [p[0] + 1.4, 0], [p[0] + 0.2, p[1]]]);
  }
}

// ---------------- peças ----------------
Z0P = 8.5;   // início dos painéis
module corpo() {
  R = F_CORPO / 2;
  difference() {
    union() {
      linear_extrude(4) oct(F_PLINTO);
      translate([0, 0, 4]) hull() { linear_extrude(0.01) oct(F_PLINTO); translate([0, 0, 3]) linear_extrude(0.01) oct(F_CORPO); }
      linear_extrude(H) oct(F_CORPO);
      translate([0, 0, H - 5]) hull() { linear_extrude(0.01) oct(F_CORPO); translate([0, 0, 2]) linear_extrude(0.01) oct(F_MOLD); }
      translate([0, 0, H - 3]) linear_extrude(3) oct(F_MOLD);
    }
    translate([0, 0, FUNDO]) linear_extrude(H) oct(F_INT);
    for (i = [0:7]) rotate(i * 45) translate([R - 0.8, -PW / 2, Z0P]) cube([2, PW, PH]);
  }
  for (i = [0:7]) rotate(i * 45) translate([R - 0.8, 0, Z0P]) rotate([90, 0, 90])
    linear_extrude(0.8) intersection() { painel2d(ELEMENTO, i); translate([-PW / 2, 0]) square([PW, PH]); }
}

// tampa na posição de USO: face de cima em z = ZT
ZT = 12;
module tampa_uso(rebaixo = 0) {
  lab = F_INT - 2 * FOLGA_JUSTA;
  difference() {
    union() {
      linear_extrude(4) oct(F_TAMPA);
      translate([0, 0, 4]) hull() { linear_extrude(0.01) oct(F_TAMPA); translate([0, 0, ZT - 4]) linear_extrude(0.01) oct(F_TOPO); }
      translate([0, 0, -LABIO]) linear_extrude(LABIO + 0.01) difference() { oct(lab); oct(lab - 3.2); }
    }
    translate([0, 0, -LABIO - 1]) linear_extrude(LABIO + 1 + ZT - 2.4) oct(lab - 3.2);
    if (rebaixo > 0) translate([0, 0, ZT - rebaixo]) linear_extrude(rebaixo + 1) selo2d(ELEMENTO);
  }
}
module selo_uso() translate([0, 0, ZT - INLAY]) linear_extrude(INLAY) selo2d(ELEMENTO);
// virar para imprimir: girar 180° no eixo Y (preserva a leitura do selo)
module para_impressao() translate([0, 0, ZT]) rotate([0, 180, 0]) children();

function cores(e) = e == "sangue" ? ["#151515", "#c0141c"] : e == "morte" ? ["#151515", "#f0f0f0"] : ["#f0f0f0", "#151515"];

if (PARTE == "corpo") corpo();
if (PARTE == "tampa") para_impressao() tampa_uso(INLAY);
if (PARTE == "selo") para_impressao() selo_uso();
if (PARTE == "tampa_simples") para_impressao() tampa_uso(0.8);
if (PARTE == "preview") {
  c = cores(ELEMENTO);
  color(c[0]) corpo();
  translate([0, 0, H + 0.2]) { color(c[0]) tampa_uso(INLAY); color(c[1]) translate([0, 0, 0.02]) selo_uso(); }
}
if (PARTE == "selo2d") selo2d(ELEMENTO);
