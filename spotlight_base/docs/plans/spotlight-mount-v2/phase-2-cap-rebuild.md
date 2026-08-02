# Phase 2: Cap rebuild — Ø108 thin disc + retuned channels

## Estimated effort
~6 minutes / 5 todos.

## Objective
Rebuild the cap on the new Ø108 envelope: 2 mm disc with a 1 mm cup-side pocket,
13 mm skirt reaching the ceiling, 1.8 mm wall ring, and channels retuned to the
new monolithic lug (phase 1's `lug_tip_r = 52`). The retuned channel parameters
are the fit contract the oracle/integration phases verify.

## Dependencies
- Phase 1 `done` (lug radii must exist in `base.py`).
- PLAN.md + NOTES.md read first.

## Responsibilities
Owns: cap params, `rim_channel()`, `lock_channel()`, `mount_plate()`.
Does **not** touch: the base (`base_plate`, `lock_lug`), tests, caches.

## Geometry targets
- `cap_radius = 54.0` (Ø108), `cap_disc_h = 2.0`, `cap_skirt_h = 13.0`.
- `mount_offset_z = (2 + plate_thickness) − (cap_disc_h + cap_skirt_h)` = 5 − 15 = **−10**.
- Wall ring: `ch_wall_in = lug_tip_r + ch_clear` (52.2) → wall 54 − 52.2 = 1.8 mm.
- `ch_roof_in = lug_tip_r − roof_capture` (51.4) with `roof_capture = 0.6`; roof
  inner radius must sit OUTSIDE the lug's full-height root (r ≥ step radius ≈ 51.4)
  so the twist never grazes it.
- Channel z-bands (mount-local): groove floor `ch_groove_bot` so the lug lip
  rides with clearance; roof bottom = lip top + 0.8 mm seat clearance;
  **roof top at the ceiling plane** (`ch_block_top` such that roof ≥ 1.0 mm thick).
- Channel angular window retuned for a 14 mm lug on r50 (half-angle ≈ 8°):
  widen `ch_back_wall` / `ch_front` so the lug enters at drop (rot 0) and stops
  at the back wall ~12–13°; keep `ch_ang_rot = -10`.
- Disc pocket: `disc_pocket_outer = 48.0`, `disc_pocket_inner = 8.0`,
  `disc_pocket_depth = 1.0` (1.0 mm visible floor; full thickness under the pilot).
- Keep: Ø8 wire exit at r 12, Ø2.9 pilot through the disc. No central boss.
- Keep the additive `rim_channel()` construction (no difference-based void) —
  only radii/z/angles change.

## Todos
- [ ] Update cap params (radius, disc, skirt, wall, pocket, mount_offset_z).
- [ ] Retune `rim_channel()` / `lock_channel()` to the new lug (derived radii,
      z-bands, angular window).
- [ ] Update `mount_plate()` (disc pocket, wire exit, pilot; solid thin disc).
- [ ] Verify the roof's inner radius clears the lug root during the full twist
      sweep (geometric reasoning + a classifier spot check if quick).
- [ ] Smoke-check: `python -c "from base import *; m=mount_plate(); print(m.Volume(), len(m.Solids()))"`.

## Acceptance criteria
- `mount_plate()` builds; volume ≈ 18–22 cm³ (target 19.5).
- Derived radii chain intact: `ch_wall_in == lug_tip_r + ch_clear`,
  `ch_roof_in == lug_tip_r − roof_capture`.
- Roof bottom − lip top (assembly z) ≥ 0.6 mm; roof thickness ≥ 1.0 mm.
