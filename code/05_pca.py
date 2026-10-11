"""Principal component analysis (PCA) of 20,075 city-days of air quality and weather.

Input : data/clean/daily_city_air_weather_clean.csv
Output: data/clean/pca_input_numeric.csv, pca_scores_sample.csv, pca_results.json, images/pca_*.png

Run:  python code/05_pca.py
Packages: pandas, numpy, scikit-learn, matplotlib, seaborn (Python 3.14).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CLEAN, IMG = ROOT / "data" / "clean", ROOT / "images"
sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
PALETTE = ["#2a6fdb", "#f28e2b", "#2e9e5b", "#d1495b", "#8e44ad", "#17a2b8"]
SEED = 42
FEATURES = ["pm2_5", "pm10", "co", "no2", "so2", "ozone_max", "aqi_max",
            "temp_mean", "temp_max", "temp_min", "precip_mm", "wind_max", "solar_rad"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=130)
    plt.close(fig)


def before_image(df, label_cols, num_cols, name, title):
    """Image of the cleaned table BEFORE transforming: label columns (orange) are removed later, values are in original units."""
    sample = df[label_cols + num_cols].head(7).copy()
    for c in num_cols:
        sample[c] = sample[c].round(2)
    fig, ax = plt.subplots(figsize=(13, 3.2))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    t = ax.table(cellText=sample.astype(str).values, colLabels=sample.columns, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.5)
    for (r, c), cell in t.get_celld().items():
        is_label = c < len(label_cols)
        if r == 0:
            cell.set_facecolor("#c2661d" if is_label else "#4b4fa3")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#fdebd3" if is_label else "#ffffff")
    save(fig, name)


df = pd.read_csv(CLEAN / "daily_city_air_weather_clean.csv")
X = df[FEATURES]
X.to_csv(CLEAN / "pca_input_numeric.csv", index=False)
Xs = StandardScaler().fit_transform(X)
n, p = Xs.shape
res = {"n_rows": n, "n_features": p, "features": FEATURES}

# ------------------------------------------------------------------ PCA and SVD check
pca = PCA(random_state=SEED).fit(Xs)
scores = pca.transform(Xs)
evr = pca.explained_variance_ratio_
cum = np.cumsum(evr)
U, s, Vt = np.linalg.svd(Xs, full_matrices=False)          # SVD of the centered, scaled matrix
cov_eig = np.sort(np.linalg.eigvalsh(np.cov(Xs, rowvar=False)))[::-1]   # eigenvalues of the covariance matrix
res["eigenvalues"] = [round(float(v), 4) for v in pca.explained_variance_]
res["explained_variance_ratio"] = [round(float(v), 4) for v in evr]
res["cumulative"] = [round(float(v), 4) for v in cum]
res["svd_check"] = dict(
    max_abs_diff_eigenvalues_vs_svd=float(np.abs(cov_eig - s**2 / (n - 1)).max()),
    max_abs_diff_sklearn_vs_svd=float(np.abs(pca.explained_variance_ - s**2 / (n - 1)).max()),
    max_abs_diff_components=float(np.minimum(np.abs(pca.components_ - Vt).max(axis=1),
                                             np.abs(pca.components_ + Vt).max(axis=1)).max()))
res["n_for_80_90_95"] = [int(np.argmax(cum >= t) + 1) for t in (0.80, 0.90, 0.95)]
res["kaiser_n"] = int((pca.explained_variance_ > 1).sum())
load = pd.DataFrame(pca.components_.T, index=FEATURES, columns=[f"PC{i+1}" for i in range(p)])
res["loadings_pc1_pc4"] = load.iloc[:, :4].round(3).to_dict("index")
pd.DataFrame(scores[:, :5], columns=[f"PC{i+1}" for i in range(5)]).assign(
    city=df["city"], date=df["date"], season=df["season"], aqi_category=df["aqi_category"]
).sample(2000, random_state=SEED).round(4).to_csv(CLEAN / "pca_scores_sample.csv", index=False)

before_image(df, ["city", "date", "season", "aqi_category"],
             ["pm2_5", "co", "no2", "ozone_max", "temp_mean", "precip_mm", "wind_max"],
             "pca_01a_data_before.png",
             "BEFORE: cleaned daily table (orange label columns are removed; numbers are in original units)")

# ------------------------------------------------------------------ sample image (data prep)
sample = pd.DataFrame(Xs[:7, :10], columns=FEATURES[:10]).round(2)
fig, ax = plt.subplots(figsize=(13, 3.2))
ax.axis("off")
ax.set_title("AFTER: PCA input, labels removed and every column standardized (first 7 rows, first 10 of 13 columns)",
             loc="left", fontsize=11, fontweight="bold")
t = ax.table(cellText=sample.astype(str).values, colLabels=sample.columns, loc="center", cellLoc="center")
t.auto_set_font_size(False)
t.set_fontsize(9)
t.scale(1, 1.5)
for (r, c), cell in t.get_celld().items():
    if r == 0:
        cell.set_facecolor("#4b4fa3")
        cell.set_text_props(color="white", fontweight="bold")
    elif sample.iloc[r - 1, c] < 0:
        cell.set_facecolor("#fde8e8")
    else:
        cell.set_facecolor("#e6f0fb")
save(fig, "pca_01_data_sample.png")

# ------------------------------------------------------------------ overview images (toy data and dimensionality)
rng = np.random.default_rng(SEED)
toy = rng.multivariate_normal([0, 0], [[3.0, 2.2], [2.2, 2.0]], size=250)
tp = PCA(2).fit(toy)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
ax = axes[0]
ax.scatter(*toy.T, s=18, alpha=.55, color=PALETTE[0])
for i, col in enumerate([PALETTE[3], PALETTE[1]]):
    v = tp.components_[i] * np.sqrt(tp.explained_variance_[i]) * 2
    ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=3))
    ax.text(*(v * 1.12), f"PC{i+1}\n(eigenvector)", color=col, fontweight="bold", ha="center")
ax.set(title="PCA finds the directions of greatest spread", xlabel="Original variable 1", ylabel="Original variable 2")
ax.set_aspect("equal")
ax = axes[1]
tz = tp.transform(toy)
ax.scatter(tz[:, 0], tz[:, 1], s=18, alpha=.55, color=PALETTE[2])
ax.axhline(0, color="#888", lw=.8)
ax.axvline(0, color="#888", lw=.8)
ax.set(title=f"Rotated view: PC1 holds {tp.explained_variance_ratio_[0]:.0%} of the variance",
       xlabel="PC1 (eigenvalue = %.2f)" % tp.explained_variance_[0], ylabel="PC2 (eigenvalue = %.2f)" % tp.explained_variance_[1])
ax.set_aspect("equal")
save(fig, "pca_00a_concept.png")

dims = [2, 5, 10, 20, 50, 100, 200, 500]
ratio = []
for d in dims:   # average over 50 random draws so the curve is smooth
    r = []
    for _ in range(50):
        pts = rng.random((300, d))
        dist = np.linalg.norm(pts[1:] - pts[0], axis=1)
        r.append(dist.min() / dist.max())
    ratio.append(float(np.mean(r)))
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.plot(dims, ratio, "o-", color=PALETTE[3], lw=2)
ax.set_xscale("log")
ax.set(title="Curse of dimensionality: nearest and farthest points look alike",
       xlabel="Number of dimensions (log scale)", ylabel="Nearest distance / farthest distance")
save(fig, "pca_00b_curse_of_dimensionality.png")

# ------------------------------------------------------------------ scree
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.bar(range(1, p + 1), evr * 100, color=PALETTE[0], alpha=.85, label="Variance explained by each PC")
ax.set_xlabel("Principal component")
ax.set_ylabel("Percent of variance explained")
ax2 = ax.twinx()
ax2.plot(range(1, p + 1), cum * 100, "o-", color=PALETTE[1], lw=2, label="Cumulative")
for thr in (80, 95):
    ax2.axhline(thr, color="#888", ls=":", lw=1)
ax2.set_ylabel("Cumulative percent")
ax2.set_ylim(0, 102)
ax2.grid(False)
ax.set_xticks(range(1, p + 1))
ax.set_title("Scree plot: variance explained by each principal component")
save(fig, "pca_02_scree.png")

# ------------------------------------------------------------------ loadings heatmap
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(load.iloc[:, :5], cmap="RdBu_r", center=0, annot=True, fmt=".2f", annot_kws={"size": 9},
            cbar_kws={"label": "Loading (eigenvector weight)"}, ax=ax)
ax.set_title("Loadings: how each variable contributes to PC1 to PC5")
save(fig, "pca_03_loadings.png")

# ------------------------------------------------------------------ biplot (PC1 vs PC2, colored by season)
season_colors = {"Winter": "#2a6fdb", "Spring": "#2e9e5b", "Summer": "#f28e2b", "Fall": "#8e44ad"}
fig, ax = plt.subplots(figsize=(9.5, 7))
for sname, col in season_colors.items():
    m = (df["season"] == sname).values
    ax.scatter(scores[m, 0], scores[m, 1], s=5, alpha=.25, color=col, label=sname, rasterized=True)
scale = 5.2
nudge = {"temp_max": (0.2, 0.0), "temp_mean": (0.35, 0.28), "temp_min": (0.15, -0.35), "solar_rad": (0.35, 0.15),
         "pm2_5": (-0.3, 0.2), "pm10": (0.35, -0.05), "no2": (-0.25, 0.1), "so2": (-0.1, -0.1), "co": (0.2, 0.15)}
for f in FEATURES:
    x, y = load.loc[f, "PC1"] * scale, load.loc[f, "PC2"] * scale
    ax.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="black", lw=1.4))
    dx, dy = nudge.get(f, (0, 0))
    ax.text(x * 1.1 + dx, y * 1.1 + dy, f, fontsize=9, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=.15", fc="white", ec="none", alpha=.7))
ax.set(xlim=(-7, 8), ylim=(-6, 8),
       xlabel=f"PC1 ({evr[0]:.1%} of variance)", ylabel=f"PC2 ({evr[1]:.1%} of variance)",
       title="Biplot: city-days (colored by season) and variable loadings (arrows)")
leg = ax.legend(markerscale=4, loc="lower left", title="Season")
for lh in leg.legend_handles:
    lh.set_alpha(1)
save(fig, "pca_04_biplot.png")

# ------------------------------------------------------------------ PC1 vs PC2 by AQI category
cat_order = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy"]
cat_colors = ["#2e9e5b", "#f2c94c", "#f28e2b", "#d1495b", "#8e44ad"]
fig, ax = plt.subplots(figsize=(9, 6.2))
for c, col in zip(cat_order, cat_colors):
    m = (df["aqi_category"] == c).values
    ax.scatter(scores[m, 0], scores[m, 1], s=6 if c in cat_order[:2] else 14, alpha=.35 if c in cat_order[:2] else .8,
               color=col, label=f"{c} (n={m.sum():,})", rasterized=True)
ax.set(xlim=(-7, 9), ylim=(-6, 9), xlabel=f"PC1 ({evr[0]:.1%} of variance)", ylabel=f"PC2 ({evr[1]:.1%} of variance)",
       title="City-days in the PC1 to PC2 plane, colored by AQI category")
ax.legend(loc="lower left", fontsize=8, markerscale=2)
save(fig, "pca_05_aqi_categories.png")

# ------------------------------------------------------------------ 3D view and city averages
fig = plt.figure(figsize=(8.5, 6.5))
ax = fig.add_subplot(111, projection="3d")
idx = np.random.default_rng(SEED).choice(n, 4000, replace=False)
for sname, col in season_colors.items():
    m = (df["season"].values[idx] == sname)
    ax.scatter(scores[idx][m, 0], scores[idx][m, 1], scores[idx][m, 2], s=4, alpha=.35, color=col, label=sname)
ax.set(xlabel=f"PC1 ({evr[0]:.0%})", ylabel=f"PC2 ({evr[1]:.0%})", zlabel=f"PC3 ({evr[2]:.0%})",
       title="First three principal components (4,000 sampled city-days)")
ax.legend(markerscale=3, loc="upper left")
ax.view_init(elev=18, azim=-58)
save(fig, "pca_06_3d.png")

cityavg = pd.DataFrame(scores[:, :3], columns=["PC1", "PC2", "PC3"]).groupby(df["city"].values).mean()
reg = df.groupby("city")["region"].first()
reg_colors = {"West": "#2a6fdb", "South": "#d1495b", "Midwest": "#2e9e5b", "Northeast": "#f28e2b"}
fig, ax = plt.subplots(figsize=(10, 7))
for city_name, r in cityavg.iterrows():
    ax.scatter(r["PC1"], r["PC2"], s=70, color=reg_colors[reg[city_name]], edgecolors="white")
    ax.annotate(city_name, (r["PC1"], r["PC2"]), fontsize=7, xytext=(4, 3), textcoords="offset points")
ax.axhline(0, color="#aaa", lw=.8)
ax.axvline(0, color="#aaa", lw=.8)
ax.set(xlabel=f"Average PC1 score ({evr[0]:.1%} of variance)", ylabel=f"Average PC2 score ({evr[1]:.1%} of variance)",
       title="Each city's average position on the first two components, 2023")
ax.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=c, label=k) for k, c in reg_colors.items()], title="Region")
save(fig, "pca_07_city_averages.png")
res["city_avg_extremes"] = {
    "PC1_low": cityavg["PC1"].nsmallest(4).round(2).to_dict(), "PC1_high": cityavg["PC1"].nlargest(4).round(2).to_dict(),
    "PC2_low": cityavg["PC2"].nsmallest(4).round(2).to_dict(), "PC2_high": cityavg["PC2"].nlargest(4).round(2).to_dict()}
res["season_mean_scores"] = pd.DataFrame(scores[:, :3], columns=["PC1", "PC2", "PC3"]).groupby(df["season"].values).mean().round(2).to_dict("index")
res["aqi_mean_scores"] = pd.DataFrame(scores[:, :3], columns=["PC1", "PC2", "PC3"]).groupby(df["aqi_category"].values).mean().round(2).to_dict("index")
res["pc_corr_with_pm25_ozone"] = {f"PC{i+1}": dict(pm2_5=round(float(np.corrcoef(scores[:, i], df["pm2_5"])[0, 1]), 3),
                                                     ozone_max=round(float(np.corrcoef(scores[:, i], df["ozone_max"])[0, 1]), 3),
                                                     temp_mean=round(float(np.corrcoef(scores[:, i], df["temp_mean"])[0, 1]), 3)) for i in range(4)}
(CLEAN / "pca_results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: res[k] for k in ["eigenvalues", "explained_variance_ratio", "cumulative", "svd_check", "n_for_80_90_95",
                                       "kaiser_n", "loadings_pc1_pc4", "city_avg_extremes", "season_mean_scores",
                                       "aqi_mean_scores", "pc_corr_with_pm25_ozone"]}, indent=1))
