# Spotlight Twist-Lock Ceiling Mount

CadQuery ceiling-mount twist-lock spotlight base (`base.py`). An Ø100 base plate screws to flat plaster using the existing 78 mm-spaced holes, an Ø108 cap twists ~10° over it, and a Ø40 spotlight screws onto the cap.

## Design

- **Base:** Ø100 (`plate_radius` 50) × 3 mm, central Ø40 wire hole, 2× M4 counterbored screw holes at r=39. The underside ring pocket spans r30–48 and leaves a 1.8 mm skin.
- **Lock:** three monolithic, revolve-built lugs at 0°/120°/240°. Each lug is 14 mm of rim arc and a 3 mm-wide × 1.2 mm-tall shelf (r 49–52) with no upper rib; the roof overhangs 1.5 mm past the tip (`roof_capture`) and grips the shelf's outer 1.5 mm band on pullout. The roof inner radius (r 50.5) stays **outside** the plate radius (r 50), so the mount detaches: reverse-twist to `rot ≈ -21` clears the roof from every lug and the plate rim, then it pulls straight off.
- **Cap:** Ø108 (`cap_radius` 54), 2 mm disc, 13 mm skirt, 1.8 mm wall ring, 0.4 mm bottom-edge chamfer, and three channels 10° behind the lugs (`ch_ang_rot = -10`): drop-on at `rot=0`, seat at `rot=10`.
- **Spotlight mount:** flat disc with no central boss, Ø2.9 pilot through the disc, Ø8 wire-exit hole, and a cup-side r8–48 pocket leaving a 1 mm floor.

## Derived lock radii — never hardcode

The channel stays aligned to the actual lugs through derived radii:

```text
lug_tip_r = plate_radius + lock_protrusion   # 52
lug_step_r = plate_radius - 1.0              # 49  (shelf lip inner radius; overlaps the plate ring)
ch_roof_in = lug_tip_r - roof_capture        # 50.5 (roof overhang inner radius; OUTSIDE the plate)
ch_wall_in = lug_tip_r + ch_clear            # 52.4
ch_bury   = 0.15                             # channel burial into the wall ring
relief_in = lug_step_r - 0.2                 # 48.8 (plate top-rim relief)
```

`lug_step_r` is decoupled from `roof_capture` and overlaps the plate ring
(r 49–50) so the base stays ONE solid. The roof inner radius (`ch_roof_in`)
sits **outside** the plate radius — this is the radial-trap fix: a roof that
reaches inside the plate embeds in the rim and the mount can *never* detach
(the old 3 mm grip was trapped; it required a ~21° reverse twist AND could
not pull off). With the roof at r 50.5 it clears both the plate rim and every
lug at `rot ≈ -21`, so the reverse-twist detach is force-free. The roof grips
the shelf's outer 1.5 mm band on pullout. The plate's ceiling-side rim relief
is retained from the 3 mm-grip design (no mechanical role now, just a
lightening cut over the channel arcs). `ch_bury` overlaps the roof and
back-wall slab past `ch_wall_in` into the solid wall ring so `mount_plate()`
fuses into ONE solid — the slicer detects the skirt cavity instead of filling
it with solid infill (the old 4-solid double wall cost hours of print time).

## Key decisions

- Twist lock on the outer rim with three-way symmetry; the wire path and cavity remain unobstructed.
- Compact Ø100 base / Ø108 cap; no Ø150 canopy exists to cover.
- Solid thin cap disc hides the base and screws while supporting the Ø40 spotlight.
- The cap skirt reaches the ceiling and encloses the base edge and screw heads.
- `rim_channel()` uses annular-sector unions for the outer wall, roof overhang, and back-wall slab. The back-wall stop is not represented by a difference-based void.
- Monolithic lugs replace the old `cylindric_bend` slice path, removing its accepted seam/non-manifold artifact.
- The bottom lip is a 0.4 mm chamfer (not the old 2 mm curved fillet) so the full-perimeter bottom overhang / support requirement disappears.
- The lock grip is 1.5 mm (`roof_capture`): each lug is a low shelf (no upper rib) so the roof can overhang 1.5 mm inside the tip and grip the shelf's outer band. The roof stays outside the plate radius (`ch_roof_in` 50.5 > 50), so the mount can actually detach — reverse-twist to `rot ≈ -21` then pull. (The earlier 3 mm grip reached r 49 inside the plate rim and could not detach at all — the radial-trap regression this design fixes.)

## Measured fit (OCC kernel, 2026-08-03)

| Quantity | Value |
|---|---|
| Lug angular center | 0° |
| Lug tip radius | 52 mm |
| Shelf lip band | r 49–52 mm (3 mm catch surface) |
| Shelf lip top, assembly frame | z=3.2 mm |
| Channel roof bottom, seated assembly frame | z=4.0 mm |
| Channel roof inner radius | 50.5 mm (1.5 mm overhang past the tip; OUTSIDE the plate radius — the radial-trap fix) |
| Seat roof clearance | 0.8 mm |
| Lug-tip ↔ channel-wall sliding clearance | 0.4 mm (`ch_clear`, was 0.2 — that press/snap gap bound the twist under FDM drift) |
| Channel roof thickness | 1.0 mm |
| Back-wall stop onset | approximately `rot=11.5–12°` (free through ~11.5 after the back-wall enlargement) |
| Pullout roof catch | approximately 0.8 mm mount drop (roof meets the shelf's outer 1.5 mm band) |
| **Detach** | force-free reverse twist to `rot ≈ -21` (roof clears lugs angularly at `rot < -20`), then straight pull-down — collision-free through full separation (probed to z_off −3.5). Straight pull at the drop pose still binds (the 1.5 mm lock grip, by design). |
| Tilt probes | pass at -0.5 mm and +0.3 mm assembly shifts |

## Verification — pytest is the only trusted oracle

```bash
source /home/ubuntu/workspace/.venv/bin/activate
python -m pytest spotlight_base/tests -q
```

The suite probes the cached fused solids (`base_fused.brep` = 1 solid,
14.27 cm³; `mount_fused.brep` = 1 solid, 18.18 cm³) with
`BRepClass3d_SolidClassifier`. Total modeled volume is 32.45 cm³, approximately
40.2 g at PLA density 1.24 g/cm³. Do not use trimesh, pymeshfix, or manifold3d.

- **Tiers:** parameter invariants → classifier oracle → seat / rotation / pullout / tilt / strength / twist-fit integration tests. `test_twist_fit.py` walks the attach/detach trajectory (drop → seat twist → release → **reverse-twist detach**) and gates the sliding-fit clearances (radial ≥ 0.3 mm, roof ≥ 0.6 mm) that a no-collision probe misses. It also gates the radial-trap: the roof must clear the plate radius (`ch_roof_in > plate_radius`), else the mount can never detach.
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
