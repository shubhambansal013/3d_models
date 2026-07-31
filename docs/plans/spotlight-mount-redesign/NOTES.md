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

## Planning (pre-execution)
- Current `base.scad` state (interim): cleaned refactor of original v37
  (renames plug→`base_plate`, receptacle→`mount_plate`, `lip_*`→`lock_*`),
  with the 3 pie sectors removed and a solid hub restored:
  `translate([0,0,-3]) cylinder(h=3, r=shaft_radius)` inside `base_plate()`.
  STL triangle sets were verified byte-identical to the original across all
  6 view modes during the refactor.
- Proven constants that stay unchanged: `tolerance 0.2`, `assembly_gap 5.0`
  (visual only), `lock_height 3.0`, `lock_gap_height 1.0`, `lock_taper 1.2`,
  `lock_width 2.0` (→ 8 in redesign), `lock_protrusion 0.75`, `$fn 72`.
- Old tab geometry (gone): shaft hub r=8, bend_r=9, tabs centered ~47°/167°/
  287° with angular width 34-60° and protrusion past shaft 0.75. Do not
  reuse these numbers at rim scale — rim bend is the phase-1 re-derivation.
- Old `lock_tab()` transform chain to port: `translate([-(shaft_radius +
  lock_protrusion),0,1]) rotate([0,90,0]) cylindric_bend([6,6,6], bend_r,
  nsteps=ceil(bend_steps/2))` + nested flips. `lock_channel()` similarly
  with `bend_r = shaft_radius + lock_protrusion + tolerance` and
  `nsteps = bend_steps`.
- User-confirmed redesign decisions: outer-rim twist lock; mount plate
  Ø106; cap rim reaches ceiling (base fully hidden); cap depth 14mm; screws
  counterbored flush; threaded boss with **Ø2.9 self-tap pilot** (no modeled
  thread); central **Ø50** wire hole + **Ø8** exit hole at r≈12; spotlight
  base Ø80.
- Proposed tab placement: 0°/120°/240° (3-fold), channels ~10° behind for a
  ~10° drop-on twist travel; screws at r=35 / 90°+270° (clear of tabs).
- Environment gotchas (verified):
  - `openscad_render_single` MCP: rejects `$fn` injected by quality presets
    ("Invalid variable name '$fn'") and `normal` quality dies with "Unable
    to open a connection to the X server. DISPLAY= Can't create OpenGL
    OffscreenView. Code: -1." — do NOT rely on it.
  - `openscad_validate_scad` MCP returns `valid:false` even for `cube(1)` —
    unreliable, do not use for gate decisions.
  - Working paths: `xvfb-run -a openscad <file> -D ... -o out.png` for
    renders; `openscad_analyze_model` MCP (headless) for dimensions;
    STL export + triangle-set comparison (python) for geometry equality.
- Git: repo root is `/home/ubuntu/models`; the plan folder lives at
  `docs/plans/spotlight-mount-redesign/`. At planning time the working tree
  had uncommitted changes to `spotlight_base/base.scad` + `AGENTS.md` and
  untracked PNGs from the refactor session — plan docs were committed
  separately.

---
