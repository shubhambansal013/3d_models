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
