"""
CadQuery spotlight twist-lock ceiling mount.

Base plate (ceiling side): O100 annulus screwed flat to the real ceiling
(2x M4, holes 78mm apart), with 3 monolithic lugs on its outer rim for the
twist-lock. Mount plate (light side): cap that twists ~10deg over the base rim,
with a central boss the spotlight screws onto (cap sizes still O156 pending the
phase-2 rebuild).
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
# Lock Lugs (monolithic twist-lock teeth, revolve-built, no cylindric_bend)
# ============================================================
lock_protrusion = 2.0     # Radial proud of the lug past the plate rim (mm); tip at r 52
lug_width = 14.0          # Lug arc width measured along the rim (mm)
lug_angles = [0, 120, 240]  # Angular centers of the three lugs (deg)
lock_height = plate_thickness  # Full lug height at the root (mm)
lip_h = 1.2               # Height of the stepped tip lip (mm); lip top native z = 1.2
root_fillet = 0.8         # Fillet radius where the lug meets the plate rim (mm)

# ============================================================
# Cap & Lock Channel
# ============================================================
cap_radius = 78.0     # O156/2: cap disc and skirt outer radius (mm); 3mm overhang hides the base edge
cap_disc_h = 2.5      # Disc thickness (light-side mounting face) (mm)
cap_skirt_h = 14.0    # Skirt depth (mm)
cap_fillet_r = 2.0    # Fillet radius on disc/wall junction (mm)
ch_ang_rot = -10      # Channel fold-copy axis rotation (deg)
ch_clear = 0.2        # Radial clearance to the tab outer face (mm)
ch_back_wall = -5.2   # Groove back wall (fold-local deg)
ch_front = 15.2       # Groove open entrance (fold-local deg)
ch_roof_end = 4.8     # Roof front edge (fold-local deg)
roof_capture = 0.6    # Roof overhang depth past the tab tip (mm); sized for print tolerance
ch_groove_bot = 12.3  # Groove floor (mount-local z)
ch_groove_top = 14.0  # Groove ceiling (mount-local z); gives ~0.3mm crest clearance
ch_block_top = 15.0   # Channel block top (mount-local z); roof thickness 1.0 >= 0.8 min wall
disc_pocket_depth = 1.0   # Cup-side lightening pocket depth in the mount disc (mm)
disc_pocket_inner = 8.0   # Pocket inner radius: clears the central pilot/hub (mm)
disc_pocket_outer = 68.0  # Pocket outer radius: leaves a solid ring to the skirt (mm)

# Derived lock geometry (keep the channels glued to the actual lug at any scale):
# lug_tip_r is the lug's outermost radius; the root stays full-height out to
# lug_step_r so the phase-2 roof (inner radius = lug_tip_r - roof_capture = 51.4)
# clears the full-height root and only captures the 1.2mm lip.
lug_tip_r = plate_radius + lock_protrusion   # 52: lug tip radius (mm)
lug_step_r = lug_tip_r - 0.6                 # 51.4: full-height root radius, lip starts past this
lug_overlap = 0.5             # Lug root buried this far into the plate rim (mm)
lug_root_r = plate_radius - lug_overlap      # 49.5: guarantees a true boolean union
ch_roof_in = lug_tip_r - roof_capture   # Roof overhang inner radius (mm)
ch_wall_in = lug_tip_r + ch_clear       # Channel outer-wall inner radius (mm)

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


def _lug_root_edges(shape, r, z_top, tol=0.02):
    """Straight edges at radius `r` running the full plate height z 0..z_top:
    exactly the two concave junctions where a lug's side face meets the rim."""
    out = []
    for e in shape.Edges():
        vs = e.Vertices()
        if len(vs) != 2:
            continue
        p0, p1 = vs[0], vs[1]
        r0 = math.hypot(p0.X, p0.Y)
        r1 = math.hypot(p1.X, p1.Y)
        zs = sorted([p0.Z, p1.Z])
        if abs(r0 - r) < tol and abs(r1 - r) < tol and abs(zs[0]) < tol and abs(zs[1] - z_top) < tol:
            out.append(e)
    return out


def lock_lug():
    """One monolithic twist-lock lug centred on +X, on the plate rim.

    Profile (r-z): full `lock_height` rib out to `lug_step_r` (51.4), then a
    vertical step down to a `lip_h` (1.2) lip over the outer `lock_protrusion`
    band (r .. lug_tip_r = 52). Built by revolving the r-z profile over the
    lug's angular span (`lug_width` mm of arc at the rim) - a single clean
    solid, no cylindric_bend slices. The root is buried `lug_overlap` into the
    plate rim so the base boolean is a true union (single solid); the 0.8 mm
    root fillet is applied on the fused junction edges in base_plate()."""
    half = lug_arc_angle / 2.0
    profile = [
        (lug_root_r, 0.0),
        (lug_step_r, 0.0),
        (lug_tip_r, 0.0),
        (lug_tip_r, lip_h),
        (lug_step_r, lip_h),
        (lug_step_r, lock_height),
        (lug_root_r, lock_height),
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
    lugs = threefold_pattern(lock_lug, fuse=True)
    result = result.fuse(lugs)
    # Root fillets at the 6 concave junctions where the lugs meet the rim.
    edges = _lug_root_edges(result, plate_radius, lock_height)
    if len(edges) == 6:
        result = result.fillet(root_fillet, edges)
    return result


# ============================================================
# Mount plate (light side, female socket)
# ============================================================

def cap_lip_fillet():
    """Rounded bottom lip: carves a quarter-disc of radius cap_fillet_r off the
    disc/wall corner (subtractive helper, rotate_extrude of a profile)."""
    eps = 0.1
    r = cap_radius + eps
    n = math.ceil(FN / 4)
    pts = [(r, -eps)]
    for i in range(0, n + 1):
        a = 180 - 90 * i / n
        pts.append((r + cap_fillet_r * math.cos(math.radians(a)),
                     -eps + cap_fillet_r * math.sin(math.radians(a))))
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
    """One groove: outer wall ring + roof overhang (back 10deg) + back-wall slab."""
    r_groove_in = plate_radius + ch_clear      # 75.2
    r_wall = ch_wall_in                        # 76.45
    r_outer = cap_radius

    a = annular_segment(r_wall, r_outer, ch_groove_bot, ch_block_top, ch_back_wall, ch_front)
    b = annular_segment(ch_roof_in, r_wall, ch_groove_top, ch_block_top, ch_back_wall, ch_roof_end)
    c = annular_segment(r_groove_in, r_wall, ch_groove_bot, ch_groove_top, ch_back_wall - 0.5, ch_back_wall)
    return a.fuse(b).fuse(c)


def lock_channel():
    def build():
        return rotate_deg(rim_channel(), ch_ang_rot, axis=(0, 0, 1))
    return threefold_pattern(build)


def mount_plate():
    boss_r = 4.75    # O9.5 central boss (light-side, spotlight mount)
    boss_h = 5.0
    pilot_r = 2.9   # O2.9 pilot hole through the boss
    wire_off = 12.0  # O8 wire-exit hole center radius
    wire_r = 5.0

    solid = cyl(cap_radius, cap_disc_h)
    solid = solid.fuse(cyl(cap_radius, cap_skirt_h, z0=cap_disc_h))
    # solid = solid.fuse(cyl(boss_r, boss_h + cap_disc_h, z0=-boss_h))

    hollow = cyl(ch_wall_in, cap_skirt_h + 0.2, z0=cap_disc_h - 0.1)
    pilot = cyl(pilot_r, boss_h + cap_disc_h + 2, z0=-boss_h - 1)
    wire_hole = cyl(wire_r, cap_disc_h + 2, z0=-1).translate((wire_off, 0, 0))

    # Cup-side (invisible) lightening pocket: leaves a 1.5mm floor on the
    # light-side mounting face and a solid ring out to the skirt.
    disc_pocket = cyl(disc_pocket_outer, disc_pocket_depth + 1, z0=cap_disc_h - disc_pocket_depth) \
        .cut(cyl(disc_pocket_inner, disc_pocket_depth + 2, z0=cap_disc_h - disc_pocket_depth))

    solid = solid.cut(hollow).cut(pilot).cut(wire_hole).cut(disc_pocket).cut(cap_lip_fillet())
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