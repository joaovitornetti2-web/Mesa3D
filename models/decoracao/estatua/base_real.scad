PARTE = "base";
CX = -9.3; CY = -4.1; R = 46; HB = 9;
module disco() {
  translate([CX, CY, -HB]) cylinder(r = R, h = HB - 2, $fn = 180);
  translate([CX, CY, -2]) cylinder(r1 = R, r2 = R - 2, h = 2, $fn = 180);
  // degrau decorativo
  translate([CX, CY, -HB]) cylinder(r = R + 2.5, h = 2.5, $fn = 180);
}
module texto(p = 0.9) {
  translate([CX, CY - R + 9, -p]) linear_extrude(p + 0.01)
    text("JOUI JOUKI", size = 6, halign = "center", valign = "center", font = "Liberation Serif:style=Bold", spacing = 1.18);
}
if (PARTE == "base") difference() { disco(); texto(); }
if (PARTE == "texto") intersection() { disco(); texto(); }
