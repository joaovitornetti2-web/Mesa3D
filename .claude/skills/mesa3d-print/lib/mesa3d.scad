// mesa3d.scad – constantes e módulos comuns. Use: include <../../.claude/skills/mesa3d-print/lib/mesa3d.scad>
// Mantenha estes números iguais ao printer-profile.json (não calibrados até o gauge ser impresso).
GRADE      = 25.4;   // 1 quadrado de RPG (5 pés)
FOLGA_JUSTA = 0.15;  // por lado
FOLGA_DESL  = 0.25;
PAREDE_MIN  = 1.2;
IMA_D = 6.3;  IMA_H = 3.2;   // furo para ímã 6x3
$fn = 64;

// Furo para ímã, aberto por baixo (cole o ímã depois de imprimir).
module furo_ima(d = IMA_D, h = IMA_H) { translate([0, 0, -0.01]) cylinder(d = d, h = h + 0.01); }

// Texto gravado (profundidade 0.6) no topo de uma face em z = topo.
module gravar(txt, tam = 5, topo = 0) {
  translate([0, 0, topo - 0.6]) linear_extrude(0.61)
    text(txt, size = tam, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
}

// Tile de chão: nx × ny quadrados, com sulcos da grade e (opcional) um ímã sob o centro de cada quadrado.
// Ímãs por baixo prendem o tile numa chapa de aço; eles NÃO unem um tile ao outro.
module tile_chao(nx = 2, ny = 2, altura = 6, sulco = 0.8, imas = false) {
  difference() {
    cube([nx * GRADE, ny * GRADE, altura]);
    if (nx > 1) for (i = [1:nx - 1]) translate([i * GRADE - sulco / 2, -1, altura - sulco]) cube([sulco, ny * GRADE + 2, sulco + 1]);
    if (ny > 1) for (j = [1:ny - 1]) translate([-1, j * GRADE - sulco / 2, altura - sulco]) cube([nx * GRADE + 2, sulco, sulco + 1]);
    if (imas) for (i = [0:nx - 1], j = [0:ny - 1]) translate([(i + 0.5) * GRADE, (j + 0.5) * GRADE, 0]) furo_ima();
  }
}
