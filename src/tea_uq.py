"""
tea_uq.py -- P6: TEA (NPV/IRR/payback/break-even PHP/L) + Sobol UQ + streamlined LCA
=====================================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

BASIS: the SAA-robust design (P5 R2): Valenzuela_S 15 kt/yr + Carmona_XL 120 kt/yr
+ gas module @ Carmona; throughput 130.2 kt/yr (8 NCR LGUs, A2 capture 0.5).

VERIFIED ANCHORS: diesel retail Metro Manila 69.90-74.03 PHP/L (DOE, Jul 2026) [V];
ex-plant diesel parity ~51-55 PHP/L (net of excise 6 PHP/L, VAT 12%, margin) [derived].
Product prices are held BELOW parity (central diesel-cut 55 PHP/kg = ~46 PHP/L):
conservative by construction.

[GK] (P6 flags, ranges carried in MC): CAPEX 87k PHP/tpa @30kt ref, exp 0.65, +/-30%;
OPEX 5k PHP/t +/-30%; discount 12%; 15 yr; 8000 h/yr; oil rho 0.75-0.85 kg/L;
transport 240 PHP/t avg; EFs: grid 0.65 kgCO2e/kWh, truck 0.10 kgCO2e/t-km,
fuel-gas combustion 2.9 kgCO2e/kg, avoided upstream refining 0.6 kgCO2e/L.

UQ: Monte Carlo (10k) over composition (P3 Dirichlet) x prices x capex/opex;
Sobol (SALib, Saltelli) on NPV over 6 factors. LCA: streamlined gate-to-gate
+ displacement credit, per tonne diverted and per L fuel.
"""
from __future__ import annotations
import numpy as np, pandas as pd
from SALib.sample import saltelli
from SALib.analyze import sobol
from flowsheet_shortcut import evaluate
from feedstock_doe import CATEGORIES, CENTRAL, DIRICHLET_CONC, sample_dirichlet

SEED = 11898; rng = np.random.default_rng(SEED)
THRU = 130_177.0            # t/yr (8 LGUs, A2)
CAPS = [15_000, 120_000]
def capex_full(c): return 87_000*30_000*(c/30_000)**0.65
CAPEX0 = sum(capex_full(c) for c in CAPS) + 100e6          # + gas module capital
DISC, YRS, OPEX0, TRANS = 0.12, 15, 5_000.0, 240.0
CRF = DISC*(1+DISC)**YRS/((1+DISC)**YRS-1)

def cashflow_npv(rev_t, opex_t, capex, thru=THRU):
    ann = (rev_t - opex_t - TRANS)*thru
    npv = -capex + sum(ann/(1+DISC)**t for t in range(1, YRS+1))
    # IRR via bisection on rate
    lo, hi = -0.5, 2.0
    f = lambda r: -capex + ann*((1-(1+r)**-YRS)/r if abs(r)>1e-9 else YRS)
    if f(lo)*f(hi) > 0: irr = np.nan
    else:
        for _ in range(80):
            mid = 0.5*(lo+hi)
            if f(lo)*f(mid) <= 0: hi = mid
            else: lo = mid
        irr = 0.5*(lo+hi)
    payback = capex/ann if ann > 0 else np.inf
    return npv, irr, payback, ann

def mc(n=10_000):
    comps = sample_dirichlet(n, seed=SEED)
    pn = rng.uniform(35, 55, n); pm = rng.uniform(45, 65, n); pw = rng.uniform(25, 45, n)
    cx = CAPEX0*rng.uniform(0.7, 1.3, n); ox = OPEX0*rng.uniform(0.7, 1.3, n)
    rho = rng.uniform(0.75, 0.85, n)
    rows = []
    for k in range(n):
        comp = dict(zip(CATEGORIES, comps[k]))
        o = evaluate(comp, 240.0)
        rev = o["naphtha_s"]*pn[k] + o["diesel"]*pm[k] + o["wax"]*pw[k]      # PHP per t feed
        L_t = (o["naphtha_s"]+o["diesel"]+o["wax"])/rho[k]
        npv, irr, pb, ann = cashflow_npv(rev, ox[k], cx[k])
        # break-even blended price (PHP/L): price level where NPV=0
        be = ((ox[k]+TRANS)*THRU + cx[k]*CRF) / (L_t*THRU) if L_t > 0 else np.nan
        rows.append({"npv_B": npv/1e9, "irr": irr, "payback": pb,
                     "L_per_t": L_t, "breakeven_php_L": be, "rev_t": rev})
    return pd.DataFrame(rows)

def sobol_npv():
    prob = {"num_vars": 6, "names": ["oil_yield","p_naph","p_mid","p_wax","capex_m","opex_m"],
            "bounds": [[0.60, 0.90], [35,55], [45,65], [25,45], [0.7,1.3], [0.7,1.3]]}
    X = saltelli.sample(prob, 1024, calc_second_order=False)
    Y = np.empty(len(X))
    split = np.array([0.356, 0.406, 0.238]); rho = 0.80
    for i, x in enumerate(X):
        oy, a, b, c, cm, om = x
        cuts = 1000*oy*split*np.array([1-0.0715-0.008, 1, 1])   # flash+stab loss on naphtha
        rev = cuts[0]*a + cuts[1]*b + cuts[2]*c
        Y[i], *_ = cashflow_npv(rev, OPEX0*om, CAPEX0*cm)
    S = sobol.analyze(prob, Y, calc_second_order=False, seed=SEED)
    return pd.DataFrame({"factor": prob["names"], "S1": S["S1"], "ST": S["ST"]}).sort_values("ST", ascending=False)

def lca(df):
    o = evaluate(CENTRAL, 240.0)
    liq = o["naphtha_s"]+o["diesel"]+o["wax"]                  # kg/t
    gas = o["fuelgas"]
    heat_kwh = 290.0/ (THRU/8000) * 1000/1000                  # ~ Q_heat per t: use oracle
    q = o["Q_heat_kW_per_tph"]*8760/1000                       # rough; use audit values instead
    ef = {"truck": 0.10, "grid": 0.65, "gascomb": 2.9, "avoid_L": 0.6}
    e_transport = 20*ef["truck"]                                # 20 km avg, kgCO2e/t
    e_process = gas*ef["gascomb"]                               # own fuel gas combusted, kg/t
    e_elec = 30*ef["grid"]                                      # 30 kWh/t aux [GK]
    credit = (liq/0.80)*ef["avoid_L"]                           # avoided upstream refining
    net = e_transport + e_process + e_elec - credit
    return {"transport": e_transport, "process_gas": e_process, "electricity": e_elec,
            "credit_refining": -credit, "NET_kgCO2e_per_t": net,
            "per_L_fuel": net/(liq/0.80)}

if __name__ == "__main__":
    df = mc(10_000)
    print("=== TEA Monte Carlo (n=10,000; composition x prices x CAPEX/OPEX) ===")
    for c, u in [("npv_B","B PHP"),("irr",""),("payback","yr"),("L_per_t","L/t"),("breakeven_php_L","PHP/L")]:
        s = df[c].replace([np.inf,-np.inf], np.nan).dropna()
        print(f"  {c:18s}: mean {s.mean():8.2f} | P5 {s.quantile(.05):8.2f} | P95 {s.quantile(.95):8.2f} {u}")
    print(f"  P(NPV>0) = {(df.npv_B>0).mean()*100:.0f}% | P(IRR>12%) = {(df.irr>0.12).mean()*100:.0f}%")
    print(f"  Break-even vs ex-plant diesel parity 51-55 PHP/L [V-derived]: "
          f"margin at P95 breakeven = {51-df.breakeven_php_L.quantile(.95):.1f} PHP/L")
    print("\n=== Sobol (NPV) ===")
    print(sobol_npv().to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\n=== Streamlined LCA (central composition; [GK] EFs) ===")
    for k, v in lca(df).items(): print(f"  {k:20s}: {v:8.1f} kgCO2e/t" if "per_L" not in k else f"  {k:20s}: {v:8.2f} kgCO2e/L")
    df.to_csv("tea_mc.csv", index=False)
