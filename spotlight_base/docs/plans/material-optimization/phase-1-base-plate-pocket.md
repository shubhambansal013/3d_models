# Phase 1: Base plate ring pocket

## Objective
Cut a lightening pocket from the base plate's light-side face (z=0) to remove
~24% of its material (~5.8 cm³). Self-contained single-file edit + render
verification; fits one session. Is its own phase so the volume change is
measured before the mount plate edits land in the same file.

## Dependencies
- PLAN.md + NOTES.md read.
- `base.scad` current working version (HEAD `cad9fa2`). Read `base_plate()`
  around lines 89–104 and the `Plate Dimensions` block lines 11–15.

## Responsibilities
- Add the four pocket parameters and the `base_pocket()` module.
- Wire `base_pocket()` into `base_plate()`'s `difference()`.
- Verify: `base_plate` render + STL volume comparison vs pre-change volume.
- Does NOT touch `mount_plate()`, lock geometry, or any existing parameter values.

## Todos
- [ ] In the `Plate Dimensions` block (after `wire_hole_radius`, base.scad:14)
      add:
      ```
      base_pocket_depth = 2.0;  // Underside lightening pocket depth (mm); leaves 2mm ceiling-side skin
      base_pocket_inner = 28.0; // Pocket inner radius: clears the Ø50 wire hole (mm)
      base_pocket_outer = 42.0; // Pocket outer radius: clears the tab roots at r43 (mm)
      base_pocket_boss_r = 5.0; // Full-depth circle kept around each screw (mm)
      ```
- [ ] Add a `base_pocket()` module near `base_plate()` (matches existing
      module style, comment header):
      ```
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
      ```
- [ ] In `base_plate()`'s `difference()` (base.scad:90–101) add `base_pocket();`
      after the `screw_hole()` loop.
- [ ] Sanity: pocket inner 28 > wire_hole_radius 25; outer 42 < tab body root
      (~r43); boss r5 covers counterbore (r3.1 → 38.1mm) plus margin at r35.
- [ ] Render: `xvfb-run -a openscad base.scad -D 'view_mode="base_plate"' -o out.png --viewall --imgsize=1024,1024`
      and confirm the pocket ring is visible on the light side with full-depth
      bosses at 90°/270°.
- [ ] Export STL `xvfb-run -a openscad base.scad -D 'view_mode="base_plate"' -o /tmp/base_after.stl`
      and compute volume (see NOTES.md / phase 3 for the plain-python signed-tetrahedron
      script). Record before/after in NOTES.md.
- [ ] Optionally render `view_mode="assembled"` to confirm no visual regression.

## Acceptance criteria
- `base_plate` view renders without warnings and shows the pocket ring.
- Measured base volume drops ~5–6 cm³ (before ≈ 24.4 cm³) from the pocket.
- Counterbores (full 4mm at screw bosses) and tab roots (r43–50.75) untouched.
- `git diff` is limited to the params block + `base_pocket()` + one line in
  `base_plate()`.
