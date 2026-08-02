"""Tier 2 ORACLE: prove the probe is correct on known points.

If anything here fails, the probe / frame math is broken — STOP, do not
touch the design or run the integration tests. Points are hand-picked in the
ASSEMBLY frame on known features; expected states follow from base.py params
and the assembly frame (base z 2..5, mount origin at mount_offset_z).
"""
import math

import base as sb

# (x, y, z, expected_in_base)  -- assembly frame
BASE_EXPECTED = [
    (15.0, 0.0, 3.5, False),    # wire-hole void (r<20)
    (15.0, 0.0, 4.8, False),    # wire hole near ceiling face
    (0.0, 0.0, 3.5, False),     # wire-hole center
    (30.0, 0.0, 3.5, True),     # annulus mid-band
    (30.0, 0.0, 4.8, True),     # annulus near ceiling face
    (48.0, 0.0, 3.5, True),     # annulus outer band
    (49.5, 0.0, 2.5, True),     # lug root (r=49.5, full height)
    (52.5, 0.0, 2.5, False),    # beyond lug tip
    (0.0, 39.0, 3.0, False),    # M4 through-hole (90 deg)
    (0.0, -39.0, 3.0, False),   # M4 through-hole (270 deg)
    (20.0, 39.0, 3.0, False),   # inside the widened pocket band (r~43.8, z<3.2)
    (40.0, 40.0, 2.5, False),   # widened pocket void (r~56.6, z<3.2)
    (35.0, 0.0, 2.8, False),    # ring-pocket void (z < 3.2)
    (35.0, 0.0, 4.5, True),     # above pocket -> solid skin
    (45.0, 0.0, 2.8, False),    # widened pocket void
    (49.0, 0.0, 2.8, True),     # outside the pocket band (r>48) -> solid
    (51.0, 0.0, 2.5, True),     # lug body at root (full height 3mm)
    (51.7, 0.0, 3.0, True),     # lug stepped lip (z 1.2..3.0 at r 51.4..52)
    (51.7, 0.0, 3.5, False),    # above the lug lip
    (52.3, 0.0, 2.5, False),    # beyond the lug tip radius
]

# (x, y, z, expected_in_mount)  -- assembly frame, seat pose (rot=10, z_off=0)
MOUNT_EXPECTED = [
    (40.0, 0.0, -9.0, True),        # cap disc solid, outside the disc pocket (r>48)
    (5.0, 0.0, -9.0, True),         # cap disc beside the pilot hole
    (30.0, 0.0, -8.5, False),       # cap disc inside the cup-side pocket (r~30, z -9)
    (60.0, 0.0, 0.0, False),        # far outside the cap
    (30.0, 0.0, -5.0, False),       # hollow interior
    (0.0, 0.0, -2.0, False),        # hollow interior above the disc
    (53.5, 0.0, -5.0, True),        # skirt wall (r=54)
    (53.5, 0.0, 4.0, True),         # skirt wall near the top
    (-53.5, 0.0, -5.0, True),       # skirt wall, opposite side
    (54.5, 0.0, -5.0, False),       # outside the skirt
    (0.0, 0.0, -12.0, False),       # no boss below the disc (removed by design)
    (0.0, 0.0, -11.0, False),       # pilot-hole void (through the disc)
    (12.0, 0.0, -9.0, False),       # wire-exit hole (r=4 at r=12 offset)
    (52.0, 0.0, 4.0, True),         # channel roof (ch_roof_in=51.4, roof at z 4..5)
    (52.0, 0.0, 4.5, True),         # channel roof upper
    (52.0, 0.0, 5.2, False),        # above the roof top (ch_block_top + mount_offset_z = 5)
    (52.0, 0.0, 1.5, False),        # groove void (floor at z 1.5)
    (51.5, 0.0, 1.5, False),        # groove void, inner part (inside roof)
    (51.0, 0.0, 4.0, False),        # radially inside the roof -> void
    (51.4, -10.5, 1.5, True),        # back-wall slab (assembly ang -10.5°)
    (50.0, 12.0, 1.5, False),       # front of the channel (assembly ang ~ 12°)
]


def _named_fail(pts, got, expected):
    for (x, y, z, want), g in zip(pts, got):
        if g != want:
            return (x, y, z, "IN" if want else "OUT", "IN" if g else "OUT")
    return None


def test_base_oracle(base_contains):
    pts = [(x, y, z) for x, y, z, _ in BASE_EXPECTED]
    got = base_contains(pts)
    for (x, y, z, want), g in zip(BASE_EXPECTED, got):
        assert g == want, f"base oracle @({x:.1f},{y:.1f},{z:.1f}): expected {'IN' if want else 'OUT'}, got {'IN' if g else 'OUT'}"


def test_mount_oracle(mount_contains):
    pts = [(x, y, z) for x, y, z, _ in MOUNT_EXPECTED]
    got = mount_contains(pts)
    for (x, y, z, want), g in zip(MOUNT_EXPECTED, got):
        assert g == want, f"mount oracle @({x:.1f},{y:.1f},{z:.1f}): expected {'IN' if want else 'OUT'}, got {'IN' if g else 'OUT'}"
