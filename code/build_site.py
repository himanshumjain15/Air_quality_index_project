"""Generate the static website (HTML pages + style.css) for GitHub Pages.

Run:  python code/build_site.py
Writes index.html and one page per tab into the project root.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GH = "https://github.com/himanshumjain15/Air_quality_index_project"

TABS = [  # (file, label)
    ("index.html", "Introduction"),
    ("dataprep_eda.html", "DataPrep_EDA"),
    ("clustering.html", "Clustering"),
    ("pca.html", "PCA"),
    ("naivebayes.html", "NaiveBayes"),
    ("dectrees.html", "DecTrees"),
    ("svms.html", "SVMs"),
    ("regression.html", "Regression"),
    ("nn.html", "NN"),
    ("conclusions.html", "Conclusions"),
    ("about.html", "About Me"),
]

CSS = """
:root{--bg:#f7f9fc;--card:#fff;--ink:#1f2937;--muted:#6b7280;--brand:#2a6fdb;--brand-d:#1d4fa0;--line:#e5e7eb;--accent:#f28e2b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 "Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif}
header.site{background:linear-gradient(120deg,#12325f,#2a6fdb);color:#fff;padding:28px 20px 20px}
header.site h1{margin:0 auto;max-width:1040px;font-size:1.7rem;letter-spacing:.2px}
header.site p{margin:.25rem auto 0;max-width:1040px;opacity:.9;font-size:.98rem}
nav{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
nav ul{list-style:none;margin:0 auto;padding:0 10px;max-width:1040px;display:flex;flex-wrap:wrap}
nav a{display:block;padding:12px 13px;color:var(--ink);text-decoration:none;font-size:.93rem;border-bottom:3px solid transparent}
nav a:hover{color:var(--brand)}
nav a.active{color:var(--brand);border-bottom-color:var(--brand);font-weight:600}
main{max-width:1040px;margin:26px auto 60px;padding:0 20px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px 26px;margin-bottom:22px}
h2{margin-top:0;font-size:1.4rem;color:#12325f}
h3{font-size:1.1rem;margin:1.4rem 0 .4rem;color:#1d4fa0}
p{margin:.7rem 0}
a{color:var(--brand)}
figure{margin:20px 0;text-align:center}
figure img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px;background:#fff}
figure.small img{max-width:620px}
figcaption{font-size:.92rem;color:var(--muted);max-width:820px;margin:8px auto 0;text-align:left}
figcaption b{color:var(--ink)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
table{border-collapse:collapse;width:100%;font-size:.93rem;margin:.6rem 0}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#eef3fd}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:.88em;word-break:break-all}
pre{background:#0f172a;color:#e5e7eb;padding:12px 14px;border-radius:8px;overflow:auto;font-size:.85rem}
ol.q li{margin:.35rem 0}
.note{border-left:4px solid var(--accent);background:#fff7ed;padding:10px 14px;border-radius:6px;font-size:.95rem}
.soon{border-left:4px solid var(--brand);background:#eff5ff;padding:10px 14px;border-radius:6px}
footer{text-align:center;color:var(--muted);font-size:.85rem;padding:0 0 30px}
@media(max-width:720px){.grid2{grid-template-columns:1fr}section{padding:18px}nav a{padding:10px 9px;font-size:.88rem}}
"""


def page(fname, title, body):
    active = ' class="active"'
    nav = "".join(
        f'<li><a href="{f}"{active if f == fname else ""}>{l}</a></li>' for f, l in TABS)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Air Quality, Weather and Respiratory Health</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site">
<h1>Air Quality, Weather and Respiratory Health</h1>
<p>A data science project on how weather shapes the air people breathe, and how that air relates to lung health in US cities.</p>
</header>
<nav><ul>{nav}</ul></nav>
<main>
{body}
</main>
<footer>CSCI 5612 course project &middot; <a href="{GH}">Source code and data on GitHub</a></footer>
</body>
</html>
"""
    (ROOT / fname).write_text(html, encoding="utf-8")


def fig(src, title, caption, small=False):
    cls = ' class="small"' if small else ""
    return (f'<figure{cls}><a href="images/{src}"><img src="images/{src}" alt="{title}"></a>'
            f"<figcaption><b>{title}.</b> {caption}</figcaption></figure>")


# ============================================================================ INTRODUCTION
intro = f"""
<section>
<h2>Introduction</h2>

<p>Clean air is one of the most basic requirements for human health, yet the World Health Organization estimates that the combined effects of ambient and household air pollution are linked to about 7 million premature deaths every year. Among the many pollutants in the air, fine particulate matter, known as PM2.5, is considered the most dangerous because the particles are less than 2.5 micrometers across, roughly thirty times thinner than a human hair. These particles slip past the natural defenses of the nose and throat, settle deep in the lungs, and can pass into the bloodstream, where they contribute to asthma attacks, heart disease, stroke, lung cancer, and early death. Ground-level ozone, the main ingredient of smog, is a second major concern. It forms when sunlight cooks exhaust from vehicles and industry, and it inflames the airways, making breathing painful and triggering coughing and wheezing. In 2021 the World Health Organization tightened its guidelines and now recommends that PM2.5 stay below 5 micrometers per cubic meter as a yearly average and below 15 micrometers per cubic meter on any single day. Most of the world's population, including millions of people in wealthy countries, lives in places that exceed these limits. To make invisible pollution understandable, the United States Environmental Protection Agency converts pollutant measurements into the Air Quality Index, a color-coded scale that runs from Good to Hazardous. A reading above 100 means that the air is unhealthy for sensitive groups, and a reading above 150 means that everyone may begin to feel effects. Because the index is reported daily in weather apps and news broadcasts, it has become a practical guide for deciding whether to exercise outdoors, open windows, or keep children inside. Understanding what pushes that number up or down is therefore a question that touches nearly every household.</p>

{fig("intro_aqi_scale.png", "The US Air Quality Index at a glance",
     "Each color band corresponds to a range of index values and a level of health concern. Sensitive groups begin to feel effects at 101, while everyone is affected at higher levels.")}

<p>Weather and climate act as the hidden hand behind daily air quality. Hot, sunny days speed up the chemical reactions that create ozone, which is why smog alerts cluster in summer afternoons in cities such as Los Angeles, Phoenix, and Houston. Cold, calm winter nights can form temperature inversions, in which a lid of warm air traps pollution close to the ground, a pattern familiar in mountain valleys and basins like Salt Lake City, Boise, and Fresno. Wind does the opposite job by mixing and carrying pollution away, while steady rain can wash particles out of the air, although heavy traffic and dry soil can quickly refill it. Wildfire smoke shows that pollution does not respect borders. In June 2023, smoke from hundreds of wildfires in Canada drifted south, turned the sky over New York City orange, and pushed air quality readings in the northeastern United States to levels not seen in decades, with some reports of values above 400 on the index. Millions of people who live thousands of kilometers from the flames were told to stay indoors, cancel outdoor events, and wear masks. Climate change is expected to make such episodes more frequent, because warmer and drier conditions lengthen fire seasons and worsen ozone formation. The result is that a city's air quality on any given day depends on a mix of local traffic and industry, regional geography, seasonal patterns, and events that unfold far away. Untangling these influences is central to predicting when air will be unhealthy and to warning people in time.</p>

<p>The human cost of polluted air is felt most strongly in the lungs. Asthma affects roughly 25 million people in the United States, including millions of children, and is a leading reason for missed school days and emergency room visits. Chronic obstructive pulmonary disease, known as COPD, is a progressive illness that makes breathing steadily harder, and it ranks among the leading causes of death worldwide. Tobacco smoking remains the single largest cause of COPD, so any study of lung health must recognize that pollution is only one piece of a larger puzzle that also includes smoking, obesity, poverty, access to insurance, and occupational exposure. Children, older adults, pregnant women, outdoor workers, and people with existing heart or lung disease are considered sensitive groups because the same polluted air harms them more. Exposure is also unequal. Neighborhoods located near highways, ports, power plants, and industrial zones have historically been home to lower-income families and communities of color, who breathe more pollution and often have less access to health care. These overlapping burdens mean that two people in the same metropolitan area can have very different lung health outcomes. The economic side is large as well, since sick days, medications, hospital stays, and lost productivity cost societies billions of dollars each year. Public health researchers therefore look at pollution, weather, behavior, and health together instead of in isolation.</p>

<p>Decades of policy and technology have already produced real progress. The United States Clean Air Act of 1970 set national air quality standards and forced cleaner engines, fuels, and smokestacks, and average levels of many common pollutants have fallen substantially since then even as the economy and population grew. Catalytic converters, cleaner diesel rules, and the retirement of many coal plants all played a part, and the growth of electric vehicles promises further reductions in urban exhaust. Universities and cities have begun replacing gas-powered lawn equipment such as leaf blowers with quieter, cleaner electric alternatives, and some communities restrict wood burning on high-pollution days. Public tools now help ordinary people respond. Government monitoring networks, satellite observations, and low-cost community sensors feed maps and phone apps that show local air quality almost in real time, and many schools use colored flags to decide whether recess should be held outdoors. Researchers have linked air pollution to asthma, heart disease, and even dementia, and health agencies now publish local estimates of asthma and COPD, which allows pollution and disease to be compared across places. Much remains to be done. Monitoring is sparse in rural areas and in many low-income neighborhoods, wildfire smoke is growing into a national health problem, and the effects of hot weather and pollution acting together are still not fully understood. Better warnings, smarter city planning, and personal steps such as high-efficiency filters and well-fitted masks on smoky days can all reduce harm. Continuing to connect weather, air quality, and respiratory health will help communities decide where cleaner air matters most.</p>
</section>

<section>
<h2>Ten Questions to Answer</h2>
<ol class="q">
<li>Which large US cities experience the most days with unhealthy air, and what distinguishes them from the cleanest cities?</li>
<li>How much do temperature and sunshine influence ground-level ozone from one day to the next?</li>
<li>Do rainy days actually have cleaner air than dry days, and how large is the difference?</li>
<li>How strongly do windier days reduce the concentration of fine particles?</li>
<li>How far did the June 2023 wildfire smoke change air quality in cities across the country, and how long did the effect last?</li>
<li>Do cities with higher levels of fine particles also have higher rates of asthma?</li>
<li>How closely does the share of adults who smoke track the share of adults living with COPD across US counties?</li>
<li>Do regions of the country (Northeast, Midwest, South, West) differ in both air quality and respiratory illness, and what could explain the differences?</li>
<li>Can US cities be grouped into a small number of types that share similar weather, air quality, and health profiles?</li>
<li>Which weather conditions are the best warning signs that a day will have unhealthy air, and can an air quality category be forecast from weather alone?</li>
</ol>
</section>
"""

# ============================================================================ DATAPREP_EDA
RAWLINK = "data/raw/"
CLEANLINK = "data/clean/"

FIGS = [
    ("eda_01_missing_raw.png", "Missing values in the raw API data",
     "Every column pulled from the two Open-Meteo APIs is complete, with 0% missing across 481,800 hourly air quality rows and 20,075 daily weather rows. Missing values appeared instead in the CDC health table (10 values) and as five cities with no matching county record.", True),
    ("eda_02_pm25_distribution.png", "Distribution of daily PM2.5",
     "The typical city-day has a PM2.5 of 9.3 micrograms per cubic meter, but the distribution has a long right tail that reaches 79. About 17% of all city-days exceed the WHO 24-hour guideline of 15.", True),
    ("eda_03_monthly_pm25.png", "Monthly PM2.5 variation",
     "Median PM2.5 is highest in July (12.0) and lowest in October (7.2). June has the highest average (14.3) even though its median is 11.5, which reflects the short, extreme smoke episodes of that month.", False),
    ("eda_04_city_ranking.png", "Cleanest and most polluted cities by PM2.5",
     "Los Angeles (19.2), New York (16.4) and San Diego (15.2) have the highest yearly averages, while Tucson (5.0), Anchorage (5.9) and Colorado Springs (6.4) have the lowest. The values come from an atmospheric model on a coarse grid, so coastal cities may look more polluted than monitor readings would show.", False),
    ("eda_05_aqi_categories.png", "US AQI category counts",
     "Moderate days are the most common (12,251 city-days, 61%), followed by Good (5,967, 30%) and Unhealthy for Sensitive Groups (1,493, 7%). Unhealthy (293) and Very Unhealthy (71) days are rare, and no Hazardous days occurred; the log scale is used so the small bars remain visible.", True),
    ("eda_06_correlation_heatmap.png", "Correlation between pollutants and weather",
     "PM2.5 and PM10 are almost the same signal (r = 0.95), and PM2.5 also tracks carbon monoxide (0.62). Ozone follows solar radiation (0.68), while wind speed is negatively related to PM2.5 (-0.22).", False),
    ("eda_07_temp_ozone.png", "Temperature versus ozone",
     "Each hexagon counts city-days, and the cloud slopes upward with a correlation of 0.54 between mean temperature and maximum ozone. Warm days create the conditions for ozone formation, though sunlight and precursor emissions also play a role.", True),
    ("eda_08_wildfire_episode.png", "Canadian wildfire smoke episode, 2023",
     "New York's daily PM2.5 reached 64.3 on June 7, more than four times the WHO 24-hour guideline of 15, and Boston rose the same days. Chicago peaked at about 57 in late June, while Denver and Phoenix stayed near their usual levels.", False),
    ("eda_09_rain_vs_dry.png", "PM2.5 on dry versus rainy days",
     "Dry days have a median PM2.5 of 9.37 and rainy days (at least 1 mm) 9.07, a difference of only about 3%. Rain alone at the daily scale therefore has a small effect on fine particles.", True),
    ("eda_10_asthma_distribution.png", "Asthma prevalence across US counties",
     "Across 2,956 counties the median share of adults with current asthma is 10.6%, with a range from 7.8% to 15.3%. The spread is narrow (standard deviation 0.9 points), so small differences between places may be hard to detect.", True),
    ("eda_11_pm25_vs_asthma.png", "City PM2.5 versus asthma prevalence",
     "Across 50 cities, the correlation between yearly PM2.5 and county asthma prevalence is slightly negative (r = -0.12), so no simple positive link appears at this coarse level. Detroit has the highest asthma rate (12.3%) and San Jose the lowest (7.9%), which shows that factors other than one year of PM2.5 matter.", False),
    ("eda_12_smoking_vs_copd.png", "Smoking versus COPD across counties",
     "The two rates rise together strongly (r = 0.85 across 2,956 counties), with smoking ranging from 6.4% to 39.8% of adults. This is the clearest relationship in the health data.", True),
    ("eda_13_pm25_map.png", "Mean PM2.5 by city location",
     "The highest averages sit along coastal California and the Northeast corridor, and the lowest appear in the interior Southwest and Mountain West. Each dot is one of the study cities in the contiguous United States.", False),
    ("eda_14_regions.png", "Regional averages of PM2.5, asthma and COPD",
     "The Northeast has the highest PM2.5 (13.9) but the lowest COPD (4.8%), while the Midwest has the highest asthma (10.9%) and COPD (6.7%). Pollution alone does not explain the regional pattern of lung disease.", False),
    ("eda_15_season_region.png", "PM2.5 by season and region",
     "Summer has the highest average PM2.5 (13.0) and fall the lowest (8.5), with winter at 10.0 and spring at 11.1. The bars are split by region to show that the seasonal peak is not the same everywhere.", True),
]

fig_html = "\n".join(fig(*f) for f in FIGS)

dataprep = f"""
<section>
<h2>DataPrep / EDA</h2>
<p>This tab documents how, where and why the data were gathered, how they were cleaned, and what exploratory visualization reveals. The goal is to combine <b>air quality</b> and <b>weather</b> measurements for large US cities with <b>county-level respiratory health</b> statistics, so that the questions on the Introduction tab can be examined from several angles. The data cover 55 cities across the United States for the 365 days of 2023, plus health measures for nearly 3,000 counties.</p>
<p><b>Code:</b> data gathering <a href="{GH}/blob/main/code/01_gather_data.py"><code>01_gather_data.py</code></a>, cleaning and EDA <a href="{GH}/blob/main/code/02_clean_eda.py"><code>02_clean_eda.py</code></a> (Python 3.10; packages <code>requests</code>, <code>pandas</code>, <code>numpy</code>, <code>matplotlib</code>, <code>seaborn</code>). The whole repository is at <a href="{GH}">{GH.replace("https://","")}</a>.</p>
</section>

<section>
<h2>1. Where and how the data were gathered</h2>
<table>
<tr><th>Source</th><th>Content</th><th>How obtained</th><th>Raw data</th></tr>
<tr><td><b>Open-Meteo Air Quality API</b><br><a href="https://open-meteo.com/en/docs/air-quality-api">open-meteo.com</a></td>
<td>Hourly PM10, PM2.5, carbon monoxide, nitrogen dioxide, sulphur dioxide, ozone and US AQI for each city in 2023 (481,800 rows)</td>
<td>Python <code>requests</code>, one GET call per city (no key needed)</td>
<td><a href="{RAWLINK}openmeteo_air_quality_hourly_raw.csv">openmeteo_air_quality_hourly_raw.csv</a></td></tr>
<tr><td><b>Open-Meteo Historical Weather API</b><br><a href="https://open-meteo.com/en/docs/historical-weather-api">open-meteo.com</a></td>
<td>Daily mean, maximum and minimum temperature, precipitation, maximum wind speed and solar radiation (20,075 rows)</td>
<td>Python <code>requests</code>, one GET call per city</td>
<td><a href="{RAWLINK}openmeteo_weather_daily_raw.csv">openmeteo_weather_daily_raw.csv</a></td></tr>
<tr><td><b>CDC PLACES (county data, 2023 release)</b><br><a href="https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-20/swc5-untb">data.cdc.gov</a></td>
<td>Model-based crude and age-adjusted prevalence of asthma, COPD, smoking, obesity, diabetes, uninsured adults, high blood pressure, heart disease, depression and physical inactivity for US counties (59,160 rows)</td>
<td>Socrata Open Data API, one request filtered to ten measures</td>
<td><a href="{RAWLINK}cdc_places_county_raw.csv">cdc_places_county_raw.csv</a></td></tr>
<tr><td><b>City reference table</b> (created)</td>
<td>55 cities with state, matching county name, latitude and longitude, chosen to cover all regions and a wide range of climates</td>
<td>Built by hand in the code</td>
<td><a href="{RAWLINK}cities_reference.csv">cities_reference.csv</a></td></tr>
</table>

<h3>API endpoints and example GET requests</h3>
<p><b>Air quality:</b> <code>https://air-quality-api.open-meteo.com/v1/air-quality</code></p>
<pre>GET https://air-quality-api.open-meteo.com/v1/air-quality?latitude=40.01&amp;longitude=-105.27&amp;start_date=2023-01-01&amp;end_date=2023-12-31&amp;hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi&amp;timezone=auto</pre>
<p><b>Weather:</b> <code>https://archive-api.open-meteo.com/v1/archive</code></p>
<pre>GET https://archive-api.open-meteo.com/v1/archive?latitude=40.01&amp;longitude=-105.27&amp;start_date=2023-01-01&amp;end_date=2023-12-31&amp;daily=temperature_2m_mean,precipitation_sum,wind_speed_10m_max&amp;timezone=auto</pre>
<p><b>CDC PLACES:</b> <code>https://data.cdc.gov/resource/swc5-untb.json</code></p>
<pre>GET https://data.cdc.gov/resource/swc5-untb.json?$where=measureid in ('CASTHMA','COPD')&amp;$limit=100000</pre>

<h3>Why these data</h3>
<p>Weather and air quality change every day, so hourly and daily values give thousands of observations for the questions about ozone, rain, wind and smoke. Health outcomes change slowly and are reported per county, so they add a second, unlabeled-to-labeled layer: asthma and COPD prevalence can become categories (High or Low) or numbers, which suits classification, clustering and regression later in the project. The data mix <b>quantitative</b> variables (concentrations, temperatures) with <b>qualitative</b> ones (AQI category, region, season, asthma level) and include both labeled and unlabeled variables.</p>
<div class="note"><b>Limitation.</b> Open-Meteo's air quality values are estimates from an atmospheric (CAMS) model on a coarse grid, not readings from a monitor in the city center. They capture regional patterns and large events well, but can differ from station data, especially in coastal and mountain areas. The health values are also model-based estimates for whole counties.</div>
</section>

<section>
<h2>2. Raw data and cleaned data</h2>
<p>Small previews of the first rows are shown below (the full files are linked above and in the repository).</p>
<h3>Raw</h3>
<figure><img src="images/raw_air_quality.png" alt="Raw air quality"><figcaption>Raw hourly air quality as returned by the API, one row per city and hour.</figcaption></figure>
<figure><img src="images/raw_weather.png" alt="Raw weather"><figcaption>Raw daily weather with API column names.</figcaption></figure>
<figure><img src="images/raw_cdc_places.png" alt="Raw CDC PLACES"><figcaption>Raw CDC PLACES table in long format: one row per county, measure and prevalence type.</figcaption></figure>
<h3>Cleaned</h3>
<figure><img src="images/clean_daily.png" alt="Clean daily"><figcaption>Cleaned daily table (<a href="{CLEANLINK}daily_city_air_weather_clean.csv">download</a>): hourly values aggregated to one row per city and day and joined to weather.</figcaption></figure>
<figure><img src="images/clean_health.png" alt="Clean health"><figcaption>Cleaned county health table (<a href="{CLEANLINK}county_health_clean.csv">download</a>): one row per county, one column per measure.</figcaption></figure>
<figure><img src="images/clean_city.png" alt="Clean city"><figcaption>City-level table (<a href="{CLEANLINK}city_air_weather_health_clean.csv">download</a>) that joins yearly air, weather and health features for 50 cities.</figcaption></figure>
</section>

<section>
<h2>3. Cleaning steps</h2>
<ol>
<li><b>Checks on the API data.</b> Timestamps were parsed and every column was checked for duplicates, negative concentrations and missing values. None were found in the raw API data (0 duplicates, 0 negative values, 0 missing values), so no imputation was needed. The code still contains the safeguards (clipping at zero and short-gap interpolation) so that a future download would be handled.</li>
<li><b>Hourly to daily.</b> Hourly air quality was aggregated to one row per city and day: mean PM2.5, PM10, CO, NO2 and SO2, maximum ozone and maximum AQI. Days with fewer than 18 valid hours would have been dropped; all 20,075 city-days passed.</li>
<li><b>Weather join.</b> Daily weather columns were renamed (for example <code>temperature_2m_mean</code> to <code>temp_mean</code>) and merged with air quality on city and date.</li>
<li><b>Outliers.</b> Only physically impossible values were treated as errors (PM2.5 above 1000, temperature above 60 C, and similar). None were found. Very high PM2.5 days in June 2023 are <b>real</b> smoke events and were deliberately kept.</li>
<li><b>Health data.</b> Only crude prevalence rows were kept (age-adjusted rows duplicate them), values were converted to numbers, 10 missing values were dropped, and the ten measures were pivoted into columns. Counties missing any of asthma, COPD, smoking or obesity were removed, leaving <b>2,956 counties</b>.</li>
<li><b>Unmatched cities.</b> The CDC file has no rows for Pennsylvania or Kentucky and does not list independent cities such as Baltimore City and St. Louis City. Philadelphia, Pittsburgh, Louisville, Baltimore and St. Louis therefore have air and weather data but no health match, and were left out of the merged city table (<b>50 cities</b> remain). Their daily data are still used in the daily table.</li>
<li><b>New variables.</b> AQI category (EPA bins), season, Census region, a rainy-day flag (at least 1 mm), the share of days with AQI above 100, a High/Low asthma level (median split) and a Low/Medium/High PM2.5 level (tertiles) were added by discretization.</li>
<li><b>No missing values remain</b> in the cleaned files (checked in the code). Normalization and sampling are left for each modeling tab, because each method needs different preparation.</li>
</ol>
</section>

<section>
<h2>4. Exploratory visualizations</h2>
{fig_html}
</section>
"""

# ============================================================================ MODEL TABS (placeholders)
MODELS = [
    ("clustering.html", "Clustering", "Module 2",
     "Partitional (k-means) and hierarchical clustering to group cities by air quality, weather and health profiles, guided by the Introduction question about city types.",
     "city_air_weather_health_clean.csv"),
    ("pca.html", "PCA", "Module 2",
     "Principal component analysis to reduce the correlated pollutant and weather variables to a few components that can be visualized.",
     "daily_city_air_weather_clean.csv"),
    ("naivebayes.html", "NaiveBayes", "Module 3",
     "Naive Bayes classification to predict a labeled outcome such as the AQI category or the High/Low asthma level.",
     "daily_city_air_weather_clean.csv"),
    ("dectrees.html", "DecTrees", "Module 3",
     "Decision trees to find which weather conditions best warn of unhealthy air, in a form that is easy to read.",
     "daily_city_air_weather_clean.csv"),
    ("svms.html", "SVMs", "Module 4",
     "Support vector machines with several kernels to classify air quality or asthma level, with comparisons and confusion matrices.",
     "daily_city_air_weather_clean.csv"),
    ("regression.html", "Regression", "Module 5",
     "Linear regression to estimate PM2.5 or COPD prevalence from weather and lifestyle variables.",
     "county_health_clean.csv"),
    ("nn.html", "NN", "Module 5",
     "Neural networks for predicting air quality categories or pollutant levels, compared against the earlier methods.",
     "daily_city_air_weather_clean.csv"),
]

for f, label, module, plan, data in MODELS:
    body = f"""
<section>
<h2>{label}</h2>
<div class="soon"><b>Coming in {module}.</b> This tab will be completed as the course progresses.</div>
<h3>Overview</h3>
<p>{plan}</p>
<h3>Data</h3>
<p>Planned dataset: <a href="{CLEANLINK}{data}">{data}</a> (cleaned). Raw sources are listed on the <a href="dataprep_eda.html">DataPrep_EDA</a> tab.</p>
<h3>Code</h3>
<p>To be added.</p>
<h3>Results</h3>
<p>To be added.</p>
</section>
"""
    page(f, label, body)

concl = """
<section>
<h2>Conclusions</h2>
<div class="soon"><b>Coming in the final project part.</b> This tab will hold at least five non-technical paragraphs with images that summarize what the project found about weather, air quality and lung health.</div>
</section>
"""
about = """
<section>
<h2>About Me</h2>
<p>Himanshu Jain. Student in CSCI 5612 (Data Science). More about the author will be added here.</p>
</section>
"""

(ROOT / "style.css").write_text(CSS, encoding="utf-8")
page("index.html", "Introduction", intro)
page("dataprep_eda.html", "DataPrep_EDA", dataprep)
page("conclusions.html", "Conclusions", concl)
page("about.html", "About Me", about)
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("site built")
