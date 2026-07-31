# Phase 2: Mount plate cap rebuild (Ø106 cap + channels + boss)

## Objective
Rebuild the mount plate as the Ø106mm cap: bottom disc (spotlight side),
upstanding skirt whose top edge reaches the ceiling (hiding the base),
female lock channels in the skirt's inner wall engaging the phase-1 rim tabs,
and the underside hardware (M3 boss + Ø8 wire exit). This phase proves the
tab↔channel twist engagement at rim scale.

## Dependencies
- Requires phase(s): 1 (`done`) — reuses its rim-bend constants and
  `bend_r` derivations for the channel side.
- Files/context to read before starting: `PLAN.md`, `NOTES.md`,
  `phase-1-base-plate-rebuild.md` (for the verified bend constants/offsets),
  and current `base.scad` (uses the phase-1 base plate).

## Responsibilities
Owns:
- `mount_plate()`: Ø106 cap = bottom disc (Ø106, ~2-3mm) + skirt (wall ~2mm,
  depth ~14mm from the ceiling contact down to the disc). Old socket-ring
  geometry removed.
- `lock_channel()`: re-derive `bend_r ≈ plate_radius + tolerance +
  lock_protrusion` and offsets; channels placed so the cap drops straight
  on and twists ~10° to seat (channels ~10° behind the tabs).
- Cap underside: central boss (~Ø9-10 × 5mm) with Ø2.9 pilot hole; Ø8 wire
  exit hole at r≈12 through the disc.
- Keeping `lock_channel_linear` renderable for debugging.
- `assembly_gap` may be used for placement but final assembled layout is
  phase 3's job.

Does NOT touch:
- `base_plate()` geometry (locked in phase 1; may adjust `lock_protrusion`
  only if both plates agree — note in NOTES.md).
- Assembled view layout / final camera work (phase 3).
- AGENTS.md (phase 3).

## Todos
- [ ] Rewrite `mount_plate()`: cap = disc + skirt reaching ceiling contact
      (top edge at the same z the base's ceiling face sits), with channels
      cut into the skirt inner wall. Remove the old socket-cylinder
      geometry (`cylinder(h=4, r=plate_radius)` ring + bottom cylinder).
- [ ] Re-derive `lock_channel()`: `bend_r = plate_radius + tolerance +
      lock_protrusion`; align channels to the phase-1 tab positions minus
      ~10° twist; verify the channel inner surface clears the tab by
      `tolerance`. Iterate offsets empirically via STL/analyze.
- [ ] Add the underside hardware in the cap: central boss with Ø2.9 pilot
      (through the disc), Ø8 exit hole at r≈12.
- [ ] Verify `view_mode == "mount_plate"` renders and the STL analyzes to:
      Ø≈106 outer, wall ≈2, depth ≈14 to ceiling edge, boss present with
      Ø≈2.9 pilot, Ø8 hole at r≈12, channels present at expected angles,
      single connected component, no warnings.
- [ ] Verify engagement: render `diff_check` (and/or inspect assembled
      overlap) so the rim tabs sit inside the channels when the cap is
      dropped on + twisted to the seated position. Check twist travel ≈10°
      and tab↔channel clearance ≈ `tolerance`.
- [ ] Confirm `lock_channel_linear` still renders.

## Acceptance criteria
- `mount_plate` view renders cleanly; `openscad_analyze_model` confirms the
  dimensions in the todo above.
- Part is one connected component.
- `diff_check`/assembled shows tab↔channel engagement with ~`tolerance`
  clearance and ~10° twist travel — no overlap, no gap.
- Boss + Ø8 exit hole present and unblocked.
- Phase status set to `done` in PLAN.md, results noted in NOTES.md.
