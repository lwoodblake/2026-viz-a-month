# %% -*- IMPORTS -*-
import pandas as pd
import numpy as np
from statsbombpy import sb
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from mplsoccer import Pitch, add_image
# %% -*- GET DATA -*-

# set competition id, season id, and team name for pulling event data
comp_id = 2
season_id = 44
team = 'Arsenal'

# get comp matches and filter to only matches played by team
matches_df = sb.matches(competition_id=comp_id, season_id=season_id)
team_matches = matches_df[(matches_df['home_team'] == team)
                          | (matches_df['away_team'] == team)]

team_matches = team_matches[(team_matches['match_status'] == 'available')]

# loop over list of matches to get event data and append to events_df
match_id_list = team_matches.match_id.tolist()

events_df = []

for i in match_id_list:
    match_events = sb.events(match_id=i)
    # separate x and y coordinates
    match_events['x'] = match_events['location'].str[0]
    match_events['y'] = match_events['location'].str[1]
    match_events['pass_end_x'] = match_events['pass_end_location'].str[0]
    match_events['pass_end_y'] = match_events['pass_end_location'].str[1]
    match_events['carry_end_x'] = match_events['carry_end_location'].str[0]
    match_events['carry_end_y'] = match_events['carry_end_location'].str[1]
    events_df.append(match_events)
events_df = pd.concat(events_df, ignore_index=True)

# %% ADD COLUMNS REQUIRED TO FIND ONE-TWOS
# get timestamp in seconds format
events_df['total_seconds'] = pd.to_timedelta(events_df['timestamp']).dt.total_seconds()
# get distance to goal based on start coordinates
events_df['distance_to_goal'] = np.sqrt((120 - events_df['x'])**2 + (40 - events_df['y'])**2)
# get distance to goal based on end coordinates
events_df['distance_to_goal_end_loc'] = np.sqrt((120 - events_df['pass_end_x'])**2 + (40 - events_df['pass_end_y'])**2)

# add carry length
events_df['carry_length'] = np.sqrt((events_df.carry_end_x - events_df.x)**2 + (events_df.carry_end_y -events_df.y)**2)
# %% FILTER TO TEAM EVENTS AND SORT BY TIMESTAMP
match_events = events_df[(events_df.team == team)]

match_events = match_events.sort_values(by=['match_id', 'period',
                                            'timestamp', 'index'])
# add previous event type and previous carry length to filter out one-twos
# with a significant carry in between the two passes
match_events['previous_type'] = match_events.groupby(['match_id', 'possession'])['type'].shift(+1)
match_events['previous_carry_length'] = match_events.groupby(['match_id', 'possession'])['carry_length'].shift(+1)
match_events['previous_carry_length'] = match_events['previous_carry_length'].fillna(0)

# %% SELECT PASSES

set_passes = ['Kick Off', 'Corner', 'Free Kick', 'Goal Kick', 'Throw In']
# select all open play passes
passes_df = match_events[
    (match_events['type'] == 'Pass')
    & (~match_events['pass_type'].isin(set_passes))][['match_id', 'period', 
                                                      'possession', 'id', 'total_seconds',
                                                      'player', 'pass_recipient',
                                                      'pass_outcome', 'distance_to_goal',
                                                      'distance_to_goal_end_loc',
                                                      'previous_carry_length']].copy()

# add columns for next pass details, if passes are 
# in the same possession and match
passes_df['next_pass_id'] = passes_df.groupby(['match_id', 'possession'])['id'].shift(-1)

passes_df['next_pass_recipient'] = passes_df.groupby(['match_id', 'possession'])['pass_recipient'].shift(-1)

passes_df['next_pass_outcome'] = passes_df.groupby(['match_id', 'possession'])['pass_outcome'].shift(-1)

passes_df['next_pass_seconds'] = passes_df.groupby(['match_id', 'possession'])['total_seconds'].shift(-1)

passes_df['next_distance_end_loc'] = passes_df.groupby(['match_id', 'possession'])['distance_to_goal_end_loc'].shift(-1)

# %% FILTER TO FIND VALID PASSING COMBINATIONS

# get number of seconds between the two passes
passes_df['seconds_inbetween'] = passes_df['next_pass_seconds'] - passes_df['total_seconds']

# get change in distance to goal between the two passes
passes_df['distance_change'] = passes_df['distance_to_goal'] - passes_df['next_distance_end_loc']

# filter to only passes where both passes were complete and
# the next_pass_recipient is not null
passes_df = passes_df[(passes_df['pass_outcome'].isna())
                      & (passes_df['next_pass_outcome'].isna())
                      & ~(passes_df['next_pass_recipient'].isna())]

# filter to passes where
# there was less than 5 seconds between pass 1 and 2
# the distance to goal decreased by at least 5 pseudo-yards
# between pass 1 and pass 2
# the carry length between the two passes was less than 5 pseudo-yards
passes_df = passes_df[(passes_df['seconds_inbetween'] <= 5)
                      & (passes_df['distance_change'] >= 5)
                      & (passes_df['previous_carry_length'] <= 2)]

# %% ADD COORDINATES TO PASSES_DF FOR PLOTTING

location_df = events_df[['id', 'x', 'y', 'pass_end_x', 'pass_end_y']]

# add for pass 1 in the one-two
passes_df = pd.merge(
    passes_df,
    location_df,
    on='id',
    how='left'
    )

# add for pass 2 in the one-two
passes_df = pd.merge(
    passes_df,
    location_df,
    left_on='next_pass_id',
    right_on='id',
    how='left',
    suffixes=('_1', '_2')
    )

# %% filter to one-twos by selecting passes where
# the pass recipient of pass 1 is the same as the passer of pass 2
one_two_df = passes_df[(passes_df['player'] == passes_df['next_pass_recipient'])]

# get counts for each one-two combo
combo_count = one_two_df.groupby(['player', 'pass_recipient',
                                  'next_pass_recipient']).size().reset_index(name='count')

# %% CHOOSE A GOOD EXAMPLE TO PLOT AND PLOT THE ONE-TWO

# select one-two examples that start outside of the defensive third,
# with a distance to goal deceease of at least 20 pseudo-yards
plot_df = one_two_df[(one_two_df.x_1 >= 40) & (one_two_df.distance_change>=20)].copy()

# sort by seconds between the two passes to find the most rapid one-twos
plot_df.sort_values(by='seconds_inbetween', ascending=True, inplace=True)

# select player names to use in the visualisation title
player1=plot_df.player.iloc[3]
player2=plot_df.pass_recipient.iloc[3]
player3=plot_df.next_pass_recipient.iloc[3]
# select line of data to plot
plot_df=plot_df.iloc[3]

# colour variables
white = 'white'
arsenal_red = "#EF0107"
arsenal_blue = "#063672"
sbred = "#E21017"
nice_yellow = "#FFD464"
off_white = '#F9F6EE'
charcoal = "#313639"

# load statsbomb logo
sb_logo = Image.open('/Users/lwoodblake/Documents/logos/hudl-statsbomb.png')

# load font
font_dir = ['/Users/lwoodblake/Documents/fonts/Inter']
for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

interfont = {'fontname': 'Inter'}

# add half way coordinates for arrows
plot_df['x_half_1'] = ((plot_df['pass_end_x_1']-plot_df['x_1'])/1.5)+plot_df['x_1']
plot_df['y_half_1'] = ((plot_df['pass_end_y_1']-plot_df['y_1'])/1.5)+plot_df['y_1']
plot_df['x_half_2'] = ((plot_df['pass_end_x_2']-plot_df['x_2'])/1.5)+plot_df['x_2']
plot_df['y_half_2'] = ((plot_df['pass_end_y_2']-plot_df['y_2'])/1.5)+plot_df['y_2']

# draw pitch
pitch = Pitch(pitch_type='statsbomb', pitch_color=off_white,
              line_zorder=1, line_color=charcoal, half=False)

fig, ax = pitch.draw(figsize=(10, 15), constrained_layout=True)
fig.set_facecolor(off_white)

# -*- PLOT THE FIRST PASS -*-
pitch.arrows(plot_df.x_1, plot_df.y_1,
             plot_df.pass_end_x_1, plot_df.pass_end_y_1, ax=ax,
             zorder=3, lw=0.5, color=arsenal_red, alpha=1,
             headwidth=0, headlength=0, headaxislength=0)

# include a half arrow to indicate pass direction
pitch.arrows(plot_df.x_1, plot_df.y_1,
             plot_df.x_half_1, plot_df.y_half_1,
             ax=ax, lw=0.5, zorder=3, color=arsenal_red, alpha=1,
             headwidth=4, headlength=5, headaxislength=5)

# -*- PLOT THE SECOND PASS -*-
pitch.arrows(plot_df.x_2, plot_df.y_2,
             plot_df.pass_end_x_2, plot_df.pass_end_y_2, ax=ax,
             zorder=3, lw=0.5, color=arsenal_blue, alpha=1,
             headwidth=0, headlength=0, headaxislength=0)

# include a half arrow to indicate pass direction
pitch.arrows(plot_df.x_2, plot_df.y_2,
             plot_df.x_half_2, plot_df.y_half_2,
             ax=ax, lw=0.5, zorder=3, color=arsenal_blue, alpha=1,
             headwidth=4, headlength=5, headaxislength=5)

# -*- ADDITIONAL DETAILS TO PLOT -*-

# plot player 1's movement
pitch.lines(plot_df.x_1, plot_df.y_1,
            plot_df.pass_end_x_2, plot_df.pass_end_y_2, ax=ax, lw=2,
            zorder=2, linestyle='--', color='#c3c3c3', alpha=1)

# plot player 2's movement after ball receipt, if applicable
pitch.lines(plot_df.pass_end_x_1, plot_df.pass_end_y_1,
            plot_df.x_2, plot_df.y_2, ax=ax, lw=2,
            zorder=2, linestyle='--', color='#c3c3c3', alpha=1)

# plot receipt locations
pitch.scatter(plot_df.x_1, plot_df.y_1, s=250, c=arsenal_red,
              alpha=1, ax=ax, zorder=4)

pitch.scatter(plot_df.x_2, plot_df.y_2, s=250, c=arsenal_blue,
              alpha=1, ax=ax, zorder=4)

pitch.scatter(plot_df.pass_end_x_2, plot_df.pass_end_y_2, s=250, c=arsenal_red,
              alpha=1, ax=ax, zorder=4)

# add title and subtitle
fig.text(s="One-Two Example", x=-0.02, y=0.75, fontsize=36,
         weight="bold", c=charcoal, font='Inter')

fig.text(s=f'{player1} → {player2} → {player3}', x=-0.02, y=0.72,
         fontsize=24, style='italic', c=charcoal, font='Inter')

# add logo
add_image(sb_logo, fig, left=0.55, bottom=0.25,height=0.048)

# save figure
plt.savefig('one-two-example.png', dpi=300, bbox_inches='tight')

# %%
