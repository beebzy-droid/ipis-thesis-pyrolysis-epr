"""
superstructure_opt.py  --  P4 core: two-stage stochastic spatial superstructure
================================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

THE THESIS MODEL: decentralized-vs-centralized pyrolysis siting for Metro
Manila LGU catchments, solved as a two-stage stochastic program over the P3
composition uncertainty set, with the RA 11898 obligation embedded as a
footprint-based recovery constraint (penalty form = economically faithful to
the statute's "twice the cost of recovery" fine structure).

STRUCTURE
  Stage 1 (here-and-now): site openings + size selection  z[s,k] in {0,1}
  Stage 2 (recourse, per scenario w): LGU->site flows x[i,s,w] >= 0
  Yields: per-(LGU,scenario) coefficients r/rev from the flowsheet oracle.
     KEY PROPERTY: superposition + fixed cut split => the flowsheet response is
     LINEAR in composition, so blended-feed coefficients are EXACT in the LP
     (mixing linearity holds by construction; N1 PET-piecewise dormant <33%).
     The GP surrogate substitutes the oracle at scale; here the oracle is cheap
     and the GP demonstrates the architecture (stated honestly).

MODELING ASSUMPTIONS (state in thesis):
  A1 Footprint = total contracted LGU waste W (denominator of the recovery
     obligation). The network cannot cherry-pick its way to compliance.
  A2 Capture fraction 0.5 of generated plastic reaches the network [GK].
  A3 Hierarchical scenarios: national Dirichlet draw (c=25) -> LGU-level
     Dirichlet around it (c_lgu=60) = spatial heterogeneity within scenario.
  A4 rho = 0.80 (2028+ steady-state obligation).

DATA STATUS: LGU populations [GK; PSA 2020 census, verify]; plastic generation
0.07 kg/cap/d urban [GK]; distances approximate road km [GK]; techno-economics
[GK, P6 verifies]. Structure > numbers at this phase; every figure re-derivable.

Deps: pyomo, highspy, numpy, pandas. Imports flowsheet_shortcut, feedstock_doe.
"""
from __future__ import annotations
import numpy as np, pandas as pd
import pyomo.environ as pe
from flowsheet_shortcut import evaluate, CUT_SPLIT
from feedstock_doe import CATEGORIES, CENTRAL, DIRICHLET_CONC

SEED, RHO, TAU = 11898, 0.80, 240.0
rng = np.random.default_rng(SEED)

# --- spatial instance: 8 LGU sources [GK pop, PSA 2020], 4 candidate sites ---
LGUS = {"QC": 2.96e6, "Manila": 1.85e6, "Caloocan": 1.66e6, "Taguig": 0.89e6,
        "Pasig": 0.80e6, "Valenzuela": 0.71e6, "Paranaque": 0.69e6, "Makati": 0.63e6}
W_BASE = {i: p * 0.07 * 365 / 1000 * 0.5 for i, p in LGUS.items()}   # t/yr (A2)

SITES = ["Valenzuela_N", "Navotas_Port", "Taguig_FTI", "Carmona_Central"]
DIST = pd.DataFrame(  # road km [GK]
    [[12, 14, 30, 45], [10,  6, 25, 40], [ 8, 12, 34, 50], [30, 27,  6, 28],
     [22, 22, 12, 35], [ 3, 10, 36, 52], [28, 25, 10, 30], [20, 18,  9, 33]],
    index=LGUS, columns=SITES)

SIZES = {"S": 15_000, "M": 30_000, "L": 60_000, "XL": 120_000}       # t/yr
# annualized CAPEX [GK]: PHP 87k/tpa installed, CRF 14.7%, scale exponent 0.65
def capexA(cap):  return 87_000 * 0.147 * (cap ** 0.65) / (30_000 ** 0.65) * 30_000
CAPEX_A = {k: capexA(c) for k, c in SIZES.items()}
ALLOWED = {s: (["S","M","L"] if s != "Carmona_Central" else ["L","XL"]) for s in SITES}
OPEX_T, TRANS_T_KM = 5_000.0, 12.0                                    # PHP/t, PHP/(t.km) [GK]
PEN_T = 2 * (OPEX_T + CAPEX_A["M"]/SIZES["M"] + 10_000)               # ~2x cost of recovery [statute-faithful proxy]

# --- scenarios (A3): hierarchical composition draws + oracle coefficients ---
def gen_scenarios(S=50):
    alpha_nat = DIRICHLET_CONC * np.array([CENTRAL[k] for k in CATEGORIES])
    scen = []
    for w in range(S):
        nat = rng.dirichlet(alpha_nat)
        lgu_comp, r, rev = {}, {}, {}
        for i in LGUS:
            c = rng.dirichlet(60.0 * np.maximum(nat, 1e-3))
            comp = dict(zip(CATEGORIES, c))
            out = evaluate(comp, TAU)
            lgu_comp[i] = comp
            r[i]   = out["recovery"]                    # kg liquid / kg feed
            rev[i] = out["revenue_php_per_t"] / 1000    # PHP per kg -> per t handled below
        scen.append({"r": r, "rev": {i: rev[i]*1000 for i in LGUS}})
    return scen

def build_model(scen, fix_z=None):
    S = len(scen); P = 1.0/S
    m = pe.ConcreteModel()
    m.z = pe.Var(((s,k) for s in SITES for k in ALLOWED[s]), domain=pe.Binary)
    m.x = pe.Var(LGUS.keys(), SITES, range(S), domain=pe.NonNegativeReals)
    m.short = pe.Var(range(S), domain=pe.NonNegativeReals)
    m.one_size = pe.Constraint(SITES, rule=lambda m,s: sum(m.z[s,k] for k in ALLOWED[s]) <= 1)
    m.cap = pe.Constraint(SITES, range(S), rule=lambda m,s,w:
        sum(m.x[i,s,w] for i in LGUS) <= sum(SIZES[k]*m.z[s,k] for k in ALLOWED[s]))
    m.avail = pe.Constraint(LGUS.keys(), range(S), rule=lambda m,i,w:
        sum(m.x[i,s,w] for s in SITES) <= W_BASE[i])
    Wtot = sum(W_BASE.values())
    m.epr = pe.Constraint(range(S), rule=lambda m,w:
        m.short[w] >= RHO*Wtot - sum(scen[w]["r"][i]*m.x[i,s,w] for i in LGUS for s in SITES))
    def obj(m):
        capex = sum(CAPEX_A[k]*m.z[s,k] for s in SITES for k in ALLOWED[s])
        rec = P*sum(
            sum((TRANS_T_KM*DIST.loc[i,s] + OPEX_T - scen[w]["rev"][i]) * m.x[i,s,w]
                for i in LGUS for s in SITES) + PEN_T*m.short[w]
            for w in range(S))
        return capex + rec
    m.obj = pe.Objective(rule=obj, sense=pe.minimize)
    if fix_z is not None:
        for (s,k), v in fix_z.items():
            m.z[s,k].fix(v)
    return m

def solve(m):
    res = pe.SolverFactory("appsi_highs").solve(m)
    return m

def summarize(m, scen, label):
    S = len(scen); Wtot = sum(W_BASE.values())
    z = {(s,k): round(pe.value(m.z[s,k])) for s in SITES for k in ALLOWED[s]}
    opened = {s:k for (s,k),v in z.items() if v==1}
    comp_ok = sum(1 for w in range(S) if pe.value(m.short[w]) < 1e-3)/S
    rec = [sum(scen[w]["r"][i]*pe.value(m.x[i,s,w]) for i in LGUS for s in SITES)/Wtot
           for w in range(S)]
    print(f"\n=== {label} ===")
    print(f"  config: {opened or 'NO BUILD'}  | total cap {sum(SIZES[k] for k in opened.values()):,} t/yr vs W {Wtot:,.0f} t/yr")
    print(f"  E[obj] {pe.value(m.obj)/1e6:,.1f} MPHP/yr | P(recovery>=80%) = {comp_ok*100:.0f}% | recovery mean {np.mean(rec)*100:.1f}% [P5 {np.quantile(rec,.05)*100:.1f}, P95 {np.quantile(rec,.95)*100:.1f}]")
    return z, pe.value(m.obj), comp_ok

if __name__ == "__main__":
    scen = gen_scenarios(50)
    # --- STOCHASTIC solution ---
    m_sp = solve(build_model(scen))
    z_sp, obj_sp, c_sp = summarize(m_sp, scen, "STOCHASTIC (here-and-now under 50 scenarios)")
    # --- DETERMINISTIC baseline: mean composition, then evaluated under uncertainty ---
    mean_out = evaluate(CENTRAL, TAU)
    det = [{"r": {i: mean_out["recovery"] for i in LGUS},
            "rev": {i: mean_out["revenue_php_per_t"] for i in LGUS}}]
    m_ev = solve(build_model(det))
    z_ev = {(s,k): round(pe.value(m_ev.z[s,k])) for s in SITES for k in ALLOWED[s]}
    print(f"\n=== DETERMINISTIC design (mean composition) ===\n  config: {{s:k for (s,k),v in z_ev.items() if v==1}}", {s:k for (s,k),v in z_ev.items() if v==1})
    m_eev = solve(build_model(scen, fix_z=z_ev))          # det design exposed to uncertainty
    _, obj_eev, c_eev = summarize(m_eev, scen, "DETERMINISTIC design EVALUATED under the 50 scenarios (EEV)")
    vss = obj_eev - obj_sp
    print(f"\n=== VALUE OF THE STOCHASTIC SOLUTION ===")
    print(f"  VSS = EEV - SP = {vss/1e6:,.1f} MPHP/yr  ({vss/abs(obj_eev)*100 if obj_eev else 0:.1f}% of EEV)")
    print(f"  compliance: stochastic {c_sp*100:.0f}% vs deterministic-design {c_eev*100:.0f}%")
