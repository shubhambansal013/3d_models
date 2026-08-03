"""Tier 3, part 6: twist-lock attach/detach PATH — the full drop -> seat twist
-> release twist -> lift trajectory, plus the sliding-fit clearances that gate
"ease" (not just geometric freedom).

Why this exists: the old suite only probed endpoint poses (seat, stop window)
and only asserted NO COLLISION. A press-fit twist (ch_clear=0.2) sails through
every no-collision probe yet binds hard on a printed part — that gap was how
the stiff lock slipped through. These tests WALK the trajectory and assert the
clearances that govern FDM effort:

  - radial sliding gap (lug tip face -> channel outer-wall inner) >= 0.30 mm
      (sliding-twist fit; 0.1-0.2 mm is press/snap and prints as a bind)
  - roof gap (lug lip top -> roof bottom) >= 0.60 mm (room to seat and travel)

Poses (assembly frame): base z 2..5, mount origin at mount_offset_z; drop =
rot 0, seat = rot 10, back-wall stop onset ~11.5-12 deg. Detach is the reverse
of the seat twist plus the lift, so the same pose set covers both directions.
"""
import math

import base as sb

from conftest import twist_lug_points


def _collisions(mount_contains, pts, rot, z_off):
    return sum(mount_contains(pts, rot=rot, z_off=z_off))


# --- attach / detach trajectory ---------------------------------------------

def test_attach_drop_is_free(twist_lug_points, mount_contains):
    """Lowering the mount onto the base at rot=0 (drop-on) is collision-free
    from above through the seated position and a little below it."""
    for z_off in (0.6, 0.4, 0.2, 0.0, -0.2):
        assert _collisions(mount_contains, twist_lug_points, 0.0, z_off) == 0, \
            f"drop-on blocked at z_off={z_off}"


def test_drop_tolerates_misalignment(twist_lug_points, mount_contains):
    """The lugs are hidden under the cap, so attach alignment is by feel; the
    drop must not bind a few degrees either side of the ideal drop pose."""
    for rot in (-4.0, -2.0, 2.0, 4.0):
        assert _collisions(mount_contains, twist_lug_points, rot, 0.0) == 0, \
            f"drop-on blocked at rot={rot}"


def test_seat_twist_path_is_free(twist_lug_points, mount_contains):
    """The full attach twist rot 0..11 (back-wall stop onset ~11.5-12) is
    collision-free at every degree; the release twist is the same path in
    reverse, so this covers detach too."""
    for rot in range(12):  # 0..11
        assert _collisions(mount_contains, twist_lug_points, float(rot), 0.0) == 0, \
            f"twist blocked at rot={rot}"


def test_detach_lift_is_free(twist_lug_points, mount_contains):
    """After twisting back to the drop pose, lifting the mount off is free:
    the roof clears the lug lip vertically through the whole lift."""
    for z_off in (0.0, 0.3, 0.6, 0.9, 1.2):
        assert _collisions(mount_contains, twist_lug_points, 0.0, z_off) == 0, \
            f"lift-off blocked at z_off={z_off}"


def test_reverse_twist_detach_is_free(twist_lug_points, mount_contains):
    """DETACH: twist the mount back past the drop pose to rot -21 (where the roof
    clears the lugs angularly) and pull it off — the whole path is collision-free.
    At the drop pose the roof still overhangs the shelf (test below), so the free
    detach needs the reverse twist; the radial-trap fix (roof outside the plate
    radius) is what makes it possible at all."""
    for rot in range(10, -22, -1):  # 10..-21
        assert _collisions(mount_contains, twist_lug_points, float(rot), 0.0) == 0, \
            f"release twist blocked at rot={rot}"
    for d in (0.5, 1.0, 1.5, 2.0, 3.0):
        assert _collisions(mount_contains, twist_lug_points, -21.0, -d) == 0, \
            f"pull-off at rot=-21 blocked at z_off=-{d}"


def test_drop_alignment_pull_binds(twist_lug_points, mount_contains):
    """Intended: at the drop alignment (rot 0) a straight pull DOES bind — the roof
    catches the shelf's outer 1.5mm band (the lock grip). Free detach requires the
    ~21deg reverse twist first."""
    assert _collisions(mount_contains, twist_lug_points, 0.0, -1.5) >= 3, \
        "expected the drop-pose pull to catch the shelf"


# --- ease gates: the clearances that make it operate without force -----------

def _walk_radial_gap(mount_contains, rot, ang_deg=0.0, z=3.0, step=0.05, n=13):
    """Free radial gap [mm] from the lug tip face (r = lug_tip_r) outward to
    the first mount material (the channel outer-wall inner face)."""
    a = math.radians(ang_deg)
    pts = [( (sb.lug_tip_r + step * i) * math.cos(a),
             (sb.lug_tip_r + step * i) * math.sin(a), z) for i in range(n)]
    hit = mount_contains(pts, rot=rot)
    for i, h in enumerate(hit):
        if h:
            return step * i
    return None


def _walk_roof_gap(mount_contains, rot, r=52.0, ang_deg=0.0, step=0.05, n=26):
    """Free vertical gap [mm] from the lug lip top (z = 2 + lip_h) upward to
    the first mount material (the channel roof bottom)."""
    a = math.radians(ang_deg)
    z0 = 2.0 + sb.lip_h
    pts = [(r * math.cos(a), r * math.sin(a), z0 + step * i) for i in range(n)]
    hit = mount_contains(pts, rot=rot)
    for i, h in enumerate(hit):
        if h:
            return step * i
    return None


def test_radial_sliding_gap_is_sliding_fit(mount_contains):
    """The lug tip rides the channel outer wall through the entire twist. A
    press/snap gap (< 0.3 mm) binds all three lugs on a printed part, so the
    gap must stay in the sliding-twist range at every stage of the path."""
    for rot in (0.0, 5.0, 10.0):
        gap = _walk_radial_gap(mount_contains, rot)
        assert gap is not None, f"no channel wall found radially at rot={rot}"
        assert 0.30 <= gap <= 0.55, \
            f"radial sliding gap {gap:.3f} mm at rot={rot} out of sliding range (0.30-0.55)"


def test_roof_gap_keeps_seat_clearance(mount_contains):
    """The roof bottom must clear the lug lip top through the twist so the
    mount seats and travels without the roof grinding the lip."""
    for rot in (0.0, 5.0, 10.0):
        gap = _walk_roof_gap(mount_contains, rot)
        assert gap is not None, f"no roof found above the lug at rot={rot}"
        assert 0.60 <= gap <= 1.00, \
            f"roof gap {gap:.3f} mm at rot={rot} out of range (0.60-1.00)"
