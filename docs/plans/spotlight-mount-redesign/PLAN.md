# Plan: Spotlight Mount Redesign (Ø100 ceiling base + Ø106 twist-lock cap)

## Overview
Rework `spotlight_base/base.scad` from the current small Ø20mm twist-lock
coupling into a practical ceiling mount: a Ø100mm base plate screwed flat to
the ceiling (with a Ø50mm central wire hole), and a Ø106mm mount-plate cap
that twist-locks over the base's outer rim, hides the base and its screws,
and holds wire slack in an internal cavity. The Ø80mm spotlight hangs below
the cap, held by one central M3 self-tap screw into a printed boss, with
wires exiting a Ø8mm off-center hole.

The design direction was confirmed with the user in planning Q&A; this plan
is the execution contract. Current file state (interim): the small-coupling
geometry with a restored solid hub (`translate([0,0,-3]) cylinder(h=3,
r=shaft_radius)` in `base_plate()`). The redesign discards the hub and
shaft-based lock entirely; all lock geometry moves to the outer rim.

## Goals
- Base plate (ceiling side): Ø100mm (r=50), ~4mm thick annulus with central
  Ø50 wire hole, 2× M3 counterbored flush screws at r=35 / 90° and 270°,
  3 male lock tabs on the outer rim (0°/120°/240°).
- Mount plate cap (light side): Ø106mm (r=53) cap whose rim reaches the
  ceiling, fully hiding the base; skirt ~14mm deep, wall ~2mm; interior
  cavity holds wire slack; female lock channels in the skirt inner wall
  engage the rim tabs with ~10° twist travel.
- Cap underside (spotlight side): central threaded boss (~Ø9-10 × 5mm) with
  Ø2.9mm self-tap pilot, and Ø8mm wire exit hole at r≈12.
- Spotlight: Ø80mm base hangs from the single central M3 screw.
- Single-file OpenSCAD, 3-way symmetry preserved, existing view modes kept.

## Non-goals
- No modeled M3 thread — pilot hole only; M3 screw self-taps in the print
  (user's explicit choice).
- No change to lock feature shapes (height/taper/protrusion/gap) or the
  `threefold_pattern()`/`cylindric_bend()` mechanisms — only scale and
  placement change.
- No physical printing or fit-testing; geometry-level verification only.
- No separate CAD files or multi-file refactor — `base.scad` stays one file.
- No packaging/export formats beyond what already exists (PNG + STL).

## Key decisions
- Twist-lock lives on the outer rim, not a central hub.
  Rationale: user chose "outer rim tabs"; also leaves the Ø50 wire path and
  cavity unobstructed.
- Base Ø100 vs cap Ø106 (3mm overhang hides the base edge from the side).
  Rationale: user confirmed Ø106.
- Cap rim reaches the ceiling surface.
  Rationale: user chose "Reach ceiling" — base is fully enclosed/invisible.
- Cap depth 14mm (~10mm wire-slack cavity above the base face).
  Rationale: user chose 14mm depth.
- Screws counterbored flush (Ø6.2 × 3mm counterbore over Ø3.4 through hole,
  socket head M3) so the cap face clears them.
  Rationale: user chose flush counterbore.
- Central Ø50 wire hole + Ø8 exit hole at r≈12.
  Rationale: user chose Ø50 and "slightly off-center" Ø8.
- Spotlight held by threaded boss with Ø2.9 self-tap pilot.
  Rationale: user chose "Self-tap undersize".
- Tab/channel placement: tabs at 0°/120°/240° on the base rim, channels
  offset ~10° behind so drop-on + ~10° twist seats them; screws at 90°/270°
  sit clear of tabs.
  Rationale: avoids the screw holes; gives a real (small) twist travel.
- `lock_width` 2→8 (scaled to rim scale); `bend_steps` 20→24; bend radii
  tab ≈ `plate_radius + 1.0` (51), channel ≈ `plate_radius + tolerance +
  lock_protrusion` (51.45). Offsets re-fit empirically.
  Rationale: old constants were tuned for bend radius ≈9; rim bend is the
  main unverified risk and gets its own phase.
- Rendering/verification env: MCP `openscad_render_single` and
  `openscad_validate_scad` are broken in this environment. Use headless
  `openscad` via `xvfb-run -a` for PNGs and `openscad_analyze_model` +
  STL triangle-set comparison (or STL export success) for verification.

## Phase status

| Phase | Title | Status | Notes |
|---|---|---|---|
| 1 | Base plate rebuild (Ø100 annulus + rim tabs + rim bend) | pending | Re-derives the rim bend — the risky part |
| 2 | Mount plate cap rebuild (Ø106 cap + channels + boss) | pending | Depends on phase 1 bend constants |
| 3 | Assembly, renders, docs | pending | Depends on phases 1-2 |

Status values: `pending`, `in-progress`, `done`.
This table is the first thing an execution session reads — keep it accurate
and up to date at all times.

## Phase files
- `phase-1-base-plate-rebuild.md`
- `phase-2-mount-cap-rebuild.md`
- `phase-3-assembly-renders-docs.md`

## Shared notes
See `NOTES.md` in this directory for running findings/decisions from execution
sessions.
