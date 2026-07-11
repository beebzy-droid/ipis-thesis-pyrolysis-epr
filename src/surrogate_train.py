"""
surrogate_train.py  --  P4: GP + LightGBM surrogates of the flowsheet response
===============================================================================
Repo: ipis-thesis-pyrolysis-epr (W1/A)

Trains and cross-validates two surrogate families on the flowsheet DOE
(flowsheet_shortcut.py oracle, calibrated to the verified DWSIM point):

  GP (Gaussian process, anisotropic RBF + white noise)  -> the thesis's
     Bayesian layer: predictive mean AND variance; variance feeds the
     uncertainty-aware optimization (chance constraints / risk terms).
  LightGBM -> fast benchmark; no native UQ (quantile mode noted).

Inputs  (9-dim): 8 composition fractions + tau_s
Outputs (4): liquid_L_per_t, recovery, Q_heat_kW_per_tph, revenue_php_per_t

Protocol: 80/20 train/test split (seed 11898), standardized inputs/outputs,
metrics = R2, RMSE, MAE; GP additionally checked for 95%-CI coverage
(calibration of the UQ, not just accuracy -- a reviewer will ask).
Persist: results/surrogates/*.joblib (gitignored; regenerate from src).
"""
from __future__ import annotations
import numpy as np, pandas as pd, joblib, os, time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import lightgbm as lgb

SEED = 11898
INPUTS = ["x_PE_rigid","x_PE_film","x_PP_rigid","x_PP_film",
          "x_PS_cat","x_PET_cat","x_MULTILAYER","x_CLOGGED","tau_s"]
OUTPUTS = ["liquid_L_per_t","recovery","Q_heat_kW_per_tph","revenue_php_per_t"]

def train_all(doe_csv: str = "flowsheet_doe.csv", outdir: str = "../results/surrogates"):
    df = pd.read_csv(doe_csv)
    X = df[INPUTS].values
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for target in OUTPUTS:
        y = df[target].values
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=SEED)
        xs, ys = StandardScaler().fit(Xtr), StandardScaler().fit(ytr.reshape(-1,1))
        Xtr_s, Xte_s = xs.transform(Xtr), xs.transform(Xte)
        ytr_s = ys.transform(ytr.reshape(-1,1)).ravel()

        # --- GP: anisotropic RBF (one length-scale per input) + white noise ---
        kern = ConstantKernel(1.0) * RBF(length_scale=np.ones(len(INPUTS))) \
               + WhiteKernel(noise_level=1e-4, noise_level_bounds=(1e-8, 1e-1))
        t0 = time.time()
        gp = GaussianProcessRegressor(kernel=kern, normalize_y=False,
                                      n_restarts_optimizer=2, random_state=SEED)
        gp.fit(Xtr_s, ytr_s)
        mu_s, sd_s = gp.predict(Xte_s, return_std=True)
        mu = ys.inverse_transform(mu_s.reshape(-1,1)).ravel()
        sd = sd_s * ys.scale_[0]
        gp_t = time.time() - t0
        cover = float(np.mean(np.abs(yte - mu) <= 1.96 * sd))       # 95%-CI coverage

        # --- LightGBM benchmark ---
        t0 = time.time()
        gbm = lgb.LGBMRegressor(n_estimators=600, learning_rate=0.05,
                                num_leaves=31, random_state=SEED, verbose=-1)
        gbm.fit(Xtr, ytr)
        yg = gbm.predict(Xte)
        gb_t = time.time() - t0

        for name, pred, extra in (("GP", mu, f"95%CI coverage={cover:.2f}, fit {gp_t:.1f}s"),
                                  ("LightGBM", yg, f"fit {gb_t:.1f}s")):
            rows.append({"target": target, "model": name,
                         "R2": r2_score(yte, pred),
                         "RMSE": float(np.sqrt(mean_squared_error(yte, pred))),
                         "MAE": mean_absolute_error(yte, pred),
                         "note": extra})
        joblib.dump({"gp": gp, "xscaler": xs, "yscaler": ys, "inputs": INPUTS},
                    f"{outdir}/gp_{target}.joblib")
        joblib.dump(gbm, f"{outdir}/lgbm_{target}.joblib")

    rep = pd.DataFrame(rows)
    rep.to_csv(f"{outdir}/surrogate_report.csv", index=False)
    print(rep.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
    print(f"\nModels persisted to {outdir}/ (gitignored; regenerate via `python surrogate_train.py`)")
    return rep

if __name__ == "__main__":
    train_all()
