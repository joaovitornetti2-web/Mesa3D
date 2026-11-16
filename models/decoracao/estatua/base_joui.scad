// Base da estátua do Joui (escala final, mm). Topo da base em z = 0.
PARTE = "base";        // base | texto | pedra
CX = -4; CY = -6; R = 54; HB = 8;
PE = [-39, -10]; PE_Z = 19.7;   // pé esquerdo (levantado) – a pedra sobe até ele
module disco() {
  translate([CX, CY, -HB]) cylinder(r = R, h = HB - 1.6, $fn = 160);
  translate([CX, CY, -1.6]) cylinder(r1 = R, r2 = R - 1.6, h = 1.6, $fn = 160);
}
module texto(prof = 0.9) {
  translate([CX, CY - R + 9.5, -prof]) linear_extrude(prof + 0.01)
    text("JOUI JOUKI", size = 6.5, halign = "center", valign = "center", font = "Liberation Serif:style=Bold", spacing = 1.15);
}
module pedra() {
  // rocha facetada: casco de blocos girados
  translate([PE[0], PE[1], -0.5]) hull() {
    for (b = [[0, 0, 0, 22, 17, 6, 8], [1, -1, 6, 19, 15, 6, -14], [-1, 1, 12, 16, 13, 6, 21], [0, 0, PE_Z - 1.5, 13, 11, 2.1, 5]])
      translate([b[0], b[1], b[2]]) rotate([b[6] * 0.4, -b[6] * 0.3, b[6]]) translate([-b[3] / 2, -b[4] / 2, 0]) cube([b[3], b[4], b[5]]);
  }
  // pedrinhas soltas
  for (p = [[-22, -30, 3.2], [20, -26, 2.6], [-30, 18, 2.8], [28, 16, 2.2]])
    translate([p[0], p[1], -0.5]) hull() for (k = [0:3]) rotate([k * 37, k * 53, k * 71]) cube([p[2], p[2] * 0.8, p[2] * 0.7], center = true);
}
if (PARTE == "base") difference() { disco(); texto(); }
if (PARTE == "texto") intersection() { disco(); texto(0.9); }
if (PARTE == "pedra") pedra();
