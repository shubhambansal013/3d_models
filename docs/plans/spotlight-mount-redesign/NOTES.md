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

## Phase 2 (mount plate cap rebuild) — done
- **Cap geometry:** Ø106 (r=53) disc (h=2.5) + 14mm skirt + central boss
  Ø9.5×5 with Ø2.9 pilot + Ø8 wire exit at r=12. Skirt top reaches the
  ceiling face (`mount_offset_z = (2+plate_thickness) − (cap_disc_h +
  cap_skirt_h)` = −10.5); `assembled`/`diff_check` seat the mount with
  `rotate([0,0,-ch_ang_rot])` (+10°).
- **Ground truth vs phase-1 assumption:** the real protruding tab lip is LOW,
  not z[0,2]. Point-in-mesh probes of the phase-1 base render (fold center):
  r>50.15 material only z[0,~0.8]; crest profile r50.10→1.60, 50.25→1.40,
  50.35→1.30, 50.45→1.15, 50.55→1.05, 50.65→0.90, 50.75→0.75 (a wedge);
  angular extent ±4°–4.9°. The earlier "z[0,2]" measurement included the
  inner ramp root (r 49.7–50.1). Channel sized from the crest profile, not
  the nominal 2.0.
- **`rim_channel()` direct geometry** (annular-sector union, fold-local):
  outer wall ring r[50.95,53] z[0,2.1] ang[−5.2,15.2]; roof overhang
  r[50.4,50.95] z[1.5,2.1] ang[−5.2,4.8]; back-wall slab r[50.2,50.95]
  z[0,1.5] ang[−5.7,−5.2]. Threefold at `ch_ang_rot=−10`. Params:
  `ch_back_wall −5.2`, `ch_front 15.2`, `ch_roof_end 4.8`, `ch_roof_in 50.4`,
  `ch_groove_bot/top 12.3/13.8` (mount-local), `ch_block_top 14.4`.
- **Roof must start at r=50.4 (not 50.2):** the tab's inner crest (1.3–1.6 at
  r≤50.35) would hit a roof that reaches to 50.2 during the 10° twist; at
  50.4 the under-roof crest is ≤1.2, giving 0.3mm clearance and capturing the
  outer lip (0.75–1.15 crest) with ~0.3mm pullout play.
- **Bug caught:** a difference-based `rim_channel()` (full block minus groove
  void) lets the void carve away the back-wall slab → no stop face, all
  intersection volumes 0. Fix = union form with an explicit back-wall slab
  (`annular_segment(..., back_wall−0.5, back_wall)`).
- **`annular_segment`** samples arcs at 2° steps so the chord stays above the
  radius (sagitta <0.04mm). Early draft included the origin in the polygon
  (pie fill) and sagging chords → false geometry.
- **Verification vs the real parts** (`use <base.scad>` harness,
  intersection volume via scan.py; tab lifted with `translate([0,0,lift])
  base_plate()`): rotation sweep rel_rot −15..+25 → 0.0000 at −15..+10,
  0.83 @ +15, 0.68 @ +20, 0 @ +25 (free travel, hard back-wall stop);
  pullout at seat (rel_rot=10): free to lift 0.2, blocked from 0.3 (0.02,
  0.21 @ 0.4, 0.59 @ 0.5, 2.4 @ 0.75, 4.4 @ 1.0); pullout at drop
  (rel_rot=0): free (0 even at lift 1.0). `diff_check` at seat = empty.
- **Scan-harness gotchas:** `use <base.scad>` resolves relative to the
  importing file → harness must sit in the project dir; this openscad build
  rejects `-I` (prints usage, renders nothing); OpenSCAD writes no STL for an
  empty intersection (treat missing file as 0 volume); seat pullout needs BOTH
  `-D rel_rot=10` and `-D tab_lift=...` (running only tab_lift leaves rel_rot=0
  = drop, which is free).
- `shaft_radius` removed; `lock_channel_linear()` kept for debugging;
  `mount_plate`/`lock_channel` fully replaced. Render of the cap: Ø106,
  bbox z[−5,16.5]; assembled bbox z[−15.5,6].


---
