# %% IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle
from matplotlib.colors import ListedColormap
import matplotlib.font_manager as font_manager

# %% VIZ SETTINGS
# lfc colours
colours = ["#C8102E", "#00B2A9", "#F9F6EE"]

# create cmap
lfc_cmap = ListedColormap(colours)

background_colour = "#1A1A1A"

lfc_df = pd.read_csv("lfc.csv")

font_dir = ["/Users/lwoodblake/Documents/fonts/Arvo"]

for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

plt.rcParams["font.family"] = "Arvo"
plt.rcParams["text.color"] = "white"
plt.rcParams["axes.labelcolor"] = "white"

# %% FORMAT DATA FOR EACH PLOT
plot1 = {
    "values": [lfc_df["W"].iloc[0], lfc_df["D"].iloc[0], lfc_df["L"].iloc[0]],
    "labels": ["W", "D", "L"],
    "title": {"label": f"{lfc_df['Season'].iloc[0]}", "loc": "left", "fontsize": 12},
}

plot2 = {
    "values": [lfc_df["W"].iloc[1], lfc_df["D"].iloc[1], lfc_df["L"].iloc[1]],
    "labels": ["W", "D", "L"],
    "title": {"label": f"{lfc_df['Season'].iloc[1]}", "loc": "left", "fontsize": 12},
}

plot3 = {
    "values": [lfc_df["W"].iloc[2], lfc_df["D"].iloc[2], lfc_df["L"].iloc[2]],
    "labels": ["W", "D", "L"],
    "title": {"label": f"{lfc_df['Season'].iloc[2]}", "loc": "left", "fontsize": 12},
}


plot4 = {
    "values": [lfc_df["W"].iloc[3], lfc_df["D"].iloc[3], lfc_df["L"].iloc[3]],
    "labels": ["W", "D", "L"],
    "title": {"label": f"{lfc_df['Season'].iloc[3]}", "loc": "left", "fontsize": 12},
}


plot5 = {
    "values": [lfc_df["W"].iloc[4], lfc_df["D"].iloc[4], lfc_df["L"].iloc[4]],
    "labels": ["W", "D", "L"],
    "title": {"label": f"{lfc_df['Season'].iloc[4]}", "loc": "left", "fontsize": 12},
}


# %% PLOT FIG

fig = plt.figure(
    FigureClass=Waffle,
    plots={511: plot1, 512: plot2, 513: plot3, 514: plot4, 515: plot5},
    rows=3,
    cmap_name=lfc_cmap,
    figsize=(5, 9),
    legend={
        "loc": "lower center",
        "bbox_to_anchor": (0.5, 1.05),
        "ncol": len(plot1),
        "framealpha": 0,
    },
)

fig.suptitle(
    "Liverpool FC: EPL Results by Season", fontsize=14, fontweight="bold", color="white"
)

fig.text(s="Data via FBref", x=-0.02, y=0.01, fontsize=12)

fig.text(s="@lwoodblake", x=0.8, y=0.01, fontsize=12, style="italic")

fig.set_facecolor(background_colour)

plt.savefig(
    "lfc.png",
    dpi=500,
    bbox_inches="tight",
    facecolor=background_colour,
)

plt.show()
# %%
