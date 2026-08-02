# Verification Handoff — Twist-Lock Fit/Strength Check (NEW SESSION)

> Written 2026-08-02. Goal of the NEXT session: fix the lock-fit verification.
> **Do NOT re-derive anything from scratch — read this first, then follow the
> test plan in `verification-test-plan.md`** (pytest suite structure, exact
> assertions, anti-iteration rules). The CAD model itself is considered DONE and
> looks fine on manual inspection. Only the verification tooling is unproven.

---

## 1. What is DONE (do not redo)

- `spotlight_base/base.py` — CadQuery migration + real-measurement retrofit is
  complete and builds clean:
  - Ø150 base plate (`plate_radius 75`), M4 screws at `screw_hole_radius 39`
    (chord 78.0 ✓), cap Ø156 (`cap_radius 78`), central wire hole Ø50 kept.
  - `lock_protrusion = 1.5`; lock radii are now **derived** from the tab
    (`tab_tip_r = plate_radius + 0.25 + lock_protrusion = 76.25`,
    `ch_roof_in = tab_tip_r - roof_capture(0.6) = 75.65`,
    `ch_wall_in = tab_tip_r + ch_clear(0.2) = 76.45`). Roof thickness 1.0 mm.
  - Volumes: base 40.4 cm³, mount 42.1 cm³, assembled 82.6 cm³ (lightened
    2026-08-02: widened base pocket r28→66, added cup-side disc pocket r8–68;
    down from 56.7 / 55.0 / 111.7).
- Cached fused solids (single booleans for fast probing):
  - `spotlight_base/.cache/base_fused.brep` — base fused to **1 solid**, 74.6 s,
    valid, vol 56.7 cm³.
  - `spotlight_base/.cache/mount_fused.brep` — mount stays **4 solids** (cap +
    3 channels share faces only; OCC won't merge coincident-face solids),
    valid, vol 55.0 cm³.
- `spotlight_base/lock_check.py` — FIRST-DRAFT harness. **Treat as broken; rewrite
  in the new session, don't patch.** It carries the frame bug + an untrustworthy
  mesh fallback.

## 2. The task (what verification must produce)

Twist-lock fit/tolerance check that the lock holds a **100 g light**:
1. At seat: no collision (tab clears the channel), sensible clearance numbers.
2. Rotation stop: tab hits the channel back-wall at the expected ~+18° (from seat)
   — check `rot` sweep 10→25.
3. Pullout: tab tip is blocked by the roof overhang when the mount is pulled off —
   check mount **drop** (down, away from ceiling) 0→2 mm.
4. Strength: purely analytic, already known fine (FoS ~100–400× at 1 N) — non-issue.

## 3. THE KEY BUG THAT WASTED THE SESSION (fix first in new session)

**Reference-frame confusion.** Two frames exist and I mixed them repeatedly:

- ASSEMBLY frame (what `build("assembled")` uses): base plate at z **2..6**
  (tab crest ≈ **4.40**), mount at `mount_offset_z = −10.5` → roof at z **3.5..4.5**.
- BASE-NATIVE frame (what `base_plate()` produces at z 0..4): tab crest ≈ **2.40**.
  The mount must then be placed at **`mount_offset_z − 2 = −12.5`** → roof at
  z **1.5..2.5**, groove floor 1.8, wall band 1.8..3.0.

My `seated()` used `mount_offset_z − 2` but my *validation expectations* and the
tabular z-choices were computed in the wrong frame half the time → chased ghosts.
In the new session: pick ONE frame (assembly is clearest), convert every number
once, and sanity-check on 3–5 points before sweeping.

**Open question to confirm before trusting anything:** in assembly frame, tab
crest (4.40) vs roof bottom (3.5) suggests the tab tip sits ~0.9 mm *into* the
roof at seat. Manual inspection says the part looks fine, so either my z math is
still off or there is real marginal interference — confirm with ONE exact
cross-check (render a cutaway at the tab, or OCC distance), then decide.

## 4. Measurement results from the failed session (ground truth, keep)

From a boundary scan at r=76, seat rot=10, base-native frame (mount at −12.5):
- Roof material (mount) occupies z **1.6..2.4**, angles **0..4°**, at r=76.
- At drop 1.0 (pullout): roof material shifts to z **0.6..1.4** → it DOES move
  down over the tab → pullout blocking is real.
- Tab crest measured = **2.40** (base-native), tab tip r = 76.25, tab angular
  center ≈ **5.6°** off +X (spans roughly 2.6–8.6°).

These came from the OCC classifier and agree with the geometry — keep them as the
baseline for the new session's checks.

## 5. Library survey — what works and what does NOT (all tested this session)

The model tessellates into **non-manifold / double-walled meshes** (touching
slices in `cylindric_bend`, fused coincident faces in `rim_channel`). Verified:
- **trimesh.contains** — FAILS. Wrong parity on non-watertight mesh (5/15 wrong).
- **trimesh weld** (`merge_vertices` + `unique_faces`) — base becomes watertight
  with exact volume 56.7, but parity STILL wrong (4/11) — opposite-wound
  double-walls survive. euler 140 exposes internal structure.
- **manifold3d 3.5.2** — FAILS. Strict importer rejects non-manifold input
  (`status() == NotManifold`, 0 triangles).
- **pymeshfix 0.18** (`PyTMesh().clean(10,3)`) — FAILS. Collapses thin-feature
  mesh to 116 verts / 0 vol.
- **OCP `BRepClass3d_SolidClassifier`** — WORKS. Exact point-in-solid via the
  B-rep kernel (battle-tested; it's what CadQuery itself is built on). Correct on
  every test point. Cost ~2.4 ms/pt → **use sparse sampling** (never brute-force
  grids; a 27 k-pt sweep hung the shell). Requires fused single solids (cached).

## 6. Recommended approach for the new session (in order)

1. **Rewrite the probe** around `BRepClass3d_SolidClassifier` (correct 3-arg API,
   see §7). Load the two cached `.brep` files (0.1 s). Build per-solid classifiers,
   bbox-prefilter, OR the solids.
2. Pick the **assembly frame**, hard-code the frame math in ONE place.
3. Validate the probe on ~20 known in/out points per part **before** sweeping.
4. Sweep (sparse, ≤500 total classifier calls per pose):
   - rotation rot = 10..25 step ~2 (expect back-wall contact ~18),
   - pullout drop = 0..2 step 0.5 at rot=10 (expect roof contact by ~1.0).
5. Only if mesh-based tools are still wanted: **fix the model's tessellation at
   the source** (build the tab as one revolve/loft, and `rim_channel` without
   fused coincident faces) so trimesh becomes reliable — this also kills the
   known "non-manifold edges" CGAL artifact. Bigger change; not required.
6. When sweeps pass, write results + PASS/FAIL into
   `docs/plans/verification-handoff.md` (or a phase file) and update AGENTS.md.

## 7. OCP API gotchas (verified this session — saves time)

- `BRepClass3d_SolidClassifier` ctor: `(S: TopoDS_Shape)` **or** `(S, gp_Pnt, Tol)`
  — there is **no 2-arg form**.
- `.Perform(pnt, tol)` — **requires the tolerance arg too** (no 1-arg form).
- `State()` returns `TopAbs_IN/OUT/ON`; treat IN **and** ON as occupied.
- Read cache: `BRepTools.Read_s(comp, path, bb)` needs a `TopoDS_Compound`
  target + `BRep_Builder`. Write: `BRepTools.Write_s(comp, path)`.
- `mount_plate()` returns a **Compound of 4 solids**, `base_plate()` a Compound
  of 73 — always iterate `.Solids()`.
- OCC booleans on the 73-solid base compound are unreliable (silently empty
  intersect results) — this is WHY point-classification is used instead.
- Shell commands time out ~115 s. Fusing the base takes ~75 s — always load from
  the cached `.brep`, never re-fuse in a long script.

## 8. Environment

- Python env: `source /home/ubuntu/workspace/.venv/bin/activate`
  (cadquery 2.8.0, pytest 9.1.1, mcp, numpy). trimesh/pymeshfix/manifold3d
  uninstalled 2026-08-02 (never trusted — see §5).
- System `/usr/bin/python3` has trimesh 4.12.2 but **NO cadquery** — always the venv.
- Cached solids: `spotlight_base/.cache/base_fused.brep`, `mount_fused.brep`.
- Renders: `xvfb-run -a openscad ...` is for the OLD OpenSCAD file; for CadQuery
  use `python -c "from base import *; from ocp_vscode import show; show(...)"`
  (headless-friendly) or export STL/STEP to `/mnt/user-data/outputs/`.

---

## 9. RESULT — verification rebuilt as pytest (2026-08-02)

`spotlight_base/lock_check.py` deleted. New suite at `spotlight_base/tests/`
(plan: `docs/plans/verification-fix/PLAN.md`):

```
python -m pytest spotlight_base/tests -q      # 22 passed in ~8 s (budget < 60 s)
```

| Test file | Tier | Verdict |
|---|---|---|
| `test_parameters.py` | 1 (params) | PASS — 9/9 |
| `test_classifier.py` | 2 (oracle) | PASS — 2/2, ~40 points |
| `test_seat_fit.py` | 3 (seat) | PASS — incl. the interference question |
| `test_rotation.py` | 3 (stop) | PASS |
| `test_pullout.py` | 3 (roof) | PASS |
| `test_strength.py` | 3 (FoS) | PASS — FoS > 100 @ 1 N |

### Golden numbers REVISED (kernel-measured; handoff §4/§3.4 numbers were wrong)

| Quantity | old (handoff) | new (measured 2026-08-02) |
|---|---|---|
| Tab angular center | ≈ 5.6° | **0°** (tabs on fold axes) |
| Tab tip r | 76.25 (formula) | **≈ 76.0** actual geometry |
| Tab crest (base) | 2.40 "at tip" | 2.40 only at **root r≤75**; lip crest ≈ 1.0–1.4 |
| Back-wall stop onset | ≈ 18° (from seat 10°) | **rot ≈ 12** (seat 10 → only ~2° travel) |
| Pullout catch onset | ≈ 0.9 mm | **0.3–0.5 mm** drop |
| Seat interference | "0.9 mm into roof" open Q | **NO interference**: lip crest 3.0–3.4 (asm) < roof bottom 3.5; ~0.3–0.5 mm clearance |

### Decisions confirmed this session
- **Central boss is absent by design** (user confirmed). The Ø9.5 boss
  references in old docs/AGENTS are stale; mount spotlights onto the flat
  disc + Ø2.9 pilot. Oracle expectations updated to match.
- `test_rotation` probes the back-wall band **analytically** (moving ~0.5°
  window), not by densifying the coarse tab grid — per plan rule 5.
- Oracle `test_classifier` expectations came from params + assembly frame,
  validated once against the kernel, then frozen as regression guards.

### Remaining (parked)
- MCP server + `opencode.jsonc`, `.cache` gitignore/commit decision.
- `verification-test-plan.md` still lists the old golden numbers (§4) and
  rotation expectations (§3.4) — update them to the REVISED table above.
