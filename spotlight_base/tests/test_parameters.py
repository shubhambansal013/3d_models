"""Tier 1: pure-arithmetic parameter invariants. No CAD built, sub-ms.

Expected values are derived from base.py parameters only (params are the
spec) — never from eyeballed output.
"""
import base as sb


def test_screw_chord_matches_real_spacing():
    assert abs(2 * sb.screw_hole_radius - 78.0) < 0.01


def test_tab_tip_radius_derivation():
    # Real chain in base.py: bend_r = plate_radius + 1, root = bend_r - 1.25,
    # tip = root + lock_protrusion  (= plate_radius - 0.25 + lock_protrusion).
    assert abs(sb.tab_bend_r - (sb.plate_radius + 1.0)) < 1e-9
    assert abs(sb.tab_root_r - (sb.tab_bend_r - 1.25)) < 1e-9
    assert abs(sb.tab_tip_r - (sb.tab_root_r + sb.lock_protrusion)) < 1e-9
    assert abs(sb.tab_tip_r - (sb.plate_radius - 0.25 + sb.lock_protrusion)) < 1e-9


def test_roof_inner_radius_derivation():
    assert abs(sb.ch_roof_in - (sb.tab_tip_r - sb.roof_capture)) < 1e-9


def test_wall_inner_radius_derivation():
    assert abs(sb.ch_wall_in - (sb.tab_tip_r + sb.ch_clear)) < 1e-9


def test_roof_thickness_meets_min_wall():
    assert sb.ch_block_top - sb.ch_groove_top >= 0.8


def test_groove_height_at_least_lock_gap():
    assert sb.ch_groove_top - sb.ch_groove_bot >= sb.lock_gap_height


def test_cap_hides_base():
    assert sb.cap_radius - sb.plate_radius >= 3.0


def test_assembly_z_invariant():
    assert abs((sb.mount_offset_z + sb.cap_disc_h + sb.cap_skirt_h)
               - (2 + sb.plate_thickness)) < 1e-9


def test_back_wall_band_overlaps_tab_band():
    bw_bot = sb.ch_groove_bot + sb.mount_offset_z
    bw_top = sb.ch_groove_top + sb.mount_offset_z
    tab_bot = 2.0
    tab_top = 2.0 + sb.lock_height
    overlap = min(bw_top, tab_top) - max(bw_bot, tab_bot)
    assert overlap > 0
