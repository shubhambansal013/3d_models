"""Tier 3, part 2: rotation stop — the lug meets the channel back wall.

Rotation `rot` is the mount's absolute rotation in the assembly frame;
rot=10 is the seated pose. The stop is probed analytically: the mount's
back-wall slab occupies a known ~0.5 deg-wide angular window at each rot,
so we sample base (lug) material in exactly that window (3x3x3 points =
bounded). Lug material there means the back wall is up against the lug.

Measured via the kernel (2026-08-02): free through rot ~11.5, blocked from
rot ~12.0 (onset moved ~0.5 deg earlier after the back-wall enlargement;
NOT the handoff's ~18 — that was a failed-session artifact).
"""
import math

import base as sb

from conftest import SEAT_ROT


def _back_wall_window_deg(rot):
    """Assembly-frame angular window [deg] of the mount back-wall slab at rot.
    Fold-local ch_back_wall, minus |ch_ang_rot| (lock_channel), plus rot."""
    a_hi = rot + sb.ch_back_wall + sb.ch_ang_rot
    return a_hi - 0.5, a_hi


def _back_wall_base_hits(base_contains, rot):
    """Count base (lug) sample points inside the back-wall slab's window."""
    a_lo, a_hi = _back_wall_window_deg(rot)
    pts = []
    for r in (50.5, 51.0, 51.5):
        for i in range(3):
            a = math.radians(a_lo + (a_hi - a_lo) * i / 2.0)
            for z in (2.0, 2.7, 3.4):
                pts.append((r * math.cos(a), r * math.sin(a), z))
    return sum(base_contains(pts))


def test_free_travel_at_seat(lug_points, mount_contains):
    assert sum(mount_contains(lug_points, rot=SEAT_ROT)) == 0
    assert sum(mount_contains(lug_points, rot=SEAT_ROT + 1)) == 0


def test_back_wall_stop_free_before_onset(base_contains):
    assert _back_wall_base_hits(base_contains, 10.0) == 0
    assert _back_wall_base_hits(base_contains, 11.0) == 0


def test_back_wall_stop_blocked_after_onset(base_contains):
    assert _back_wall_base_hits(base_contains, 13.0) >= 3
    assert _back_wall_base_hits(base_contains, 14.0) >= 3
