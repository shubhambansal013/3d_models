# Phase 5: Integration tests — seat / rotation / pullout / NEW tilt

## Estimated effort
~6 minutes / 5 todos.

## Objective
Re-establish the functional Tier-3 integration tests on the new geometry and add
the NEW tilt test that locks concern #1 (base-flush/tilt tolerance). The tilt
test is the key deliverable of this phase — it directly verifies the "gaps make
locks not work" fix.

## Dependencies
- Phase 4 `done` (oracle green = the probe is trustworthy).
- PLAN.md + NOTES.md read first; existing `test_seat_fit.py`, `test_rotation.py`,
  `test_pullout.py` as templates being rewritten.

## Responsibilities
Owns: `tests/test_seat_fit.py`, `tests/test_rotation.py`, `tests/test_pullout.py`,
and the new `tests/test_tilt.py`.
Does **not** touch: `base.py`, conftest, oracle, strength test.

## Todos
- [ ] Rewrite `test_seat_fit.py`: frame sanity cross-check, seat has zero lug
      points inside mount material, 3-fold symmetry — on the new lug grid/radii.
- [ ] Rewrite `test_rotation.py`: back-wall stop for the new channel (analytical
      moving-window probe at the lug's trailing edge); free before onset,
      blocked ≥ 3 pts after; measure and record the new stop onset (~12–13°).
- [ ] Rewrite `test_pullout.py`: roof catch on pullout (z_off < 0); measure the
      new catch onset.
- [ ] ADD `test_tilt.py`: assert seat clearance ≥ 0.6 mm from params; then, at
      seat, shift the lug sample points DOWN by 0.5 mm (simulated plate tilt) and
      assert still zero collisions, and shift UP by +0.3 mm (plate proud) and
      assert still zero collisions. This locks the flush tolerance.
- [ ] Run the four files green; update golden numbers in NOTES.md (stop onset,
      catch onset, seat clearance margin).

## Acceptance criteria
- `test_seat_fit.py`, `test_rotation.py`, `test_pullout.py`, `test_tilt.py` green.
- Tilt test passes with the 0.8 mm seat-clearance design (tolerates ≥ 0.5 mm of
  per-lug plate tilt, which the old 0.3 mm design could not).
