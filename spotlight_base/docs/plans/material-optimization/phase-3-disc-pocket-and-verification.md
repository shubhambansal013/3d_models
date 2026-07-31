# Phase 3: Mount plate disc pocket + full verification

## Objective
Pocket the mount disc's cup-side top face (invisible in use) to save ~7 cm³,
then run the full verification pass (all view modes + STL volume comparison)
so the plan's material targets are confirmed and the final state is rendered.

## Dependencies
- PLAN.md + NOTES.md read. Phases 1 and 2 should be `done` (all edits land in
  the same `base.scad`, and the final volume comparison needs both parts).

## Responsibilities
- Add the disc pocket parameters and its subtraction in `mount_plate()`.
- Run the complete verification battery: renders of all view modes, `diff_check`
  overlap sanity, STL volume comparison for both parts.
- Update NOTES.md with measured volumes and any gotchas.
- Does NOT change lock geometry, dimensions, or rework existing pocket/fillet code.

## Todos
- [ ] In the `Cap & Lock Channel` block add:
      ```
      disc_pocket_depth = 1.0;  // Cup-side lightening pocket depth in the disc (mm)
      disc_pocket_inner = 6.0;  // Pocket inner radius: clears the boss (r4.75) and pilot (mm)
      disc_pocket_outer = 48.0; // Pocket outer radius: leaves the channel rim solid (mm)
      ```
- [ ] In `mount_plate()`'s `difference()` (base.scad:154–169) add a new
      subtraction:
      ```
      // Lightening pocket on the disc's cup-side face (invisible in use);
      // leaves a 1.5mm floor on the light side.
      translate([0, 0, cap_disc_h - disc_pocket_depth])
          difference() {
              cylinder(h = disc_pocket_depth + 1, r = disc_pocket_outer);
              cylinder(h = disc_pocket_depth + 2, r = disc_pocket_inner);
          }
      ```
- [ ] Sanity: pocket inner 6 > pilot r1.45 and boss r4.75; outer 48 < channel
      rim (r50.2+); depth 1 leaves disc floor 1.5mm; wire-exit hole at r12
      overlaps the pocket — harmless (both voids).
- [ ] Verify all view modes render (parse + no warnings):
      ```
      xvfb-run -a openscad base.scad -D 'view_mode="base_plate"'   -o /tmp/bp.png --viewall --imgsize=1024,1024
      xvfb-run -a openscad base.scad -D 'view_mode="mount_plate"'  -o /tmp/mp.png --viewall --imgsize=1024,1024
      xvfb-run -a openscad base.scad -D 'view_mode="assembled"'    -o /tmp/as.png --viewall --imgsize=1024,1024
      xvfb-run -a openscad base.scad -D 'view_mode="diff_check"'   -o /tmp/dc.png --viewall --imgsize=1024,1024
      ```
- [ ] Confirm `diff_check` shows only the tab/channel engagement overlap —
      no new geometric interference from the pockets or fillet.
- [ ] Volume comparison. Export and measure both parts:
      ```
      xvfb-run -a openscad base.scad -D 'view_mode="base_plate"'  -o /tmp/base_final.stl
      xvfb-run -a openscad base.scad -D 'view_mode="mount_plate"' -o /tmp/mount_final.stl
      ```
      Compute STL volume with a plain-python signed-tetrahedron sum (no deps;
      watertight mesh → abs of summed signed volumes). Targets:
      base ≈ 18.5 cm³ (from ~24.4), mount ≈ 26.5 cm³ (from ~31.9, net of
      +fillet −disc-pocket). Record actuals in NOTES.md.
- [ ] Refresh the deliverable renders tracked in the repo (base_plate_*, mount_plate_*,
      assembled_*, diff_check.png) to match the new geometry.
- [ ] Update AGENTS.md design notes only if a parameter's behavior changed in a
      way the notes describe (pockets/fillet are new params — add a one-line
      note each in the Key parameters section; do NOT rewrite lock notes).

## Acceptance criteria
- All five view modes render cleanly; `diff_check` unchanged except tab engagement.
- Measured volumes meet targets (±0.5 cm³): base ≈ 18.5 cm³, mount ≈ 26.5 cm³.
- No lock/channel/dimension parameter values changed.
- Repo renders updated; NOTES.md has measured numbers and any deviations.
