// Logo Mesa3D em relevo (para foto de perfil e também imprimível como placa/ímã).
// PARTE: base | icone | texto
PARTE = "base";
use <../kit/kit_rpg.scad>
$fn = 96;
D = 100;
if (PARTE == "base") cylinder(d = D, h = 3);
if (PARTE == "icone") translate([0, 11, 2.99]) linear_extrude(1.4) d20_2d(27, 2.6);
if (PARTE == "texto") translate([0, -27, 2.99]) linear_extrude(1.4) text("MESA3D", size = 12.5, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
