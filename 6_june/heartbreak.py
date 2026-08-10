# %% -*- IMPORTS -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as font_manager

# %% read csv file
results_df = pd.read_csv("ENG_results.csv")
# %% set order of round so the best result (F) is a the top of the chart

round_order = ["F", "SF", "QF", "Rof16", "GS", "DNQ"]

results_df["Round"] = pd.Categorical(
    results_df["Round"], categories=round_order, ordered=True
)

# %% -*- DATA VIZ -*-

# set colour variables
tournament_colours = {"World Cup": "#FFFFFF", "Euros": "#CE1124"}
background_colour = "#F9F6EE"
blue_colour = "#000040"

# add marker font
font_dir = ["/Users/lwoodblake/Documents/fonts/Permanent_Marker"]

for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

marker_font = {"fontname": "Permanent Marker"}

# add sen font
font_dir = ["/Users/lwoodblake/Documents/fonts/Sen"]

for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

sen_font = {"fontname": "Sen"}


# create viz
sns.set_theme(
    rc={"axes.facecolor": background_colour, "figure.facecolor": background_colour}
)
sns.set_style("whitegrid", {"axes.grid": False})

plt.rcParams.update(
    {
        "font.family": "",
        "axes.labelcolor": blue_colour,
        "xtick.color": blue_colour,
        "ytick.color": blue_colour,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
    }
)
plt.figure(figsize=(8, 4))

plt.gca().set_facecolor(background_colour)
plt.gcf().set_facecolor(background_colour)

sns.lineplot(data=results_df, x="Year", y="Round", color="#c3c3c3")

sns.scatterplot(
    data=results_df,
    x="Year",
    y="Round",
    hue="Tournament",
    palette=tournament_colours,
    s=100,
    zorder=2,
    edgecolor=blue_colour,
    linewidth=1.5,
)

plt.xticks(
    [
        1996,
        1998,
        2000,
        2002,
        2004,
        2006,
        2008,
        2010,
        2012,
        2014,
        2016,
        2018,
        2020,
        2022,
        2024,
        2026,
    ],
    rotation=90,
)
plt.tick_params(which="both", direction="out", bottom=True, left=True)
sns.despine(top=True, right=True, left=False, bottom=False)
plt.legend(title=None, loc="lower right", frameon=False)
plt.xlabel("Year", labelpad=15)
plt.ylabel("Stage Reached", labelpad=15)

plt.title(
    "England: Major Tournament Results",
    fontsize=21,
    fontweight="bold",
    fontname="Permanent Marker",
    color=blue_colour,
    pad=20,
)

plt.savefig(
    f"heartbreak.png",
    dpi=500,
    bbox_inches="tight",
    facecolor=background_colour,
)

plt.show()
