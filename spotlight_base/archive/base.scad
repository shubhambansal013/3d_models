// Spotlight twist-lock ceiling mount.
// Base plate (ceiling side): Ø100 annulus screwed flat to the ceiling, with
// 3 lock tabs on its outer rim. Mount plate (light side): Ø106 cap that
// twists ~10° over the base rim, fully hiding the base, with a central boss
// the spotlight screws onto.

/* [Global & Render Settings] */
view_mode = "assembled"; // [assembled, base_plate, mount_plate, lock_tab_linear, lock_channel_linear, diff_check]
$fn       = 72;          // Curved-surface resolution

/* [Plate Dimensions] */
plate_radius      = 50.0;  // Outer radius of the base plate annulus (mm)
plate_thickness   = 4.0;   // Thickness of the base plate (mm)
wire_hole_radius  = 25.0;  // Radius of the central wire through-hole (mm)
base_pocket_depth = 2.0;   // Underside lightening pocket depth (mm); leaves 2mm ceiling-side skin
base_pocket_inner = 28.0;  // Pocket inner radius: clears the Ø50 wire hole (mm)
base_pocket_outer = 42.0;  // Pocket outer radius: clears the tab roots at r43 (mm)
base_pocket_boss_r = 5.0;  // Full-depth circle kept around each screw (mm)
bend_steps        = 24;    // Segment count for the cylindrical bend

/* [Screw Holes] */
screw_hole_radius   = 35.0;       // Radius of the M3 screw hole centers (mm)
screw_angles        = [90, 270];  // Angular positions of the screw holes (deg)
screw_through_r     = 1.7;        // Through-hole radius for M3 (Ø3.4, mm)
screw_counterbore_r = 3.1;        // Counterbore radius for socket-head M3 (Ø6.2, mm)
screw_counterbore_d = 3.0;        // Counterbore depth (mm)

/* [Lock Geometry] */
lock_height     = 3.0;   // Overall height of the locking lip (mm)
lock_gap_height = 1.0;   // Vertical slot height of the locking channel (mm)
lock_taper      = 1.2;   // Ramp length on the locking tab (mm)
lock_width      = 8.0;   // Width of the tab engagement surface (mm)
lock_protrusion = 1.0;   // Total tab lip span (radial); 0.25 embeds in the rim, 0.75 sticks out (mm)

/* [Cap & Lock Channel (phase 2)] */
cap_radius    = 53.0;  // Ø106 / 2: cap disc and skirt outer radius (mm)
cap_disc_h    = 2.5;   // Disc thickness (light-side mounting face) (mm)
cap_skirt_h   = 14.0;  // Skirt depth: ceiling edge down to the disc (mm)
cap_fillet_r  = 2.0;   // Fillet radius on the disc/wall junction (bottom lip, mm)

ch_ang_rot    = -10;   // Channel fold-copy axis, 10° behind the tab at drop (deg)
ch_clear      = 0.2;   // Radial clearance to the tab outer face (mm)
ch_back_wall  = -5.2;  // Groove back wall (fold-local deg): seats the tab back edge
ch_front      = 15.2;  // Groove open entrance (fold-local deg): clears the tab at drop
ch_roof_end   = 4.8;   // Roof front edge (fold-local deg): free drop, captured at seat
ch_roof_in    = 50.4;  // Roof overhang inner radius: captures the tab's outer lip (mm)
ch_groove_bot = 12.3;  // Groove floor (mount-local z): tab base − clearance
ch_groove_top = 13.8;  // Groove ceiling (mount-local z): 1.5 over the tab base
ch_block_top  = 14.4;  // Channel block top (mount-local z): roof thickness 0.6

// ============================================================
// Entry point
// ============================================================

// Skirt top (cap_disc_h + cap_skirt_h above the mount origin) meets the base
// ceiling face (assembled base top = 2 + plate_thickness).
mount_offset_z = (2 + plate_thickness) - (cap_disc_h + cap_skirt_h);

if (view_mode == "assembled") {
    // Mount shown seated: rotate +10° (= −ch_ang_rot) from the drop pose
    rotate([0, 0, -ch_ang_rot])
        translate([0, 0, mount_offset_z])
            mount_plate();
    translate([0, 0, 2])
        base_plate();
}
else if (view_mode == "base_plate") {
    base_plate();
}
else if (view_mode == "mount_plate") {
    mount_plate();
}
else if (view_mode == "lock_tab_linear") {
    lock_tab_linear();
}
else if (view_mode == "lock_channel_linear") {
    lock_channel_linear();
}
else if (view_mode == "diff_check") {
    color("red")
    intersection() {
        rotate([0, 0, -ch_ang_rot])
            translate([0, 0, mount_offset_z])
                mount_plate();
        translate([0, 0, 2])
            base_plate();
    }
}

// ============================================================
// Base plate (ceiling side, male insert)
// ============================================================

module base_plate() {
    difference() {
        // Ø100 × 4 annulus, bottom face toward the light side
        cylinder(h = plate_thickness, r = plate_radius);
        // Central Ø50 wire through-hole
        translate([0, 0, -1])
            cylinder(h = plate_thickness + 2, r = wire_hole_radius);
        // 2× flush counterbored M3 screws at r=35 / 90° + 270°
        for (a = screw_angles)
            rotate([0, 0, a])
                translate([screw_hole_radius, 0, 0])
                    screw_hole();
        // Underside (light-side) ring pocket to save filament
        base_pocket();
    }
    // 3 rim-mounted lock tabs at 0°/120°/240°
    lock_tab();
}

// Through-hole (Ø3.4) with a flush counterbore (Ø6.2 × 3) from the bottom face
module screw_hole() {
    translate([0, 0, -1])
        cylinder(h = plate_thickness + 2, r = screw_through_r);
    cylinder(h = screw_counterbore_d, r = screw_counterbore_r);
}

// Underside (light side) ring pocket to save filament. Screw bosses keep
// full plate thickness so the counterbores stay flush and the ceiling
// side remains a flat 2mm skin.
module base_pocket() {
    translate([0, 0, -1])
        difference() {
            cylinder(h = base_pocket_depth + 1, r = base_pocket_outer);
            cylinder(h = base_pocket_depth + 2, r = base_pocket_inner);
            for (a = screw_angles)
                rotate([0, 0, a])
                    translate([screw_hole_radius, 0, 0])
                        cylinder(h = base_pocket_depth + 2, r = base_pocket_boss_r);
        }
}

module lock_tab() {
    bend_r = plate_radius + 1.0;
    threefold_pattern()
        // The tab's arc starts at the fold axis and extends 5.6° past it;
        // this extra 180°+ rotation centers each tab on its 0°/120°/240° axis.
        rotate([0, 0, 180 + (lock_width / 2 + 1) / bend_r * (180 / PI)])
            translate([-(plate_radius + 1.0), 0, 2])
                rotate([0, 90, 0])
                    cylindric_bend([8, 10.5, 8], bend_r, nsteps = bend_steps)
                        // z=1.25: tab base embeds 0.25mm past the rim so the
                        // union with the annulus is robust at $fn=72
                        translate([0, lock_width + 1, 1.25])
                            rotate([0, -90, 0])
                                rotate([0, 0, 90])
                                    rotate([0, 180, 0])
                                        lock_tab_linear();
}

module lock_tab_linear() {
    difference() {
        hull() {
            lip_prism();
            translate([lock_width, 0, 0])
                lip_prism();
        }
        translate([-10, -10, lock_height - lock_gap_height])
            cube([20, 20, 20]);
    }
}

// ============================================================
// Mount plate (light side, female socket)
// ============================================================

module mount_plate() {
    boss_r    = 4.75;   // Ø9.5 central boss (light-side, spotlight mount)
    boss_h    = 5.0;
    pilot_r   = 1.45;   // Ø2.9 pilot hole through the boss
    wire_off  = 12.0;   // Ø8 wire-exit hole center radius
    wire_r    = 4.0;
    union() {
        difference() {
            union() {
                cylinder(h = cap_disc_h, r = cap_radius);
                translate([0, 0, cap_disc_h])
                    cylinder(h = cap_skirt_h, r = cap_radius);
                translate([0, 0, -boss_h])
                    cylinder(h = boss_h + cap_disc_h, r = boss_r);
            }
            // Hollow cup: open interior under the disc, skirt top open to the ceiling
            translate([0, 0, cap_disc_h - 0.1])
                cylinder(h = cap_skirt_h + 0.2, r = plate_radius + 1.0);
            translate([0, 0, -boss_h - 1])
                cylinder(h = boss_h + cap_disc_h + 2, r = pilot_r);
            translate([wire_off, 0, -1])
                cylinder(h = cap_disc_h + 2, r = wire_r);
            // Rounded bottom lip: carve the quarter-round so the visible edge
            // reads as a smooth fillet while the Ø106 envelope holds.
            cap_lip_fillet();
        }
        // Rim lock channels engaging the base-plate tabs (restore the channel region)
        lock_channel();
    }
}

module lock_channel() {
    threefold_pattern()
        rotate([0, 0, ch_ang_rot])
            rim_channel();
}

// Rounded bottom lip. Carves a quarter-disc of radius cap_fillet_r off the
// disc/wall corner. The quarter-disc's 90° corner sits just outside the part
// (r = cap_radius + eps, z = -eps) so its two flat faces over-cut the disc
// face and the outer wall instead of coinciding with them; the visible edge
// is the smooth arc. Subtractive: the Ø106 envelope and skirt top are kept.
module cap_lip_fillet() {
    eps = 0.1;                      // Over-cut past the two faces (mm)
    r   = cap_radius + eps;
    n   = ceil($fn / 4);
    rotate_extrude($fn = $fn)
        polygon(concat(
            [[r, -eps]],
            [for (i = [0 : n]) let(a = 180 - 90 * i / n)
                 [r + cap_fillet_r * cos(a), -eps + cap_fillet_r * sin(a)]]
        ));
}

module rim_channel() {
    // One groove: outer wall ring + roof overhang (back 10°) + back-wall slab.
    // Tab (measured at rim): outer r 50.75, angular ±5°, wedge crest 0.75–1.6
    // (tallest at the root near r 50.1). Groove void = r[50.2,50.95] × z[bot,top]
    // × angular [back_wall, front]; the roof starts at r 50.4 to clear the tab's
    // inner crest during rotation while capturing its outer lip against pullout.
    r_groove_in = plate_radius + ch_clear;              // 50.2
    r_wall      = 50.75 + ch_clear;                     // 50.95
    r_outer     = cap_radius;
    union() {
        annular_segment(r_wall, r_outer, ch_groove_bot, ch_block_top, ch_back_wall, ch_front);
        annular_segment(ch_roof_in, r_wall, ch_groove_top, ch_block_top, ch_back_wall, ch_roof_end);
        annular_segment(r_groove_in, r_wall, ch_groove_bot, ch_groove_top, ch_back_wall - 0.5, ch_back_wall);
    }
}

// Annular sector r1<=r<=r2, z z1..z2, angles a1..a2 (deg, around +X).
// Arcs sampled so the chord sagitta stays below ~0.04mm (2° steps at r~51).
module annular_segment(r1, r2, z1, z2, a1, a2) {
    n = max(2, ceil(abs(a2 - a1) / 2));
    outer = [for (i = [0 : n]) let(a = a1 + (a2 - a1) * i / n)
                 [r2 * cos(a), r2 * sin(a)]];
    inner = [for (i = [0 : n]) let(a = a2 - (a2 - a1) * i / n)
                 [r1 * cos(a), r1 * sin(a)]];
    translate([0, 0, z1])
        linear_extrude(height = z2 - z1)
            polygon(concat(outer, inner));
}

module lock_channel_linear() {
    difference() {
        union() {
            hull() {
                lip_prism();
                translate([lock_taper, 0, -lock_gap_height * 0.5])
                    lip_prism();
            }
            hull() {
                translate([lock_taper, 0, -0.5])
                    lip_prism();
                translate([lock_taper * 2, 0, -lock_gap_height * 0.25])
                    lip_prism();
            }
            hull() {
                translate([lock_taper * 2, 0, -0.25])
                    lip_prism();
                translate([lock_taper * 3 + lock_width, 0, -0.25])
                    lip_prism();
            }
            hull() {
                translate([lock_taper * 3 + lock_width, 0, -(lock_height + lock_gap_height - lock_taper)])
                    lip_prism();
                translate([lock_taper * 4 + lock_width, 0, -(lock_height + lock_gap_height - lock_taper)])
                    lip_prism();
            }
        }
        union() {
            translate([-10, -10, 2.0])
                cube([20, 20, 20]);
            translate([-10, -10, -21.0])
                cube([20, 20, 20]);
        }
    }
}

// ============================================================
// Shared helpers
// ============================================================

module lip_prism() {
    hull() {
        translate([0, 0, 0.01])
            cylinder(r = 0.05, h = 0.01, center = true);
        translate([0, 0, lock_taper])
            linear_extrude(height = 5)
                polygon([[0, lock_protrusion], [1, 0], [-1, 0]]);
    }
}

// Reproduces children three times at 120-degree intervals
module threefold_pattern() {
    children();
    rotate([0, 0, 120])  children();
    rotate([0, 0, -120]) children();
}

// Bends a flat child object around a cylinder of the given radius
module cylindric_bend(size, radius, nsteps = $fn) {
    step_angle = (nsteps == 0) ? $fa : atan(size.y / (radius * nsteps));
    steps      = ceil((nsteps == 0) ? size.y / (tan(step_angle) * radius) : nsteps);
    step_width = size.y / steps;

    intersection() {
        children();
        cube([size.x, step_width * 0.5, size.z]);
    }

    for (step = [1 : steps]) {
        translate([
            0,
            radius * sin(step * step_angle),
            radius * (1 - cos(step * step_angle))
        ])
        rotate(step_angle * step, [1, 0, 0])
        translate([0, -step * step_width, 0])
        intersection() {
            children();
            translate([0, (step - 0.5) * step_width, 0])
                cube([size.x, step_width, size.z]);
        }
    }
}
