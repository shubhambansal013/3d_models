# Spotlight Twist-Lock Mount

CadQuery project: `spotlight_base/base.py`. Ceiling-mount twist-lock spotlight
base: an Ø100 base plate screws to flat plaster using the existing 78 mm-spaced
holes, a Ø108 cap twists ~10° over it, and a Ø40 spotlight screws onto the cap.

## Verification (run first on any change)

```bash
source /home/ubuntu/workspace/.venv/bin/activate
python -m pytest spotlight_base/tests -q        # ~8 s, must stay < 60 s
```

The suite is the only trusted verification. It probes the cached fused solids
(`spotlight_base/.cache/base_fused.brep` = 1 solid 14.27 cm³, `mount_fused.brep`
= 1 solid 18.18 cm³) with OCC `BRepClass3d_SolidClassifier` — the only tool
correct on this model. Total modeled volume is
32.45 cm³, approximately 40.2 g at PLA density 1.24 g/cm³. **Do not use
trimesh / pymeshfix / manifold3d** (all proven wrong; removed from the venv).

Tiers: `test_parameters.py` (pure-arithmetic invariants) → `test_classifier.py`
(**oracle**, gates everything — if it fails, STOP and fix the probe, not the
design) → `test_seat_fit.py` / `test_rotation.py` / `test_pullout.py` /
`test_strength.py` / `test_tilt.py` / `test_twist_fit.py` (sparse
assembly-frame integration, ≤ 200 pts/pose). `test_twist_fit.py` walks the
full attach/detach trajectory (drop → seat twist → release → **reverse-twist
detach**) AND gates the sliding-fit clearances (radial gap ≥ 0.3 mm, roof gap
≥ 0.6 mm) — a no-collision probe alone missed the 0.2 mm press-fit bind. It
also gates the radial-trap: `ch_roof_in` must stay > `plate_radius`, else the
mount can never detach.

Frame discipline: assembly frame ONLY — base at z 2..5, mount origin at
`mount_offset_z = -10`; seat pose is mount rotation +10 (`rot=10`). See
`spotlight_base/README.md` (design, key decisions, golden numbers, OCP
gotchas).

Process: plans live in `spotlight_base/docs/plans/`; delete a plan folder once
all its phases are done (distill must-keep facts into the README first). Only
pending plans remain.

## Key parameters (top of `base.py`)

- Base: `plate_radius` (50, Ø100), `plate_thickness` (3), `wire_hole_radius`
  (20, Ø40), `screw_*` (M4 at r=39 → 78 mm chord, counterbored flush).
  Underside ring pocket `base_pocket_outer` (48) saves material.
- Lock: monolithic shelf `lug_width` (14 mm arc), `lock_protrusion` (2),
  `lock_height` (3), `lip_h` (1.2), `roof_capture` (1.5 — the lock grip;
  the roof stays OUTSIDE the plate radius so the mount can detach).
  Derived: `lug_tip_r = plate_radius + lock_protrusion` (52),
  `lug_step_r = plate_radius − 1` (49, decoupled from roof_capture so the
  shelf overlaps the plate ring), `ch_roof_in = lug_tip_r − roof_capture`
  (50.5 > plate_radius 50 — the radial-trap fix), `ch_wall_in = lug_tip_r +
  ch_clear` (52.4), and `ch_bury` (0.15) — the burial that makes
  `mount_plate()` fuse the channels into ONE solid. The plate's ceiling-side
  rim relief (`relief_in` 48.8) is retained but vestigial (no longer needed
  now the roof is outside the plate).
  `rim_channel()` + `mount_plate()` must keep using the derived radii.
- Cap: `cap_radius` (54, Ø108), `cap_disc_h` (2), `cap_skirt_h` (13),
  `cap_chamfer` (0.4 bottom-edge chamfer), `ch_*` (channel groove
  angles/radii). Cup-side disc pocket `disc_pocket_*` (r8–48, 1 mm deep,
  1 mm floor).

## Design notes

- Twist lock on the outer rim, 3-way radial symmetry via `threefold_pattern()`
  at 0°/120°/240°. Channels sit 10° behind (`ch_ang_rot = -10`): drop-on at
  `rot=0`, seat at `rot=10`.
- **Measured (via the OCC kernel, 2026-08-03):** lug center 0°, tip r=52,
  shelf lip r 49–52, back-wall stop onset `rot≈11.5–12°` (after the
  back-wall enlargement), pullout roof catch at mount drop ≈ 0.8 mm (roof
  meets the shelf's outer 1.5 mm band), seat roof clearance 0.8 mm. **Detach
  (2026-08-04):** force-free reverse twist to `rot ≈ -21` (roof clears the
  lugs angularly for `rot < -20`) then straight pull-down — collision-free
  through full separation (probed to z_off −3.5); straight pull at the drop
  pose still binds (the 1.5 mm lock grip, by design). The tilt probes pass
  at -0.5 mm and +0.3 mm assembly shifts.
- Mount has **no central boss**. The spotlight mounts on the flat disc; Ø2.9
  pilot goes through the disc.
- `rim_channel()` builds each groove from annular sectors (outer wall + roof
  overhang + back-wall slab) — no difference-based void, so the back-wall stop
  survives.
- Monolithic revolve-built lugs replace the old `cylindric_bend` slice path;
  the accepted slice-boundary non-manifold artifact is no longer part of the
  build path.
