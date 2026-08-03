"""Tier 3, part 1: seat fit — frame sanity, seat clearance, the
seat-interference question, and 3-fold symmetry."""
import math

import pytest

from conftest import SEAT_ROT, lug_grid


def _rotate_z(pt, deg):
    x, y, z = pt
    a = math.radians(deg)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z)


def test_frame_sanity_cross_check(base_contains, mount_contains):
    """Both probes agree in the assembly frame: shelf/annulus solid is base-only,
    roof solid is mount-only. The roof now sits OUTSIDE the plate radius, so the
    roof-contrast point moves to r 51 (roof band, beyond the plate rim)."""
    assert base_contains([(49.5, 0.0, 2.2)]) == [True]
    assert mount_contains([(49.5, 0.0, 2.2)]) == [False]
    assert base_contains([(51.0, 0.0, 4.5)]) == [False]   # beyond the plate rim
    assert mount_contains([(51.0, 0.0, 4.5)]) == [True]    # roof overhang band


def test_frame_oracle_settles_interference(base_contains, mount_contains):
    """At seat (rot=10, drop=0) no lug material may sit inside the mount."""
    pts = lug_grid()
    in_base = base_contains(pts)
    assert any(in_base), "lug grid must intersect the base at +X"
    lug_pts = [p for p, hit in zip(pts, in_base) if hit]
    assert len(lug_pts) >= 10, "expected a decent sample of lug material"
    hit_mount = mount_contains(lug_pts)
    assert not any(hit_mount), (
        f"{sum(hit_mount)}/{len(lug_pts)} lug points collide with the mount at seat"
    )


def test_seat_clearance(lug_points, mount_contains):
    """Seat pose: zero lug points inside mount material."""
    hit = mount_contains(lug_points, rot=SEAT_ROT, z_off=0.0)
    assert sum(hit) == 0, f"{sum(hit)}/{len(lug_points)} lug points in mount at seat"


def test_threefold_symmetry(lug_points, base_contains, mount_contains):
    """Rotating the +X lug grid by 120/240 deg reproduces the same results
    (catches fold-axis / wiring bugs)."""
    pts120 = [_rotate_z(p, 120.0) for p in lug_points]
    pts240 = [_rotate_z(p, 240.0) for p in lug_points]
    assert all(base_contains(pts120)), "120 deg copy must be inside base"
    assert all(base_contains(pts240)), "240 deg copy must be inside base"
    hit0 = sum(mount_contains(lug_points))
    hit120 = sum(mount_contains(pts120))
    hit240 = sum(mount_contains(pts240))
    assert hit0 == hit120 == hit240, f"mount contact counts differ: {hit0}/{hit120}/{hit240}"
