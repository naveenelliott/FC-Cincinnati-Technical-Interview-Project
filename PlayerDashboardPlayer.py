# Importing necessary packages
import os 
import pandas as pd
import random
import string

# Setting a random seed for the six-digit key
random.seed(42)

# This function cleans the dataset and formats the csv file into proper use
def getFinalGrade(game_df):
    game_df.columns = game_df.iloc[3]
    game_df = game_df.iloc[4:]
    game_df = game_df.reset_index(drop=True)

    start_index = game_df.index[game_df["Period Name"] == "Round By Position Player"][0]

    # Find the index where "period name" is equal to "running by position player"
    end_index = game_df.index[game_df["Period Name"] == "Round By Team"][0]

# Select the rows between the two indices
    selected_rows = game_df.iloc[start_index:end_index]
    selected = selected_rows.reset_index(drop=True)
    selected = selected.iloc[1:]    
    return selected


# Directory paths for team folders
u13_folder = 'Bolts Post-Match/BoltsThirteenGames/'
u14_folder = 'Bolts Post-Match/BoltsFourteenGames/'
u15_folder = 'Bolts Post-Match/BoltsFifteenGames/'
u16_folder = 'Bolts Post-Match/BoltsSixteenGames/'
u17_folder = 'Bolts Post-Match/BoltsSeventeenGames/'
u19_folder = 'Bolts Post-Match/BoltsNineteenGames/'

# Initialize an empty list to store the selected dataframes
selected_dfs = []

# Function to process files in a folder and joining those files together
def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            game_df = pd.read_csv(file_path)
            selected_df = getFinalGrade(game_df)
            selected_dfs.append(selected_df)

# Process folders
process_folder(u13_folder)
process_folder(u14_folder)
process_folder(u15_folder)
process_folder(u16_folder)
process_folder(u17_folder)
process_folder(u19_folder)


# Concatenate all selected dataframes into one
selected = pd.concat(selected_dfs, ignore_index=True)

# dropping unnecessary columns
remove_first = ['Period Name', 'Squad Number', 'Match Date', 'Round Name']
selected = selected.drop(columns=remove_first, errors='ignore')
selected = selected.dropna(axis=1, how='all')

selected['Player Full Name'] = selected['Player Full Name'].replace('Christi Vilkimkin', 'Christi Vilikin')
selected['Player Full Name'] = selected['Player Full Name'].replace('Christian Martinez-Mole', 'Christian Martinez-Moule')
selected['Player Full Name'] = selected['Player Full Name'].replace('Della Rocca', 'Giovanni Della Rocca')
selected['Player Full Name'] = selected['Player Full Name'].replace('Estevez Rubino', 'Valentin Estevez Rubino')
selected['Player Full Name'] = selected['Player Full Name'].replace('George Noualme', 'George Nouaime')
selected['Player Full Name'] = selected['Player Full Name'].replace('Shai Sarrony', 'Shai Saarony')

# selecting the unique details for the players
details = selected.loc[:, ['Player Full Name', 'Team Name', 'As At Date']]
details.reset_index(drop=True, inplace=True)

# Function to generate random strings
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

# Create a dictionary to store the mappings of unique names to random assignments
name_assignments = {}

# Iterate through unique names
for name in selected['Player Full Name'].unique():
    # Generate a random assignment of six characters
    random_assignment = generate_random_string(6)
    # Store the mapping
    name_assignments[name] = random_assignment

# Apply the mappings to the key column in the DataFrame
selected['Key'] = selected['Player Full Name'].map(name_assignments)

# These are all the columns we need
og_columns = ['Player Full Name', 'mins played', 'Team Name', 'Match Name', 'Key', 'Position Tag', 'Yellow Card', 'Red Card', 'Goal', 'Assist',
              'Goal Against', 'Progr Rec', 'Unprogr Rec', 'Forward', 'Unsucc Forward', 'Line Break',
              'Dribble', 'Loss of Poss', 'Success', 'Unsuccess', 'Unprogr Inter', 'Progr Inter', 'Efforts on Goal', 
              'Att 1v1', 'Pass into Oppo Box', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Def Aerial', 'Unsucc Def Aerial', 
              'Tackle', 'Own Box Clear', 'Blocked Shot', 'Blocked Cross', 'Long', 'Opposition']
# These are the columns we need to convert to floats
number_columns = ['mins played', 'Yellow Card', 'Red Card', 'Goal', 'Assist',
              'Goal Against', 'Progr Rec', 'Unprogr Rec', 'Forward', 'Unsucc Forward', 'Line Break',
              'Dribble', 'Loss of Poss', 'Success', 'Unsuccess', 'Unprogr Inter', 'Progr Inter', 'Efforts on Goal', 
              'Att 1v1', 'Pass into Oppo Box', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Def Aerial', 'Unsucc Def Aerial',
              'Tackle', 'Own Box Clear', 'Blocked Shot', 'Blocked Cross', 'Long']
selected = selected.loc[:, og_columns]
selected[number_columns] = selected[number_columns].astype(float)

# Changing positions to fit our positions as a club
selected['Position Tag'] = selected['Position Tag'].str.replace('AM', 'CM')
selected['Position Tag'] = selected['Position Tag'].str.replace('LWB', 'FB')
selected['Position Tag'] = selected['Position Tag'].str.replace('RWB', 'FB')
selected['Position Tag'] = selected['Position Tag'].str.replace('RW', 'Wing')
selected['Position Tag'] = selected['Position Tag'].str.replace('LW', 'Wing')
selected['Position Tag'] = selected['Position Tag'].str.replace('ATT', 'CF')
selected['Position Tag'] = selected['Position Tag'].str.replace('LB', 'FB')
selected['Position Tag'] = selected['Position Tag'].str.replace('RB', 'FB')
selected['Position Tag'] = selected['Position Tag'].str.replace('RCB', 'CB')
selected['Position Tag'] = selected['Position Tag'].str.replace('LCB', 'CB')

# Getting the primary position for each player, this is what we will use for the KPI's down the line
primary_position = selected.groupby(['Player Full Name', 'Position Tag'])['mins played'].sum().reset_index()
primary_position_max = primary_position.groupby('Player Full Name').apply(lambda x: x.loc[x['mins played'].idxmax()]).reset_index(drop=True)

final = selected.groupby(['Player Full Name', 'Match Name', 'Key', 'Opposition']).sum(number_columns)
final.reset_index(level=['Player Full Name', 'Match Name', 'Key', 'Opposition'], inplace=True)

# Filtering out match dates from last season
final['Match Date'] = final['Match Name'].str.extract(r'(\d{4}-\d{2}-\d{2})')
final['Match Date'] = pd.to_datetime(final['Match Date'])
final = final[final['Match Date'] > '2023-07-01']

final = pd.merge(final, primary_position_max[['Player Full Name', 'Position Tag']], how='inner')

# Removing all goalkeepers, we have a seperate goalkeeping report
final = final.loc[final['Position Tag'] != 'GK']

# Finding the most recent date for the highlight in Tableau
latest_dates = final.groupby('Player Full Name')['Match Date'].max()
final = pd.merge(latest_dates, final, on='Player Full Name', how='inner')

# Renaming columns
final.rename(columns={'Match Date_x': 'Most Recent Match',
              'Match Date_y': 'Match Date'}, inplace=True)


# This is a checking step where I make sure the keys remain the same
temp = final[['Player Full Name', 'Key']].drop_duplicates()

# Converting to a csv to use in Tableau
final.to_csv('PlayerDashboardData.csv', index=False)


