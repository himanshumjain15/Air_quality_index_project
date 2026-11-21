"""Linear regression, logistic regression and AdaBoost on the air quality data (Part 4).

Same rows and the same training / testing split as Part 3 (row ids are read from dt_train.csv and dt_test.csv).
All tuning (regularization, probability cut-off, boosting rounds, learning rate, base-tree depth) uses 5-fold
cross-validation INSIDE the training set. The testing set is used once, for the final chosen models.

Targets
  linear regression : daily mean PM2.5 (numeric)
  logistic regression: Unhealthy day (US AQI >= 101) yes / no (two-class label)
  AdaBoost          : AQI group Good / Moderate / Unhealthy (same label as Part 3, for a fair comparison)

Input : data/clean/daily_city_air_weather_clean.csv, nb_dt_labeled_dataset.csv, dt_train.csv, dt_test.csv,
        data/raw/cities_reference.csv
Output: data/clean/reg_*.csv, ada_*.csv, reg_ada_results.json, images/reg_*.png, images/ada_*.png

Run:  python code/07_regression_adaboost.py
Packages: pandas, numpy, scipy, scikit-learn, joblib, matplotlib, seaborn (Python 3.10+).
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from joblib import Parallel, delayed
from scipy.stats import binomtest
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import KBinsDiscretizer, StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, IMG = ROOT / "data" / "raw", ROOT / "data" / "clean", ROOT / "images"
sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
SEED = 42
BLUE, ORANGE, RED, GREEN, GREY = "#2a6fdb", "#f28e2b", "#d1495b", "#2e9e5b", "#6b7280"
CLASSES = ["Good", "Moderate", "Unhealthy"]
CCOL = {"Good": GREEN, "Moderate": "#f2c94c", "Unhealthy": RED}
RES = {}
CV = StratifiedKFold(5, shuffle=True, random_state=SEED)


def save(fig, name, dpi=130):
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def table_image(df, name, title, highlight=None, nrows=8, ncols=10):
    sample = df.head(nrows).iloc[:, :ncols].copy()
    for c in sample.columns:
        if sample[c].dtype.kind == "f":
            sample[c] = sample[c].round(2)
    fig, ax = plt.subplots(figsize=(min(2 + 1.3 * sample.shape[1], 16), 0.5 * len(sample) + 1.3))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    t = ax.table(cellText=sample.astype(str).values, colLabels=sample.columns, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.scale(1, 1.4)
    for (r, c), cell in t.get_celld().items():
        hl = highlight is not None and sample.columns[c] in highlight
        if r == 0:
            cell.set_facecolor("#fde3c8" if hl else "#e8eefc")
            cell.set_text_props(fontweight="bold")
        elif hl:
            cell.set_facecolor("#fff4e6")
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=130, bbox_inches="tight")
    plt.close(fig)


def cm_panel(ax, cm, labels, title):
    cm = np.array(cm)
    pct = cm / cm.sum(axis=1, keepdims=True).clip(min=1) * 100
    ax.imshow(pct, cmap="Blues", vmin=0, vmax=100)
    k = len(labels)
    for i in range(k):
        for j in range(k):
            ax.text(j, i, f"{cm[i, j]:,}\n({pct[i, j]:.0f}%)", ha="center", va="center", fontsize=9,
                    color="white" if pct[i, j] > 55 else "black")
    ax.set_xticks(range(k))
    ax.set_yticks(range(k))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(title, fontsize=10)
    ax.grid(False)


# ============================================================================ data
day = pd.read_csv(CLEAN / "daily_city_air_weather_clean.csv", parse_dates=["date"])
day.insert(0, "row_id", np.arange(len(day)))
cities = pd.read_csv(RAW / "cities_reference.csv")[["city", "state", "latitude", "longitude"]]
n0 = len(day)
day = day.merge(cities, on=["city", "state"], how="left")
assert len(day) == n0
lab = pd.read_csv(CLEAN / "nb_dt_labeled_dataset.csv")[["row_id", "label"]]
day = day.merge(lab, on="row_id", how="left")
assert day["label"].notna().all()
tr_ids = pd.read_csv(CLEAN / "dt_train.csv")["row_id"]
te_ids = pd.read_csv(CLEAN / "dt_test.csv")["row_id"]
assert len(set(tr_ids) & set(te_ids)) == 0
day["temp_range"] = day["temp_max"] - day["temp_min"]
for _s in ["Winter", "Spring", "Summer"]:      # Fall is the reference season (cleanest on average)
    day[f"season_{_s}"] = (day["season"] == _s).astype(int)
day["unhealthy"] = (day["aqi_max"] >= 101).astype(int)
train = day[day["row_id"].isin(tr_ids)].reset_index(drop=True)
test = day[day["row_id"].isin(te_ids)].reset_index(drop=True)
RES["split"] = {"train_rows": int(len(train)), "test_rows": int(len(test)),
                "overlap_rows": int(len(set(train["row_id"]) & set(test["row_id"])))}
RES["same_split_as_part3"] = True
RES["corr_temps"] = {"mean_max": float(day["temp_mean"].corr(day["temp_max"])),
                     "mean_min": float(day["temp_mean"].corr(day["temp_min"])),
                     "max_min": float(day["temp_max"].corr(day["temp_min"]))}
tr_t, te_t = day[day["month"] <= 9].reset_index(drop=True), day[day["month"] >= 10].reset_index(drop=True)
RES["time_holdout_rows"] = {"train": int(len(tr_t)), "test": int(len(te_t))}

# ============================================================================ REGRESSION
RFEAT = ["temp_mean", "temp_range", "precip_mm", "wind_max", "solar_rad", "season_Winter", "season_Spring", "season_Summer"]
R5 = RFEAT[:5]
RLOC = RFEAT + ["latitude", "longitude"]
RES["reg_features"] = RFEAT

reg_cols = ["row_id", "city", "date"] + RFEAT + ["pm2_5", "unhealthy"]
for name, df in [("reg_dataset", day), ("reg_train", train), ("reg_test", test)]:
    out = df[reg_cols].copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(CLEAN / f"{name}.csv", index=False)
samp = day[reg_cols].sample(8, random_state=SEED).assign(date=lambda x: x["date"].dt.strftime("%Y-%m-%d"))
table_image(samp[["city", "date", "temp_mean", "temp_range", "precip_mm", "wind_max", "solar_rad", "pm2_5", "unhealthy"]],
            "reg_01_data_sample.png", "Sample of the regression data: weather inputs, numeric target (pm2_5), two-class target (unhealthy)",
            highlight=["pm2_5", "unhealthy"], ncols=9)
tcols = ["city", "temp_mean", "temp_range", "wind_max", "solar_rad", "pm2_5", "unhealthy"]
table_image(train[tcols].head(8), "reg_02_train_sample.png", f"Training set ({len(train):,} rows): first rows",
            highlight=["pm2_5", "unhealthy"])
table_image(test[tcols].head(8), "reg_03_test_sample.png", f"Testing set ({len(test):,} rows): first rows",
            highlight=["pm2_5", "unhealthy"])

# ---------------------------------------------------------------- linear regression
ytr_r, yte_r = train["pm2_5"].to_numpy(), test["pm2_5"].to_numpy()


def reg_metrics(y, p, base_mean):
    return {"rmse": float(mean_squared_error(y, p) ** 0.5), "mae": float(mean_absolute_error(y, p)),
            "r2": float(r2_score(y, p)),
            "baseline_rmse": float(mean_squared_error(y, np.full_like(y, base_mean, dtype=float)) ** 0.5),
            "baseline_mae": float(mean_absolute_error(y, np.full_like(y, base_mean, dtype=float)))}


RES["pm25"] = {"train_mean": float(ytr_r.mean()), "train_std": float(ytr_r.std()), "test_mean": float(yte_r.mean())}
RES["linear"] = {}
lin_sets = {"Weather only (5 inputs)": R5, "Weather and season (8 inputs, main model)": RFEAT,
            "Weather, season and location (10 inputs)": RLOC}
lin_models = {}
for name, feats in lin_sets.items():
    m = LinearRegression().fit(train[feats], ytr_r)
    lin_models[name] = (m, feats)
    r = reg_metrics(yte_r, m.predict(test[feats]), ytr_r.mean())
    r["cv_r2_train"] = float(cross_val_score(LinearRegression(), train[feats], ytr_r, cv=5, scoring="r2").mean())
    r["train_r2"] = float(m.score(train[feats], ytr_r))
    RES["linear"][name] = r
main_name = "Weather and season (8 inputs, main model)"
lm, lfe = lin_models[main_name]
RES["linear_main"] = main_name
RES["linear_coefficients"] = dict(zip(lfe, map(float, lm.coef_)))
RES["linear_intercept"] = float(lm.intercept_)
sd = train[lfe].std()
sd = sd.where(~sd.index.str.startswith("season_"), 1.0)
RES["linear_std_coefficients"] = {f: float(c * sd[f]) for f, c in zip(lfe, lm.coef_)}
RES["feature_sd"] = {f: float(sd[f]) for f in lfe}
rng = np.random.default_rng(SEED)
boots = []
for _ in range(300):
    idx = rng.integers(0, len(train), len(train))
    mb = LinearRegression().fit(train.loc[idx, lfe], ytr_r[idx])
    boots.append(mb.coef_ * sd[lfe].to_numpy())
boots = np.array(boots)
RES["linear_std_coef_ci"] = {f: [float(np.percentile(boots[:, i], 2.5)), float(np.percentile(boots[:, i], 97.5))]
                             for i, f in enumerate(lfe)}
# time-based holdout
mt = LinearRegression().fit(tr_t[lfe], tr_t["pm2_5"])
RES["linear_time_holdout"] = reg_metrics(te_t["pm2_5"].to_numpy(), mt.predict(te_t[lfe]), tr_t["pm2_5"].mean())

pred = lm.predict(test[lfe])
fig, ax = plt.subplots(figsize=(6.6, 5.6))
hb = ax.hexbin(pred, yte_r, gridsize=40, cmap="Blues", mincnt=1, bins="log", extent=(0, 18, 0, 45))
fig.colorbar(hb, ax=ax, label="Test days (log scale)")
lim = [0, 18]
ax.plot(lim, lim, color=RED, ls="--", lw=1.5, label="Perfect prediction")
bins = np.linspace(pred.min(), pred.max(), 12)
mid = (bins[:-1] + bins[1:]) / 2
avg = [yte_r[(pred >= a) & (pred < b)].mean() if ((pred >= a) & (pred < b)).any() else np.nan for a, b in zip(bins[:-1], bins[1:])]
ax.plot(mid, avg, color=ORANGE, lw=2.5, marker="o", label="Average actual value per predicted bin")
ax.set_xlim(0, 18)
ax.set_ylim(0, 45)
ax.set_xlabel("Predicted PM2.5 (ug/m3)")
ax.set_ylabel("Actual PM2.5 (ug/m3)")
r = RES["linear"][main_name]
ax.set_title(f"Linear regression on the testing set\nRMSE {r['rmse']:.2f}, MAE {r['mae']:.2f}, R-squared {r['r2']:.2f}", fontsize=11)
ax.legend(loc="upper left", fontsize=8)
save(fig, "reg_04_predicted_vs_actual.png")

fig, ax = plt.subplots(figsize=(8.8, 5.0))
order = sorted(lfe, key=lambda f: RES["linear_std_coefficients"][f])
vals = [RES["linear_std_coefficients"][f] for f in order]
lo = [RES["linear_std_coefficients"][f] - RES["linear_std_coef_ci"][f][0] for f in order]
hi = [RES["linear_std_coef_ci"][f][1] - RES["linear_std_coefficients"][f] for f in order]
lbl = [f if f.startswith("season_") else f"{f}\n(+1 SD = {sd[f]:.1f})" for f in order]
ax.barh(lbl, vals, xerr=[lo, hi], color=[BLUE if v > 0 else ORANGE for v in vals], capsize=3)
ax.axvline(0, color="k", lw=0.8)
ax.set_xlabel("Change in predicted PM2.5 (ug/m3)")
ax.set_title("What the linear regression learned\nNumbers: +1 standard deviation. Seasons: compared with Fall. Whiskers: 95% bootstrap interval", fontsize=10)
ax.grid(axis="y", visible=False)
save(fig, "reg_05_coefficients.png")

# ---------------------------------------------------------------- logistic regression
ytr_c, yte_c = train["unhealthy"].to_numpy(), test["unhealthy"].to_numpy()
RES["unhealthy"] = {"train_share": float(ytr_c.mean()), "test_share": float(yte_c.mean()),
                    "test_positives": int(yte_c.sum()), "baseline_accuracy": float(1 - yte_c.mean())}


def bin_metrics(y, p, proba):
    cm = confusion_matrix(y, p, labels=[0, 1])
    return {"accuracy": float(accuracy_score(y, p)), "precision": float(precision_score(y, p, zero_division=0)),
            "recall": float(recall_score(y, p, zero_division=0)), "f1": float(f1_score(y, p, zero_division=0)),
            "auc": float(roc_auc_score(y, proba)), "confusion": cm.tolist(), "predicted_positive": int(p.sum())}


def best_threshold(y, proba):
    grid = np.arange(0.02, 0.60, 0.005)
    f = [f1_score(y, (proba >= t).astype(int), zero_division=0) for t in grid]
    return float(grid[int(np.argmax(f))])


scaler = StandardScaler().fit(train[RFEAT])
Atr, Ate = scaler.transform(train[RFEAT]), scaler.transform(test[RFEAT])
gs = GridSearchCV(LogisticRegression(max_iter=5000), {"C": [0.001, 0.01, 0.1, 1, 10, 100]}, cv=CV,
                  scoring="neg_log_loss").fit(Atr, ytr_c)
C_BEST = float(gs.best_params_["C"])
RES["logistic_C"] = C_BEST
RES["logistic_C_cv_logloss"] = {str(c): float(-s) for c, s in zip(gs.cv_results_["param_C"], gs.cv_results_["mean_test_score"])}
lg = LogisticRegression(C=C_BEST, max_iter=5000).fit(Atr, ytr_c)
lgb = LogisticRegression(C=C_BEST, max_iter=5000, class_weight="balanced").fit(Atr, ytr_c)
oof = cross_val_predict(LogisticRegression(C=C_BEST, max_iter=5000), Atr, ytr_c, cv=CV, method="predict_proba")[:, 1]
THR_LOG = best_threshold(ytr_c, oof)
pl = lg.predict_proba(Ate)[:, 1]
plb = lgb.predict_proba(Ate)[:, 1]
RES["logistic"] = {
    "Logistic, default cut-off 0.5": bin_metrics(yte_c, (pl >= 0.5).astype(int), pl),
    "Logistic, balanced class weights": bin_metrics(yte_c, (plb >= 0.5).astype(int), plb),
    f"Logistic, cut-off tuned by cross-validation ({THR_LOG:.3f})": bin_metrics(yte_c, (pl >= THR_LOG).astype(int), pl),
}
RES["logistic_threshold"] = THR_LOG
# coefficients: standardized fit converted to raw units
sdv_raw = scaler.scale_
coef_raw = lg.coef_[0] / sdv_raw
sdv = np.where([f.startswith("season_") for f in RFEAT], 1.0, sdv_raw)
RES["logistic_coef_raw"] = dict(zip(RFEAT, map(float, coef_raw)))
RES["logistic_step"] = dict(zip(RFEAT, map(float, sdv)))
RES["logistic_odds_ratio_per_unit"] = {f: float(np.exp(c)) for f, c in zip(RFEAT, coef_raw)}
RES["logistic_odds_ratio_per_sd"] = {f: float(np.exp(c * s)) for f, c, s in zip(RFEAT, coef_raw, sdv)}
RES["logistic_intercept_std"] = float(lg.intercept_[0])
boots = []
for _ in range(300):
    idx = rng.integers(0, len(train), len(train))
    mb = LogisticRegression(C=C_BEST, max_iter=5000).fit(Atr[idx], ytr_c[idx])
    boots.append(mb.coef_[0])
boots = np.array(boots)
RES["logistic_or_per_sd_ci"] = {f: [float(np.exp(np.percentile(boots[:, i] / sdv_raw[i] * sdv[i], 2.5))),
                                    float(np.exp(np.percentile(boots[:, i] / sdv_raw[i] * sdv[i], 97.5)))]
                                for i, f in enumerate(RFEAT)}
# no-season and location variants (AUC only)
RES["logistic_variants_auc"] = {}
for nm, feats in [("Weather only (5 inputs)", R5), ("Weather and season (8 inputs)", RFEAT), ("Weather, season and location (10 inputs)", RLOC)]:
    sc = StandardScaler().fit(train[feats])
    mm = LogisticRegression(C=C_BEST, max_iter=5000).fit(sc.transform(train[feats]), ytr_c)
    RES["logistic_variants_auc"][nm] = float(roc_auc_score(yte_c, mm.predict_proba(sc.transform(test[feats]))[:, 1]))
# time-based holdout
sct = StandardScaler().fit(tr_t[RFEAT])
mt = LogisticRegression(C=C_BEST, max_iter=5000).fit(sct.transform(tr_t[RFEAT]), tr_t["unhealthy"])
pt = mt.predict_proba(sct.transform(te_t[RFEAT]))[:, 1]
RES["logistic_time_holdout"] = {"test_positives": int(te_t["unhealthy"].sum()), "test_rows": int(len(te_t)),
                                "auc": float(roc_auc_score(te_t["unhealthy"], pt)),
                                "accuracy_default": float(accuracy_score(te_t["unhealthy"], (pt >= 0.5).astype(int))),
                                "baseline_accuracy": float(1 - te_t["unhealthy"].mean())}

# ---------------------------------------------------------------- naive bayes on the same two-class label
NBF = ["temp_mean", "temp_max", "temp_min", "precip_mm", "wind_max", "solar_rad", "month"]


def nb_pipe():
    return make_pipeline(KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile",
                                          quantile_method="averaged_inverted_cdf"), MultinomialNB())


nb = nb_pipe().fit(train[NBF], ytr_c)
pn = nb.predict_proba(test[NBF])[:, 1]
oof_nb = cross_val_predict(nb_pipe(), train[NBF], ytr_c, cv=CV, method="predict_proba")[:, 1]
THR_NB = best_threshold(ytr_c, oof_nb)
RES["nb_binary"] = {
    "Naive Bayes, default cut-off 0.5": bin_metrics(yte_c, (pn >= 0.5).astype(int), pn),
    f"Naive Bayes, cut-off tuned by cross-validation ({THR_NB:.3f})": bin_metrics(yte_c, (pn >= THR_NB).astype(int), pn),
}
RES["nb_threshold"] = THR_NB
# time holdout NB
nbt = nb_pipe().fit(tr_t[NBF], tr_t["unhealthy"])
pnt = nbt.predict_proba(te_t[NBF])[:, 1]
RES["nb_time_holdout_auc"] = float(roc_auc_score(te_t["unhealthy"], pnt))

# ---- figures: confusion matrices and ROC
fig, axes = plt.subplots(1, 4, figsize=(17, 4.5))
panels = [("Logistic, default cut-off 0.5", RES["logistic"]["Logistic, default cut-off 0.5"]),
          (f"Logistic, tuned cut-off {THR_LOG:.2f}", RES["logistic"][f"Logistic, cut-off tuned by cross-validation ({THR_LOG:.3f})"]),
          ("Naive Bayes, default cut-off 0.5", RES["nb_binary"]["Naive Bayes, default cut-off 0.5"]),
          (f"Naive Bayes, tuned cut-off {THR_NB:.2f}", RES["nb_binary"][f"Naive Bayes, cut-off tuned by cross-validation ({THR_NB:.3f})"])]
for ax, (ttl, r) in zip(axes, panels):
    cm_panel(ax, r["confusion"], ["Not unhealthy", "Unhealthy"],
             f"{ttl}\naccuracy {r['accuracy']:.1%}, recall {r['recall']:.0%}, precision {r['precision']:.0%}")
fig.suptitle("Unhealthy day or not: confusion matrices on the testing set (cells: count and share of the actual group)", fontsize=12, y=1.03)
save(fig, "reg_07_confusion_matrices.png")

fig, ax = plt.subplots(figsize=(6.2, 5.4))
for nm, pr, col in [("Logistic regression", pl, BLUE), ("Naive Bayes (binned)", pn, ORANGE)]:
    fpr, tpr, _ = roc_curve(yte_c, pr)
    ax.plot(fpr, tpr, color=col, lw=2.2, label=f"{nm} (AUC {roc_auc_score(yte_c, pr):.3f})")
ax.plot([0, 1], [0, 1], color=GREY, ls="--", label="Guessing (AUC 0.5)")
ax.set_xlabel("False alarm rate (share of non-unhealthy days flagged)")
ax.set_ylabel("Detection rate (share of unhealthy days found)")
ax.set_title("ROC curves: how well each method ranks days by risk", fontsize=11)
ax.legend(loc="lower right", fontsize=9)
save(fig, "reg_08_roc.png")

fig, ax = plt.subplots(figsize=(8.8, 5.0))
orr = sorted(RFEAT, key=lambda f: RES["logistic_odds_ratio_per_sd"][f])
v = [RES["logistic_odds_ratio_per_sd"][f] for f in orr]
lo = [RES["logistic_odds_ratio_per_sd"][f] - RES["logistic_or_per_sd_ci"][f][0] for f in orr]
hi = [RES["logistic_or_per_sd_ci"][f][1] - RES["logistic_odds_ratio_per_sd"][f] for f in orr]
lbl = [f if f.startswith("season_") else f"{f}\n(+1 SD = {RES['logistic_step'][f]:.1f})" for f in orr]
ax.barh(lbl, np.array(v) - 1, left=1, xerr=[lo, hi], color=[RED if x > 1 else BLUE for x in v], capsize=3)
ax.axvline(1, color="k", lw=0.8)
ax.set_xscale("log")
ax.set_xlabel("Odds ratio of an unhealthy day (1 = no effect)")
ax.set_title("What the logistic regression learned\nNumbers: +1 standard deviation. Seasons: compared with Fall. Whiskers: 95% bootstrap interval", fontsize=10)
ax.grid(axis="y", visible=False)
save(fig, "reg_09_odds_ratios.png")

# ---- overview figures
one = "solar_rad"
sl = LinearRegression().fit(train[[one]], ytr_r)
samp = train.sample(220, random_state=3)
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.scatter(samp[one], samp["pm2_5"], s=18, color=BLUE, alpha=0.5, label="Days (random sample)")
xs = np.linspace(train[one].min(), train[one].max(), 50)
ax.plot(xs, sl.predict(pd.DataFrame({one: xs})), color=RED, lw=2.5, label="Fitted line")
for _, rw in samp.head(18).iterrows():
    ax.plot([rw[one]] * 2, [rw["pm2_5"], sl.predict(pd.DataFrame({one: [rw[one]]}))[0]], color=ORANGE, lw=1.2)
ax.plot([], [], color=ORANGE, label="Residual = actual - predicted")
ax.set_ylim(0, 45)
ax.set_xlabel("Solar radiation (MJ/m2 per day)")
ax.set_ylabel("PM2.5 (ug/m3)")
ax.set_title(f"Linear regression with one input: PM2.5 = {sl.intercept_:.1f} + {sl.coef_[0]:.2f} x solar radiation", fontsize=11)
ax.legend(fontsize=8, loc="upper left")
save(fig, "reg_00a_linear_idea.png")
RES["one_input_linear"] = {"intercept": float(sl.intercept_), "slope": float(sl.coef_[0]),
                           "r2_train": float(sl.score(train[[one]], ytr_r))}

one = "temp_max"
sl2 = LogisticRegression(max_iter=2000).fit(train[[one]], ytr_c)
b0, b1 = float(sl2.intercept_[0]), float(sl2.coef_[0][0])
RES["one_input_logistic"] = {"b0": b0, "b1": b1, "feature": "temp_max"}
xs = np.linspace(-10, 47, 200)
z = b0 + b1 * xs
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
axes[0].plot(xs, z, color=BLUE, lw=2.5)
axes[0].axhline(0, color=GREY, ls=":")
axes[0].set_xlabel("Maximum daily temperature (C)")
axes[0].set_ylabel("Linear score z")
axes[0].set_title(f"Step 1: a linear score, z = {b0:.2f} + {b1:.2f} x temperature", fontsize=10)
axes[1].plot(xs, 1 / (1 + np.exp(-z)), color=RED, lw=2.5, label="Sigmoid: p = 1 / (1 + e^-z)")
bins = np.linspace(-10, 47, 14)
mid = (bins[:-1] + bins[1:]) / 2
share = [train.loc[(train[one] >= a) & (train[one] < b), "unhealthy"].mean() if ((train[one] >= a) & (train[one] < b)).sum() > 15 else np.nan
         for a, b in zip(bins[:-1], bins[1:])]
axes[1].scatter(mid, share, color=BLUE, s=40, zorder=5, label="Observed share of unhealthy days")
axes[1].axhline(0.5, color=GREY, ls="--")
axes[1].text(-9, 0.53, "cut-off 0.5: above = Unhealthy, below = not", fontsize=8.5, color=GREY)
axes[1].set_xlabel("Maximum daily temperature (C)")
axes[1].set_ylabel("Probability of an unhealthy day")
axes[1].set_ylim(-0.02, 1.02)
axes[1].set_title("Step 2: the sigmoid squeezes the score into a probability", fontsize=10)
axes[1].legend(fontsize=8, loc="upper left")
save(fig, "reg_00b_sigmoid.png")

fig, ax = plt.subplots(figsize=(13, 2.4))
ax.axis("off")
steps = [("Weather inputs\n(temperature,\nwind, sun, ...)", "#eef3fd"), ("Linear score\nz = b0 + b1x1\n+ b2x2 + ...", "#eef3fd"),
         ("Sigmoid\np = 1/(1 + e^-z)", "#fde9d6"), ("Probability\np, for example\n0.73", "#fde9d6"),
         ("Cut-off rule\nis p >= 0.5 ?", "#e6f4ea"), ("Class\nUnhealthy\nor not", "#e6f4ea")]
cx = [0.075 + i * 0.17 for i in range(len(steps))]
for i, (txt, col) in enumerate(steps):
    ax.text(cx[i], 0.5, txt, ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.5", fc=col, ec=GREY))
    if i < len(steps) - 1:
        ax.annotate("", xy=(cx[i + 1] - 0.062, 0.5), xytext=(cx[i] + 0.062, 0.5), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.6))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
save(fig, "reg_00c_logistic_pipeline.png")

# ============================================================================ ADABOOST
ANUM = ["temp_mean", "temp_max", "temp_min", "precip_mm", "wind_max", "solar_rad", "month"]
ACAT = ["season", "region"]
RES["ada_numeric"], RES["ada_categorical"] = ANUM, ACAT


def design(df, cols=None):
    X = pd.concat([df[ANUM].reset_index(drop=True), pd.get_dummies(df[ACAT]).astype(int).reset_index(drop=True)], axis=1)
    X.columns = [str(c) for c in X.columns]
    return X if cols is None else X.reindex(columns=cols, fill_value=0)


Xtr_a = design(train)
Xte_a = design(test, Xtr_a.columns)
ytr_a, yte_a = train["label"].to_numpy(), test["label"].to_numpy()
RES["ada_columns"] = list(Xtr_a.columns)
base_acc = float((yte_a == "Moderate").mean())
RES["ada_baseline_accuracy"] = base_acc

adaset = day[["row_id", "city", "date"] + ANUM + ACAT + ["label"]].copy()
adaset["date"] = adaset["date"].dt.strftime("%Y-%m-%d")
adaset.to_csv(CLEAN / "ada_dataset.csv", index=False)
pd.concat([Xtr_a, pd.Series(ytr_a, name="label"), train["row_id"]], axis=1).to_csv(CLEAN / "ada_train_onehot.csv", index=False)
pd.concat([Xte_a, pd.Series(yte_a, name="label"), test["row_id"]], axis=1).to_csv(CLEAN / "ada_test_onehot.csv", index=False)

s = day.sample(8, random_state=SEED)
table_image(s.assign(date=s["date"].dt.strftime("%Y-%m-%d"))[["city", "date", "temp_mean", "precip_mm", "wind_max", "solar_rad", "season", "region", "label"]],
            "ada_01_data_sample.png", "Sample of the AdaBoost data: numeric weather, two text columns (season, region) and the label",
            highlight=["label", "season", "region"], ncols=9)
_ex = train.sample(6, random_state=21)
sb = _ex[["season", "region"]].reset_index(drop=True)
sa = design(_ex, Xtr_a.columns)[[c for c in Xtr_a.columns if c.startswith(("season_", "region_"))]]
fig, axes = plt.subplots(1, 2, figsize=(15, 3.6), gridspec_kw={"width_ratios": [1, 3.3]})
for ax, df, ttl in [(axes[0], sb, "Before: two text columns"), (axes[1], sa, "After one-hot encoding: eight 0/1 number columns")]:
    ax.axis("off")
    ax.set_title(ttl, loc="left", fontsize=11, fontweight="bold")
    t = ax.table(cellText=df.astype(str).values, colLabels=[c.replace("season_", "season=").replace("region_", "region=") for c in df.columns],
                 loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.scale(1, 1.5)
    for (r, c), cell in t.get_celld().items():
        if r == 0:
            cell.set_facecolor("#e8eefc")
            cell.set_text_props(fontweight="bold")
        elif df.iloc[r - 1, c] == 1 and df.dtypes.iloc[c] != object:
            cell.set_facecolor("#cfe3ff")
save(fig, "ada_02_onehot_step.png")
table_image(pd.concat([train[["row_id"]].reset_index(drop=True), Xtr_a, pd.Series(ytr_a, name="label")], axis=1).head(8),
            "ada_03_train_sample.png", f"Training set ({len(train):,} rows): first rows of the encoded data", highlight=["label"], ncols=9)
table_image(pd.concat([test[["row_id"]].reset_index(drop=True), Xte_a, pd.Series(yte_a, name="label")], axis=1).head(8),
            "ada_04_test_sample.png", f"Testing set ({len(test):,} rows): first rows of the encoded data", highlight=["label"], ncols=9)

# ---------------------------------------------------------------- tuning by cross-validation (training set only)
MAXN = 500
DEPTHS, LRS = [1, 2, 3], [0.05, 0.1, 0.3, 1.0]


def fold_curves(depth, lr, a, b):
    m = AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=depth), n_estimators=MAXN, learning_rate=lr,
                           random_state=SEED).fit(Xtr_a.iloc[a], ytr_a[a])
    acc, f1m = [], []
    for p in m.staged_predict(Xtr_a.iloc[b]):
        acc.append(accuracy_score(ytr_a[b], p))
        f1m.append(f1_score(ytr_a[b], p, average="macro"))
    pad = MAXN - len(acc)
    return np.array(acc + [acc[-1]] * pad), np.array(f1m + [f1m[-1]] * pad)


jobs = [(d, lr, a, b) for d in DEPTHS for lr in LRS for a, b in CV.split(Xtr_a, ytr_a)]
out = Parallel(n_jobs=-1)(delayed(fold_curves)(*j) for j in jobs)
cvacc, cvf1 = {}, {}
for (d, lr, a, b), (acc, f1m) in zip(jobs, out):
    cvacc.setdefault((d, lr), []).append(acc)
    cvf1.setdefault((d, lr), []).append(f1m)
cvacc = {k: np.mean(v, axis=0) for k, v in cvacc.items()}
cvf1 = {k: np.mean(v, axis=0) for k, v in cvf1.items()}
best = {k: (int(np.argmax(v)) + 1, float(v.max())) for k, v in cvacc.items()}
bk = max(best, key=lambda k: (round(best[k][1], 5), -best[k][0]))
BD, BLR, BN = bk[0], bk[1], best[bk][0]
RES["ada_grid"] = [{"depth": k[0], "learning_rate": k[1], "best_rounds": v[0], "cv_accuracy": v[1],
                    "cv_macro_f1_at_best": float(cvf1[k][v[0] - 1])} for k, v in best.items()]
RES["ada_chosen"] = {"base_depth": BD, "learning_rate": BLR, "rounds": BN, "cv_accuracy": best[bk][1],
                     "cv_macro_f1": float(cvf1[bk][BN - 1])}
bstump = max([k for k in best if k[0] == 1], key=lambda k: best[k][1])
RES["ada_best_stump"] = {"base_depth": 1, "learning_rate": bstump[1], "rounds": best[bstump][0], "cv_accuracy": best[bstump][1]}

rounds = np.arange(1, MAXN + 1)
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
for d, col in zip(DEPTHS, [GREY, ORANGE, BLUE]):
    lr = max([k for k in best if k[0] == d], key=lambda k: best[k][1])[1]
    axes[0].plot(rounds, cvacc[(d, lr)] * 100, color=col, lw=2, label=f"base tree depth {d} ({'stumps' if d == 1 else 'small trees'}), best learning rate {lr}")
    axes[0].scatter([best[(d, lr)][0]], [best[(d, lr)][1] * 100], color=col, s=60, zorder=5, edgecolor="k")
for lr, col in zip(LRS, ["#a8c4f0", "#6e9fe6", BLUE, "#16408c"]):
    axes[1].plot(rounds, cvacc[(BD, lr)] * 100, color=col, lw=2, label=f"learning rate {lr}")
    axes[1].scatter([best[(BD, lr)][0]], [best[(BD, lr)][1] * 100], color=col, s=60, zorder=5, edgecolor="k")
for ax in axes:
    ax.axhline(base_acc * 100, color="k", ls=":", lw=1)
    ax.set_xlabel("Boosting rounds (number of trees added)")
    ax.legend(fontsize=8, loc="lower right")
axes[0].set_ylabel("Validation accuracy (5-fold cross-validation, %)")
axes[0].set_title("Effect of the base tree depth", fontsize=10)
axes[1].set_title(f"Effect of the learning rate (base depth {BD})", fontsize=10)
fig.suptitle("How validation accuracy changes as rounds are added (dots mark the best round; dotted line = always answering Moderate)", fontsize=11, y=1.02)
save(fig, "ada_05_validation_curves.png")

heat = np.array([[best[(d, lr)][1] * 100 for lr in LRS] for d in DEPTHS])
fig, ax = plt.subplots(figsize=(6.8, 3.6))
sns.heatmap(heat, annot=[[f"{best[(d, lr)][1] * 100:.1f}%\n({best[(d, lr)][0]} rounds)" for lr in LRS] for d in DEPTHS], fmt="", cmap="Blues",
            xticklabels=[str(l) for l in LRS], yticklabels=[f"depth {d}" for d in DEPTHS], cbar_kws={"label": "Best validation accuracy (%)"}, ax=ax,
            annot_kws={"fontsize": 8})
ax.set_xlabel("Learning rate")
ax.set_ylabel("Base tree")
ax.set_title("Grid searched by cross-validation on the training set", fontsize=10)
save(fig, "ada_06_grid.png")

# ---------------------------------------------------------------- final models, evaluated once on the testing set
def mk_ada(d, lr, n):
    return AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=d), n_estimators=n, learning_rate=lr, random_state=SEED)


def mc_metrics(y, p):
    cm = confusion_matrix(y, p, labels=CLASSES)
    return {"accuracy": float(accuracy_score(y, p)), "macro_f1": float(f1_score(y, p, average="macro", labels=CLASSES)),
            "recall": {c: float(recall_score(y, p, labels=[c], average=None)[0]) for c in CLASSES},
            "precision": {c: float(precision_score(y, p, labels=[c], average=None, zero_division=0)[0]) for c in CLASSES},
            "confusion": cm.tolist(), "predicted_counts": {c: int((p == c).sum()) for c in CLASSES}}


ada = mk_ada(BD, BLR, BN).fit(Xtr_a, ytr_a)
p_ada = ada.predict(Xte_a)
RES["ada"] = mc_metrics(yte_a, p_ada)
RES["ada"]["train_accuracy"] = float(ada.score(Xtr_a, ytr_a))
st = mk_ada(1, bstump[1], best[bstump][0]).fit(Xtr_a, ytr_a)
RES["ada_stumps"] = mc_metrics(yte_a, st.predict(Xte_a))

# decision tree on the same encoded inputs (depth chosen by cross-validation on the training set)
dts = {dep: cross_val_score(DecisionTreeClassifier(max_depth=dep, random_state=SEED), Xtr_a, ytr_a, cv=CV).mean() for dep in range(1, 16)}
dbest = max(dts, key=lambda k: (round(dts[k], 5), -k))
dt = DecisionTreeClassifier(max_depth=dbest, random_state=SEED).fit(Xtr_a, ytr_a)
p_dt = dt.predict(Xte_a)
RES["dt_same_inputs"] = mc_metrics(yte_a, p_dt)
RES["dt_same_inputs"].update({"depth": int(dbest), "cv_accuracy": float(dts[dbest])})
RES["dt_part3_tuned_weather"] = {"accuracy": 0.652, "macro_f1": 0.528, "note": "values from the Part 3 results file (nb_dt_results.json)"}
part3 = json.loads((CLEAN / "nb_dt_results.json").read_text(encoding="utf-8"))
k3 = [k for k in part3["dt"] if k.startswith("Tuned") and "location" not in k][0]
RES["dt_part3_tuned_weather"] = {"accuracy": part3["dt"][k3]["accuracy"], "macro_f1": part3["dt"][k3]["macro_f1"],
                                 "recall_unhealthy": part3["dt"][k3]["recall"]["Unhealthy"], "depth": part3["dt"][k3]["depth"]}
# paired comparison on the testing set
ok_a, ok_d = p_ada == yte_a, p_dt == yte_a
n_a_only, n_d_only = int((ok_a & ~ok_d).sum()), int((~ok_a & ok_d).sum())
RES["ada_vs_dt"] = {"ada_only_correct": n_a_only, "dt_only_correct": n_d_only,
                    "mcnemar_p": float(binomtest(min(n_a_only, n_d_only), n_a_only + n_d_only, 0.5).pvalue),
                    "difference_points": float((ok_a.mean() - ok_d.mean()) * 100)}
bs = []
for _ in range(2000):
    i = rng.integers(0, len(yte_a), len(yte_a))
    bs.append((ok_a[i].mean() - ok_d[i].mean()) * 100)
RES["ada_vs_dt"]["difference_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
imp = pd.Series(ada.feature_importances_, index=Xtr_a.columns).sort_values()
RES["ada_importance"] = {k: float(v) for k, v in imp.sort_values(ascending=False).items()}
# time-based holdout
Xa_t, Xb_t = design(tr_t), None
Xb_t = design(te_t, Xa_t.columns)
at = mk_ada(BD, BLR, BN).fit(Xa_t, tr_t["label"].to_numpy())
dtt = DecisionTreeClassifier(max_depth=dbest, random_state=SEED).fit(Xa_t, tr_t["label"].to_numpy())
yb = te_t["label"].to_numpy()
RES["ada_time_holdout"] = {"ada": mc_metrics(yb, at.predict(Xb_t)), "dt": mc_metrics(yb, dtt.predict(Xb_t)),
                           "baseline_accuracy": float((yb == tr_t["label"].mode()[0]).mean())}

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
cm_panel(axes[0], RES["ada"]["confusion"], CLASSES, f"AdaBoost (depth {BD}, {BN} rounds)\naccuracy {RES['ada']['accuracy']:.1%}, macro-F1 {RES['ada']['macro_f1']:.2f}")
cm_panel(axes[1], RES["dt_same_inputs"]["confusion"], CLASSES, f"Decision tree (depth {dbest}), same inputs\naccuracy {RES['dt_same_inputs']['accuracy']:.1%}, macro-F1 {RES['dt_same_inputs']['macro_f1']:.2f}")
cm_panel(axes[2], RES["ada_stumps"]["confusion"], CLASSES, f"AdaBoost with stumps ({RES['ada_best_stump']['rounds']} rounds)\naccuracy {RES['ada_stumps']['accuracy']:.1%}, macro-F1 {RES['ada_stumps']['macro_f1']:.2f}")
fig.suptitle("Confusion matrices on the testing set (cells: count and share of the actual group)", fontsize=12, y=1.03)
save(fig, "ada_07_confusion_matrices.png")

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4))
items = [("Decision tree\n(Part 3, weather)", RES["dt_part3_tuned_weather"]["accuracy"], RES["dt_part3_tuned_weather"]["macro_f1"], RES["dt_part3_tuned_weather"]["recall_unhealthy"], GREY),
         (f"Decision tree\n(same inputs)", RES["dt_same_inputs"]["accuracy"], RES["dt_same_inputs"]["macro_f1"], RES["dt_same_inputs"]["recall"]["Unhealthy"], ORANGE),
         ("AdaBoost\n(tuned)", RES["ada"]["accuracy"], RES["ada"]["macro_f1"], RES["ada"]["recall"]["Unhealthy"], BLUE)]
for ax, (idx, ttl, scale) in zip(axes, [(1, "Accuracy (%)", 100), (2, "Macro-F1 (0 to 1)", 1), (3, "Share of Unhealthy days found (%)", 100)]):
    vals = [it[idx] * scale for it in items]
    bars = ax.bar([it[0] for it in items], vals, color=[it[4] for it in items])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.01 if scale == 1 else 1) * (1 if scale == 1 else 1), f"{v:.1f}" if scale == 100 else f"{v:.2f}", ha="center", fontsize=9)
    ax.set_title(ttl, fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="x", labelsize=8)
    if idx == 1:
        ax.axhline(base_acc * 100, color="k", ls=":", lw=1)
        ax.set_ylim(50, 72)
    elif idx == 2:
        ax.set_ylim(0, 0.7)
    else:
        ax.set_ylim(0, 50)
fig.suptitle("AdaBoost versus decision trees on the same testing set (dotted line: always answering Moderate)", fontsize=11, y=1.03)
save(fig, "ada_08_comparison.png")

fig, ax = plt.subplots(figsize=(7.6, 4.6))
ax.barh(imp.index, imp.values * 100, color=BLUE)
ax.set_xlabel("Share of total importance (%)")
ax.set_title("Which inputs the boosted trees rely on", fontsize=11)
ax.grid(axis="y", visible=False)
save(fig, "ada_09_importance.png")

# ---------------------------------------------------------------- explanatory figures with real data (toy example)
def run_toy(seed):
    tdf = pd.concat([train[train["label"] == "Good"].sample(35, random_state=seed),
                     train[train["label"] == "Unhealthy"].sample(35, random_state=seed)])
    x_ = tdf[["solar_rad", "temp_max"]].to_numpy()
    y_ = np.where(tdf["label"] == "Unhealthy", 1, -1)
    w_ = np.ones(len(y_)) / len(y_)
    h_ = []
    for _ in range(3):
        s_ = DecisionTreeClassifier(max_depth=1, random_state=0).fit(x_, y_, sample_weight=w_)
        pr_ = s_.predict(x_)
        e_ = float(w_[pr_ != y_].sum())
        a_ = 0.5 * np.log((1 - e_) / e_)
        h_.append({"w": w_.copy(), "stump": s_, "eps": e_, "alpha": float(a_), "pred": pr_.copy()})
        w_ = w_ * np.exp(-a_ * y_ * pr_)
        w_ = w_ / w_.sum()
    return tdf, x_, y_, h_


def toy_ok(h_, x_, y_):
    """Accept a sample where every stump says Unhealthy when hotter or sunnier, errors grow, alphas shrink,
    and the weighted vote beats every single stump."""
    dirs = []
    for hh in h_:
        f_ = int(hh["stump"].tree_.feature[0])
        t_ = float(hh["stump"].tree_.threshold[0])
        probe = np.zeros((1, 2))
        probe[0, f_] = t_ + 1
        dirs.append(int(hh["stump"].predict(probe)[0]) == 1)
    fin_ = np.sign(sum(hh["alpha"] * hh["stump"].predict(x_) for hh in h_))
    best_single = max((hh["pred"] == y_).mean() for hh in h_)
    return (all(dirs) and h_[0]["eps"] < h_[1]["eps"] < h_[2]["eps"] < 0.4
            and (fin_ == y_).mean() >= 0.9 and (fin_ == y_).mean() > best_single)


TOY_SEED = 7
for sd_ in range(80):
    _t, _x, _y, _h = run_toy(sd_)
    if toy_ok(_h, _x, _y):
        TOY_SEED = sd_
        break
toy, tx, ty, hist = run_toy(TOY_SEED)
RES["toy_seed"] = int(TOY_SEED)
names = ["solar radiation", "maximum temperature"]


def stump_rule(s_):
    f, t = int(s_.tree_.feature[0]), float(s_.tree_.threshold[0])
    hi = int(np.sign(s_.predict(np.where(np.arange(2) == f, t + 1, 0).reshape(1, 2).astype(float))[0]))
    return f, t, hi


gx, gy = np.meshgrid(np.linspace(tx[:, 0].min() - 1, tx[:, 0].max() + 1, 200), np.linspace(tx[:, 1].min() - 2, tx[:, 1].max() + 2, 200))
grid = np.c_[gx.ravel(), gy.ravel()]
fig, axes = plt.subplots(1, 4, figsize=(17, 4.4))
RES["toy"] = {"n_points": int(len(ty)), "rounds": []}
for i, (ax, h) in enumerate(zip(axes[:3], hist)):
    f, t, hi = stump_rule(h["stump"])
    zz = h["stump"].predict(grid).reshape(gx.shape)
    ax.contourf(gx, gy, zz, levels=[-2, 0, 2], colors=["#d8f0df", "#f8d9de"], alpha=0.8)
    ax.scatter(tx[:, 0], tx[:, 1], s=h["w"] / h["w"].max() * 160 + 12, c=np.where(ty == 1, RED, GREEN), edgecolor="white", linewidth=0.6)
    wrong = h["pred"] != ty
    ax.scatter(tx[wrong, 0], tx[wrong, 1], s=h["w"][wrong] / h["w"].max() * 160 + 12, facecolors="none", edgecolors="k", linewidth=1.4)
    ax.set_title(f"Round {i + 1}: weighted error {h['eps']:.2f}, weight alpha = {h['alpha']:.2f}", fontsize=10)
    ax.set_xlabel("Solar radiation (MJ/m2)")
    ax.set_ylabel("Maximum temperature (C)")
    RES["toy"]["rounds"].append({"round": i + 1, "rule": f"{names[f]} <= {t:.1f}", "feature": names[f], "threshold": t,
                                 "unhealthy_side": "above" if hi == 1 else "below", "weighted_error": h["eps"], "alpha": h["alpha"],
                                 "factor_wrong": float(np.exp(h["alpha"])), "factor_right": float(np.exp(-h["alpha"])),
                                 "n_wrong": int(wrong.sum())})
score = sum(h["alpha"] * h["stump"].predict(grid) for h in hist).reshape(gx.shape)
axes[3].contourf(gx, gy, score, levels=[-1e9, 0, 1e9], colors=["#d8f0df", "#f8d9de"], alpha=0.8)
axes[3].scatter(tx[:, 0], tx[:, 1], s=40, c=np.where(ty == 1, RED, GREEN), edgecolor="white", linewidth=0.6)
fin = np.sign(sum(h["alpha"] * h["stump"].predict(tx) for h in hist))
RES["toy"]["final_accuracy"] = float((fin == ty).mean())
RES["toy"]["stump_accuracies"] = [float((h["pred"] == ty).mean()) for h in hist]
axes[3].set_title(f"Weighted vote of 3 stumps: {RES['toy']['final_accuracy']:.0%} correct", fontsize=10)
axes[3].set_xlabel("Solar radiation (MJ/m2)")
axes[3].set_ylabel("Maximum temperature (C)")
fig.suptitle("AdaBoost on 70 real days (red = Unhealthy, green = Good): bigger dots carry more weight, circled dots were misclassified by that round's stump",
             fontsize=11, y=1.03)
save(fig, "ada_00b_reweighting.png")

# weighted-vote example: pick a day that the first stump gets wrong but the ensemble gets right
cand = [i for i in range(len(ty)) if hist[0]["pred"][i] != ty[i] and fin[i] == ty[i]]
ex = cand[0] if cand else 0
votes = [h["alpha"] * float(h["stump"].predict(tx[ex:ex + 1])[0]) for h in hist]
RES["toy"]["vote_example"] = {"true_class": "Unhealthy" if ty[ex] == 1 else "Good", "votes": votes, "total": float(sum(votes)),
                              "stump_predictions": [int(h["stump"].predict(tx[ex:ex + 1])[0]) for h in hist],
                              "solar_rad": float(tx[ex, 0]), "temp_max": float(tx[ex, 1])}
fig, ax = plt.subplots(figsize=(7.4, 4.2))
labs = ["Stump 1", "Stump 2", "Stump 3", "Total vote"]
vals = votes + [sum(votes)]
ax.bar(labs, vals, color=[RED if v > 0 else GREEN for v in vals], edgecolor=["none"] * 3 + ["k"], linewidth=[0, 0, 0, 2])
ax.axhline(0, color="k", lw=0.8)
for i, v in enumerate(vals):
    ax.text(i, v + (0.04 if v >= 0 else -0.09), f"{v:+.2f}", ha="center", fontsize=10)
ax.set_ylabel("Vote = alpha x (+1 Unhealthy or -1 Good)")
ax.set_title(f"One day, {RES['toy']['vote_example']['true_class']} in reality: each stump votes with its own weight alpha", fontsize=10)
ax.grid(axis="x", visible=False)
save(fig, "ada_00c_weighted_vote.png")

# bagging versus boosting schematic
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for ax in axes:
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
ax = axes[0]
ax.set_title("Bagging: trees are built independently, in parallel", fontsize=11, fontweight="bold")
ax.text(0.12, 0.5, "All\ntraining\ndays", ha="center", va="center", fontsize=9.5, bbox=dict(boxstyle="round", fc="#eef3fd", ec=GREY))
for i, yy in enumerate([0.82, 0.5, 0.18]):
    ax.annotate("", xy=(0.38, yy), xytext=(0.2, 0.5), arrowprops=dict(arrowstyle="->", color=GREY))
    ax.text(0.5, yy, f"Random sample {i + 1}\n-> tree {i + 1}", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", fc="#fde9d6", ec=GREY))
    ax.annotate("", xy=(0.82, 0.5), xytext=(0.64, yy), arrowprops=dict(arrowstyle="->", color=GREY))
ax.text(0.9, 0.5, "Equal\nvote", ha="center", va="center", fontsize=9.5, bbox=dict(boxstyle="round", fc="#e6f4ea", ec=GREY))
ax = axes[1]
ax.set_title("Boosting: each tree is built after the last, and fixes its mistakes", fontsize=11, fontweight="bold")
xs_ = [0.1, 0.38, 0.66]
for i, x0 in enumerate(xs_):
    ax.text(x0 + 0.08, 0.7, f"Tree {i + 1}\n(small, weak)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", fc="#fde9d6", ec=GREY))
    if i < 2:
        ax.annotate("", xy=(xs_[i + 1] - 0.02, 0.7), xytext=(x0 + 0.17, 0.7), arrowprops=dict(arrowstyle="->", color=GREY))
        ax.text((x0 + xs_[i + 1] + 0.15) / 2, 0.83, "raise the weight of\nwrongly classified days", ha="center", fontsize=8, color=RED)
    ax.annotate("", xy=(0.5, 0.3), xytext=(x0 + 0.08, 0.6), arrowprops=dict(arrowstyle="->", color=GREY))
ax.text(0.5, 0.18, "Weighted vote: trees that are more accurate\nhave a larger say (alpha)", ha="center", va="center", fontsize=9.5,
        bbox=dict(boxstyle="round", fc="#e6f4ea", ec=GREY))
save(fig, "ada_00a_bagging_vs_boosting.png")

(CLEAN / "reg_ada_results.json").write_text(json.dumps(RES, indent=2, default=str), encoding="utf-8")

# ---------------------------------------------------------------- console summary
L = RES["linear"]
for k, v in L.items():
    print("LIN", k, "RMSE", round(v["rmse"], 2), "MAE", round(v["mae"], 2), "R2", round(v["r2"], 3), "cvR2", round(v["cv_r2_train"], 3))
print("LIN coef", {k: round(v, 3) for k, v in RES["linear_coefficients"].items()})
for k, v in RES["logistic"].items():
    print("LOG", k, "acc", round(v["accuracy"], 3), "rec", round(v["recall"], 3), "prec", round(v["precision"], 3), "AUC", round(v["auc"], 3))
for k, v in RES["nb_binary"].items():
    print("NB ", k, "acc", round(v["accuracy"], 3), "rec", round(v["recall"], 3), "prec", round(v["precision"], 3), "AUC", round(v["auc"], 3))
print("C", C_BEST, "thr", THR_LOG, THR_NB, "OR/unit", {k: round(v, 3) for k, v in RES["logistic_odds_ratio_per_unit"].items()})
print("ADA chosen", RES["ada_chosen"], "test acc", round(RES["ada"]["accuracy"], 4), "F1", round(RES["ada"]["macro_f1"], 3), "unh recall", round(RES["ada"]["recall"]["Unhealthy"], 3))
print("ADA stumps", RES["ada_best_stump"], "test acc", round(RES["ada_stumps"]["accuracy"], 4))
print("DT same", RES["dt_same_inputs"]["depth"], round(RES["dt_same_inputs"]["accuracy"], 4), round(RES["dt_same_inputs"]["macro_f1"], 3))
print("ADA vs DT", RES["ada_vs_dt"])
print("time holdout ada", round(RES["ada_time_holdout"]["ada"]["accuracy"], 3), "dt", round(RES["ada_time_holdout"]["dt"]["accuracy"], 3), "base", round(RES["ada_time_holdout"]["baseline_accuracy"], 3))
print("toy", RES["toy"]["rounds"], RES["toy"]["final_accuracy"])
