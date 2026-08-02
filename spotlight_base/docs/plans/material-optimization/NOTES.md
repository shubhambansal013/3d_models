# Notes

Running log for future sessions working on this plan. Append entries as you
go during execution — don't wait until the end of a session. Keep entries
short. Newest at the bottom.

Suggested entry format:

```
## <date or phase label>
- Finding/decision/gotcha, one or two lines.
```

---

## planning session
- Baseline volumes (computed analytically from the CAD, pre-change): base ≈
  24.4 cm³ (annulus 23.6 − screws 0.2 + tabs ≈ 1.0), mount ≈ 31.9 cm³
  (disc 22.1 + skirt 9.1 + boss 0.35 + channels 0.5 − holes 0.18).
- User chose: ring pocket only (base), lip fillet only (mount), yes to disc pocket.
- Pocket/fillet keep all lock geometry and the Ø106/Ø100 envelopes intact.
- Verify volumes from exported STLs in phase 3; these analytic numbers are the
  comparison baseline if no pre-change STL is exported first.
- Plain-python STL volume: parse binary STL, sum signed tetrahedron volumes
  about the origin, take abs (mesh is watertight). No numpy needed.

## phase 1 (base plate ring pocket)
- Added `base_pocket_depth/inner/outer/boss_r` params + `base_pocket()` module,
  wired into `base_plate()`'s difference after the screw-hole loop. No other
  file changes.
- STL volumes via trimesh (plain signed-tetrahedron script initially mislabeled
  units as cm³; raw value is mm³, and coincident-face artifact can also poison
  signed sums — use trimesh). Before: 23.359 cm³, after: 17.523 cm³.
  Reduction 5.84 cm³ = 25.0% (plan target ~24%). Matches analytic
  π(42²−28²)·2 − 2·π·5²·2 = 5.84 cm³.
- Measured before (23.359) < analytic estimate (24.4) — use STL numbers as the
  comparison baseline for phase 3, not the NOTES estimate.
- Point-containment checks passed (trimesh `contains`, needs `rtree`):
  pocket zone r28–42 z<2 hollow; skin z≥2 solid; outside r42 solid at z1/3;
  boss r5 around screws full-depth (material at r3.5/r4.5 off hole, counterbore
  r3.1 + through-hole still hollow); wire hole r20 hollow.
- `base_plate` and `assembled` renders clean, no warnings. CGAL still reports
  "Volumes: 2" (known tab-slice artifact), "Simple: yes".

## phase 2 (mount plate lip fillet)
- Plan's additive half-torus was a geometric no-op: the disc (r≤53, z0..2.5)
  and skirt already fill the torus volume centered at (r=51, z=2), so unioning
  it changed nothing (verified: `union()` left the part byte-identical in
  volume, "Simple: yes, Volumes: 2"). The phase's "+1.5–2 cm³" expectation was
  therefore impossible.
- Exact-torus *subtraction* was also wrong: the corner (53,0) is 2.83 mm from
  the torus center, so the cut never reached it — carved a hidden internal
  pocket instead ("Simple: no, Volumes: 4").
- Implemented subtractive quarter-round instead: `cap_lip_fillet()` — a
  `rotate_extrude`'d quarter-disc of radius `cap_fillet_r` whose 90° corner sits
  at (r = cap_radius + 0.1, z = −0.1). The flat faces over-cut z=0 and r=53
  (no coincident faces → "Simple: yes"); the smooth 2mm arc is the visible
  rounded lip. Envelope stays r≤53, skirt top flat, channels/boss/pilot/wire
  untouched (trimesh `contains` checks all pass).
- Volumes: mount 30.56 → 29.66 cm³ (−0.90 cm³ from the carved lip). Fillet is
  subtractive, so it REDUCES mount material (not the planned increase).
- `diff_check` intersection is empty both before and after (mount seats clear of
  base material at rest — tab sits in channel void). No interference concern.
- `mount_plate` and `assembled` renders compile clean, no warnings.
