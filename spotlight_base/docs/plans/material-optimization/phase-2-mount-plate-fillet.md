# Phase 2: Mount plate lip fillet

## Objective
Add a rounded fillet to the mount plate's bottom lip (the junction between the
disc face and the outer wall) — the edge visible from inside the room. Small,
additive change; own phase so its added material is measured separately from
the phase-3 disc pocket.

## Dependencies
- PLAN.md + NOTES.md read. Phase 1 may be `done` (same file, edits are
  independent — safe to proceed if phase 1 is `in-progress` but not required
  to wait).
- Read `mount_plate()` around lines 147–173 and the `Cap & Lock Channel`
  block lines 31–44.

## Responsibilities
- Add `cap_fillet_r` and union the fillet torus into `mount_plate()`.
- Verify: `mount_plate` and `assembled` renders.
- Does NOT touch the disc pocket (phase 3), the skirt's ceiling-side top edge,
  the lock channels, or any base-plate code.

## Todos
- [ ] In the `Cap & Lock Channel` block add:
      ```
      cap_fillet_r = 2.0;   // Fillet radius on the disc/wall junction (bottom lip, mm)
      ```
- [ ] In `mount_plate()`, in the final `union()` alongside `lock_channel()`
      (base.scad:170–171), add:
      ```
      // Rounded bottom lip: half-torus at the disc/wall junction, stays within Ø106.
      // The cup subtraction auto-clips its inner-upper quadrant.
      translate([0, 0, cap_fillet_r])
          rotate_extrude($fn = $fn)
              translate([cap_radius - cap_fillet_r, 0])
                  circle(r = cap_fillet_r);
      ```
- [ ] Confirm the torus max r = `cap_radius − cap_fillet_r + cap_fillet_r` =
      `cap_radius` (53) — envelope unchanged, no collision with base rim/tabs.
- [ ] Confirm the torus (z 0..4) does not overlap the lock channels
      (z 12.3..14.4) — it does not.
- [ ] Render: `xvfb-run -a openscad base.scad -D 'view_mode="mount_plate"' -o out.png --viewall --imgsize=1024,1024`
      and check the bottom lip reads as a smooth rounded edge.
- [ ] Render `view_mode="assembled"` to confirm the cap still fully hides the
      base and the fillet doesn't interfere.
- [ ] Record mount volume before (≈ 31.9 cm³) and after fillet in NOTES.md
      (expected +1.5–2 cm³ from the outer torus bulge).

## Acceptance criteria
- `mount_plate` render shows a rounded bottom lip, flat skirt top, no clipping artifacts.
- `assembled` render shows no new interference.
- Measured volume increases only by the fillet bulge (~1.5–2 cm³), which phase 3's disc pocket more than cancels out.
