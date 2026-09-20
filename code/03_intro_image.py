"""Create the AQI scale infographic used in the Introduction tab.

Category ranges and colors follow the US EPA Air Quality Index.
Run:  python code/03_intro_image.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "images" / "intro_aqi_scale.png"

levels = [
    ("Good", "0-50", "#2e9e5b", "Satisfactory air.\nLittle or no risk."),
    ("Moderate", "51-100", "#f2c94c", "Acceptable. A few very\nsensitive people\nmay be affected."),
    ("Unhealthy for\nSensitive Groups", "101-150", "#f28e2b", "Children, older adults\nand people with lung\ndisease are at risk."),
    ("Unhealthy", "151-200", "#d1495b", "Everyone may begin\nto feel health effects."),
    ("Very Unhealthy", "201-300", "#8e44ad", "Health alert:\ngreater risk for all."),
    ("Hazardous", "301+", "#7b1e3a", "Emergency conditions.\nEveryone likely affected."),
]

fig, ax = plt.subplots(figsize=(12, 3.6))
ax.set_xlim(0, 6)
ax.set_ylim(0, 3.6)
ax.axis("off")
for i, (name, rng, color, text) in enumerate(levels):
    ax.add_patch(FancyBboxPatch((i + 0.04, 1.75), 0.92, 1.1, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=color, ec="none"))
    ax.text(i + 0.5, 2.5, name, ha="center", va="center", fontsize=10.5, fontweight="bold",
            color="black" if i == 1 else "white")
    ax.text(i + 0.5, 2.0, rng, ha="center", va="center", fontsize=12, color="black" if i == 1 else "white")
    ax.text(i + 0.5, 1.2, text, ha="center", va="top", fontsize=8.4, color="#374151")
ax.text(0, 3.4, "US Air Quality Index (AQI): what each level means for health", fontsize=14,
        fontweight="bold", va="center")
ax.text(0, 0.15, "Source: US EPA AirNow AQI categories. The index is driven by the worst of the measured "
        "pollutants (fine particles, ozone, and others).", fontsize=8.5, color="#6b7280")
fig.savefig(OUT, dpi=140, bbox_inches="tight")
