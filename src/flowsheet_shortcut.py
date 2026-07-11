"""
flowsheet_shortcut.py  --  P4: Python mirror of the verified DWSIM flowsheet
=============================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

PURPOSE: batch-evaluate the P3 DOE (200 compositions x tau) through the FULL
flowsheet response -- product slate, energy duties, recovery, revenue -- which
DWSIM cannot do 200x by hand. This is the surrogate's training oracle.

CALIBRATION: every duty/loss coefficient is anchored to the ONE verified DWSIM
point (pyrolysis_base_v2.dwxmz, V1=0.0011%): FEED 928 kg/h -> FUELGAS 53.57,
NAPHTHA-S 303.42, DIESEL 362.38, WAX 208.65 kg/h; E1..E5 = 369.78/154.74/
229.76/119.10/112.47 kW. Single-point calibration is a stated limitation;
multi-point DWSIM validation is an optional user-side check (P4 backlog).

NONLINEARITIES CARRIED (the surrogate's actual job):
  N1 Genuino PET-interaction correction (piecewise, >33 wt% PET)  [V, Genuino Fig.3/5]
  N2 V-101 flash coupling: naphtha loss to fuel gas ~ gas make x naphtha share
     (partial-pressure physics, calibrated to the 11.2 kg/h DWSIM loss)
  N3 Oil density = f(aromaticity) -> L/t nonlinear in composition  [GK per-cat densities]
  N4 Conversion X(tau) = sum x_i(1-exp(-k_i tau))  (nonlinear in tau)

Deps: numpy, pandas. Imports lumped_kinetics (verified), feedstock_doe (P3 set).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from lumped_kinetics import superposition_yields, conversion, GENUINO_YIELDS
from feedstock_doe import CATEGORIES, lhs_simplex, TAU_GRID_S, T_BASIS_K

# ---------------------------------------------------------------------------
# BASE-CASE ANCHORS (verified DWSIM v2 run; 928 kg/h to DWSIM of 1000 kg/h feed)
# ---------------------------------------------------------------------------
BASE = dict(feed_dwsim=928.0, oil=882.0, gas=46.0,
            naphtha_in_oil_frac=0.356,           # central split (option 3)
            flash_naphtha_loss=11.2,             # kg/h naphtha into V-101 gas
            stab_lights_loss=2.46,               # kg/h stabilizer overhead
            E1=369.78, E2=154.74, E3=229.76, E4=119.10, E5=112.47)  # kW

CUT_SPLIT = {"NAPHTHA": 0.356, "MIDDLE": 0.406, "WAX": 0.238}       # central; sampled in optimization

# N2: flash-loss coefficient  loss = K_FLASH * gas_kg * w_naphtha_in_oil
K_FLASH = BASE["flash_naphtha_loss"] / (BASE["gas"] * BASE["naphtha_in_oil_frac"])   # = 0.684
# --- P5 DWSIM 6-point recalibration (verify_vs_dwsim.py, 24 cells, post-fit <=1.6%) ---
LOSS_SCALE = 0.762   # flash+stab losses were calibrated pre-Path-A (0.02 keys); 24% high
WAX_LEAK   = 0.0134  # v3 plant-of-record: SCOL-2 keys tightened 0.02->0.005 (user, verified from run: wax purity 0.9948, flow 217.2); scaled 0.0534*(0.005/0.02)

# N3: per-category pyrolysis-oil densities [GK] (kg/L); aromatic-rich denser
OIL_RHO = {"PE_rigid": 0.78, "PE_film": 0.78, "PP_rigid": 0.77, "PP_film": 0.77,
           "PS_cat": 0.91, "PET_cat": 0.95, "MULTILAYER": 0.85, "CLOGGED": 0.85}

# Duty calibration: duty = c_i * (physics scale term), c_i fit at base case
DHVAP = {"NAPHTHA": 320.0, "MIDDLE": 250.0, "WAX": 220.0}   # kJ/kg [GK]
REFLUX = 2.0
_c1 = BASE["E1"] / BASE["feed_dwsim"]                                   # kW per kg/h through cooler
_c2 = BASE["E2"] / (BASE["oil"]*CUT_SPLIT["NAPHTHA"]*(1+REFLUX)*DHVAP["NAPHTHA"]/3600)
_c3 = BASE["E3"] / (BASE["oil"]*(1-CUT_SPLIT["NAPHTHA"])*DHVAP["MIDDLE"]/3600 + 1e-9)
_c4 = BASE["E4"] / (BASE["oil"]*CUT_SPLIT["MIDDLE"]*(1+REFLUX)*DHVAP["MIDDLE"]/3600)
_c5 = BASE["E5"] / (BASE["oil"]*CUT_SPLIT["WAX"]*DHVAP["WAX"]/3600)

PRICES = {"NAPHTHA": 45.0, "MIDDLE": 55.0, "WAX": 35.0, "FUELGAS": 0.0}  # PHP/kg central [GK]

def evaluate(comp: dict[str, float], tau_s: float = 240.0,
             split: dict[str, float] = CUT_SPLIT, basis_kg: float = 1000.0) -> dict:
    """Full-flowsheet response per `basis_kg` of plastic feed. Composition over CATEGORIES."""
    y = superposition_yields(comp, pet_correction=True)          # N1 (PET piecewise)
    X = conversion(comp, T_BASIS_K, tau_s)                       # N4
    oil = basis_kg * y["OIL_WAX"]/100 * X
    gas = basis_kg * y["GAS"]/100 * X
    sol = basis_kg * y["SOLID"]/100 * X
    unc = basis_kg * (1 - X)

    naph_in_oil = oil * split["NAPHTHA"]
    flash_loss = LOSS_SCALE * min(K_FLASH * gas * split["NAPHTHA"], 0.5*naph_in_oil)   # N2, recal
    stab_loss  = LOSS_SCALE * BASE["stab_lights_loss"]/(BASE["oil"]*BASE["naphtha_in_oil_frac"]) * naph_in_oil
    naphtha_s  = naph_in_oil - flash_loss - stab_loss
    wax0       = oil * split["WAX"]
    wax        = wax0 * (1 - WAX_LEAK)                                     # SCOL-2 HK leakage
    diesel     = oil * split["MIDDLE"] + wax0 * WAX_LEAK
    fuelgas    = gas + flash_loss + stab_loss

    # N3: composition-weighted oil density -> liquid volume
    tot = sum(comp.values()) or 1.0
    rho = sum(comp[k]/tot * OIL_RHO[k] for k in comp)
    liquid_L = (naphtha_s + diesel + wax) / rho

    m = fuelgas + naphtha_s + diesel + wax                       # through the train
    Q_cool = _c1*m + _c2*(naph_in_oil*(1+REFLUX)*DHVAP["NAPHTHA"]/3600) \
                   + _c4*(diesel*(1+REFLUX)*DHVAP["MIDDLE"]/3600)
    Q_heat = _c3*((oil-naph_in_oil)*DHVAP["MIDDLE"]/3600) + _c5*(wax*DHVAP["WAX"]/3600)

    recovery = (naphtha_s + diesel + wax) / basis_kg             # RA11898 conservative (liquid)
    revenue = (naphtha_s*PRICES["NAPHTHA"] + diesel*PRICES["MIDDLE"] + wax*PRICES["WAX"])

    return {"naphtha_s": naphtha_s, "diesel": diesel, "wax": wax, "fuelgas": fuelgas,
            "solid": sol, "unconv": unc, "liquid_L_per_t": liquid_L*(1000/basis_kg),
            "recovery": recovery, "Q_heat_kW_per_tph": Q_heat, "Q_cool_kW_per_tph": Q_cool,
            "revenue_php_per_t": revenue*(1000/basis_kg),
            "closure": (m + sol + unc)/basis_kg}

def base_case_check() -> None:
    """Reproduce the verified DWSIM point; must match anchors closely."""
    demo = {"PE_rigid":0.0,"PE_film":0.0,"PP_rigid":0.0,"PP_film":0.0,
            "PS_cat":0.0,"PET_cat":0.0,"MULTILAYER":0.15,"CLOGGED":0.0}
    # base DWSIM case used virgin HDPE/PP/PS; map: HDPE->PE_rigid-like yields differ.
    # Calibration check is done on FLOWS via the anchor feed directly:
    from lumped_kinetics import superposition_yields as sy
    comp = {"HDPE":0.45,"PP":0.30,"PS":0.10,"MULTILAYER":0.15}
    yv = sy(comp)
    oil = 1000*yv["OIL_WAX"]/100; gas = 1000*yv["GAS"]/100
    naph = oil*CUT_SPLIT["NAPHTHA"]; loss = K_FLASH*gas*CUT_SPLIT["NAPHTHA"]
    stab = BASE["stab_lights_loss"]/(BASE["oil"]*BASE["naphtha_in_oil_frac"])*naph
    print(f"base check: oil {oil:.0f} (anchor 882+ char basis), flash loss {loss:.1f} "
          f"(anchor 11.2), stab {stab:.2f} (anchor 2.46) kg/h-eq")

def build_flowsheet_doe(n_comp: int = 200, seed: int = 11898) -> pd.DataFrame:
    Xc = lhs_simplex(n_comp, seed=seed)
    rows = []
    for x in Xc:
        comp = {k: float(v) for k, v in zip(CATEGORIES, x)}
        for tau in TAU_GRID_S:
            out = evaluate(comp, tau)
            row = {f"x_{k}": comp[k] for k in CATEGORIES} | {"tau_s": tau} | out
            rows.append(row)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    base_case_check()
    df = build_flowsheet_doe(200)
    df.to_csv("flowsheet_doe.csv", index=False)
    print(f"\nflowsheet_doe.csv: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"closure: max |err| = {abs(df['closure']-1).max():.2e}")
    for c in ["liquid_L_per_t","recovery","Q_heat_kW_per_tph","revenue_php_per_t"]:
        print(f"  {c:20s}: mean {df[c].mean():10.1f}  P5 {df[c].quantile(.05):10.1f}  P95 {df[c].quantile(.95):10.1f}")
    print(f"  P(recovery>=0.80) at tau=240s: "
          f"{(df[df.tau_s==240].recovery>=0.80).mean()*100:.0f}%")
