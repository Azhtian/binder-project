import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge

"""
Preparations for making prediction data.
Go to the bottom.
"""


# Open files with correct encoding
games_2017 = pd.read_html('2017/games.xls', encoding='utf-8')[0]
games_2018 = pd.read_html('2018/games.xls', encoding='utf-8')[0]
games_2019 = pd.read_html('2019/games.xls', encoding='utf-8')[0]

teams_2017 = pd.read_html('2017/team-stats.xls', encoding='utf-8')[0]
teams_2018 = pd.read_html('2018/team-stats.xls', encoding='utf-8')[0]
teams_2019 = pd.read_html('2019/team-stats.xls', encoding='utf-8')[0]

# Gather all years in one table.
tot_games = pd.concat((pd.concat((games_2017, games_2018)), games_2019))
tot_teams = pd.concat((pd.concat((teams_2017, teams_2018)), teams_2019))

# Drop rows where all values are NaN and iterate to change row format of Score from "2-1" to two rows with 2 and 1 as Score.
# Only choosing the columns I am interested in.
iter_data = tot_games.loc[:, ['Score', 'Home', 'Away', 'Venue', 'Attendance']].dropna(how='all').reset_index()
df_games = pd.DataFrame([], index=[], columns=['Score', 'Home', 'Away', 'Venue', 'Attendance'])

# For 2017-2019 games
for (i, row) in iter_data.iterrows():
    homeGls = row[1][0]
    awayGls = row[1][2]
    home = row[2]
    away = row[3]
    # første kamp rad
    row[1] = homeGls
    row[5] = 1
    df_games = df_games.append(row.drop(['index']))
    # andre kamp rad
    row[1] = awayGls
    row[2] = away
    row[3] = home
    row[5] = 0
    df_games = df_games.append(row.drop(['index']))

# Making new column names and removing two matches where IF Fløya shows up.
df_games = df_games.rename(columns={'Home': 'Team', 'Away': 'Opponent', 'Attendance': 'Venue_HA'}).reset_index(drop=True)
df_games = df_games.iloc[:-4]

# Making a dataframe of averages from the teams df.
# list of team names
all_teams = tot_teams.drop_duplicates(('Unnamed: 0_level_0', 'Squad'), ignore_index=True)['Unnamed: 0_level_0']

for (i, row) in all_teams.iterrows():
    # Number of matches
    games_played = len(df_games.loc[df_games['Team'] == row.values[0]])
    games_played_venue = games_played/2

    # Calculating averages
    avgGls = sum(map(int, df_games.loc[df_games['Team'] == row.values[0]]['Score'].values))/games_played
    avgConceded = sum(map(int, df_games.loc[df_games['Opponent'] == row.values[0]]['Score'].values))/games_played
    avgGlsHome = sum(map(int, df_games.loc[(df_games['Team'] == row.values[0]) & (df_games['Venue_HA'] == 1)]['Score'].values))/games_played_venue
    avgGlsAway = sum(map(int, df_games.loc[(df_games['Team'] == row.values[0]) & (df_games['Venue_HA'] == 0)]['Score'].values))/games_played_venue
    avgConcededHome = sum(map(int, df_games.loc[(df_games['Opponent'] == row.values[0]) & (df_games['Venue_HA'] == 0)]['Score'].values))/games_played_venue
    avgConcededAway = sum(map(int, df_games.loc[(df_games['Opponent'] == row.values[0]) & (df_games['Venue_HA'] == 1)]['Score'].values))/games_played_venue
    avgAge = sum(tot_teams.loc[tot_teams[('Unnamed: 0_level_0', 'Squad')] == row.values[0], ('Unnamed: 2_level_0', 'Age')])/len(tot_teams.loc[tot_teams[('Unnamed: 0_level_0', 'Squad')] == row.values[0], ('Unnamed: 2_level_0', 'Age')])

    all_teams.loc[i, 'AvgGls'] = avgGls
    all_teams.loc[i, 'AvgConceded'] = avgConceded
    all_teams.loc[i, 'AvgGlsHome'] = avgGlsHome
    all_teams.loc[i, 'AvgGlsAway'] = avgGlsAway
    all_teams.loc[i, 'AvgConcededHome'] = avgConcededHome
    all_teams.loc[i, 'AvgConcededAway'] = avgConcededAway
    all_teams.loc[i, 'AvgAge'] = avgAge

df_venues = df_games.loc[:, ['Venue']].drop_duplicates('Venue', ignore_index=True)

for (i, row) in df_venues.iterrows():
    venue = df_games.loc[df_games['Venue'] == row.values[0]]['Score'].values
    avgGlsPrVenue = sum(map(int, venue))/len(venue)
    df_venues.loc[i, 'AvgGlsPrVenue'] = avgGlsPrVenue


def put_it_in_there(datafr):
    for j in ['AvgGls', 'AvgConceded', 'AvgGlsHA', 'Venue_H', 'Venue_A', 'AvgConcededHA', 'AvgGlsPrVenue', 'AvgAge', 'AvgAgeOpp']:
        datafr[j] = 0

    for (i, row) in datafr.iterrows():
        datafr.loc[i, 'AvgGls'] = all_teams.loc[all_teams['Squad'] == row.values[0], 'AvgGls'].values[0]
        datafr.loc[i, 'AvgConceded'] = all_teams.loc[all_teams['Squad'] == row.values[1], 'AvgConceded'].values[0]
        datafr.loc[i, 'AvgGlsPrVenue'] = df_venues.loc[df_venues['Venue'] == row.values[2], 'AvgGlsPrVenue'].values[0]
        datafr.loc[i, 'AvgAge'] = all_teams.loc[all_teams['Squad'] == row.values[0], 'AvgAge'].values[0]
        datafr.loc[i, 'AvgAgeOpp'] = all_teams.loc[all_teams['Squad'] == row.values[1], 'AvgAge'].values[0]

        # team is playing on home venue
        if row.values[3] == 1:
            datafr.loc[i, 'AvgGlsHA'] = all_teams.loc[all_teams['Squad'] == row.values[0], 'AvgGlsHome'].values[0]
            datafr.loc[i, 'Venue_H'] = 1
            datafr.loc[i, 'AvgConcededHA'] = all_teams.loc[all_teams['Squad'] == row.values[0], 'AvgConcededAway'].values[0]

        # team is playing on away venue
        elif row.values[3] == 0:
            datafr.loc[i, 'AvgGlsHA'] = all_teams.loc[all_teams['Squad'] == row.values[0], 'AvgGlsAway'].values[0]
            datafr.loc[i, 'Venue_A'] = 1
            datafr.loc[i, 'AvgConcededHA'] = all_teams.loc[all_teams['Squad'] == row.values[0], 'AvgConcededHome'].values[0]
    datafr = datafr.iloc[:, 3:]
    return datafr


X_all = pd.read_csv('X_all.csv')
y_all = pd.read_csv('y_all.csv')


def predict_score(X):
    lasso = Ridge(alpha=3.57143)
    lasso.fit(np.array(X_all), np.array(y_all))
    X = put_it_in_there(pd.DataFrame(X))
    return lasso.predict(np.array(X))
