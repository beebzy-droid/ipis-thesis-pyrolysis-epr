"""
cut_split_uncertainty.py  --  Option 3: oil cut split as a modeled uncertainty
===============================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

DECISION (locked this session): the naphtha/middle/wax split of the pyrolysis
OIL_WAX lump is treated as an UNCERTAIN PARAMETER, not a point value, because
Genuino et al. (2023) characterize the oil by 13C NMR carbon type only (no
boiling-point / GC-SimDist distribution). Literature bounds [GK, flagged]:
polyolefin pyrolysis oil at ~500 C: naphtha C5-C12 ~20-40%, middle C13-C20
~30-45%, wax C21+ ~20-40% of the oil, T/tau-dependent.

WHAT THIS MODULE PROVES QUANTITATIVELY (the separation argument):
  VERIFIED CHAIN  (feeds siting + RA 11898 constraint):
      feed composition -> superposition yields (V3-verified) -> total liquid
      [kg/t and L/t] and recovery fraction. INDEPENDENT of the cut split.
  UNCERTAIN CHAIN (feeds TEA revenue only):
      cut split ~ Dirichlet around DWSIM central (0.36/0.40/0.24) ->
      product-value mix [PHP/t]. Bounded, propagated by Monte Carlo.
  Output: recovery/yield variance from split = 0 (exact); revenue P5-P95 band.

All prices are [GK] bounded placeholders sampled uniformly; P6 TEA verifies.
Deps: numpy, pandas; imports lumped_kinetics (verified engine).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from lumped_kinetics import superposition_yields

RNG = np.random.default_rng(11898)   # reproducible; seed = the RA number

# ---------------------------------------------------------------------------
# VERIFIED LAYER -- total liquid, L/t, RA 11898 recovery (split-independent)
# ---------------------------------------------------------------------------
OIL_DENSITY_KG_L = (0.75, 0.80, 0.85)   # (lo, central, hi) [GK] mixed polyolefin pyro-oil

def verified_metrics(feed: dict[str, float]) -> dict:
    """Split-independent quantities: the numbers the siting model consumes."""
    y = superposition_yields(feed)                     # V3-verified (4.6 pp)
    oil_kg_t  = 10.0 * y["OIL_WAX"]                    # wt% -> kg per tonne feed
    gas_kg_t  = 10.0 * y["GAS"]
    sol_kg_t  = 10.0 * y["SOLID"]
    lo, c, hi = OIL_DENSITY_KG_L
    return {
        "oil_wax_kg_per_t": oil_kg_t,
        "gas_kg_per_t": gas_kg_t,
        "solid_kg_per_t": sol_kg_t,
        "liquid_L_per_t_central": oil_kg_t / c,
        "liquid_L_per_t_range": (oil_kg_t / hi, oil_kg_t / lo),
        # RA 11898 recovery accounting (assumption A1, state in thesis):
        # conservative = liquid product only counts as recovered;
        # extended     = liquid + fuel-gas energy recovery counts.
        "recovery_frac_conservative": y["OIL_WAX"] / 100.0,
        "recovery_frac_extended": (y["OIL_WAX"] + y["GAS"]) / 100.0,
    }

# ---------------------------------------------------------------------------
# UNCERTAIN LAYER -- cut split + prices (TEA revenue only)
# ---------------------------------------------------------------------------
SPLIT_CENTRAL = np.array([0.356, 0.406, 0.238])  # naphtha/middle/wax, DWSIM run basis
SPLIT_CONC = 50.0    # Dirichlet concentration: std ~ sqrt(p(1-p)/(c+1)) -> +/-2sigma
                     # ~ +/-0.13 on naphtha -- matches the [GK] literature bounds.

PRICES_PHP_KG = {    # (lo, hi) uniform [GK] ex-plant; P6 verifies with PH quotes
    "NAPHTHA": (35.0, 55.0),
    "MIDDLE":  (45.0, 65.0),   # diesel-range = the premium cut
    "WAX":     (25.0, 45.0),
}
CUTS = ["NAPHTHA", "MIDDLE", "WAX"]

def sample_splits(n: int) -> np.ndarray:
    """n x 3 Dirichlet samples around SPLIT_CENTRAL (each row sums to 1)."""
    return RNG.dirichlet(SPLIT_CONC * SPLIT_CENTRAL, size=n)

def monte_carlo(feed: dict[str, float], n: int = 10_000) -> pd.DataFrame:
    """Propagate split + price uncertainty to revenue; verified metrics constant."""
    vm = verified_metrics(feed)
    oil = vm["oil_wax_kg_per_t"]                       # kg oil per tonne feed (FIXED)
    splits = sample_splits(n)                          # (n,3)
    prices = np.column_stack([RNG.uniform(*PRICES_PHP_KG[c], size=n) for c in CUTS])
    cut_kg = splits * oil                              # kg of each cut per tonne
    revenue = (cut_kg * prices).sum(axis=1)            # PHP per tonne feed
    df = pd.DataFrame({
        "w_naphtha": splits[:, 0], "w_middle": splits[:, 1], "w_wax": splits[:, 2],
        "revenue_php_per_t": revenue,
        # verified metrics repeated per row to make the zero-variance check explicit:
        "liquid_L_per_t": vm["liquid_L_per_t_central"],
        "recovery_conservative": vm["recovery_frac_conservative"],
    })
    return df

# ---------------------------------------------------------------------------
def report(feed: dict[str, float], n: int = 10_000) -> None:
    vm = verified_metrics(feed)
    df = monte_carlo(feed, n)
    r = df["revenue_php_per_t"]
    print("=== VERIFIED (split-independent -> siting + RA 11898) ===")
    print(f"  oil/wax      : {vm['oil_wax_kg_per_t']:.0f} kg/t "
          f"({vm['liquid_L_per_t_central']:.0f} L/t central; "
          f"{vm['liquid_L_per_t_range'][0]:.0f}-{vm['liquid_L_per_t_range'][1]:.0f} L/t density band)")
    print(f"  gas / solid  : {vm['gas_kg_per_t']:.0f} / {vm['solid_kg_per_t']:.0f} kg/t")
    print(f"  RA11898 rec. : {vm['recovery_frac_conservative']*100:.1f}% conservative "
          f"(liquid only) | {vm['recovery_frac_extended']*100:.1f}% extended (+gas)")
    print(f"  vs 2028 target 80%: margin {vm['recovery_frac_conservative']*100-80:+.1f} pp "
          f"(conservative accounting)")
    print("\n=== UNCERTAIN (cut split + prices -> TEA revenue only) ===")
    print(f"  split samples: naphtha {df.w_naphtha.mean():.3f}+/-{df.w_naphtha.std():.3f} | "
          f"middle {df.w_middle.mean():.3f}+/-{df.w_middle.std():.3f} | "
          f"wax {df.w_wax.mean():.3f}+/-{df.w_wax.std():.3f}")
    print(f"  revenue      : mean {r.mean():,.0f} PHP/t | P5 {r.quantile(.05):,.0f} | "
          f"P95 {r.quantile(.95):,.0f}")
    print("\n=== SEPARATION PROOF ===")
    print(f"  var(liquid L/t)   across {n:,} split samples: {df.liquid_L_per_t.var():.3e}  (exactly 0)")
    print(f"  var(recovery frac) across split samples     : {df.recovery_conservative.var():.3e}  (exactly 0)")
    print("  -> the siting decision variables are provably insensitive to the cut split;")
    print("     the split affects ONLY revenue valuation, which is carried as a bounded band.")

if __name__ == "__main__":
    FEED = {"HDPE": 0.45, "PP": 0.30, "PS": 0.10, "MULTILAYER": 0.15}   # PH demo vector
    report(FEED)
    monte_carlo(FEED).to_csv("cut_split_mc.csv", index=False)
    print("\nWrote cut_split_mc.csv (10,000 samples) for the TEA phase.")
