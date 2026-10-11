"""Clustering of 50 US cities: k-means (Euclidean) and hierarchical (cosine distance).

Input : data/clean/city_air_weather_health_clean.csv
Output: data/clean/clustering_input_numeric.csv, clustering_input_scaled.csv,
        city_clusters.csv, clustering_results.json, images/cluster_*.png

Run:  python code/04_clustering.py
Packages: pandas, numpy, scikit-learn, scipy, matplotlib, seaborn (Python 3.14).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import cophenet, dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_samples, silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CLEAN, IMG = ROOT / "data" / "clean", ROOT / "images"
sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
PALETTE = ["#2a6fdb", "#f28e2b", "#2e9e5b", "#d1495b", "#8e44ad", "#17a2b8", "#7f7f7f"]
SEED = 42
KS = range(2, 11)
COMPARE_K = [3, 4, 5]      # values of k compared in the write-up
MAIN_K = 4                 # k used for profiles, map and the cluster table

AIR = ["pm2_5_mean", "pm2_5_p95", "no2_mean", "so2_mean", "co_mean", "ozone_max_mean", "unhealthy_day_share"]
WEATHER = ["temp_mean", "precip_total", "wind_mean"]
HEALTH = ["uninsured", "high_bp", "asthma", "heart_disease", "copd", "smoking", "depression",
          "diabetes", "inactivity", "obesity"]
FEATURES = AIR + WEATHER + HEALTH


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


# ------------------------------------------------------------------ data
city = pd.read_csv(CLEAN / "city_air_weather_health_clean.csv")
names = (city["city"] + ", " + city["state"]).tolist()
X = city[FEATURES]
Xs = StandardScaler().fit_transform(X)
X.to_csv(CLEAN / "clustering_input_numeric.csv", index=False)
pd.DataFrame(Xs, columns=FEATURES).round(4).to_csv(CLEAN / "clustering_input_scaled.csv", index=False)
res = {"n_cities": len(city), "n_features": len(FEATURES), "features": FEATURES}

before_image(city, ["city", "state", "region", "asthma_level"],
             ["pm2_5_mean", "no2_mean", "co_mean", "temp_mean", "precip_total", "smoking", "copd"],
             "cluster_01a_data_before.png",
             "BEFORE: cleaned city table (orange label columns are removed; numbers are in original units)")

# ------------------------------------------------------------------ sample image (data prep)
sample = pd.DataFrame(Xs[:7, :10], columns=FEATURES[:10]).round(2)
fig, ax = plt.subplots(figsize=(13, 3.2))
ax.axis("off")
ax.set_title("AFTER: clustering input, labels removed and every column standardized (first 7 rows, first 10 of 20 columns)",
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
save(fig, "cluster_01_data_sample.png")

# ------------------------------------------------------------------ overview concept images (toy data)
rng = np.random.default_rng(SEED)
blobs = np.vstack([rng.normal(c, 0.55, size=(30, 2)) for c in [(0, 0), (4, 0.5), (2, 3.6)]])
km_toy = KMeans(3, n_init=10, random_state=SEED).fit(blobs)
Z_toy = linkage(blobs[::3], "average")
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 1.1]})
ax = axes[0]
ax.scatter(blobs[:, 0], blobs[:, 1], c=[PALETTE[i] for i in km_toy.labels_], s=30, alpha=.8)
ax.scatter(*km_toy.cluster_centers_.T, marker="X", s=260, c="black", edgecolors="white", label="centroid")
ax.set(title="Partitional (k-means): choose k, assign to nearest centroid", xlabel="Feature 1", ylabel="Feature 2")
ax.legend(loc="lower right")
dendrogram(Z_toy, ax=axes[1], color_threshold=Z_toy[-2, 2] * 1.01, above_threshold_color="#888", no_labels=True)
axes[1].set(title="Hierarchical: merge the closest groups step by step", xlabel="Observations", ylabel="Merge distance")
save(fig, "cluster_00a_partitional_vs_hierarchical.png")

a, b, c = np.array([2.0, 1.0]), np.array([4.0, 2.0]), np.array([1.0, 3.5])
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
ax = axes[0]
for p, lab, col in [(a, "A", PALETTE[0]), (b, "B (2A)", PALETTE[1]), (c, "C", PALETTE[2])]:
    ax.annotate("", xy=p, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2.2))
    ax.text(p[0] + .08, p[1] + .08, lab, color=col, fontweight="bold")
ax.plot([a[0], b[0]], [a[1], b[1]], "--", color="#555")
ax.set(xlim=(0, 5), ylim=(0, 4.3), xlabel="Feature 1", ylabel="Feature 2",
       title="Euclidean distance looks at the gap between points")
ax.text(3.2, 1.2, "A and B are far apart", fontsize=10)
ax = axes[1]
for p, lab, col in [(a, "A", PALETTE[0]), (b, "B (2A)", PALETTE[1]), (c, "C", PALETTE[2])]:
    ax.annotate("", xy=p / np.linalg.norm(p) * 3, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2.2))
    ax.text(*(p / np.linalg.norm(p) * 3 + (.08, .08 if lab != "A" else -.3)), lab, color=col, fontweight="bold")
ax.set(xlim=(0, 5), ylim=(0, 4.3), xlabel="Feature 1", ylabel="Feature 2",
       title="Cosine distance looks at the angle (pattern, not size)")
ax.text(2.2, 0.35, "A and B point the same way: cosine distance = 0", fontsize=10)
save(fig, "cluster_00b_distance_metrics.png")

def by_pm25(labels):
    """Relabel clusters 0..k-1 from lowest to highest mean PM2.5 so colors match across figures."""
    order = city["pm2_5_mean"].groupby(labels).mean().sort_values().index
    rank = {old: new for new, old in enumerate(order)}
    return np.array([rank[v] for v in labels])


# ------------------------------------------------------------------ k-means over k
km_res = {}
for k in KS:
    km = KMeans(k, n_init=50, random_state=SEED).fit(Xs)
    km_res[k] = dict(model=km, inertia=km.inertia_, sil=silhouette_score(Xs, km.labels_))
res["kmeans"] = {int(k): dict(inertia=round(v["inertia"], 2), silhouette=round(v["sil"], 4)) for k, v in km_res.items()}
best_km = max(km_res, key=lambda k: km_res[k]["sil"])
res["kmeans_best_k_by_silhouette"] = int(best_km)

# ------------------------------------------------------------------ hierarchical (cosine distance, average linkage)
D = pdist(Xs, metric="cosine")
Dsq = squareform(D)
Z = linkage(D, method="average")
res["cophenetic_corr"] = round(float(cophenet(Z, D)[0]), 4)
hc_res = {}
for k in KS:
    lab = fcluster(Z, k, criterion="maxclust")
    hc_res[k] = dict(labels=lab, sil=silhouette_score(Dsq, lab, metric="precomputed"),
                     sizes=sorted(np.bincount(lab)[1:].tolist(), reverse=True))
res["hclust"] = {int(k): dict(silhouette_cosine=round(v["sil"], 4), sizes=v["sizes"]) for k, v in hc_res.items()}
best_hc = max(hc_res, key=lambda k: hc_res[k]["sil"])
res["hclust_best_k_by_silhouette"] = int(best_hc)

# k-means vs hierarchical agreement
res["agreement_ARI"] = {int(k): round(adjusted_rand_score(km_res[k]["model"].labels_, hc_res[k]["labels"]), 4) for k in KS}

# ------------------------------------------------------------------ figures: elbow and silhouette
fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.plot(list(KS), [km_res[k]["inertia"] for k in KS], "o-", color=PALETTE[0], lw=2)
ax.set(title="K-means elbow plot (within-cluster sum of squares)", xlabel="Number of clusters k", ylabel="Inertia")
save(fig, "cluster_02_elbow.png")

fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(list(KS), [km_res[k]["sil"] for k in KS], "o-", color=PALETTE[0], lw=2, label="K-means (Euclidean)")
ax.plot(list(KS), [hc_res[k]["sil"] for k in KS], "s--", color=PALETTE[1], lw=2, label="Hierarchical (cosine, average)")
ax.axvline(best_km, color=PALETTE[0], alpha=.25, lw=6)
ax.set(title="Average silhouette width by number of clusters", xlabel="Number of clusters k", ylabel="Average silhouette")
ax.legend()
save(fig, "cluster_03_silhouette_scores.png")

fig, axes = plt.subplots(1, len(COMPARE_K), figsize=(13, 4.8), sharex=True)
for ax, k in zip(axes, COMPARE_K):
    lab = by_pm25(km_res[k]["model"].labels_)
    s = silhouette_samples(Xs, lab)
    y = 0
    for j in range(k):
        v = np.sort(s[lab == j])
        ax.fill_betweenx(np.arange(y, y + len(v)), 0, v, color=PALETTE[j], alpha=.85)
        ax.text(-0.17, y + len(v) / 2, f"C{j}", va="center", fontsize=9)
        y += len(v) + 2
    ax.axvline(km_res[k]["sil"], color="red", ls="--")
    ax.set(title=f"k = {k} (mean {km_res[k]['sil']:.2f})", xlabel="Silhouette value", yticks=[])
    ax.set_xlim(-0.2, 0.6)
axes[0].set_ylabel("Cities, grouped by cluster")
fig.suptitle("Per-city silhouette values for k-means", fontsize=13, fontweight="bold")
save(fig, "cluster_04_silhouette_by_city.png")

# ------------------------------------------------------------------ dendrogram
cut_h = (Z[-(MAIN_K - 1), 2] + Z[-MAIN_K, 2]) / 2   # height that gives MAIN_K groups
fig, ax = plt.subplots(figsize=(10, 11))
dendrogram(Z, labels=names, orientation="left", color_threshold=cut_h, leaf_font_size=10, ax=ax)
ax.axvline(cut_h, color="red", ls="--", lw=1.2)
ax.set(title=f"Hierarchical clustering of 50 cities (cosine distance, average linkage)\ndashed line cuts the tree into k = {MAIN_K} groups",
       xlabel="Cosine distance between merged groups")
save(fig, "cluster_05_dendrogram.png")

# ------------------------------------------------------------------ cluster scatter (PCA used only to draw)
pca2 = PCA(2, random_state=SEED).fit(Xs)
P = pca2.transform(Xs)
fig, axes = plt.subplots(1, len(COMPARE_K), figsize=(14, 4.9), sharex=True, sharey=True)
for ax, k in zip(axes, COMPARE_K):
    lab = by_pm25(km_res[k]["model"].labels_)
    ax.scatter(P[:, 0], P[:, 1], c=[PALETTE[i] for i in lab], s=70, edgecolors="white", linewidth=.6)
    ax.set(title=f"k = {k}", xlabel=f"PC1 ({pca2.explained_variance_ratio_[0]:.0%} of variance)")
axes[0].set_ylabel(f"PC2 ({pca2.explained_variance_ratio_[1]:.0%} of variance)")
fig.suptitle("K-means clusters of the 50 cities, drawn on the first two principal components", fontsize=13, fontweight="bold")
save(fig, "cluster_06_kmeans_scatter.png")
res["pc12_variance"] = [round(float(v), 4) for v in pca2.explained_variance_ratio_]

# ------------------------------------------------------------------ main solution: profiles, map, table
km_main = km_res[MAIN_K]["model"]
kmeans_main = by_pm25(km_main.labels_)   # cluster 0 = lowest mean PM2.5, highest number = highest
hc_main = fcluster(Z, MAIN_K, criterion="maxclust") - 1
out = city[["city", "state", "region", "asthma_level", "pm_level"]].copy()
out["kmeans_cluster"] = kmeans_main
out["hclust_cluster"] = hc_main
out["pm2_5_mean"] = city["pm2_5_mean"].round(2)
out.to_csv(CLEAN / "city_clusters.csv", index=False)

prof = pd.DataFrame(Xs, columns=FEATURES).groupby(kmeans_main).mean()
prof.index = [f"Cluster {i} (n={int((kmeans_main == i).sum())})" for i in prof.index]
fig, ax = plt.subplots(figsize=(13, 3.8))
sns.heatmap(prof, cmap="RdBu_r", center=0, annot=True, fmt=".1f", annot_kws={"size": 8}, cbar_kws={"label": "Mean z-score"}, ax=ax)
ax.set_title(f"What distinguishes each k-means cluster (k = {MAIN_K}): mean standardized value of every feature")
ax.tick_params(axis="x", rotation=60)
save(fig, "cluster_07_profiles.png")

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(city["longitude"], city["latitude"], c=[PALETTE[i] for i in kmeans_main], s=130, edgecolors="white", linewidth=.8)
for i, r in city.iterrows():
    ax.annotate(r["city"], (r["longitude"], r["latitude"]), fontsize=7, xytext=(4, 3), textcoords="offset points")
ax.set(xlim=(-126, -66), ylim=(24, 50), title=f"Where the k-means clusters sit (k = {MAIN_K})", xlabel="Longitude", ylabel="Latitude")
handles = [plt.Line2D([], [], marker="o", ls="", color=PALETTE[i], label=f"Cluster {i}") for i in range(MAIN_K)]
ax.legend(handles=handles, loc="lower left")
save(fig, "cluster_08_map.png")

ct = pd.crosstab(pd.Series(kmeans_main, name="K-means cluster"), pd.Series(hc_main, name="Hierarchical cluster"))
fig, ax = plt.subplots(figsize=(6.5, 4.6))
sns.heatmap(ct, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax)
ax.set_title(f"K-means vs hierarchical membership (k = {MAIN_K})")
save(fig, "cluster_09_agreement.png")

# facts used in the write-up
res["main_k"] = MAIN_K
res["main_cluster_members"] = {int(i): out.loc[out.kmeans_cluster == i, "city"].tolist() for i in range(MAIN_K)}
res["main_cluster_profile_raw_means"] = X.groupby(kmeans_main).mean().round(2).to_dict("index")
res["main_cluster_region_counts"] = pd.crosstab(kmeans_main, city["region"]).to_dict("index")
res["main_cluster_asthma_level_counts"] = pd.crosstab(kmeans_main, city["asthma_level"]).to_dict("index")
res["crosstab_kmeans_vs_hclust"] = ct.to_dict("index")
res["hclust_main_members"] = {int(i): out.loc[out.hclust_cluster == i, "city"].tolist() for i in range(MAIN_K)}
res["top_profile_zscores"] = {int(i): prof.iloc[i].round(2).sort_values().to_dict() for i in range(MAIN_K)}
(CLEAN / "clustering_results.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: res[k] for k in ["kmeans", "hclust", "agreement_ARI", "cophenetic_corr",
                                       "kmeans_best_k_by_silhouette", "hclust_best_k_by_silhouette", "pc12_variance"]}, indent=1))
