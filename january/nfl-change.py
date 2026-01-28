# %% -*- IMPORTS -*-
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import nflreadpy as nfl
import urllib.request
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import urllib
import urllib.request

# %% -*- FONT AND COLOUR SETTINGS -*-
charcoal = '#313639'
background_colour = '#F9F6EE'
decline_colour = '#D50A0A'
improved_colour = '#0096FF'

font_dir = ['/Users/lwoodblake/Documents/fonts/Michroma']

for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

michroma_font = {'fontname': 'Michroma'}
# %% -*- FUNCTION TO GET IMAGE FROM URL -*-


def getImage(path, zoom=0.5, target_size=(75, 75)):
    with urllib.request.urlopen(path) as url:
        img = Image.open(url)
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        return OffsetImage(img, zoom=zoom)


# %% -*- GRAB TEAM LOGOS FROM nflreadpy -*-
logos = nfl.load_teams()
logos_df = logos.to_pandas()

# %% -*- LOAD NFL DATA -*-
nfl_df = pd.read_csv('nfl-24-25.csv')

# add team logos to nfl data
nfl_df = nfl_df.merge(logos_df, left_on='Team', right_on='team_name')

# %% -*- CALCULATE MOST IMPROVED AND MOST DECLINED -*-

# pivot data to have seasons as columns
nfl_pivot = pd.pivot_table(
    nfl_df, values="Pct", index=["Team"], columns=["Season"]
).reset_index()

# calculate pct change between 2024 and 2025
nfl_pivot['pct_change'] = nfl_pivot[2025] - nfl_pivot[2024]

# highest pct_change
nfl_pivot.sort_values(by="pct_change", ascending=False, inplace=True)
improved_df = nfl_pivot.head(5)
most_improved = improved_df['Team'].tolist()

# lowest pct_change
nfl_pivot.sort_values(by="pct_change", ascending=True, inplace=True)
declined_df = nfl_pivot.head(5)
most_declined = declined_df['Team'].tolist()

# ensure data types are correct for plotting
nfl_df['Season'] = nfl_df['Season'].astype(int)
nfl_df['Pct'] = nfl_df['Pct'].astype(float)

# list of divisions to loop through
divisions = nfl_df['Division'].unique().tolist()


# %% -*- PLOT VIZ -*-

# set figure size and dimensions
fig, axes = plt.subplots(4, 2, figsize=(10, 20))
fig.patch.set_facecolor(background_colour)

# create ax for 8 subplots, one for each division
ax1 = axes[0, 0]
ax2 = axes[1, 0]
ax3 = axes[0, 1]
ax4 = axes[1, 1]
ax5 = axes[2, 0]
ax6 = axes[2, 1]
ax7 = axes[3, 0]
ax8 = axes[3, 1]

# add axes to a list for looping
ax_list = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

for i in range(len(divisions)):
    # each division gets its own ax
    ax = ax_list[i]
    division = divisions[i]
    # filter data to the division
    division_df = nfl_df[(nfl_df['Division'] == division)]
    # create a list of teams within the division
    teams = division_df['Team'].unique().tolist()

    # ax visual settings
    ax.set(aspect='equal')
    ax.tick_params(axis='x', which='both', bottom=False, labelbottom=True)
    ax.set_xticks([2024, 2025])
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.axhline(y=0.25, color='#c3c3c3', linestyle='--', linewidth=1)
    ax.axhline(y=0.5, color='#c3c3c3', linestyle='--', linewidth=1)
    ax.axhline(y=0.75, color='#c3c3c3', linestyle='--', linewidth=1)

    # loop through teams in the select division and plot
    for team in teams:

        # filter to the team
        team_df = division_df[(division_df['Team'] == team)]

        # set line colour based on whether team is in improved/declined lists
        if team in most_improved:
            colour = improved_colour
        elif team in most_declined:
            colour = decline_colour
        else:
            colour = '#A9A9A9'

        # add the trendline to the plot
        ax.set_ylim(0, 1)
        ax.plot(team_df['Season'], team_df['Pct'], marker='.', color=colour)

        # find url for team logo and set x y coords for plotting
        paths = team_df.team_logo_espn.tolist()
        x = team_df['Season'].tolist()
        y = team_df['Pct'].tolist()

        # plot team logos on the chart
        for x0, y0, path in zip(x, y, paths):
            try:
                offset_image = getImage(path)
                if offset_image:
                    ab = AnnotationBbox(offset_image, (x0, y0), frameon=False)
                    ax.add_artist(ab)
                else:
                    print(f"image not found for {team}")
            except Exception as e:
                print(f"getImage error {e}")

    # add title for division
    ax.set_title(f'{division}', fontname='Michroma', fontsize=16,
                 color=charcoal)

# add titles to fig
fig.text(s="NFL Win %: 2024 -> 2025", x=0.05, y=0.94, fontsize=24,
         fontname='Michroma', color=charcoal)

fig.text(s="Top 5 most", x=0.05, y=0.92, fontsize=16,
         fontname='Michroma', color=charcoal)

fig.text(s="improved", x=0.22, y=0.92, fontsize=16, fontname='Michroma',
         color=improved_colour, weight='heavy')

fig.text(s=" & ", x=0.35, y=0.92, fontsize=16, fontname='Michroma',
         color=charcoal)

fig.text(s="declined", x=0.39, y=0.92, fontsize=16, fontname='Michroma',
         color=decline_colour, weight='heavy')

fig.text(s="highlighted", x=0.515, y=0.92, fontsize=16,
         fontname='Michroma', color=charcoal)

fig.text(s="Regular season only. Data from nfl.com/standings/",
         x=0.45, y=0.08, fontsize=12, fontname='Michroma', color=charcoal)

# save fig
plt.savefig('nfl-change.png', dpi=1000, bbox_inches='tight',
            facecolor=background_colour)
plt.show()

# %%
