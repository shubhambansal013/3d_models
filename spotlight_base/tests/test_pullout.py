"""Tier 3, part 3: pullout — the roof overhang catches the tab when the mount
is pulled down (away from the ceiling).

z_off < 0 lowers the mount; the roof descends onto the tab's outer lip.
"""
import pytest

from conftest import SEAT_ROT

DROPS = [0.0, 0.5, 1.0, 1.5]


def test_pullout_roof_catch(tab_points, mount_contains):
    n0 = sum(mount_contains(tab_points, rot=SEAT_ROT, z_off=0.0))
    assert n0 == 0, f"mount not free at seat: {n0}"

    for d in DROPS[1:]:
        n = sum(mount_contains(tab_points, rot=SEAT_ROT, z_off=-d))
        if d >= 1.0:
            assert n >= 3, f"roof catch failed at drop {d} mm: {n} contact pts"
