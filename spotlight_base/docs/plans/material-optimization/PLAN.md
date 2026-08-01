# Plan: Material Optimization & Edge Rounding

## Overview
Reduce filament usage and print time for the spotlight twist-lock mount and
round the mount plate's visible edges. The base plate is a solid Ø100×4
annulus (~24.4 cm³) — mostly dead weight — so an underside ring pocket
removes ~25% of it with no structural risk. The mount plate is a solid
Ø106×2.5 disc (~31.9 cm³); its cup-side top face is never seen, so a shallow
pocket there saves another ~7 cm³, and a 2mm fillet on the bottom lip rounds
the visible edge while keeping the Ø106 envelope and the ceiling seal intact.

All changes live in the single file `base.scad`. No lock geometry, dimensions,
or hardware change.

## Goals
- Cut base plate filament by ~24% (ring pocket on the light-side face).
- Cut mount plate filament by ~20% (pocket on the disc's cup-side top face).
- Round the mount plate bottom lip with a small fillet (aesthetic, finger-friendly).
- Keep all dimensions, lock features, and assembly behavior identical.
- Verify with renders and STL volume comparison.

## Non-goals
- No change to `plate_radius`, `cap_radius`, `plate_thickness`, or any lock/channel parameter.
- No full-depth lightening holes through the base (bridging + stiffness risk). Ring pocket only.
- No rounding of the skirt's ceiling-side top edge (must stay flat to seat against the ceiling).
- No change to hardware (M3 screws, counterbore size/depth).
- No new view modes in the `view_mode` switch (existing modes used for verification).

## Key decisions
- Decision: Underside ring pocket on the base (r28–42, 2mm deep) rather than lightening holes or segmented struts.
  Rationale: User picked this. Open recess prints flat with no supports/bridging; the flat ceiling-facing top stays a continuous 2mm skin; screw bosses and tab-embed rim band keep full 4mm depth.
- Decision: Fillet only on the mount's bottom lip (r = 2mm, stays inside Ø106).
  Rationale: User picked this. Skirt top stays flat so it still fully hides the base and seats against the ceiling.
- Decision: Pocket the mount disc's cup-side face (r6–48, 1mm deep).
  Rationale: User picked this. The face is invisible in use; leaves 1.5mm floor on the visible light side; clears boss (r4.75) and pilot.
- Decision: Fillet implemented as a subtractive `rotate_extrude` quarter-disc (`cap_lip_fillet()`), carved from the disc/wall corner; the quarter-disc's corner sits just outside the part (r = cap_radius + 0.1, z = −0.1) so the flat faces over-cut the two faces and the smooth 2mm arc is the visible lip.
  Rationale: The originally planned additive half-torus centered at r = cap_radius − cap_fillet_r turned out to be a geometric no-op (the disc+skirt already fill that volume), and the exact-torus subtraction never reached the corner. Subtractive keeps the Ø106 envelope and skirt top; see NOTES.md phase 2.

## Phase status

| Phase | Title | Status | Notes |
|---|---|---|---|
| 1 | Base plate ring pocket | done | base 23.359→17.523 cm³ (−25%), verified |
| 2 | Mount plate lip fillet | done | mount 30.56→29.66 cm³ (subtractive quarter-round, −0.9 cm³) |
| 3 | Mount plate disc pocket + full verification | done | final renders + STL volume comparison |

## Phase files
- `phase-1-base-plate-pocket.md`
- `phase-2-mount-plate-fillet.md`
- `phase-3-disc-pocket-and-verification.md`

## Shared notes
See `NOTES.md` in this directory for running findings/decisions from execution
sessions.
