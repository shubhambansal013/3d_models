# Plan: Fix Lock-Fit Verification (pytest suite)

> Written 2026-08-02. Companion docs: `../verification-handoff.md` and
> `../verification-test-plan.md` (test catalog + anti-iteration rules).
> The CAD model (`base.py`) is considered DONE; only the verification tooling
> is being rebuilt. This plan replaces the broken `lock_check.py` print-and-
> inspect harness with a deterministic pytest suite.

## Goals
- Make lock-fit verification deterministic and fast: `python -m pytest
  spotlight_base/tests -q` green in < 60 s.
- Single verified probe path: OCP `BRepClass3d_SolidClassifier` on the cached
  fused `.brep` solids. Drop trimesh / pymeshfix / manifold3d entirely (all
  proven wrong on the double-walled tessellation — see handoff §5).
- Fail-fast assertions with explicit tolerances. No print-and-inspect, no
  visual/eyeball debugging.

## Tiered structure (per Gemini plan + test-plan.md)

| Tier | File | What |
|---|---|---|
| 1 | `test_parameters.py` | Pure-arithmetic invariants from `base.py` params, no CAD |
| 2 | `test_classifier.py` | ORACLE: probe correctness on ~20 known in/out points per part — gates everything |
| 3 | `test_seat_fit.py` | Assembly-frame sanity + seat clearance + the seat-interference question |
| 3 | `test_rotation.py` | Back-wall rotation stop |
| 3 | `test_pullout.py` | Roof-overhang pullout catch |
| 3 | `test_strength.py` | Analytic FoS at 100 g, no CAD |

`conftest.py`: fixtures for cache load, single assembly frame, bounded grids.

## Operational rules
1. `test_classifier` first. If it fails → STOP; fix the probe, not the design.
2. One assembly frame ONLY (base z 2..6, mount at `mount_offset_z = −10.5`).
   All expected values derived from `base.py` params, never eyeballed.
3. Sparse sampling by construction: ≤ 200 pts/pose, bounded grids, seeded RNG.
4. One surprise → one new targeted assertion; never re-run a 20-pose sweep.
5. No mesh repair paths; if tessellation is ever needed, fix the model source.

## Key environment facts (verified this session)
- Cached solids load in ~50 ms; classifier probe ~4 ms/pt; base = 1 solid
  (56.7 cm³), mount = 4 solids (55.0 cm³) — matches handoff.
- `pytest 9.1.1` installed in `/home/ubuntu/workspace/.venv`; trimesh/
  pymeshfix/manifold3d uninstalled.
- OCP API: `BRepClass3d_SolidClassifier(solid)` ctor + `.Perform(pnt, tol)`
  (both need the tol arg); treat IN **and** ON as occupied; read `.brep` via
  `BRepTools.Read_s` + `BRep_Builder` + `TopExp_Explorer` (handoff §7).

## Caution (do not hardcode failed-session numbers)
The handoff's golden numbers (tab center 5.6°, tip 76.25, crest 2.40) were
measured during the confused session and may not match the cached geometry
(a quick probe this session measured tab center 0°, tip ≈ 76.0, root crest
2.40 / lip crest ≈ 1.0). Expected values therefore come from `base.py`
params and are validated BY the classifier oracle — the seat-interference
"open question" is settled inside `test_seat_fit` by exact OCC probing.

## Definition of done
- pytest green < 60 s; oracle proves the probe; seat/rotation/pullout pass.
- Results + PASS/FAIL appended to `verification-handoff.md`; AGENTS.md
  verification section updated.
- Model params satisfy `3d-print` skill (roof ≥ 0.8 mm, fit gaps 0.2–0.4).
- Final CAD exports cleanly (`.step` / `.brep`).
