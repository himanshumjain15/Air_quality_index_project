"""Generate the static website (HTML pages + style.css) for GitHub Pages.

Run:  python code/build_site.py
Writes index.html and one page per tab into the project root.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GH = "https://github.com/himanshumjain15/Air_quality_index_project"

NAV = [
    ("index.html", "Home"),
    ("introduction.html", "Introduction"),
    ("dataprep_eda.html", "DataPrep_EDA"),
    ("Unsupervised", [("clustering.html", "Clustering"), ("pca.html", "PCA")]),
    # Latest course instruction: SVM and NN tabs removed; Regression, AdaBoost, GradientBoosting and XGBoost added.
    ("Supervised", [("naivebayes.html", "NaiveBayes"), ("dectrees.html", "DecTrees"),
                    ("regression.html", "Regression"), ("adaboost.html", "AdaBoost"),
                    ("gradientboosting.html", "GradientBoosting"), ("xgboost.html", "XGBoost")]),
    ("conclusions.html", "Conclusions"),
    ("about.html", "About Me"),
]

CSS = """
:root{--bg:#fafaf8;--ink:#1c1c28;--muted:#6b6b78;--brand:#4b4fa3;--soft:#ececf6;--line:#e3e3e8;--card:#fff;--code:#f0f0f4;--warn:#fff6e8;--warnline:#e09a3c}
:root[data-theme=dark]{--bg:#16161d;--ink:#e8e8ee;--muted:#a0a0ae;--brand:#9da1f2;--soft:#25253a;--line:#2d2d3a;--card:#1e1e28;--code:#252533;--warn:#2b2418;--warnline:#c48a3a}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
h1,h2,h3{font-family:"Source Serif 4","Iowan Old Style",Georgia,serif;line-height:1.25}
nav.top{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line)}
nav.top .in{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;gap:6px;min-height:54px}
nav.top .brand{font-family:"Source Serif 4",Georgia,serif;font-weight:600;color:var(--ink);text-decoration:none;margin-right:14px;font-size:1.02rem;white-space:nowrap}
nav.top ul{list-style:none;margin:0;padding:0;display:flex;gap:2px;flex-wrap:wrap;flex:1}
nav.top li{position:relative}
nav.top li>a,nav.top li>button{display:block;background:none;border:0;font:inherit;font-size:.9rem;color:var(--muted);padding:7px 10px;border-radius:6px;text-decoration:none;cursor:pointer}
nav.top li>a:hover,nav.top li>button:hover{color:var(--ink)}
nav.top li>a.active,nav.top li>button.active{background:var(--soft);color:var(--brand);font-weight:600}
nav.top .dd{display:none;position:absolute;top:100%;left:0;min-width:170px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
nav.top li:hover .dd,nav.top li:focus-within .dd,nav.top li.open .dd{display:block}
nav.top .dd a{display:block;padding:7px 10px;border-radius:6px;color:var(--ink);text-decoration:none;font-size:.9rem}
nav.top .dd a:hover{background:var(--soft)}
nav.top .dd a.active{color:var(--brand);font-weight:600}
.tools{display:flex;gap:4px;margin-left:auto}
.tools a,.tools button{background:none;border:0;color:var(--muted);cursor:pointer;padding:7px;border-radius:6px;display:flex}
.tools a:hover,.tools button:hover{color:var(--ink);background:var(--soft)}
main{max-width:860px;margin:0 auto;padding:42px 22px 80px}
h1{font-size:2.15rem;margin:0 0 .35rem}
.sub{color:var(--muted);font-size:1.08rem;margin:0 0 1.6rem}
h2{font-size:1.5rem;margin:2.6rem 0 .6rem;padding-top:.3rem}
h3{font-size:1.15rem;margin:1.7rem 0 .3rem}
p{margin:.85rem 0}
a{color:var(--brand)}
.lead{font-size:1.1rem}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:1.8rem 0}
.stats b{display:block;font:600 1.9rem "IBM Plex Sans",sans-serif;color:var(--brand);line-height:1.2}
.stats span{font-size:.85rem;color:var(--muted)}
ul.cover li,ol li{margin:.3rem 0}
figure{margin:24px 0;text-align:center}
figure img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px;background:#fff}
figure.small img{max-width:min(640px,100%)}
figcaption{font-size:.92rem;color:var(--muted);margin:9px auto 0;text-align:left}
figcaption b{color:var(--ink)}
table{border-collapse:collapse;width:100%;font-size:.92rem;margin:.8rem 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--soft)}
code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:.87em;word-break:break-word}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow:auto;font-size:.84rem;line-height:1.5}
pre code{background:none;padding:0;word-break:normal}
.note{border-left:4px solid var(--warnline);background:var(--warn);padding:10px 16px;border-radius:6px;font-size:.95rem;margin:1.2rem 0}
.soon{border-left:4px solid var(--brand);background:var(--soft);padding:10px 16px;border-radius:6px;margin:1rem 0}
.start{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:1rem}
.start a{display:block;border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--ink);background:var(--card)}
.start a:hover{border-color:var(--brand)}
.start a b{display:block;color:var(--brand)}
.start a span{font-size:.88rem;color:var(--muted)}
.figrow{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}
.figrow figure{margin:12px 0}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:.8rem}
.card{border:1px solid var(--line);border-radius:12px;padding:16px 18px;background:var(--card)}
.card b{display:block;font-family:"Source Serif 4",Georgia,serif;font-size:1.05rem}
.card span{display:block;color:var(--muted);font-size:.95rem}
.card small{display:block;color:var(--muted);margin-top:.7rem;font-size:.85rem}
.card .tags{margin:.7rem 0 0;display:flex;flex-wrap:wrap;gap:6px}
.card .tags em{font-style:normal;font-size:.78rem;background:var(--soft);color:var(--brand);border-radius:999px;padding:2px 10px}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:.85rem;text-align:center;padding:22px}
@media(max-width:760px){.figrow{grid-template-columns:minmax(0,1fr)}.stats,.start{grid-template-columns:1fr 1fr}.cards{grid-template-columns:1fr}nav.top .in{flex-wrap:wrap;padding:6px 14px}nav.top .dd{position:static;box-shadow:none}h1{font-size:1.7rem}main{padding-top:28px}}
"""

THEME_JS = "(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"
TOGGLE_JS = """
document.getElementById('theme').addEventListener('click',function(){
var d=document.documentElement,n=d.getAttribute('data-theme')==='dark'?'light':'dark';
d.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){}});
document.querySelectorAll('nav.top li.has-dd>button').forEach(function(b){
b.addEventListener('click',function(){b.parentElement.classList.toggle('open')})});
"""

GH_ICON = ('<svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
           '2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13'
           '-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-'
           '3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 '
           '.27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73'
           '.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')
MOON_ICON = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>')


def page(fname, title, body):
    items = []
    for entry in NAV:
        if isinstance(entry[1], list):
            group, links = entry
            act = any(f == fname for f, _ in links)
            sub = "".join(f'<a href="{f}"{" class=active" if f == fname else ""}>{l}</a>' for f, l in links)
            cls = "active" if act else ""
            items.append(f'<li class="has-dd"><button class="{cls}" aria-haspopup="true">'
                         f'{group} &#9662;</button><div class="dd">{sub}</div></li>')
        else:
            f, l = entry
            items.append(f'<li><a href="{f}"{" class=active" if f == fname else ""}>{l}</a></li>')
    nav_items = "".join(items)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Air Quality, Weather and Respiratory Health</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:wght@500;600&display=swap" rel="stylesheet">
<script>{THEME_JS}</script>
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav class="top"><div class="in">
<a class="brand" href="index.html">Air Quality &amp; Lung Health</a>
<ul>{nav_items}</ul>
<div class="tools"><a href="{GH}" aria-label="GitHub repository">{GH_ICON}</a>
<button id="theme" aria-label="Toggle dark mode">{MOON_ICON}</button></div>
</div></nav>
<main>
{body}
</main>
<footer>CSCI 5612 course project &middot; <a href="{GH}">Source code and data on GitHub</a></footer>
<script>{TOGGLE_JS}</script>
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
<h1>Introduction</h1>
<p class="sub">Why air quality, weather and lung health belong together</p>
<section>

<p>Clean air is one of the most basic requirements for human health, yet the World Health Organization estimates that the combined effects of ambient and household air pollution are linked to about 6.7 million premature deaths every year. Among the many pollutants in the air, fine particulate matter, known as PM2.5, is considered the most dangerous because the particles are less than 2.5 micrometers across, roughly thirty times thinner than a human hair. These particles slip past the natural defenses of the nose and throat, settle deep in the lungs, and can pass into the bloodstream, where they contribute to asthma attacks, heart disease, stroke, lung cancer, and early death. Ground-level ozone, the main ingredient of smog, is a second major concern. It forms when sunlight cooks exhaust from vehicles and industry, and it inflames the airways, making breathing painful and triggering coughing and wheezing. In 2021 the World Health Organization tightened its guidelines and now recommends that PM2.5 stay below 5 micrometers per cubic meter as a yearly average and below 15 micrometers per cubic meter on any single day. Most of the world's population, including millions of people in wealthy countries, lives in places that exceed these limits. To make invisible pollution understandable, the United States Environmental Protection Agency converts pollutant measurements into the Air Quality Index, a color-coded scale that runs from Good to Hazardous. A reading above 100 means that the air is unhealthy for sensitive groups, and a reading above 150 means that everyone may begin to feel effects. Because the index is reported daily in weather apps and news broadcasts, it has become a practical guide for deciding whether to exercise outdoors, open windows, or keep children inside. Understanding what pushes that number up or down is therefore a question that touches nearly every household.</p>

{fig("intro_aqi_scale.png", "The US Air Quality Index at a glance",
     "Each color band corresponds to a range of index values and a level of health concern. Sensitive groups begin to feel effects at 101, while everyone is affected at higher levels.")}

<p>Weather and climate act as the hidden hand behind daily air quality. Hot, sunny days speed up the chemical reactions that create ozone, which is why smog alerts cluster in summer afternoons in cities such as Los Angeles, Phoenix, and Houston. Cold, calm winter nights can form temperature inversions, in which a lid of warm air traps pollution close to the ground, a pattern familiar in mountain valleys and basins like Salt Lake City, Boise, and Fresno. Wind does the opposite job by mixing and carrying pollution away, while steady rain can wash particles out of the air, although heavy traffic and dry soil can quickly refill it. Wildfire smoke shows that pollution does not respect borders. In June 2023, smoke from hundreds of wildfires in Canada drifted south, turned the sky over New York City orange, and pushed air quality readings in the northeastern United States to levels not seen in decades, with New York City readings reported above 350 on the index at their worst. Millions of people who live thousands of kilometers from the flames were told to stay indoors, cancel outdoor events, and wear masks. Climate change is expected to make such episodes more frequent, because warmer and drier conditions lengthen fire seasons and worsen ozone formation. The result is that a city's air quality on any given day depends on a mix of local traffic and industry, regional geography, seasonal patterns, and events that unfold far away. Untangling these influences is central to predicting when air will be unhealthy and to warning people in time.</p>

{fig("eda_08_wildfire_episode.png", "When distant smoke reached big cities",
     "In early June 2023, New York and Boston saw air pollution jump to several times the safe daily limit because of smoke from Canadian fires. Chicago followed in late June, while Denver and Phoenix stayed close to their usual levels.")}

<p>The human cost of polluted air is felt most strongly in the lungs. Asthma affects roughly 25 million people in the United States, including millions of children, and is a leading reason for missed school days and emergency room visits. Chronic obstructive pulmonary disease, known as COPD, is a progressive illness that makes breathing steadily harder, and it ranks among the leading causes of death worldwide. Tobacco smoking remains the single largest cause of COPD, so any study of lung health must recognize that pollution is only one piece of a larger puzzle that also includes smoking, obesity, poverty, access to insurance, and occupational exposure. Children, older adults, pregnant women, outdoor workers, and people with existing heart or lung disease are considered sensitive groups because the same polluted air harms them more. Exposure is also unequal. Neighborhoods located near highways, ports, power plants, and industrial zones have historically been home to lower-income families and communities of color, who breathe more pollution and often have less access to health care. These overlapping burdens mean that two people in the same metropolitan area can have very different lung health outcomes. The economic side is large as well, since sick days, medications, hospital stays, and lost productivity cost societies billions of dollars each year. Public health researchers therefore look at pollution, weather, behavior, and health together instead of in isolation.</p>

<p>Decades of policy and technology have already produced real progress. The United States Clean Air Act of 1970 set national air quality standards and forced cleaner engines, fuels, and smokestacks, and average levels of many common pollutants have fallen substantially since then even as the economy and population grew. Catalytic converters, cleaner diesel rules, and the retirement of many coal plants all played a part, and the growth of electric vehicles promises further reductions in urban exhaust. Universities and cities have begun replacing gas-powered lawn equipment such as leaf blowers with quieter, cleaner electric alternatives, and some communities restrict wood burning on high-pollution days. Public tools now help ordinary people respond. Government monitoring networks, satellite observations, and low-cost community sensors feed maps and phone apps that show local air quality almost in real time, and many schools use colored flags to decide whether recess should be held outdoors. Researchers have linked air pollution to asthma, heart disease, and even dementia, and health agencies now publish local estimates of asthma and COPD, which allows pollution and disease to be compared across places. Much remains to be done. Monitoring is sparse in rural areas and in many low-income neighborhoods, wildfire smoke is growing into a national health problem, and the effects of hot weather and pollution acting together are still not fully understood. Better warnings, smarter city planning, and personal steps such as high-efficiency filters and well-fitted masks on smoky days can all reduce harm. Continuing to connect weather, air quality, and respiratory health will help communities decide where cleaner air matters most.</p>

<p>Cities are not all alike, and that is part of what makes the air they breathe so hard to summarize with a single number. A coastal city with mild temperatures, a desert city with scorching summers, an older industrial city with cold winters, and a mountain town ringed by forest each face a different mix of pollution sources and weather. Residents of these places also differ in age, income, health insurance, and habits such as smoking, all of which shape lung health apart from the air itself. Public health planners cannot study every city one at a time, so they look for patterns that let similar places be treated in similar ways. A natural question is whether American cities fall into a small number of recognizable types, such as hot and sunny cities with smoggy summers, cool and clean western cities, or large metropolitan areas with heavy traffic and haze. If such types exist, a lesson learned in one city could help others of the same type, and warnings or programs could be designed for whole groups of cities instead of one by one. It would also show which cities are unusual and deserve special attention. A second question is which everyday conditions really matter. Temperature, sunshine, rain, wind, and many different pollutants are recorded every day, and they tend to rise and fall together, which makes it hard to tell what is driving what. Boiling a long list of related conditions down to a few simple ideas, such as how hot and sunny a day is or how much traffic and heating smoke is in the air, would make the story far easier to tell. Whether cities fall into recognizable types, and which few conditions matter most, are central to understanding and explaining the air that people breathe.</p>

{fig("eda_13_pm25_map.png", "Air quality differs from place to place",
     "Cities on the California coast and along the Northeast corridor tend to have the dirtiest air, while the interior Southwest and the Mountain West tend to have the cleanest. Each dot is one large city, so the map hints that places may sort into recognizable types.")}

<p>Warning people before the air turns unhealthy is only possible if the conditions that lead to bad air days are understood. Air quality forecasts are issued daily by government agencies, and in many places they trigger action days on which residents are urged to limit driving, avoid burning wood, and postpone strenuous outdoor activity. Families who manage asthma often rely on such forecasts to decide whether children should play outside or carry rescue inhalers, and many schools plan recess around the daily color or flag. A useful warning must arrive early and must be right often enough that people keep trusting it. Too many false alarms lead to warning fatigue, while missed events leave the most vulnerable people exposed. Weather is the natural starting point for anticipating the air, because temperature, sunshine, wind, and season are known ahead of time far better than traffic or industrial activity, and because they decide whether pollution builds up or blows away. Yet weather is clearly not the whole story. Two cities with identical weather can have very different air because of their geography, their traffic, their industries, and the smoke that arrives from fires far away. The seasons add another layer, since summer brings the sunshine and heat that favor smog, while autumn tends to bring the cleanest air of the year. Unusual events such as wildfire smoke can overwhelm every ordinary pattern for days at a time. Understanding how far everyday conditions can anticipate the state of the air, and where they fall short, helps public health officials decide when simple rules of thumb are enough and when more monitoring is worth the cost. It also tells the public how much confidence to place in a warning that rests on the weather outlook alone.</p>

{fig("eda_15_season_region.png", "Air quality follows the seasons",
     "Average fine-particle levels are lowest in fall in all four regions and highest in summer in three of them, while the West peaks in winter instead. The pattern differs by region, which is one reason a single rule for every city rarely works.")}

<p>Air quality is a spectrum and not a switch, and the way it is described to the public shapes how people respond. Fine particle levels rise and fall continuously, and health risks rise with them gradually instead of jumping at a single line. Yet warnings must be simple, so agencies draw lines on the scale, such as an index value of 101, above which sensitive groups are advised to take care. Every line creates two kinds of mistakes. A line set too high misses days when vulnerable people should have been warned, and a line set too low produces so many alerts that people stop paying attention. Public health officials therefore weigh the cost of a missed warning against the cost of a false alarm, and the balance differs for a school nurse, a marathon organizer, and a hospital planning for extra asthma admissions. Another challenge is that conditions that go together are easy to confuse. Hot days tend to be sunny, sunny days tend to be calm, and calm days let pollution build up, so it takes care to say which of these truly matters and by how much. A statement such as every extra bit of breeze lowers the level a little is easier to act on than the vague claim that wind helps. Knowing both how much the air changes with conditions and how reliably a day can be sorted into safe or unsafe lets communities set realistic expectations for forecasts. These ideas also explain why the same forecast can be judged a success by a city planner and a failure by the parent of a child with asthma.</p>

{fig("eda_02_pm25_distribution.png", "Most days are clean, but a long tail is not",
     "Daily fine-particle levels vary continuously: most city-days fall below the World Health Organization guideline of 15 micrograms per cubic meter, but about 17% exceed it, and a few days reach several times that level. Any single line drawn through this spread will separate some days wrongly.")}
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

<section>
<h2>Sources</h2>
<ul>
<li>World Health Organization, <a href="https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health">Ambient (outdoor) air quality and health</a></li>
<li>World Health Organization, <a href="https://www.who.int/news-room/fact-sheets/detail/chronic-obstructive-pulmonary-disease-(copd)">Chronic obstructive pulmonary disease (COPD)</a></li>
<li>US EPA and AirNow, <a href="https://www.airnow.gov/aqi/aqi-basics/">Air Quality Index basics</a></li>
<li>US EPA, <a href="https://www.epa.gov/pm-pollution/particulate-matter-pm-basics">Particulate matter (PM) basics</a></li>
<li>US EPA, <a href="https://www.epa.gov/clean-air-act-overview">Clean Air Act overview</a></li>
<li>US Centers for Disease Control and Prevention, <a href="https://www.cdc.gov/asthma/">Asthma</a> and <a href="https://www.cdc.gov/places/">PLACES local health data</a></li>
</ul>
</section>
"""

# ============================================================================ DATAPREP_EDA
RAWLINK = "data/raw/"
CLEANLINK = "data/clean/"

FIGS = [
    ("eda_01_missing_raw.png", "Where data were missing before cleaning",
     "The two Open-Meteo APIs returned complete data (0% missing across 481,800 hourly rows and 20,075 daily weather rows), and only 10 CDC prevalence values (0.03%) were missing. The largest gap is structural: 5 of 55 cities (9.1%) have no matching county in the CDC file.", True),
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
    ("eda_16_outlier_check.png", "Outlier check on daily PM2.5",
     "Applying the interquartile-range rule within each city flags 765 of 20,075 city-days (3.8%), shown as red dots for the ten cities with the most extreme days. The most extreme value (Pittsburgh, 78.7 on June 29) falls in the documented June 2023 smoke period, so flagged days were kept as plausible values and not treated as errors.", False),
]

fig_html = "\n".join(fig(*f) for f in FIGS)

dataprep = f"""
<h1>DataPrep_EDA</h1>
<p class="sub">How the data were gathered, cleaned and explored</p>
<p>This tab documents how, where and why the data were gathered, how they were cleaned, and what exploratory visualization reveals. The goal is to combine <b>air quality</b> and <b>weather</b> measurements for large US cities with <b>county-level respiratory health</b> statistics, so that the questions on the Introduction tab can be examined from several angles. The data cover 55 cities across the United States for the 365 days of 2023, plus health measures for nearly 3,000 counties.</p>

<section>
<h2>Data Sources</h2>
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

<h3>Why these data</h3>
<p>Weather and air quality change every day, so hourly and daily values give thousands of observations for the questions about ozone, rain, wind and smoke. Health outcomes change slowly and are reported per county, so they add a second layer: asthma and COPD prevalence can become categories (High or Low) or numbers, which suits classification, clustering and regression later in the project. The data mix <b>quantitative</b> variables (concentrations, temperatures) with <b>qualitative</b> ones (AQI category, region, season, asthma level) and include both labeled and unlabeled variables.</p>
<div class="note"><b>Limitation.</b> Open-Meteo's air quality values are estimates from an atmospheric (CAMS) model on a coarse grid, not readings from a monitor in the city center. They capture regional patterns and large events well, but can differ from station data, especially in coastal and mountain areas. The health values are also model-based estimates for whole counties.</div>
</section>

<section>
<h2>APIs Used</h2>
<p>Two of the sources are true APIs queried from Python; the CDC data are pulled from an open data API as well. Each call below is an example of a core endpoint with a GET request.</p>
<p><b>Air quality:</b> <code>https://air-quality-api.open-meteo.com/v1/air-quality</code></p>
<pre>GET https://air-quality-api.open-meteo.com/v1/air-quality?latitude=40.01&amp;longitude=-105.27&amp;start_date=2023-01-01&amp;end_date=2023-12-31&amp;hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi&amp;timezone=auto</pre>
<p><b>Weather:</b> <code>https://archive-api.open-meteo.com/v1/archive</code></p>
<pre>GET https://archive-api.open-meteo.com/v1/archive?latitude=40.01&amp;longitude=-105.27&amp;start_date=2023-01-01&amp;end_date=2023-12-31&amp;daily=temperature_2m_mean,precipitation_sum,wind_speed_10m_max&amp;timezone=auto</pre>
<p><b>CDC PLACES:</b> <code>https://data.cdc.gov/resource/swc5-untb.json</code></p>
<pre>GET https://data.cdc.gov/resource/swc5-untb.json?$where=measureid in ('CASTHMA','COPD')&amp;$limit=100000</pre>

</section>

<section>
<h2>Raw Data Access</h2>
<ul>
<li><a href="{RAWLINK}openmeteo_air_quality_hourly_raw.csv">Open-Meteo hourly air quality (raw CSV)</a></li>
<li><a href="{RAWLINK}openmeteo_weather_daily_raw.csv">Open-Meteo daily weather (raw CSV)</a></li>
<li><a href="{RAWLINK}cdc_places_county_raw.csv">CDC PLACES county health (raw CSV)</a></li>
<li><a href="{RAWLINK}cities_reference.csv">City reference table (CSV)</a></li>
<li>Cleaned files: <a href="{CLEANLINK}daily_city_air_weather_clean.csv">daily</a>, <a href="{CLEANLINK}county_health_clean.csv">county health</a>, <a href="{CLEANLINK}city_air_weather_health_clean.csv">city level</a>, and the <a href="{CLEANLINK}cleaning_log.txt">cleaning log</a></li>
</ul>
</section>

<section>
<h2>Code</h2>
<p>All code is written in Python 3.10 with the packages <code>requests</code>, <code>pandas</code>, <code>numpy</code>, <code>matplotlib</code> and <code>seaborn</code>.</p>
<ul>
<li><a href="{GH}/blob/main/code/01_gather_data.py"><code>01_gather_data.py</code></a> gathers the raw data from the APIs.</li>
<li><a href="{GH}/blob/main/code/02_clean_eda.py"><code>02_clean_eda.py</code></a> cleans the data and creates the figures.</li>
<li><a href="{GH}/blob/main/code/03_intro_image.py"><code>03_intro_image.py</code></a> creates the Introduction image.</li>
<li><a href="{GH}/blob/main/code/build_site.py"><code>build_site.py</code></a> generates the website pages.</li>
</ul>
<p>The whole repository is at <a href="{GH}">{GH.replace("https://","")}</a>.</p>
</section>

<section>
<h2>Raw and Cleaned Data</h2>
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
<h2>Cleaning Pipeline</h2>
<ol>
<li><b>Checks on the API data.</b> Timestamps were parsed and every column was checked for duplicates, negative concentrations and missing values. None were found in the raw API data (0 duplicates, 0 negative values, 0 missing values), so no imputation was needed. The code still contains the safeguards (clipping at zero and short-gap interpolation) so that a future download would be handled.</li>
<li><b>Hourly to daily.</b> Hourly air quality was aggregated to one row per city and day: mean PM2.5, PM10, CO, NO2 and SO2, maximum ozone and maximum AQI. Days with fewer than 18 valid hours would have been dropped; all 20,075 city-days passed.</li>
<li><b>Weather join.</b> Daily weather columns were renamed (for example <code>temperature_2m_mean</code> to <code>temp_mean</code>) and merged with air quality on city and date.</li>
<li><b>Outliers.</b> Two checks were used. First, physically impossible values (PM2.5 above 1000, temperature above 60 C, and similar) would be removed as errors, and none were found. Second, the interquartile-range rule within each city flagged 765 of 20,075 city-days (3.8%) (see the outlier figure below). The most extreme values fall in the June 2023 wildfire smoke period, so the flagged days were kept as plausible values, because removing them would hide exactly the episodes the project studies.</li>
<li><b>Health data.</b> Only crude prevalence rows were kept (age-adjusted rows duplicate them), values were converted to numbers, 10 missing values were dropped, and the ten measures were pivoted into columns. Counties missing any of asthma, COPD, smoking or obesity were removed, leaving <b>2,956 counties</b>.</li>
<li><b>Unmatched cities.</b> The CDC file has no rows for Pennsylvania or Kentucky and does not list independent cities such as Baltimore City and St. Louis City. Philadelphia, Pittsburgh, Louisville, Baltimore and St. Louis therefore have air and weather data but no health match, and were left out of the merged city table (<b>50 cities</b> remain). Their daily data are still used in the daily table.</li>
<li><b>New variables.</b> AQI category (EPA bins), season, Census region, a rainy-day flag (at least 1 mm), the share of days with AQI above 100, a High/Low asthma level (median split) and a Low/Medium/High PM2.5 level (tertiles) were added by discretization.</li>
<li><b>No missing values remain</b> in the cleaned files (checked in the code). Normalization and sampling are left for each modeling tab, because each method needs different preparation.</li>
</ol>
</section>

<section>
<h2>Exploratory Data Visualizations</h2>
{fig_html}
</section>
"""

# ============================================================================ CLUSTERING AND PCA TABS (Module 2)
import json

CR = json.loads((ROOT / "data" / "clean" / "clustering_results.json").read_text(encoding="utf-8"))
CLUSTER_NAMES = {
    "0": "Warm, low-pollution cities with many uninsured adults",
    "1": "Cool, clean and healthier cities, mostly in the West",
    "2": "Heartland and Deep South cities with heavy lung-disease burden",
    "3": "Large metropolitan areas with the dirtiest air",
}
rows = []
for c in ["0", "1", "2", "3"]:
    m = CR["main_cluster_members"][c]
    pr = CR["main_cluster_profile_raw_means"][c]
    ast = CR["main_cluster_asthma_level_counts"][c]
    rows.append(
        f"<tr><td><b>{c}</b><br>{CLUSTER_NAMES[c]}</td><td>{len(m)}</td><td>{', '.join(m)}</td>"
        f"<td>{pr['pm2_5_mean']:.1f}</td><td>{pr['temp_mean']:.1f}</td><td>{pr['smoking']:.1f}</td>"
        f"<td>{pr['copd']:.1f}</td><td>{pr['obesity']:.1f}</td><td>{ast['High']} of {ast['High'] + ast['Low']}</td></tr>")
cluster_table = ("<table><tr><th>Cluster (k = 4)</th><th>Cities</th><th>Members</th><th>PM2.5</th><th>Temp (C)</th>"
                 "<th>Smoking %</th><th>COPD %</th><th>Obesity %</th><th>High-asthma cities</th></tr>" + "".join(rows) + "</table>")

CODE04 = f"{GH}/blob/main/code/04_clustering.py"
CODE05 = f"{GH}/blob/main/code/05_pca.py"

clustering = f"""
<h1>Clustering</h1>
<p class="sub">Do large US cities fall into natural types?</p>
<p>Clustering searches for groups in data without being told what the groups are. Here, the 50 cities that have both air and health records are grouped by their air quality, weather and respiratory health profiles, with two different clustering families applied to the same data. The write-up is organized into Overview, Data Prep, Code, Results and Conclusions.</p>

<section>
<h2>Overview</h2>
<p><b>Clustering</b> is an unsupervised method: it receives only numbers describing each observation and looks for groups in which members are more similar to each other than to members of other groups. No labels guide it, so the groups it finds are a form of discovery, and their meaning has to be checked afterwards.</p>
<p><b>Partitional clustering</b>, of which <b>k-means</b> is the best-known example, decides the number of groups <i>k</i> in advance. The algorithm places <i>k</i> centroids, assigns every observation to the nearest one, moves each centroid to the average of its members, and repeats until nothing changes. The result is a single flat set of groups that minimizes the total squared distance between observations and their centroids. Because the starting centroids are random, the algorithm is restarted many times and the best run is kept.</p>
<p><b>Hierarchical clustering</b> builds a family of nested groupings instead of one. The agglomerative version used here starts with every city as its own group and repeatedly merges the two closest groups, and the full merging history is drawn as a tree called a <b>dendrogram</b>. Cutting the tree at a chosen height gives any number of groups, so <i>k</i> can be decided after seeing the tree. The distance between two groups depends on the <b>linkage</b> rule, and here the <b>average</b> linkage rule is used, which takes the mean distance between all pairs of members.</p>
{fig("cluster_00a_partitional_vs_hierarchical.png", "Partitional versus hierarchical clustering",
     "K-means (left) fixes the number of groups and moves centroids (black crosses) until each point sits with its nearest one, while hierarchical clustering (right) records every merge in a tree. The data in this figure are synthetic and serve only to illustrate the two ideas.")}
<h3>Distance metrics</h3>
<p>Every clustering method depends on a definition of distance. <b>Euclidean distance</b>, the straight-line distance between two points, is used for k-means because the method minimizes squared Euclidean distance. <b>Cosine distance</b> (one minus the cosine similarity) is used for the hierarchical clustering, as the assignment requires. It measures the angle between two vectors instead of the gap between them, so it compares the <i>shape</i> of two cities' profiles: which variables are unusually high or low relative to the average, regardless of how extreme the overall values are. The <b>silhouette</b> score, which compares how close each city is to its own cluster against the nearest other cluster, is used to judge the number of groups (values near 1 mean well-separated groups, values near 0 mean overlapping groups, and negative values suggest a misplaced city).</p>
{fig("cluster_00b_distance_metrics.png", "Euclidean distance versus cosine distance",
     "Points A and B lie on the same line from the origin, so cosine distance sees them as identical in direction even though Euclidean distance places them far apart. Cosine distance therefore ignores the overall size of a profile and compares only its pattern.")}
<h3>How clustering is used here</h3>
<p>The Introduction asked whether US cities can be grouped into a small number of types. Clustering answers this by looking at all variables together: yearly pollution levels, weather, and the county health rates for asthma, COPD, smoking and other conditions. The labels that are known (region, and the High/Low asthma level) are deliberately kept out of the clustering and used only afterwards, to check whether the discovered groups agree with geography or with disease burden. Agreement would show that the groups capture something real, and disagreement would show where cities behave differently from their neighbors.</p>
</section>

<section>
<h2>Data Prep</h2>
<p>Clustering needs <b>unlabeled numeric data</b> only. Every column must be a number, because distances are computed between rows, and no label such as the city name, region or asthma category may be included, because a label would either break the distance calculation or leak the answer into the groups. Variables on large scales would also dominate the distances: carbon monoxide is measured in the hundreds while the unhealthy-day share is between 0 and 1. Every column was therefore standardized to a mean of 0 and a standard deviation of 1 (a z-score).</p>
<p>The sample comes from the city-level table, which has one row per city (50 cities, no missing values). Twenty numeric columns were kept: <b>air quality</b> (mean and 95th percentile of PM2.5, nitrogen dioxide, sulphur dioxide, carbon monoxide, mean daily maximum ozone, share of days with AQI above 100), <b>weather</b> (mean temperature, total precipitation, mean wind speed) and <b>health</b> (county prevalence of uninsured adults, high blood pressure, asthma, heart disease, COPD, smoking, depression, diabetes, physical inactivity, obesity). PM10 and mean AQI were left out because they nearly duplicate PM2.5 and the unhealthy-day share and would count the same signal twice. The city name, state, county, region, latitude, longitude, population, number of days, and the High/Low asthma and PM2.5 levels were removed before clustering and kept aside to interpret the results.</p>
{fig("cluster_01a_data_before.png", "Before transforming: the cleaned city table",
     "The table mixes label columns (orange: city, state, region and asthma level) with numbers in very different units, such as carbon monoxide in the hundreds and COPD in single digits. Only the numeric columns (blue headers) can be used for clustering.")}
<h3>The transformation, step by step</h3>
<ol>
<li><b>Remove the labels.</b> City, state, county, region, the High/Low asthma level and the PM2.5 level, latitude, longitude, population and number of days were taken out of the matrix and stored separately. They are used only afterwards, to interpret the clusters.</li>
<li><b>Drop duplicated signals.</b> PM10 and mean AQI were removed because they nearly repeat PM2.5 and the unhealthy-day share.</li>
<li><b>Standardize every column.</b> Each value had its column average subtracted and was divided by the column standard deviation. For example, Albuquerque's mean PM2.5 of 7.37 (average of all 50 cities 10.54, standard deviation 2.53) becomes -1.26, and its carbon monoxide of 186.3 (average 223.7, standard deviation 46.6) becomes -0.80, so both now sit on the same scale.</li>
</ol>
{fig("cluster_01_data_sample.png", "After transforming: the data given to the clustering algorithms",
     "Each row is one city and each column is one standardized variable, with no names or labels attached; the first seven rows and ten of twenty columns are shown. Pink cells are below the average of all cities and blue cells are above it.")}
<ul>
<li><a href="{CLEANLINK}clustering_input_numeric.csv">clustering_input_numeric.csv</a>: the 50 x 20 numeric matrix in original units (row order follows the city table)</li>
<li><a href="{CLEANLINK}clustering_input_scaled.csv">clustering_input_scaled.csv</a>: the same matrix after standardization, which is what the algorithms receive</li>
<li><a href="{CLEANLINK}city_air_weather_health_clean.csv">city_air_weather_health_clean.csv</a>: the cleaned city table the sample was taken from</li>
</ul>
</section>

<section>
<h2>Code</h2>
<p>The analysis is written in <b>Python 3.14</b> with <code>pandas</code>, <code>numpy</code>, <code>scikit-learn</code> (<code>KMeans</code>, <code>silhouette_score</code>), <code>scipy</code> (<code>linkage</code>, <code>dendrogram</code>, <code>pdist</code>), <code>matplotlib</code> and <code>seaborn</code>. K-means used 50 random restarts and a fixed seed so that results can be reproduced. The hierarchical clustering used cosine distance with average linkage, because Ward linkage is defined only for Euclidean distance.</p>
<ul>
<li><a href="{CODE04}"><code>04_clustering.py</code></a> on GitHub: builds the sample, runs k-means for k = 2 to 10, runs hierarchical clustering, computes silhouette scores and draws every figure on this tab</li>
<li><a href="{CLEANLINK}city_clusters.csv">city_clusters.csv</a> and <a href="{CLEANLINK}clustering_results.json">clustering_results.json</a>: the cluster assignment of every city and the numbers quoted below</li>
</ul>
</section>

<section>
<h2>Results</h2>
<h3>K-means and the choice of k</h3>
<p>K-means was run for every k from 2 to 10. The sum of squared distances within clusters falls from 758 at k = 2 to 546 at k = 4 and 335 at k = 10, a steady decline without a sharp elbow, which suggests that the cities do not form tightly separated groups. Three values of k (3, 4 and 5) are compared in detail below, with k = 2 as the reference point.</p>
{fig("cluster_02_elbow.png", "Elbow plot for k-means",
     "Within-cluster variation falls from 758 at k = 2 to 546 at k = 4 and keeps shrinking at about the same pace for larger k. No single bend stands out, so the elbow rule gives no clear answer.", small=True)}
<p>The <b>silhouette method</b> points to <b>k = 2</b> as the best value for k-means, with an average silhouette of 0.214, followed by k = 3 (0.196), k = 4 (0.190) and k = 5 (0.183). All of these values are low: scores below roughly 0.25 are usually read as weak structure, so the cities form overlapping groups along a continuum and not distinct clusters. The two-group solution splits the cities into 25 and 25, separating the cooler cities with lower smoking, obesity and COPD (average COPD 4.7%) from the warmer South, Midwest and desert cities with higher rates (average COPD 6.5%).</p>
{fig("cluster_03_silhouette_scores.png", "Average silhouette width by number of clusters",
     "Both methods reach their highest silhouette at k = 2 (0.214 for k-means and 0.375 for hierarchical clustering), and the k-means score declines steadily afterwards. The silhouette values are not directly comparable between the two lines because they use different distance measures.")}
{fig("cluster_04_silhouette_by_city.png", "Silhouette values of individual cities for k = 3, 4 and 5",
     "Each horizontal bar is one city, grouped by cluster, with the red dashed line marking the average. Several clusters contain cities near or below zero, which are cities that sit between two groups.")}
{fig("cluster_06_kmeans_scatter.png", "K-means clusters for k = 3, 4 and 5",
     "The 50 cities are drawn on the first two principal components of the standardized data, which together keep 55% of the variation, and colored by cluster. The groups touch and overlap at their edges, which agrees with the low silhouette scores.")}
<p>Although k = 2 has the highest silhouette, it only separates two broad halves. The four-group solution (k = 4) was chosen for interpretation because it divides the cities into groups that can be described in plain terms while the silhouette cost is small (0.190 against 0.214). It is shown in the profile heatmap, map and table below, and the choice is a judgment, not something the silhouette demands.</p>
{fig("cluster_07_profiles.png", "What sets each k-means cluster apart (k = 4)",
     "Each cell is the average standardized value of one variable within a cluster, with red meaning above the average of all cities and blue below. Cluster 3 stands out for every pollutant, cluster 2 for COPD, smoking and obesity, and cluster 0 for heat and uninsured adults.")}
{fig("cluster_08_map.png", "Where the four k-means clusters are located",
     "Each dot is one city, colored by cluster. The clean, cool cluster is concentrated in the West and Mountain states, the high-pollution cluster mixes large coastal and interior metropolitan areas, and the heartland cluster fills the Midwest and Southern interior.")}
{cluster_table}
<p>The held-out labels agree with the clusters in an informative way. Cluster 2 (heartland and Deep South) contains 11 cities that were labeled High asthma out of 12, while cluster 0 and cluster 3 are mostly Low asthma (11 of 14 and 7 of 9). Region labels were not used, yet cluster 2 contains no Western city and cluster 1 contains 11 Western cities out of 15, so the clusters recover geography on their own.</p>

<h3>Hierarchical clustering with cosine distance</h3>
<p>Hierarchical clustering was run on the same standardized matrix with cosine distance and average linkage. The tree has a cophenetic correlation of 0.74, which means that the distances implied by the tree reproduce the original pairwise distances reasonably well. The last merge, which joins the final two groups, happens at a height of 1.26, the merge before it at 0.97 and the one before that at 0.93, followed by a drop to 0.82.</p>
{fig("cluster_05_dendrogram.png", "Dendrogram of 50 cities (cosine distance, average linkage)",
     "Cities that merge close to the right edge are very similar, such as Detroit and Cleveland or Denver and Boulder, and the red dashed line cuts the tree into four groups. The longest vertical gap sits between the top merge (1.26) and the next one (0.97), which suggests two main branches, with four groups as the next sensible level.")}
<p><b>Value of k suggested by hierarchical clustering.</b> The largest gap in the tree and the best silhouette (0.375 at k = 2, against 0.363 at k = 3, 0.341 at k = 4 and 0.354 at k = 5) both suggest <b>k = 2</b>, which matches the k-means result. As with k-means, a finer cut into four groups is easier to interpret and has the next clear gap in the tree.</p>
<h3>How the two methods compare</h3>
<p>The two methods agree strongly on the coarse structure and less on the details. At k = 2 the groupings are almost identical (adjusted Rand index 0.92, where 1 means identical partitions). At k = 3 the agreement falls to 0.47 and at k = 4 it is 0.54, rising to 0.67 at k = 5, probably because cosine distance emphasizes the shape of a profile while k-means also responds to how far a city lies from the average.</p>
{fig("cluster_09_agreement.png", "Membership overlap between k-means and hierarchical clusters (k = 4)",
     "Each cell counts the cities shared by one k-means cluster (rows) and one hierarchical cluster (columns). The heartland cluster is recovered almost exactly (12 of its 13 hierarchical members), and the warm cluster overlaps by 11 cities, while the cool and polluted groups are divided differently by the two methods.")}
<p>The hierarchical four-group cut gives a Midwest-and-South group of 13 cities (the k-means heartland cluster plus Jacksonville), a group of 13 hot or humid cities (Phoenix, Riverside, Houston, Dallas, Miami and others), a group of 14 that mixes large polluted metropolitan areas with cooler cities (Atlanta, Boston, Chicago, Denver, Los Angeles, New York and Seattle, among others), and a group of 10 mostly coastal and mountain cities. K-means keeps the nine most polluted metropolitan areas together, whereas the cosine-based tree places several of them with cooler cities that share a similar pattern.</p>
</section>

<section>
<h2>Conclusions</h2>
<p>American cities do fall into recognizable types, although the borders between the types are blurry. Four kinds of city stand out. <b>Large metropolitan areas with the dirtiest air</b> include Los Angeles, New York, Chicago, Atlanta, Washington, Phoenix and San Diego. <b>Heartland and Deep South cities</b>, such as Detroit, Cleveland, Memphis, Nashville and New Orleans, carry the heaviest burden of lung disease. <b>Cool, clean cities</b>, mostly in the West (Seattle, Denver, Boise, Salt Lake City and others), have the lowest average rates of smoking, obesity and COPD. <b>Warm, low-pollution cities</b>, such as Houston, Miami, Las Vegas and Tucson, have clean air but many adults without health insurance.</p>
<p>The most important lesson is that the dirtiest air and the sickest lungs are not in the same places. The big metropolitan areas with the most polluted air have relatively low rates of COPD and smoking, while the heartland cities with only moderately polluted air have the highest rates of COPD, asthma, smoking and obesity. This matches the earlier finding that cities with more fine-particle pollution did not have more asthma, and it suggests that smoking, weight, income and access to health care shape how common lung disease is in a city at least as much as the outdoor air does. Weather and geography sort the cities as well, since the warm group averages about 20 degrees Celsius and the cool group about 12.</p>
<p>These types are a helpful summary and not hard categories. Many cities sit between two groups, and two different grouping methods agreed on the broad picture but placed some cities differently. The air quality values are model estimates, the health values describe whole counties, and only 50 cities were studied, so the findings should be read as patterns and not as proof. For decision makers, the results suggest that smog and smoke warnings matter most in the big metropolitan areas, while stop-smoking and health insurance programs matter most in the heartland and the Deep South.</p>
</section>
"""

page("clustering.html", "Clustering", clustering)

PR = json.loads((ROOT / "data" / "clean" / "pca_results.json").read_text(encoding="utf-8"))
pca_page = f"""
<h1>PCA</h1>
<p class="sub">Reducing 13 daily air quality and weather measurements to a few patterns</p>
<p>Principal component analysis (PCA) takes many related numeric variables and rewrites them as a smaller set of new, uncorrelated variables that keep as much of the original variation as possible. Here it is applied to the {PR["n_rows"]:,} city-days of the daily table, which describe each day with {PR["n_features"]} pollutant and weather measurements. The write-up is organized into Overview, Data Prep, Code, Results and Conclusions.</p>

<section>
<h2>Overview</h2>
<p><b>PCA</b> is an unsupervised, linear method for dimensionality reduction. It looks for the direction in the data along which the observations spread out the most, calls it the first principal component, then looks for the direction of greatest remaining spread that is perpendicular to the first, and so on. Each principal component is a weighted combination of the original variables, the components are uncorrelated with each other, and they are ordered by how much variation they carry. Keeping only the first few therefore compresses the data while discarding the least informative directions.</p>
<h3>Eigenvalues and eigenvectors</h3>
<p>The mathematics sits in the <b>covariance matrix</b> of the standardized variables, which records how every pair of variables moves together. An <b>eigenvector</b> of this matrix is a direction that the matrix only stretches and does not rotate, and the amount of stretching is its <b>eigenvalue</b>. For PCA the eigenvectors are the principal components (the axes), the eigenvalue of each one is the variance of the data along that axis, and the eigenvalue divided by the sum of all eigenvalues is the share of the total variance that component explains. Sorting the eigenvectors from the largest eigenvalue to the smallest gives PC1, PC2, and so on.</p>
<p><b>Singular value decomposition (SVD)</b> reaches the same answer without forming the covariance matrix. A centered data matrix X with n rows is factored as X = U &Sigma; V<sup>T</sup>, where the columns of V are the principal directions (the eigenvectors) and the squared singular values divided by n - 1 are the eigenvalues. Statistical packages usually compute PCA this way because it is numerically stable. The code for this tab checks the equivalence on the actual data: the eigenvalues from the covariance matrix, from scikit-learn and from the SVD agree to about 10<sup>-14</sup>.</p>
{fig("pca_00a_concept.png", "PCA finds the directions of greatest spread",
     "On the left, the two arrows are the eigenvectors of two correlated variables, drawn with a length that reflects how much variance lies along each. On the right, the same points are rotated so that PC1 lies along the horizontal axis and holds most of the variance (the data are synthetic).")}
<h3>Dimensionality reduction and the challenges of many dimensions</h3>
<p><b>Dimensionality reduction</b> means describing each observation with fewer variables while losing as little information as possible. It matters for several reasons. People can only look at two or three dimensions at once, so reduction makes it possible to see structure in data that have many columns. Real measurements are often redundant (here PM2.5 and PM10 are almost the same signal, and the three temperature variables move together), and reduction removes this duplication, which also avoids the instability that correlated predictors cause in later models. Fewer variables mean faster computation and less noise.</p>
<p>High-dimensional data bring particular problems that are often called the <b>curse of dimensionality</b>. As the number of dimensions grows, the space becomes so large that data points become sparse, and a fixed number of observations covers less and less of it. Distances also lose meaning, because the nearest and farthest neighbors of a point end up at almost the same distance, which damages methods based on distance such as clustering and nearest-neighbor classification. Models with many inputs overfit more easily, and results are harder to explain. Projecting the data onto a few principal components addresses these problems by keeping the directions that carry the signal.</p>
{fig("pca_00b_curse_of_dimensionality.png", "The curse of dimensionality",
     "Averaged over 50 simulations of 300 random points, the ratio of the nearest to the farthest distance from one point climbs toward 1 as the number of dimensions grows, which means that neighbors stop looking different from strangers. The values come from a simulation of uniformly random points.")}
</section>

<h3>How PCA is used in this project</h3>
<p>The daily table describes every city-day with 13 measurements that overlap heavily: PM2.5 and PM10 are almost the same signal, three temperature columns move together, and ozone rises with sunshine. PCA is used here to (1) find out which measurements move together and which are independent, (2) shrink the 13 measurements to a few patterns that still describe most of the day-to-day variation, (3) draw the 20,075 city-days on a flat plot so that seasons, cities and AQI categories can be compared by eye, and (4) prepare a smaller, less redundant set of inputs for the models in the later parts of the project.</p>
</section>

<section>
<h2>Data Prep</h2>
<p>PCA requires a <b>numeric</b> matrix with <b>no missing values</b> and no label columns. Because it works on variance, variables with large units would dominate: carbon monoxide is measured in hundreds while precipitation is mostly near zero. Each column was therefore <b>centered and scaled</b> to a mean of 0 and a standard deviation of 1 before the analysis, so that PCA effectively decomposes the correlation matrix.</p>
<p>The sample is the daily city table: <b>{PR["n_rows"]:,} city-days by {PR["n_features"]} numeric columns</b>. The variables are PM2.5, PM10, carbon monoxide, nitrogen dioxide, sulphur dioxide, maximum ozone, maximum AQI, mean, maximum and minimum temperature, precipitation, maximum wind speed and solar radiation. The city, state, date, month, season, region, AQI category and rainy-day flag were removed from the matrix and kept aside, to color the plots afterwards. Extreme smoke days were kept in the data, since they are real events, which means that they can pull the components toward pollution.</p>
{fig("pca_01a_data_before.png", "Before transforming: the cleaned daily table",
     "The table mixes label columns (orange: city, date, season and AQI category) with measurements in very different units, such as carbon monoxide in the hundreds and precipitation in single digits. Only the numeric columns (blue headers) go into PCA.")}
<h3>The transformation, step by step</h3>
<ol>
<li><b>Remove the labels.</b> City, state, date, month, season, region, AQI category and the rainy-day flag were taken out of the matrix and kept aside, to color the plots afterwards.</li>
<li><b>Keep the 13 numeric measurements</b> for all {PR["n_rows"]:,} city-days. There were no missing values to fill.</li>
<li><b>Center and scale every column.</b> Each value had its column average subtracted and was divided by the column standard deviation. For example, on 1 January 2023 in Albuquerque the mean temperature of 6.5 C (average of all city-days 15.57, standard deviation 9.44) becomes -0.96, and carbon monoxide of 280.6 (average 225.95, standard deviation 89.67) becomes 0.61.</li>
</ol>
{fig("pca_01_data_sample.png", "After transforming: the data given to PCA",
     "Each row is one city-day and each column is one standardized measurement, with no names or labels attached; the first seven rows and ten of thirteen columns are shown. Pink cells are below the overall average and blue cells above it.")}
<ul>
<li><a href="{CLEANLINK}pca_input_numeric.csv">pca_input_numeric.csv</a>: the full {PR["n_rows"]:,} x {PR["n_features"]} numeric matrix in original units</li>
<li><a href="{CLEANLINK}pca_scores_sample.csv">pca_scores_sample.csv</a>: the scores on the first five components for a random sample of 2,000 city-days, with the labels used for coloring</li>
<li><a href="{CLEANLINK}daily_city_air_weather_clean.csv">daily_city_air_weather_clean.csv</a>: the cleaned daily table the matrix was taken from</li>
</ul>
</section>

<section>
<h2>Code</h2>
<p>The analysis is written in <b>Python 3.14</b> with <code>pandas</code>, <code>numpy</code> (<code>numpy.linalg.svd</code>), <code>scikit-learn</code> (<code>StandardScaler</code>, <code>PCA</code>), <code>matplotlib</code> and <code>seaborn</code>.</p>
<ul>
<li><a href="{CODE05}"><code>05_pca.py</code></a> on GitHub: standardizes the data, fits PCA, verifies the result with SVD, and draws every figure on this tab</li>
<li><a href="{CLEANLINK}pca_results.json">pca_results.json</a>: all numbers quoted below (eigenvalues, loadings, scores)</li>
</ul>
</section>

<section>
<h2>Results</h2>
<h3>How many components are needed</h3>
<p>The first component explains <b>35.2%</b> of the total variance (eigenvalue 4.57), the second <b>27.1%</b> (3.52), and the third 9.6% (1.25), so the first two together carry <b>62.2%</b> and the first three <b>71.9%</b>. Three components have an eigenvalue above 1 (the Kaiser rule, which keeps components that explain more than one original variable's worth of variance). Reaching 80% of the variance takes 5 components, 90% takes 7 and 95% takes 8, so the 13 variables are reducible to a handful of patterns but not to just two.</p>
{fig("pca_02_scree.png", "Scree plot with cumulative variance",
     "The bars show that the first two components stand well above the rest and the curve flattens after the third, while the orange line reaches 80% at five components and 95% at eight. The sharp drop after PC2 (27.1% to 9.6%) marks the natural place to stop for visualization.")}
<h3>Relationship between variables and components</h3>
<p>Each component is a weighted sum of the variables, and the weights are called <b>loadings</b> (the entries of the eigenvector). A large positive or negative loading means that the variable contributes strongly to the component, and variables with loadings of the same sign move together along it. The heatmap reads as a recipe for each component.</p>
{fig("pca_03_loadings.png", "Loadings of each variable on the first five components",
     "Red cells push a component up and blue cells push it down. PC1 is dominated by temperature, ozone, AQI and solar radiation, PC2 by nitrogen dioxide, carbon monoxide and particles, and PC3 by precipitation and wind.")}
<ul>
<li><b>PC1 (35.2%), the warm and sunny axis.</b> Temperature (loadings 0.35 to 0.39), maximum ozone (0.37), AQI (0.37) and solar radiation (0.34) all load positively, with PM2.5 (0.28) and PM10 (0.30) smaller. The score correlates 0.80 with mean temperature and 0.80 with ozone. This is the chemistry of summer smog: sunny, hot days go together with high ozone.</li>
<li><b>PC2 (27.1%), the combustion pollution axis.</b> Nitrogen dioxide (0.43), carbon monoxide (0.43), PM2.5 (0.35) and sulphur dioxide (0.34) load positively while temperatures load negatively (about -0.25). Its score correlates 0.66 with PM2.5. High values mean a day with traffic and heating pollution building up in cool, still air.</li>
<li><b>PC3 (9.6%), the wet and windy axis.</b> Precipitation (0.77) and wind (0.44) load positively and solar radiation negatively (-0.31), which describes stormy, cloudy weather.</li>
</ul>
{fig("pca_04_biplot.png", "Biplot of city-days and variable loadings",
     "Each dot is one city-day (colored by season) plotted by its scores on PC1 and PC2, and each arrow shows how one variable points in that plane, so arrows pointing the same way are positively correlated and arrows at right angles are unrelated. Summer days sit to the right with the temperature and ozone arrows, while winter days sit upward and to the left with the pollution arrows.")}
<p>The biplot shows the relationships directly. The three temperature arrows and solar radiation point almost the same way, which confirms that they are near-duplicates, and the pollutant arrows (nitrogen dioxide, carbon monoxide, sulphur dioxide and particles) form a second bundle that is roughly at a right angle to the temperature bundle, which means that heat and combustion pollution vary largely independently. PM2.5 sits between the two bundles, since fine particles come both from local combustion and from sunlight-driven chemistry and smoke. By season, the average PC1 score is 2.08 in summer and -1.74 in winter, and the average PC2 score is 1.11 in winter and -0.77 in summer.</p>
{fig("pca_05_aqi_categories.png", "City-days in the PC1 to PC2 plane, colored by AQI category",
     "The unhealthy categories move steadily toward the upper right, with the average PC1 score rising from -1.55 on Good days to 3.44 on Unhealthy for Sensitive Groups, 5.24 on Unhealthy and 7.11 on Very Unhealthy days. The two components were built without any knowledge of the AQI category, so this separation shows that they capture the conditions that make air unhealthy.")}
{fig("pca_06_3d.png", "The first three principal components",
     "A random sample of 4,000 city-days is drawn in the space of PC1, PC2 and PC3 and colored by season. The third axis (9.6% of the variance) adds spread mainly for rainy and windy days and separates the seasons little.")}
<h3>City profiles</h3>
{fig("pca_07_city_averages.png", "Each city's average position on the first two components",
     "Every dot is the average of one city's 365 daily scores, colored by region. Los Angeles has the highest average PC1 (2.07) and PC2 (3.67), Anchorage the lowest PC1 (-3.10), and Honolulu, Tucson and Miami the lowest PC2 (-2.40, -2.09 and -2.00).")}
<p>Averaged over the year, the cities with the highest PC1 are Los Angeles (2.07), Phoenix (1.83), Riverside (1.68) and Bakersfield (1.06), which are hot, sunny and high in ozone, and the lowest are Anchorage (-3.10), Portland (-1.33), Colorado Springs (-1.22) and Boise (-1.12). On PC2, Los Angeles (3.67), New York (2.38), Detroit (1.37) and Philadelphia (1.26) have the heaviest combustion pollution, whereas Honolulu, Tucson, Miami and Austin are lowest. Los Angeles is the only city that stands out on both axes.</p>
</section>

<section>
<h2>Conclusions</h2>
<p>The 13 daily measurements are mostly telling the same few stories. About three patterns describe most of what changes from one day to the next: how hot and sunny the day is, how much traffic and heating pollution has built up, and how wet and windy the weather is. Hot, sunny summer days are when ozone smog is worst, while cool, still winter days are when exhaust-type pollution builds up near the ground. Fine particles belong to both stories, since they come from local pollution, from sunlight-driven chemistry and from smoke, which is why weather alone does not predict them well.</p>
<p>The same two patterns line up with the air quality ratings, even though the method knew nothing about them: days rated Unhealthy or Very Unhealthy sit at the extreme end of both patterns, while Good days sit at the opposite end. Cities have their own signatures. Los Angeles combines both kinds of pollution, Phoenix and Riverside are mainly hot and smoggy, Anchorage and Portland are cool, with little of the warm-weather smog, and Honolulu, Tucson and Miami have the lowest build-up of combustion pollution. For everyday life, this means that summer afternoons are the time to watch for smog and cold winter days are the time to watch for traffic and heating pollution in big cities.</p>
<p>The results also help the rest of the project, because a few combined patterns can replace many overlapping measurements in later predictions. The patterns are a simplified summary, and rare events such as the 2023 smoke episodes do not fit neatly into the usual seasonal stories, so they deserve separate attention.</p>
</section>
"""

page("pca.html", "PCA", pca_page)

# ============================================================================ NAIVE BAYES AND DECISION TREES TABS (Module 3)
NR = json.loads((ROOT / "data" / "clean" / "nb_dt_results.json").read_text(encoding="utf-8"))
CODE06 = f"{GH}/blob/main/code/06_naive_bayes_trees.py"


def pc(x, d=1):
    return f"{x * 100:.{d}f}%"


BASE = NR["baseline_accuracy_test"]
LC, SP = NR["label_counts"], NR["split"]
NBM = NR["nb"]["Multinomial NB (binned values)"]
NBS = NR["nb"]["Multinomial NB (scaled values)"]
NBB = NR["nb"]["Bernoulli NB (binned values)"]
NBG = NR["nb"]["Gaussian NB (raw values)"]
DT = NR["dt"]
T1, T2, T3 = (DT["Tree 1: Gini, depth 3, weather"], DT["Tree 2: Entropy, depth 3, weather"],
              DT["Tree 3: Gini, depth 4, weather + location"])
TW, TL = DT[NR["dt_names"]["tuned_weather"]], DT[NR["dt_names"]["tuned_location"]]
SE = NR["split_example"]
MOD_SHARES = [sum(r[1] for r in t['confusion']) / sum(map(sum, t['confusion'])) * 100 for t in (T1, T2, T3)]
MOD_LO, MOD_HI = round(min(MOD_SHARES)), round(max(MOD_SHARES))
NBT, DTT, DTTT = NR["nb_time_holdout"], NR["dt_time_holdout"], NR["dt_time_holdout_tuned"]
NBL = NR["nb_location"]
THR = NR["time_holdout_rows"]
IMPW, IMPL = TW["importance"], TL["importance"]
TEMP_SUM = IMPW["temp_mean"] + IMPW["temp_max"] + IMPW["temp_min"]


def nb_row(name, r):
    return (f"<tr><td>{name}</td><td>{pc(r['accuracy'])}</td><td>{r['macro_f1']:.2f}</td>"
            f"<td>{pc(r['recall']['Good'], 0)}</td><td>{pc(r['recall']['Moderate'], 0)}</td>"
            f"<td>{pc(r['recall']['Unhealthy'], 0)}</td><td>{pc(r['precision']['Unhealthy'], 0)}</td></tr>")


NB_TABLE = ("<table><tr><th>Variant</th><th>Accuracy</th><th>Macro-F1</th><th>Recall: Good</th><th>Recall: Moderate</th>"
            "<th>Recall: Unhealthy</th><th>Precision: Unhealthy</th></tr>"
            f"<tr><td><i>Always predict Moderate (baseline)</i></td><td>{pc(BASE)}</td><td>0.25</td><td>0%</td><td>100%</td><td>0%</td><td>-</td></tr>"
            + nb_row("Multinomial, scaled values", NBS) + nb_row("Multinomial, binned values", NBM)
            + nb_row("Bernoulli, binned values", NBB) + nb_row("Gaussian, raw values", NBG) + "</table>")


def dt_row(name, r):
    return (f"<tr><td>{name}</td><td>{r['criterion']}</td><td>{r['depth']}</td><td>{r['leaves']}</td>"
            f"<td>{pc(r['train_accuracy'])}</td><td>{pc(r['accuracy'])}</td><td>{r['macro_f1']:.2f}</td>"
            f"<td>{pc(r['recall']['Unhealthy'], 0)}</td></tr>")


DT_TABLE = ("<table><tr><th>Tree</th><th>Criterion</th><th>Depth</th><th>Leaves</th><th>Training accuracy</th>"
            "<th>Testing accuracy</th><th>Macro-F1</th><th>Recall: Unhealthy</th></tr>"
            f"<tr><td><i>Always predict Moderate (baseline)</i></td><td>-</td><td>0</td><td>1</td><td>{pc(LC['Moderate'] / NR['n_rows'])}</td><td>{pc(BASE)}</td><td>0.25</td><td>0%</td></tr>"
            + dt_row("Tree 1: weather", T1) + dt_row("Tree 2: weather", T2) + dt_row("Tree 3: weather + location", T3)
            + dt_row("Tuned: weather", TW) + dt_row("Tuned: weather + location", TL) + "</table>")

DATA_LINKS = f"""<ul>
<li><a href="{CLEANLINK}nb_dt_labeled_dataset.csv">nb_dt_labeled_dataset.csv</a>: the full labeled sample ({NR['n_rows']:,} city-days, weather features plus the label)</li>
<li><a href="{CLEANLINK}daily_city_air_weather_clean.csv">daily_city_air_weather_clean.csv</a>: the cleaned daily table the sample comes from</li>
<li>Raw data: <a href="{RAWLINK}openmeteo_weather_daily_raw.csv">daily weather</a>, <a href="{RAWLINK}openmeteo_air_quality_hourly_raw.csv">hourly air quality</a> (the AQI that defines the label) and <a href="{RAWLINK}cities_reference.csv">city locations</a></li>
</ul>"""

SPLIT_TEXT = f"""<p>A supervised method needs <b>labeled data</b>: every row must come with the correct answer so that the method can learn from it and be graded against it. Only rows with a known label can be used, and here every one of the {NR['n_rows']:,} city-days has one. The label is the AQI group of the day. The cleaned table already contained the official EPA category of each day (computed from the pollutant readings in Part 1), and the four upper categories were merged into three groups because Unhealthy (293 days) and Very Unhealthy (71 days) are too rare to learn on their own and no Hazardous day occurred: <b>Good</b> ({LC['Good']:,} days, {pc(NR['label_share']['Good'])}), <b>Moderate</b> ({LC['Moderate']:,} days, {pc(NR['label_share']['Moderate'])}) and <b>Unhealthy</b> ({LC['Unhealthy']:,} days, {pc(NR['label_share']['Unhealthy'])}), the last meaning an AQI of 101 or more (unhealthy for sensitive groups or worse).</p>
<p>The inputs are the daily weather: mean, maximum and minimum temperature, precipitation, maximum wind speed, solar radiation, and the month of the year. <b>No pollutant column is used</b>, because the label is computed from pollutant readings, so including them would hand the answer to the method. The city is also left out, which keeps the question the one asked in the Introduction: can the air quality group be forecast from the weather alone? A second experiment adds each city's latitude and longitude to test how much location contributes.</p>
{fig("nb_01_labeled_sample.png", "A sample of the labeled data",
     "Each row is one city on one day, with the weather inputs on the left and the answer on the right (orange columns). Only the label column and the weather columns are used by the methods, and the city and date are kept only to identify rows.")}
<h3>Training set and testing set</h3>
<p>The labeled rows were split at random into a <b>training set</b> (80%, {SP['train_rows']:,} rows), which the method uses to learn, and a <b>testing set</b> (20%, {SP['test_rows']:,} rows), which is kept aside and used only once, to measure how well the learned rules work on days it has never seen. The split was <b>stratified</b>, which means that each set has the same share of Good, Moderate and Unhealthy days as the whole sample, and the random seed was fixed (42) so the split can be reproduced. The two sets must be <b>disjoint</b>, with no row in both. If a day were in both sets, the method could simply memorize it and the test would measure memory, not the ability to predict new days, so accuracy would look better than it really is. Every row carries an identifier (<code>row_id</code>), and the code confirms that the two sets share <b>{SP['overlap_rows']} rows</b>.</p>
<div class="figrow">
{fig("nb_02_train_sample.png", "Training set", f"The first rows of the {SP['train_rows']:,}-day training set, used to learn the rules.", True)}
{fig("nb_03_test_sample.png", "Testing set", f"The first rows of the {SP['test_rows']:,}-day testing set, used only to grade the learned rules.", True)}
</div>
{fig("nb_05_split_balance.png", "Both sets have the same label proportions",
     "Stratified sampling keeps about 30% Good, 61% Moderate and 9% Unhealthy days in both sets. The shares differ by less than 0.1 percentage points between the training and testing sets.", True)}
<p>One caution applies to any random split of daily data: days next to each other, and days from the same city, resemble each other, so a random split can be slightly optimistic. A harder check is reported in the Results section, where the rules are learned from January to September and tested on October to December.</p>"""

# ---------------------------------------------------------------- NAIVE BAYES PAGE
naivebayes = f"""
<h1>NaiveBayes</h1>
<p class="sub">Can the air quality group of a day be guessed from the weather with simple probabilities?</p>
<p>This tab applies Naive Bayes to the labeled city-days to predict whether a day will be Good, Moderate or Unhealthy from that day's weather. It is organized into Overview, Data Prep, Code, Results and Conclusions.</p>

<section>
<h2>Overview</h2>
<p><b>Naive Bayes</b> is a supervised classifier: it learns from days whose answer is already known and then assigns a group to days it has not seen. It is built on Bayes' theorem, which turns the question "how likely is this weather on an Unhealthy day?" into the question that matters, "how likely is an Unhealthy day, given this weather?". For a day with weather features x1, x2, ..., xn, the score of group c is proportional to P(c) &times; P(x1 | c) &times; P(x2 | c) &times; ... &times; P(xn | c). The first term, the <b>prior</b>, is how common the group is overall. The other terms are <b>likelihoods</b>, estimated by counting how often each weather condition occurred on days of that group in the training data. The group with the highest score is the prediction.</p>
<p>The method is called <b>naive</b> because it multiplies the likelihoods as if the features were unrelated once the group is known. That is rarely exactly true (here, mean, maximum and minimum temperature move together almost perfectly), yet Naive Bayes often classifies well because only the ranking of the groups matters, not the exact probabilities. It is very fast, works with little data and many features, and is a classic choice for spam filtering, document and sentiment classification, and medical screening. A small <b>smoothing</b> count (alpha = 1, called Laplace smoothing) is added to every count so that a condition never seen in a group does not force its probability to zero.</p>
{fig("nb_00a_ingredients.png", "The ingredients of Naive Bayes",
     "The left panel is the prior (how common each group is among training days), and the other two panels are likelihoods (how solar radiation and temperature are distributed within each group). Unhealthy days (red) cluster at high sunshine and heat, which is exactly the kind of evidence Naive Bayes multiplies together.")}
<h3>Multinomial, Bernoulli and Gaussian Naive Bayes</h3>
<p>The versions differ in how they model the features. <b>Multinomial Naive Bayes</b> (the standard version used in class) treats each feature as a <i>count</i> or frequency of an event, as in the number of times each word appears in a document. The likelihood of feature i in group c is (count of i among days of group c + alpha) divided by (total count in group c + alpha &times; number of features), so every feature must be a non-negative number. <b>Bernoulli Naive Bayes</b> instead treats every feature as a yes/no question: the feature is present (1) or absent (0). Its likelihood is the share of days in the group on which the feature is present, and, unlike the multinomial version, it also uses <i>absence</i> as evidence, because a 0 contributes the probability that the feature is not present. It suits short texts and binary indicators. A third version, <b>Gaussian Naive Bayes</b>, models each continuous measurement within a group with a normal curve and is included here as a comparison.</p>
{fig("nb_00b_multinomial_vs_bernoulli.png", "One day as bin columns: how the two versions read it",
     f"A real day ({NR['example_row']['city']}, {NR['example_row']['date']}) is shown as 0/1 bin columns, with each filled cell marking the range its weather value falls in. Multinomial Naive Bayes counts only the bins that occur, while Bernoulli Naive Bayes also uses the bins that do not occur.", True)}
<h3>What is done with it here</h3>
<p>The Introduction asked whether an air quality group can be forecast from weather alone. Naive Bayes is used to answer this as a first, simple attempt: the probabilities of each weather condition within Good, Moderate and Unhealthy days are learned from the training set and used to classify the testing set. Four versions are compared (multinomial on scaled values, multinomial on binned values, Bernoulli and Gaussian), and results are judged with accuracy, a majority-class baseline, and the confusion matrix. <b>Recall</b> (the share of days of a group that were found) and <b>precision</b> (the share of days predicted as a group that really belonged to it) are reported for each group, and <b>macro-F1</b> averages the balance of precision and recall over the three groups, so a method that ignores a rare group scores low even if its accuracy looks high.</p>
</section>

<section>
<h2>Data Prep</h2>
{SPLIT_TEXT}
<h3>Preparing the numbers for Multinomial Naive Bayes</h3>
<p>Multinomial Naive Bayes in Python (<code>scikit-learn</code>) accepts only <b>numeric, non-negative</b> input. The weather columns are numeric, but temperatures drop below zero in winter, so they cannot be used directly. Two preparations were tested. First, every column was <b>scaled</b> to the range 0 to 1 using the training set only. Second, every column was <b>binned</b> into five groups of equal size (quantile bins, learned from the training set) and each day was recorded as a set of 0/1 columns, one per bin, giving {NR['nb_binned_columns']} columns (precipitation has only three bins, because more than half of all days are dry). The binned version is the closest match to how multinomial Naive Bayes is normally used, because each 1 marks an event that occurred. The scaled version is kept in the comparison because it shows what goes wrong without this step.</p>
{fig("nb_04_binned_sample.png", "After preparation: weather turned into 0/1 bin columns",
     "Each day now has exactly one 1 per weather variable, in the column for the range that its value falls in (only two of the seven variables are shown). The label on the right is not an input; it is the answer used for training and grading.")}
{DATA_LINKS}
<ul>
<li><a href="{CLEANLINK}nb_train_binned.csv">nb_train_binned.csv</a> and <a href="{CLEANLINK}nb_test_binned.csv">nb_test_binned.csv</a>: the prepared training and testing sets (0/1 bin columns plus label and <code>row_id</code>)</li>
</ul>
</section>

<section>
<h2>Code</h2>
<p>The analysis is written in <b>Python</b> with <code>pandas</code>, <code>numpy</code>, <code>scikit-learn</code> (<code>MultinomialNB</code>, <code>BernoulliNB</code>, <code>GaussianNB</code>, <code>KBinsDiscretizer</code>, <code>MinMaxScaler</code>, <code>train_test_split</code>), <code>matplotlib</code> and <code>seaborn</code>.</p>
<ul>
<li><a href="{CODE06}"><code>06_naive_bayes_trees.py</code></a> on GitHub: creates the labels, splits the data, prepares the features, fits all Naive Bayes variants and draws every figure on this tab (the same script also produces the Decision Trees tab)</li>
<li><a href="{CLEANLINK}nb_dt_results.json">nb_dt_results.json</a>: every number quoted on this tab</li>
</ul>
</section>

<section>
<h2>Results</h2>
<p>All results are measured on the <b>testing set</b> ({SP['test_rows']:,} days that were never used for learning). The most important reference is a method that ignores the weather and always answers the most common group, Moderate, which is correct on <b>{pc(BASE)}</b> of days. Smoothing was alpha = 1 and the binned versions used five quantile bins; the class priors were learned from the training set ({pc(NR['label_share']['Good'], 0)} Good, {pc(NR['label_share']['Moderate'], 0)} Moderate, {pc(NR['label_share']['Unhealthy'], 0)} Unhealthy).</p>
{NB_TABLE}
{fig("nb_06_confusion_matrices.png", "Confusion matrices of the four Naive Bayes versions",
     "Rows are the true group and columns are the predicted group, so the diagonal holds the correct answers. The scaled multinomial version (far left) predicts Moderate for every day, while the binned and Gaussian versions spread their predictions over all three groups and find most of the Unhealthy days.")}
<p><b>Scaled values fail in an instructive way.</b> The multinomial version on scaled values reaches {pc(NBS['accuracy'])} accuracy, equal to the baseline, but its confusion matrix shows that it predicts Moderate for all {SP['test_rows']:,} days, so it never finds a Good or Unhealthy day (macro-F1 {NBS['macro_f1']:.2f}). Values between 0 and 1 are not counts, so the Moderate prior dominates every decision.</p>
<p><b>Binned values give a working classifier, but with lower accuracy.</b> Multinomial Naive Bayes on binned values has an accuracy of {pc(NBM['accuracy'])}, below the baseline, but a macro-F1 of {NBM['macro_f1']:.2f} against {NBS['macro_f1']:.2f}. It finds {pc(NBM['recall']['Unhealthy'], 0)} of the Unhealthy days ({round(NBM['recall']['Unhealthy'] * 372)} of 372) and {pc(NBM['recall']['Good'], 0)} of the Good days. The price is a large number of false alarms: only {pc(NBM['precision']['Unhealthy'], 0)} of the days it labels Unhealthy really were, so about seven of every ten warnings would be wrong. Bernoulli Naive Bayes gives almost the same result ({pc(NBB['accuracy'])} accuracy, macro-F1 {NBB['macro_f1']:.2f}), which is expected because the inputs are binary, and Gaussian Naive Bayes on raw values finds the most Unhealthy days ({pc(NBG['recall']['Unhealthy'], 0)}) at the lowest accuracy ({pc(NBG['accuracy'])}).</p>
{fig("nb_07_metrics_comparison.png", "Accuracy versus macro-F1 for each version",
     "Accuracy (blue) rewards the version that always answers Moderate, while macro-F1 (orange) rewards the versions that tell the groups apart. The dashed line is the accuracy of always predicting Moderate.", True)}
<h3>What the classifier learned</h3>
{fig("nb_08_top_bins.png", "Weather conditions that most separate Unhealthy days from Good days",
     "Bars to the right (red) are conditions much more common on Unhealthy days than on Good days, and bars to the left (blue) are conditions much more common on Good days. Hot, sunny days from May to July (the month bin 5.0 to 8.0) point to Unhealthy air, while cold, dim days from October to December (bin 10.0 to 12.0) point strongly to Good air.", True)}
<p>The strongest evidence for an Unhealthy day is a maximum temperature of 29.9 C or more, solar radiation of 24.6 MJ per square meter or more, and the months May to July. The strongest evidence for a Good day is the months October to December, followed by cold days (maximum temperature below 11.9 C) with little sunshine. This matches the chemistry of smog described in the Introduction.</p>
<h3>Two robustness checks</h3>
<ul>
<li><b>Adding location.</b> With each city's latitude and longitude binned and added as inputs, multinomial Naive Bayes reaches {pc(NBL['accuracy'])} accuracy and macro-F1 {NBL['macro_f1']:.2f}, only a small improvement (from {pc(NBM['accuracy'])} and {NBM['macro_f1']:.2f}). Naive Bayes cannot combine location and weather in a flexible way, because it treats them as independent.</li>
<li><b>Learning from January to September and testing on October to December</b> ({THR['train']:,} training days, {THR['test']:,} testing days). Accuracy is {pc(NBT['accuracy'])} against a baseline of {pc(NBT['baseline_accuracy'])} for that period, which is a clearer gain over guessing, but only {pc(NBT['recall']['Unhealthy'], 0)} of the Unhealthy days are found, because very few Unhealthy days occur in autumn at all. The baseline differs from the main experiment because the mix of groups changes with the season, so these accuracies should be compared with their own baselines and not with each other.</li>
</ul>
</section>

<section>
<h2>Conclusions</h2>
<p><b>Weather alone is a weak forecaster of the daily air quality group.</b> Every Naive Bayes version that actually tells the groups apart has an accuracy ({pc(NBG['accuracy'])} to {pc(NBB['accuracy'])}) below the {pc(BASE)} obtained by always answering Moderate, so on accuracy alone the classifier adds nothing. What it adds is sensitivity: it finds about seven in ten Unhealthy days, which the baseline never does, at the cost of many false alarms. For a public health warning, where a missed Unhealthy day is usually worse than an unnecessary caution, that trade can be reasonable, but a warning that is wrong seven times in ten would soon be ignored.</p>
<p><b>The learned evidence agrees with the science.</b> Heat, strong sunshine and the summer months raise the probability of an Unhealthy day, and the cool, dim days of late autumn almost guarantee good air. This answers the part of the Introduction's tenth question about which conditions are the best warning signs: high temperature and solar radiation in the warm months.</p>
<p><b>Limits.</b> The independence assumption is clearly violated, because the three temperature columns are nearly copies of each other and are counted as separate evidence. The AQI values come from an atmospheric model on a coarse grid, one year of data was used, and neighboring days are similar, so the random split is somewhat optimistic. Unusual events such as the June 2023 smoke cannot be anticipated from local weather at all. The next method, decision trees, can combine conditions (for example heat <i>and</i> calm winds) and is tested on the same data and split.</p>
</section>
"""
page("naivebayes.html", "NaiveBayes", naivebayes)

# ---------------------------------------------------------------- DECISION TREES PAGE
SEP, SEL, SER = SE["parent"], SE["left"], SE["right"]
pp = [c / SEP["n"] for c in SEP["counts"]]
dectrees = f"""
<h1>DecTrees</h1>
<p class="sub">Which weather rules best separate clean days from unhealthy ones?</p>
<p>This tab applies decision trees to the same labeled city-days and the same training and testing sets as the Naive Bayes tab, so the two methods can be compared fairly. It is organized into Overview, Data Prep, Code, Results and Conclusions.</p>

<section>
<h2>Overview</h2>
<p>A <b>decision tree</b> is a flowchart of yes/no questions about the inputs. A day enters at the top (the <b>root node</b>), is sent left or right depending on the answer to a question such as "is the month October or later?", meets another question in an <b>internal (decision) node</b>, and finally lands in a <b>leaf node</b>, which holds the prediction (the most common group among the training days that ended up there). Trees are popular because the finished model can be read, explained and drawn, they need no scaling of the inputs, they handle numbers and categories, and they capture <b>interactions</b>, such as "hot <i>and</i> calm". They are used for medical diagnosis, credit decisions, customer behavior, and many other classification tasks (a variant predicts numbers instead of groups).</p>
{fig("dt_00a_tree_anatomy.png", "The anatomy of a decision tree (a real tree of depth 2 from this project's training data)",
     "Each box shows its question, its impurity (gini) and how many training days reached it. The root asks the first question, internal nodes ask further questions, and leaves stop and predict the most common group, shown in the colour of that group.")}
<h3>How a tree chooses its questions: Gini, entropy and information gain</h3>
<p>A tree is grown from the top. At every node, the algorithm tries every input and every possible cut point and keeps the question that makes the two resulting groups as <b>pure</b> as possible, meaning each group is dominated by a single AQI group. To compare questions, purity needs a number, and two standard measures are used. <b>Gini impurity</b> is 1 - (p1&sup2; + p2&sup2; + ... + pk&sup2;), where pi is the share of days in the node that belong to group i. <b>Entropy</b> is -(p1 log2 p1 + p2 log2 p2 + ... + pk log2 pk), measured in bits. Both are 0 for a node that holds only one group and largest when the groups are mixed in equal shares (for two groups the maximum is 0.5 for Gini and 1 bit for entropy). They are used because they turn "how mixed is this node?" into a number that can be compared across candidate questions. Gini is slightly cheaper to compute, while entropy punishes mixed nodes slightly more, and they usually select similar trees.</p>
<p>The quality of a question is its <b>gain</b>: the impurity of the parent node minus the weighted average impurity of the two child nodes, where each child is weighted by the share of days it receives. When entropy is the impurity, this gain is called <b>information gain</b>, and with Gini it is the Gini decrease. The question with the largest gain is chosen, the process repeats inside each child, and it stops when a node is pure, too small, or a depth limit is reached.</p>
{fig("dt_00b_impurity_curves.png", "Gini and entropy for a node with two groups",
     "Both curves are zero when the node contains only one group (left and right edges) and peak when the two groups are equally mixed (center). The shapes are similar, which is why the two criteria usually pick similar splits.", True)}
<h3>A worked example from the training data</h3>
<p>Take the root question chosen by the Gini tree, "is the month at most {SE['threshold']:.1f}" (that is, January to September). The {SEP['n']:,} training days contain {SEP['counts'][0]:,} Good, {SEP['counts'][1]:,} Moderate and {SEP['counts'][2]:,} Unhealthy days, so the shares are {pp[0]:.3f}, {pp[1]:.3f} and {pp[2]:.3f}.</p>
<ul>
<li><b>Gini of the parent</b> = 1 - ({pp[0]:.3f}&sup2; + {pp[1]:.3f}&sup2; + {pp[2]:.3f}&sup2;) = <b>{SEP['gini']:.3f}</b>.</li>
<li><b>Entropy of the parent</b> = -({pp[0]:.3f} log2 {pp[0]:.3f} + {pp[1]:.3f} log2 {pp[1]:.3f} + {pp[2]:.3f} log2 {pp[2]:.3f}) = <b>{SEP['entropy']:.3f}</b> bits.</li>
<li>The question sends {SEL['n']:,} days to the left (Gini {SEL['gini']:.3f}, entropy {SEL['entropy']:.3f}) and {SER['n']:,} days to the right (Gini {SER['gini']:.3f}, entropy {SER['entropy']:.3f}). The right-hand group, October to December, holds {SER['counts'][2]} Unhealthy days out of {SER['n']:,}.</li>
<li><b>Weighted Gini of the children</b> = ({SEL['n']:,} &times; {SEL['gini']:.3f} + {SER['n']:,} &times; {SER['gini']:.3f}) / {SEP['n']:,} = {SE['weighted_gini']:.3f}, so the <b>Gini gain</b> is {SEP['gini']:.3f} - {SE['weighted_gini']:.3f} = <b>{SE['gini_gain']:.3f}</b>.</li>
<li><b>Weighted entropy of the children</b> = ({SEL['n']:,} &times; {SEL['entropy']:.3f} + {SER['n']:,} &times; {SER['entropy']:.3f}) / {SEP['n']:,} = {SE['weighted_entropy']:.3f}, so the <b>information gain</b> is {SEP['entropy']:.3f} - {SE['weighted_entropy']:.3f} = <b>{SE['information_gain']:.3f}</b> bits.</li>
</ul>
{fig("dt_00c_split_example.png", "The root split in numbers",
     "The colored bars show the share of Good, Moderate and Unhealthy days before and after the split. The gains are small because no single question separates the groups well, but this was still the best question available at the root.")}
<p>The two measures do not always agree: on this same data, the Gini criterion chooses the month as its first question, while the entropy criterion chooses solar radiation (see the two trees in the Results section).</p>
<h3>Why there is an infinite number of possible trees</h3>
<p>Many different trees can be built from the same data. A numeric input such as temperature can be cut at <b>any real number</b>, and every value between two neighboring observed temperatures separates the training days in exactly the same way yet gives a different tree for new days, so the choices are unlimited. Beyond thresholds, any input can be reused at any depth and in any order, the depth and the stopping rules are free parameters, and different criteria (Gini or entropy) or different random tie-breaking give different trees. A tree allowed to grow until every leaf is pure can even memorize the training data, which gives one more valid tree. Finding the single best tree is computationally intractable (the problem is known to be NP-complete), so real algorithms grow the tree greedily, choosing the best question at each step without looking ahead. This means that the result is a good tree, never provably the best one, and it also means that the depth must be controlled to avoid memorizing noise.</p>
</section>

<section>
<h2>Data Prep</h2>
<p>Decision trees use the <b>same labeled sample and the same training and testing sets</b> as the Naive Bayes tab, which makes the two methods directly comparable. The details of the labels, the choice of inputs and the disjoint split are repeated below.</p>
{SPLIT_TEXT.replace("nb_02_train_sample.png", "dt_02_train_sample.png").replace("nb_03_test_sample.png", "dt_03_test_sample.png")}
<p>Unlike Naive Bayes, trees need no scaling or binning. A question such as "temperature at most 28.95" depends only on the order of the values, so negative temperatures and very different units cause no problem. The raw numeric columns were used as they are. Two input sets were tested: the seven weather columns, and the same seven plus latitude and longitude. The depth of the tuned trees was chosen by <b>5-fold cross-validation inside the training set</b> (the training days are divided into five parts, each part takes a turn as a pretend test set), so the real testing set was never used to make any choice.</p>
{DATA_LINKS}
<ul>
<li><a href="{CLEANLINK}dt_train.csv">dt_train.csv</a> and <a href="{CLEANLINK}dt_test.csv">dt_test.csv</a>: the training and testing sets used by the trees (raw weather columns, latitude, longitude, label and <code>row_id</code>)</li>
</ul>
</section>

<section>
<h2>Code</h2>
<p>The analysis is written in <b>Python</b> with <code>pandas</code>, <code>numpy</code>, <code>scikit-learn</code> (<code>DecisionTreeClassifier</code>, <code>plot_tree</code>, <code>cross_val_score</code>, <code>train_test_split</code>), <code>matplotlib</code> and <code>seaborn</code>.</p>
<ul>
<li><a href="{CODE06}"><code>06_naive_bayes_trees.py</code></a> on GitHub: builds the labels and the split, grows every tree, selects depths by cross-validation and draws every figure on this tab</li>
<li><a href="{CLEANLINK}nb_dt_results.json">nb_dt_results.json</a>: every number quoted on this tab</li>
</ul>
</section>

<section>
<h2>Results</h2>
<p>All accuracies are measured on the testing set ({SP['test_rows']:,} days), and always answering Moderate would be correct on <b>{pc(BASE)}</b> of them. Three trees were built to show the effect of the splitting criterion and the inputs: Tree 1 (Gini, depth 3, weather), Tree 2 (entropy, depth 3, weather) and Tree 3 (Gini, depth 4, weather plus location). Two further trees use the depth that cross-validation preferred.</p>
{DT_TABLE}
<h3>Tree 1: Gini, depth 3, weather</h3>
{fig("dt_tree1_gini_depth3.png", "Tree 1: a Gini tree of depth 3",
     "Each box shows its question, its gini impurity, the number of training days that reached it, the count of Good, Moderate and Unhealthy days (value), and its majority group. Orange boxes lean Good, green boxes lean Moderate and purple boxes lean Unhealthy, and darker shades mean purer nodes.")}
<p>The first question is the month: of the {SEP['counts'][2]:,} Unhealthy days in the training set, {SEL['counts'][2]:,} fall in January to September and only {SER['counts'][2]} in October to December. For the warm months, the tree asks whether the maximum temperature exceeded 28.95 C and then whether the wind speed was at most 11.45 km/h. The only leaf that predicts Unhealthy is the hot, calm one (334 training days, of which 190 were Unhealthy, 131 Moderate and 13 Good). In the October to December branch, cold days lean Good: calm days with a maximum temperature of 4.25 C or less, and windy days with a minimum temperature of 10.65 C or less. On the testing set the tree reaches {pc(T1['accuracy'])} accuracy and finds {pc(T1['recall']['Unhealthy'], 0)} of Unhealthy days, but when it does predict Unhealthy it is right {pc(T1['precision']['Unhealthy'], 0)} of the time.</p>
<h3>Tree 2: entropy, depth 3, weather</h3>
{fig("dt_tree2_entropy_depth3.png", "Tree 2: an entropy tree of depth 3",
     "The same inputs and depth as Tree 1 but with entropy as the splitting measure. The tree starts from a different question (solar radiation) and ends with only one leaf that does not predict Moderate.")}
<p>With entropy the root question is solar radiation at most 19.29, not the month, so the same data and depth produce a different tree. The only leaf that predicts Good collects dim days from October to December with strong winds (1,937 training days, 1,190 of them Good). No leaf predicts Unhealthy, so the tree finds none of the Unhealthy days on the testing set. Its accuracy is {pc(T2['accuracy'])}, close to Tree 1 ({pc(T1['accuracy'])}), which shows that the two criteria can differ in structure while performing about the same.</p>
<h3>Tree 3: Gini, depth 4, weather plus location</h3>
{fig("dt_tree3_gini_depth4_location.png", "Tree 3: a Gini tree of depth 4 that may also use latitude and longitude",
     "Latitude and longitude are available as inputs, and eight of its fifteen questions use them. A leaf with a gini of 0.0 contains days of a single group.")}
<p>Allowed to use location, the tree asks about longitude and latitude in eight of its fifteen questions, which splits the country into regions before weather conditions are considered. One branch (calm days from October to December with longitude at most -136.29, which matches only the two far-western cities in the study, Honolulu and Anchorage) ends in a leaf of 85 days that were all Good. Accuracy rises to {pc(T3['accuracy'])}, but the tree still never predicts Unhealthy on the testing set.</p>
<h3>Choosing the depth, and the tuned trees</h3>
{fig("dt_04_depth_sweep.png", "Training accuracy keeps rising with depth but cross-validated accuracy does not",
     f"The dashed lines show accuracy on the training days, which climb past 85% as the trees memorize them, and the solid lines show cross-validated accuracy, which peaks and then falls. The dots mark the depth chosen for each input set (weather: depth {NR['best_depth_cv']['gini|weather']} for Gini; weather plus location: depth {NR['best_depth_cv']['gini|weather+location']}).")}
<p>Deeper trees fit the training days better and better, but the cross-validated accuracy peaks early and then declines, which is the signature of <b>overfitting</b>. The tuned weather-only tree (Gini, depth {TW['depth']}, {TW['leaves']} leaves) reaches {pc(TW['accuracy'])} accuracy and macro-F1 {TW['macro_f1']:.2f}, and finds {pc(TW['recall']['Unhealthy'], 0)} of the Unhealthy days with {pc(TW['precision']['Unhealthy'], 0)} precision. With location added, the tuned tree (depth {TL['depth']}, {TL['leaves']} leaves) reaches {pc(TL['accuracy'])} accuracy and macro-F1 {TL['macro_f1']:.2f} and finds {pc(TL['recall']['Unhealthy'], 0)} of the Unhealthy days.</p>
{fig("dt_05_confusion_matrices.png", "Confusion matrices of three trees and the tuned weather tree",
     f"The three small trees answer Moderate for {MOD_LO}% to {MOD_HI}% of all days, which is why their Unhealthy row has few or no correct answers. The tuned tree (far right) spreads its answers across all groups and finds {TW['confusion'][2][2]} of the {sum(TW['confusion'][2])} Unhealthy days.")}
{fig("dt_06_importance.png", "Which inputs the tuned trees rely on",
     f"Importance is the share of the tree's total impurity reduction that comes from questions about each input. In the weather-only tree, the month ({pc(IMPW['month'], 0)}) and the three temperature columns together ({pc(TEMP_SUM, 0)}) dominate, and precipitation is almost unused ({pc(IMPW['precip_mm'], 0)}).")}
<h3>A harder test: learn on January to September, test on October to December</h3>
<p>Because daily weather and air quality are strongly related from one day to the next, a random split can be optimistic. In a time-based test, the trees were grown on January to September ({THR['train']:,} days) and graded on October to December ({THR['test']:,} days), where always answering Moderate is correct on {pc(DTT['baseline_accuracy'])} of days. Tree 1 simply answers Moderate every time ({pc(DTT['accuracy'])} accuracy, the same as the baseline), and the tuned weather tree reaches {pc(DTTT['accuracy'])} accuracy and macro-F1 {DTTT['macro_f1']:.2f}, but finds only {pc(DTTT['recall']['Unhealthy'], 0)} of the few Unhealthy days. A tree trained on warm months has little to learn about the cool-season days it is asked to judge, so forecasting into a new season is much harder than the random split suggests.</p>
</section>

<section>
<h2>Conclusions</h2>
<p><b>The month and the temperature are the strongest signals in the weather.</b> They account for about {pc(IMPW['month'], 0)} and {pc(TEMP_SUM, 0)} of the tuned weather tree's decisions, followed by wind speed ({pc(IMPW['wind_max'], 0)}). Almost all Unhealthy days ({SEL['counts'][2]:,} of {SEP['counts'][2]:,} in the training set) fall between January and September, and the tree's one Unhealthy rule is a hot, calm day. Precipitation barely matters, consistent with the earlier finding that rainy and dry days had nearly the same fine-particle levels.</p>
<p><b>Readable trees are not good forecasters here.</b> The three small trees predict Moderate for most days and find few or none of the Unhealthy days, and even the cross-validated tree reaches {pc(TW['accuracy'])} accuracy against a {pc(BASE)} baseline, a gain of about {(TW['accuracy'] - BASE) * 100:.0f} percentage points. Location matters as much as weather: adding latitude and longitude lifts accuracy to {pc(TL['accuracy'])} and macro-F1 to {TL['macro_f1']:.2f}, so where a day happens carries information that the weather alone does not.</p>
<p><b>Comparison with Naive Bayes.</b> On the same testing set, Naive Bayes (binned) is less accurate ({pc(NBM['accuracy'])}) but finds {pc(NBM['recall']['Unhealthy'], 0)} of the Unhealthy days, whereas the tuned tree is more accurate ({pc(TW['accuracy'])}) but finds only {pc(TW['recall']['Unhealthy'], 0)}. Naive Bayes behaves like a cautious alarm that is often wrong, and the tree behaves like a conservative forecaster that rarely warns. Neither is good enough to be a stand-alone warning system, and the later methods in this project will test whether ensembles of trees can do better.</p>
<p><b>Limits.</b> The AQI is a modeled value, one year of data was used, the testing set shares the weather patterns of the training set, and the greedy tree-building method gives a good tree but not the only possible one. Rare events such as wildfire smoke cannot be predicted from local weather at all.</p>
</section>
"""
page("dectrees.html", "DecTrees", dectrees)

# ============================================================================ REGRESSION AND ADABOOST TABS (Module 4)
RA = json.loads((ROOT / "data" / "clean" / "reg_ada_results.json").read_text(encoding="utf-8"))
CODE07 = f"{GH}/blob/main/code/07_regression_adaboost.py"


def pick(d, prefix):
    return d[[k for k in d if k.startswith(prefix)][0]]


LIN = RA["linear"]
LMAIN = LIN[RA["linear_main"]]
LWEA = LIN["Weather only (5 inputs)"]
LLOC = LIN["Weather, season and location (10 inputs)"]
LCO, LST, LCI, LSD = RA["linear_coefficients"], RA["linear_std_coefficients"], RA["linear_std_coef_ci"], RA["feature_sd"]
WIND_CI = [LCI["wind_max"][0] / LSD["wind_max"], LCI["wind_max"][1] / LSD["wind_max"]]
LTIME = RA["linear_time_holdout"]
UNH = RA["unhealthy"]
LG = RA["logistic"]
LG05, LGBAL, LGTUN = pick(LG, "Logistic, default"), pick(LG, "Logistic, balanced"), pick(LG, "Logistic, cut-off")
NBB = RA["nb_binary"]
NB05, NBTUN = pick(NBB, "Naive Bayes, default"), pick(NBB, "Naive Bayes, cut-off")
ORU, ORS, ORCI = RA["logistic_odds_ratio_per_unit"], RA["logistic_odds_ratio_per_sd"], RA["logistic_or_per_sd_ci"]
LOGCOEF, LOGSTEP = RA["logistic_coef_raw"], RA["logistic_step"]
THR_L, THR_N = RA["logistic_threshold"], RA["nb_threshold"]
VAUC = RA["logistic_variants_auc"]
LTIME_C = RA["logistic_time_holdout"]
ODDS_START = 0.10
ODDS_AFTER = ODDS_START / (1 - ODDS_START) * ORS["wind_max"]
P_AFTER = ODDS_AFTER / (1 + ODDS_AFTER)


def lin_row(name, r):
    return f"<tr><td>{name}</td><td>{r['rmse']:.2f}</td><td>{r['mae']:.2f}</td><td>{r['r2']:.3f}</td><td>{r['cv_r2_train']:.3f}</td></tr>"


LIN_TABLE = ("<table><tr><th>Inputs</th><th>RMSE (ug/m3)</th><th>MAE (ug/m3)</th><th>R-squared (testing set)</th><th>R-squared (5-fold, training set)</th></tr>"
             f"<tr><td><i>Always predict the training average ({RA['pm25']['train_mean']:.1f})</i></td><td>{LMAIN['baseline_rmse']:.2f}</td><td>{LMAIN['baseline_mae']:.2f}</td><td>0.000</td><td>-</td></tr>"
             + lin_row("Weather only (5 inputs)", LWEA) + lin_row("Weather and season (8 inputs), the main model", LMAIN)
             + lin_row("Weather, season and location (10 inputs)", LLOC) + "</table>")


def coef_rows():
    names = {"temp_mean": ("Mean temperature", "per 1 C"), "temp_range": ("Daily temperature range", "per 1 C"),
             "precip_mm": ("Precipitation", "per 1 mm"), "wind_max": ("Maximum wind speed", "per 1 km/h"),
             "solar_rad": ("Solar radiation", "per 1 MJ/m2"), "season_Winter": ("Winter instead of Fall", "per switch"),
             "season_Spring": ("Spring instead of Fall", "per switch"), "season_Summer": ("Summer instead of Fall", "per switch")}
    out = []
    for f, (nm, unit) in names.items():
        lo, hi = LCI[f][0] / LSD[f], LCI[f][1] / LSD[f]
        out.append(f"<tr><td>{nm}</td><td>{LCO[f]:+.3f} ug/m3 {unit}</td><td>{lo:+.3f} to {hi:+.3f}</td></tr>")
    return "".join(out)


LIN_COEF_TABLE = "<table><tr><th>Input</th><th>Coefficient</th><th>95% bootstrap interval</th></tr>" + coef_rows() + "</table>"


def bin_row(name, r):
    return (f"<tr><td>{name}</td><td>{pc(r['accuracy'])}</td><td>{pc(r['recall'], 1)}</td><td>{pc(r['precision'], 1)}</td>"
            f"<td>{r['f1']:.3f}</td><td>{r['auc']:.3f}</td></tr>")


CLS_TABLE = ("<table><tr><th>Method and cut-off</th><th>Accuracy</th><th>Recall (unhealthy days found)</th><th>Precision (alerts that were right)</th><th>F1</th><th>AUC</th></tr>"
             f"<tr><td><i>Always answer 'not unhealthy' (baseline)</i></td><td>{pc(UNH['baseline_accuracy'])}</td><td>0.0%</td><td>-</td><td>0.000</td><td>0.500</td></tr>"
             + bin_row("Logistic regression, cut-off 0.5", LG05) + bin_row("Logistic regression, balanced class weights", LGBAL)
             + bin_row(f"Logistic regression, cut-off {THR_L:.3f} (chosen by cross-validation)", LGTUN)
             + bin_row("Naive Bayes (Part 3 method), cut-off 0.5", NB05)
             + bin_row(f"Naive Bayes, cut-off {THR_N:.3f} (chosen by cross-validation)", NBTUN) + "</table>")

REG_DATA_LINKS = f"""<ul>
<li><a href="{CLEANLINK}reg_dataset.csv">reg_dataset.csv</a>: the full sample ({NR['n_rows']:,} city-days, inputs and both targets)</li>
<li><a href="{CLEANLINK}reg_train.csv">reg_train.csv</a> and <a href="{CLEANLINK}reg_test.csv">reg_test.csv</a>: the training and testing sets</li>
<li><a href="{CLEANLINK}daily_city_air_weather_clean.csv">daily_city_air_weather_clean.csv</a>: the cleaned daily table the sample comes from</li>
<li>Raw data: <a href="{RAWLINK}openmeteo_weather_daily_raw.csv">daily weather</a>, <a href="{RAWLINK}openmeteo_air_quality_hourly_raw.csv">hourly air quality</a> and <a href="{RAWLINK}cities_reference.csv">city locations</a></li>
</ul>"""

regression = f"""
<h1>Regression</h1>
<p class="sub">How much does the weather change PM2.5, and which days turn unhealthy?</p>
<p>This tab applies two regression methods to the same city-days, and the same training and testing split, as the Part 3 tabs. <b>Linear regression</b> predicts a number (the daily PM2.5 level) and <b>logistic regression</b> predicts a yes/no answer (is the day Unhealthy?). The logistic model is compared with the Naive Bayes model from Part 3. The write-up is organized into Overview, Data Prep, Code, Results and Conclusions.</p>

<section>
<h2>Overview</h2>
<h3>Linear regression: predicting a number</h3>
<p><b>Linear regression</b> predicts a numeric target as a weighted sum of the inputs: prediction = b0 + b1 &times; x1 + b2 &times; x2 + ... With one input this is a straight line, and with several inputs it is a flat surface. The numbers b1, b2, ... are the <b>coefficients</b>, and each says how much the prediction changes when its input increases by one unit while the others stay fixed. The coefficients are found by <b>least squares</b>: of all possible lines, the method keeps the one that makes the sum of squared <b>residuals</b> (actual value minus predicted value) as small as possible. Three numbers summarize how well it works on data it has not seen: the <b>RMSE</b> (typical size of the error in the units of the target, with large misses weighing heavily), the <b>MAE</b> (the average size of the error), and <b>R-squared</b> (the share of the variation in the target that the model explains, where 0 means no better than always predicting the average and 1 means perfect).</p>
{fig("reg_00a_linear_idea.png", "Linear regression with a single input",
     f"Each dot is a day, the red line is the fitted line, and each orange segment is a residual (the gap between the actual and the predicted PM2.5). With solar radiation alone the line rises only slightly (R-squared {RA['one_input_linear']['r2_train']:.2f} on the training days), which previews how much of the day-to-day change one weather variable can explain.", True)}
<h3>Logistic regression: predicting a class through a probability</h3>
<p>When the target is a category, such as Unhealthy or not, a straight line is a poor choice because it can predict values below 0 or above 1, which are not probabilities. <b>Logistic regression</b> keeps the linear idea but adds a step. It first computes the same kind of weighted sum, called the <b>linear score</b> z = b0 + b1 &times; x1 + b2 &times; x2 + ..., which can be any number from very negative to very positive. It then passes z through the <b>sigmoid</b> function, p = 1 / (1 + e<sup>-z</sup>), which squeezes every score into the range 0 to 1: a score of 0 gives p = 0.5, a large positive score gives p close to 1, and a large negative score gives p close to 0. The result p is read as the probability of the Unhealthy class. To turn the probability into a <b>class</b>, a <b>cut-off</b> is applied, usually 0.5: if p is at least the cut-off the day is called Unhealthy, otherwise not.</p>
{fig("reg_00b_sigmoid.png", "From a linear score to a probability",
     "The left panel shows the straight-line score of a one-input model that uses the maximum daily temperature, and the right panel shows the sigmoid that turns it into a probability. The blue dots are the observed share of unhealthy days in each temperature band, and they follow the red curve closely.")}
{fig("reg_00c_logistic_pipeline.png", "The logistic regression pipeline", "Weather inputs become a linear score, the sigmoid turns the score into a probability, and a cut-off rule turns the probability into a class.")}
<p>The coefficients of a logistic regression act on the <b>odds</b>, which are p / (1 - p), the ratio of the chance that the day is Unhealthy to the chance that it is not. Increasing an input by one unit multiplies the odds by e<sup>b</sup>, where b is its coefficient, so a coefficient of 0 means no effect, a positive coefficient raises the odds, and a negative coefficient lowers them.</p>
<h3>How the two methods differ</h3>
<table>
<tr><th></th><th>Linear regression</th><th>Logistic regression</th></tr>
<tr><td>Predicts</td><td>A number of any size (here, PM2.5)</td><td>The probability of a class, then the class (here, Unhealthy or not)</td></tr>
<tr><td>Output range</td><td>Unbounded</td><td>Always between 0 and 1</td></tr>
<tr><td>Fitted by</td><td>Minimizing squared errors (least squares)</td><td>Maximizing the likelihood of the observed classes</td></tr>
<tr><td>A coefficient means</td><td>An <i>additive</i> change in the prediction per unit</td><td>A <i>multiplicative</i> change in the odds per unit</td></tr>
<tr><td>Judged with</td><td>RMSE, MAE, R-squared, predicted versus actual plot</td><td>Confusion matrix, accuracy, recall, precision, AUC</td></tr>
</table>
<h3>What is done with them here</h3>
<p>Linear regression is asked how well the weather and the season predict the daily PM2.5 level, and what a change in wind or season is worth in micrograms per cubic meter. Logistic regression is asked whether a day will be Unhealthy (an AQI of 101 or more) and how the odds of that change with the conditions. Its results are then compared with the Naive Bayes model of Part 3 on the identical two-class question.</p>
</section>

<section>
<h2>Data Prep</h2>
<p>Supervised modeling needs <b>labeled data</b>, which means that every row carries the correct answer. All {NR['n_rows']:,} city-days have one, because both targets are computed from the cleaned air quality measurements. The rows were split into a <b>training set</b> ({RA['split']['train_rows']:,} rows), used to fit the models, and a <b>testing set</b> ({RA['split']['test_rows']:,} rows), used only once to grade them. The split is <b>the same as in Part 3</b>, which makes the results comparable. The two sets are <b>disjoint</b>: each row has an identifier, and the code verified that the sets share <b>{RA['split']['overlap_rows']} rows</b>. They must be disjoint because a model graded on rows it has already seen is graded on memory, and the accuracy would look better than it really is. The split was stratified in Part 3, so the share of Unhealthy days is {pc(UNH['train_share'])} in the training set and {pc(UNH['test_share'])} in the testing set.</p>
<h3>Which columns were used</h3>
<ul>
<li><b>Linear regression needs a numeric target:</b> <code>pm2_5</code>, the daily mean PM2.5 in micrograms per cubic meter (average {RA['pm25']['train_mean']:.1f}, standard deviation {RA['pm25']['train_std']:.1f} in the training set).</li>
<li><b>Logistic regression needs a two-class label:</b> <code>unhealthy</code>, equal to 1 when the daily maximum AQI is 101 or more and 0 otherwise. This is {pc(UNH['train_share'])} of training days, so the classes are very unbalanced.</li>
<li><b>Inputs for both:</b> mean temperature, the daily temperature range (maximum minus minimum), precipitation, maximum wind speed, solar radiation, and the season as three 0/1 columns for Winter, Spring and Summer (Fall is the reference, because it is the cleanest season).</li>
<li><b>Not used:</b> any pollutant or AQI column, because the targets are computed from them. The three temperature columns were replaced by the mean and the range because the mean, maximum and minimum are nearly copies of each other (correlations of {RA['corr_temps']['mean_max']:.2f}, {RA['corr_temps']['mean_min']:.2f} and {RA['corr_temps']['max_min']:.2f}), and such overlapping inputs make coefficients unstable and hard to interpret.</li>
<li><b>Scaling:</b> for logistic regression the inputs were standardized (average 0, standard deviation 1, learned from the training set only), which helps the fitting procedure; the coefficients were converted back to original units for interpretation.</li>
</ul>
{fig("reg_01_data_sample.png", "A sample of the regression data",
     "Each row is a city and a day, with the weather inputs followed by the two targets (orange): the numeric pm2_5 for linear regression and the 0/1 label unhealthy for logistic regression.")}
<div class="figrow">
{fig("reg_02_train_sample.png", "Training set", f"The first rows of the {RA['split']['train_rows']:,}-day training set, used to fit the models.", True)}
{fig("reg_03_test_sample.png", "Testing set", f"The first rows of the {RA['split']['test_rows']:,}-day testing set, used only to grade the models.", True)}
</div>
{REG_DATA_LINKS}
</section>

<section>
<h2>Code</h2>
<p>The analysis is written in <b>Python</b> with <code>pandas</code>, <code>numpy</code>, <code>scikit-learn</code> (<code>LinearRegression</code>, <code>LogisticRegression</code>, <code>StandardScaler</code>, <code>GridSearchCV</code>, <code>cross_val_predict</code>), <code>scipy</code>, <code>matplotlib</code> and <code>seaborn</code>. The logistic regression uses the default L2 regularization, and its strength (C = {RA['logistic_C']:g}) was chosen by 5-fold cross-validation on the training set only, as was the tuned cut-off. The testing set was used once, for the final models.</p>
<ul>
<li><a href="{CODE07}"><code>07_regression_adaboost.py</code></a> on GitHub: builds the targets, fits both regressions, compares them with Naive Bayes, and draws every figure on this tab (the same script also produces the AdaBoost tab)</li>
<li><a href="{CLEANLINK}reg_ada_results.json">reg_ada_results.json</a>: every number quoted on this tab</li>
</ul>
</section>

<section>
<h2>Results</h2>
<h3>Linear regression: predicting the PM2.5 level</h3>
{LIN_TABLE}
<p>On the testing set, the main model (weather and season) has an <b>RMSE of {LMAIN['rmse']:.2f}</b> and an <b>MAE of {LMAIN['mae']:.2f}</b> micrograms per cubic meter, compared with {LMAIN['baseline_rmse']:.2f} and {LMAIN['baseline_mae']:.2f} for simply guessing the average, and an <b>R-squared of {LMAIN['r2']:.3f}</b>. The weather and the season therefore explain only about {LMAIN['r2'] * 100:.0f}% of the day-to-day variation in PM2.5, and the typical error shrinks by only about {(1 - LMAIN['mae'] / LMAIN['baseline_mae']) * 100:.0f}%. The cross-validated R-squared on the training set ({LMAIN['cv_r2_train']:.3f}) is almost identical, so the result is stable and not a matter of luck in the split. Adding the season helps (R-squared {LWEA['r2']:.3f} for weather alone), and adding each city's location helps a little more ({LLOC['r2']:.3f}).</p>
{fig("reg_04_predicted_vs_actual.png", "Predicted versus actual PM2.5 on the testing set",
     "Each cell counts test days; a perfect model would put every day on the red dashed line. The predictions span only a narrow range (about 1 to 16), while the actual values are spread from 1 to over 40, and the orange line, which averages the actual values within bands of the prediction, rises with the prediction but stays flatter than the red line.")}
<h3>Two coefficients in plain words</h3>
{LIN_COEF_TABLE}
<ul>
<li><b>Wind speed ({LCO['wind_max']:+.3f} per km/h).</b> On windier days there is less fine particulate matter. For every extra kilometer per hour of maximum wind speed, the predicted PM2.5 is about {abs(LCO['wind_max']):.2f} micrograms per cubic meter lower, with the temperature, sun, rain and season held fixed (the 95% interval is {WIND_CI[0]:.2f} to {WIND_CI[1]:.2f}). A day that is {LSD['wind_max']:.0f} km/h windier than usual is predicted to be about {abs(LST['wind_max']):.1f} units cleaner. This matches the idea that wind mixes pollution upward and carries it away.</li>
<li><b>Summer ({LCO['season_Summer']:+.2f}).</b> A summer day has, on average, about {LCO['season_Summer']:.1f} micrograms per cubic meter more PM2.5 than a fall day with the same temperature, wind, sun and rain (95% interval {LCI['season_Summer'][0]:.1f} to {LCI['season_Summer'][1]:.1f}). Spring ({LCO['season_Spring']:+.1f}) and winter ({LCO['season_Winter']:+.1f}) are also higher than fall, which is consistently the cleanest season.</li>
</ul>
{fig("reg_05_coefficients.png", "What the linear regression learned",
     "Each bar is the change in the predicted PM2.5 when an input rises by one standard deviation, or when a season replaces fall, and the black whiskers are 95% bootstrap intervals. The season and the wind speed matter most, while precipitation and the temperature range are not distinguishable from zero.")}
<p>These coefficients describe associations in this data, and they are not proof that wind or summer <i>causes</i> a change. Because sunny, hot and calm weather occur together, the effect of one condition is shared with others, which is why the small temperature and solar radiation coefficients should not be read alone.</p>
<h3>Learning from January to September, testing on October to December</h3>
<p>In a harder, time-based test, the same linear model was fitted on {RA['time_holdout_rows']['train']:,} days from January to September and graded on {RA['time_holdout_rows']['test']:,} days from October to December. The RMSE was {LTIME['rmse']:.2f}, better than the {LTIME['baseline_rmse']:.2f} obtained by carrying over the January to September average, because the model knows that autumn is cleaner. Its R-squared of {LTIME['r2']:.3f}, however, shows that within autumn it explains nothing beyond the autumn average, so forecasting day-to-day changes into a new season is much harder than the random split suggests.</p>

<h3>Logistic regression: will the day be Unhealthy?</h3>
{CLS_TABLE}
{fig("reg_07_confusion_matrices.png", "Confusion matrices: logistic regression and Naive Bayes on the same two-class question",
     "Rows are the true answer and columns are the prediction, so the diagonal holds the correct answers. At the default cut-off the logistic regression says 'not unhealthy' almost every time, while a lower, cross-validated cut-off (second panel) finds many more unhealthy days at the cost of more false alarms.")}
<p><b>Accuracy at the default cut-off is misleading.</b> With a cut-off of 0.5, logistic regression is correct on <b>{pc(LG05['accuracy'])}</b> of testing days, but always answering 'not unhealthy' would be correct on {pc(UNH['baseline_accuracy'])}, so the model barely improves on guessing. Its confusion matrix shows why: it finds only {LG05['confusion'][1][1]} of the {UNH['test_positives']} unhealthy days ({pc(LG05['recall'], 0)}). Unhealthy days are rare ({pc(UNH['test_share'])}), so the predicted probability seldom rises above 0.5, even on risky days. This is a problem of the cut-off, not of the ranking: the <b>AUC of {LG05['auc']:.3f}</b> says that if one unhealthy day and one other day are picked at random, the unhealthy day receives the higher probability about {LG05['auc'] * 100:.0f}% of the time. A cut-off of {THR_L:.3f}, chosen by cross-validation on the training set to maximize the F1 score, finds {pc(LGTUN['recall'], 1)} of the unhealthy days ({LGTUN['confusion'][1][1]} of {UNH['test_positives']}), with an accuracy of {pc(LGTUN['accuracy'])} and a precision of {pc(LGTUN['precision'], 1)}, so about two of every three alerts are false.</p>
<h3>What a coefficient means for the odds</h3>
<p>The coefficient of the wind speed is {LOGCOEF['wind_max']:.3f} per km/h, and e raised to that power is <b>{ORU['wind_max']:.3f}</b>. In words: for each extra kilometer per hour of maximum wind speed, the <b>odds</b> of an unhealthy day are multiplied by {ORU['wind_max']:.2f}, which is {abs(1 - ORU['wind_max']) * 100:.0f}% lower, with the other inputs held fixed. For a wind speed {LOGSTEP['wind_max']:.0f} km/h higher (one standard deviation) the odds are multiplied by {ORS['wind_max']:.2f} (95% interval {ORCI['wind_max'][0]:.2f} to {ORCI['wind_max'][1]:.2f}). As an example, a day with a {ODDS_START * 100:.0f}% chance of being unhealthy has odds of {ODDS_START / (1 - ODDS_START):.3f}; after the wind increases by {LOGSTEP['wind_max']:.0f} km/h the odds become {ODDS_AFTER:.3f}, which is a chance of about {P_AFTER * 100:.1f}%. In the same way, a summer day has {ORU['season_Summer']:.1f} times the odds of an unhealthy day compared with a fall day with the same weather (95% interval {ORCI['season_Summer'][0]:.1f} to {ORCI['season_Summer'][1]:.1f}).</p>
{fig("reg_09_odds_ratios.png", "What the logistic regression learned",
     "Bars to the right of 1 raise the odds of an unhealthy day and bars to the left lower them, each for an increase of one standard deviation or for a season instead of fall. Summer, heat and sunshine raise the odds the most, and wind lowers them.")}
<h3>Comparison with Naive Bayes (Part 3)</h3>
<p>For a fair comparison, Naive Bayes was re-run on the same two-class label and the same split (the Part 3 results were for three groups, so those numbers are not directly comparable). The two methods <b>rank days equally well</b>: both have an AUC of {LG05['auc']:.3f} and their ROC curves lie on top of each other. They differ mainly in where their default cut-off falls. At 0.5, Naive Bayes is far more willing to raise an alert (it finds {pc(NB05['recall'], 0)} of unhealthy days with {pc(NB05['precision'], 0)} precision and {pc(NB05['accuracy'])} accuracy) than logistic regression ({pc(LG05['recall'], 0)} found, {pc(LG05['precision'], 0)} precision, {pc(LG05['accuracy'])} accuracy). When each method's cut-off is tuned the same way, they are practically tied: F1 of {LGTUN['f1']:.3f} for logistic regression and {NBTUN['f1']:.3f} for Naive Bayes.</p>
{fig("reg_08_roc.png", "ROC curves of logistic regression and Naive Bayes",
     "Each curve shows the share of unhealthy days found against the share of other days wrongly flagged as the cut-off moves, and a curve closer to the upper left corner is better. The two curves are almost identical, and both are far above the dashed line for guessing.", True)}
<p>The real differences are practical. Logistic regression uses the weather numbers directly, with no binning, and gives odds ratios that can be explained (as above), whereas Naive Bayes needs the numbers turned into counts and treats related inputs such as the three temperatures as separate evidence. Adding the season, and then the city location, changes the AUC of the logistic regression only slightly ({VAUC['Weather only (5 inputs)']:.3f} for weather alone, {VAUC['Weather and season (8 inputs)']:.3f} with the season and {VAUC['Weather, season and location (10 inputs)']:.3f} with the location), so for the yes/no question the weather and the season already carry nearly all the available information.</p>
<p>In the time-based test (October to December), only {LTIME_C['test_positives']} of {LTIME_C['test_rows']:,} days were unhealthy, so the AUC there ({LTIME_C['auc']:.3f} for logistic regression, {RA['nb_time_holdout_auc']:.3f} for Naive Bayes) rests on very few cases and should be treated as indicative only.</p>
</section>

<section>
<h2>Conclusions</h2>
<p><b>The weather explains the season and the wind well, but the level of PM2.5 only weakly.</b> Weather and season together explain about {LMAIN['r2'] * 100:.0f}% of the day-to-day variation in PM2.5, and the typical error ({LMAIN['mae']:.1f} micrograms per cubic meter) is only {(1 - LMAIN['mae'] / LMAIN['baseline_mae']) * 100:.0f}% smaller than the error of guessing the average. The clearest signals are the season (summer about {LCO['season_Summer']:.0f} units higher than fall) and the wind (about {abs(LCO['wind_max']):.1f} units lower for each extra kilometer per hour). A forecast of the actual level cannot rest on the weather alone.</p>
<p><b>Sorting days into unhealthy or not works better than predicting the level.</b> The ranking is good (AUC {LG05['auc']:.2f}): hot, sunny summer days with light winds carry several times the odds of an unhealthy day. Turning that ranking into an alert is where the cost appears. At the cut-off tuned for balance, about {pc(LGTUN['recall'], 0)} of unhealthy days are caught and roughly two of every three alerts are false, and a cut-off that catches more days produces even more false alarms. The cut-off is therefore a choice about how to weigh a missed warning against a false alarm, as the Introduction discussed.</p>
<p><b>Logistic regression and Naive Bayes are equally good, so the choice is about explanation.</b> Both rank days equally well, and logistic regression is easier to explain, since each coefficient is an odds ratio.</p>
<p><b>Limits.</b> The coefficients show association and not cause, the temperature, sun and calm weather overlap, the air quality values are modeled estimates, one year of data was used, and days close in time resemble each other. Distant events such as the June 2023 wildfire smoke cannot be seen in local weather at all.</p>
</section>
"""
page("regression.html", "Regression", regression)

# ---------------------------------------------------------------- ADABOOST PAGE
AG = RA["ada_grid"]
AC, AST = RA["ada_chosen"], RA["ada_best_stump"]
AD, ASTP, ADT = RA["ada"], RA["ada_stumps"], RA["dt_same_inputs"]
P3 = RA["dt_part3_tuned_weather"]
ADV = RA["ada_vs_dt"]
AIMP = RA["ada_importance"]
REG_IMP = sum(v for k, v in AIMP.items() if k.startswith("region_"))
ATH = RA["ada_time_holdout"]
TOY = RA["toy"]
ABASE = RA["ada_baseline_accuracy"]
GRID_TABLE = ("<table><tr><th>Base tree</th>" + "".join(f"<th>Learning rate {lr}</th>" for lr in [0.05, 0.1, 0.3, 1.0]) + "</tr>"
              + "".join("<tr><td>" + ("depth 1 (stumps)" if d == 1 else f"depth {d}") + "</td>" + "".join(
                  "<td>" + "".join(f"{g['cv_accuracy'] * 100:.1f}% at {g['best_rounds']} rounds" for g in AG if g["depth"] == d and g["learning_rate"] == lr) + "</td>"
                  for lr in [0.05, 0.1, 0.3, 1.0]) + "</tr>" for d in [1, 2, 3]) + "</table>")
TOY_TABLE = ("<table><tr><th>Round</th><th>Stump (a single question)</th><th>Weighted error</th><th>Weight alpha</th><th>Weight of a wrong day</th><th>Weight of a right day</th></tr>"
             + "".join(f"<tr><td>{r['round']}</td><td>{r['rule']}? If higher, Unhealthy; otherwise Good</td><td>{r['weighted_error']:.3f}</td><td>{r['alpha']:.2f}</td>"
                       f"<td>&times; {r['factor_wrong']:.2f}</td><td>&times; {r['factor_right']:.2f}</td></tr>" for r in TOY["rounds"]) + "</table>")


def mc_row(name, r, extra=""):
    return (f"<tr><td>{name}</td><td>{pc(r['accuracy'])}</td><td>{r['macro_f1']:.3f}</td><td>{pc(r['recall']['Good'], 0)}</td>"
            f"<td>{pc(r['recall']['Moderate'], 0)}</td><td>{pc(r['recall']['Unhealthy'], 0)}</td><td>{pc(r['precision']['Unhealthy'], 0)}</td></tr>")


P3ROW = (f"<tr><td>Decision tree from Part 3 (weather inputs, depth {P3['depth']})</td><td>{pc(P3['accuracy'])}</td><td>{P3['macro_f1']:.3f}</td>"
         f"<td>-</td><td>-</td><td>{pc(P3['recall_unhealthy'], 0)}</td><td>-</td></tr>")
COMP_TABLE = ("<table><tr><th>Method</th><th>Accuracy</th><th>Macro-F1</th><th>Recall: Good</th><th>Recall: Moderate</th><th>Recall: Unhealthy</th><th>Precision: Unhealthy</th></tr>"
              f"<tr><td><i>Always answer Moderate (baseline)</i></td><td>{pc(ABASE)}</td><td>0.253</td><td>0%</td><td>100%</td><td>0%</td><td>-</td></tr>"
              + P3ROW + mc_row(f"Decision tree, same 15 inputs (depth {ADT['depth']})", ADT)
              + mc_row(f"AdaBoost with stumps ({AST['rounds']} rounds)", ASTP)
              + mc_row(f"AdaBoost, chosen by cross-validation (depth {AC['base_depth']}, {AC['rounds']} rounds)", AD) + "</table>")
VOTE = TOY["vote_example"]
_sign = 1 if VOTE["true_class"] == "Unhealthy" else -1
VOTE_RIGHT = sum(abs(v) for v in VOTE["votes"] if v * _sign > 0)
VOTE_WRONG = sum(abs(v) for v in VOTE["votes"] if v * _sign < 0)
VOTE_OK = VOTE["total"] * _sign > 0
STUMP_ACC = TOY["stump_accuracies"]

ADA_DATA_LINKS = f"""<ul>
<li><a href="{CLEANLINK}ada_dataset.csv">ada_dataset.csv</a>: the full labeled sample with the text columns (season, region) before encoding</li>
<li><a href="{CLEANLINK}ada_train_onehot.csv">ada_train_onehot.csv</a> and <a href="{CLEANLINK}ada_test_onehot.csv">ada_test_onehot.csv</a>: the encoded training and testing sets used by AdaBoost</li>
<li><a href="{CLEANLINK}daily_city_air_weather_clean.csv">daily_city_air_weather_clean.csv</a>: the cleaned daily table the sample comes from</li>
<li>Raw data: <a href="{RAWLINK}openmeteo_weather_daily_raw.csv">daily weather</a>, <a href="{RAWLINK}openmeteo_air_quality_hourly_raw.csv">hourly air quality</a> and <a href="{RAWLINK}cities_reference.csv">city locations</a></li>
</ul>"""

adaboost = f"""
<h1>AdaBoost</h1>
<p class="sub">Can many weak decision trees, each fixing the last one's mistakes, beat a single tree?</p>
<p>This tab applies AdaBoost to the same labeled city-days, the same AQI groups (Good, Moderate, Unhealthy) and the same training and testing split as the Decision Trees tab of Part 3, and compares it with the decision tree. It is organized into Overview, Data Prep, Code, Results and Conclusions.</p>

<section>
<h2>Overview</h2>
<h3>Bagging and boosting</h3>
<p>One decision tree is easy to read but unstable: a small change in the data can change the tree a lot. <b>Ensemble</b> methods combine many trees to get a steadier answer, and the two main strategies differ in how the trees are built. In <b>bagging</b>, many trees are grown independently, each on a random resample of the training days, and they vote with equal weight, which mainly reduces the instability. In <b>boosting</b>, the trees are grown <b>one after another</b>, and every new tree concentrates on the days that the earlier trees got wrong. The final answer is a <b>weighted vote</b>, in which trees that earned more trust have a larger say. Boosting mainly reduces the systematic error of very simple trees.</p>
{fig("ada_00a_bagging_vs_boosting.png", "Bagging versus boosting",
     "In bagging (left) the trees never see each other's mistakes, and each gets one equal vote. In boosting (right) each tree is built after the last, and the days it got wrong are given more weight so the next tree must pay attention to them.")}
<h3>Decision stumps and the AdaBoost recipe</h3>
<p>The classic building block of AdaBoost is the <b>decision stump</b>: a tree with a single question and two leaves, for example "is the solar radiation at most 23?". A stump is a <b>weak learner</b>, only a little better than guessing. <b>AdaBoost</b> (adaptive boosting) turns many weak learners into a strong one with the following steps, written for two classes:</p>
<ol>
<li><b>Start with equal weights.</b> Each of the n training days gets the weight 1/n.</li>
<li><b>Fit a stump</b> that makes the smallest <i>weighted</i> error &epsilon; (the total weight of the days it classifies wrongly).</li>
<li><b>Give the stump its weight alpha</b>: alpha = &frac12; ln((1 - &epsilon;) / &epsilon;). A stump with a small error gets a large positive alpha, a stump that is as good as a coin flip (&epsilon; = 0.5) gets alpha = 0 and no say, and a stump worse than a coin flip gets a negative alpha. Alpha is therefore the <b>trust</b> given to that stump in the final vote.</li>
<li><b>Reweight the days.</b> The weight of every day that the stump got wrong is multiplied by e<sup>alpha</sup> (it becomes larger), the weight of every day it got right is multiplied by e<sup>-alpha</sup> (it becomes smaller), and all weights are rescaled to add up to 1. The next stump is therefore forced to concentrate on the hard days.</li>
<li><b>Repeat</b> for the chosen number of rounds.</li>
<li><b>Take a weighted vote.</b> Each stump votes +1 or -1 and is multiplied by its alpha. The class with the larger total vote wins.</li>
</ol>
<p>With more than two classes, scikit-learn uses the SAMME version, in which alpha = ln((1 - &epsilon;) / &epsilon;) + ln(K - 1) for K classes, and the vote is taken over all classes. Two settings control the process: the <b>number of rounds</b> (n_estimators) and the <b>learning rate</b>, which shrinks every alpha, so that a small learning rate needs more rounds but learns more carefully.</p>
<h3>A worked example with real days</h3>
<p>The example below uses {TOY['n_points']} real days (35 Good and 35 Unhealthy) described by two inputs, the solar radiation and the maximum temperature. In every round the weights of the days change, and the circled days are the ones that round's stump classified wrongly.</p>
{TOY_TABLE}
{fig("ada_00b_reweighting.png", "Three rounds of AdaBoost on 70 real days",
     f"Bigger dots carry more weight, and the shaded areas show what each stump predicts. In round 1, {TOY['rounds'][0]['n_wrong']} days are wrong, so their weights are multiplied by {TOY['rounds'][0]['factor_wrong']:.1f} and the right days' weights by {TOY['rounds'][0]['factor_right']:.2f}, which is why the wrongly classified days are larger in round 2. The final panel combines the three stumps with their alphas.")}
<p>The first stump is the most accurate on the original weights, so it receives the largest alpha ({TOY['rounds'][0]['alpha']:.2f}), and the stumps of the later rounds earn less trust because they work on the harder, reweighted days. Each stump alone is right on {STUMP_ACC[0] * 100:.0f}%, {STUMP_ACC[1] * 100:.0f}% and {STUMP_ACC[2] * 100:.0f}% of the 70 days, while their weighted vote is right on <b>{TOY['final_accuracy'] * 100:.0f}%</b>. The figure below shows how the vote is computed for one day that is really {VOTE['true_class']}: the stumps that vote for the right class carry a combined weight of {VOTE_RIGHT:.2f}, the stumps that vote for the wrong class carry {VOTE_WRONG:.2f}, and the total vote of {VOTE['total']:+.2f} gives the {'correct' if VOTE_OK else 'wrong'} answer.</p>
{fig("ada_00c_weighted_vote.png", "The weighted vote for one day", "Each bar is one stump's vote, which is its alpha with the sign of its prediction, and the last bar is their sum. The sign of the total decides the class: red for Unhealthy and green for Good.", True)}
<h3>What is done with it here</h3>
<p>AdaBoost is applied to the three-group AQI label, with small decision trees as the weak learners, and its number of rounds, its learning rate and the depth of its base trees are tuned by cross-validation. The result is compared with the single decision tree of Part 3 to see whether combining many weak trees gives a measurable gain.</p>
</section>

<section>
<h2>Data Prep</h2>
<p>AdaBoost is supervised, so every row needs a known label. The label is the <b>AQI group</b> of the day (Good, Moderate, or Unhealthy, meaning an AQI of 101 or more), as in Part 3, and all {NR['n_rows']:,} city-days have one. The rows were split into a <b>training set</b> ({RA['split']['train_rows']:,} rows) to fit the models and a <b>testing set</b> ({RA['split']['test_rows']:,} rows) to grade them once, exactly as in Part 3. The two sets are <b>disjoint</b>, and the code confirmed that they share <b>{RA['split']['overlap_rows']} rows</b>; this matters because a model graded on days it has already seen would be graded on memory and would look better than it is. The split was stratified, so the label proportions are the same in both sets ({pc(NR['label_share']['Good'], 0)} Good, {pc(NR['label_share']['Moderate'], 0)} Moderate and {pc(NR['label_share']['Unhealthy'], 0)} Unhealthy).</p>
{fig("ada_01_data_sample.png", "A sample of the AdaBoost data",
     "Each row is a day with its numeric weather, two text columns (season and region, orange) and the label (orange). Scikit-learn cannot use the text columns as they are, so they must be turned into numbers.")}
<h3>Turning text columns into numbers: one-hot encoding</h3>
<p>The scikit-learn version of AdaBoost needs numeric inputs. Seven columns are already numbers (mean, maximum and minimum temperature, precipitation, maximum wind speed, solar radiation and the month), but <b>season</b> and <b>region</b> are text. Replacing the words by 1, 2, 3 and 4 would invent an order and distances that do not exist, so each category was turned into its own 0/1 column instead, a method called <b>one-hot encoding</b>: a winter day gets a 1 in <code>season_Winter</code> and 0 in the other three season columns, and a day in the West gets a 1 in <code>region_West</code>. Season has four values and region has four (the US Census regions), so the two text columns became eight number columns and the inputs total {len(RA['ada_columns'])}. Trees need no scaling, so the numeric columns were kept in their original units. The region adds a coarse idea of where the city is, which the weather alone does not give.</p>
{fig("ada_02_onehot_step.png", "The one-hot step on six real days",
     "Each row of the left table (season and region as words) becomes the row on the right, where exactly one season column and exactly one region column hold a 1 (highlighted). Only the training set was used to decide which columns exist, and the testing set was encoded with the same columns.")}
<div class="figrow">
{fig("ada_03_train_sample.png", "Training set", f"The first rows of the {RA['split']['train_rows']:,}-day training set after encoding, used to fit the models.", True)}
{fig("ada_04_test_sample.png", "Testing set", f"The first rows of the {RA['split']['test_rows']:,}-day testing set after encoding, used only to grade the final models.", True)}
</div>
{ADA_DATA_LINKS}
</section>

<section>
<h2>Code</h2>
<p>The analysis is written in <b>Python</b> with <code>pandas</code>, <code>numpy</code>, <code>scikit-learn</code> (<code>AdaBoostClassifier</code> with <code>DecisionTreeClassifier</code> as the weak learner, <code>StratifiedKFold</code>, <code>staged_predict</code>), <code>joblib</code>, <code>scipy</code>, <code>matplotlib</code> and <code>seaborn</code>. The worked example above was computed with a hand-written AdaBoost loop (in the same script) so that the weights and alphas could be shown.</p>
<ul>
<li><a href="{CODE07}"><code>07_regression_adaboost.py</code></a> on GitHub: encodes the data, tunes AdaBoost by cross-validation, fits the final models, compares them with the decision tree and draws every figure on this tab</li>
<li><a href="{CLEANLINK}reg_ada_results.json">reg_ada_results.json</a>: every number quoted on this tab</li>
</ul>
</section>

<section>
<h2>Results</h2>
<h3>Tuning without touching the testing set</h3>
<p>All settings were chosen with <b>5-fold cross-validation inside the training set</b>: the training days were divided into five parts, each part took a turn as the validation set, and the validation accuracy was recorded after <i>every</i> boosting round. The testing set was not used for any choice. It was used once, for the final comparison. The search covered the depth of the base trees (1, 2 or 3), the learning rate (0.05, 0.1, 0.3 or 1.0) and up to 500 rounds.</p>
{GRID_TABLE}
{fig("ada_05_validation_curves.png", "How validation accuracy changes as boosting rounds are added",
     f"The left panel compares base trees of depth 1, 2 and 3, and the right panel compares learning rates for depth 3; each dot is the best round. Accuracy rises quickly during the first 30 rounds, then flattens, and the depth-3 trees clearly beat stumps, while a learning rate of 1.0 is noisy and worse.")}
<p>The best setting was <b>base trees of depth {AC['base_depth']}, a learning rate of {AC['learning_rate']}, and {AC['rounds']} rounds</b>, with a cross-validated accuracy of {pc(AC['cv_accuracy'], 2)} (the dotted line in the figure, {pc(ABASE)}, is the accuracy of always answering Moderate). Plain stumps reach only {pc(AST['cv_accuracy'], 2)} even with the best learning rate ({AST['learning_rate']}, {AST['rounds']} rounds), most likely because a single question cannot express a combination such as "hot and calm". Past about 150 rounds the curves are flat, so the extra rounds add almost nothing.</p>
{fig("ada_06_grid.png", "The grid of settings searched", "Each cell shows the best cross-validated accuracy and the round at which it was reached. Deeper base trees help much more than any change in the learning rate.", True)}
<h3>Final results on the testing set</h3>
<p>The chosen model was fitted once on the whole training set and graded on the testing set: <b>accuracy {pc(AD['accuracy'])}</b>, macro-F1 {AD['macro_f1']:.3f}, and it finds {pc(AD['recall']['Unhealthy'], 1)} of the Unhealthy days ({AD['confusion'][2][2]} of {sum(AD['confusion'][2])}), with a precision of {pc(AD['precision']['Unhealthy'], 0)} when it predicts Unhealthy.</p>
{fig("ada_07_confusion_matrices.png", "Confusion matrices on the testing set",
     "The diagonal holds the correct answers. The tuned AdaBoost (left) and the decision tree on the same inputs (center) have similar patterns, while AdaBoost with stumps (right) answers Moderate for almost every day.")}
<h3>AdaBoost versus the decision tree from Part 3</h3>
{COMP_TABLE}
{fig("ada_08_comparison.png", "AdaBoost compared with the decision trees",
     "From left to right in each panel: the Part 3 tuned tree, a decision tree refitted on this tab's 15 inputs, and the tuned AdaBoost. All three are within a fraction of a point on accuracy and macro-F1, and all are about four and a half points above always answering Moderate.")}
<p><b>Which did best, and by how much?</b> AdaBoost has the highest numbers, but by a margin that is too small to trust. Its accuracy of {pc(AD['accuracy'], 2)} is <b>{ADV['difference_points']:.2f} percentage points</b> above the decision tree on the same inputs ({pc(ADT['accuracy'], 2)}) and {(AD['accuracy'] - P3['accuracy']) * 100:.2f} points above the tuned tree of Part 3 ({pc(P3['accuracy'], 2)}). On the testing set, AdaBoost was right where the tree was wrong on {ADV['ada_only_correct']} days, and the tree was right where AdaBoost was wrong on {ADV['dt_only_correct']} days, which is a difference of only {ADV['ada_only_correct'] - ADV['dt_only_correct']} days out of {RA['split']['test_rows']:,}. A paired significance test (McNemar's exact test) gives p = {ADV['mcnemar_p']:.2f}, and the 95% bootstrap interval of the difference runs from {ADV['difference_ci95'][0]:+.1f} to {ADV['difference_ci95'][1]:+.1f} points, so the two methods are statistically <b>tied</b>. The macro-F1 ({AD['macro_f1']:.3f} against {ADT['macro_f1']:.3f}) and the share of Unhealthy days found ({pc(AD['recall']['Unhealthy'], 0)} against {pc(ADT['recall']['Unhealthy'], 0)}) tell the same story. Both are about {(AD['accuracy'] - ABASE) * 100:.1f} points above the {pc(ABASE)} of always answering Moderate.</p>
{fig("ada_09_importance.png", "Which inputs the boosted trees rely on",
     f"The month and the solar radiation carry about {(AIMP['month'] + AIMP['solar_rad']) * 100:.0f}% of the importance, followed by the maximum temperature and the wind. The four region columns together hold about {REG_IMP * 100:.0f}%, so location added little.", True)}
<h3>A harder test: learn on January to September, test on October to December</h3>
<p>When the models were fitted on {RA['time_holdout_rows']['train']:,} days from January to September and graded on {RA['time_holdout_rows']['test']:,} days from October to December, always answering the training period's most common group was right on {pc(ATH['baseline_accuracy'])} of days. AdaBoost reached {pc(ATH['ada']['accuracy'])} (macro-F1 {ATH['ada']['macro_f1']:.2f}) and the decision tree {pc(ATH['dt']['accuracy'])} (macro-F1 {ATH['dt']['macro_f1']:.2f}). AdaBoost is again ahead, but it finds {pc(ATH['ada']['recall']['Unhealthy'], 0)} of the few Unhealthy days of that period and the tree finds {pc(ATH['dt']['recall']['Unhealthy'], 0)}, because few such days occur in autumn and the models learned mostly from the warm months. Forecasting into a new season remains much harder than the random split suggests.</p>
</section>

<section>
<h2>Conclusions</h2>
<p><b>Boosting helped only slightly.</b> Combining {AC['rounds']} small trees raised accuracy to {pc(AD['accuracy'])}, about {(AD['accuracy'] - ABASE) * 100:.1f} points above guessing the most common group, but a single well-tuned decision tree reaches nearly the same level ({pc(ADT['accuracy'])}). Boosting reduces the errors that come from using very simple trees, yet it cannot create information that the inputs do not contain. The weather, the month and the region leave a large part of the variation in air quality unexplained, such as local traffic, industry and distant smoke.</p>
<p><b>Depth mattered more than the number of rounds.</b> Plain stumps stayed at {pc(AST['cv_accuracy'], 1)} in cross-validation, while trees of depth 3 reached {pc(AC['cv_accuracy'], 1)}, and extra rounds beyond about 150 changed little. The combinations of conditions that signal unhealthy air, such as heat together with strong sunshine and calm winds, are probably better captured by trees that can ask a few questions in a row.</p>
<p><b>The practical choice is the simpler tree.</b> Because AdaBoost and a decision tree are statistically tied, the tree is the better tool when the goal is to explain a warning to the public: it can be drawn and read, while a weighted vote of {AC['rounds']} trees cannot. AdaBoost is worth its extra complexity only if a small gain would matter.</p>
<p><b>Detection remains limited.</b> AdaBoost finds about {pc(AD['recall']['Unhealthy'], 0)} of the Unhealthy days, and it is right about {pc(AD['precision']['Unhealthy'], 0)} of the time when it says a day will be unhealthy. As in the earlier parts, the days that matter most for health are the ones the weather alone predicts least well.</p>
</section>
"""
page("adaboost.html", "AdaBoost", adaboost)

# ============================================================================ MODEL TABS (placeholders)
MODELS = [
    ("gradientboosting.html", "GradientBoosting", "a later part of the course",
     "Gradient boosting, which builds trees one after another so that each corrects the errors of the previous ones, to predict PM2.5 or the AQI category.",
     "daily_city_air_weather_clean.csv"),
    ("xgboost.html", "XGBoost", "a later part of the course",
     "XGBoost, an optimized and regularized version of gradient boosting, to predict air quality and compare it with AdaBoost and the other boosting methods.",
     "daily_city_air_weather_clean.csv"),
]

for f, label, module, plan, data in MODELS:
    body = f"""
<h1>{label}</h1>
<p class="sub">Analysis tab, to be completed in {module}</p>
<section>
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
<h1>Conclusions</h1>
<p class="sub">What the findings mean for everyday life</p>
<section>
<div class="soon"><b>Coming in the final project part.</b> This tab will hold at least five non-technical paragraphs with images that summarize what the project found about weather, air quality and lung health.</div>
</section>
"""
about = """
<h1>About Me</h1>
<p class="sub">The person behind the project</p>
<p class="lead"><b>Himanshu Jain</b></p>
<p>I am a Master's student in Data Science at the University of Colorado Boulder (Class of 2027), with data science internships at Summer Atlantic Capital, Ernst &amp; Young, and LG Electronics. I am skilled in Python, SQL, and Tableau/Power BI for large-scale analysis, statistical modeling, and KPI tracking.</p>
<p>I have experience translating complex analyses into clear business recommendations through dashboards, reports, and presentations. I am equally comfortable designing data pipelines, validating findings with rigorous experiments, and shipping models to production as containerized services on AWS.</p>
<h2>Education</h2>
<div class="cards">
<div class="card"><b>University of Colorado Boulder</b><span>Master of Science in Data Science</span>
<small>Aug 2025 &ndash; May 2027 &middot; Boulder, CO</small>
<p class="tags"><em>Statistical Inference</em><em>Data Mining</em><em>Big Data Architecture</em></p></div>
<div class="card"><b>Manipal Institute of Technology</b><span>Bachelor of Science in Electronics and Communication</span>
<small>Aug 2021 &ndash; May 2025 &middot; India</small></div>
</div>
"""

home = f"""
<h1>How Weather Shapes the Air People Breathe, and What It Means for Lung Health</h1>
<p class="sub">Air quality, weather and respiratory health across 55 US cities, 2023</p>
<p class="lead">On June 7, 2023, smoke from Canadian wildfires pushed New York City's daily fine-particle level to more than four times the World Health Organization guideline, while Denver and Phoenix barely changed. That contrast frames this project: how much of the air people breathe is set by weather, season and distant events, and how does that air relate to asthma and COPD? The project draws on three data sources covering hourly air quality and daily weather for 55 cities in 2023 and county-level health statistics for 2,956 US counties.</p>
<div class="stats">
<div><b>55</b><span>US cities analyzed</span></div>
<div><b>481,800</b><span>hourly air quality readings</span></div>
<div><b>2,956</b><span>counties with health data</span></div>
<div><b>3</b><span>data sources</span></div>
</div>
{fig("eda_08_wildfire_episode.png", "One smoke event, five cities",
     "Daily PM2.5 during the Canadian wildfire smoke episode of 2023. New York and Boston spiked in early June and Chicago in late June, while Denver and Phoenix stayed near normal.")}
<h2>What this project covers</h2>
<ul class="cover">
<li>Data preparation and exploratory analysis: <b>complete</b></li>
<li>Clustering and PCA: <b>complete</b></li>
<li>Naive Bayes and decision trees: <b>complete</b></li>
<li>Regression and AdaBoost: <b>complete</b></li>
<li>GradientBoosting and XGBoost: to come</li>
</ul>
<h2>Where to start</h2>
<div class="start">
<a href="introduction.html"><b>Introduction</b><span>Why air, weather and lung health belong together, plus ten guiding questions</span></a>
<a href="dataprep_eda.html"><b>DataPrep_EDA</b><span>Data sources, APIs, cleaning steps and 16 visualizations</span></a>
<a href="conclusions.html"><b>Conclusions</b><span>What it all means (coming at the end of the course)</span></a>
</div>
"""

(ROOT / "style.css").write_text(CSS, encoding="utf-8")
page("index.html", "Home", home)
page("introduction.html", "Introduction", intro)
page("dataprep_eda.html", "DataPrep_EDA", dataprep)
page("conclusions.html", "Conclusions", concl)
page("about.html", "About Me", about)
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("site built")
