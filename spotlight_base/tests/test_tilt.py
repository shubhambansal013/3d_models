"""Tier 3, part 5: tilt tolerance — the seat clearance survives plate tilt.

At the seated pose, shift lug sample points DOWN by 0.5 mm (simulated plate
tilt/gap) and assert still zero collisions. Shift UP by +0.3 mm (plate proud)
and assert still zero collisions. This locks the flush tolerance that the
old 0.3 mm design could not tolerate.
"""
import pytest

from conftest import SEAT_ROT, lug_points


def test_tilt_gap_down(lug_points, mount_contains):
    """Plate tilts/gaps downward 0.5 mm at the lugs — roof clearance must survive."""
    hit = mount_contains(lug_points, rot=SEAT_ROT, z_off=0.5)
    assert sum(hit) == 0, (
        f"{sum(hit)}/{len(lug_points)} lug points collide with mount at seat +0.5 mm drop"
    )


def test_tilt_gap_up(lug_points, mount_contains):
    """Plate is proud +0.3 mm at the lugs — roof clearance must survive."""
    hit = mount_contains(lug_points, rot=SEAT_ROT, z_off=-0.3)
    assert sum(hit) == 0, (
        f"{sum(hit)}/{len(lug_points)} lug points collide with mount at seat -0.3 mm (proud)"
    )