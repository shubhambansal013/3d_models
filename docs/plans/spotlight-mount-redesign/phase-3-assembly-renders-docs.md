# Phase 3: Assembly, renders, docs

## Objective
Make the assembled view correct and presentable, verify the wire path and
hide-the-base requirement, produce the final renders, and bring the repo
docs (AGENTS.md) up to date with the new architecture.

## Dependencies
- Requires phase(s): 1 and 2 (`done`).
- Files/context to read before starting: `PLAN.md`, `NOTES.md`, and the
  current `base.scad` with both rebuilt plates.

## Responsibilities
Owns:
- Assembled view layout (`view_mode == "assembled"`): cap's skirt top edge
  at the ceiling surface, base nested inside, `assembly_gap` repurposed if
  needed; verify no base geometry pokes out past the cap rim (fully hidden)
  and no interference.
- Final render pass via `xvfb-run -a openscad`:
  `base_plate`, `mount_plate`, `assembled`, `diff_check` (and the linear
  debug modes if useful).
- Final STL export and `openscad_analyze_model` dimension check of both
  parts.
- Updating `/home/ubuntu/models/spotlight_base/AGENTS.md`: key parameters,
  design notes, view-mode list, assembly narrative (ceiling → base → cap →
  spotlight), rim-based lock notes.
- Cleanup: remove any now-dead parameters/modules (e.g. leftover
  `shaft_radius` references, old hub code); ensure the parameter block
  matches what the file actually uses.

Does NOT touch:
- Lock feature shapes / fit tolerances (locked in phases 1-2; only fix if
  clearly broken, and note it).
- Physical printing concerns.

## Todos
- [ ] Fix `assembled` view: stack base + cap so the cap rim reaches the
      ceiling plane and the base is invisible from outside; set up
      `assembly_gap` accordingly. Verify no intersections (base∩cap in the
      seated position should only be the tab/channel contact faces).
- [ ] Verify wire path end-to-end: ceiling → Ø50 base hole → cap cavity →
      Ø8 exit → spotlight. Both holes are centered on the same axis; confirm
      the cavity is unobstructed and the base's screw heads don't foul the
      cap disc when seated.
- [ ] Render final PNGs (`xvfb-run -a openscad`): base plate top/bottom,
      cap (underside showing boss + Ø8 hole), assembled, diff_check. Save
      alongside the existing PNGs in `spotlight_base/`.
- [ ] Export both parts to STL and run `openscad_analyze_model`; record
      final dims in NOTES.md.
- [ ] Update AGENTS.md for the new architecture (params, naming, view modes,
      design notes).
- [ ] Remove dead code/params from `base.scad`; re-run validation that all
      view modes still render after cleanup.

## Acceptance criteria
- `assembled` renders with the base fully hidden inside the cap, no
  interference, wire path clear.
- Final PNGs saved and STL dims recorded.
- AGENTS.md describes the current design accurately.
- All six view modes render without warnings.
- Phase status set to `done` in PLAN.md; NOTES.md has a final entry;
  PLAN.md notes column updated if anything changed mid-flight.
