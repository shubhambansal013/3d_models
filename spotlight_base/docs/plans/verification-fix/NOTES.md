# Notes

Running log for future sessions working on this plan. Append entries as you
go. Keep entries short. Newest at the bottom.

---

## planning session
- Chose the `verification-test-plan.md` catalog as the executable spec; the
  Gemini tiered plan maps 1:1 (Tier 1 params / Tier 2 classifier oracle /
  Tier 3 sparse integration).
- Decision: delete `lock_check.py` (handoff §1: broken, don't patch) rather
  than salvage it. Its only useful logic (frame math, strength calc) is
  re-expressed as asserts in the pytest suite.
- Decision: drop trimesh/pymeshfix/manifold3d (uninstalled from the venv).
  `BRepClass3d_SolidClassifier` is the only trusted containment tool.
- Verified environment: cached `.brep` load ~50 ms, probe ~4 ms/pt, base=1
  solid (56.7 cm³), mount=4 solids (55.0 cm³). pytest 9.1.1 installed.
- Caution recorded: handoff golden numbers (tab 5.6°/76.25/2.40) may be off;
  derive expected values from params + validate via the oracle instead.

## execution session (1)
- Wrote `tests/` suite (conftest.py + 6 test files). `conftest.py` holds the
  one true assembly frame (base z 2..6, mount at -10.5, `rot=10` seat) and the
  OCP probe; every test goes through it.
- `test_parameters.py` fixed: the real derivation chain is
  `tab_bend_r = plate_radius + 1` → `tab_root_r = tab_bend_r - 1.25` →
  `tab_tip_r = tab_root_r + lock_protrusion` (= plate_radius − 0.25 + 1.5 =
  76.25). The handoff's formula (`tab_bend_r − 1.25 + protrusion`) was wrong.
- `test_classifier.py` fixed twice:
  - `(10,39)` assembly ≈ base `(10,39,1)` was INSIDE the screw boss ring —
    moved to `(20,39,3)` (outside the pocket band r28–42).
  - `(0,36)` was inside the M4 counterbore (r≈3.8 at screw r=39) — moved to
    `(40,40,2.3)` (open ring).
  - Boss points → expect False after user confirmed the boss is gone.
- Only remaining failure: `test_rotation::test_back_wall_stop_onset` — coarse
  rot sweep `[10,12,14,16,18,20,22,25]` counted 0 or 5, but kernel probe showed
  the true band: free ≤11.5, blocked 12.0–18.5, free ≥19.5. Handoff's "18°"
  onset was a coarse-grid artifact, not physics.
- Fix: rewritten as `test_free_travel_at_seat` + `test_back_wall_stop_*`
  probing the moving ~0.5° back-wall window analytically at r 75.35/75.8/76.3,
  z 2.0/2.7/3.4 (3×3×3 = 27 pts) — matches kernel (0 at 10/11, ≥6 at 12).
- `requirements.txt` + AGENTS.md updated (CadQuery, pytest; trimesh/manifold3d
  gone). `verification-handoff.md` §9 appended with REVISED golden numbers.
- **22 passed in ~8 s** (budget 60 s), deterministic across repeat runs.
- PARKED: MCP server + `opencode.jsonc`, `.cache` git handling; refresh the
  stale golden numbers in `verification-test-plan.md` §3.4/§4.
