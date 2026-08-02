"""Tier 3, part 3: pullout — the roof overhang catches the lug when the mount
is pulled down (away from the ceiling).

z_off < 0 lowers the mount; the roof descends onto the lug's outer lip.
"""
import math

import base as sb
import pytest

from conftest import SEAT_ROT, grid


def _lip_grid():
    """Targeted grid on the lug's 1.2 mm lip (r ~51.5..52, z 3.2)."""
    # Lip spans r from lug_step_r (51.5) to lug_tip_r (52.0) at z = 2 + lip_h (3.2)
    # Sample 3 radial × 5 angular points on the +X lug
    ang_span = math.degrees(sb.lug_width / sb.plate_radius) / 2.0
    return grid(sb.lug_step_r, sb.lug_tip_r, 3, -ang_span, ang_span, 5, 3.2, 3.2, 1)


DROPS = [0.0, 0.5, 1.0, 1.5]


def test_pullout_roof_catch(mount_contains):
    lip_pts = _lip_grid()
    n0 = sum(mount_contains(lip_pts, rot=SEAT_ROT, z_off=0.0))
    assert n0 == 0, f"mount not free at seat: {n0}"

    for d in DROPS[1:]:
        n = sum(mount_contains(lip_pts, rot=SEAT_ROT, z_off=-d))
        if d >= 1.5:
            assert n >= 3, f"roof catch failed at drop {d} mm: {n} contact pts"
