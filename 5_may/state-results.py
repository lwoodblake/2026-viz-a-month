# %% -*- IMPORTS -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import geopandas as gpd
import cartopy.crs as ccrs
from geopy.geocoders import Nominatim

# %% SET STATE NAME
state_name = "NEBRASKA"
focus_year = 2024
# %% -*- LOAD DATA -*-

# load shapefile
shape_path = "tl_2024_us_county/tl_2024_us_county.shp"
gdf = gpd.read_file(shape_path)

# load results csv
results_df = pd.read_csv("county_results_00_24.csv")

# %% -*- PREPARE DATA -*-

# filter by state_name and focus_year variables
state_results_df = results_df[
    (results_df.state == state_name) & (results_df.year == focus_year)
]

winners_df = state_results_df.loc[
    state_results_df.groupby("county_name")["candidatevotes"].idxmax()
]

# MERGE RESULTS DATA WITH SHAPEFILE DATA
# convert county_fips column to an int first to remove ".0"
# then convert to a string for merging
winners_df["county_fips"] = winners_df["county_fips"].astype(int)
winners_df["county_fips"] = winners_df["county_fips"].astype(str)

wins_shp_df = winners_df.merge(gdf, left_on="county_fips", right_on="GEOID", how="left")

# %% locate geographic extent for the given state
geolocator = Nominatim(user_agent="us_state_extent")
location = geolocator.geocode(state_name)
# format coordinates: [West, East, South, North]
bbox = [float(coord) for coord in location.raw["boundingbox"]]
extent = [bbox[2], bbox[3], bbox[0], bbox[1]]

# %% -*- CREATE MAP VISUALISATION -*-
# FONT AND COLOUR SETTINGS
charcoal = "#313639"
background_colour = "#F9F6EE"
republican_red = "#E81B23"
democrat_blue = "#0015BC"

# add graduate font
font_dir = ["/Users/lwoodblake/Documents/fonts/Graduate"]

for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

graduate_font = {"fontname": "Graduate"}

# add sen font
font_dir = ["/Users/lwoodblake/Documents/fonts/Sen"]

for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

sen_font = {"fontname": "Sen"}

# set county colour based on winning party
wins_shp_df["party_colour"] = np.where(
    wins_shp_df["party"] == "REPUBLICAN", republican_red, democrat_blue
)

# set map projection
map_crs = ccrs.AlbersEqualArea(central_longitude=-99.5, central_latitude=41.5)

# create plot
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": map_crs})

# viz aesthetics
fig.patch.set_facecolor(background_colour)
ax.patch.set_facecolor(background_colour)
ax.spines["geo"].set_visible(False)

# plot county polygons
ax.add_geometries(
    wins_shp_df["geometry"],
    crs=ccrs.PlateCarree(),
    facecolor=wins_shp_df["party_colour"],
    edgecolor="white",
    linewidth=0.8,
    alpha=0.8,
)

# set extent
ax.set_extent(extent, crs=ccrs.PlateCarree())

# titles and save fig
plt.title(
    f"{state_name} \n Presidential Election Results by County: {focus_year}",
    fontsize=21,
    fontweight="bold",
    fontname="Graduate",
    color=charcoal,
)

fig.text(
    s="Electoral data from https://electionlab.mit.edu/data \nShapefile from US Census Bureau",
    x=0.125,
    y=0.08,
    fontsize=12,
    fontname="Sen",
    color=charcoal,
)


plt.savefig(
    f"{state_name}_{focus_year}.png",
    dpi=500,
    bbox_inches="tight",
    facecolor=background_colour,
)
plt.show()
