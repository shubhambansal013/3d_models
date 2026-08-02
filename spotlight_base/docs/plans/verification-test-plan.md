# Verification Test-Suite Plan (pytest)

> Written 2026-08-02. Companion to `verification-handoff.md`. Purpose: make the
> lock-fit verification a deterministic, fast, **test-shaped** suite so a future
> session validates in minutes instead of iterating for hours. Do NOT start
> implementing until the "Test of the test" (test_classifier) passes — everything
> else depends on it.

---

## 1. Why the last session burned so many iterations (anti-patterns to kill)

1. **No oracle.** We probed geometry without first proving the probe tool was
   correct on known points → chased tool bugs as if they were design bugs.
2. **Two reference frames, used inconsistently.** base-native (z 0..4, tab crest
   ≈ 2.40) vs assembly (base z 2..6, mount at `mount_offset_z = −10.5`). Expected
   values were computed in one frame, samples in the other, repeatedly.
3. **Brute-force sampling.** 27 k points × 25 classifiers hung the shell. Sampling
   must be sparse and bounded *a priori*.
4. **Unreliable tools used interchangeably.** CSG booleans on the 73-solid base
   compound silently return empty; trimesh/manifold3d/pymeshfix all fail on the
   double-walled tessellation. Only OCP `BRepClass3d_SolidClassifier` is correct.
5. **Print-and-inspect.** Numbers were eyeballed from stdout instead of asserted.

## 2. Architecture

One package, pytest, all fast. Files under `spotlight_base/tests/`:

```
conftest.py           # fixtures: load cached fused .brep, frame constants, sample-grid helpers
test_parameters.py    # pure-arithmetic invariants (no CAD built, sub-ms)
test_classifier.py    # ORACLE: probe correctness on ~20 known in/out points per part
test_seat_fit.py      # integration: frame sanity + seat clearance + the open interference question
test_rotation.py      # integration: back-wall stop
test_pullout.py       # integration: roof catch
test_strength.py      # analytic FoS at 100 g load (no CAD)
```

- Run: `source /home/ubuntu/workspace/.venv/bin/activate && python -m pytest spotlight_base/tests -q`
- Budget: **full suite < 60 s** (cache load 0.1 s + a few hundred classifier calls).

### Frame discipline (single source of truth)

- **Assembly frame ONLY.** base plate at z 2..6, mount at `mount_offset_z = −10.5`
  (roof at z 3.5..4.5, groove floor 1.8, back-wall band 1.8..3.0).
- One helper in conftest: `asm_point(x, y, z)` + `seated(rot, drop)` returning the
  posed mount. No test computes offsets itself.
- Expected values for tests come from **base.py parameters**, never from eyeballed
  output.

## 3. Test catalog (exact assertions)

### 3.1 `test_parameters.py` — invariants from params, no CAD
- `2 * screw_hole_radius == 78.0` (real ceiling-base spacing).
- `tab_tip_r == plate_radius + 0.25 + lock_protrusion` (= 76.25).
- `ch_roof_in == tab_tip_r − roof_capture` (= 75.65).
- `ch_wall_in == tab_tip_r + ch_clear` (= 76.45).
- Roof thickness `ch_block_top − ch_groove_top >= 0.8` (= 1.0).
- Groove height `ch_groove_top − ch_groove_bot >= lock_gap_height` (= 1.7 vs 1.0).
- Cap hides base: `cap_radius − plate_radius >= 3.0` (= 3.0).
- Assembly invariant: `mount_offset_z + cap_disc_h + cap_skirt_h == 2 + plate_thickness` (= 6) — skirt top meets base ceiling face.
- Catch face overlap: back-wall z-band `[ch_groove_bot, ch_groove_top] + mount_offset_z` must overlap the tab z-band in assembly (rotation stop needs it).

### 3.2 `test_classifier.py` — THE ORACLE (run first, gate everything)
Fix ~20 points per part, hand-picked on the known features (annulus inside/outside,
wire hole, screw hole, tab body, tab tip, groove void, roof, back-wall, wall,
hollow, boss, outside cap). Assert `in_base`/`in_mount` equals expected. 
**If any fail → stop. The probe is broken; no downstream test is valid.**

### 3.3 `test_seat_fit.py` — interference question RESOLVED (2026-08-02)
- `test_frame_oracle`: at seat (rot=10, drop=0) the tab-tip zone must match a
  fixed set of explicit expected points. **Resolved: NO interference.** The tab
  lip crest is 3.0–3.4 (assembly), 0.3–0.5 mm below the roof bottom (3.5);
  earlier "0.9 mm into roof" was a measurement artifact.
- `test_seat_clearance`: no sampled tab points inside mount material at seat
  (expect 0, tolerance ±0).
- `test_symmetry`: rotate tab sample points by 120°/240° → identical results
  (catches fold/wiring bugs).

### 3.4 `test_rotation.py` — back-wall stop
- Sparse tab samples (fixed grid, ≤ 200 pts). Assert:
  - rot 10 (seat): 0 tab points in mount.
  - rot 11.5: 0 (travel still free).
  - rot 13/14: back-wall band probe ≥ 3 (onset ≈ 12, blocked 12–18.5).
  - Re-free by rot ≈ 19.5. Use count ≥ 3, not ratio.
- The stop is probed ANALYTICALLY: the back-wall slab sits in a moving ~0.5°
  window at `rot + ch_back_wall + ch_ang_rot`; coarse grids miss it.

### 3.5 `test_pullout.py` — roof catch (mount drops DOWN, away from ceiling)
- At rot=10, drop ∈ {0, 0.5, 1.0, 1.5}:
  - drop 0: 0 in mount.
  - drop ≥ 1.0: roof has descended onto the tab → points in mount ≥ 3.
  - Onset measured ≈ 0.3–0.5 mm (§ golden numbers), not 0.9.

### 3.6 `test_strength.py` — analytic, no CAD
- FoS at 100 g (≈1 N) on the thinnest catch section: **FoS > 100** (PLA yield
  50 MPa, shear 35 MPa). Purely arithmetic; assert with margin.

## 4. Golden numbers (kernel-measured 2026-08-02 — authoritative, replaces all earlier guesses)

| Quantity | Value | Status |
| --- | --- | --- |
| Tab crest z (base-native) | 2.40 at root r≤75; ≈ 1.0–1.4 at lip | measured |
| Tab crest z (assembly) | 4.40 at root; 3.0–3.4 at lip | measured |
| Roof bottom (assembly) | 3.50 | from params |
| Tab tip r | ≈ 76.0 (formula 76.25) | measured |
| Roof inner r | 75.65 | from params |
| Wall inner r | 76.45 | from params |
| Tab angular center | 0° (tabs on fold axes) | measured |
| Rotation-stop onset (from seat 10°) | ≈ 12° (blocked ≈ 12–18.5, free ≥ 19.5) | measured |
| Pullout-catch onset (drop) | ≈ 0.3–0.5 mm | measured |

Seat interference is RESOLVED (none — see handoff §9): lip crest 3.0–3.4 stays
0.3–0.5 mm below the roof bottom 3.5; back-wall stop works, onset ≈ 2° of
travel past seat.

## 5. Determinism & caching

- Cache fused solids in `spotlight_base/.cache/*.brep`, keyed on a hash of the
  relevant base.py params; regenerate in a fixture only if the hash changed.
- Fixed sample grids + seeded RNG. Never random, never interactive.
- Classifier reuse: one `BRepClass3d_SolidClassifier` per solid, `.Perform(pnt, tol)`
  (remember: **both ctor and Perform need the tol arg**).

## 6. Anti-iteration rules (enforce in the new session)

1. **test_classifier first.** If it fails, stop and fix the probe; do not touch
   design or run other tests.
2. **Assert, don't eyeball.** Every check is a named assertion with a tolerance.
   No printing a sweep table and reasoning about it.
3. **One surprise → one new assertion.** If a test fails unexpectedly, add a
   single targeted assertion that isolates the cause; never re-run a 20-pose sweep.
4. **Params are the spec.** When a parameter changes, update the expected value in
   test_parameters, not a magic number in a test.
5. **Sparse sampling by construction.** Cap points per pose (≤ 500). If a test
   needs more resolution, add resolution analytically (probe the boundary) — not
   by densifying the grid.
6. If meshes/tools are ever needed again, fix the MODEL tessellation (build the
   tab as one revolve/loft, rim_channel without fused coincident faces) so trimesh
   is trustworthy — don't add another mesh-repair path.

## 7. Definition of done

- `pytest -q` green in < 60 s.
- test_classifier oracle proves the probe.
- seat/rotation/pullout all pass with the golden numbers confirmed.
- Results table + PASS/FAIL appended to `verification-handoff.md`; AGENTS.md
  updated to say verification is via `python -m pytest spotlight_base/tests -q`.
