"""
saa_stability.py -- P5: SAA replication study + deterministic-benchmark table
==============================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

JOB 1 (SAA stability): R=10 independent replications x S=100 scenarios, both
heterogeneity regimes. Per replication: risk-neutral SP solve + chance-
constrained solve (P>=90%). Outputs: mean +/- 95% CI on the cost of assurance,
frequency of each design feature (gas modules, LGU drops) -> distinguishes
structural decisions from sampling noise. MIP gap 1e-3 (+/-~2.7 MPHP on a
~2,700 MPHP objective; adequate for CI purposes, stated).

JOB 2 (benchmark table): deterministic mean-composition design "promises"
compliance (short=0 at the mean); realized compliance under the scenario set
is lower. Over-promise [pp] = 100% - realized. The Santibanez-class contrast:
composition-blind fixed-yield models cannot even see the risk.

Deps: pyomo, highspy. Reuses superstructure_p4b machinery.
"""
from __future__ import annotations
import numpy as np, pandas as pd, time
import pyomo.environ as pe
import superstructure_p4b as M

R, S_SAA, EPS = 10, 100, 0.10   # executed in batches (CLI: regime rep_start rep_end) to fit call limits

def cc_solve(scen):
    m = M.build(scen, eps=EPS)
    M.solve(m, gap=1e-3)
    try:
        obj = pe.value(m.obj)
    except Exception:
        return None
    Sn = len(scen)
    comp = 1 - sum(round(pe.value(m.b[w])) for w in range(Sn)) / Sn
    gm = tuple(s for s in M.SITES if round(pe.value(m.gm[s])) == 1)
    dropped = tuple(i for i in M.LGUS if round(pe.value(m.ct[i])) == 0)
    sites = tuple((s, k) for s in M.SITES for k in M.ALLOWED[s]
                  if round(pe.value(m.z[s, k])) == 1)
    return {"obj_cc": obj, "comp": comp, "gm": gm, "dropped": dropped, "sites": sites}

def run_batch(c_lgu, tag, rep_start, rep_end):
    import os
    rows = []
    if True:
        for rep in range(rep_start, rep_end):
            M.rng = np.random.default_rng(20_000 + 1000 * rep + int(c_lgu))
            scen = M.gen_scen(c_lgu, s=S_SAA)
            t0 = time.time()
            m_sp = M.solve(M.build(scen), gap=1e-3)
            obj_sp = pe.value(m_sp.obj)
            comp_sp = 1 - sum(round(pe.value(m_sp.b[w])) for w in range(S_SAA)) / S_SAA
            cc = cc_solve(scen)
            rows.append({"het": tag, "rep": rep, "obj_sp": obj_sp, "comp_sp": comp_sp,
                         "obj_cc": cc["obj_cc"] if cc else np.nan,
                         "assure_cost": (cc["obj_cc"] - obj_sp) if cc else np.nan,
                         "comp_cc": cc["comp"] if cc else np.nan,
                         "gm": cc["gm"] if cc else (), "dropped": cc["dropped"] if cc else ("INFEAS",),
                         "sites": cc["sites"] if cc else (), "t_s": time.time() - t0})
            print(f"[{tag} rep {rep}] SP {obj_sp/1e6:,.0f} | comp_SP {comp_sp*100:.0f}% | "
                  f"assure {rows[-1]['assure_cost']/1e6:,.1f} MPHP | dropped {rows[-1]['dropped'] or '-'} "
                  f"| {rows[-1]['t_s']:.0f}s", flush=True)
    hdr = not os.path.exists("saa_results.csv")
    pd.DataFrame(rows).to_csv("saa_results.csv", mode="a", header=hdr, index=False)

def aggregate():
    dfall = pd.read_csv("saa_results.csv")
    import ast
    for tag in ("mild", "strong"):
        df = dfall[dfall.het == tag]
        ac = df["assure_cost"].dropna() / 1e6
        ci = 1.96 * ac.std(ddof=1) / np.sqrt(len(ac))
        drops = [i for d in df["dropped"] for i in ast.literal_eval(str(d)) if i != "INFEAS"]
        gms = [s for g in df["gm"] for s in ast.literal_eval(str(g))]
        drop_freq = pd.Series(drops).value_counts()
        gm_freq = pd.Series(gms).value_counts()
        print(f"\n== {tag.upper()} heterogeneity (R={len(df)}, S={S_SAA}) ==")
        print(f"  cost of 90% assurance: {ac.mean():,.1f} +/- {ci:,.1f} MPHP/yr (95% CI) "
              f"[min {ac.min():,.1f}, max {ac.max():,.1f}]")
        print(f"  compliance (risk-neutral SP): {df.comp_sp.mean()*100:.0f}% mean")
        print(f"  gas-module frequency: {dict(gm_freq)}")
        print(f"  LGU-drop frequency (of {len(df)} reps): {dict(drop_freq) if len(drop_freq) else 'none'}\n")

def benchmark():
    # JOB 2 -- deterministic over-promise table (one representative set per regime)
    print("== BENCHMARK: deterministic over-promise ==")
    for c_lgu, tag in [(60.0, "mild"), (15.0, "strong")]:
        M.rng = np.random.default_rng(99_000 + int(c_lgu))
        scen = M.gen_scen(c_lgu, s=S_SAA)
        mo = M.evaluate(M.CENTRAL, M.TAU)
        det = [{"r": {i: mo["recovery"] for i in M.LGUS}, "g": {i: mo["fuelgas"]/1000 for i in M.LGUS},
                "rev": {i: mo["revenue_php_per_t"] for i in M.LGUS}, "W": dict(M.W0)}]
        m_ev = M.solve(M.build(det), gap=1e-3)
        promised = 1.0 if pe.value(m_ev.short[0]) < 1e-3 else 0.0
        fix = {"z": {(s,k): round(pe.value(m_ev.z[s,k])) for s in M.SITES for k in M.ALLOWED[s]},
               "gm": {s: round(pe.value(m_ev.gm[s])) for s in M.SITES},
               "ct": {i: round(pe.value(m_ev.ct[i])) for i in M.LGUS}}
        m_r = M.solve(M.build(scen, fix=fix), gap=1e-3)
        realized = 1 - sum(round(pe.value(m_r.b[w])) for w in range(S_SAA)) / S_SAA
        print(f"  [{tag}] deterministic design promises {promised*100:.0f}% compliance; "
              f"realized {realized*100:.0f}% -> over-promise {promised*100-realized*100:.0f} pp")

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "batch":
        c = 60.0 if sys.argv[2] == "mild" else 15.0
        run_batch(c, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif sys.argv[1] == "aggregate":
        aggregate()
    elif sys.argv[1] == "benchmark":
        benchmark()
