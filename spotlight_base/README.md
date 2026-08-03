# Spotlight Twist-Lock Ceiling Mount

CadQuery ceiling-mount twist-lock spotlight base (`base.py`). An Ø100 base plate screws to flat plaster using the existing 78 mm-spaced holes, an Ø108 cap twists ~10° over it, and a Ø40 spotlight screws onto the cap.

## Design

- **Base:** Ø100 (`plate_radius` 50) × 3 mm, central Ø40 wire hole, 2× M4 counterbored screw holes at r=39. The underside ring pocket spans r30–48 and leaves a 1.8 mm skin.
- **Lock:** three monolithic, revolve-built lugs at 0°/120°/240°. Each lug is 14 mm of rim arc, 2 mm proud, 3 mm high at the root, with a 1.2 mm stepped lip and 0.8 mm fused-root fillets.
- **Cap:** Ø108 (`cap_radius` 54), 2 mm disc, 13 mm skirt, 1.8 mm wall ring, 0.4 mm bottom-edge chamfer, and three channels 10° behind the lugs (`ch_ang_rot = -10`): drop-on at `rot=0`, seat at `rot=10`.
- **Spotlight mount:** flat disc with no central boss, Ø2.9 pilot through the disc, Ø8 wire-exit hole, and a cup-side r8–48 pocket leaving a 1 mm floor.

## Derived lock radii — never hardcode

The channel stays aligned to the actual lugs through derived radii:

```text
lug_tip_r = plate_radius + lock_protrusion  # 52
ch_roof_in = lug_tip_r - roof_capture       # 51.5
ch_wall_in = lug_tip_r + ch_clear            # 52.2
ch_bury   = 0.15                             # channel burial into the wall ring
```

The roof inner radius is outside the lug full-height root (`lug_step_r = 51.5`) so the twist does not graze the root. `ch_bury` overlaps the roof and back-wall slab past `ch_wall_in` into the solid wall ring so `mount_plate()` fuses into ONE solid — the slicer detects the skirt cavity instead of filling it with solid infill (the old 4-solid double wall cost hours of print time).

## Key decisions

- Twist lock on the outer rim with three-way symmetry; the wire path and cavity remain unobstructed.
- Compact Ø100 base / Ø108 cap; no Ø150 canopy exists to cover.
- Solid thin cap disc hides the base and screws while supporting the Ø40 spotlight.
- The cap skirt reaches the ceiling and encloses the base edge and screw heads.
- `rim_channel()` uses annular-sector unions for the outer wall, roof overhang, and back-wall slab. The back-wall stop is not represented by a difference-based void.
- Monolithic lugs replace the old `cylindric_bend` slice path, removing its accepted seam/non-manifold artifact.
- The bottom lip is a 0.4 mm chamfer (not the old 2 mm curved fillet) so the full-perimeter bottom overhang / support requirement disappears.

## Measured fit (OCC kernel, 2026-08-02)

| Quantity | Value |
|---|---|
| Lug angular center | 0° |
| Lug tip radius | 52 mm |
| Lug lip top, assembly frame | z=3.2 mm |
| Channel roof bottom, seated assembly frame | z=4.0 mm |
| Seat roof clearance | 0.8 mm |
| Channel roof thickness | 1.0 mm |
| Back-wall stop onset | approximately `rot=11.5–12°` (free through ~11.5 after the back-wall enlargement) |
| Pullout roof catch | approximately 1.0–1.5 mm mount drop in sparse probe |
| Tilt probes | pass at -0.5 mm and +0.3 mm assembly shifts |

## Verification — pytest is the only trusted oracle

```bash
source /home/ubuntu/workspace/.venv/bin/activate
python -m pytest spotlight_base/tests -q
```

The suite probes the cached fused solids (`base_fused.brep` = 1 solid,
14.63 cm³; `mount_fused.brep` = 1 solid, 18.92 cm³) with
`BRepClass3d_SolidClassifier`. Total modeled volume is 33.55 cm³, approximately
41.6 g at PLA density 1.24 g/cm³. Do not use trimesh, pymeshfix, or manifold3d.

- **Tiers:** parameter invariants → classifier oracle → seat / rotation / pullout / tilt / strength integration tests.
- **Frame:** assembly only; base at z 2..5, mount origin at `mount_offset_z = -10`, seated mount rotation `rot=10`.
- Treat both `IN` and `ON` as occupied. Load cached BREP solids rather than re-fusing them in probes.

## Layout

- `base.py` — model and view modes (`assembled`, `base_plate`, `mount_plate`, `diff_check`).
- `tests/` — deterministic verification suite and the assembly-frame OCC probe.
- `scripts/rebuild_cache.py` — regenerate cached BREP solids.
- `.cache/` — tracked fused-solid caches.
- `output/` — exported STEP and STL files.

## Process

Plans live in `docs/plans/`. Delete a plan folder once all its phases are done; distill must-keep facts into this README first. Only pending plans remain.
