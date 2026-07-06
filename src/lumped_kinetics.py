"""
lumped_kinetics.py  --  P2 pyrolysis yield-shift reactor engine  (v2, REAL params)
==================================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

MODEL (grounded in the two project PDFs; no fabricated parameters)
------------------------------------------------------------------
Product lumps = {GAS, OIL_WAX, SOLID}  <- Genuino et al. (2023) lump structure.
  * YIELD engine  = Genuino linear SUPERPOSITION model, validated to <=8 pp:
        yield_j(x) = sum_i x_i * Y_ij      [Genuino 2023, Waste Manag 156:208-215, Table 1]
    Y_ij = measured single-component yields at 500 C (batch, 60 min, complete conversion).
    Documented breakdown: PET > 33 wt% -> superposition OVER-predicts oil/wax (up to 8 pp)
    and UNDER-predicts solid (up to 16 pp) due to PET-polyolefin interaction. Flagged.
  * CONVERSION engine = Westerhout et al. (1997) IECR 36:1955, Table 4 (first-order,
    70-90% conv). Gives X(T,tau) per polymer + linear mixing rule (Westerhout Sec. 5.4).
    Used for reactor SIZING (tau for X>=0.99) and to flag operation off the 500 C basis.

SCOPE / LIMITATION (state in the thesis, do not bury):
  Genuino yields are 500 C-specific. This is a DESIGN-POINT yield model. Off-500 C yield
  extrapolation is NOT supported by these data; a T-dependent yield surface is a P3 DOE task.
  The GAS/OIL_WAX/SOLID lumps are NOT the fuel cuts; splitting OIL_WAX into naphtha/middle/
  wax is a DWSIM fractionation step driven by a boiling curve (oil composition, Genuino SI
  or literature) -- see flowsheet_spec.md. Do not report cut yields from this module.

Dependencies: numpy, scipy, pandas.  Python 3.10+.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

R = 8.314462618  # J/(mol*K)

PRODUCT_LUMPS = ["GAS", "OIL_WAX", "SOLID"]

# ===========================================================================
# GENUINO 2023, Table 1 -- measured single-component yields at 500 C [wt%, RAW].
# Order: (GAS, OIL_WAX, SOLID). Rows normalized to 100% at use (Genuino's own
# treatment). Two libraries: clean virgin resins, and real DKR-350 sorting cats
# (the latter carry the contaminated multilayer/clogged streams relevant to PH).
# ===========================================================================
GENUINO_YIELDS_RAW = {
    # --- virgin polymers ---
    "HDPE": (4, 94, 0),   "LDPE": (4, 96, 0),   "PP": (4, 96, 0),
    "PS":   (2, 94, 4),   "PET":  (9, 54, 32),
    # --- DKR-350 sorting categories (real waste) ---
    "PE_rigid": (4, 91, 0), "PE_film": (5, 80, 0),
    "PP_rigid": (7, 89, 0), "PP_film": (5, 88, 0),
    "PET_cat":  (18, 54, 23), "PS_cat": (5, 81, 8),
    "CLOGGED":  (8, 54, 32), "MULTILAYER": (9, 46, 39),
}

def _norm_yields(raw: tuple[float, float, float]) -> dict[str, float]:
    s = sum(raw) or 1.0
    return {lump: 100.0 * v / s for lump, v in zip(PRODUCT_LUMPS, raw)}

GENUINO_YIELDS = {k: _norm_yields(v) for k, v in GENUINO_YIELDS_RAW.items()}

# ===========================================================================
# WESTERHOUT 1997, Table 4 -- fitted first-order kinetics (70-90% conv):
# (k0 [1/s], Eact [J/mol]).  PE and PP have HDPE/LDPE and PP1/PP2 variants;
# k0-Eact are strongly correlated (small TGA window) so k(T) is the robust
# quantity, not k0/Eact individually (Westerhout Sec. 5.2).
# ===========================================================================
WESTERHOUT_KINETICS = {
    "HDPE":  (1.9e13, 220e3), "LDPE1": (1.0e15, 241e3), "LDPE2": (9.8e11, 201e3),
    "PP1":   (3.2e15, 244e3), "PP2":   (2.2e11, 188e3), "PS":    (3.3e13, 204e3),
}
# representative rate per resin class used in mixing (documented choice):
_RESIN_KINETICS = {"PE": WESTERHOUT_KINETICS["HDPE"],   # HDPE as PE representative
                   "PP": WESTERHOUT_KINETICS["PP2"],    # PP2 (lower-Ea branch)
                   "PS": WESTERHOUT_KINETICS["PS"]}
# map yield components -> kinetic resin class for the conversion/sizing calc:
_COMP_TO_RESIN = {"HDPE": "PE", "LDPE": "PE", "PE_rigid": "PE", "PE_film": "PE",
                  "PP": "PP", "PP_rigid": "PP", "PP_film": "PP",
                  "PS": "PS", "PS_cat": "PS",
                  "PET": "PP", "PET_cat": "PP",          # PET kinetics ~polyolefin order (approx; flagged)
                  "CLOGGED": "PE", "MULTILAYER": "PE"}   # polyolefin-dominated cats


# ---------------------------------------------------------------------------
# YIELD MODEL  (Genuino superposition) -- the product split fed to DWSIM
# ---------------------------------------------------------------------------
def superposition_yields(composition: dict[str, float],
                         pet_correction: bool = False) -> dict[str, float]:
    """
    Product-lump yields [wt%] via Genuino linear superposition.
    composition : mass fractions over GENUINO_YIELDS keys (need not sum to 1).
    pet_correction : apply documented PET>33wt% empirical shift (oil->solid).
    """
    tot = sum(composition.values()) or 1.0
    x = {k: v / tot for k, v in composition.items()}
    unknown = set(x) - set(GENUINO_YIELDS)
    if unknown:
        raise KeyError(f"no Genuino yields for: {unknown}. Use keys {list(GENUINO_YIELDS)}")

    y = {lump: sum(x[k] * GENUINO_YIELDS[k][lump] for k in x) for lump in PRODUCT_LUMPS}

    # PET-interaction correction (Genuino Fig.3/Fig.5): above 33 wt% PET, each extra
    # wt% PET shifts ~ oil/wax -> solid. Linear approx anchored on the 45 wt% case
    # (oil/wax -8 pp, solid +16 pp vs superposition at ~ +25 pp PET over threshold).
    pet = sum(x.get(k, 0) for k in ("PET", "PET_cat")) * 100.0
    if pet_correction and pet > 33.0:
        over = pet - 33.0
        shift_solid = min(16.0, 16.0 * over / 12.0)     # cap at observed +16 pp
        shift_oil = min(8.0, 8.0 * over / 12.0)
        y["OIL_WAX"] -= shift_oil
        y["SOLID"] += shift_solid
    return y


# ---------------------------------------------------------------------------
# CONVERSION MODEL  (Westerhout) -- reactor sizing + off-500C flag
# ---------------------------------------------------------------------------
def _k(resin: str, T: float) -> float:
    k0, Ea = _RESIN_KINETICS[resin]
    return k0 * np.exp(-Ea / (R * T))

def conversion(composition: dict[str, float], T_K: float, tau_s: float) -> float:
    """
    Mixture devolatilization conversion X in [0,1] at (T,tau).
    First-order per resin (X_i = 1-exp(-k_i*tau)); linear mixing (Westerhout Sec.5.4).
    """
    tot = sum(composition.values()) or 1.0
    X = 0.0
    for comp, m in composition.items():
        resin = _COMP_TO_RESIN[comp]
        Xi = 1.0 - np.exp(-_k(resin, T_K) * tau_s)
        X += (m / tot) * Xi
    return float(X)

def tau_for_conversion(composition: dict[str, float], T_K: float, X_target: float = 0.99) -> float:
    """Residence time [s] to reach X_target at T (slowest-resin bound; for sizing/CAPEX)."""
    tot = sum(composition.values()) or 1.0
    resins = {_COMP_TO_RESIN[c] for c in composition}
    kmin = min(_k(r, T_K) for r in resins)
    return float(-np.log(1.0 - X_target) / kmin)


# ---------------------------------------------------------------------------
# COMBINED reactor outlet  -- yields fed to the DWSIM yield-shift block
# ---------------------------------------------------------------------------
def pyrolysis_yields(composition: dict[str, float], T_K: float = 773.15,
                     tau_s: float | None = None, pet_correction: bool = False,
                     scale_by_conversion: bool = True) -> dict[str, float]:
    """
    Product-lump yields [wt%] at the reactor outlet.
    Genuino superposition gives the split at complete conversion (500 C basis).
    If tau given and scale_by_conversion, unconverted polymer is reported separately
    (converted fraction splits per Genuino). Flags operation far from 500 C.
    """
    y = superposition_yields(composition, pet_correction=pet_correction)
    out = dict(y)
    if tau_s is not None and scale_by_conversion:
        X = conversion(composition, T_K, tau_s)
        out = {lump: v * X for lump, v in y.items()}
        out["UNCONVERTED"] = 100.0 * (1.0 - X)
    if abs(T_K - 773.15) > 30:   # >30 K off the 500 C Genuino basis
        out["_WARN"] = f"T={T_K-273.15:.0f}C off 500C basis; yields extrapolated (unsupported by Genuino data)"
    return out


# ---------------------------------------------------------------------------
# YIELD TABLE  -- DOE grid feeding DWSIM + the P4 surrogate
# ---------------------------------------------------------------------------
def build_yield_table(compositions: list[dict[str, float]],
                      T_grid: list[float], tau_grid: list[float],
                      pet_correction: bool = False) -> pd.DataFrame:
    keys = sorted({k for c in compositions for k in c})
    rows = []
    for comp in compositions:
        for T in T_grid:
            for tau in tau_grid:
                y = pyrolysis_yields(comp, T, tau, pet_correction=pet_correction)
                row = {f"x_{k}": comp.get(k, 0.0) for k in keys}
                row |= {"T_K": T, "tau_s": tau, "X": conversion(comp, T, tau)}
                row |= {f"y_{p}": y.get(p, 0.0) for p in PRODUCT_LUMPS}
                row["y_unconv"] = y.get("UNCONVERTED", 0.0)
                row["closure"] = sum(y.get(p, 0.0) for p in PRODUCT_LUMPS) + y.get("UNCONVERTED", 0.0)
                rows.append(row)
    return pd.DataFrame(rows)


DWSIM_SCRIPT_UO = r'''
# DWSIM Python Script UO -- yield-shift reactor (3-lump Genuino basis)
# ims=inlet MaterialStream, oms=outlet. yields[] from build_yield_table() for this block.
# Map: GAS -> light-gas compounds; OIL_WAX -> petroleum pseudocomponent(s) [split into
# naphtha/middle/wax by the downstream fractionation boiling curve, NOT here];
# SOLID -> inert/char outlet (split off pre-fractionation).
feed = ims.GetMassFlow()                       # kg/s
yields = {"GAS":0.0,"OIL_WAX":0.0,"SOLID":0.0} # <- fill per block (wt% -> fraction)
oms.SetMassFlow(feed)                          # conserve mass across the block
# assign component mass flows on oms per the compound mapping for this flowsheet.
'''


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("REAL params (Genuino 2023 yields + Westerhout 1997 kinetics).\n")

    # --- single component sanity (matches Genuino Table 1 after normalization) ---
    print("Single-component yields [GAS/OIL_WAX/SOLID wt%] (normalized Genuino Table 1):")
    for c in ["HDPE", "PP", "PS", "PET", "MULTILAYER"]:
        y = superposition_yields({c: 1.0})
        print(f"  {c:11s}: {y['GAS']:5.1f} / {y['OIL_WAX']:5.1f} / {y['SOLID']:5.1f}")

    # --- reactor sizing (Westerhout) at 500 C ---
    feed = {"HDPE": 0.45, "PP": 0.30, "PS": 0.10, "MULTILAYER": 0.15}
    tau99 = tau_for_conversion(feed, 773.15, 0.99)
    print(f"\nReactor sizing @500C: tau for X=0.99 = {tau99:.2f} s (feed {feed})")

    # --- outlet yields at design point ---
    y = pyrolysis_yields(feed, 773.15, tau_s=max(tau99, 2.0))
    print("Outlet yields [wt%]:", {k: round(v, 1) for k, v in y.items() if not k.startswith("_")})

    # --- DOE table ---
    comps = [feed, {"HDPE": 0.6, "PP": 0.2, "PS": 0.1, "PET": 0.1}]
    df = build_yield_table(comps, [748.15, 773.15, 798.15], [2.0, 5.0])
    df.to_csv("yield_table.csv", index=False)
    print(f"\nWrote yield_table.csv ({len(df)} rows). Max closure err: {abs(df['closure']-100).max():.2e}")
