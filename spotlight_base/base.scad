// ============================================================
// PARAMETRIC TWIST & LOCK COUPLING v37
// Refactored and fully parametric
// ============================================================

/* [Global & Render Settings] */
// Select what to render: "assembled", "receptacle", "plug", or "diff_check"
view_mode   = "assembled"; // [assembled, receptacle, plug, diff_check]
$fn         = 72;          // Resolution of rounded elements

/* [Coupling Fit & Tolerances] */
plug_radius = 8;  // Core radius of the male plug shaft (mm)
tolerance   = 0.2;  // Clearance offset for smooth mating (mm)
mating_dist = 5.0;  // Spacing height when assembled (mm)

/* [Locking Lip Dimensions] */
lip_total_height = 3.0;   // Overall height of the locking lip (mm)
lip_gap_height   = 1.0;   // Vertical slot height for locking channel (mm)
lip_taper        = 1.2;   // Taper distance along the locking ramp (mm)
lip_width        = 2.0;   // Width of the locking engagement surface (mm)
lip_protrude     = 0.75;  // Radial protrude height of locking tabs (mm)

/* [Base Flange Settings] */
flange_radius    = 10.0;  // Radius of the outer mounting plates (mm)
bend_steps       = 20;    // Step resolution for cylindrical bend function

// ============================================================
// HELPER & UTILITY MODULES
// ============================================================

// Bends a flat 3D object around a cylinder of a specified radius
module cylindric_bend(dimensions, radius, nsteps = $fn) {
    step_angle = (nsteps == 0) ? $fa : atan(dimensions.y / (radius * nsteps));
    steps      = ceil((nsteps == 0) ? dimensions.y / (tan(step_angle) * radius) : nsteps);
    step_width = dimensions.y / steps;
    
    intersection() {
        children();
        cube([dimensions.x, step_width * 0.5, dimensions.z]);
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
                cube([dimensions.x, step_width, dimensions.z]);
        }
    }
}

// 3-Way Radial Symmetry Pattern (120-degree rotation)
module tri_pattern() {
    children();
    rotate([0, 0, 120])  children();
    rotate([0, 0, -120]) children();
}

// Clean 3D prism anchor point for lip geometry
module liprism() {
    hull() {
        translate([0, 0, 0.01])
            cylinder(r = 0.05, h = 0.01, center = true);
        translate([0, 0, lip_taper])
            linear_extrude(height = 5)
                polygon([[0, lip_protrude], [1, 0], [-1, 0]]);
    }
}

// ============================================================
// LINEAR LOCKING LIP GENERATORS
// ============================================================

module reclip_linear() {
    difference() {
        union() {
            hull() {
                liprism();
                translate([lip_taper, 0, -lip_gap_height * 0.5])
                    liprism();
            }
            hull() {
                translate([lip_taper, 0, -0.5])
                    liprism();
                translate([lip_taper * 2, 0, -lip_gap_height * 0.25])
                    liprism();
            }
            hull() {
                translate([lip_taper * 2, 0, -0.25])
                    liprism();
                translate([lip_taper * 3 + lip_width, 0, -0.25])
                    liprism();
            }
            hull() {
                translate([lip_taper * 3 + lip_width, 0, -(lip_total_height + lip_gap_height - lip_taper)])
                    liprism();
                translate([lip_taper * 4 + lip_width, 0, -(lip_total_height + lip_gap_height - lip_taper)])
                    liprism();
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

module pluglip_linear() {
    difference() {
        hull() {
            liprism();
            translate([lip_width, 0, 0])
                liprism();
        }
        translate([-10, -10, lip_total_height - lip_gap_height])
            cube([20, 20, 20]);
    }
}

// Creates cylindrical arc sections instead of a full cylinder
module cylinder_arc_sections(h, r, centers, angle_width) {
    union() {
        for (center = centers) {
            intersection() {
                cylinder(h = h, r = r);
                linear_extrude(height = h)
                polygon(concat(
                    [[0, 0]],
                    [for (a = [center - angle_width/2 : 1 : center + angle_width/2])
                        [r * cos(a), r * sin(a)]]
                ));
            }
        }
    }
}

// ============================================================
// MAIN COMPONENT MODULES
// ============================================================

// --- Receptacle (Female Socket) ---
module reclip() {
    bend_r = plug_radius + lip_protrude + tolerance;
    tri_pattern() {
        translate([-bend_r, 0, 0])
            rotate([0, 90, 0])
                cylindric_bend([10, 10, 10], bend_r, nsteps = bend_steps)
                    translate([2, 7, 0])
                        rotate([0, -90, 0])
                            rotate([0, 0, -90])
                                reclip_linear();
    }
}

module receptacle() {
    outer_socket_r = plug_radius + tolerance + lip_protrude;
    union() {
        difference() {
            cylinder(h = 4, r = flange_radius, center = true);
            cylinder(h = 5, r = outer_socket_r, center = true);
        }
        translate([0, 0, 2])
            reclip();
        translate([0, 0, -5])
            cylinder(h = 3, r = flange_radius);
    }
}

// --- Plug (Male Insert) ---
module plug() {
    bend_r = plug_radius + 1.0;
    translate([0, 0, mating_dist + 0.5]) {
        cylinder(h = 2, r = flange_radius);
        
        difference() {
            union() {
                translate([0, 0, -3])
                    cylinder_arc_sections(h = 3, r = plug_radius, centers = [60, 180, 300], angle_width = 60);
                
                translate([0, 0, -2]) {
                    tri_pattern()
                        translate([-(plug_radius + lip_protrude), 0, 1])
                            rotate([0, 90, 0])
                                cylindric_bend([6, 6, 6], bend_r, nsteps = ceil(bend_steps / 2))
                                    translate([0, lip_width + 1, 1])
                                        rotate([0, -90, 0])
                                            rotate([0, 0, 90])
                                                rotate([0, 180, 0])
                                                    pluglip_linear();
                }
            }
            
            // Internal core relief cutout
            translate([0, 0, -3.1])
                cylinder(h = 2.1, r = plug_radius - 0.8);
        }
    }
}

// ============================================================
// EXECUTION & VIEW CONTROLLER
// ============================================================

if (view_mode == "assembled") {
    receptacle();
    translate([0, 0, 2])
        plug();
} 
else if (view_mode == "receptacle") {
    receptacle();
} 
else if (view_mode == "pluglip_linear") {
    pluglip_linear();
}
else if (view_mode == "reclip_linear") {
    reclip_linear();
} 
else if (view_mode == "plug") {
    plug();
} 
else if (view_mode == "diff_check") {
    // Shows true geometric overlap between the plug and receptacle
    color("red")
    intersection() {
        receptacle();
        plug();
    }
}
