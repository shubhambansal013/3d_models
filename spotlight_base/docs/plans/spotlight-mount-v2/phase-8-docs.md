# Phase 8: Docs — AGENTS.md, README golden numbers, PLAN/NOTES

## Estimated effort
~5 minutes / 4 todos.

## Objective
Make the docs match the shipped design so a fresh session trusts the suite and
does not re-derive stale numbers. This closes the loop on concern #1–#3 with
recorded kernel-measured golden numbers.

## Dependencies
- Phase 7 `done` (final volumes + golden numbers exist).
- PLAN.md + NOTES.md read first.

## Responsibilities
Owns: `AGENTS.md`, `spotlight_base/README.md`, and this plan's own PLAN/NOTES.
Does **not** touch: `base.py`, tests, caches.

## Todos
- [ ] Update `AGENTS.md`: new sizes (Ø100 base / Ø108 cap, plate 3 mm, screw M4
      at r39, wire Ø40), monolithic lugs (replace the `cylindric_bend`/slice
      artifact note — stale), new volumes (~14.7 / ~19.5 cm³, ~42 g total),
      updated key-parameters list and the new tilt test.
- [ ] Append the new kernel-measured golden numbers to
      `spotlight_base/README.md` (lip top z, roof bottom z, stop onset, catch
      onset, seat-clearance margin) and mark the old Ø150 table as superseded.
- [ ] Update this plan's PLAN.md status table (all `done`) + NOTES.md
      current-state block; ensure NOTES.md has the phase log entries appended.

## Acceptance criteria
- AGENTS.md + README reflect the Ø100/Ø108 design with measured golden numbers;
  no stale Ø150/slice-artifact claims remain.
- PLAN.md status table all `done`; NOTES.md current-state + log current.
