# Spotlight Twist-Lock Mount

CadQuery project: `spotlight_base/base.py`. Ceiling-mount twist-lock spotlight
base: an Ø150 base plate screws to the real Ø150 ceiling base, a Ø156 cap
(mount plate) twists ~10° over it, and a spotlight screws onto the cap.

## Verification (run first on any change)

```bash
source /home/ubuntu/workspace/.venv/bin/activate
python -m pytest spotlight_base/tests -q        # ~8 s, must stay < 60 s
```

The suite is the only trusted verification. It probes the cached fused solids
(`spotlight_base/.cache/base_fused.brep` = 1 solid 49.3 cm³, `mount_fused.brep`
= 4 solids 42.1 cm³) with OCC `BRepClass3d_SolidClassifier` — the only tool
correct on this model's double-walled tessellation. **Do not use trimesh /
pymeshfix / manifold3d** (all proven wrong; removed from the venv).

Tiers: `test_parameters.py` (pure-arithmetic invariants) → `test_classifier.py`
(**oracle**, gates everything — if it fails, STOP and fix the probe, not the
design) → `test_seat_fit.py` / `test_rotation.py` / `test_pullout.py` /
`test_strength.py` (sparse assembly-frame integration, ≤ 200 pts/pose).

Frame discipline: assembly frame ONLY — base at z 2..6, mount origin at
`mount_offset_z = -10.5`; seat pose is mount rotation +10 (`rot=10`). See
`docs/plans/verification-handoff.md` + `verification-test-plan.md`.

## Key parameters (top of `base.py`)

- Base: `plate_radius` (75, Ø150), `plate_thickness` (4), `wire_hole_radius`
  (25), `screw_*` (M4 at r=39 → 78 mm chord, counterbored flush). Underside
  ring pocket `base_pocket_outer` (66) saves ~13 cm³.
- Lock: `lock_width` (8), `lock_protrusion` (1.5), `lock_taper`/`lock_height`/
  `lock_gap_height`, `bend_steps` (24). Derived: `tab_tip_r = tab_bend_r −
  1.25 + lock_protrusion` (76.25); `ch_roof_in = tab_tip_r − roof_capture`
  (75.65); `ch_wall_in = tab_tip_r + ch_clear` (76.45). `rim_channel()` +
  `mount_plate()` must keep using the derived radii (a stale `50.75 + ch_clear`
  / `plate_radius + 1.0` hardcode silently re-buries the channel in the base).
- Cap: `cap_radius` (78, Ø156), `cap_disc_h` (2.5), `cap_skirt_h` (14),
  `ch_*` (channel groove angles/radii). Cup-side disc pocket
  `disc_pocket_*` (r8–68, 1 mm deep, 1.5 mm floor) saves ~13 cm³.

## Design notes

- Twist lock on the outer rim, 3-way radial symmetry via `threefold_pattern()`
  at 0°/120°/240°. Channels sit 10° behind (`ch_ang_rot = -10`): drop-on at
  `rot=0`, seat at `rot=10`.
- **Measured (via the OCC kernel, 2026-08-02):** tab center 0°, tip r≈76.0
  (crest tapers 2.4 at root r≤75.0 → ~1.0 at tip), back-wall stop onset
  `rot≈12` (NOT the earlier handoff guess of 18), pullout roof catch at drop
  ~0.3–0.5 mm, seat has ~0.3–0.5 mm roof clearance (no interference).
- Mount has **no central boss** (removed by design; docs mentioning a Ø9.5
  boss are stale). The spotlight mounts on the flat disc; Ø2.9 pilot goes
  through the disc.
- `rim_channel()` builds each groove from annular sectors (outer wall + roof
  overhang + back-wall slab) — no difference-based void, so the back-wall stop
  survives.
- `cylindric_bend()` bends flat lip geometry along `bend_r = plate_radius +
  1.0` in touching slices. Known artifact: slice boundaries create coincident
  faces → CGAL reports non-manifold edges / extra volumes; accepted as-is.
