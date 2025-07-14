"""
Data vizualization of the 1000g project data on a phenotype / composition basis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas
import os
import cartopy.io.shapereader as shpreader

# Get the absolute path of the CSV file
base_dir = os.path.dirname(os.path.abspath(__file__))
phenotypes_path = os.path.abspath(os.path.join(base_dir, "phenotypes.csv"))
df = pd.read_csv(phenotypes_path)

# Set the style for the plots
sns.set_style("white")

# 1. Gender Distribution within each Super Population (Stacked Bar Chart)
plt.figure(figsize=(12, 7), facecolor="none")
# Crosstabulation of super_pop and gender
super_pop_gender = pd.crosstab(df["super_pop"], df["gender"])
colors = sns.color_palette("viridis", len(super_pop_gender.columns))
ax = super_pop_gender.plot(kind="bar", stacked=True, color=colors, figsize=(12, 7))
ax.set_facecolor("none")
plt.xlabel("Super Population")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.legend(title="Gender", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(
    os.path.join(base_dir, "gender_by_super_pop.png"),
    dpi=300,
    bbox_inches="tight",
    transparent=True,
)
plt.clf()

# 2. Population Distribution within each Super Population (Stacked Bar Chart)
plt.figure(figsize=(15, 8), facecolor="none")
super_pop_pop = pd.crosstab(df["super_pop"], df["pop"])

# Population labels mapping
pop_labels = {
    "ACB": "African Caribbean in Barbados",
    "GBR": "British from England and Scotland",
    "CDX": "Chinese Dai in Xishuangbanna, China",
    "CLM": "Colombian in Medellín, Colombia",
    "FIN": "Finnish in Finland",
    "GWD": "Gambian in Western Division - Mandinka",
    "CHS": "Han Chinese South China",
    "IBS": "Iberian populations in Spain",
    "KHV": "Kinh in Ho Chi Minh City, Vietnam",
    "PEL": "Peruvian in Lima, Peru",
    "PUR": "Puerto Rican in Puerto Rico",
    "PJL": "Punjabi in Lahore, Pakistan",
}

# Create legend labels for populations present in data
present_pops = super_pop_pop.columns.tolist()
legend_labels = [f"{pop}: {pop_labels.get(pop, pop)}" for pop in present_pops]

colors = sns.color_palette("tab20", len(super_pop_pop.columns))
ax = super_pop_pop.plot(kind="bar", stacked=True, color=colors, figsize=(15, 8))
ax.set_facecolor("none")
plt.xlabel("Super Population")
plt.ylabel("Count")
plt.xticks(rotation=45)

# Add population labels on bar segments
for i, super_pop in enumerate(super_pop_pop.index):
    y_offset = 0
    for j, pop in enumerate(super_pop_pop.columns):
        count = super_pop_pop.loc[super_pop, pop]
        if count > 0:  # Only add label if there are samples
            # Calculate the middle position of this segment
            y_position = y_offset + count / 2
            ax.text(
                i,
                y_position,
                pop,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="white",
            )
            y_offset += count

plt.legend(
    legend_labels, title="Population", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8
)
plt.tight_layout()
plt.savefig(
    os.path.join(base_dir, "population_by_super_pop.png"),
    dpi=300,
    bbox_inches="tight",
    transparent=True,
)
plt.clf()

# 3. World Map of Population Distribution
# Population to coordinates mapping
pop_coords = {
    "IBS": {"lat": 40, "lon": -4},  # Spain
    "CHS": {"lat": 30, "lon": 104},  # China
    "PUR": {"lat": 18.5, "lon": -66.5},  # Puerto Rico
    "FIN": {"lat": 62, "lon": 25},  # Finland
    "KHV": {"lat": 11, "lon": 105},  # Vietnam
    "ACB": {"lat": 13, "lon": -59},  # Barbados
    "CLM": {"lat": 4, "lon": -74},  # Colombia
    "CDX": {"lat": 23, "lon": 113},  # China
    "GBR": {"lat": 53, "lon": 0},  # United Kingdom
    "PEL": {"lat": -12, "lon": -77},  # Peru
    "GWD": {"lat": 13, "lon": -15},  # Gambia
    "PJL": {"lat": 30, "lon": 69},  # Pakistan
}

pop_df = pd.DataFrame.from_dict(pop_coords, orient="index").reset_index()
pop_df.columns = ["pop", "lat", "lon"]

# Merge with phenotype data to get counts
pop_counts = df["pop"].value_counts().reset_index()
pop_counts.columns = ["pop", "count"]
pop_geo_df = pd.merge(pop_df, pop_counts, on="pop")

# Create GeoDataFrame
gdf = geopandas.GeoDataFrame(
    pop_geo_df, geometry=geopandas.points_from_xy(pop_geo_df.lon, pop_geo_df.lat)
)

# Plotting
world = geopandas.read_file(
    shpreader.natural_earth(resolution="110m", category="cultural", name="admin_0_countries")
)
fig, ax = plt.subplots(figsize=(20, 10), facecolor="none")
world.plot(ax=ax, color="#ededed", edgecolor="black")
ax.set_facecolor("none")
ax.grid(False)  # Remove grid
ax.set_xticks([])  # Remove x-axis ticks
ax.set_yticks([])  # Remove y-axis ticks

# Scale marker sizes to be more visible and proportional
min_size = 100  # minimum marker size
max_size = 1000  # maximum marker size
normalized_sizes = min_size + (gdf["count"] - gdf["count"].min()) / (
    gdf["count"].max() - gdf["count"].min()
) * (max_size - min_size)

# Plot without legend first to have better control
gdf.plot(
    ax=ax,
    c=gdf["count"],
    cmap="viridis",
    markersize=normalized_sizes,
    alpha=0.8,
    legend=False,  # We'll create our own legend
    edgecolors="white",
    linewidth=1.0,
)

# Add text labels for each population
for idx, row in gdf.iterrows():
    ax.annotate(
        f"{row['pop']} ({int(row['count'])})",
        (row.geometry.x, row.geometry.y),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        ha="left",
    )

plt.tight_layout()
plt.savefig(
    os.path.join(base_dir, "population_map.png"),
    dpi=300,
    bbox_inches="tight",
    transparent=True,
)
