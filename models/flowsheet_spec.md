# P2 — Base Flowsheet Specification & Verification Protocol
**Repo:** `ipis-thesis-pyrolysis-epr` · **Idea:** W1/A · **Phase:** P2 (base pyrolysis+distillation flowsheet, verified)
**Decisions locked (this session):** yield-shift reactor · kinetics from Locaspi 2023 + Westerhout 1997 · verify vs Genuino 2023.
**Deliverable target (prospectus §11):** verified base model + verification note. This file is the build spec + the verification note skeleton.

---

## 1. Reactor strategy — yield-shift (locked)

DWSIM has no native polymer-pyrolysis reactor. The reactor is a **yield-shift block**: `src/lumped_kinetics.py` computes product-lump yields = f(feed composition, T, τ); DWSIM applies the yield vector via a **Python Script unit operation** (snippet in the module). DWSIM owns thermo + fractionation; Python owns the reaction.

**Parameter sources (real, extracted from the project PDFs):** the yield split comes from the **Genuino et al. (2023) linear superposition model** — measured single-component yields at 500 °C, `yield_j(x)=Σ xᵢ·Yᵢⱼ` — over lumps **{GAS, OIL_WAX, SOLID}**. Devolatilization **conversion X(T,τ)** and reactor **sizing** come from **Westerhout et al. (1997) Table 4** first-order kinetics (k₀, Eₐ per resin) with a linear mixing rule. No fabricated parameters.

Rejected alternatives, for the record: **Conversion reactor** needs fixed stoichiometric lump reactions with conversions relinked per operating point — clumsier for a composition-and-T-dependent yield surface. **Gibbs/equilibrium** is wrong for pyrolysis — pyrolysis is a **kinetically controlled**, non-equilibrium devolatilization; a Gibbs reactor would drive to thermodynamic equilibrium (mostly light gas + coke) and destroy the oil/wax slate the thesis depends on. Do not use it.

This external-reaction seam is deliberate: it is the same interface the **P4 surrogate** replaces (surrogate emulates `pyrolysis_yields()` at network scale). P2 and P4 share the boundary.

## 2. Property package — Peng–Robinson (PR)

**Rationale (numbers-first):** the fractionation feed is a non-polar hydrocarbon mixture spanning C1–C40+ (paraffins, olefins, aromatics) over a wide boiling range (gas → wax, ~−160 °C to >350 °C NBP). PR is the refinery-standard cubic EOS for this class: reliable VLE for light-to-heavy hydrocarbons, handles supercritical light gases in the liquid, and pairs natively with petroleum-pseudocomponent characterization. NRTL/UNIQUAC (activity-coefficient models) are for polar/non-ideal liquid mixtures — not needed here and weaker on the light-gas end.
- **Caveat to flag in the write-up:** PS-derived oil is aromatic-rich (styrene, toluene, ethylbenzene). If aromatics dominate a case, spot-check PR against a PR-with-modified-mixing-rules or SRK run; report any Δ in cut split.

## 3. Compound / pseudocomponent set

**Two-level structure (important):** the *reactor* produces **3 lumps** (Genuino basis); the *fractionation train* splits OIL_WAX into fuel cuts.

| Reactor lump (from `lumped_kinetics`) | → downstream | DWSIM representation | Boiling range (1 atm) |
|---|---|---|---|
| GAS | fuel gas | real compounds: H2, CH4, C2H4, C2H6, C3H6, C3H8, C4s | < 30 °C |
| OIL_WAX | **fractionate →** NAPHTHA / MIDDLE / WAX | petroleum pseudocomponents | 30 → >350 °C |
| SOLID | char/residue out | inert solid | split off pre-fractionation |

The NAPHTHA (~30–200 °C, C5–C12) / MIDDLE (~200–350 °C, C13–C20) / WAX (>350 °C, C21+) split is set by the **OIL_WAX boiling curve**, applied in the fractionation column — **not** by the reactor. Genuino gives OIL_WAX *composition* (aliphatic/aromatic C by ¹³C NMR) but not a boiling-point distribution; the cut split needs a boiling curve from Genuino's SI (GC-SimDist) or a literature analogue. **Flag:** this is the one remaining data gap for the *fuel-cut* yields (not the reactor yields, which are verified). Char/SOLID is excluded from PR VLE.

## 4. Feed handling

The plastic feed carries no meaningful VLE (solid polymer). Represent it as a **mass-flow basis** (kg/s over the FEED_LUMPS composition vector); the yield-shift UO consumes it and emits the product-compound stream. No rigorous solid thermo required — the reactor block is the thermodynamic boundary.

## 5. Unit sequence (base flowsheet)

```
 Plastic feed (mass basis, comp vector)
        │
        ▼
 [Yield-shift reactor]  ── Python Script UO, T setpoint, yields from lumped_kinetics
        │  (product vapor + char)
        ▼
 [Char separator]  ── solid/inert split  ──►  CHAR out
        │  (product vapor)
        ▼
 [Quench / condenser]  ── cool to condense oil
        │
        ▼
 [Gas–liquid flash]  ── noncondensables ──►  GAS out (fuel gas)
        │  (condensed oil)
        ▼
 [Fractionation column]  ── atmospheric, side draws
        ├──► NAPHTHA
        ├──► MIDDLE (diesel-range)
        └──► WAX (bottoms; recycle-to-reactor optional, P4 lever)
```
Base model = **one** atmospheric fractionation column with side draws (keep it minimal for verification). Column complexity (second column, wax recycle) is a P4 design lever, not P2.

## 6. Verification protocol — quantitative acceptance criteria

The base model is "verified" only if **all** pass. Record actuals in the verification note.

| # | Check | Acceptance criterion | Source |
|---|---|---|---|
| V1 | Overall mass balance | closure error ≤ **0.1 %** (converged sim) | first principles |
| V2 | Elemental C/H balance | ≤ **1 %** each | first principles |
| V3 | Reactor yield vs Genuino 2023 | **✅ PASS** — `verify_vs_genuino.py`: worst error **4.6 pp** < 5 pp tol over {GAS, OIL_WAX, SOLID} on both virgin mixtures (20% & 45% PET). Reproduces the documented PET>33% breakdown | `genuino2023predicting` |
| V4 | Reactor endotherm | duty in **0.5–1.5 MJ/kg** plastic band (order-of-magnitude sanity) — flag if outside | Sharuddin/Papari (general) |
| V5 | Column convergence | converges; cut recoveries physically reasonable (no negative flows, monotone cut NBPs) | first principles |
| V6 | Yield-table closure | ✅ met — closure error **0.00** (exact) | first principles |

**V3/V4 now grounded in Genuino Table 1** (real, extracted): single-resin oil/wax yields at 500 °C — HDPE 94, LDPE 96, PP 96, PS 94, **PET 54** (32 solid); DKR categories — **multilayer 46, clogged 54** (high solid, the PH-relevant contaminated fraction). Reactor sizing (Westerhout): τ for X=0.99 at 500 °C ≈ **177 s** (intrinsic kinetics; drops to ~22 s at 550 °C — Arrhenius), which sets reactor volume/CAPEX in the TEA.

## 7. Status — reactor model verified; two items remain

**Resolved (this session):** Genuino 2023 + Westerhout 1997 extracted from project PDFs → `KINETIC_SCHEME` replaced with real params → V3 PASS (4.6 pp) → `verify_vs_genuino.py` built → yield table regenerated. **The reactor yield model is verified.**

**Remaining (2 items, neither blocks the DWSIM structural build):**
1. **OIL_WAX boiling curve** → to split OIL_WAX into NAPHTHA/MIDDLE/WAX fuel cuts (§3). Needs Genuino SI GC-SimDist or a literature boiling distribution. Until then, fuel-*cut* yields are unset (reactor lump yields are verified).
2. **Off-500 °C yield surface** → Genuino is single-T. If the network optimizer varies reactor T, a T-dependent yield DOE is needed (P3). At the 500 °C design point, none required.

**Third project PDF** (`...S0165237023...`) is a *different* Locaspi paper — a 400-reaction detailed PS mechanism (J. Anal. Appl. Pyrolysis), not the PE/PP lumped scheme. Not needed for the yield-shift model; retain as a reference for PS-pathway detail if a reviewer probes styrene selectivity.

