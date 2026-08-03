"""Tier 1: pure-arithmetic parameter invariants. No CAD built, sub-ms.

Expected values are derived from base.py parameters only (params are the
spec) — never from eyeballed output.
"""
import base as sb


def test_screw_chord_matches_real_spacing():
    assert abs(2 * sb.screw_hole_radius - 78.0) < 0.01


def test_lug_tip_radius_derivation():
    assert abs(sb.lug_tip_r - (sb.plate_radius + sb.lock_protrusion)) < 1e-9


def test_ch_wall_inner_radius_derivation():
    assert abs(sb.ch_wall_in - (sb.lug_tip_r + sb.ch_clear)) < 1e-9


def test_ch_roof_inner_radius_derivation():
    assert abs(sb.ch_roof_in - (sb.lug_tip_r - sb.roof_capture)) < 1e-9


def test_roof_thickness_meets_min_wall():
    assert sb.ch_block_top - sb.ch_groove_top >= 0.8


def test_seat_clearance_minimum():
    # seat clearance = roof bottom (ch_groove_top + mount_offset_z) - lip top (2 + lip_h)
    seat_clear = (sb.ch_groove_top + sb.mount_offset_z) - (2.0 + sb.lip_h)
    assert seat_clear >= 0.6


def test_sliding_clearance_in_sliding_range():
    # the lug tip rides the channel outer wall through the whole twist; 0.2 mm
    # was press/snap and bound under FDM drift (the "hard to attach/detach"
    # bug). Sliding twist locks need 0.3-0.4 mm. Gate it here AND on the mesh
    # (test_twist_fit.py) so a regression fails instantly.
    assert 0.30 <= sb.ch_clear <= 0.50


def test_roof_clearance_in_range():
    # roof bottom clears the lip top by 0.6-1.0 mm: enough to seat/travel, not
    # so much the mount rattles on its roof catch.
    seat_clear = (sb.ch_groove_top + sb.mount_offset_z) - (2.0 + sb.lip_h)
    assert 0.60 <= seat_clear <= 1.00


def test_cap_covers_base():
    assert sb.cap_radius - sb.lug_tip_r >= 1.5


def test_assembly_z_invariant():
    assert abs((sb.mount_offset_z + sb.cap_disc_h + sb.cap_skirt_h)
               - (2 + sb.plate_thickness)) < 1e-9


def test_lock_grip_is_1_5mm():
    # the requested lock grip: the roof overhangs 1.5mm past the lug tip
    assert abs(sb.roof_capture - 1.5) < 1e-9


def test_shelf_outer_band_is_captured():
    # the roof grips the shelf's outer roof_capture band (r ch_roof_in..tip)
    assert abs(sb.lug_tip_r - sb.ch_roof_in - sb.roof_capture) < 1e-9
    assert sb.roof_capture >= 1.0, "grip must stay meaningful"
    assert sb.lug_tip_r - sb.lug_step_r > sb.roof_capture, "shelf must extend past the roof grip"


def test_roof_clears_plate_radius():
    # RADIAL-TRAP GATE: the roof inner radius must stay OUTSIDE the plate radius,
    # else the roof embeds in the plate rim and the mount can never detach (the
    # 3mm-grip regression). Keeps >= 0.3mm radial clearance to the plate rim.
    assert sb.ch_roof_in > sb.plate_radius + 0.3


def test_relief_clears_roof():
    # plate top-rim relief inner radius stays inside the roof inner radius
    assert sb.relief_in < sb.ch_roof_in - 1e-9


def test_back_wall_band_overlaps_lug_band():
    bw_bot = sb.ch_groove_bot + sb.mount_offset_z
    bw_top = sb.ch_groove_top + sb.mount_offset_z
    lug_bot = 2.0
    lug_top = 2.0 + sb.lip_h
    overlap = min(bw_top, lug_top) - max(bw_bot, lug_bot)
    assert overlap > 0
