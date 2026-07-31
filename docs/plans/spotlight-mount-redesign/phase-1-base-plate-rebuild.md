# Phase 1: Base plate rebuild (Ø100 annulus + rim tabs)

## Objective
Replace the hub-based base plate with the new ceiling-side Ø100mm part and
prove the rim bend works at radius ≈51 before the cap is built on top of it.
This is its own phase because the rim-bend constants are the biggest unknown
in the whole redesign and must be settled before phase 2 reuses the same
tooling for the cap's channels.

## Dependencies
- Requires phase(s): none (first phase).
- Files/context to read before starting: `PLAN.md` (key decisions), `NOTES.md`
  (full), and the current `/home/ubuntu/models/spotlight_base/base.scad`
  (212 lines; `lock_tab()`, `lock_tab_linear()`, `cylindric_bend()`,
  `threefold_pattern()` are the pieces this phase touches).
- Environment facts: `openscad_render_single` and `openscad_validate_scad`
  MCP tools are unreliable here (see NOTES.md). Use `xvfb-run -a openscad`
  for PNGs, `openscad_analyze_model` / STL export for geometry checks.

## Responsibilities
Owns:
- The global parameter block (new dimensions, drop `shaft_radius`).
- `base_plate()`: annulus Ø100×4 with Ø50 hole, 2 counterbored M3 holes,
  3 rim-mounted lock tabs.
- Re-derivation of the rim bend: `lock_tab()` transform offsets, `bend_r`,
  arc/footprint placement at `plate_radius`.
- Any helper needed for the annulus / counterbores (e.g. a screw-hole
  module).
- Keeping `lock_tab_linear`, `lock_channel_linear`, `lock_channel`,
  `mount_plate` renderable (may be temporarily broken/dirty — that is fine,
  phase 2 fixes them).

Does NOT touch:
- `mount_plate()` / `lock_channel()` geometry (phase 2).
- Assembly view layout / `assembly_gap` (phase 3).
- AGENTS.md (phase 3).

## Todos
- [ ] Replace the parameter block: `plate_radius = 50`, `plate_thickness = 4`,
      `wire_hole_radius = 25`, `screw_hole_radius = 35`, `screw_angles =
      [90, 270]`, counterbore dims (through Ø3.4, counterbore Ø6.2 × 3),
      `lock_width = 8`, `bend_steps = 24`, `lock_protrusion` keep 0.75 (or
      bump to 1.0 if tab visibility on the rim is too small), keep
      `tolerance 0.2`, `lock_height 3.0`, `lock_gap_height 1.0`,
      `lock_taper 1.2`. Remove `shaft_radius` (or keep only if a helper
      needs it — prefer removing).
- [ ] Re-derive the rim bend: compute `lock_tab()` with `bend_r =
      plate_radius + 1.0`, place tab angularly at 0°/120°/240° (3-fold),
      tabs centered on the rim edge, protruding radially ~`lock_protrusion`.
      Verify via STL export + `openscad_analyze_model` (or footprint
      inspection in a linear view) that the tab hugs the rim at r≈51 and is
      oriented radially. Iterate the translate/rotate offsets in
      `lock_tab()` until correct.
- [ ] Rewrite `base_plate()`: `difference()` of Ø100×4 disc minus central
      Ø50 hole and 2 flush counterbores (Ø3.4 through, Ø6.2 × 3 deep) at
      r=35 / 90° and 270°; add the rim tabs. Remove the old solid-hub
      cylinder (`translate([0,0,-3]) cylinder(h=3, r=shaft_radius)`).
- [ ] Verify `view_mode == "base_plate"` renders via
      `xvfb-run -a openscad` and analyze the STL: outer Ø≈100, inner Ø≈50,
      counterbores present at r≈35 / 90°+270° (Ø≈6.2, ~3 deep), three rim
      tabs, part is a single connected component, no warnings.
- [ ] Confirm `lock_tab_linear` still renders for debugging.

## Acceptance criteria
- `base_plate` view renders cleanly (no warnings/errors) and
  `openscad_analyze_model` confirms the dimensions in the todo above.
- The part is one connected component.
- The rim tab footprint is verified to sit tangent to the rim at
  `plate_radius` (the bend constants this produces are the input phase 2
  relies on).
- Phase status set to `done` in PLAN.md, results noted in NOTES.md.
