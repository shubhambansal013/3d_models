"""Tier 3, part 4: strength — purely analytic FoS for a 100 g light (~1 N),
no CAD. PLA yield 50 MPa, shear 35 MPa (3d-cad-modelling skill)."""
import base as sb

PLA_YIELD = 50.0
PLA_SHEAR = 35.0
F_100G = 1.0  # N
# conservative catch-section thicknesses (mm), from the probed tab lip
CREST_TIP = 1.0
CREST_ROOT = 1.8


def _stresses():
    per_tab = F_100G / 3.0
    width = sb.lock_width
    lip_arm = sb.tab_tip_r - sb.tab_root_r
    roof_t = sb.ch_block_top - sb.ch_groove_top
    capture = sb.roof_capture
    tau = per_tab / (width * CREST_TIP)
    sigma_lip = per_tab * lip_arm / (width * CREST_ROOT ** 2 / 6.0)
    sigma_roof = per_tab * capture / (width * roof_t ** 2 / 6.0)
    return tau, sigma_lip, sigma_roof


def test_lip_shear_fos():
    tau, _, _ = _stresses()
    assert PLA_SHEAR / tau > 100


def test_lip_bending_fos():
    _, sigma, _ = _stresses()
    assert PLA_YIELD / sigma > 100


def test_roof_bending_fos():
    _, _, sigma = _stresses()
    assert PLA_YIELD / sigma > 100
