# Plan: Spotlight Mount v2 — Compact Ø100/Ø108, Beefed Twist-Lock, ~60% Lighter

## Overview
Rework `spotlight_base/base.py` (CadQuery) from the current Ø150/Ø156 twist-lock
ceiling mount into a compact Ø100/Ø108 mount. Ground truth (user-confirmed):
the ceiling is **flat plaster** with a center wire hole and **two existing screw
holes 78 mm apart** (rawl-plugged) — there is NO Ø150 canopy to cover, and the
spotlight is **Ø40, not Ø80**. The current design has three confirmed flaws:
(1) the lock's 0.3–0.5 mm vertical engagement window is tied to the ceiling
plane via `mount_offset_z`, so plate tilt/gaps jam the seat; (2) the 8×3×1.5 mm
tabs built from 24 `cylindric_bend` slices have un-filleted, seam-ridden roots
(known non-manifold artifact) that break under hand force; (3) 91.4 cm³ ≈ 113 g
of filament (base 49.25, mount 42.10 cm³).

New design: **monolithic filleted lugs** (14 mm arc × full 3 mm height, 2.0 mm
proud → tip r 52, ~1.2 mm stepped lip at the tip) on a Ø100×3 base; Ø108 cap
with 2 mm disc + 1 mm cup-side pocket, 13 mm skirt reaching the ceiling, wall
ring 1.8 mm, and **0.8 mm roof clearance** (2.7× current tilt tolerance) with a
≥1.0 mm roof. Target ≈ 34 cm³ ≈ **42 g (~62% lighter)**. The lock hangs on the
lugs at rest, so the ceiling stops being the vertical datum; the monolithic lugs
also kill the slice-artifact, so the base becomes a genuine fused single solid.

## Goals
- Fix flush/tilt failure: seat clearance 0.3 → **0.8 mm**, roof ≥ 1.0 mm; locked
  by a NEW tilt test in the suite.
- Fix tab breakage: monolithic lugs, ~3× shear area, root fillets; strength test
  re-modeled at hand force (25 N pull / 2 N·m twist), FoS ≥ 5.
- Cut filament to ≈ 42 g (≤ ~45 g budget) from 113 g.
- Compact to Ø100 base / Ø108 cap; keep 78 mm screw spacing and the 10° twist.
- Remove `cylindric_bend` from the build path; base fuses to a single clean solid.

## Non-goals
- No change to the 78 mm screw spacing; the real anchor/screw type is confirmed
  on-site and `screw_*` stays parametric (default M4 pan head, Ø8.2 × 2.0 cbore).
- No magnets, glue, clips, or springs.
- No Ø150-size parts; the cap need not cover any Ø150 object.
- No change to the tiered verification methodology or the OCC `BRepClass3d_SolidClassifier` oracle — rebuilt with new golden numbers, oracle gates everything.
- No print-and-inspect verification; pytest stays the only trusted oracle.
- No trimesh/pymeshfix/manifold3d (still prohibited).

## Key decisions
- **Keep beefed-up twist-lock** (user chose over magnets / hybrid).
  Rationale: no added hardware cost, keeps the twist action; monolithic lugs remove the breakage root cause.
- **Compact Ø100 base / Ø108 cap** (user chose).
  Rationale: Ø150/Ø156 existed only to cover an Ø150 canopy that doesn't exist; real constraints are 78 mm screw holes + center wire + Ø40 light.
- **Solid thin cap disc** (user chose over ring+spokes).
  Rationale: a Ø40 light would be lost on an open-spoke cap; solid disc hides the base + screws.
- **Monolithic rim lugs replace `cylindric_bend` slices.**
  Rationale: kills the known non-manifold artifact (AGENTS "known artifact" note becomes stale), enables root fillets, lets `base_plate()` fuse to one solid.
- **Seat clearance 0.8 mm, roof ≥ 1.0 mm thick (roof top at the ceiling plane).**
  Rationale: 2.7× the current 0.3 mm window tolerates plaster tilt; cap hangs on the lugs at rest so the ceiling is no longer the vertical datum; ≤0.8 mm skirt seam accepted as a shadow line.
- **Derived radii:** `lug_tip_r = plate_radius + lock_protrusion` (52),
  `ch_wall_in = lug_tip_r + ch_clear` (52.2), `ch_roof_in = lug_tip_r − roof_capture` (51.4). Roof inner radius must sit OUTSIDE the lug's full-height root (r ≥ step radius) so the twist never grazes it.
- Keep the assembly frame convention (base at z 2..5 for the 3 mm plate; `mount_offset_z = (2 + plate_thickness) − (cap_disc_h + cap_skirt_h)`).

## Phase status

| Phase | Title | Est. | Status | Notes |
|---|---|---|---|---|
| 1 | Base rebuild: Ø100×3 + monolithic lugs | ~6 min | done | `base.py` params + `lock_lug()`, remove `cylindric_bend` path |
| 2 | Cap rebuild: Ø108 thin disc + retuned channels | ~6 min | pending | depends on 1 (lug radii) |
| 3 | Cache rebuild + volume smoke | ~5 min | pending | `scripts/rebuild_cache.py`, new contract ~15 / ~19.5 cm³ |
| 4 | Harness + oracle rebuild (conftest, params, classifier) | ~6 min | pending | gates everything downstream |
| 5 | Integration tests: seat / rotation / pullout / NEW tilt | ~6 min | pending | depends on 4 |
| 6 | Strength model: hand-force, lug section, FoS ≥ 5 | ~4 min | pending | depends on 4 (standalone arithmetic) |
| 7 | Full suite green + exports + renders | ~5 min | pending | depends on 5, 6 |
| 8 | Docs: AGENTS.md, handoff/test-plan golden numbers, PLAN/NOTES | ~5 min | pending | depends on 7 |

Status values: `pending`, `in-progress`, `done`. This table is the first thing
an execution session reads — keep it accurate and up to date at all times.

## Phase files
- `phase-1-base-rebuild.md`
- `phase-2-cap-rebuild.md`
- `phase-3-cache-rebuild.md`
- `phase-4-oracle-rebuild.md`
- `phase-5-integration-tests.md`
- `phase-6-strength-model.md`
- `phase-7-full-suite-exports.md`
- `phase-8-docs.md`

## Shared notes
See `NOTES.md` in this directory: the "Current state & deviations" block at the
top reflects the plan as it stands now; the log below is history.
