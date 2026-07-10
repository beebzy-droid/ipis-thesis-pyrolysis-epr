"""
feedstock_doe.py  --  P3: PH feedstock composition uncertainty set + LHS DOE
=============================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

DATA SITUATION (verified, P3 recon):
  - National anchors [V]: 2.7 Mt/yr plastic waste; ~28% of key resins recycled
    (2019); stream dominated by low-value flexible/sachet packaging; key-resin
    framing = PET/LDPE/HDPE/PP (World Bank 2021, hdl:10986/35295).
  - LGU-level WACS studies report "plastics" as ONE MSW fraction; NO public
    LGU-resolved resin split exists (WACS manual, DOST-ITDI, does not mandate it).
  => The composition uncertainty set is CONSTRUCTED, not measured. That is the
     thesis's data-scarcity premise (G1). Everything not [V] is flagged [GK].

DESIGN (pre-registered in P1):
  1) Composition lives on the 8-simplex of Genuino DKR-350 categories (the only
     categories with V3-verified yields).
  2) STOCHASTIC set: Dirichlet(alpha = c * m) around a central vector m, with
     concentration c as the data-scarcity knob (small c = honest wide set).
  3) ROBUST fallback: box (min,max) per category + simplex constraint, for the
     Bertsimas-Sim / DRO formulation if the distributional story is challenged.
  4) LHS DOE over (composition x tau) at the 500 C Genuino basis, evaluated
     through the VERIFIED yield engine -> surrogate training table for P4.

HONEST NOTE for P4: superposition is LINEAR in composition, so a surrogate of
the reactor alone is trivial. The surrogate's real target is the FULL flowsheet
response (cut flows, duties, purities, energy), which is nonlinear through the
separation train. This DOE is the INPUT design; flowsheet evaluation of the DOE
points (DWSIM or python separation shortcut) is the P4 step.

Deps: numpy, scipy, pandas. Uses lumped_kinetics (verified).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import qmc
from lumped_kinetics import superposition_yields, conversion, tau_for_conversion

RNG_SEED = 11898
CATEGORIES = ["PE_rigid", "PE_film", "PP_rigid", "PP_film",
              "PS_cat", "PET_cat", "MULTILAYER", "CLOGGED"]

# ---------------------------------------------------------------------------
# CENTRAL COMPOSITION VECTOR m  [GK -- constructed, every line justified]
# Qualitative anchors [V]: film/flexible-dominated stream ("high share of
# low-value flexible packaging", sachet economy); PET has the HIGHEST
# collection-for-recycling pull-out (so post-collection residual PET is LOW);
# rigids are preferentially picked by the informal sector (value hierarchy).
# Magnitudes are [GK] engineering estimates pending a commissioned WACS+ study;
# the WIDE Dirichlet below is the honest representation of that ignorance.
# ---------------------------------------------------------------------------
CENTRAL = {
    "PE_film":    0.28,   # sachet/film economy dominates residual stream [GK]
    "MULTILAYER": 0.22,   # sachets proper: multilayer laminates [GK]
    "PP_film":    0.12,   # flexible PP (noodle/snack wrappers) [GK]
    "PE_rigid":   0.10,   # rigids partially removed by informal sector [GK]
    "PP_rigid":   0.10,   # [GK]
    "CLOGGED":    0.08,   # contaminated/mixed residual [GK]
    "PS_cat":     0.05,   # PS incl. foam [GK]
    "PET_cat":    0.05,   # LOW residual: highest waste-picker pull-out [V anchor, GK magnitude]
}
assert abs(sum(CENTRAL.values()) - 1.0) < 1e-9

# Data-scarcity knob: c=25 gives per-category std ~ sqrt(m(1-m)/(c+1))
# e.g. PE_film: sqrt(.28*.72/26)=0.088 -> 95% band ~ [0.12, 0.46]. WIDE = honest.
DIRICHLET_CONC = 25.0

# ROBUST box set [GK]: central +/- 2 sigma, clipped to [0.01, 0.60]
def robust_box(conc: float = DIRICHLET_CONC) -> dict[str, tuple[float, float]]:
    box = {}
    for k in CATEGORIES:
        m = CENTRAL[k]
        s = np.sqrt(m * (1 - m) / (conc + 1))
        box[k] = (max(0.01, m - 2 * s), min(0.60, m + 2 * s))
    return box

# ---------------------------------------------------------------------------
# SAMPLERS
# ---------------------------------------------------------------------------
def sample_dirichlet(n: int, conc: float = DIRICHLET_CONC,
                     seed: int = RNG_SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    alpha = conc * np.array([CENTRAL[k] for k in CATEGORIES])
    return rng.dirichlet(alpha, size=n)

def lhs_simplex(n: int, seed: int = RNG_SEED) -> np.ndarray:
    """
    Space-filling LHS on the simplex via the exponential-spacings map:
    LHS in [0,1]^d -> E_i = -ln(1-u_i) -> x = E/sum(E). Preserves LHS
    stratification per coordinate while landing uniformly-ish on the simplex,
    then importance-tilted toward the Dirichlet set by rejection against
    the robust box (keeps DOE inside the plausible region).
    """
    d = len(CATEGORIES)
    sampler = qmc.LatinHypercube(d=d, seed=seed)
    u = sampler.random(n * 6)                      # oversample for the box filter
    e = -np.log(1.0 - np.clip(u, 0, 1 - 1e-12))
    x = e / e.sum(axis=1, keepdims=True)
    box = robust_box()
    lo = np.array([box[k][0] for k in CATEGORIES])
    hi = np.array([box[k][1] for k in CATEGORIES])
    keep = ((x >= lo) & (x <= hi)).all(axis=1)
    x = x[keep][:n]
    if len(x) < n:                                  # top up from Dirichlet if box is tight
        x = np.vstack([x, sample_dirichlet(n - len(x), seed=seed + 1)])
    return x

# ---------------------------------------------------------------------------
# DOE BUILD  -- inputs (composition, tau) -> verified reactor outputs
# ---------------------------------------------------------------------------
T_BASIS_K = 773.15          # Genuino 500 C basis; off-basis unsupported (flag)
TAU_GRID_S = [60.0, 120.0, 180.0, 240.0]   # spans tau99~177 s at 500 C (Westerhout)

def build_doe(n_comp: int = 200, seed: int = RNG_SEED) -> pd.DataFrame:
    X = lhs_simplex(n_comp, seed=seed)
    rows = []
    for x in X:
        comp = {k: float(v) for k, v in zip(CATEGORIES, x)}
        y_full = superposition_yields(comp)                    # complete-conversion split
        for tau in TAU_GRID_S:
            Xc = conversion(comp, T_BASIS_K, tau)
            row = {f"x_{k}": comp[k] for k in CATEGORIES}
            row |= {"T_K": T_BASIS_K, "tau_s": tau, "X_conv": Xc,
                    "tau99_s": tau_for_conversion(comp, T_BASIS_K)}
            row |= {f"y_{l}": y_full[l] * Xc for l in ("GAS", "OIL_WAX", "SOLID")}
            row["y_unconv"] = 100.0 * (1 - Xc)
            rows.append(row)
    return pd.DataFrame(rows)

def summarize(df: pd.DataFrame) -> None:
    full = df[df.tau_s == max(TAU_GRID_S)]
    oil = full["y_OIL_WAX"]
    print(f"DOE: {df.shape[0]} rows ({df[[c for c in df if c.startswith('x_')]].drop_duplicates().shape[0]} compositions x {len(TAU_GRID_S)} tau)")
    print(f"Composition set (Dirichlet c={DIRICHLET_CONC}, [GK] central, box-filtered LHS):")
    for k in CATEGORIES:
        col = df[f"x_{k}"]
        print(f"  {k:11s}: mean {col.mean():.3f}  range [{col.min():.3f}, {col.max():.3f}]")
    print(f"\nOIL_WAX yield across the set (tau={max(TAU_GRID_S):.0f}s): "
          f"mean {oil.mean():.1f} | P5 {oil.quantile(.05):.1f} | P95 {oil.quantile(.95):.1f} wt%")
    rec = oil / 100.0
    print(f"RA11898 conservative recovery: P5 {rec.quantile(.05)*100:.1f}% | P95 {rec.quantile(.95)*100:.1f}% "
          f"vs 80% target -> P(recovery >= 80%) = {(rec >= 0.80).mean()*100:.0f}%")
    print("\n-> THIS is G1 made quantitative: composition uncertainty alone moves the")
    print("   compliance margin; the stochastic siting program (P4) prices that risk.")

if __name__ == "__main__":
    df = build_doe(200)
    df.to_csv("doe_table.csv", index=False)
    summarize(df)
    box = robust_box()
    pd.DataFrame([{"category": k, "lo": v[0], "hi": v[1], "central": CENTRAL[k]}
                  for k, v in box.items()]).to_csv("uncertainty_set.csv", index=False)
    print("\nWrote doe_table.csv (surrogate training inputs+reactor outputs) and uncertainty_set.csv (robust box).")
