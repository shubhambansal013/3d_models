# Spotlight Twist-Lock Ceiling Mount

CadQuery ceiling-mount twist-lock spotlight base (`base.py`). An Ø150 base
plate screws flat to the real Ø150 ceiling base, an Ø156 cap twists ~10° over
it, and the spotlight screws onto the cap.

## Design

- **Base (ceiling side):** Ø150 annulus (`plate_radius` 75) × 4 mm, central
  Ø50 wire hole, 2× M4 socket-head screws counterbored flush at r=39 (78 mm
  chord — matches the real ceiling hole spacing). Underside ring pocket
  r28–66 saves ~13 cm³.
- **Lock:** 3 tabs on the base outer rim at 0°/120°/240° (`lock_width` 8,
  `lock_protrusion` 1.5), built by bending flat lip geometry along
  `bend_r = plate_radius + 1.0` in 24 touching slices (`cylindric_bend`).
- **Cap (light side):** Ø156 (`cap_radius` 78), 2.5 mm disc + 14 mm skirt
  reaching the ceiling (hides base + screws), 3 rim channels 10° behind the
  tabs (`ch_ang_rot = -10`): drop-on at `rot=0`, seat at `rot=10`.
- **Spotlight mount:** the spotlight screws onto the flat disc — **no central
  boss** (removed by design). A Ø2.9 self-tap pilot goes through the disc.
  Cup-side disc pocket r8–68 saves ~13 cm³.

## Derived lock radii — never hardcode

The channel is kept glued to the actual tab by deriving all lock radii from
`plate_radius`. A stale hardcode (e.g. `50.75 + ch_clear` or
`plate_radius + 1.0` in the mount) silently re-buries the channel in the base.

```
tab_bend_r = plate_radius + 1.0              # bend axis radius
tab_root_r = tab_bend_r - 1.25               # tab root radius
tab_tip_r  = tab_root_r + lock_protrusion    # 76.25
ch_roof_in = tab_tip_r - roof_capture        # 75.65  (roof overhang inner r)
ch_wall_in = tab_tip_r + ch_clear            # 76.45  (channel wall inner r)
```

## Key decisions

- **Twist lock on the outer rim** (3-way symmetry), not a central hub — leaves
  the wire path and cavity unobstructed. User-chosen.
- **Ø156 cap over Ø150 base:** 3 mm overhang hides the base edge from the side.
- **Skirt reaches the ceiling:** base and screw heads fully enclosed.
- **Screws counterbored flush** (socket-head M4) so the cap face clears them.
- **No central boss** (user-confirmed): the spotlight mounts on the flat disc
  via a Ø2.9 self-tap pilot. Any doc mentioning a Ø9.5 boss is stale.
- **`rim_channel()` is built from annular-sector unions** (outer wall + roof
  overhang + back-wall slab) — NOT a difference-based void — so the back-wall
  rotation stop survives the boolean.
- **Known artifact (accepted):** `cylindric_bend()` slice boundaries create
  coincident faces → CGAL reports non-manifold edges / extra volumes. Do not
  chase it; the OCC classifier probes still work.

## Measured fit (OCC kernel, 2026-08-02)

| Quantity | Value |
|---|---|
| Tab angular center | 0° (tabs on fold axes) |
| Tab tip radius | ≈ 76.0 (crest tapers 2.4 at root r≤75 → ~1.0 at tip) |
| Back-wall stop onset (from seat `rot=10`) | `rot≈12` (NOT the earlier 18 guess) |
| Pullout roof catch (mount drop) | ~0.3–0.5 mm |
| Seat roof clearance | ~0.3–0.5 mm (no interference) |

## Verification — pytest is the only trusted oracle

```bash
source /home/ubuntu/workspace/.venv/bin/activate
python -m pytest spotlight_base/tests -q      # ~8 s, budget < 60 s
```

The suite probes the cached fused solids (`spotlight_base/.cache/base_fused.brep`
= 1 solid 49.3 cm³, `mount_fused.brep` = 4 solids 42.1 cm³) with OCC
`BRepClass3d_SolidClassifier` — the only tool correct on this model's
double-walled tessellation. **Do not use trimesh / pymeshfix / manifold3d**
(all proven wrong; removed from the venv).

- **Tiers:** `test_parameters.py` (pure-arithmetic invariants) →
  `test_classifier.py` (**oracle**, gates everything — if it fails, STOP and
  fix the probe, not the design) → `test_seat_fit.py` / `test_rotation.py` /
  `test_pullout.py` / `test_strength.py` (sparse assembly-frame integration,
  ≤ 200 pts/pose).
- **Frame discipline:** assembly frame ONLY — base at z 2..6, mount origin at
  `mount_offset_z = -10.5`; seat pose is mount rotation +10 (`rot=10`).
  Expected values come from `base.py` params, never from eyeballed output.
- **Anti-iteration rules:** classifier first; assert, don't eyeball; one
  surprise → one new targeted assertion (never re-run a 20-pose sweep); params
  are the spec; sparse sampling by construction; never add a mesh-repair path.

### OCC API gotchas

- `BRepClass3d_SolidClassifier(S, pnt, tol)` and `.Perform(pnt, tol)` both
  require the tolerance argument (no 2-arg / 1-arg forms).
- Treat `IN` **and** `ON` as occupied.
- Read the `.brep` cache via `BRepTools.Read_s` + `BRep_Builder` +
  `TopExp_Explorer`; always iterate `.Solids()` (the mount is 4 solids; OCC
  won't merge coincident-face solids). Re-fusing the base takes ~75 s — load
  the cache, never re-fuse in a long script.

## Layout

- `base.py` — the model (`VIEW_MODE` switch: assembled / base_plate /
  mount_plate / diff_check).
- `tests/` — the verification suite (`conftest.py` holds the one true assembly
  frame + the OCC probe).
- `scripts/rebuild_cache.py` — regenerate `.cache/*.brep` fused solids.
- `.cache/` — cached fused solids (tracked; regenerate only on geometry change).
- `output/` — exported `base.step` / `base.stl` / `mount.step` / `mount.stl`.

## Process

Plans live in `docs/plans/`. A plan folder is deleted once all its phases are
done — must-keep facts are distilled into this README first; git history keeps
the rest. Only pending plans remain.
