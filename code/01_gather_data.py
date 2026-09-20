"""Gather raw data for the Air Quality, Weather and Respiratory Health project.

Sources
1. Open-Meteo Air Quality API  (hourly pollutants + US AQI)   - API, no key required
2. Open-Meteo Historical Weather API (daily weather)          - API, no key required
3. CDC PLACES county data via the Socrata API (health)        - open data download

Run:  python code/01_gather_data.py
Output: data/raw/*.csv
"""
import time
from pathlib import Path

import pandas as pd
import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

START, END = "2023-01-01", "2023-12-31"

AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WX_URL = "https://archive-api.open-meteo.com/v1/archive"
PLACES_URL = "https://data.cdc.gov/resource/swc5-untb.json"

AQ_VARS = ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide",
           "sulphur_dioxide", "ozone", "us_aqi"]
WX_VARS = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
           "precipitation_sum", "wind_speed_10m_max", "shortwave_radiation_sum"]

# city, state, county name (as used by CDC PLACES), latitude, longitude
CITIES = [
    ("New York", "NY", "New York", 40.71, -74.01),
    ("Los Angeles", "CA", "Los Angeles", 34.05, -118.24),
    ("Chicago", "IL", "Cook", 41.88, -87.63),
    ("Houston", "TX", "Harris", 29.76, -95.37),
    ("Phoenix", "AZ", "Maricopa", 33.45, -112.07),
    ("Philadelphia", "PA", "Philadelphia", 39.95, -75.17),
    ("San Antonio", "TX", "Bexar", 29.42, -98.49),
    ("San Diego", "CA", "San Diego", 32.72, -117.16),
    ("Dallas", "TX", "Dallas", 32.78, -96.80),
    ("San Jose", "CA", "Santa Clara", 37.34, -121.89),
    ("Austin", "TX", "Travis", 30.27, -97.74),
    ("Jacksonville", "FL", "Duval", 30.33, -81.66),
    ("Columbus", "OH", "Franklin", 39.96, -83.00),
    ("Charlotte", "NC", "Mecklenburg", 35.23, -80.84),
    ("Indianapolis", "IN", "Marion", 39.77, -86.16),
    ("San Francisco", "CA", "San Francisco", 37.77, -122.42),
    ("Seattle", "WA", "King", 47.61, -122.33),
    ("Denver", "CO", "Denver", 39.74, -104.99),
    ("Washington", "DC", "District of Columbia", 38.91, -77.04),
    ("Boston", "MA", "Suffolk", 42.36, -71.06),
    ("El Paso", "TX", "El Paso", 31.76, -106.49),
    ("Nashville", "TN", "Davidson", 36.16, -86.78),
    ("Detroit", "MI", "Wayne", 42.33, -83.05),
    ("Oklahoma City", "OK", "Oklahoma", 35.47, -97.52),
    ("Portland", "OR", "Multnomah", 45.52, -122.68),
    ("Las Vegas", "NV", "Clark", 36.17, -115.14),
    ("Memphis", "TN", "Shelby", 35.15, -90.05),
    ("Louisville", "KY", "Jefferson", 38.25, -85.76),
    ("Baltimore", "MD", "Baltimore City", 39.29, -76.61),
    ("Milwaukee", "WI", "Milwaukee", 43.04, -87.91),
    ("Albuquerque", "NM", "Bernalillo", 35.08, -106.65),
    ("Tucson", "AZ", "Pima", 32.22, -110.97),
    ("Fresno", "CA", "Fresno", 36.74, -119.79),
    ("Sacramento", "CA", "Sacramento", 38.58, -121.49),
    ("Kansas City", "MO", "Jackson", 39.10, -94.58),
    ("Atlanta", "GA", "Fulton", 33.75, -84.39),
    ("Omaha", "NE", "Douglas", 41.26, -95.94),
    ("Colorado Springs", "CO", "El Paso", 38.83, -104.82),
    ("Raleigh", "NC", "Wake", 35.78, -78.64),
    ("Miami", "FL", "Miami-Dade", 25.76, -80.19),
    ("Minneapolis", "MN", "Hennepin", 44.98, -93.27),
    ("Tampa", "FL", "Hillsborough", 27.95, -82.46),
    ("New Orleans", "LA", "Orleans", 29.95, -90.07),
    ("Cleveland", "OH", "Cuyahoga", 41.50, -81.69),
    ("Pittsburgh", "PA", "Allegheny", 40.44, -79.99),
    ("Salt Lake City", "UT", "Salt Lake", 40.76, -111.89),
    ("Cincinnati", "OH", "Hamilton", 39.10, -84.51),
    ("St. Louis", "MO", "St. Louis City", 38.63, -90.20),
    ("Riverside", "CA", "Riverside", 33.95, -117.40),
    ("Bakersfield", "CA", "Kern", 35.37, -119.02),
    ("Boise", "ID", "Ada", 43.62, -116.20),
    ("Boulder", "CO", "Boulder", 40.01, -105.27),
    ("Honolulu", "HI", "Honolulu", 21.31, -157.86),
    ("Anchorage", "AK", "Anchorage", 61.22, -149.90),
    ("Birmingham", "AL", "Jefferson", 33.52, -86.81),
]

PLACES_MEASURES = ["CASTHMA", "COPD", "CSMOKING", "OBESITY", "DIABETES",
                   "ACCESS2", "BPHIGH", "CHD", "DEPRESSION", "LPA"]


def get_json(url, params, retries=4):
    for attempt in range(retries):
        r = requests.get(url, params=params, timeout=90)
        if r.status_code == 200:
            return r.json()
        time.sleep(3 * (attempt + 1))
    r.raise_for_status()


def gather_air_quality():
    frames = []
    for city, state, county, lat, lon in CITIES:
        data = get_json(AQ_URL, {"latitude": lat, "longitude": lon, "start_date": START,
                                 "end_date": END, "hourly": ",".join(AQ_VARS),
                                 "timezone": "auto"})
        df = pd.DataFrame(data["hourly"])
        df.insert(0, "city", city)
        df.insert(1, "state", state)
        frames.append(df)
        print("air quality", city, len(df))
        time.sleep(0.4)
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(RAW / "openmeteo_air_quality_hourly_raw.csv", index=False)


def gather_weather():
    frames = []
    for city, state, county, lat, lon in CITIES:
        data = get_json(WX_URL, {"latitude": lat, "longitude": lon, "start_date": START,
                                 "end_date": END, "daily": ",".join(WX_VARS),
                                 "timezone": "auto"})
        df = pd.DataFrame(data["daily"])
        df.insert(0, "city", city)
        df.insert(1, "state", state)
        frames.append(df)
        print("weather", city, len(df))
        time.sleep(0.4)
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(RAW / "openmeteo_weather_daily_raw.csv", index=False)


def gather_health():
    where = "measureid in (" + ",".join(f"'{m}'" for m in PLACES_MEASURES) + ")"
    rows = get_json(PLACES_URL, {"$where": where, "$limit": 100000})
    df = pd.json_normalize(rows)
    df.to_csv(RAW / "cdc_places_county_raw.csv", index=False)
    print("CDC PLACES rows", len(df))


def save_city_table():
    pd.DataFrame(CITIES, columns=["city", "state", "county", "latitude", "longitude"]) \
        .to_csv(RAW / "cities_reference.csv", index=False)


if __name__ == "__main__":
    save_city_table()
    gather_health()
    gather_weather()
    gather_air_quality()
