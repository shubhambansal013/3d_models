"""
CadQuery spotlight twist-lock ceiling mount.

Base plate (ceiling side): O150 annulus screwed flat to the real O150
ceiling base (2x M4, holes 78mm apart), with 3 lock tabs on its outer rim.
Mount plate (light side): O156 cap that twists ~10deg over the base rim,
fully hiding the base, with a central boss the spotlight screws onto.
"""
import math
import random
import cadquery as cq
from cadquery import Vector
from ocp_vscode import show

# ============================================================
# Global & Render Settings
# ============================================================
VIEW_MODE = "assembled"  # assembled, base_plate, mount_plate, lock_tab_linear, lock_channel_linear, diff_check
FN = 72  # curved-surface resolution (used to size arc sampling below)

# ============================================================
# Plate Dimensions
# ============================================================
plate_radius = 75.0       # Outer radius of the base plate annulus (mm); covers the real O150 ceiling base
plate_thickness = 2.0     # Thickness of the base plate (mm)
wire_hole_radius = 25.0   # Radius of the central wire through-hole (mm)
base_pocket_depth = 1.2   # Underside lightening pocket depth (mm)
base_pocket_inner = 28.0  # Pocket inner radius (mm)
base_pocket_outer = 66.0  # Pocket outer radius (mm); leaves a solid ring to the tab rim
base_pocket_boss_r = 4.5  # Full-depth circle kept around each screw (mm)
bend_steps = 24           # Segment count for the cylindrical bend

# ============================================================
# Screw Holes (M4 socket head, heads sit ~1mm proud, hidden in the cap cavity)
# ============================================================
screw_hole_radius = 39.0     # Radius of the M4 screw hole centers (mm); 2*39 = 78mm real hole spacing
screw_angles = [90, 270]     # Angular positions of the screw holes (deg)
screw_through_r = 2.1        # Through-hole radius for M4 (O4.2, mm)
screw_counterbore_r = 3.8    # Counterbore radius for socket-head M4 (O7.6, mm)
screw_counterbore_d = 3.0    # Counterbore depth (mm)

# ============================================================
# Lock Geometry
# ============================================================
lock_height = 3.0        # Overall height of the locking lip (mm)
lock_gap_height = 1.0    # Vertical slot height of the locking channel (mm)
lock_taper = 1.2         # Ramp length on the locking tab (mm)
lock_width = 8.0         # Width of the tab engagement surface (mm)
lock_protrusion = 1.5    # Total tab lip span (radial) (mm)

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

# Derived lock geometry (keep the channel glued to the actual tab at any scale):
# tab bend radius / root / tip (see lock_tab()); roof hangs `roof_capture` past the tip.
tab_bend_r = plate_radius + 1.0
tab_root_r = tab_bend_r - 1.25
tab_tip_r = tab_root_r + lock_protrusion
ch_roof_in = tab_tip_r - roof_capture   # Roof overhang inner radius (mm)
ch_wall_in = tab_tip_r + ch_clear       # Channel outer-wall inner radius (mm)

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


def convex_hull_2d(points):
    """Pure-Python 2D convex hull (Andrew's monotone chain), no external deps.
    points: iterable of (x, y). Returns hull vertices in CCW order."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def hull_solid(shapes):
    """Convex hull of the vertices of one or more solids -> a single solid.
    General-purpose, dependency-free stand-in for OpenSCAD's hull(), via brute-force
    O(n^3) facet enumeration. A tiny random jitter breaks exact coplanarity/collinearity
    so the "all other points on one side" test never has to special-case degenerate
    ties. Fine for the modest point counts this model produces (debug views only) -
    the two hull() calls on the hot path (lip_prism / lock_tab_linear) are instead
    built exactly via ruled lofts (see below) and don't use this at all."""
    rng = random.Random(0)
    pts = []
    for s in shapes:
        for v in s.Vertices():
            pts.append((v.X, v.Y, v.Z))
    # de-duplicate first (cheap), then jitter to break degeneracies
    pts = list({p for p in pts})
    eps = 1e-6
    jittered = [(x + rng.uniform(-eps, eps),
                 y + rng.uniform(-eps, eps),
                 z + rng.uniform(-eps, eps)) for x, y, z in pts]

    n = len(jittered)

    def sub(a, b):
        return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

    def cross3(a, b):
        return (a[1] * b[2] - a[2] * b[1],
                 a[2] * b[0] - a[0] * b[2],
                 a[0] * b[1] - a[1] * b[0])

    def dot(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    faces = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                p0, p1, p2 = jittered[i], jittered[j], jittered[k]
                normal = cross3(sub(p1, p0), sub(p2, p0))
                nrm = math.sqrt(dot(normal, normal))
                if nrm < 1e-12:
                    continue  # collinear triple, not a face
                pos = neg = False
                for m in range(n):
                    if m in (i, j, k):
                        continue
                    d = dot(normal, sub(jittered[m], p0))
                    if d > 1e-9:
                        pos = True
                    elif d < -1e-9:
                        neg = True
                    if pos and neg:
                        break
                if pos and neg:
                    continue  # points on both sides -> not a hull face
                # orient outward: all other points must be on the "neg" side of normal
                if pos and not neg:
                    normal = tuple(-c for c in normal)
                    p1, p2 = p2, p1
                faces.append((p0, p1, p2))

    cq_faces = []
    for p0, p1, p2 in faces:
        wire = cq.Wire.makePolygon([Vector(*p0), Vector(*p1), Vector(*p2)], close=True)
        cq_faces.append(cq.Face.makeFromWires(wire))

    # Tolerant sewing (rather than strict Shell.makeShell/Solid.makeSolid) copes with
    # the near-degenerate slivers the tessellated "point" circles can produce.
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopoDS import TopoDS

    sewing = BRepBuilderAPI_Sewing(1e-4)
    for f in cq_faces:
        sewing.Add(f.wrapped)
    sewing.Perform()
    sewn = sewing.SewedShape()
    shell = TopoDS.Shell_s(sewn) if sewn.ShapeType().name == "SHELL" else None
    if shell is None:
        # fall back: take the first shell found inside whatever sewing produced
        shell = cq.Shape.cast(sewn).Shells()[0].wrapped
    solid = ShapeFix_Solid().SolidFromShell(shell)
    result = cq.Solid(solid)
    if result.Volume() < 0:
        result = cq.Solid(solid.Reversed())
    result = result.clean()
    if not result.isValid():
        raise RuntimeError(
            "hull_solid() produced a non-manifold/invalid shape for this point set "
            "(this brute-force fallback is only exercised by the lock_channel_linear "
            "debug view - the main assembled/base_plate/mount_plate/lock_tab_linear "
            "geometry never calls it). Reduce circle tessellation or inspect the "
            "input points if you need this specific view."
        )
    return result


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

def _circle_pts(r, n=16, center=(0.0, 0.0)):
    cx, cy = center
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def _wire_at_z(points_xy, z):
    return cq.Wire.makePolygon([Vector(x, y, z) for x, y in points_xy], close=True)


def lip_prism():
    """hull(tiny near-point cylinder @ z~0.01, triangular prism from z=lock_taper..+5).
    Since the "point" is by far the smallest cross-section and the triangle only grows
    from there (never shrinks), the hull is exactly: a ruled loft from the tiny circle
    up to the triangle, fused with the constant-cross-section prism above it - so this
    is built directly, with no generic hull() needed."""
    bottom = _wire_at_z(_circle_pts(0.05, n=16), 0.01)
    tri_pts = [(0, lock_protrusion), (1, 0), (-1, 0)]
    top = _wire_at_z(tri_pts, lock_taper)
    cone = cq.Solid.makeLoft([bottom, top], ruled=True)
    prism = polygon_extrude(tri_pts, 5, z0=lock_taper)
    return cone.fuse(prism)


def lock_tab_linear():
    """hull(lip_prism(), lip_prism() shifted +lock_width in X), then cut to height.
    Both lip_prisms share the same z-profile (tiny circle -> triangle -> constant
    prism), just offset in X, so the combined hull's cross-section at any z is simply
    the 2D convex hull of the two individual cross-sections at that same z - built
    exactly via 2D hulls at the two key z-levels, ruled-lofted between them."""
    bottom_pts = convex_hull_2d(
        _circle_pts(0.05, n=16, center=(0, 0)) + _circle_pts(0.05, n=16, center=(lock_width, 0))
    )
    tri_a = [(0, lock_protrusion), (1, 0), (-1, 0)]
    tri_b = [(lock_width, lock_protrusion), (lock_width + 1, 0), (lock_width - 1, 0)]
    top_pts = convex_hull_2d(tri_a + tri_b)

    bottom = _wire_at_z(bottom_pts, 0.01)
    top = _wire_at_z(top_pts, lock_taper)
    cone = cq.Solid.makeLoft([bottom, top], ruled=True)
    prism = polygon_extrude(top_pts, 5, z0=lock_taper)
    h = cone.fuse(prism)

    cut_box = box(20, 20, 20, corner=(-10, -10, lock_height - lock_gap_height))
    return h.cut(cut_box)


def cylindric_bend(child, size_x, size_y, size_z, radius, nsteps):
    """Bends a flat child object (extending in +Y, within [0,size_x]x[0,size_y]x[0,size_z])
    around a cylinder of the given radius, in `nsteps` flat facets - direct port of the
    OpenSCAD cylindric_bend() module.

    Returns a Compound of the (nsteps+1) touching slices rather than a boolean-fused
    solid: each slice only touches its neighbour along a shared cut plane (no true
    overlap), but OCC's boolean fuse is unreliable when chained across dozens of such
    coincident/touching faces - in testing it silently discarded all but a sliver of
    the material. A Compound of touching solids tessellates identically to a fused
    solid for STL/3D-printing purposes, so nothing is lost by skipping the fuse."""
    step_angle = math.degrees(math.atan(size_y / (radius * nsteps)))
    steps = nsteps
    step_width = size_y / steps

    pieces = []

    # central sliver at the tangent point (untransformed)
    center_cube = box(size_x, step_width * 0.5, size_z)
    pieces.append(child.intersect(center_cube))

    for step in range(1, steps + 1):
        slice_cube = box(size_x, step_width, size_z, corner=(0, (step - 0.5) * step_width, 0))
        piece = child.intersect(slice_cube)
        piece = piece.translate((0, -step * step_width, 0))
        piece = rotate_deg(piece, step_angle * step, axis=(1, 0, 0))
        piece = piece.translate((
            0,
            radius * math.sin(math.radians(step_angle * step)),
            radius * (1 - math.cos(math.radians(step_angle * step))),
        ))
        pieces.append(piece)

    return cq.Compound.makeCompound(pieces)


def lock_tab():
    bend_r = plate_radius + 1.0

    def build():
        # translate([0, lock_width+1, 1.25]) rotate([0,-90,0]) rotate([0,0,90]) rotate([0,180,0]) lock_tab_linear();
        child = lock_tab_linear()
        child = rotate_deg(child, 180, axis=(0, 1, 0))
        child = rotate_deg(child, 90, axis=(0, 0, 1))
        child = rotate_deg(child, -90, axis=(0, 1, 0))
        child = child.translate((0, lock_width + 1, 1.25))

        bent = cylindric_bend(child, 8, 10.5, 8, bend_r, bend_steps)

        # rotate([0,90,0]) translate([-(plate_radius+1.0),0,2]) rotate([0,0,180+offset])
        result = rotate_deg(bent, 90, axis=(0, 1, 0))
        result = result.translate((-(plate_radius + 1.0), 0, 2))
        offset = (lock_width / 2 + 1) / bend_r * (180 / math.pi)
        result = rotate_deg(result, 180 + offset, axis=(0, 0, 1))
        return result

    return threefold_pattern(build, fuse=False)


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
    side remains a flat 2mm skin."""
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
    # lock_tab() is a Compound of many touching (not overlapping) slices; a boolean
    # fuse with it is unreliable (see cylindric_bend), so bundle everything into one
    # Compound instead - identical result for STL/3D-printing purposes.
    return cq.Compound.makeCompound([result] + list(lock_tab().Solids()))


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
# Debug-view helper (view_mode = "lock_channel_linear")
# ============================================================

def lock_channel_linear():
    def hull_pair(off_a, z_a, off_b, z_b):
        a = lip_prism().translate((off_a, 0, z_a))
        b = lip_prism().translate((off_b, 0, z_b))
        return hull_solid([a, b])

    parts = [
        hull_pair(0, 0, lock_taper, -lock_gap_height * 0.5),
        hull_pair(lock_taper, -0.5, lock_taper * 2, -lock_gap_height * 0.25),
        hull_pair(lock_taper * 2, -0.25, lock_taper * 3 + lock_width, -0.25),
        hull_pair(lock_taper * 3 + lock_width, -(lock_height + lock_gap_height - lock_taper),
                   lock_taper * 4 + lock_width, -(lock_height + lock_gap_height - lock_taper)),
    ]
    union = parts[0]
    for p in parts[1:]:
        union = union.fuse(p)

    cut1 = box(20, 20, 20, corner=(-10, -10, 2.0))
    cut2 = box(20, 20, 20, corner=(-10, -10, -21.0))
    return union.cut(cut1).cut(cut2)


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
    elif view_mode == "lock_tab_linear":
        return lock_tab_linear()
    elif view_mode == "lock_channel_linear":
        return lock_channel_linear()
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