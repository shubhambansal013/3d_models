# Phase 3: Cache rebuild + volume smoke

## Estimated effort
~5 minutes / 3 todos.

## Objective
Regenerate the cached fused solids the test suite probes and confirm the new
geometry's volumes match the design targets before any test work. The cache
contract changes materially (base should now be a genuine 1 solid, not 73 fused;
volumes drop from 49.25/42.10 to ~14.7/~19.5 cm³).

## Dependencies
- Phases 1 and 2 `done`.
- PLAN.md + NOTES.md read first.

## Responsibilities
Owns: `scripts/rebuild_cache.py` and the `.cache/*.brep` files.
Does **not** touch: `base.py` geometry or test files (test volume ranges are
updated in phase 4).

## Todos
- [ ] Update `scripts/rebuild_cache.py` if its fusion strategy no longer matches
      (base should now fuse to a single solid — the script's loop still works on
      a 1-solid compound, but its printed/comment contract must be updated).
- [ ] Run `source /home/ubuntu/workspace/.venv/bin/activate && python spotlight_base/scripts/rebuild_cache.py`.
- [ ] Record measured volumes + solid counts in NOTES.md (compare to targets:
      base ~14.7 cm³ / 1 solid, mount ~19.5 cm³).

## Acceptance criteria
- Cache regenerates cleanly.
- `base_fused.brep`: 1 solid, ≈ 13–17 cm³.
- `mount_fused.brep`: 4 solids (cap + 3 channels) or fewer, ≈ 17–22 cm³.
- Volumes recorded in NOTES.md for phase 4's conftest ranges.
