# Phase 7: Full suite green + exports + renders

## Estimated effort
~5 minutes / 4 todos.

## Objective
Run the complete verification suite end-to-end, export STL/STEP, and produce
headless renders for the docs. Everything must be green in under 60 s.

## Dependencies
- Phases 4, 5, 6 `done` (oracle + integration + strength green individually).
- PLAN.md + NOTES.md read first.

## Responsibilities
Owns: the full test run, `output/*.{stl,step}`, and the render outputs.
Does **not** touch: `base.py` geometry or test assertions (any failure here is a
bug to fix, not a number to fudge).

## Todos
- [ ] Run `source /home/ubuntu/workspace/.venv/bin/activate && python -m pytest spotlight_base/tests -q`
      — full suite green, total < 60 s.
- [ ] Export `output/base.stl|step` + `output/mount.stl|step` via the module's
      `__main__` path or a small script; confirm the files update.
- [ ] Render assembled / base / mount views headlessly (ocp_vscode or STEP→PNG
      path that works in this env) for the docs.
- [ ] Compute and record final volumes + weight (PLA 1.24 g/cm³) in NOTES.md;
      compare vs the 91.4 cm³ / 113 g baseline.

## Acceptance criteria
- Full suite green in < 60 s.
- Final weight ≈ 42 g (±5 g) — the drastic-reduction goal met.
- Exports + renders refreshed on disk.
