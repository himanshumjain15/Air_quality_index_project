# Project context: Air Quality, Weather and Respiratory Health

CSCI 5612 (Data Science) individual project, built as a static website on GitHub Pages and submitted in five parts.
Repo: https://github.com/himanshumjain15/Air_quality_index_project
Live site: https://himanshumjain15.github.io/Air_quality_index_project/

## Course rules that shape every change
- Tab names must stay exactly: Introduction, DataPrep_EDA, Clustering, PCA, NaiveBayes, DecTrees, SVMs, Regression, NN, Conclusions (plus About Me).
- All writing is third person ("the data", "the analysis"). Never use I/me/my/we. Only the About Me tab is first person.
- Introduction and Conclusions are 100% non-technical: no models, methods or datasets. Final Introduction needs 5+ paragraphs of about 10 sentences, with images. Conclusions needs 5+ paragraphs with images.
- Every model tab needs: Overview, DATA (small image of the prepared data plus links to raw and clean data), CODE (link and note language/packages; do not paste code), RESULTS.
- Figures need a title, labels, color, and two sentences of caption. Link all code and all raw data.
- Topic must not be stock-market prediction.
- Parts: 1 = topic, data, cleaning, EDA (done). 2 = clustering and PCA (done, on branch `part2-clustering-pca`, awaiting the user's push). 3 = Naive Bayes and decision trees. 4 = SVMs (multiple kernels). 5 = linear regression, neural networks, final Introduction and Conclusions.

## Topic and data
Question: how do weather and season shape daily air quality in large US cities, and how does air quality relate to asthma and COPD?
- Open-Meteo Air Quality API (hourly, 55 cities, 2023, 481,800 rows) and Open-Meteo Historical Weather API (daily). No API keys needed.
- CDC PLACES county data via the Socrata API (2,956 counties, ten measures, crude prevalence).
- `data/raw/cities_reference.csv`: hand-built list of 55 cities with county, lat, lon.
- Clean files in `data/clean/`: `daily_city_air_weather_clean.csv` (20,075 city-days), `county_health_clean.csv`, `city_air_weather_health_clean.csv` (50 cities).
- Labels available for supervised parts: `aqi_category`, `asthma_level` (High/Low median split), `pm_level` (tertiles). Regression targets: pm2_5, copd, asthma.
- Known data gaps: CDC has no PA or KY rows and no independent cities, so Philadelphia, Pittsburgh, Louisville, Baltimore and St. Louis are in the daily table but not the 50-city merged table.
- Air quality values are CAMS model estimates on a coarse grid, not monitor readings. The site states this.

## Findings so far (use real numbers in captions)
Median daily PM2.5 9.3; 17% of city-days above the WHO 15 guideline. Los Angeles, New York and San Diego are highest. New York peaked at 64.3 on 2023-06-07 (Canadian smoke). Smoking vs COPD r = 0.85 across counties. City PM2.5 vs asthma r = -0.12 (no positive link at this level). Dry vs rainy median PM2.5 is 9.37 vs 9.07.

## Repository layout and how to rebuild
- `code/01_gather_data.py` pulls raw data into `data/raw/` (about 10 minutes, needs internet).
- `code/02_clean_eda.py` cleans data and writes `data/clean/` and `images/` (16 EDA figures plus raw/clean previews).
- `code/03_intro_image.py` makes the AQI scale image.
- `code/04_clustering.py` (Part 2): k-means k=2..10 plus hierarchical (cosine distance, average linkage) on 50 cities x 20 numeric features; writes `data/clean/clustering_*.csv|json`, `city_clusters.csv` and `images/cluster_*.png`.
- `code/05_pca.py` (Part 2): PCA on 20,075 city-days x 13 numeric features with an SVD check; writes `data/clean/pca_*.csv|json` and `images/pca_*.png`.
- `code/build_site.py` generates every HTML page and `style.css` in the repo root. HTML files are generated: edit `build_site.py`, then run it. Do not hand-edit the HTML.
- Mac setup: virtual environment at `.venv` in the repo root, Python 3.14.8. Create with `python3 -m venv .venv`, then `.venv/bin/pip install -r requirements.txt`. Preview with `.venv/bin/python -m http.server 8765` from the repo root.
- `requirements.txt` pins the versions installed in `.venv`: pandas 3.0.6, numpy 2.5.4, matplotlib 3.11.2, seaborn 0.13.2, requests 2.34.2, scikit-learn 1.9.1. The Windows setup used pandas 2.3.3, numpy 2.2.6, matplotlib 3.10.8, requests 2.32.5, scikit-learn 1.7.2.
- `build_site.py` has been run successfully on the Mac setup. `code/02_clean_eda.py` has NOT been re-run under pandas 3. Do not re-run it until it has been checked for pandas 3 compatibility (it regenerates `data/clean/` and `images/`).
- Site design copies a classmate's demo (Quarto-style): serif headings, IBM Plex Sans, indigo accent, dropdown nav (Unsupervised, Supervised), dark-mode toggle.

## Working conventions
- Do NOT add a "Co-Authored-By: Claude" trailer to commits. The user had Claude removed from the GitHub contributors list (history was rewritten and force-pushed once).
- Force-pushes and history rewrites need explicit user approval.
- NEVER push to GitHub. Commit on a feature branch and let the user push and open the PR. No Claude trailer, and the git identity is himanshumjain15 <himanshumjain15@gmail.com> (set in repo-local config).
- Part 2 findings: silhouette favors k=2 for both methods (k-means 0.214, hclust-cosine 0.375) but all scores are weak; k=4 used for interpretation. Highest-PM2.5 metros (LA, NYC, Chicago...) have low COPD/smoking; heartland/Deep South cluster has the highest COPD, smoking, obesity. PCA: PC1 35.2% warm/sunny/ozone, PC2 27.1% combustion pollution, PC3 9.6% wet/windy; 3 PCs = 71.9%, 80% needs 5.
- Never fabricate results; check numbers against the data before writing captions. Say plainly when a result is null or weak.

## Open items
- Introduction facts (WHO 7 million deaths, 25 million US asthma cases, 400+ AQI in June 2023) are not yet verified against sources. Two CDC links in the Sources list returned 403 to scripts and were not checked.
- Model tabs NaiveBayes through NN and Conclusions are placeholders to fill in as each part comes due. Introduction now has 5 paragraphs and 3 images (still to be fact-checked).
- Submission each part: a .docx named with the student's name and the project part, containing only the site URL, uploaded to Canvas.
- Student: Himanshu Jain, MS Data Science, CU Boulder. Machine moved from Windows to a new Mac (setup confirmed working).
