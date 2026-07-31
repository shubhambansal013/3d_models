// Spotlight twist-lock mount.
// The base plate (ceiling side) carries a male insert that locks into the
// mount plate (light side). The spotlight screws onto the mount plate.

/* [Global & Render Settings] */
view_mode = "assembled"; // [assembled, base_plate, mount_plate, lock_tab_linear, lock_channel_linear, diff_check]
$fn       = 72;          // Curved-surface resolution

/* [Plate Dimensions] */
plate_radius     = 50.0;  // Outer radius of the base plate annulus (mm)
plate_thickness  = 4.0;   // Thickness of the base plate (mm)
wire_hole_radius = 25.0;  // Radius of the central wire through-hole (mm)
bend_steps       = 24;    // Segment count for the cylindrical bend

/* [Screw Holes] */
screw_hole_radius   = 35.0;       // Radius of the M3 screw hole centers (mm)
screw_angles        = [90, 270];  // Angular positions of the screw holes (deg)
screw_through_r     = 1.7;        // Through-hole radius for M3 (Ø3.4, mm)
screw_counterbore_r = 3.1;        // Counterbore radius for socket-head M3 (Ø6.2, mm)
screw_counterbore_d = 3.0;        // Counterbore depth (mm)

/* [Fit & Tolerances] */
tolerance    = 0.2;  // Clearance added to the female side for smooth mating (mm)
assembly_gap = 5.0;  // Vertical spacing between the plates when assembled (mm)

/* [Lock Geometry] */
lock_height     = 3.0;   // Overall height of the locking lip (mm)
lock_gap_height = 1.0;   // Vertical slot height of the locking channel (mm)
lock_taper      = 1.2;   // Ramp length on the locking tab (mm)
lock_width      = 8.0;   // Width of the tab engagement surface (mm)
lock_protrusion = 1.0;   // Total tab lip span (radial); 0.25 embeds in the rim, 0.75 sticks out (mm)

/* [Legacy — removed in phase 2] */
shaft_radius = 8;  // Old male-insert radius; only lock_channel still references it

// ============================================================
// Entry point
// ============================================================

if (view_mode == "assembled") {
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
        mount_plate();
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
    socket_radius = shaft_radius + tolerance + lock_protrusion;
    union() {
        difference() {
            cylinder(h = 4, r = plate_radius, center = true);
            cylinder(h = 5, r = socket_radius, center = true);
        }
        translate([0, 0, 2])
            lock_channel();
        translate([0, 0, -5])
            cylinder(h = 3, r = plate_radius);
    }
}

module lock_channel() {
    bend_r = shaft_radius + lock_protrusion + tolerance;
    threefold_pattern() {
        translate([-bend_r, 0, 0])
            rotate([0, 90, 0])
                cylindric_bend([10, 10, 10], bend_r, nsteps = bend_steps)
                    translate([2, 7, 0])
                        rotate([0, -90, 0])
                            rotate([0, 0, -90])
                                lock_channel_linear();
    }
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
