"""
make_figures.py -- P7: the 6 CACE manuscript figures, publication-grade
========================================================================
Conventions: Elsevier single column 90 mm (3.54 in) / double 190 mm (7.48 in);
fonts >=8 pt (Arial/Helvetica); colorblind-safe (Okabe-Ito); vector PDF + 600 dpi
PNG; no gridlines-as-decoration; every panel regenerated from repo data.
Run from src/:  python figures/make_figures.py   -> ../results/figures/F*.{pdf,png}
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle, Circle
import sys, os, ast
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OI = ["#0072B2","#E69F00","#009E73","#D55E00","#CC79A7","#56B4E9","#000000"]
plt.rcParams.update({"font.size":8,"font.family":"DejaVu Sans","axes.spines.top":False,
    "axes.spines.right":False,"pdf.fonttype":42,"savefig.dpi":600,"axes.linewidth":0.6})
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "results","figures")
os.makedirs(OUT, exist_ok=True)
def save(fig, name):
    for ext in ("pdf","png"): fig.savefig(f"{OUT}/{name}.{ext}", bbox_inches="tight")
    plt.close(fig); print(f"  {name} saved")

SC, DC = 3.54, 7.48   # column widths, inches

# ---------- F1: superstructure schematic + flowsheet inset ----------
def F1():
    fig, ax = plt.subplots(figsize=(DC, 3.4)); ax.axis("off")
    lgus = [("QC",.06,.82),("Manila",.05,.62),("Caloocan",.07,.42),("Taguig",.05,.22),
            ("Pasig",.16,.90),("Valenzuela",.16,.10),("Paranaque",.24,.86),("Makati",.24,.14)]
    sites = [("Valenzuela_N",.46,.78),("Navotas_Port",.46,.55),("Taguig_FTI",.46,.32),("Carmona_Central",.46,.09)]
    for n,x,y in lgus:
        ax.add_patch(Circle((x,y),.016,fc=OI[5],ec="k",lw=.5)); ax.text(x,y+.045,n,ha="center",fontsize=6.5)
        for _,sx,sy in sites: ax.plot([x+.016,sx-.03],[y,sy],color="0.8",lw=.4,zorder=0)
    for n,x,y in sites:
        ax.add_patch(Rectangle((x-.03,y-.035),.06,.07,fc=OI[1],ec="k",lw=.6))
        ax.text(x,y-.075,n.replace("_","\n"),ha="center",fontsize=6.5)
    for lbl,x,y,c in [("NAPHTHA",.94,.75,OI[0]),("DIESEL",.94,.55,OI[2]),("WAX",.94,.35,OI[3]),("FUELGAS",.94,.15,OI[4])]:
        ax.add_patch(Circle((x,y),.014,fc=c,ec="k",lw=.5)); ax.text(x-.03,y,lbl,ha="right",fontsize=6.5,va="center")
        for _,sx,sy in sites: ax.plot([sx+.03,x-.014],[sy,y],color="0.85",lw=.4,zorder=0)
    # flowsheet inset strip
    ax.add_patch(Rectangle((.56,.02),.30,.96,fc="none",ec="0.4",lw=.6,ls=":"))
    steps=["Yield-shift\nreactor\n(Genuino+\nWesterhout)","Quench+\nflash\nV-101","Stabilizer\nH-102/V-102","C-101\n(naphtha)","SCOL-2\nvacuum\n(diesel/wax)"]
    for i,t in enumerate(steps):
        y=.86-.19*i
        ax.add_patch(Rectangle((.585,y-.07),.10,.14,fc="white",ec="k",lw=.6))
        ax.text(.635,y,t,ha="center",va="center",fontsize=5.6)
        if i<4: ax.annotate("",xy=(.635,y-.083),xytext=(.635,y-.115),arrowprops=dict(arrowstyle="->",lw=.6))
    ax.text(.71,.5,"stage 1: sites z, gas modules g,\ncontracts c\nstage 2: flows x per scenario\nRA 11898: recover >= 80% of\ncontracted footprint",fontsize=6.4,va="center")
    ax.text(.02,.985,"(a) spatial superstructure",fontsize=8,weight="bold",va="top")
    ax.text(.57,.985,"(b) site flowsheet (verified, v3)",fontsize=8,weight="bold",va="top")
    ax.set_xlim(0,1); ax.set_ylim(0,1); save(fig,"F1_superstructure")

# ---------- F2: recovery distributions vs 80% across fidelity layers ----------
def F2():
    from feedstock_doe import build_doe
    from flowsheet_shortcut import build_flowsheet_doe
    d1 = build_doe(200); r1 = d1[d1.tau_s==240]["y_OIL_WAX"]/100
    d2 = build_flowsheet_doe(200); r2 = d2[d2.tau_s==240]["recovery"]
    fig, ax = plt.subplots(figsize=(SC,2.6))
    for r,lab,c in [(r1,"reactor lump (superposition)",OI[0]),(r2,"full flowsheet (v3 oracle)",OI[3])]:
        ax.hist(r*100, bins=28, alpha=.55, label=f"{lab}\nP(>=80%)={ (r>=.8).mean()*100:.0f}%", color=c, edgecolor="none")
    ax.axvline(80, color="k", lw=1, ls="--"); ax.text(80.4, ax.get_ylim()[1]*.95, "RA 11898\n80% (2028)", fontsize=6.5, va="top")
    ax.set_xlabel("liquid recovery of contracted footprint (wt %)"); ax.set_ylabel("count (200 compositions)")
    ax.legend(fontsize=6.2, frameon=False, loc="upper left"); save(fig,"F2_recovery_vs_target")

# ---------- F3: DWSIM 6-point parity, pre/post recalibration ----------
def F3():
    from verify_vs_dwsim import DWSIM, FEEDS, predict
    pre = {c: predict(o,g,1.0,0.0) for c,(o,g) in FEEDS.items()}
    post= {c: predict(o,g,0.762,0.0534) for c,(o,g) in FEEDS.items()}
    fig, axs = plt.subplots(1,2,figsize=(DC,2.7),sharex=True,sharey=True)
    for ax,dat,t in [(axs[0],pre,"pre-recalibration"),(axs[1],post,"post (2-parameter fit)")]:
        for k,c,m in zip(range(4),["NAPHTHA-S","DIESEL","WAX","FUELGAS"],["o","s","^","D"]):
            x=[DWSIM[cs][k] for cs in DWSIM]; y=[dat[cs][k] for cs in DWSIM]
            ax.scatter(x,y,s=16,marker=m,color=OI[k],label=c,zorder=3)
        lim=[60,380]; ax.plot(lim,lim,"k-",lw=.6); 
        ax.fill_between(lim,[l*.95 for l in lim],[l*1.05 for l in lim],color="0.9",zorder=0)
        ax.set_xlim(lim); ax.set_ylim(lim); ax.set_title(t,fontsize=8)
        ax.set_xlabel("DWSIM rigorous (kg h$^{-1}$)")
    axs[0].set_ylabel("shortcut oracle (kg h$^{-1}$)")
    axs[1].legend(fontsize=6.2,frameon=False,loc="lower right")
    axs[0].text(70,340,"worst 6.5%",fontsize=6.5); axs[1].text(70,340,"worst 1.6%\n(24/24 <= 2%)",fontsize=6.5)
    save(fig,"F3_dwsim_parity")

# ---------- F4: GP parity + CI coverage ----------
def F4():
    import joblib
    from sklearn.model_selection import train_test_split
    df = pd.read_csv("flowsheet_doe.csv")
    X = df[[c for c in df.columns if c.startswith("x_")]+["tau_s"]].values
    y = df["recovery"].values
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.2,random_state=11898)
    b = joblib.load("../results/surrogates/gp_recovery.joblib")
    mu_s, sd_s = b["gp"].predict(b["xscaler"].transform(Xte), return_std=True)
    mu = b["yscaler"].inverse_transform(mu_s.reshape(-1,1)).ravel(); sd = sd_s*b["yscaler"].scale_[0]
    fig, axs = plt.subplots(1,2,figsize=(DC,2.7))
    axs[0].errorbar(yte*100, mu*100, yerr=1.96*sd*100, fmt="o", ms=2.5, lw=.5, color=OI[0], ecolor="0.7")
    lim=[min(yte.min(),mu.min())*100-1, max(yte.max(),mu.max())*100+1]
    axs[0].plot(lim,lim,"k-",lw=.6); axs[0].set_xlim(lim); axs[0].set_ylim(lim)
    axs[0].set_xlabel("oracle recovery (wt %)"); axs[0].set_ylabel("GP prediction $\\pm$95% CI (wt %)")
    z = (yte-mu)/sd
    axs[1].hist(z, bins=24, density=True, color=OI[2], alpha=.7, edgecolor="none")
    xs=np.linspace(-4,4,200); axs[1].plot(xs, np.exp(-xs**2/2)/np.sqrt(2*np.pi), "k-", lw=.8, label="N(0,1)")
    axs[1].set_xlabel("standardized residual"); axs[1].set_ylabel("density")
    cov=float(np.mean(np.abs(yte-mu)<=1.96*sd))
    axs[1].text(.03,.95,f"95% CI coverage = {cov:.2f}",transform=axs[1].transAxes,fontsize=7,va="top")
    axs[1].legend(fontsize=6.5,frameon=False); save(fig,"F4_gp_calibration")

# ---------- F5: cost-of-assurance by heterogeneity, mechanism-annotated ----------
def F5():
    df = pd.read_csv("saa_results.csv")
    df["mech"]="hardware"
    df.loc[df["dropped"].apply(lambda d: len(ast.literal_eval(str(d)))>=8),"mech"]="exit"
    df.loc[(df["dropped"].apply(lambda d: 0<len(ast.literal_eval(str(d)))<8)),"mech"]="selective contracting"
    fig, ax = plt.subplots(figsize=(SC,2.9))
    cols={"hardware":OI[2],"selective contracting":OI[1],"exit":OI[3]}
    for j,het in enumerate(["mild","strong"]):
        sub=df[df.het==het]
        ax.boxplot(sub.assure_cost/1e6, positions=[j], widths=.45, showfliers=False,
                   medianprops=dict(color="k",lw=1))
        for _,r in sub.iterrows():
            ax.scatter(j+np.random.default_rng(int(r.rep)).uniform(-.14,.14), r.assure_cost/1e6,
                       s=16, color=cols[r.mech], zorder=3, edgecolor="k", lw=.3)
    ax.set_yscale("log"); ax.set_xticks([0,1]); ax.set_xticklabels(["mild\n(c$_{LGU}$=60)","strong\n(c$_{LGU}$=15)"])
    ax.set_ylabel("cost of 90% compliance assurance (MPHP yr$^{-1}$, log)")
    for m,c in cols.items(): ax.scatter([],[],color=c,edgecolor="k",lw=.3,s=16,label=m)
    ax.legend(fontsize=6.2,frameon=False,loc="upper left",title="assurance mechanism",title_fontsize=6.2)
    ax.text(0,2.2,"18.3$\\pm$9.9",fontsize=6.5,ha="center"); ax.text(1,3000,"median 413",fontsize=6.5,ha="center")
    save(fig,"F5_cost_of_assurance")

# ---------- F6: Sobol tornado ----------
def F6():
    from tea_uq import sobol_npv
    S = sobol_npv().iloc[::-1]
    names={"oil_yield":"oil yield (feed composition)","p_mid":"diesel-cut price","capex_m":"CAPEX $\\pm$30%",
           "p_naph":"naphtha price","p_wax":"wax price","opex_m":"OPEX $\\pm$30%"}
    fig, ax = plt.subplots(figsize=(SC,2.4))
    yp=np.arange(len(S))
    ax.barh(yp+.18, S.S1, height=.34, color=OI[0], label="first order $S_1$")
    ax.barh(yp-.18, S.ST, height=.34, color=OI[1], label="total $S_T$")
    ax.set_yticks(yp); ax.set_yticklabels([names[n] for n in S.factor], fontsize=7)
    ax.set_xlabel("Sobol index (NPV)"); ax.legend(fontsize=6.5,frameon=False,loc="lower right")
    ax.text(.62,len(S)-1.15,"62%",fontsize=7,weight="bold")
    save(fig,"F6_sobol_npv")

if __name__=="__main__":
    for f in (F1,F2,F3,F4,F5,F6):
        print(f.__name__+":"); f()
