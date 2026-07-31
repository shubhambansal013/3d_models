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

## Phase 1 (base plate rebuild) — done
- **Rim bend transform chain re-derived.** The old `lock_tab()` chain is
  correct at rim scale with these constants (verified stage-by-stage via STL
  bboxes): `bend_r = plate_radius + 1.0` (51), outer translate
  `[-(plate_radius+1.0), 0, 2]`, inner translate `[0, lock_width+1, 1.25]`,
  `cylindric_bend([8, 10.5, 8], bend_r, nsteps=bend_steps)`, and a
  `rotate([0,0, 180 + (lock_width/2+1)/bend_r*(180/PI)])` to center each tab
  on its 0°/120°/240° fold axis. Final tabs measured at 0.0°/119.9°/240.0°
  (≤0.1° error).
- How the chain maps the linear tab: net inner rotation is (x,y,z)→(z,−x,−y),
  so tab x→arc, tab y→radial (inverted), tab z→bend axis. Final radius =
  `|X0| − z_off` (base) to `|X0| − z_off + lock_protrusion` (lip tip); final
  Z = `z_translate − tab_height` (tab vertical band [0,2]).
- **Two design constants deviated from PLAN (noted for phase 2):**
  1. `lock_protrusion` bumped 0.75 → **1.0** and the tab base embeds 0.25mm
     into the rim (`z_off=1.25`). At `z_off=1.0` the tab was tangent to the
     rim at the arc center and the union produced **Volumes: 2**. With
     `z_off=1.25` the base sits at r≈49.7 and the union is a real single
     volume. Net effect: tab tip radius = **50.75** (= plate_radius + 0.75),
     base radius ≈49.7 (0.25–0.3 embed). Tab is still 0.75 proud — same as
     planned, but `lock_protrusion` no longer equals the proud distance.
  2. Tab vertical band is `z∈[0,2]` (annulus bottom face at z=0), raised from
     the old hanging position so it is fully embedded in the plate thickness
     and prints flat on the bed. The locking lip/hook edge sits at the tab's
     bottom (z=0); the channel's vertical slot must accept the tab at z∈[0,2].
- **Measured tab footprint (for phase 2 channel sizing):** tip radius 50.75,
  base 49.7, arc spans ±4.9° around 0/120/240 (9.8° wide at the tip),
  `bend_r=51`. Channel inner wall should sit at `plate_radius + tolerance`
  (50.2); channel recess should reach ≥ tip radius + tolerance (≈50.95);
  channels offset ~10° behind the tabs for the drop-on twist.
- **Bug caught in first pass:** `center=true` cutters (h=6) for the wire hole
  and screw through-holes only span z∈[−3,3] and left the top 1mm of the 4mm
  plate solid (blind holes). Fixed with `translate([0,0,-1]) cylinder(h=6)` →
  z∈[−1,5]. Re-verified: wire hole r=25 wall spans z 0..4, through-hole r=1.7
  spans z 3..4, counterbore r=3.1 spans z 0..3.
- **Pre-existing mesh artifact (do not chase in phase 2):** `cylindric_bend`
  slice boundaries create coincident faces → CGAL reports odd volumes and
  non-manifold edges in the exported STL. Old `lock_channel` shows the same
  (Volumes: 4, 664 non-manifold edges); new base_plate shows Volumes: 2
  (206 non-manifold edges, all along the tab's bottom ridge at the slice
  spacing). Renders "Simple: yes", 1 closed surface shell, genuinely one
  connected part. Accepted as-is.
- `base_plate` verified: Ø100×4 annulus, Ø50 wire hole, 2× counterbore
  Ø6.2×3 + Ø3.4 through at r=35/90°+270°, 3 rim tabs (tip r=50.75), all view
  modes render with no warnings. `lock_tab_linear` unchanged and still
  renders.
- `shaft_radius` kept as a legacy param (only `lock_channel`/`mount_plate`
  still reference it — they are untouched but still old geometry; phase 2
  replaces them and removes `shaft_radius`).

---
