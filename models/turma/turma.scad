// A Turma do Ateliê – criaturinhas fofas de desenho próprio, em até 4 cores (AMS):
// cor 1 = corpo, cor 2 = detalhes escuros (pupilas, boca), cor 3 = branco (olhos, dentes), cor 4 = bochechas/acento.
// PARTE: <bicho>_c1 | _c2 | _c3 | _c4   bichos: fantasminha, gosminha, olhinho, caveirinha, morceguinho
PARTE = "fantasminha_c1";
$fn = 48;

// ponto na superfície (frente, -Y) de uma esfera de raio R centrada em (0,0,zc)
function sup(x, z, R, zc) = -sqrt(max(0, R * R - x * x - (z - zc) * (z - zc)));
// olho fofo: branco (cor 3), pupila (cor 2) e brilho (cor 3), virado para a frente
module olho(x, z, R, zc, r = 4.2, cor = 3, olhar = [0, 0]) {
  y = sup(x, z, R, zc);
  translate([x, y + 0.6, z]) rotate([90, 0, 0]) {
    if (cor == 3) scale([1, 1.12, 0.45]) sphere(r = r);
    if (cor == 2) translate([olhar[0], olhar[1] - 0.4, r * 0.3]) scale([1, 1.1, 0.5]) sphere(r = r * 0.58);
    if (cor == 3) translate([olhar[0] + r * 0.22, olhar[1] + r * 0.18, r * 0.52]) sphere(r = r * 0.2);
  }
}
module bochecha(x, z, R, zc) { y = sup(x, z, R, zc); translate([x, y + 0.5, z]) rotate([90, 0, 0]) scale([1.4, 0.9, 0.35]) sphere(r = 2.4); }
module boca_aberta(z, R, zc, w = 3.4, h = 2.6) { y = sup(0, z, R, zc); translate([0, y + 0.2, z]) rotate([90, 0, 0]) scale([w, h, 1.6]) sphere(r = 1); }
module sorriso(z, R, zc, larg = 7) {   // arco feito de bolinhas
  for (t = [-60:10:60]) let(x = sin(t) * larg / 2, zz = z - (1 - cos(t)) * larg * 0.35) {
    y = sup(x, zz, R, zc); translate([x, y + 0.4, zz]) sphere(r = 0.75);
  }
}
module base_disco(r) { cylinder(r = r, h = 2.2, $fn = 64); }

// ---------------- FANTASMINHA ----------------
FR = 16; FZ = 30;
module fantasminha_detalhes(cor) {
  for (s = [-1, 1]) olho(s * 6, FZ + 1, FR, FZ, 4.4, cor, [s * 0.4, -0.3]);
  if (cor == 2) boca_aberta(FZ - 7, FR, FZ, 2.6, 2.4);
  if (cor == 4) for (s = [-1, 1]) bochecha(s * 10.5, FZ - 4.5, FR, FZ);
}
module fantasminha_corpo() {
  difference() {
    union() {
      hull() { translate([0, 0, FZ]) sphere(r = FR); translate([0, 0, 7]) cylinder(r = 15, h = 1, $fn = 64); }
      for (a = [0:60:300]) rotate(a + 30) translate([13, 0, 6]) sphere(r = 5.2);        // barra ondulada
      for (s = [-1, 1]) translate([s * 15, -2, 22]) rotate([0, s * 35, 0]) scale([0.6, 0.6, 1.2]) sphere(r = 5); // bracinhos
      base_disco(14);
    }
    translate([0, 0, -10]) cube(40, center = true);
    for (c = [2, 3, 4]) fantasminha_detalhes(c);
  }
}

// ---------------- GOSMINHA (slime) ----------------
GR = 18; GZ = 13;
module gosminha_detalhes(cor) {
  for (s = [-1, 1]) olho(s * 7, GZ + 4, GR, GZ, 5, cor, [s * 0.6, 0.5]);
  if (cor == 2) sorriso(GZ - 3, GR, GZ, 9);
  if (cor == 4) for (s = [-1, 1]) bochecha(s * 12.5, GZ - 1, GR, GZ);
}
module gosminha_corpo() {
  difference() {
    union() {
      translate([0, 0, GZ]) scale([1, 1, 0.92]) sphere(r = GR, $fn = 64);
      translate([0, 0, 0]) cylinder(r = 19, h = 3, $fn = 64);
      for (p = [[-14, -9, 6], [15, -6, 4], [5, -16, 3]]) translate([p[0], p[1], 0]) hull() {   // pingos escorrendo
        translate([0, 0, GZ - 2]) sphere(r = 3.6); translate([0, 0, 1.5]) sphere(r = p[2] * 0.9);
      }
      translate([0, 0, GZ + GR * 0.9]) hull() { sphere(r = 3.2); translate([2, 0, 5]) sphere(r = 1.6); }   // pingo no topo
    }
    translate([0, 0, -10]) cube(60, center = true);
    for (c = [2, 3, 4]) gosminha_detalhes(c);
  }
}

// ---------------- OLHINHO (olho com asinhas e chifrinhos) ----------------
OR = 15; OZ = 24;
module olhinho_detalhes(cor) {
  y = sup(0, OZ + 1, OR, OZ);
  translate([0, y + 0.7, OZ + 1]) rotate([90, 0, 0]) {
    if (cor == 3) scale([1, 1, 0.35]) sphere(r = 10.5);
    if (cor == 4) translate([0, 0, 2.6]) scale([1, 1, 0.3]) sphere(r = 6.4);      // íris
    if (cor == 2) translate([0, 0, 3.6]) scale([0.7, 1, 0.3]) sphere(r = 3.6);    // pupila
    if (cor == 3) translate([2.4, 2.4, 4.4]) sphere(r = 1.3);                    // brilho
  }
}
module olhinho_corpo() {
  difference() {
    union() {
      translate([0, 0, OZ]) sphere(r = OR, $fn = 64);
      for (s = [-1, 1]) {
        translate([s * 6, 1, 0]) hull() { translate([0, 0, 1.5]) scale([1.4, 1.8, 0.8]) sphere(r = 2.4); translate([0, 0, OZ - 8]) sphere(r = 2.2); } // perninhas
        translate([s * 9, 2, OZ + OR - 4]) rotate([0, s * 25, 0]) cylinder(r1 = 2.6, r2 = 0.5, h = 7);                                  // chifrinhos
        translate([s * (OR - 2), 4, OZ + 2]) rotate([0, 0, s * 15]) rotate([90, 0, 0]) linear_extrude(2.2, center = true)            // asinhas
          scale([s, 1]) polygon([[0, 0], [14, 9], [11, 3], [16, 1], [12, -3], [15, -7], [0, -4]]);
      }
      base_disco(12);
    }
    translate([0, 0, -10]) cube(60, center = true);
    for (c = [2, 3, 4]) olhinho_detalhes(c);
  }
}

// ---------------- CAVEIRINHA ----------------
CR = 15; CZ = 26;
module caveirinha_detalhes(cor) {
  for (s = [-1, 1]) let(x = s * 5.6, z = CZ - 1) {
    y = sup(x, z, CR, CZ);
    translate([x, y + 1.4, z]) rotate([90, 0, 0]) {
      if (cor == 2) scale([1, 1.15, 0.6]) sphere(r = 4.2);                     // órbitas
      if (cor == 3) translate([s * 0.8, 1.2, 2]) sphere(r = 1.3);              // brilho nos olhos
    }
  }
  if (cor == 2) translate([0, sup(0, CZ - 7.5, CR, CZ) + 0.8, CZ - 7.5]) rotate([90, 0, 0]) linear_extrude(1.6, center = true) polygon([[-1.6, 1], [1.6, 1], [0, -1.4]]); // nariz
  if (cor == 3) for (x = [-4.5:3:4.5]) translate([x, -9.6, 12.5]) cube([2.3, 1.6, 3], center = true);  // dentes
  if (cor == 4) translate([7, -3, CZ + CR - 3]) for (a = [0:72:288]) rotate([20, 0, a]) translate([2.4, 0, 0]) scale([1, 0.7, 0.4]) sphere(r = 2.2); // florzinha
}
module caveirinha_corpo() {
  difference() {
    union() {
      translate([0, 0, CZ]) scale([1, 0.95, 0.92]) sphere(r = CR, $fn = 64);
      hull() { translate([-7, -5, 10]) cylinder(r = 3.5, h = 6); translate([7, -5, 10]) cylinder(r = 3.5, h = 6); translate([0, 3, 10]) cylinder(r = 6, h = 8); } // maxilar
      base_disco(12);
      translate([0, 0, 0]) cylinder(r = 6, h = 12);
    }
    translate([0, 0, -10]) cube(60, center = true);
    for (c = [2, 3]) caveirinha_detalhes(c);
  }
  // a flor fica por cima (cor 4), sem furar o crânio
}

// ---------------- MORCEGUINHO ----------------
MR = 13; MZ = 19;
module morceguinho_detalhes(cor) {
  for (s = [-1, 1]) olho(s * 5, MZ + 2, MR, MZ, 3.8, cor, [s * 0.3, 0]);
  if (cor == 3) for (s = [-1, 1]) translate([s * 2, sup(s * 2, MZ - 5, MR, MZ) + 0.6, MZ - 6.2]) rotate([90, 0, 0]) cylinder(r1 = 0.9, r2 = 0.9, h = 1.2, center = true, $fn = 3); // presinhas
  if (cor == 2) sorriso(MZ - 4, MR, MZ, 5);
  if (cor == 4) for (s = [-1, 1]) bochecha(s * 8.5, MZ - 2, MR, MZ);
}
module morceguinho_corpo() {
  difference() {
    union() {
      translate([0, 0, MZ]) scale([1, 0.92, 1]) sphere(r = MR, $fn = 64);
      for (s = [-1, 1]) {
        translate([s * 7, 0, MZ + MR - 4]) rotate([0, s * 18, 0]) scale([1, 0.55, 1]) cylinder(r1 = 4.5, r2 = 0.8, h = 10);   // orelhas
        translate([s * (MR - 3), 3, MZ + 1]) rotate([0, 0, s * 20]) rotate([90, 0, 0]) linear_extrude(2.4, center = true)       // asas
          scale([s, 1]) polygon([[0, 6], [10, 10], [20, 4], [17, 1], [19, -4], [14, -3], [13, -8], [8, -4], [0, -5]]);
        translate([s * 4.5, 0, 0]) hull() { translate([0, 0, 1.2]) scale([1.3, 1.6, 0.6]) sphere(r = 2.3); translate([0, 0, MZ - 9]) sphere(r = 2); } // pezinhos
      }
      base_disco(12);
    }
    translate([0, 0, -10]) cube(60, center = true);
    for (c = [2, 3, 4]) morceguinho_detalhes(c);
  }
}

module bicho(nome, cor) {
  if (nome == "fantasminha") { if (cor == 1) fantasminha_corpo(); else fantasminha_detalhes(cor); }
  if (nome == "gosminha") { if (cor == 1) gosminha_corpo(); else gosminha_detalhes(cor); }
  if (nome == "olhinho") { if (cor == 1) olhinho_corpo(); else olhinho_detalhes(cor); }
  if (nome == "caveirinha") { if (cor == 1) caveirinha_corpo(); else caveirinha_detalhes(cor); }
  if (nome == "morceguinho") { if (cor == 1) morceguinho_corpo(); else morceguinho_detalhes(cor); }
}
for (n = ["fantasminha", "gosminha", "olhinho", "caveirinha", "morceguinho"], c = [1:4])
  if (PARTE == str(n, "_c", c)) bicho(n, c);
