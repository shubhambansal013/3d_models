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
(`spotlight_base/.cache/base_fused.brep` = 1 solid 14.63 cm³, `mount_fused.brep`
= 4 solids 18.03 cm³) with OCC `BRepClass3d_SolidClassifier` — the only tool
correct on this model's double-walled tessellation. Total modeled volume is
32.66 cm³, approximately 40.5 g at PLA density 1.24 g/cm³. **Do not use
trimesh / pymeshfix / manifold3d** (all proven wrong; removed from the venv).

Tiers: `test_parameters.py` (pure-arithmetic invariants) → `test_classifier.py`
(**oracle**, gates everything — if it fails, STOP and fix the probe, not the
design) → `test_seat_fit.py` / `test_rotation.py` / `test_pullout.py` /
`test_strength.py` (sparse assembly-frame integration, ≤ 200 pts/pose).

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
- Lock: monolithic `lug_width` (14 mm arc), `lock_protrusion` (2),
  `lock_height` (3), `lip_h` (1.2), `root_fillet` (0.8). Derived:
  `lug_tip_r = plate_radius + lock_protrusion` (52),
  `ch_roof_in = lug_tip_r − roof_capture` (51.5), and
  `ch_wall_in = lug_tip_r + ch_clear` (52.2). `rim_channel()` +
  `mount_plate()` must keep using the derived radii.
- Cap: `cap_radius` (54, Ø108), `cap_disc_h` (2), `cap_skirt_h` (13),
  `ch_*` (channel groove angles/radii). Cup-side disc pocket
  `disc_pocket_*` (r8–48, 1 mm deep, 1 mm floor).

## Design notes

- Twist lock on the outer rim, 3-way radial symmetry via `threefold_pattern()`
  at 0°/120°/240°. Channels sit 10° behind (`ch_ang_rot = -10`): drop-on at
  `rot=0`, seat at `rot=10`.
- **Measured (via the OCC kernel, 2026-08-02):** lug center 0°, tip r=52,
  back-wall stop onset `rot≈12–13°`, pullout roof catch at mount drop
  approximately 1.0–1.5 mm in the sparse probe, seat roof clearance 0.8 mm.
  The tilt probes pass at -0.5 mm and +0.3 mm assembly shifts.
- Mount has **no central boss**. The spotlight mounts on the flat disc; Ø2.9
  pilot goes through the disc.
- `rim_channel()` builds each groove from annular sectors (outer wall + roof
  overhang + back-wall slab) — no difference-based void, so the back-wall stop
  survives.
- Monolithic revolve-built lugs replace the old `cylindric_bend` slice path;
  the accepted slice-boundary non-manifold artifact is no longer part of the
  build path.
