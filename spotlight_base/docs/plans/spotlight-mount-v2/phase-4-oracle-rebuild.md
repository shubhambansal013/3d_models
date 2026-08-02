# Phase 4: Harness + oracle rebuild (conftest, parameters, classifier)

## Estimated effort
~6 minutes / 4 todos.

## Objective
Bring the verification harness and the oracle up to the new geometry. This is
the GATE for all downstream test work: if `test_parameters.py` +
`test_classifier.py` are not green, STOP and fix the probe/harness, not the
design. New golden numbers get measured here and frozen.

## Dependencies
- Phases 1–3 `done` (geometry + fresh cache).
- PLAN.md + NOTES.md read first; read existing `tests/conftest.py`,
  `test_parameters.py`, `test_classifier.py` as the templates being rewritten.

## Responsibilities
Owns: `tests/conftest.py`, `tests/test_parameters.py`, `tests/test_classifier.py`.
Does **not** touch: seat/rotation/pullout/strength tests (phase 5/6), `base.py`.

## Todos
- [ ] Update `conftest.py` to the new frame: base at assembly z 2..5 (3 mm plate),
      `MOUNT_Z = sb.mount_offset_z` (−10), cache volume sanity ranges from phase 3's
      measured numbers, and a lug grid helper sized to `lug_tip_r` (r band
      ~50.5..52.2, angular span ~±9°, z 2..5).
- [ ] Rewrite `test_parameters.py` invariants for the new chain:
      screw chord 2·r = 78; `lug_tip_r == plate_radius + lock_protrusion`;
      `ch_wall_in == lug_tip_r + ch_clear`; `ch_roof_in == lug_tip_r − roof_capture`;
      roof ≥ 0.8; seat clearance (roof bottom − lip top) ≥ 0.6; cap covers base
      `cap_radius − lug_tip_r ≥ 1.5`; assembly z invariant; roof inner radius ≥ lug step radius.
- [ ] Rebuild the oracle point sets in `test_classifier.py` for the new parts:
      base annulus r25..50, wire hole r<20, screw holes/counterbores, pocket zone
      r30..48, screw bosses, 3 lug bodies + stepped lips; cap disc/pocket/pilot/wire
      exit, skirt wall, groove roof/back-wall/floor, cavity. ~20 pts per part.
- [ ] Run `python -m pytest spotlight_base/tests/test_parameters.py spotlight_base/tests/test_classifier.py -q`
      until green (this is the ONLY gate; other tests may still fail).

## Acceptance criteria
- `test_parameters.py` + `test_classifier.py` green.
- New golden numbers (lip top z, roof bottom z, stop onset, catch onset) measured
  via the kernel and recorded in NOTES.md / verification-handoff later.
- Frame transforms validated by the oracle and then frozen (tests stop computing offsets).
