"""Tier 3, part 1: seat fit — frame sanity, seat clearance, the
seat-interference question, and 3-fold symmetry."""
import math

import pytest

from conftest import SEAT_ROT, tab_grid


def _rotate_z(pt, deg):
    x, y, z = pt
    a = math.radians(deg)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z)


def test_frame_sanity_cross_check(base_contains, mount_contains):
    """Both probes agree in the assembly frame: annulus solid is base-only,
    roof solid is mount-only."""
    assert base_contains([(50.0, 0.0, 4.0)]) == [True]
    assert mount_contains([(50.0, 0.0, 4.0)]) == [False]
    assert base_contains([(76.0, 0.0, 3.8)]) == [False]
    assert mount_contains([(76.0, 0.0, 3.8)]) == [True]


def test_frame_oracle_settles_interference(base_contains, mount_contains):
    """At seat (rot=10, drop=0) no tab material may sit inside the mount.
    This is the exact OCC cross-check for the '0.9 mm into the roof' open
    question from the handoff — the answer comes from the kernel, not a render."""
    pts = tab_grid()
    in_base = base_contains(pts)
    assert any(in_base), "tab grid must intersect the base at +X"
    tab_pts = [p for p, hit in zip(pts, in_base) if hit]
    assert len(tab_pts) >= 10, "expected a decent sample of tab material"
    hit_mount = mount_contains(tab_pts)
    assert not any(hit_mount), (
        f"{sum(hit_mount)}/{len(tab_pts)} tab points collide with the mount at seat"
    )


def test_seat_clearance(tab_points, mount_contains):
    """Seat pose: zero tab points inside mount material."""
    hit = mount_contains(tab_points, rot=SEAT_ROT, z_off=0.0)
    assert sum(hit) == 0, f"{sum(hit)}/{len(tab_points)} tab points in mount at seat"


def test_threefold_symmetry(tab_points, base_contains, mount_contains):
    """Rotating the +X tab grid by 120/240 deg reproduces the same results
    (catches fold-axis / wiring bugs)."""
    pts120 = [_rotate_z(p, 120.0) for p in tab_points]
    pts240 = [_rotate_z(p, 240.0) for p in tab_points]
    assert all(base_contains(pts120)), "120 deg copy must be inside base"
    assert all(base_contains(pts240)), "240 deg copy must be inside base"
    hit0 = sum(mount_contains(tab_points))
    hit120 = sum(mount_contains(pts120))
    hit240 = sum(mount_contains(pts240))
    assert hit0 == hit120 == hit240, f"mount contact counts differ: {hit0}/{hit120}/{hit240}"
