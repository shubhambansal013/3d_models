# Spotlight Twist-Lock Mount

OpenSCAD project: `models/spotlight_base/base.scad`

## Design

- **Plug** — the base plate (mounts to ceiling). Has a flat top plate + cylinder shaft with 3 lock tabs (pluglip_linear) at 60°, 180°, 300° via `tri_pattern()`. The shaft cylinder is cut into 3 arc sections (60° each) so only the tab-supporting parts remain (`cylinder_arc_sections`).
- **Receptacle** — the floor-facing female socket. Has a flat flange ring + 3 female lock tabs (reclip_linear) + a full continuous outer cylinder below the plate.

## Naming convention

- Plug = base plate (ceiling side)
- Receptacle = mount (light fixture side)

## Parameters (in file)

`plug_radius`, `tolerance`, `mating_dist`, `lip_*`, `flange_radius`, `bend_steps`
