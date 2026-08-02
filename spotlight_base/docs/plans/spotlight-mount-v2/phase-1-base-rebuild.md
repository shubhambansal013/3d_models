# Phase 1: Base rebuild — Ø100×3 + monolithic lugs

## Estimated effort
~6 minutes / 5 todos. This is the biggest single geometry change; if it starts
to overrun, split the dead-code cleanup (todo 5) into phase 1b.

## Objective
Replace the slice-built `cylindric_bend` tabs with **monolithic lugs** on a new
compact Ø100×3 base. This is its own phase because it changes the base's
construction paradigm (Compound of 73 touching solids → one fused solid), which
everything downstream (cache, oracle, tests) builds on.

## Dependencies
- PLAN.md + NOTES.md read first.
- Existing `base.py` (current Ø150 geometry) as the thing being replaced.

## Responsibilities
Owns: `base.py` params block (base/lug/screw/wire), `lock_lug()` + `base_plate()`,
the ring pocket, and removing dead slice-based helpers from the build path.
Does **not** touch: the cap (`mount_plate`, `rim_channel`, `lock_channel`) —
that is phase 2. Does not rebuild caches or edit tests.

## Geometry targets (params at top of base.py)
- `plate_radius = 50.0`, `plate_thickness = 3.0`, `wire_hole_radius = 20.0` (Ø40).
- `screw_hole_radius = 39.0` (KEEP — 78 mm chord), `screw_angles = [90, 270]`.
  Screws default to M4 pan head: `screw_through_r = 2.25`, counterbore `r 4.1 × 2.0`
  (1.0 mm skin) — real plug type to be confirmed on-site, keep parametric.
- Lugs: `lock_protrusion = 2.0`, `lug_width = 14.0` (arc, mm), `lug_angles = [0, 120, 240]`,
  `lock_height = plate_thickness` (full height), `lip_h = 1.2` (tip step-down),
  `root_fillet = 0.8`. Derived: `lug_tip_r = plate_radius + lock_protrusion` (52).
- Ring pocket: `base_pocket_inner = 30.0`, `base_pocket_outer = 48.0`,
  `base_pocket_depth = 1.2` (leaves 1.8 mm skin), screw bosses keep full depth.
- Assembly: `mount_offset_z = (2 + plate_thickness) − (cap_disc_h + cap_skirt_h)`
  (formula unchanged; value changes once phase 2 sets the cap depths).
- Lug profile: full 3 mm height at root (r ≤ ~51.4), stepped down to a 1.2 mm lip
  (lip top native z = 1.2, = assembly z 3.2) over the outer ~0.6 mm (r 51.4..52).
  Root fillet 0.8 on the rim junction. Build directly (extrude/loft a rib on the
  rim, revolve threefold), NO `cylindric_bend`.

## Todos
- [ ] Rewrite the params block (sizes, lug params, derived `lug_tip_r`, screw/wire/pocket).
- [ ] Implement `lock_lug()` as one monolithic solid per lug (full-height rib,
      stepped tip lip, 0.8 mm root fillet) and wire it via `threefold_pattern(fuse=True)`.
- [ ] Update `base_plate()`: fuse to a single solid (drop the Compound-of-73
      bundling); keep the ring pocket + screw holes.
- [ ] Remove `cylindric_bend`, `lock_tab`, `lock_tab_linear`, and `lip_prism`/
      `hull_solid`/`lock_channel_linear` from the build path (drop the
      `lock_channel_linear` debug view; keep `convex_hull_2d` only if still used).
- [ ] Smoke-check: `python -c "from base import *; b=base_plate(); print(b.Volume(), len(b.Solids()))"`.

## Acceptance criteria
- `base_plate()` builds in reasonable time; volume ≈ 14–17 cm³ (target 14.7).
- Base is **1 solid** (single fused solid, no slice-seam compounds).
- No references to `cylindric_bend` / `lock_tab_linear` remain in the build path.
- `test_parameters.py` may be red (expects old radii) — that is fine; it is fixed in phase 4.
