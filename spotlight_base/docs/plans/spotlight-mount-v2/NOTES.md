# Notes

## Current state & deviations (READ FIRST)

Keep this block amended in place during execution — it always describes the
plan as it stands NOW. A fresh executor reads this before anything else. If it
contradicts PLAN.md or a phase file, this block wins (and the stale doc should
be amended to match). Newest/current truth at the top; replace stale lines,
don't stack them.

- Current phase: 2 — phase 1 (base rebuild) is done; next is the cap rebuild
  (depends on the phase-1 lug radii).
- Deviations from the written plan:
  - Lug root is buried `lug_overlap` (0.5) into the plate rim
    (`lug_root_r = plate_radius - lug_overlap`) so the plate/lug boolean is a
    true union — touching-only solids stayed disconnected (4 solids). Root
    fillet (0.8) is therefore applied on the fused junction edges (6, at
    r = plate_radius) in `base_plate()`, not inside `lock_lug()`.
  - `ch_roof_in`/`ch_wall_in` now derive from `lug_tip_r` (= phase-2 formula:
    `lug_tip_r - roof_capture`, `lug_tip_r + ch_clear`) since the `tab_tip_r`
    chain is gone. `rim_channel`/`mount_plate`/`lock_channel` left untouched
    (phase-2 owned) and still build.
  - `lock_tab_linear` / `lock_channel_linear` debug views removed with their
    helpers (`cylindric_bend`, `lock_tab`, `lip_prism`, `hull_solid`).
- Gotchas that still matter:
  - The OCC `BRepClass3d_SolidClassifier` oracle + cached `.brep` probes are the
    ONLY trusted verification; trimesh/pymeshfix/manifold3d remain prohibited.
    Cache is STALE (old Ø150 solids) — phase 3 rebuilds it, don't probe it.
  - Real ceiling = flat plaster + 2 rawl-plugged holes 78 mm apart + center
    wires; screw/anchor size must be confirmed on-site (`screw_*` parametric).
  - Assembly frame convention kept: base at z 2..5 (3 mm plate),
    `mount_offset_z` formula unchanged (evaluates to -11.5 until phase 2).
- Next up: execute phase 2 (cap rebuild).

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

## 2026-08-02 (phase 1 done)
- Base rebuilt: Ø100×3, wire Ø40, screws M4 @ r39 (78 mm chord), ring pocket
  r30–48 × 1.2. `lock_lug()` = monolithic revolve rib (full 3 mm to r51.4, step
  to 1.2 mm lip over r51.4..52, tip r52), threefold-fused.
- Measured: `base_plate()` = **14.62 cm³, 1 solid, valid** (target 14.7);
  per-lug 90.9 mm³; all view modes (`base_plate`/`mount_plate`/`assembled`/
  `diff_check`) build. Root fillet 0.8 engaged on all 6 junction edges.
- Removed from build path: `cylindric_bend`, `lock_tab`, `lock_tab_linear`,
  `lip_prism`, `hull_solid`, `lock_channel_linear` (+ `lock_tab_linear`/
  `lock_channel_linear` view modes, `bend_steps`, `lock_width`→`lug_width`).
- Deviations: lug root overlaps plate 0.5 mm (`lug_overlap`) for a true union;
  fillet applied post-fuse in `base_plate()`; `ch_*` keyed off `lug_tip_r`.
- Suite red as expected (old radii in test_parameters/strength/conftest + stale
  cache) — phase 4 fixes; nothing unexpected failed.
- Commit: 2f1101f (code + PLAN in-progress).
