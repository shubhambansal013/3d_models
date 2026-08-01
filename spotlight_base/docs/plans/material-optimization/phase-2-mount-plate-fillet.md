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
- [x] In the `Cap & Lock Channel` block add:
      ```
      cap_fillet_r = 2.0;   // Fillet radius on the disc/wall junction (bottom lip, mm)
      ```
- [x] In `mount_plate()`, inside the `difference()` after the wire-exit hole, add
      the subtractive quarter-round `cap_lip_fillet()` (module defined next to
      `lock_channel()`).
- [x] Deviaton from plan: the planned *additive* half-torus (`rotate_extrude`
      circle centered at `cap_radius - cap_fillet_r`, unioned alongside
      `lock_channel()`) is a geometric no-op — the existing disc + skirt already
      fill that volume, so it adds nothing visible (union left the part
      identical, `Simple: yes, Volumes: 2`). The exact-torus *subtraction*
      carves a hidden internal pocket instead (it never reaches the corner,
      which lies 2.83 mm from the torus center). Implemented instead a
      quarter-disc subtraction whose 90° corner sits just outside the part
      (`r = cap_radius + 0.1, z = -0.1`), so its two flat faces over-cut the
      disc face and outer wall (no coincident faces) and the smooth 2 mm arc is
      the visible lip. `Simple: yes`, envelope unchanged.
- [x] Confirm the fillet tool (z −0.1..1.9, r ≥ 51.1) does not overlap the lock
      channels (z 12.3..14.4) — it does not.
- [x] Render `view_mode="mount_plate"` and `view_mode="assembled"` — both
      compile clean, no warnings. (Lip profile verified numerically with
      trimesh `contains`: disc face solid to r≈51, arc void at (52, 0.1),
      wall solid again at z≈1.9.)
- [x] Record mount volume before/after in NOTES.md.
      Pre: 30.56 cm³, post: 29.66 cm³ → −0.90 cm³. Subtractive fillet removes
      material (phase expectation of +1.5–2 cm³ was based on the no-op additive
      torus and is void).

## Acceptance criteria
- [x] `mount_plate` render shows a rounded bottom lip, flat skirt top, no clipping artifacts.
- [x] `assembled` render shows no new interference (`diff_check` intersection empty before and after).
- [x] Measured volume changes only by the fillet (−0.90 cm³ from the carved lip); phase 3's disc pocket adds its own savings on top.
