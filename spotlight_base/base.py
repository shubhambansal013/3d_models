"""
CadQuery spotlight twist-lock ceiling mount.

Base plate (ceiling side): O100 annulus screwed flat to the real ceiling
(2x M4, holes 78mm apart), with 3 monolithic shelf lugs on its outer rim for
the twist-lock. Mount plate (light side): O108 cap that twists ~10deg over the
base rim, 2mm disc (1mm cup-side pocket) + 13mm skirt; the spotlight screws
onto the flat disc (no central boss). The roof overhangs 3mm past the lug tip
and grips each 3mm-wide shelf lip (back-wall stop at rot ~11.5-12).
"""
import math
import cadquery as cq
from cadquery import Vector
from ocp_vscode import show

# ============================================================
# Global & Render Settings
# ============================================================
VIEW_MODE = "assembled"  # assembled, base_plate, mount_plate, diff_check
FN = 72  # curved-surface resolution (used to size arc sampling below)

# ============================================================
# Plate Dimensions
# ============================================================
plate_radius = 50.0       # Outer radius of the base plate annulus (mm); O100
plate_thickness = 3.0     # Thickness of the base plate (mm)
wire_hole_radius = 20.0   # Radius of the central wire through-hole (mm; O40)
base_pocket_depth = 1.2   # Underside lightening pocket depth (mm); leaves 1.8mm skin
base_pocket_inner = 30.0  # Pocket inner radius (mm)
base_pocket_outer = 48.0  # Pocket outer radius (mm); leaves a solid ring to the lug rim
base_pocket_boss_r = 4.5  # Full-depth circle kept around each screw (mm)

# ============================================================
# Screw Holes (M4 pan head, counterbored flush from the ceiling side)
# ============================================================
screw_hole_radius = 39.0     # Radius of the M4 screw hole centers (mm); 2*39 = 78mm real hole spacing
screw_angles = [90, 270]     # Angular positions of the screw holes (deg)
screw_through_r = 2.25       # Through-hole radius for M4 (O4.5, mm)
screw_counterbore_r = 4.1    # Counterbore radius for M4 pan head (O8.2, mm)
screw_counterbore_d = 2.0    # Counterbore depth (mm); leaves 1.0mm skin

# ============================================================
# Lock Lugs (monolithic twist-lock shelf teeth, revolve-built, no cylindric_bend)
# ============================================================
lock_protrusion = 2.0     # Radial proud of the lug past the plate rim (mm); tip at r 52
lug_width = 14.0          # Lug arc width measured along the rim (mm)
lug_angles = [0, 120, 240]  # Angular centers of the three lugs (deg)
lock_height = plate_thickness  # Full plate height at the root (mm)
lip_h = 1.2               # Height of the shelf lip (mm); lip top native z = 1.2

# ============================================================
# Cap & Lock Channel
# ============================================================
cap_radius = 54.0     # O108/2: cap disc and skirt outer radius (mm); 2mm overhang hides the lug edge
cap_disc_h = 2.0      # Disc thickness (light-side mounting face) (mm)
cap_skirt_h = 13.0    # Skirt depth (mm)
cap_chamfer = 0.4     # Bottom-edge chamfer on the disc/wall corner (mm). A straight
                      # chamfer (not the old 2mm curved lip) so the full-perimeter
                      # bottom overhang / support requirement disappears.
ch_ang_rot = -10      # Channel fold-copy axis rotation (deg)
ch_clear = 0.2        # Radial clearance to the lug tip face (mm)
ch_back_wall = -10.5  # Groove back wall (fold-local deg): mount-local -20.5, lug stop at rot ~12
ch_front = 22.0       # Groove open entrance (fold-local deg): mount-local +12, clears lug entry at drop
ch_roof_end = 22.0    # Roof front edge (fold-local deg): lip captured from drop through seat
roof_capture = 3.0    # Lock grip: roof overhang depth past the lug tip (mm); the
                      # roof reaches 3mm inside the tip and grips the full 3mm lip.
ch_groove_bot = 11.5  # Groove floor (mount-local z); 0.5mm clear below the lip bottom (z 12.0)
ch_groove_top = 14.0  # Groove ceiling / roof bottom (mount-local z); seat clearance 0.8mm over lip top (13.2)
ch_block_top = 15.0   # Channel block top / roof top (mount-local z) = ceiling plane; roof thickness 1.0
disc_pocket_depth = 1.0   # Cup-side lightening pocket depth in the mount disc (mm)
disc_pocket_inner = 8.0   # Pocket inner radius: clears the central pilot (mm)
disc_pocket_outer = 48.0  # Pocket outer radius: leaves a solid ring to the wall (mm)

# Derived lock geometry (keep the channels glued to the actual lug at any scale):
# lug_tip_r is the lug's outermost radius; the lug is a low SHELF (r lug_step_r..tip,
# lip_h tall) with no upper rib, so the roof (inner radius = lug_tip_r - roof_capture)
# can overhang 3mm inside the tip and grip the whole shelf lip without grazing.
lug_tip_r = plate_radius + lock_protrusion   # 52: lug tip radius (mm)
lug_step_r = lug_tip_r - roof_capture        # 49: shelf lip inner radius (mm)
ch_roof_in = lug_tip_r - roof_capture        # Roof overhang inner radius (mm)
ch_wall_in = lug_tip_r + ch_clear            # Channel outer-wall inner radius (mm)
ch_bury = 0.15            # Channel burial into the wall ring past ch_wall_in (mm):
                          # the roof + back-wall slab genuinely overlap the solid wall
                          # ring so mount_plate() fuses into ONE solid (no coincident
                          # faces -> the slicer sees the skirt cavity, not solid infill)

# Plate top-rim relief: the roof (r ch_roof_in..) and its pullout travel sit inside
# the plate radius, so the ceiling-side rim is cut back to relief_in over the three
# channel arcs (angular span = the roof's full drop->seat rotation sweep, plate-local).
relief_in = lug_step_r - 0.2              # 48.8: relief inner radius (mm)
relief_z_lo = lip_h                       # 1.2: shelf top; relief spans z 1.2..3
relief_ang_lo = ch_back_wall + ch_ang_rot # -20.5: roof fold-local at drop, plate-local
relief_ang_hi = ch_roof_end               # 22: roof fold-local at seat, plate-local

# Angular half-span of one lug about its center (arc mm -> rad at the rim).
lug_arc_angle = math.degrees(lug_width / plate_radius)

# Skirt top (cap_disc_h + cap_skirt_h above the mount origin) meets the base
# ceiling face (assembled base top = 2 + plate_thickness).
mount_offset_z = (2 + plate_thickness) - (cap_disc_h + cap_skirt_h)


# ============================================================
# Generic helpers replicating OpenSCAD builtins
# ============================================================

def cyl(r, h, z0=0.0):
    """cylinder(h=h, r=r) sitting at z0..z0+h (OpenSCAD default: base at origin)."""
    return cq.Solid.makeCylinder(r, h, pnt=Vector(0, 0, z0), dir=Vector(0, 0, 1))


def box(sx, sy, sz, corner=(0, 0, 0)):
    """cube([sx,sy,sz]) with default (non-centered) OpenSCAD corner semantics,
    optionally placed with its (0,0,0) corner translated to `corner`."""
    b = cq.Solid.makeBox(sx, sy, sz)
    return b.translate(corner)


def rotate_deg(shape, angle, axis=(0, 0, 1), about=(0, 0, 0)):
    ax0 = Vector(*about)
    ax1 = Vector(about[0] + axis[0], about[1] + axis[1], about[2] + axis[2])
    return shape.rotate(ax0, ax1, angle)


def polygon_extrude(points_xy, height, z0=0.0):
    """linear_extrude(height) of a 2D polygon defined in the XY plane,
    with the extrusion's base placed at z0."""
    wire = cq.Wire.makePolygon([Vector(x, y, 0) for x, y in points_xy], close=True)
    solid = cq.Solid.extrudeLinear(wire, [], Vector(0, 0, height))
    return solid.translate((0, 0, z0))


def revolve_profile(points_xz, angle=360, axis_pt0=(0, 0, 0), axis_pt1=(0, 0, 1)):
    """rotate_extrude() of a profile given as (x, z) points around the Z axis
    (x = radius, taken as the local XY-plane profile OpenSCAD rotates)."""
    wire = cq.Wire.makePolygon([Vector(x, 0, z) for x, z in points_xz], close=True)
    return cq.Solid.revolve(wire, [], angle, Vector(*axis_pt0), Vector(*axis_pt1))


def threefold_pattern(build_fn, fuse=True):
    """Reproduces build_fn() three times at 120-degree intervals.
    fuse=True boolean-unions the 3 copies (fine when each copy is a single clean
    solid, e.g. rim_channel). fuse=False just bundles them as a Compound instead -
    needed when build_fn() itself returns many touching pieces (e.g. a bent tab
    built from dozens of thin slices), where OCC's boolean fuse is unreliable across
    that many coincident/touching faces even though nothing actually overlaps."""
    a = build_fn()
    b = rotate_deg(build_fn(), 120)
    c = rotate_deg(build_fn(), -120)
    if fuse:
        return a.fuse(b).fuse(c)
    solids = list(a.Solids()) + list(b.Solids()) + list(c.Solids())
    return cq.Compound.makeCompound(solids)


# ============================================================
# Shared helpers (from OpenSCAD "Shared helpers" section)
# ============================================================

def polygon_extrude(points_xy, height, z0=0.0):
    """linear_extrude(height) of a 2D polygon defined in the XY plane,
    with the extrusion's base placed at z0."""
    wire = cq.Wire.makePolygon([Vector(x, y, 0) for x, y in points_xy], close=True)
    solid = cq.Solid.extrudeLinear(wire, [], Vector(0, 0, height))
    return solid.translate((0, 0, z0))


def revolve_profile(points_xz, angle=360, axis_pt0=(0, 0, 0), axis_pt1=(0, 0, 1)):
    """rotate_extrude() of a profile given as (x, z) points around the Z axis
    (x = radius, taken as the local XY-plane profile OpenSCAD rotates)."""
    wire = cq.Wire.makePolygon([Vector(x, 0, z) for x, z in points_xz], close=True)
    return cq.Solid.revolve(wire, [], angle, Vector(*axis_pt0), Vector(*axis_pt1))


def threefold_pattern(build_fn, fuse=True):
    """Reproduces build_fn() three times at 120-degree intervals.
    fuse=True boolean-unions the 3 copies (fine when each copy is a single clean
    solid, e.g. a monolithic lug)."""
    a = build_fn()
    b = rotate_deg(build_fn(), 120)
    c = rotate_deg(build_fn(), -120)
    if fuse:
        return a.fuse(b).fuse(c)
    solids = list(a.Solids()) + list(b.Solids()) + list(c.Solids())
    return cq.Compound.makeCompound(solids)


def lock_lug():
    """One monolithic twist-lock lug centred on +X, on the plate rim.

    Profile (r-z): a 3mm-wide shelf (r lug_step_r..lug_tip_r = 49..52), lip_h
    (1.2) tall, on the plate's light-side face. The roof overhangs 3mm past the
    tip and grips the shelf's top face on pullout; there is no upper rib (the
    roof occupies that z-band), so the back-wall stop acts on the shelf's back
    face. Built by revolving the r-z profile over the lug's angular span
    (`lug_width` mm of arc at the rim) - a single clean solid, no cylindric_bend
    slices. The shelf overlaps the plate ring (r 49..50) so the base boolean is
    a true union (single solid)."""
    half = lug_arc_angle / 2.0
    profile = [
        (lug_step_r, 0.0),
        (lug_tip_r, 0.0),
        (lug_tip_r, lip_h),
        (lug_step_r, lip_h),
    ]
    lug = revolve_profile(profile, angle=lug_arc_angle)
    return rotate_deg(lug, -half, axis=(0, 0, 1))


# ============================================================
# Base plate (ceiling side, male insert)
# ============================================================

def _screw_hole_solid():
    """Through-hole (r=screw_through_r) with a flush counterbore from the bottom face,
    both sitting at the local origin along +Z, ready to be translated/rotated into place."""
    through = cyl(screw_through_r, plate_thickness + 2, z0=-1)
    counterbore = cyl(screw_counterbore_r, screw_counterbore_d, z0=0)
    return through.fuse(counterbore)


def base_pocket():
    """Underside (light side) ring pocket to save filament. Screw bosses keep
    full plate thickness so the counterbores stay flush and the ceiling
    side remains a flat 1.8mm skin."""
    outer = cyl(base_pocket_outer, base_pocket_depth + 1, z0=-1)
    inner = cyl(base_pocket_inner, base_pocket_depth + 2, z0=-1)
    pocket = outer.cut(inner)
    for a in screw_angles:
        boss = cyl(base_pocket_boss_r, base_pocket_depth + 2, z0=-1)
        boss = boss.translate((screw_hole_radius, 0, 0))
        boss = rotate_deg(boss, a, axis=(0, 0, 1))
        pocket = pocket.cut(boss)
    return pocket


def base_top_relief():
    """Three arc-shaped pockets cut in the plate's ceiling-side rim so the
    mount's roof (r ch_roof_in.., z relief_z_lo..plate top) can overhang 3mm
    inside the plate radius and still seat and travel on pullout. One per lug;
    the angular span covers the roof's full drop->seat rotation sweep."""
    return threefold_pattern(
        lambda: annular_segment(relief_in, plate_radius, relief_z_lo,
                                plate_thickness, relief_ang_lo, relief_ang_hi))


def base_plate():
    plate = cyl(plate_radius, plate_thickness)
    wire_hole = cyl(wire_hole_radius, plate_thickness + 2, z0=-1)
    result = plate.cut(wire_hole)
    for a in screw_angles:
        sh = _screw_hole_solid()
        sh = sh.translate((screw_hole_radius, 0, 0))
        sh = rotate_deg(sh, a, axis=(0, 0, 1))
        result = result.cut(sh)
    result = result.cut(base_pocket())
    result = result.cut(base_top_relief())
    lugs = threefold_pattern(lock_lug, fuse=True)
    result = result.fuse(lugs)
    return result


# ============================================================
# Mount plate (light side, female socket)
# ============================================================

def cap_lip_chamfer():
    """Chamfered bottom lip: carves a 45-degree wedge of size cap_chamfer off the
    disc/wall corner (subtractive helper, rotate_extrude of a profile). A straight
    chamfer prints without the full-perimeter bottom overhang the old 2mm curved
    lip caused, and counters elephant's foot on the light-side edge."""
    eps = 0.1
    c = cap_chamfer
    r = cap_radius
    pts = [(r + eps, -eps), (r, c), (r - c, 0.0)]
    return revolve_profile(pts, 360)


def annular_segment(r1, r2, z1, z2, a1, a2):
    """Annular sector r1<=r<=r2, z z1..z2, angles a1..a2 (deg, around +X)."""
    n = max(2, math.ceil(abs(a2 - a1) / 2))
    outer = []
    for i in range(0, n + 1):
        a = a1 + (a2 - a1) * i / n
        outer.append((r2 * math.cos(math.radians(a)), r2 * math.sin(math.radians(a))))
    inner = []
    for i in range(0, n + 1):
        a = a2 - (a2 - a1) * i / n
        inner.append((r1 * math.cos(math.radians(a)), r1 * math.sin(math.radians(a))))
    pts = outer + inner
    return polygon_extrude(pts, z2 - z1, z0=z1)


def rim_channel():
    """One groove: outer wall ring + roof overhang (back 10deg) + back-wall slab.
    The roof and back-wall slab extend ch_bury past ch_wall_in into the solid wall
    ring, guaranteeing a true boolean union with the cap shell."""
    r_groove_in = plate_radius + ch_clear      # 50.2
    r_wall = ch_wall_in                        # 52.2
    r_outer = cap_radius

    a = annular_segment(r_wall, r_outer, ch_groove_bot, ch_block_top, ch_back_wall, ch_front)
    b = annular_segment(ch_roof_in, r_wall + ch_bury, ch_groove_top, ch_block_top, ch_back_wall, ch_roof_end)
    c = annular_segment(r_groove_in, r_wall + ch_bury, ch_groove_bot, ch_groove_top, ch_back_wall - 0.5, ch_back_wall + 1)
    return a.fuse(b).fuse(c)


def lock_channel():
    def build():
        return rotate_deg(rim_channel(), ch_ang_rot, axis=(0, 0, 1))
    return threefold_pattern(build)


def mount_plate():
    pilot_r = 1.45   # O2.9 pilot hole through the disc (no central boss)
    wire_off = 12.0  # O8 wire-exit hole center radius
    wire_r = 4.0     # O8 wire exit hole

    solid = cyl(cap_radius, cap_disc_h)
    solid = solid.fuse(cyl(cap_radius, cap_skirt_h, z0=cap_disc_h))

    hollow = cyl(ch_wall_in, cap_skirt_h + 0.2, z0=cap_disc_h - 0.1)
    pilot = cyl(pilot_r, cap_disc_h + 2, z0=-1)
    wire_hole = cyl(wire_r, cap_disc_h + 2, z0=-1).translate((wire_off, 0, 0))

    # Cup-side (invisible) lightening pocket: leaves a 1.0mm floor on the
    # light-side mounting face and a solid ring out to the wall.
    disc_pocket = cyl(disc_pocket_outer, disc_pocket_depth + 1, z0=cap_disc_h - disc_pocket_depth) \
        .cut(cyl(disc_pocket_inner, disc_pocket_depth + 2, z0=cap_disc_h - disc_pocket_depth))

    solid = solid.cut(hollow).cut(pilot).cut(wire_hole).cut(disc_pocket).cut(cap_lip_chamfer())
    solid = solid.fuse(lock_channel())
    return solid


# ============================================================
# Entry point (mirrors the OpenSCAD `if (view_mode == ...)` block)
# ============================================================

def _mount_seated():
    """Mount shown seated: rotate +10deg (= -ch_ang_rot) from the drop pose."""
    mount = rotate_deg(mount_plate(), -ch_ang_rot, axis=(0, 0, 1))
    return mount.translate((0, 0, mount_offset_z))


def build(view_mode=VIEW_MODE):
    if view_mode == "assembled":
        mount = _mount_seated()
        base = base_plate().translate((0, 0, 2))
        return mount.fuse(base)
    elif view_mode == "base_plate":
        return base_plate()
    elif view_mode == "mount_plate":
        return mount_plate()
    elif view_mode == "diff_check":
        mount = _mount_seated()
        base = base_plate().translate((0, 0, 2))
        return mount.intersect(base)
    else:
        raise ValueError(f"Unknown view_mode: {view_mode}")


if __name__ == "__main__":
    result = build(VIEW_MODE)
    mount = _mount_seated()
    base = base_plate().translate((0, 0, 2))

    # Pass each part as a separate argument with a label
    show(mount, base, names=["Mount", "Base Plate"])
    cq.exporters.export(cq.Workplane(obj = mount), "/home/ubuntu/workspace/models/spotlight_base/output/mount.stl")
    cq.exporters.export(cq.Workplane(obj = base), "/home/ubuntu/workspace/models/spotlight_base/output/base.stl")
    cq.exporters.export(cq.Workplane(obj = mount), "/home/ubuntu/workspace/models/spotlight_base/output/mount.step")
    cq.exporters.export(cq.Workplane(obj = base), "/home/ubuntu/workspace/models/spotlight_base/output/base.step")
    print("Exported. Mount volume:", mount.Volume())
    print("Exported. Base volume:", base.Volume())