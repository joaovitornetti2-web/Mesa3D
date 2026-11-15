// Relicário octogonal decorativo (guarda um jogo de dados) – Morte, Sangue e Medo.
// Selos e runas ORIGINAIS na estética de horror ocultista; não copiam sigilos oficiais.
//
// PARTE: "corpo" | "tampa" | "medalhao" | "medalhao_cor1" | "medalhao_cor2" | "preview" | "selo2d"
// A tampa sai virada para imprimir (face de cima na mesa). O medalhão é uma peça à parte,
// impressa deitada, que encaixa (e cola) no assento da tampa. A 2ª cor é só o topo do relevo.
include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>
include <texturas.scad>

ELEMENTO = "sangue";   // sangue | morte | medo | energia
PARTE    = "preview";
// Símbolo próprio (uso pessoal): caminho de um SVG que substitui o motivo central.
// O build preenche sozinho se existir simbolos/<elemento>.svg (ou .png).
SIMBOLO_SVG = "";
SIMBOLO_CENTRO = [0, 0];   // calculado pelo build
SIMBOLO_ESCALA = 1;
// PLACAS = true: paredes lisas com rebaixo em arco para colar placas de personagens
PLACAS = false;
// Tamanho: 1 = 10 dados, 1.145 = 15, 1.26 = 20. Só a tampa é gerada já escalada aqui
// (para manter as folgas reais); corpo e medalhão são escalados depois, no build.
ESCALA = 1;
$fn = 72;

// ---- medidas (mm) ----
F_CORPO  = 76;   // octógono, de face a face
F_INT    = 70;   // cavidade
F_PLINTO = 82;   // base
F_MOLD   = 80;   // moldura do topo
F_TAMPA  = 83;   // aba da tampa (1.5 mm além da moldura, para pegar)
F_TOPO   = 67;   // face de cima da tampa
H        = 34;   // altura do corpo (o build muda por tamanho: 2 camadas de dados)
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

module motivo_energia() {
  anel(19, 1.3);
  polygon([[3.5, 16], [-8, -1], [-0.8, -1], [-4.5, -16], [8, 2.8], [0.8, 2.8]]);
  for (a = [30:60:359]) rotate(a) translate([0, 13]) polygon([[0, -2.2], [0.7, 0], [0, 2.2], [-0.7, 0]]);
}
module motivo(e) {
  if (SIMBOLO_SVG != "") scale(SIMBOLO_ESCALA) translate(-SIMBOLO_CENTRO) import(SIMBOLO_SVG);
  else if (e == "sangue") motivo_sangue(); else if (e == "morte") motivo_morte(); else if (e == "energia") motivo_energia(); else motivo_medo(); }
function semente(e) = e == "sangue" ? 11 : e == "morte" ? 23 : e == "energia" ? 53 : 37;

// selo completo (2D, centrado). Cabe no octógono do topo (raio inscrito 33.5).
module selo2d(e) {
  anel(30, 1.4);
  anel_runas(18, 25.2, semente(e), 4.6);
  anel(21.7, 1.1);
  motivo(e);
  for (a = [22.5:45:359]) rotate(a) translate([0, 31.6]) polygon([[0, -0.6], [1.4, 1.2], [0, 3.2], [-1.4, 1.2]]);
}

// ---------------- painéis laterais (2D: x ao longo da face, y para cima) ----------------
PW = 22; PH = H - 14.5;   // painel acompanha a altura do corpo
// arco ogival: retângulo + ponta formada por dois círculos
module arco2d(w = PW, h = PH) {
  r = 0.6 * w; off = r - w / 2; ha = sqrt(r * r - off * off);
  translate([-w / 2, 0]) square([w, h - ha]);
  translate([0, h - ha]) intersection() {
    translate([off, 0]) circle(r = r, $fn = 96);
    translate([-off, 0]) circle(r = r, $fn = 96);
    translate([-w / 2, 0]) square([w, ha]);
  }
}
module painel2d(e, i) {
  s = semente(e) * 100 + i * 7;
  if (e == "sangue") {
    // escorridos do alto, runas no meio, presas embaixo (bestialidade)
    for (d = [[-9, 4], [-6, 7], [-3, 3.5], [0.5, 6], [3.5, 8], [6.5, 4], [9, 5.5]])
      hull() { translate([d[0] - 1, PH - 0.5]) square([2, 0.5]); translate([d[0], PH - d[1] * (PH - 9) / 10.5]) circle(d = 2.2, $fn = 20); }
    for (k = [0:2]) translate([(k - 1) * 6.5, 6.9]) runa(s + k, 3.4, 4.6);
    for (x = [-9:3:9]) polygon([[x - 1.3, 0], [x + 1.3, 0], [x, 2.8 + (abs(x) % 6 == 0 ? 0.7 : 0)]]);
  } else if (e == "morte") {
    // espiral do tempo dentro do arco, runas embaixo
    translate([0, PH - 7.1]) linha([for (t = [0:8:3 * 360]) let(rr = 0.7 + t / 360 * 1.75) [rr * cos(-t + 90), rr * sin(-t + 90)]], 1.0);
    translate([0, PH - 7.1]) circle(d = 1.8);
    for (y = [11.5:7.5:PH - 15.5]) for (x = [-5.5, 5.5]) translate([x, y]) linha([for (t = [0:12:2 * 360]) let(rr = 0.5 + t / 360 * 1.15) [rr * cos(t), rr * sin(t)]], 0.9);
    translate([-PW / 2 + 1.5, 5.6]) square([PW - 3, 0.9]);
    for (k = [0:2]) translate([(k - 1) * 6.5, 2.6]) runa(s + k, 3.2, 4.0);
  } else if (e == "energia") {
    // raio central em zigue-zague, faíscas, faixas de falha digital e runas
    polygon([[2.2, PH], [-3.6, PH * 0.55], [-0.4, PH * 0.55], [-2.8, 7.2], [3.8, PH * 0.62], [0.6, PH * 0.62], [5.2, PH]]);
    for (q = [[-7, PH * 0.78, 1.6], [7.2, PH * 0.7, 1.3], [-6.5, PH * 0.42, 1.1], [6.8, PH * 0.38, 1.5], [-3.2, PH * 0.9, 0.9]])
      translate([q[0], q[1]]) scale(q[2]) polygon([[0, -2], [0.45, -0.45], [2, 0], [0.45, 0.45], [0, 2], [-0.45, 0.45], [-2, 0], [-0.45, -0.45]]);
    for (b = [[-10, PH * 0.6, 5], [5.5, PH * 0.5, 4.5], [-9.5, PH * 0.3, 3.5], [6, PH * 0.84, 4]])
      translate([b[0], b[1]]) square([b[2], 0.9]);
    translate([-PW / 2 + 1.5, 5.6]) square([PW - 3, 0.9]);
    for (k = [0:2]) translate([(k - 1) * 6.5, 2.6]) runa(s + k, 3.2, 4.0);
  } else {
    // olho no alto, névoa ondulada, espinhos embaixo (o impossível)
    translate([0, PH - 4.7]) {
      difference() {
        intersection() { translate([0, -3.4]) circle(r = 6.2); translate([0, 3.4]) circle(r = 6.2); }
        intersection() { translate([0, -3.4]) circle(r = 5.1); translate([0, 3.4]) circle(r = 5.1); }
      }
      circle(r = 1.7);
    }
    for (y = [7.6:2.9:PH - 9.4]) linha([for (x = [-10:1:10]) [x, y + 0.7 * sin(x * 50 + y * 40)]], 0.9);
    for (p = [[-9, 5], [-6, 6.5], [-3, 4], [0, 6.8], [3, 4.5], [6, 6.2], [9, 4.8]])
      polygon([[p[0] - 1.3, 0], [p[0] + 1.3, 0], [p[0] + 0.2, p[1]]]);
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
    for (i = [0:7]) rotate(i * 45) translate([R - 0.8, 0, Z0P]) rotate([90, 0, 90]) linear_extrude(2) arco2d();
  }
  // detalhes: avançam 0.3 mm dentro da parede do arco e terminam 0.05 mm abaixo da face (malha fechada)
  if (!PLACAS) for (i = [0:7]) rotate(i * 45) translate([R - 0.9, 0, Z0P]) rotate([90, 0, 90])
    linear_extrude(0.85) intersection() { painel2d(ELEMENTO, i); offset(delta = 0.3) arco2d(); }
  // moldura do arco em relevo
  for (i = [0:7]) rotate(i * 45) translate([R - 0.03, 0, Z0P]) rotate([90, 0, 90])
    linear_extrude(0.7) difference() { translate([0, -0.3]) arco2d(PW + 2.4, PH + 1.47); translate([0, -1]) arco2d(PW + 0.04, PH + 1.03); }
  colunas();
}

// colunas nos 8 cantos, com base e capitel
RV = F_CORPO / 2 / cos(22.5);   // raio do vértice do corpo
module colunas() for (i = [0:7]) rotate(22.5 + i * 45) translate([RV - 0.6, 0, 0]) {
  if (ELEMENTO == "energia")   // bobina de energia: coluna torcida
    translate([0, 0, 7]) linear_extrude(H - 12, twist = -120 * (H - 12) / 10, slices = round(H * 2))
      for (a = [0:120:359]) rotate(a) translate([1.25, 0]) circle(d = 2.9, $fn = 20);
  else translate([0, 0, 7]) cylinder(d = 5.4, h = H - 12, $fn = 32);
  translate([0, 0, 7]) cylinder(d1 = 7.2, d2 = 5.4, h = 1.8, $fn = 32);
  translate([0, 0, H - 7.6]) cylinder(d1 = 5.4, d2 = 7.2, h = 1.8, $fn = 32);
  translate([0, 0, H - 5.85]) cylinder(d = 7.2, h = 0.85, $fn = 32);   // sobrepõe 0.05 (evita fresta numérica)
  if (ELEMENTO != "energia") for (z = [11:5.5:H - 9]) translate([0, 0, z]) cylinder(d = 6.2, h = 0.8, $fn = 32);   // anéis
}

// tampa na posição de USO: face de cima em z = ZT
ZT = 12;
R_MED = 31.0;     // raio do medalhão
ASSENTO = 2.0;    // altura do assento cônico (45°)
module tampa_uso() {
  lab = F_INT - 2 * FOLGA_JUSTA / ESCALA;
  difference() {
    union() {
      linear_extrude(4) oct(F_TAMPA);
      translate([0, 0, 4]) hull() { linear_extrude(0.01) oct(F_TAMPA); translate([0, 0, ZT - 4]) linear_extrude(0.01) oct(F_TOPO); }
      translate([0, 0, -LABIO]) linear_extrude(LABIO + 0.01) difference() { oct(lab); oct(lab - 3.2); }
    }
    translate([0, 0, -LABIO - 1]) linear_extrude(LABIO + 1 + ZT - 2.6) oct(lab - 3.2);
    // assento cônico do medalhão (vira chanfro de 45° na impressão, sem suporte)
    translate([0, 0, ZT - ASSENTO]) cylinder(r1 = R_MED - ASSENTO + 0.2 / ESCALA, r2 = R_MED + 0.2 / ESCALA, h = ASSENTO + 0.01, $fn = 128);
    translate([0, 0, ZT - 3]) cylinder(r = R_MED - ASSENTO + 0.2 / ESCALA, h = 2, $fn = 128);
    // diamantes gravados nos cantos do topo
    for (a = [22.5:45:359]) rotate(a) translate([0, 32.6, ZT - 0.6]) linear_extrude(1) polygon([[0, -1.2], [1.3, 0.4], [0, 2.4], [-1.3, 0.4]]);
  }
}
// virar para imprimir: girar 180° no eixo Y (preserva a leitura)
module para_impressao() translate([0, 0, ZT]) rotate([0, 180, 0]) children();

// ---- medalhão (z = 0 na mesa) ----
Z_CAMPO = ASSENTO;          // nível do fundo (rente à tampa)
H_TEXT  = 0.6;              // relevo da pedra
H_FAIXA = 0.8;              // faixa das runas
Z_COR   = Z_CAMPO + 1.4;    // troca de cor
Z_TOPO  = Z_CAMPO + 2.2;    // topo do relevo (0.8 mm = 4 camadas da 2ª cor)
Z_SIMB  = ELEMENTO == "energia" ? Z_TOPO + 0.8 : Z_TOPO;   // energia: símbolo sobe mais, topo na 3ª cor
function rachas(e) = e == "sangue" ? RACHAS_SANGUE : e == "morte" ? RACHAS_MORTE : e == "energia" ? RACHAS_ENERGIA : RACHAS_MEDO;
function larg(e) = e == "sangue" ? LARG_SANGUE : e == "morte" ? LARG_MORTE : e == "energia" ? LARG_ENERGIA : LARG_MEDO;

module medalhao() {
  e = ELEMENTO;
  cylinder(r1 = R_MED - ASSENTO, r2 = R_MED, h = ASSENTO, $fn = 128);
  // fundo de pedra rachada
  translate([0, 0, Z_CAMPO - 0.01]) linear_extrude(H_TEXT + 0.01) difference() {
    circle(r = 21.2, $fn = 128);
    for (l = rachas(e)) linha(l, larg(e));
  }
  // faixa das runas
  translate([0, 0, Z_CAMPO - 0.01]) linear_extrude(H_FAIXA + 0.01) anel(R_MED, R_MED - 21.0);
  // runas, anéis e ornamentos saltados (topo na 2ª cor)
  translate([0, 0, Z_CAMPO]) linear_extrude(Z_TOPO - Z_CAMPO) {
    anel(R_MED, 1.4);
    anel(22.0, 1.1);
    anel_runas(18, 25.6, semente(e), 4.4);
  }
  // símbolo com contorno-sombra (contorno fica na 1ª cor)
  translate([0, 0, Z_CAMPO]) linear_extrude(Z_COR - 0.2 - Z_CAMPO) intersection() { offset(r = 0.8) motivo(e); circle(r = 21); }
  translate([0, 0, Z_CAMPO]) linear_extrude(Z_SIMB - Z_CAMPO) intersection() { motivo(e); circle(r = 21); }
}
module corte(cima) intersection() { children(); translate([-50, -50, cima ? Z_COR : -1]) cube([100, 100, cima ? 20 : Z_COR + 1]); }

function cores(e) = e == "sangue" ? ["#151515", "#c0141c"] : e == "morte" ? ["#151515", "#f0f0f0"] : e == "energia" ? ["#151515", "#f0f0f0", "#c0141c"] : ["#f0f0f0", "#151515"];

if (PARTE == "corpo") corpo();
if (PARTE == "tampa") scale(ESCALA) para_impressao() tampa_uso();
if (PARTE == "medalhao") medalhao();
if (PARTE == "medalhao_cor1") corte(false) medalhao();
if (PARTE == "medalhao_cor2") corte(true) medalhao();
if (PARTE == "preview") {
  c = cores(ELEMENTO);
  color(c[0]) corpo();
  translate([0, 0, H + 0.2]) {
    color(c[0]) tampa_uso();
    translate([0, 0, ZT - ASSENTO]) { color(c[0]) corte(false) medalhao(); color(c[1]) corte(true) medalhao(); }
  }
}
if (PARTE == "selo2d") selo2d(ELEMENTO);
if (PARTE == "campo2d") difference() { circle(r = 21.2, $fn = 128); for (l = rachas(ELEMENTO)) linha(l, larg(ELEMENTO)); }
if (PARTE == "painel2d") for (k = [0:2]) translate([k * 26, 0]) intersection() { painel2d(["sangue", "morte", "medo"][k], 0); arco2d(); }
