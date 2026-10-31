"""Naive Bayes and Decision Trees: predict the AQI group of a city-day from weather.

Target (label): Good / Moderate / Unhealthy (US AQI 101+, i.e. unhealthy for sensitive groups or worse)
Features      : daily weather (7 columns) and, in a second experiment, city latitude and longitude.
              No pollutant columns are used, because the AQI is computed from them (that would leak the label).

Input : data/clean/daily_city_air_weather_clean.csv, data/raw/cities_reference.csv
Output: data/clean/nb_dt_labeled_dataset.csv, nb_train_binned.csv, nb_test_binned.csv, dt_train.csv, dt_test.csv,
        nb_dt_results.json, images/nb_*.png, images/dt_*.png

Run:  python code/06_naive_bayes_trees.py
Packages: pandas, numpy, scikit-learn, matplotlib, seaborn (Python 3.10+).
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
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.preprocessing import KBinsDiscretizer, MinMaxScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

warnings.filterwarnings("ignore", message="Bins whose width")

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, IMG = ROOT / "data" / "raw", ROOT / "data" / "clean", ROOT / "images"
sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
SEED = 42
CLASSES = ["Good", "Moderate", "Unhealthy"]
CCOL = {"Good": "#2e9e5b", "Moderate": "#f2c94c", "Unhealthy": "#d1495b"}
BLUE, ORANGE, GREY = "#2a6fdb", "#f28e2b", "#6b7280"
WEATHER = ["temp_mean", "temp_max", "temp_min", "precip_mm", "wind_max", "solar_rad", "month"]
WEATHER_LOC = WEATHER + ["latitude", "longitude"]
N_BINS = 5
RES = {}


def save(fig, name, dpi=130):
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def table_image(df, name, title, highlight=None, nrows=8, ncols=9):
    """Render the head of a dataframe as a small picture (for the 'image of the data' requirement)."""
    sample = df.head(nrows).iloc[:, :ncols].copy()
    for c in sample.columns:
        if sample[c].dtype.kind == "f":
            sample[c] = sample[c].round(2)
    fig, ax = plt.subplots(figsize=(min(2 + 1.3 * sample.shape[1], 15), 0.5 * len(sample) + 1.3))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    t = ax.table(cellText=sample.astype(str).values, colLabels=sample.columns, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.scale(1, 1.4)
    for (r, c), cell in t.get_celld().items():
        if r == 0:
            is_label = highlight is not None and sample.columns[c] in highlight
            cell.set_facecolor("#fde3c8" if is_label else "#e8eefc")
            cell.set_text_props(fontweight="bold")
        elif highlight is not None and sample.columns[c] in highlight:
            cell.set_facecolor("#fff4e6")
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=130)
    plt.close(fig)


def metrics(y_true, y_pred, baseline_label):
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=CLASSES, zero_division=0)
    return {
        "accuracy": float((np.asarray(y_true) == np.asarray(y_pred)).mean()),
        "macro_f1": float(f1_score(y_true, y_pred, labels=CLASSES, average="macro", zero_division=0)),
        "recall": dict(zip(CLASSES, map(float, r))),
        "precision": dict(zip(CLASSES, map(float, p))),
        "predicted_counts": {c: int((np.asarray(y_pred) == c).sum()) for c in CLASSES},
        "confusion": cm.tolist(),
        "baseline_accuracy": float((np.asarray(y_true) == baseline_label).mean()),
    }


def cm_panel(ax, cm, title):
    cm = np.array(cm)
    pct = cm / cm.sum(axis=1, keepdims=True).clip(min=1) * 100
    ax.imshow(pct, cmap="Blues", vmin=0, vmax=100)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{cm[i, j]:,}\n({pct[i, j]:.0f}%)", ha="center", va="center", fontsize=9,
                    color="white" if pct[i, j] > 55 else "black")
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(CLASSES, fontsize=9)
    ax.set_yticklabels(CLASSES, fontsize=9)
    ax.set_xlabel("Predicted AQI group")
    ax.set_ylabel("Actual AQI group")
    ax.set_title(title, fontsize=10)
    ax.grid(False)


# ============================================================================ data and labels
d = pd.read_csv(CLEAN / "daily_city_air_weather_clean.csv", parse_dates=["date"])
cities = pd.read_csv(RAW / "cities_reference.csv")[["city", "state", "latitude", "longitude"]]
n0 = len(d)
d = d.merge(cities, on=["city", "state"], how="left")
assert len(d) == n0 and d[["latitude", "longitude"]].notna().all().all()
d["label"] = d["aqi_category"].map({"Good": "Good", "Moderate": "Moderate"}).fillna("Unhealthy")
d.insert(0, "row_id", np.arange(len(d)))
labeled_cols = ["row_id", "city", "state", "date"] + WEATHER + ["latitude", "longitude", "aqi_category", "label"]
d[labeled_cols].to_csv(CLEAN / "nb_dt_labeled_dataset.csv", index=False)
RES["n_rows"] = int(len(d))
RES["label_counts"] = d["label"].value_counts().reindex(CLASSES).astype(int).to_dict()
RES["label_share"] = (d["label"].value_counts(normalize=True).reindex(CLASSES)).round(4).to_dict()
RES["aqi_category_counts"] = d["aqi_category"].value_counts().astype(int).to_dict()

table_image(d[["city", "date", "temp_mean", "precip_mm", "wind_max", "solar_rad", "month", "aqi_category", "label"]]
            .assign(date=d["date"].dt.strftime("%Y-%m-%d")).sample(8, random_state=SEED),
            "nb_01_labeled_sample.png", "Labeled sample: weather features and the AQI group label (random rows)",
            highlight=["aqi_category", "label"])

# ============================================================================ train / test split
train, test = train_test_split(d, test_size=0.2, stratify=d["label"], random_state=SEED)
overlap = len(set(train["row_id"]) & set(test["row_id"]))
assert overlap == 0
RES["split"] = {"train_rows": int(len(train)), "test_rows": int(len(test)), "overlap_rows": int(overlap),
                "train_share": train["label"].value_counts(normalize=True).reindex(CLASSES).round(4).to_dict(),
                "test_share": test["label"].value_counts(normalize=True).reindex(CLASSES).round(4).to_dict(),
                "train_counts": train["label"].value_counts().reindex(CLASSES).astype(int).to_dict(),
                "test_counts": test["label"].value_counts().reindex(CLASSES).astype(int).to_dict()}
majority = train["label"].mode()[0]
RES["majority_class"] = majority
RES["baseline_accuracy_test"] = float((test["label"] == majority).mean())
ytr, yte = train["label"].to_numpy(), test["label"].to_numpy()

fig, ax = plt.subplots(figsize=(8, 4.3))
x = np.arange(3)
for k, (nm, df, col) in enumerate([("Training set", train, BLUE), ("Testing set", test, ORANGE)]):
    sh = df["label"].value_counts(normalize=True).reindex(CLASSES) * 100
    cnt = df["label"].value_counts().reindex(CLASSES)
    bars = ax.bar(x + (k - 0.5) * 0.38, sh.values, 0.38, color=col, label=f"{nm} ({len(df):,} rows)")
    for b, v, c in zip(bars, sh.values, cnt.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%\n({c:,})", ha="center", fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels(CLASSES)
ax.set_ylabel("Share of rows (%)")
ax.set_ylim(0, 75)
ax.grid(axis="x", visible=False)
ax.set_title("Stratified split keeps the label proportions the same in both sets")
ax.legend()
save(fig, "nb_05_split_balance.png")

# ============================================================================ NAIVE BAYES
# --- feature views
scaler = MinMaxScaler().fit(train[WEATHER])
Xtr_scaled, Xte_scaled = scaler.transform(train[WEATHER]), scaler.transform(test[WEATHER])


def make_binner(cols, frame):
    kb = KBinsDiscretizer(n_bins=N_BINS, encode="onehot-dense", strategy="quantile",
                          quantile_method="averaged_inverted_cdf")
    kb.fit(frame[cols])
    return kb


def bin_names(cols, kb):
    names = []
    for col, edges in zip(cols, kb.bin_edges_):
        for lo, hi in zip(edges[:-1], edges[1:]):
            names.append(f"{col} {lo:.1f} to {hi:.1f}")
    return names


kb = make_binner(WEATHER, train)
Xtr_bin, Xte_bin = kb.transform(train[WEATHER]), kb.transform(test[WEATHER])
names_bin = bin_names(WEATHER, kb)
RES["nb_binned_columns"] = int(Xtr_bin.shape[1])
pd.DataFrame(Xtr_bin.astype(int), columns=names_bin).assign(label=ytr, row_id=train["row_id"].to_numpy()) \
    .to_csv(CLEAN / "nb_train_binned.csv", index=False)
pd.DataFrame(Xte_bin.astype(int), columns=names_bin).assign(label=yte, row_id=test["row_id"].to_numpy()) \
    .to_csv(CLEAN / "nb_test_binned.csv", index=False)

show_cols = [c for c in names_bin if c.startswith("temp_mean") or c.startswith("solar_rad")]
tmp = pd.DataFrame(Xtr_bin.astype(int), columns=names_bin)[show_cols].assign(label=ytr)
tmp.columns = [c.replace(" to ", "-") for c in tmp.columns]
table_image(tmp, "nb_04_binned_sample.png",
            "After preparation: weather values turned into 0/1 bin columns (temp_mean and solar_rad shown)",
            highlight=["label"], ncols=11)
table_image(train[["city", "temp_mean", "precip_mm", "wind_max", "solar_rad", "month", "label"]]
            .head(8), "nb_02_train_sample.png", f"Training set ({len(train):,} rows): first rows", highlight=["label"])
table_image(test[["city", "temp_mean", "precip_mm", "wind_max", "solar_rad", "month", "label"]]
            .head(8), "nb_03_test_sample.png", f"Testing set ({len(test):,} rows): first rows", highlight=["label"])

# --- models
nb_models = {
    "Multinomial NB\n(scaled values)": (MultinomialNB(), Xtr_scaled, Xte_scaled),
    "Multinomial NB\n(binned values)": (MultinomialNB(), Xtr_bin, Xte_bin),
    "Bernoulli NB\n(binned values)": (BernoulliNB(), Xtr_bin, Xte_bin),
    "Gaussian NB\n(raw values)": (GaussianNB(), train[WEATHER].to_numpy(), test[WEATHER].to_numpy()),
}
RES["nb"] = {}
nb_preds = {}
for name, (m, A, B) in nb_models.items():
    m.fit(A, ytr)
    p = m.predict(B)
    nb_preds[name] = p
    RES["nb"][name.replace("\n", " ")] = metrics(yte, p, majority)
mn = nb_models["Multinomial NB\n(binned values)"][0]
RES["nb_priors_train"] = dict(zip(mn.classes_, map(float, np.exp(mn.class_log_prior_))))

# --- confusion matrices and comparison
fig, axes = plt.subplots(1, 4, figsize=(17, 4.6))
for ax, name in zip(axes, nb_models):
    r = RES["nb"][name.replace("\n", " ")]
    cm_panel(ax, r["confusion"], f"{name.replace(chr(10), ' ')}\naccuracy {r['accuracy']:.1%}, macro-F1 {r['macro_f1']:.2f}")
fig.suptitle("Naive Bayes confusion matrices on the testing set (cells: count and share of the actual group)",
             fontsize=12, y=1.03)
save(fig, "nb_06_confusion_matrices.png")

fig, ax = plt.subplots(figsize=(9, 4.6))
labels = [n.replace("\n", "\n") for n in nb_models]
xx = np.arange(len(labels))
acc = [RES["nb"][n.replace("\n", " ")]["accuracy"] * 100 for n in nb_models]
f1s = [RES["nb"][n.replace("\n", " ")]["macro_f1"] * 100 for n in nb_models]
b1 = ax.bar(xx - 0.2, acc, 0.4, color=BLUE, label="Accuracy")
b2 = ax.bar(xx + 0.2, f1s, 0.4, color=ORANGE, label="Macro-F1 (average over the 3 groups)")
for b in list(b1) + list(b2):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, f"{b.get_height():.0f}", ha="center", fontsize=9)
ax.axhline(RES["baseline_accuracy_test"] * 100, color="k", ls="--", lw=1)
ax.text(len(labels) - 0.5, RES["baseline_accuracy_test"] * 100 + 1.5,
        f"always predicting {majority}: {RES['baseline_accuracy_test']:.0%}", ha="right", fontsize=9)
ax.set_xticks(xx)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Score (%)")
ax.set_ylim(0, 80)
ax.grid(axis="x", visible=False)
ax.set_title("Naive Bayes variants: accuracy alone hides the failure to detect minority groups")
ax.legend(loc="upper left", fontsize=9)
save(fig, "nb_07_metrics_comparison.png")

# --- which bins push a day toward 'Unhealthy' (multinomial, binned)
flp = mn.feature_log_prob_
ci = {c: i for i, c in enumerate(mn.classes_)}
ratio = pd.Series(flp[ci["Unhealthy"]] - flp[ci["Good"]], index=names_bin).sort_values()
sel = pd.concat([ratio.head(7), ratio.tail(7)])
fig, ax = plt.subplots(figsize=(9, 5.4))
ax.barh(sel.index, sel.values, color=[BLUE if v < 0 else "#d1495b" for v in sel.values])
ax.axvline(0, color="k", lw=0.8)
ax.set_xlabel("log( P(bin | Unhealthy) / P(bin | Good) )")
ax.set_title("Weather conditions that most separate Unhealthy days from Good days")
ax.grid(axis="y", visible=False)
save(fig, "nb_08_top_bins.png")
RES["nb_top_unhealthy_bins"] = ratio.tail(5).round(3).to_dict()
RES["nb_top_good_bins"] = ratio.head(5).round(3).to_dict()

# --- overview figures: ingredients of NB (priors and class-conditional distributions)
fig, axes = plt.subplots(1, 3, figsize=(13, 3.9))
pri = train["label"].value_counts(normalize=True).reindex(CLASSES) * 100
axes[0].bar(CLASSES, pri.values, color=[CCOL[c] for c in CLASSES])
for i, v in enumerate(pri.values):
    axes[0].text(i, v + 1, f"{v:.0f}%", ha="center", fontsize=9)
axes[0].set_title("Prior: P(group)", fontsize=10)
axes[0].set_ylabel("Share of training days (%)")
axes[0].grid(axis="x", visible=False)
for ax, col, ttl in [(axes[1], "solar_rad", "Likelihood: solar radiation given group"),
                     (axes[2], "temp_mean", "Likelihood: mean temperature given group")]:
    for c in CLASSES:
        sns.kdeplot(train.loc[train["label"] == c, col], ax=ax, color=CCOL[c], fill=True, alpha=0.25, label=c,
                    common_norm=False, bw_adjust=1.2)
    ax.set_title(ttl, fontsize=10)
    ax.set_xlabel("Solar radiation (MJ/m2 per day)" if col == "solar_rad" else "Mean temperature (C)")
    ax.set_ylabel("Density")
axes[1].legend(fontsize=8)
fig.suptitle("Ingredients of Naive Bayes, estimated from the training days", fontsize=12, y=1.04)
save(fig, "nb_00a_ingredients.png")

# multinomial vs bernoulli schematic (one real day, real bin edges)
ex = test.iloc[[0]]
row = kb.transform(ex[WEATHER])[0].reshape(-1)
fig, ax = plt.subplots(figsize=(11, 3.7))
ax.axis("off")
off = 0
for fi, (col, edges) in enumerate(zip(WEATHER, kb.bin_edges_)):
    nbin = len(edges) - 1
    if col in ("temp_mean", "precip_mm", "wind_max", "solar_rad"):
        y0 = 0.74 - ["temp_mean", "precip_mm", "wind_max", "solar_rad"].index(col) * 0.2
        ax.text(0.0, y0 + 0.04, col, fontsize=10, va="center", fontweight="bold")
        for b in range(nbin):
            on = row[off + b] == 1
            ax.add_patch(plt.Rectangle((0.2 + b * 0.09, y0), 0.08, 0.1, fc=BLUE if on else "white", ec=GREY))
            ax.text(0.24 + b * 0.09, y0 + 0.05, "1" if on else "0", ha="center", va="center", fontsize=9,
                    color="white" if on else GREY)
    off += nbin
ax.text(0.2, 0.93, "One day, turned into 0/1 bin columns (each weather variable has up to 5 bins)",
        fontsize=10, fontweight="bold")
ax.text(0.68, 0.72, "Multinomial NB", fontsize=11, fontweight="bold", color=BLUE)
ax.text(0.68, 0.62, "counts how often each bin occurs.\nOnly bins that occur (the 1s)\nadd evidence to a group.", fontsize=9.5, va="top")
ax.text(0.68, 0.34, "Bernoulli NB", fontsize=11, fontweight="bold", color=ORANGE)
ax.text(0.68, 0.24, "models every bin as yes/no.\nBins that do NOT occur (the 0s)\nalso add evidence.", fontsize=9.5, va="top")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
save(fig, "nb_00b_multinomial_vs_bernoulli.png")
RES["example_row"] = {"city": str(ex["city"].iloc[0]), "date": str(ex["date"].iloc[0].date())}

# --- location extension and time-based holdout for NB
kb_l = make_binner(WEATHER_LOC, train)
A, B = kb_l.transform(train[WEATHER_LOC]), kb_l.transform(test[WEATHER_LOC])
m = MultinomialNB().fit(A, ytr)
RES["nb_location"] = metrics(yte, m.predict(B), majority)
tr_t, te_t = d[d["month"] <= 9], d[d["month"] >= 10]
kb_t = make_binner(WEATHER, tr_t)
m = MultinomialNB().fit(kb_t.transform(tr_t[WEATHER]), tr_t["label"])
maj_t = tr_t["label"].mode()[0]
RES["nb_time_holdout"] = metrics(te_t["label"], m.predict(kb_t.transform(te_t[WEATHER])), maj_t)
RES["time_holdout_rows"] = {"train": int(len(tr_t)), "test": int(len(te_t))}

# ============================================================================ DECISION TREES
dtr, dte = train[WEATHER_LOC + ["label", "row_id"]], test[WEATHER_LOC + ["label", "row_id"]]
dtr.to_csv(CLEAN / "dt_train.csv", index=False)
dte.to_csv(CLEAN / "dt_test.csv", index=False)

# depth selection by 5-fold cross-validation on the training set only
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
sweep = {}
for crit in ["gini", "entropy"]:
    for feats_name, feats in [("weather", WEATHER), ("weather+location", WEATHER_LOC)]:
        rows = []
        for depth in range(1, 16):
            t = DecisionTreeClassifier(criterion=crit, max_depth=depth, random_state=SEED)
            cvs = cross_val_score(t, train[feats], ytr, cv=cv).mean()
            rows.append((depth, t.fit(train[feats], ytr).score(train[feats], ytr), cvs))
        sweep[(crit, feats_name)] = rows
best = {k: max(v, key=lambda r: (round(r[2], 4), -r[0]))[0] for k, v in sweep.items()}
RES["best_depth_cv"] = {f"{k[0]}|{k[1]}": int(v) for k, v in best.items()}

fig, axes = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
for ax, fn in zip(axes, ["weather", "weather+location"]):
    for crit, col in [("gini", BLUE), ("entropy", ORANGE)]:
        r = np.array(sweep[(crit, fn)])
        ax.plot(r[:, 0], r[:, 1] * 100, color=col, ls="--", alpha=0.6, label=f"{crit}: training accuracy")
        ax.plot(r[:, 0], r[:, 2] * 100, color=col, lw=2, label=f"{crit}: cross-validated accuracy")
        ax.scatter([best[(crit, fn)]], [r[best[(crit, fn)] - 1, 2] * 100], color=col, s=70, zorder=5, edgecolor="k")
    ax.axhline(RES["baseline_accuracy_test"] * 100, color="k", ls=":", lw=1)
    ax.set_xlabel("Maximum tree depth")
    ax.set_title(f"Features: {fn}", fontsize=10)
axes[0].set_ylabel("Accuracy (%)")
axes[0].legend(fontsize=8, loc="lower right")
fig.suptitle("Deeper trees fit the training data better, but cross-validated accuracy levels off (dot = chosen depth)",
             fontsize=11, y=1.02)
save(fig, "dt_04_depth_sweep.png")

# --- the three required trees plus tuned trees
specs = {
    "Tree 1: Gini, depth 3, weather": ("gini", 3, WEATHER),
    "Tree 2: Entropy, depth 3, weather": ("entropy", 3, WEATHER),
    "Tree 3: Gini, depth 4, weather + location": ("gini", 4, WEATHER_LOC),
    f"Tuned: Gini, depth {best[('gini', 'weather')]}, weather": ("gini", best[("gini", "weather")], WEATHER),
    f"Tuned: Gini, depth {best[('gini', 'weather+location')]}, weather + location":
        ("gini", best[("gini", "weather+location")], WEATHER_LOC),
}
trees, RES["dt"] = {}, {}
for name, (crit, depth, feats) in specs.items():
    t = DecisionTreeClassifier(criterion=crit, max_depth=depth, random_state=SEED).fit(train[feats], ytr)
    trees[name] = (t, feats)
    r = metrics(yte, t.predict(test[feats]), majority)
    r.update({"criterion": crit, "depth": int(depth), "leaves": int(t.get_n_leaves()),
              "train_accuracy": float(t.score(train[feats], ytr))})
    RES["dt"][name] = r

for fname, key, w in [("dt_tree1_gini_depth3.png", "Tree 1: Gini, depth 3, weather", (19, 8.5)),
                      ("dt_tree2_entropy_depth3.png", "Tree 2: Entropy, depth 3, weather", (19, 8.5)),
                      ("dt_tree3_gini_depth4_location.png", "Tree 3: Gini, depth 4, weather + location", (27, 10))]:
    t, feats = trees[key]
    fig, ax = plt.subplots(figsize=w)
    plot_tree(t, feature_names=feats, class_names=CLASSES, filled=True, rounded=True, fontsize=9, ax=ax, precision=2)
    ax.set_title(key, fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(IMG / fname, dpi=100)
    plt.close(fig)

tuned_w = [k for k in trees if k.startswith("Tuned") and "location" not in k][0]
tuned_wl = [k for k in trees if k.startswith("Tuned") and "location" in k][0]
panel = ["Tree 1: Gini, depth 3, weather", "Tree 2: Entropy, depth 3, weather",
         "Tree 3: Gini, depth 4, weather + location", tuned_w]
fig, axes = plt.subplots(1, 4, figsize=(17, 4.8))
for ax, k in zip(axes, panel):
    r = RES["dt"][k]
    cm_panel(ax, r["confusion"], f"{k.split(',')[0]}, {k.split(',')[1].strip()}\naccuracy {r['accuracy']:.1%}, macro-F1 {r['macro_f1']:.2f}")
fig.suptitle("Decision tree confusion matrices on the testing set (cells: count and share of the actual group)",
             fontsize=12, y=1.03)
save(fig, "dt_05_confusion_matrices.png")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharex=True)
for ax, k in zip(axes, [tuned_w, tuned_wl]):
    t, feats = trees[k]
    imp = pd.Series(t.feature_importances_, index=feats).sort_values()
    ax.barh(imp.index, imp.values * 100, color=BLUE)
    ax.set_title(k.replace("Tuned: ", "Tuned tree: "), fontsize=9.5)
    ax.set_xlabel("Share of total impurity reduction (%)")
    ax.grid(axis="y", visible=False)
    RES["dt"][k]["importance"] = imp.round(4).to_dict()
fig.suptitle("Which inputs the trees rely on", fontsize=12, y=1.02)
save(fig, "dt_06_importance.png")

# --- worked example of a split on the root of Tree 1 (training data)
t1, f1_ = trees["Tree 1: Gini, depth 3, weather"]
feat, thr = f1_[t1.tree_.feature[0]], float(t1.tree_.threshold[0])
mask = train[feat] <= thr
parts = {"parent": ytr, "left": ytr[mask.to_numpy()], "right": ytr[~mask.to_numpy()]}


def counts(arr):
    return np.array([(arr == c).sum() for c in CLASSES])


def gini(c):
    p = c / c.sum()
    return float(1 - (p ** 2).sum())


def entropy(c):
    p = c / c.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


ex_ = {}
for k, arr in parts.items():
    c = counts(arr)
    ex_[k] = {"counts": c.tolist(), "n": int(c.sum()), "gini": gini(c), "entropy": entropy(c)}
n, nl, nr = ex_["parent"]["n"], ex_["left"]["n"], ex_["right"]["n"]
ex_["weighted_gini"] = (nl * ex_["left"]["gini"] + nr * ex_["right"]["gini"]) / n
ex_["weighted_entropy"] = (nl * ex_["left"]["entropy"] + nr * ex_["right"]["entropy"]) / n
ex_["gini_gain"] = ex_["parent"]["gini"] - ex_["weighted_gini"]
ex_["information_gain"] = ex_["parent"]["entropy"] - ex_["weighted_entropy"]
ex_["feature"], ex_["threshold"] = feat, thr
RES["split_example"] = ex_

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.axis("off")
boxes = [("parent", 0.5, 0.72, f"All {n:,} training days"),
         ("left", 0.22, 0.14, f"{feat} <= {thr:.2f}"),
         ("right", 0.78, 0.14, f"{feat} > {thr:.2f}")]
for key, x0, y0, ttl in boxes:
    c = np.array(ex_[key]["counts"])
    left, w = x0 - 0.17, 0.34
    ax.text(x0, y0 + 0.17, ttl, ha="center", fontsize=10.5, fontweight="bold")
    cum = 0
    for cls, v in zip(CLASSES, c):
        ax.add_patch(plt.Rectangle((left + cum / c.sum() * w, y0 + 0.02), v / c.sum() * w, 0.1, fc=CCOL[cls], ec="white"))
        cum += v
    ax.text(x0, y0 - 0.04, f"n = {c.sum():,}   Gini = {ex_[key]['gini']:.3f}   Entropy = {ex_[key]['entropy']:.3f}",
            ha="center", fontsize=9)
for x1 in (0.22, 0.78):
    ax.annotate("", xy=(x1, 0.4), xytext=(0.5, 0.64), arrowprops=dict(arrowstyle="->", color=GREY))
ax.text(0.5, -0.17, f"Gini gain = {ex_['parent']['gini']:.3f} - {ex_['weighted_gini']:.3f} = {ex_['gini_gain']:.3f}\n"
        f"Information gain = {ex_['parent']['entropy']:.3f} - {ex_['weighted_entropy']:.3f} = {ex_['information_gain']:.3f}",
        ha="center", va="center", fontsize=10.5, bbox=dict(boxstyle="round", fc="#eef3fd", ec=BLUE))
for i, cls in enumerate(CLASSES):
    ax.add_patch(plt.Rectangle((0.02 + i * 0.13, 0.95), 0.025, 0.04, fc=CCOL[cls], ec="none"))
    ax.text(0.05 + i * 0.13, 0.97, cls, va="center", fontsize=9)
ax.set_xlim(0, 1)
ax.set_ylim(-0.3, 1.02)
save(fig, "dt_00c_split_example.png")

# --- impurity curves (two-group case)
p = np.linspace(0.0005, 0.9995, 400)
fig, ax = plt.subplots(figsize=(7.5, 4.3))
ax.plot(p, 1 - p ** 2 - (1 - p) ** 2, color=BLUE, lw=2.5, label="Gini  = 1 - p1^2 - p2^2")
ax.plot(p, -p * np.log2(p) - (1 - p) * np.log2(1 - p), color=ORANGE, lw=2.5, label="Entropy = -p1 log2 p1 - p2 log2 p2")
ax.axvline(0.5, color=GREY, ls=":")
ax.set_xlabel("Share of the first group in a node (p1)")
ax.set_ylabel("Impurity")
ax.set_title("Both measures are 0 for a pure node and largest for a 50/50 node")
ax.legend(loc="lower center", fontsize=9)
save(fig, "dt_00b_impurity_curves.png")

# --- anatomy of a small tree (real depth-2 tree on the training data)
t2 = DecisionTreeClassifier(max_depth=2, random_state=SEED).fit(train[WEATHER], ytr)
T = t2.tree_
pos, counter = {}, [0]


def layout(nid, depth):
    if T.children_left[nid] == -1:
        pos[nid] = (counter[0], depth)
        counter[0] += 1
    else:
        layout(T.children_left[nid], depth + 1)
        layout(T.children_right[nid], depth + 1)
        pos[nid] = ((pos[T.children_left[nid]][0] + pos[T.children_right[nid]][0]) / 2, depth)


layout(0, 0)
nleaf = counter[0]
pos = {k: ((x + 0.5) / nleaf, 0.84 - dep * 0.36) for k, (x, dep) in pos.items()}
fig, ax = plt.subplots(figsize=(11, 5.2))
ax.axis("off")
for nid, (x0, y0) in pos.items():
    if T.children_left[nid] != -1:
        txt = f"{WEATHER[T.feature[nid]]} <= {T.threshold[nid]:.1f}?\ngini = {T.impurity[nid]:.2f}\nsamples = {T.n_node_samples[nid]:,}"
        fc = "#eef3fd"
    else:
        cls = t2.classes_[int(np.argmax(T.value[nid]))]
        txt = f"Predict: {cls}\ngini = {T.impurity[nid]:.2f}\nsamples = {T.n_node_samples[nid]:,}"
        fc = CCOL[cls] + "55"
    ax.text(x0, y0, txt, ha="center", va="center", fontsize=8.5, bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec=GREY))
    if T.children_left[nid] != -1:
        for ch, lab in [(T.children_left[nid], "yes"), (T.children_right[nid], "no")]:
            cx, cy = pos[ch]
            ax.annotate("", xy=(cx, cy + 0.1), xytext=(x0, y0 - 0.1), arrowprops=dict(arrowstyle="->", color=GREY))
            ax.text((x0 + cx) / 2 + (-0.02 if lab == "yes" else 0.02), (y0 + cy) / 2, lab, fontsize=9, color=BLUE,
                    ha="center")
ax.text(0.5, 0.99, "Root node: the first question", ha="center", fontsize=10, fontweight="bold", color=BLUE)
ax.text(0.02, 0.5, "Decision (internal)\nnode: another question", fontsize=9.5, fontweight="bold", color=BLUE, va="center")
ax.text(0.5, 0.0, "Leaf nodes: no more questions, the node predicts its majority group", ha="center",
        fontsize=10, fontweight="bold", color=BLUE)
ax.set_xlim(0, 1)
ax.set_ylim(-0.04, 1.03)
save(fig, "dt_00a_tree_anatomy.png")

# --- data prep pictures for the DT tab
table_image(dtr[["row_id", "temp_mean", "precip_mm", "wind_max", "solar_rad", "month", "latitude", "label"]].head(8),
            "dt_02_train_sample.png", f"Training set ({len(dtr):,} rows): first rows", highlight=["label"])
table_image(dte[["row_id", "temp_mean", "precip_mm", "wind_max", "solar_rad", "month", "latitude", "label"]].head(8),
            "dt_03_test_sample.png", f"Testing set ({len(dte):,} rows): first rows", highlight=["label"])

# --- time-based holdout for the trees
for key in ["Tree 1: Gini, depth 3, weather"]:
    crit, depth, feats = specs[key]
    t = DecisionTreeClassifier(criterion=crit, max_depth=depth, random_state=SEED).fit(tr_t[feats], tr_t["label"])
    RES["dt_time_holdout"] = metrics(te_t["label"], t.predict(te_t[feats]), maj_t)
    ct, dpt, fts = specs[tuned_w]
    t = DecisionTreeClassifier(criterion=ct, max_depth=dpt, random_state=SEED).fit(tr_t[fts], tr_t["label"])
    RES["dt_time_holdout_tuned"] = metrics(te_t["label"], t.predict(te_t[fts]), maj_t)
RES["dt_names"] = {"tuned_weather": tuned_w, "tuned_location": tuned_wl}

(CLEAN / "nb_dt_results.json").write_text(json.dumps(RES, indent=2, default=str), encoding="utf-8")
print("rows", RES["n_rows"], "baseline", round(RES["baseline_accuracy_test"], 3))
for k, v in RES["nb"].items():
    print("NB", k, round(v["accuracy"], 3), round(v["macro_f1"], 3), v["predicted_counts"])
for k, v in RES["dt"].items():
    print("DT", k, round(v["accuracy"], 3), round(v["macro_f1"], 3), "train", round(v["train_accuracy"], 3))
print("time holdout NB", round(RES["nb_time_holdout"]["accuracy"], 3), "baseline", round(RES["nb_time_holdout"]["baseline_accuracy"], 3),
      "DT", round(RES["dt_time_holdout"]["accuracy"], 3))
