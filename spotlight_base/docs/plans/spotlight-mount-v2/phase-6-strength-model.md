# Phase 6: Strength model — hand-force, monolithic lug section

## Estimated effort
~4 minutes / 3 todos.

## Objective
Replace the current 100 g / FoS>100 analytic model with a hand-force model that
reflects the "person applies too much force" concern (#2) on the new monolithic
lug cross-sections. Target FoS ≥ 5 under a 25 N pull and 2 N·m twist.

## Dependencies
- Phase 4 `done` (new params/lug radii exist to derive from). Standalone arithmetic — no CAD.
- PLAN.md + NOTES.md read first; existing `test_strength.py` as the template.

## Responsibilities
Owns: `tests/test_strength.py` only.
Does **not** touch: `base.py` or the classifier tests.

## Load model
- Hand pull: 25 N total, shared by 3 lugs → ~8.3 N per lug.
- Hand twist: 2 N·m at r ≈ 0.05 m → ~40 N tangential total, ~13.3 N per lug,
  taken by the lug's full cross-section against the back-wall stop.
- Lug section (monolithic, from params): width `lug_width` 14 mm, full height
  `plate_thickness` 3 mm; lip shear area = width × `lip_h` (14 × 1.2 mm).
- Material: PLA yield 50 MPa, shear 35 MPa (3d-cad-modelling skill).

## Todos
- [ ] Rewrite `test_strength.py` with the hand-force model above; shear and
      bending computed on the monolithic lug section (full height at the root,
      lip section for the roof catch).
- [ ] Assert FoS ≥ 5 on all three checks (lug root shear at twist, lip shear at
      pullout, lip bending at pullout) at 25 N / 2 N·m.
- [ ] Record computed stresses in NOTES.md for the docs phase.

## Acceptance criteria
- `test_strength.py` green with FoS ≥ 5 at hand force (current design would fail
  this bar — the test proves the monolithic lugs).
