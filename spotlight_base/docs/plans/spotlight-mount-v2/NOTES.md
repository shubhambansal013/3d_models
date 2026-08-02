# Notes

## Current state & deviations (READ FIRST)

Keep this block amended in place during execution — it always describes the
plan as it stands NOW. A fresh executor reads this before anything else. If it
contradicts PLAN.md or a phase file, this block wins (and the stale doc should
be amended to match). Newest/current truth at the top; replace stale lines,
don't stack them.

- Current phase: 3 — phases 1 (base rebuild) and 2 (cap rebuild) are done; next
  is the cache rebuild (rebuild `.brep` caches, new ~15 / ~19.5 cm³ contract).
- Deviations from the written plan:
  - Lug root is buried `lug_overlap` (0.5) into the plate rim
    (`lug_root_r = plate_radius - lug_overlap`) so the plate/lug boolean is a
    true union — touching-only solids stayed disconnected (4 solids). Root
    fillet (0.8) is therefore applied on the fused junction edges (6, at
    r = plate_radius) in `base_plate()`, not inside `lock_lug()`.
  - `ch_roof_in`/`ch_wall_in` derive from `lug_tip_r` (`lug_tip_r - roof_capture`
    = 51.4, `lug_tip_r + ch_clear` = 52.2) since the `tab_tip_r` chain is gone.
  - Cap rebuilt to Ø108 in phase 2: `mount_offset_z` = **-10**. Wire exit was
    Ø10 in the old code — corrected to the plan's **Ø8** (`wire_r` 5.0 → 4.0);
    pilot was Ø5.8 (labeled Ø2.9) — corrected to **Ø2.9** (`pilot_r` 2.9 → 1.45);
    central boss fully removed (was already commented out of the build).
  - `ch_roof_in = 51.4` sits EXACTLY on the lug's full-height root radius
    (`lug_step_r` = 51.4, roof_capture = 0.6 = tip − step). Zero radial gap —
    coincident faces, no volume overlap (classifier spot check at rot 0/5/10
    clean). If phase-5 probes or reality show grazing, reduce `roof_capture`
    (e.g. 0.5 → 51.5) for real clearance.
  - `lock_tab_linear` / `lock_channel_linear` debug views removed with their
    helpers (`cylindric_bend`, `lock_tab`, `lip_prism`, `hull_solid`).
- Gotchas that still matter:
  - The OCC `BRepClass3d_SolidClassifier` oracle + cached `.brep` probes are the
    ONLY trusted verification; trimesh/pymeshfix/manifold3d remain prohibited.
    Cache is STALE (old Ø150 solids) — phase 3 rebuilds it, don't probe it.
  - Mount fuses to 4 solids (cap + 3 channel unions) — same known state as the
    old Ø156 mount; the channels share coincident faces with the cap body.
  - Real ceiling = flat plaster + 2 rawl-plugged holes 78 mm apart + center
    wires; screw/anchor size must be confirmed on-site (`screw_*` parametric).
  - Assembly frame convention kept: base at z 2..5 (3 mm plate),
    `mount_offset_z` formula `(2 + plate_thickness) − (cap_disc_h + cap_skirt_h)` = -10.
- Next up: execute phase 3 (cache rebuild).

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

## 2026-08-02 (phase 2 done)
- Cap rebuilt to Ø108: `cap_radius` 78 → 54, `cap_disc_h` 2.5 → 2.0,
  `cap_skirt_h` 14 → 13, `mount_offset_z` 5 − 15 = **-10**. Disc pocket
  `disc_pocket_outer` 68 → 48 (r8–48, 1.0 deep, 1.0 mm visible floor); wire
  exit corrected Ø10 → **Ø8** at r12; pilot corrected to **Ø2.9** through the
  disc (no boss).
- Channels retuned to the monolithic lug (fold-local deg, mount frame in parens):
  `ch_back_wall` -5.2 → **-10.5** (-20.5, stop at rot ≈ 12.5), `ch_front`
  15.2 → **22.0** (+12, lug entry at drop), `ch_roof_end` 4.8 → **22.0** (+12,
  lip captured from drop through seat), `ch_groove_bot` 12.3 → **11.5**
  (0.5 below lip bottom at 12.0). z-bands: floor 11.5 / roof bottom 14.0 /
  roof top 15.0 (ceiling plane). `ch_ang_rot` = -10 kept.
- Derived chain: `ch_wall_in` = lug_tip_r + ch_clear = 52.2 (1.8 mm wall),
  `ch_roof_in` = lug_tip_r − roof_capture = 51.4 (= lug_step_r, exact boundary).
- Measured: `mount_plate()` = **18.04 cm³, 4 solids** (target 19.5, band 18–22);
  `base_plate()` still 14.62 cm³ / 1 solid. Seat clearance (roof bottom − lip
  top, assembly) = **0.80 mm**; roof thickness = **1.00 mm**; groove floor 0.5
  below lip bottom.
- Twist-sweep classifier spot check (fresh solids, rot 0/5/10): probes just
  inside the root (r51.35) base-only and just outside (r51.45) mount-only —
  **no overlap**; roof/root faces coincide at r51.4 exactly (recorded in the
  current-state block as a watch item for phase 5).
- Deviations: wire Ø10→Ø8 and pilot Ø5.8→Ø2.9 are corrections to match the plan
  (old code labels were wrong); `ch_roof_in` sits exactly on the root radius
  (0.6 = tip − step) rather than clear of it.
- Commit: 700907d (cap code), 5a470f5 (PLAN/NOTES).
