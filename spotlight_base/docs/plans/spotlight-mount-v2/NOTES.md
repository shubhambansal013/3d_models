# Notes

## Current state & deviations (READ FIRST)

Keep this block amended in place during execution — it always describes the
plan as it stands NOW. A fresh executor reads this before anything else. If it
contradicts PLAN.md or a phase file, this block wins (and the stale doc should
be amended to match). Newest/current truth at the top; replace stale lines,
don't stack them.

- Current phase: 0 — plan written, not started (user: write down, don't execute).
- Deviations from the written plan: none yet.
- Gotchas that still matter:
  - The OCC `BRepClass3d_SolidClassifier` oracle + cached `.brep` probes are the
    ONLY trusted verification; trimesh/pymeshfix/manifold3d remain prohibited.
  - Real ceiling = flat plaster + 2 rawl-plugged holes 78 mm apart + center
    wires; screw/anchor size must be confirmed on-site (`screw_*` parametric).
  - Assembly frame convention kept: base at z 2..5 (3 mm plate), `mount_offset_z = -10`.
- Next up: execute phase 1 (base rebuild) when the user gives the go-ahead.

---

## Log

Chronological entries, newest at the bottom. History only — the block above is
the truth. Append entries as you go during execution — don't wait until the end
of a session. Keep entries short.

## 2026-08-02 (planning)
- User confirmed ground truth: flat plaster ceiling, center wires, two holes
  78 mm apart; spotlight is Ø40 (not Ø80); NO Ø150 canopy exists.
- User decisions: keep beefed-up twist-lock (no magnets); compact Ø100 base /
  Ø108 cap; solid thin cap disc.
- Root causes recorded: (1) 0.3–0.5 mm lock window tied to ceiling plane via
  mount_offset_z; (2) slice-built 8×3×1.5 mm tabs, sharp unfilleted roots,
  non-manifold seams; (3) 91.4 cm³ ≈ 113 g (base 49.25, mount 42.10 cm³).
- Targets: monolithic filleted lugs (14 mm × 3 mm, 2.0 mm proud, 1.2 mm lip),
  seat clearance 0.8 mm, roof ≥ 1.0 mm, ≈ 34 cm³ ≈ 42 g (−62%).
- Plan written to `docs/plans/spotlight-mount-v2/` (8 phases). Execution not started.
