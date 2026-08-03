"""Regenerate the cached fused solids the test suite probes.

Run after any geometry-affecting change to base.py:

    source /home/ubuntu/workspace/.venv/bin/activate
    python spotlight_base/scripts/rebuild_cache.py
    python -m pytest spotlight_base/tests -q

The contract (enforced by tests/conftest.py):
  - .cache/base_fused.brep  -> 1 solid,  ~14.6 cm3
  - .cache/mount_fused.brep -> 1 solid, ~18.0 cm3
"""
import os
import sys

SPOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(SPOT_DIR, ".cache")
sys.path.insert(0, SPOT_DIR)

import base as sb  # noqa: E402

from OCP.BRepTools import BRepTools  # noqa: E402


def _write(solid, path):
    os.makedirs(CACHE_DIR, exist_ok=True)
    BRepTools.Write_s(solid.wrapped, path)
    print(f"  {path}: {sum(s.Volume() for s in solid.Solids())/1000.0:.2f} cm3, "
          f"{len(solid.Solids())} solid(s)")


def main():
    print("Base plate: single fused solid (monolithic lugs, no slices) ...")
    _write(sb.base_plate(), os.path.join(CACHE_DIR, "base_fused.brep"))

    print("Mount plate: single fused solid (channels buried ch_bury into the wall ring) ...")
    _write(sb.mount_plate(), os.path.join(CACHE_DIR, "mount_fused.brep"))


if __name__ == "__main__":
    main()
