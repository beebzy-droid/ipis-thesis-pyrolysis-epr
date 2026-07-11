"""
superstructure_p4b.py -- P4b: the four-lever experiment + chance-constrained variant
=====================================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A). Extends superstructure_opt.py (P4a, VSS=0
diagnosed: chemistry-bound compliance under A1). Levers, each motivated by the
P4a diagnosis:

  L1 GAS-ENERGY-RECOVERY MODULE per site (stage-1 binary, capex [GK] 15 MPHP/yr
     annualized): fuel gas counts toward recovery at eta=0.9 ONLY if built.
     Shortfall is convex in composition -> Jensen -> mean-design under-hedges.
  L2 PARTIAL CONTRACTING (stage-1 binary per LGU): a PRO chooses which obliged
     footprints to serve (legitimate under RA 11898 -- producers contract PROs
     voluntarily). Obligation denominator = contracted footprint only.
  L3 QUANTITY UNCERTAINTY: W_iw = W_i * lognormal(sigma=0.20) [GK] -> capacity
     sizing becomes a genuine hedge.
  L4 STATUTE-FAITHFUL FINES: pen_w = max( 2x-recovery-cost * shortfall,
     20 MPHP lump if noncompliant )  [RA 11898 fine structure].

  + LGU heterogeneity sensitivity: c_lgu in {60 (mild), 15 (strong)} -- no data
    constrains within-metro spread [P3 finding], so we report both.
  + CHANCE-CONSTRAINED variant: min cost s.t. P(recovery>=80%) >= 1-eps
    (scenario-counting binaries). If infeasible: max-compliance solve ->
    the FEASIBILITY FRONTIER of the 2028 obligation.

Deps: pyomo, highspy. Reuses flowsheet oracle + P3 uncertainty set.
"""
from __future__ import annotations
import numpy as np, pandas as pd
import pyomo.environ as pe
from flowsheet_shortcut import evaluate
from feedstock_doe import CATEGORIES, CENTRAL, DIRICHLET_CONC

SEED, RHO, TAU, S = 11898, 0.80, 240.0, 50
rng = np.random.default_rng(SEED)

LGUS = {"QC": 2.96e6, "Manila": 1.85e6, "Caloocan": 1.66e6, "Taguig": 0.89e6,
        "Pasig": 0.80e6, "Valenzuela": 0.71e6, "Paranaque": 0.69e6, "Makati": 0.63e6}
W0 = {i: p*0.07*365/1000*0.5 for i, p in LGUS.items()}
SITES = ["Valenzuela_N", "Navotas_Port", "Taguig_FTI", "Carmona_Central"]
DIST = pd.DataFrame([[12,14,30,45],[10,6,25,40],[8,12,34,50],[30,27,6,28],
                     [22,22,12,35],[3,10,36,52],[28,25,10,30],[20,18,9,33]],
                    index=LGUS, columns=SITES)
SIZES = {"S":15_000,"M":30_000,"L":60_000,"XL":120_000}
def capexA(c): return 87_000*0.147*(c**0.65)/(30_000**0.65)*30_000
CAPEX_A = {k: capexA(c) for k,c in SIZES.items()}
ALLOWED = {s: (["S","M","L"] if s!="Carmona_Central" else ["L","XL"]) for s in SITES}
OPEX_T, TRANS = 5_000.0, 12.0
PEN_T = 2*(OPEX_T + CAPEX_A["M"]/SIZES["M"] + 10_000)         # 2x recovery-cost proxy
FINE_LUMP, GASMOD_CAPEX, ETA = 20e6, 15e6, 0.9                # [statute] / [GK] / [GK]

def gen_scen(c_lgu=60.0, s=S):
    a_nat = DIRICHLET_CONC*np.array([CENTRAL[k] for k in CATEGORIES])
    out=[]
    for w in range(s):
        nat = rng.dirichlet(a_nat)
        d={"r":{}, "g":{}, "rev":{}, "W":{}}
        for i in LGUS:
            comp = dict(zip(CATEGORIES, rng.dirichlet(c_lgu*np.maximum(nat,1e-3))))
            o = evaluate(comp, TAU)
            d["r"][i], d["g"][i] = o["recovery"], o["fuelgas"]/1000.0
            d["rev"][i] = o["revenue_php_per_t"]
            d["W"][i] = W0[i]*float(rng.lognormal(0, 0.20))            # L3
        out.append(d)
    return out

def build(scen, eps=None, fix=None):
    Sn=len(scen); P=1.0/Sn
    m=pe.ConcreteModel()
    m.z=pe.Var(((s,k) for s in SITES for k in ALLOWED[s]), domain=pe.Binary)
    m.gm=pe.Var(SITES, domain=pe.Binary)                                # L1
    m.ct=pe.Var(LGUS.keys(), domain=pe.Binary)                          # L2
    m.x=pe.Var(LGUS.keys(), SITES, range(Sn), domain=pe.NonNegativeReals)
    m.cred=pe.Var(SITES, range(Sn), domain=pe.NonNegativeReals)
    m.short=pe.Var(range(Sn), domain=pe.NonNegativeReals)
    m.pen=pe.Var(range(Sn), domain=pe.NonNegativeReals)
    m.b=pe.Var(range(Sn), domain=pe.Binary)                             # noncompliance
    m.onesize=pe.Constraint(SITES, rule=lambda m,s: sum(m.z[s,k] for k in ALLOWED[s])<=1)
    m.cap=pe.Constraint(SITES, range(Sn), rule=lambda m,s,w:
        sum(m.x[i,s,w] for i in LGUS)<=sum(SIZES[k]*m.z[s,k] for k in ALLOWED[s]))
    m.avail=pe.Constraint(LGUS.keys(), range(Sn), rule=lambda m,i,w:
        sum(m.x[i,s,w] for s in SITES)<=scen[w]["W"][i]*m.ct[i])
    m.cr1=pe.Constraint(SITES, range(Sn), rule=lambda m,s,w:
        m.cred[s,w]<=ETA*sum(scen[w]["g"][i]*m.x[i,s,w] for i in LGUS))
    m.cr2=pe.Constraint(SITES, range(Sn), rule=lambda m,s,w:
        m.cred[s,w]<=15_000*m.gm[s])                                    # M: eta*gmax*capmax
    m.epr=pe.Constraint(range(Sn), rule=lambda m,w:
        m.short[w] >= RHO*sum(scen[w]["W"][i]*m.ct[i] for i in LGUS)
                      - sum(scen[w]["r"][i]*m.x[i,s,w] for i in LGUS for s in SITES)
                      - sum(m.cred[s,w] for s in SITES))
    m.p1=pe.Constraint(range(Sn), rule=lambda m,w: m.pen[w]>=PEN_T*m.short[w])   # L4
    m.p2=pe.Constraint(range(Sn), rule=lambda m,w: m.pen[w]>=FINE_LUMP*m.b[w])
    m.bm=pe.Constraint(range(Sn), rule=lambda m,w: m.short[w]<=2.0e5*m.b[w])
    if eps is not None:
        m.cc=pe.Constraint(expr=sum(m.b[w] for w in range(Sn))<=int(eps*Sn))
    def obj(m):
        cap=sum(CAPEX_A[k]*m.z[s,k] for s in SITES for k in ALLOWED[s])+GASMOD_CAPEX*sum(m.gm[s] for s in SITES)
        rec=P*sum(sum((TRANS*DIST.loc[i,s]+OPEX_T-scen[w]["rev"][i])*m.x[i,s,w]
                      for i in LGUS for s in SITES)+m.pen[w] for w in range(Sn))
        return cap+rec
    m.obj=pe.Objective(rule=obj, sense=pe.minimize)
    if fix:
        for name,vals in fix.items():
            var=getattr(m,name)
            for key,v in vals.items(): var[key].fix(v)
    return m

def solve(m, gap=0.0001):
    opt=pe.SolverFactory("appsi_highs"); opt.config.mip_gap=gap
    opt.solve(m); return m

def readout(m, scen, label):
    Sn=len(scen)
    z={(s,k):round(pe.value(m.z[s,k])) for s in SITES for k in ALLOWED[s]}
    opened={s:k for (s,k),v in z.items() if v==1}
    gmods=[s for s in SITES if round(pe.value(m.gm[s]))==1]
    ctr=[i for i in LGUS if round(pe.value(m.ct[i]))==1]
    comp=1-sum(round(pe.value(m.b[w])) for w in range(Sn))/Sn
    print(f"\n=== {label} ===")
    print(f"  sites: {opened or 'none'} | gas modules: {gmods or 'none'}")
    print(f"  contracted LGUs ({len(ctr)}/8): {ctr}")
    print(f"  E[obj] {pe.value(m.obj)/1e6:,.1f} MPHP/yr | P(compliance) {comp*100:.0f}%")
    return {"z":z, "gm":{s:round(pe.value(m.gm[s])) for s in SITES},
            "ct":{i:round(pe.value(m.ct[i])) for i in LGUS}}, pe.value(m.obj), comp

if __name__=="__main__":
    for c_lgu, tag in [(60.0,"MILD heterogeneity (c_lgu=60)"), (15.0,"STRONG heterogeneity (c_lgu=15)")]:
        rng_state = np.random.default_rng(SEED)  # reset for comparability
        globals()['rng'] = rng_state
        scen = gen_scen(c_lgu)
        print("\n"+"#"*70+f"\n# {tag}\n"+"#"*70)
        fx, obj_sp, c_sp = readout(solve(build(scen)), scen, "STOCHASTIC (4 levers)")
        mean_o = evaluate(CENTRAL, TAU)
        det=[{"r":{i:mean_o["recovery"] for i in LGUS},"g":{i:mean_o["fuelgas"]/1000 for i in LGUS},
              "rev":{i:mean_o["revenue_php_per_t"] for i in LGUS},"W":dict(W0)}]
        m_ev=solve(build(det))
        fix={"z":{(s,k):round(pe.value(m_ev.z[s,k])) for s in SITES for k in ALLOWED[s]},
             "gm":{s:round(pe.value(m_ev.gm[s])) for s in SITES},
             "ct":{i:round(pe.value(m_ev.ct[i])) for i in LGUS}}
        _, obj_eev, c_eev = readout(solve(build(scen, fix=fix)), scen, "DETERMINISTIC design under scenarios (EEV)")
        print(f"  --> VSS = {(obj_eev-obj_sp)/1e6:,.1f} MPHP/yr | compliance SP {c_sp*100:.0f}% vs det {c_eev*100:.0f}%")
        # chance-constrained: 90% assurance
        m_cc=build(scen, eps=0.10); solve(m_cc)
        try:
            _, obj_cc, c_cc = readout(m_cc, scen, "CHANCE-CONSTRAINED (P>=90%)")
            print(f"  --> COST OF 90% ASSURANCE = {(obj_cc-obj_sp)/1e6:,.1f} MPHP/yr over risk-neutral")
        except Exception:
            m_mx=build(scen); m_mx.obj.deactivate()
            m_mx.obj2=pe.Objective(expr=sum(m_mx.b[w] for w in range(len(scen))), sense=pe.minimize)
            solve(m_mx)
            print(f"  CC at 90% INFEASIBLE; max achievable P(compliance) = {(1-pe.value(m_mx.obj2)/len(scen))*100:.0f}%")
