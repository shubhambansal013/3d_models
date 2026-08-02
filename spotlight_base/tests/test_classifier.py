"""Tier 2 ORACLE: prove the probe is correct on known points.

If anything here fails, the probe / frame math is broken — STOP, do not
touch the design or run the integration tests. Points are hand-picked in the
ASSEMBLY frame on known features; expected states follow from base.py params
and the assembly frame (base z 2..6, mount origin at mount_offset_z).
"""
import math

import base as sb

# (x, y, z, expected_in_base)  -- assembly frame
BASE_EXPECTED = [
    (20.0, 0.0, 4.0, False),    # wire-hole void
    (20.0, 0.0, 5.8, False),    # wire hole near ceiling face
    (0.0, 0.0, 4.0, False),     # wire-hole center
    (50.0, 0.0, 4.0, True),     # annulus mid-band
    (50.0, 0.0, 5.8, True),     # annulus near ceiling face
    (70.0, 0.0, 4.0, True),     # annulus outer band
    (74.5, 0.0, 3.0, True),     # rim / tab root
    (78.0, 0.0, 3.0, False),    # beyond plate and tab tip
    (0.0, 39.0, 3.0, False),    # M4 through-hole (90 deg)
    (0.0, -39.0, 3.0, False),   # M4 through-hole (270 deg)
    (20.0, 39.0, 3.0, False),   # inside the widened pocket band (r~43.8, z<1.2)
    (40.0, 40.0, 2.3, False),   # widened pocket void (r~56.6, z<1.2)
    (35.0, 0.0, 2.5, False),    # ring-pocket void
    (35.0, 0.0, 4.5, True),     # above pocket -> solid skin
    (60.0, 0.0, 2.2, False),    # widened pocket void
    (70.0, 0.0, 2.2, True),     # outside the pocket band (r>66) -> solid
    (74.9, 0.0, 3.5, True),     # tab body at root (crest ~2.4 base)
    (76.0, 0.0, 2.6, True),     # tab outer lip
    (76.0, 0.0, 3.6, False),    # above the tab lip crest
    (76.3, 0.0, 3.0, False),    # beyond the tab tip radius
]

# (x, y, z, expected_in_mount)  -- assembly frame, seat pose (rot=10, z_off=0)
MOUNT_EXPECTED = [
    (70.0, 0.0, -9.0, True),        # cap disc solid, outside the disc pocket (r>68)
    (5.0, 0.0, -9.0, True),         # cap disc beside the pilot hole
    (40.0, 0.0, -8.5, False),       # cap disc inside the cup-side pocket (r~40, z 2.0)
    (80.0, 0.0, 0.0, False),        # far outside the cap
    (40.0, 0.0, -5.0, False),       # hollow interior
    (0.0, 0.0, 3.8, False),         # hollow interior above the disc
    (77.0, 0.0, -5.0, True),        # skirt wall
    (77.0, 0.0, 5.0, True),         # skirt wall near the top
    (-77.0, 0.0, -5.0, True),       # skirt wall, opposite side
    (78.5, 0.0, -5.0, False),       # outside the skirt
    (0.0, 0.0, -12.0, False),       # no boss below the disc (removed by design)
    (0.0, 0.0, -11.0, False),       # boss pilot-hole void (through the disc)
    (12.0, 0.0, -9.0, False),       # wire-exit hole
    (76.0, 0.0, 3.8, True),         # channel roof
    (76.0, 0.0, 4.2, True),         # channel roof upper
    (76.0, 0.0, 4.8, False),        # above the roof top (ch_block_top)
    (76.0, 0.0, 2.0, False),        # groove void
    (76.3, 0.0, 2.0, False),        # groove void, outer part
    (75.3, 0.0, 3.8, False),        # radially inside the roof -> void
    (75.66, -7.22, 2.0, True),      # back-wall slab (assembly ang -5.45 deg)
    (71.4, 26.0, 2.0, False),       # front of the channel (assembly ang ~20)
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
