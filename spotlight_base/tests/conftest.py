"""Shared fixtures for the spotlight_base verification suite.

Single reference frame: ASSEMBLY frame — base plate at z 2..6, mount origin
at z = mount_offset_z (=-10.5). Tests never compute offsets themselves; they
use base_contains / mount_contains only.

Containment is exact OCC B-Rep classification (BRepClass3d_SolidClassifier)
against the cached fused solids — the only tool proven correct on this
model's double-walled tessellation (see docs/plans/verification-handoff.md).
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import base as sb  # noqa: E402

from OCP.BRep import BRep_Builder  # noqa: E402
from OCP.BRepClass3d import BRepClass3d_SolidClassifier  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.BRepTools import BRepTools  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.TopAbs import TopAbs_IN, TopAbs_ON, TopAbs_SOLID  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopoDS import TopoDS, TopoDS_Shape  # noqa: E402

_SPOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(_SPOT_DIR, ".cache")
BASE_CACHE = os.path.join(CACHE_DIR, "base_fused.brep")
MOUNT_CACHE = os.path.join(CACHE_DIR, "mount_fused.brep")

SEAT_ROT = -sb.ch_ang_rot  # 10 deg — mount rotation at the seated pose
MOUNT_Z = sb.mount_offset_z  # -10.5


def asm_to_base(x, y, z):
    """Assembly-frame point -> base-native (base sits at z 2..6 in assembly)."""
    return (x, y, z - 2.0)


def asm_to_mount(x, y, z, rot, z_off):
    """Assembly-frame point -> mount-native for a mount at rotation `rot`
    about Z and vertical offset `z_off` from its seated origin
    (z_off < 0 = pulled down, away from the ceiling)."""
    a = math.radians(-rot)
    z_m = z - (MOUNT_Z + z_off)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z_m)


def _load_solids(path):
    shp = TopoDS_Shape()
    comp = TopoDS.Compound(shp)
    bb = BRep_Builder()
    bb.MakeCompound(comp)
    BRepTools.Read_s(comp, path, bb)
    exp = TopExp_Explorer(comp, TopAbs_SOLID)
    out = []
    while exp.More():
        out.append(exp.Current())
        exp.Next()
    return out


def _solid_volume_cm3(s):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(s, props)
    return props.Mass() / 1000.0


class Probe:
    """Exact point-in-part classification via OCC B-Rep on fused solids."""

    def __init__(self, solids):
        self.clf = [BRepClass3d_SolidClassifier(s) for s in solids]

    def contains(self, pts):
        from OCP.gp import gp_Pnt

        res = []
        for x, y, z in pts:
            p = gp_Pnt(float(x), float(y), float(z))
            hit = False
            for c in self.clf:
                c.Perform(p, 1e-3)
                if c.State() in (TopAbs_IN, TopAbs_ON):
                    hit = True
                    break
            res.append(hit)
        return res


@pytest.fixture(scope="session")
def base_probe():
    solids = _load_solids(BASE_CACHE)
    assert len(solids) == 1, "base_fused.brep should be one fused solid"
    v = _solid_volume_cm3(solids[0])
    assert 39.5 < v < 41.5, (
        f"base cache volume {v:.2f} cm3 out of range (expect ~40.4). "
        "The cache is stale or the model changed; regenerate it."
    )
    return Probe(solids)


@pytest.fixture(scope="session")
def mount_probe():
    solids = _load_solids(MOUNT_CACHE)
    assert len(solids) == 4, "mount_fused.brep should be cap + 3 channel solids"
    v = sum(_solid_volume_cm3(s) for s in solids)
    assert 41.0 < v < 43.5, (
        f"mount cache volume {v:.2f} cm3 out of range (expect ~42.1). "
        "The cache is stale or the model changed; regenerate it."
    )
    return Probe(solids)


@pytest.fixture(scope="session")
def base_contains(base_probe):
    def f(pts):
        return base_probe.contains([asm_to_base(*p) for p in pts])

    return f


@pytest.fixture(scope="session")
def mount_contains(mount_probe):
    def f(pts, rot=SEAT_ROT, z_off=0.0):
        return mount_probe.contains([asm_to_mount(x, y, z, rot, z_off) for x, y, z in pts])

    return f


def grid(r_lo, r_hi, n_r, ang_lo, ang_hi, n_ang, z_lo, z_hi, n_z):
    """Fixed cylindrical point grid in the assembly frame (no RNG)."""
    pts = []
    for i in range(n_r):
        r = r_lo + (r_hi - r_lo) * i / (n_r - 1)
        for j in range(n_ang):
            a = math.radians(ang_lo + (ang_hi - ang_lo) * j / (n_ang - 1))
            for k in range(n_z):
                z = z_lo + (z_hi - z_lo) * k / (n_z - 1)
                pts.append((r * math.cos(a), r * math.sin(a), z))
    return pts


def tab_grid(n_rad=5, n_ang=9, n_z=6):
    """Assembly-frame grid covering the +X lock tab (r band, angular span,
    vertical band). Size is bounded: 5*9*6 = 270 pts max."""
    r_lo, r_hi = sb.tab_root_r - 0.3, sb.tab_tip_r + 0.2
    z_lo, z_hi = 2.0, 2.0 + sb.lock_height
    return grid(r_lo, r_hi, n_rad, -6.0, 6.0, n_ang, z_lo, z_hi, n_z)


@pytest.fixture(scope="session")
def tab_points(base_contains):
    """Tab sample points in the assembly frame that are confirmed inside the
    base (so a mount collision means genuine contact)."""
    pts = tab_grid()
    in_base = base_contains(pts)
    return [p for p, hit in zip(pts, in_base) if hit]
