"""Clean the raw data and create the exploratory figures for the DataPrep_EDA tab.

Input : data/raw/*.csv           (created by 01_gather_data.py)
Output: data/clean/*.csv, images/*.png

Run:  python code/02_clean_eda.py
"""
import ast
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, IMG = ROOT / "data" / "raw", ROOT / "data" / "clean", ROOT / "images"
CLEAN.mkdir(exist_ok=True)
IMG.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
BLUE, ORANGE, RED, GREY = "#2a6fdb", "#f28e2b", "#d1495b", "#6b7280"

REGION = {  # US Census regions
    **dict.fromkeys(["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"], "Northeast"),
    **dict.fromkeys(["IL", "IN", "MI", "OH", "WI", "IA", "KS", "MN", "MO", "NE", "ND", "SD"], "Midwest"),
    **dict.fromkeys(["DE", "DC", "FL", "GA", "MD", "NC", "SC", "VA", "WV", "AL", "KY", "MS", "TN",
                     "AR", "LA", "OK", "TX"], "South"),
    **dict.fromkeys(["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY", "AK", "CA", "HI", "OR", "WA"], "West"),
}
AQI_BINS = [-1, 50, 100, 150, 200, 300, 1000]
AQI_LABELS = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
AQI_COLORS = ["#2e9e5b", "#f2c94c", "#f28e2b", "#d1495b", "#8e44ad", "#7b1e3a"]
LOG = []


def log(msg):
    print(msg)
    LOG.append(msg)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=130)
    plt.close(fig)


def table_image(df, name, title, nrows=8):
    """Render the head of a dataframe as a small image (used for RAW / CLEAN previews)."""
    sample = df.head(nrows).copy()
    sample = sample.iloc[:, :9]
    for c in sample.columns:
        if sample[c].dtype.kind == "f":
            sample[c] = sample[c].round(2)
    fig, ax = plt.subplots(figsize=(min(2 + 1.25 * sample.shape[1], 14), 0.5 * nrows + 1.2))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    t = ax.table(cellText=sample.astype(str).values, colLabels=sample.columns, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.scale(1, 1.4)
    for (r, _), cell in t.get_celld().items():
        if r == 0:
            cell.set_facecolor("#e8eefc")
            cell.set_text_props(fontweight="bold")
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=130)
    plt.close(fig)


# ----------------------------------------------------------------------------- load raw
aq_raw = pd.read_csv(RAW / "openmeteo_air_quality_hourly_raw.csv")
wx_raw = pd.read_csv(RAW / "openmeteo_weather_daily_raw.csv")
places_raw = pd.read_csv(RAW / "cdc_places_county_raw.csv", dtype={"locationid": str})
cities = pd.read_csv(RAW / "cities_reference.csv")

table_image(aq_raw, "raw_air_quality.png", "RAW: Open-Meteo hourly air quality (first rows)")
table_image(wx_raw, "raw_weather.png", "RAW: Open-Meteo daily weather (first rows)")
table_image(places_raw[["year", "stateabbr", "locationname", "measureid", "data_value_type",
                        "data_value", "low_confidence_limit", "high_confidence_limit", "totalpopulation"]],
            "raw_cdc_places.png", "RAW: CDC PLACES county health measures (first rows)")

log(f"Raw shapes  air quality {aq_raw.shape}, weather {wx_raw.shape}, CDC PLACES {places_raw.shape}")

# ----------------------------------------------------------------------------- figure 1: missingness (raw)
miss = pd.concat([aq_raw.isna().mean(), wx_raw.isna().mean()]).drop(["city", "state", "time"], errors="ignore")
miss = miss[miss > 0].sort_values()
fig, ax = plt.subplots(figsize=(8, 4.5))
if len(miss):
    ax.barh(miss.index, miss.values * 100, color=ORANGE)
else:
    ax.text(0.5, 0.5, "No missing values in raw API data", ha="center", va="center", transform=ax.transAxes)
ax.set_xlabel("Missing values (%)")
ax.set_title("Share of missing values per column in the raw API data")
save(fig, "eda_01_missing_raw.png")
log("Missing (raw, % of rows):\n" + (miss * 100).round(2).to_string() if len(miss) else "Missing (raw): none")

# ----------------------------------------------------------------------------- clean air quality
aq = aq_raw.copy()
aq["time"] = pd.to_datetime(aq["time"])
before = len(aq)
aq = aq.drop_duplicates(["city", "time"])
log(f"Air quality: removed {before - len(aq)} duplicate city-hour rows")

pollutants = ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "us_aqi"]
neg = int((aq[pollutants] < 0).sum().sum())
aq[pollutants] = aq[pollutants].clip(lower=0)
log(f"Air quality: {neg} negative concentration values set to 0")

n_na = int(aq[pollutants].isna().sum().sum())
aq = aq.sort_values(["city", "time"])
aq[pollutants] = aq.groupby("city")[pollutants].transform(lambda s: s.interpolate(limit=6, limit_direction="both"))
log(f"Air quality: {n_na} missing hourly values; short gaps (<=6 h) linearly interpolated, "
    f"{int(aq[pollutants].isna().sum().sum())} remain")
aq = aq.dropna(subset=pollutants)

aq["date"] = aq["time"].dt.date.astype(str)
daily_aq = aq.groupby(["city", "state", "date"]).agg(
    pm2_5=("pm2_5", "mean"), pm10=("pm10", "mean"), co=("carbon_monoxide", "mean"),
    no2=("nitrogen_dioxide", "mean"), so2=("sulphur_dioxide", "mean"), ozone_max=("ozone", "max"),
    aqi_max=("us_aqi", "max"), hours=("time", "count")).reset_index()
daily_aq = daily_aq[daily_aq["hours"] >= 18].drop(columns="hours")   # keep days with >=18 valid hours

# ----------------------------------------------------------------------------- clean weather
wx = wx_raw.copy().drop_duplicates(["city", "date" if "date" in wx_raw else "time"])
wx = wx.rename(columns={"time": "date"})
wcols = [c for c in wx.columns if c not in ("city", "state", "date")]
log(f"Weather: {int(wx[wcols].isna().sum().sum())} missing values")
wx[wcols] = wx.groupby("city")[wcols].transform(lambda s: s.interpolate(limit=3, limit_direction="both"))
wx = wx.dropna(subset=wcols)
wx = wx.rename(columns={"temperature_2m_mean": "temp_mean", "temperature_2m_max": "temp_max",
                        "temperature_2m_min": "temp_min", "precipitation_sum": "precip_mm",
                        "wind_speed_10m_max": "wind_max", "shortwave_radiation_sum": "solar_rad"})
wx["precip_mm"] = wx["precip_mm"].clip(lower=0)

daily = daily_aq.merge(wx, on=["city", "state", "date"], how="inner")
daily["date"] = pd.to_datetime(daily["date"])
daily["month"] = daily["date"].dt.month
daily["season"] = daily["month"].map({12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring",
                                      5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer",
                                      9: "Fall", 10: "Fall", 11: "Fall"})
daily["region"] = daily["state"].map(REGION)
daily["aqi_category"] = pd.cut(daily["aqi_max"], AQI_BINS, labels=AQI_LABELS)
daily["rainy"] = np.where(daily["precip_mm"] >= 1, "Rain (>=1 mm)", "Dry")

# outliers: physically implausible values only (extreme smoke days are real and are kept)
for col, hi in [("pm2_5", 1000), ("pm10", 2000), ("temp_mean", 60), ("wind_max", 200)]:
    bad = daily[col] > hi
    if bad.any():
        log(f"Outliers: dropping {int(bad.sum())} rows with {col} > {hi}")
        daily = daily[~bad]
log(f"Clean daily city table: {daily.shape}, cities {daily.city.nunique()}, NAs {int(daily.isna().sum().sum())}")
daily.to_csv(CLEAN / "daily_city_air_weather_clean.csv", index=False)
table_image(daily.drop(columns=["season", "rainy", "region"]), "clean_daily.png",
            "CLEAN: daily city air quality + weather (first rows)")

# ----------------------------------------------------------------------------- clean health (CDC PLACES)
pl = places_raw.copy()
pl = pl[pl["data_value_type"] == "Crude prevalence"].copy()
pl["data_value"] = pd.to_numeric(pl["data_value"], errors="coerce")
log(f"CDC PLACES: {int(pl['data_value'].isna().sum())} crude prevalence values are missing and dropped")
pl = pl.dropna(subset=["data_value"])
health = pl.pivot_table(index=["stateabbr", "locationname", "locationid"], columns="measureid",
                        values="data_value", aggfunc="first").reset_index()
health = health.rename(columns={"CASTHMA": "asthma", "COPD": "copd", "CSMOKING": "smoking",
                                "OBESITY": "obesity", "DIABETES": "diabetes", "ACCESS2": "uninsured",
                                "BPHIGH": "high_bp", "CHD": "heart_disease", "DEPRESSION": "depression",
                                "LPA": "inactivity", "stateabbr": "state", "locationname": "county"})
pop = pl.drop_duplicates("locationid").set_index("locationid")["totalpopulation"]
health["population"] = health["locationid"].map(pop).astype(float)


def coords(s):
    try:
        lon, lat = ast.literal_eval(s)["coordinates"] if isinstance(s, str) and s.startswith("{") else (np.nan,) * 2
    except Exception:
        lon, lat = np.nan, np.nan
    return lon, lat


geo_col = "geolocation.coordinates"
if geo_col in pl:
    g = pl.drop_duplicates("locationid").set_index("locationid")[geo_col]
    parsed = g.map(lambda v: ast.literal_eval(v) if isinstance(v, str) else [np.nan, np.nan])
    health["lon"] = health["locationid"].map(parsed.map(lambda v: v[0]))
    health["lat"] = health["locationid"].map(parsed.map(lambda v: v[1]))
health = health.dropna(subset=["asthma", "copd", "smoking", "obesity"])
health["region"] = health["state"].map(REGION)
log(f"Clean county health table: {health.shape}, NAs in key columns {int(health[['asthma','copd','smoking','obesity']].isna().sum().sum())}")
health.to_csv(CLEAN / "county_health_clean.csv", index=False)
table_image(health, "clean_health.png", "CLEAN: county health prevalence (%) (first rows)")

# ----------------------------------------------------------------------------- city-level table
grp = daily.groupby(["city", "state"])
city = grp.agg(pm2_5_mean=("pm2_5", "mean"), pm2_5_p95=("pm2_5", lambda s: s.quantile(0.95)),
               pm10_mean=("pm10", "mean"), no2_mean=("no2", "mean"), so2_mean=("so2", "mean"),
               co_mean=("co", "mean"), ozone_max_mean=("ozone_max", "mean"),
               aqi_mean=("aqi_max", "mean"), temp_mean=("temp_mean", "mean"),
               precip_total=("precip_mm", "sum"), wind_mean=("wind_max", "mean"),
               days=("date", "count")).reset_index()
city["unhealthy_day_share"] = grp["aqi_max"].apply(lambda s: (s > 100).mean()).values
city = city.merge(cities[["city", "state", "county", "latitude", "longitude"]], on=["city", "state"])
city["region"] = city["state"].map(REGION)
city["_k"] = city["county"].str.lower()
health["_k"] = health["county"].str.lower()
city = city.merge(health.drop(columns=["county", "region", "lat", "lon", "locationid"], errors="ignore"),
                  left_on=["state", "_k"], right_on=["state", "_k"], how="left").drop(columns="_k")
no_match = city[city["asthma"].isna()]["city"].tolist()
log(f"City table: {len(city)} cities; no CDC county record for {no_match} (PA/KY absent and independent "
    f"cities not in PLACES) -> dropped from the merged city table")
city = city.dropna(subset=["asthma", "copd"]).reset_index(drop=True)
city["asthma_level"] = np.where(city["asthma"] >= city["asthma"].median(), "High", "Low")
city["pm_level"] = pd.qcut(city["pm2_5_mean"], 3, labels=["Low", "Medium", "High"])
log(f"Clean merged city table: {city.shape}, NAs {int(city.isna().sum().sum())}")
city.to_csv(CLEAN / "city_air_weather_health_clean.csv", index=False)
table_image(city[["city", "state", "pm2_5_mean", "no2_mean", "ozone_max_mean", "temp_mean",
                  "asthma", "copd", "smoking", "asthma_level"]],
            "clean_city.png", "CLEAN: city-level air, weather and health features (first rows)")

# ============================================================================= EDA figures
# 2 distribution of daily PM2.5
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(daily["pm2_5"].clip(upper=80), bins=60, color=BLUE, alpha=0.85)
ax.axvline(15, color=RED, ls="--", label="WHO 24-hour guideline (15 ug/m3)")
ax.axvline(daily["pm2_5"].median(), color=ORANGE, ls="-", label=f"Median ({daily['pm2_5'].median():.1f})")
ax.set_xlabel("Daily mean PM2.5 (ug/m3, clipped at 80)")
ax.set_ylabel("City-days")
ax.set_title("Distribution of daily PM2.5 across 55 US cities, 2023")
ax.legend()
save(fig, "eda_02_pm25_distribution.png")

# 3 monthly seasonality
fig, ax = plt.subplots(figsize=(9, 4.5))
sns.boxplot(data=daily, x="month", y="pm2_5", color=BLUE, fliersize=1, ax=ax)
ax.set_ylim(0, 60)
ax.set_xlabel("Month of 2023")
ax.set_ylabel("Daily mean PM2.5 (ug/m3)")
ax.set_title("Monthly variation of PM2.5 (all cities)")
save(fig, "eda_03_monthly_pm25.png")

# 4 city ranking
rank = city.sort_values("pm2_5_mean")
show = pd.concat([rank.head(10), rank.tail(10)])
fig, ax = plt.subplots(figsize=(8, 6.5))
ax.barh(show["city"], show["pm2_5_mean"], color=[BLUE] * 10 + [RED] * 10)
ax.set_xlabel("Mean daily PM2.5 in 2023 (ug/m3)")
ax.set_title("Cleanest (blue) and most polluted (red) cities by PM2.5")
save(fig, "eda_04_city_ranking.png")

# 5 AQI categories
cat_counts = daily["aqi_category"].value_counts().reindex(AQI_LABELS).fillna(0)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(range(len(cat_counts)), cat_counts.values, color=AQI_COLORS)
ax.set_xticks(range(len(cat_counts)))
ax.set_xticklabels([l.replace(" for Sensitive", "\nfor Sensitive").replace("Very Unhealthy", "Very\nUnhealthy")
                    for l in AQI_LABELS], fontsize=9)
ax.set_ylabel("City-days")
ax.set_yscale("log")
ax.set_title("City-days in each US AQI category (log scale)")
save(fig, "eda_05_aqi_categories.png")

# 6 correlation heatmap
corr_cols = ["pm2_5", "pm10", "no2", "so2", "co", "ozone_max", "aqi_max", "temp_mean", "precip_mm",
             "wind_max", "solar_rad"]
fig, ax = plt.subplots(figsize=(8.5, 7))
sns.heatmap(daily[corr_cols].corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
            annot_kws={"size": 7}, ax=ax, cbar_kws={"shrink": 0.8})
ax.set_title("Correlation between pollutants and weather (daily, all cities)")
save(fig, "eda_06_correlation_heatmap.png")

# 7 temperature vs ozone
fig, ax = plt.subplots(figsize=(8, 5))
hb = ax.hexbin(daily["temp_mean"], daily["ozone_max"], gridsize=45, cmap="viridis", mincnt=1, bins="log")
fig.colorbar(hb, ax=ax, label="City-days (log)")
ax.set_xlabel("Daily mean temperature (C)")
ax.set_ylabel("Daily maximum ozone (ug/m3)")
ax.set_title("Warmer days tend to have higher ozone")
save(fig, "eda_07_temp_ozone.png")

# 8 wildfire smoke event
fig, ax = plt.subplots(figsize=(9.5, 4.8))
for c, col in zip(["New York", "Boston", "Chicago", "Denver", "Phoenix"],
                  [RED, ORANGE, BLUE, "#2e9e5b", GREY]):
    s = daily[(daily.city == c) & (daily.date >= "2023-05-15") & (daily.date <= "2023-07-31")]
    ax.plot(s["date"], s["pm2_5"], label=c, color=col, lw=1.8)
ax.set_ylabel("Daily mean PM2.5 (ug/m3)")
ax.set_title("Canadian wildfire smoke episode, June 2023: PM2.5 in five cities")
ax.legend(ncol=5, fontsize=8)
fig.autofmt_xdate()
save(fig, "eda_08_wildfire_episode.png")

# 9 rain vs dry
fig, ax = plt.subplots(figsize=(6.5, 4.8))
sns.boxplot(data=daily, x="rainy", y="pm2_5", order=["Dry", "Rain (>=1 mm)"],
            palette=[ORANGE, BLUE], fliersize=1, ax=ax)
ax.set_ylim(0, 40)
ax.set_xlabel("")
ax.set_ylabel("Daily mean PM2.5 (ug/m3)")
ax.set_title("PM2.5 on dry days vs rainy days")
save(fig, "eda_09_rain_vs_dry.png")

# 10 asthma distribution across counties
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(health["asthma"], bins=40, color=BLUE, alpha=0.85)
ax.axvline(health["asthma"].median(), color=RED, ls="--", label=f"Median {health['asthma'].median():.1f}%")
ax.set_xlabel("Adults with current asthma (%)")
ax.set_ylabel("US counties")
ax.set_title(f"Asthma prevalence across {len(health):,} US counties (CDC PLACES 2023)")
ax.legend()
save(fig, "eda_10_asthma_distribution.png")

# 11 PM2.5 vs asthma (city level)
fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.regplot(data=city, x="pm2_5_mean", y="asthma", scatter_kws={"s": 45, "color": BLUE},
            line_kws={"color": RED}, ax=ax)
for _, r in city.nlargest(4, "pm2_5_mean").iterrows():
    ax.annotate(r["city"], (r["pm2_5_mean"], r["asthma"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
for _, r in city.nlargest(3, "asthma").iterrows():
    ax.annotate(r["city"], (r["pm2_5_mean"], r["asthma"]), fontsize=8, xytext=(4, -10), textcoords="offset points")
ax.set_xlabel("Mean daily PM2.5 in 2023 (ug/m3)")
ax.set_ylabel("Adult asthma prevalence (%)")
r_val = city["pm2_5_mean"].corr(city["asthma"])
ax.set_title(f"City PM2.5 vs county asthma prevalence (r = {r_val:.2f})")
save(fig, "eda_11_pm25_vs_asthma.png")

# 12 smoking vs COPD (county)
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(health["smoking"], health["copd"], s=6, alpha=0.35, color=BLUE)
m, b = np.polyfit(health["smoking"], health["copd"], 1)
xs = np.linspace(health["smoking"].min(), health["smoking"].max(), 50)
ax.plot(xs, m * xs + b, color=RED)
ax.set_xlabel("Adults who currently smoke (%)")
ax.set_ylabel("Adults with COPD (%)")
ax.set_title(f"Smoking and COPD prevalence across counties (r = {health['smoking'].corr(health['copd']):.2f})")
save(fig, "eda_12_smoking_vs_copd.png")

# 13 map of mean PM2.5
fig, ax = plt.subplots(figsize=(10, 5.5))
mainland = city[(city.state != "AK") & (city.state != "HI")]
sc = ax.scatter(mainland["longitude"], mainland["latitude"], c=mainland["pm2_5_mean"], s=90,
                cmap="YlOrRd", edgecolor="k", linewidth=0.4)
fig.colorbar(sc, ax=ax, label="Mean PM2.5 (ug/m3)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Mean PM2.5 by city location (contiguous US)")
save(fig, "eda_13_pm25_map.png")

# 14 region comparison
reg = city.groupby("region")[["pm2_5_mean", "asthma", "copd", "smoking"]].mean().round(2)
fig, axes = plt.subplots(1, 3, figsize=(11, 4))
for ax, col, ttl in zip(axes, ["pm2_5_mean", "asthma", "copd"],
                        ["PM2.5 (ug/m3)", "Asthma (%)", "COPD (%)"]):
    reg[col].plot.bar(ax=ax, color=BLUE)
    ax.set_title(ttl)
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=30)
fig.suptitle("Regional averages across the study cities", y=1.02)
save(fig, "eda_14_regions.png")

# 15 seasonal weather relation: PM2.5 by season and region
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(data=daily, x="season", y="pm2_5", hue="region", order=["Winter", "Spring", "Summer", "Fall"],
            errorbar=None, ax=ax)
ax.set_ylabel("Mean daily PM2.5 (ug/m3)")
ax.set_xlabel("")
ax.set_title("Mean PM2.5 by season and region")
ax.legend(fontsize=8)
save(fig, "eda_15_season_region.png")

# ----------------------------------------------------------------------------- summary numbers for the write-up
summary = {
    "daily_rows": len(daily), "cities_daily": daily.city.nunique(), "cities_merged": len(city),
    "counties": len(health), "median_pm25": daily.pm2_5.median(),
    "share_days_above_who": (daily.pm2_5 > 15).mean(),
    "r_pm25_asthma_city": r_val, "r_smoking_copd_county": health["smoking"].corr(health["copd"]),
    "top5_pm25": rank.tail(5)[["city", "pm2_5_mean"]].round(1).values.tolist(),
    "bottom5_pm25": rank.head(5)[["city", "pm2_5_mean"]].round(1).values.tolist(),
    "asthma_median": health.asthma.median(), "rain_dry_median": daily.groupby("rainy").pm2_5.median().round(2).to_dict(),
}
for k, v in summary.items():
    log(f"SUMMARY {k}: {v}")
(ROOT / "data" / "clean" / "cleaning_log.txt").write_text("\n".join(LOG), encoding="utf-8")
