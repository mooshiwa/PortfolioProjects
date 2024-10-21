import requests
from bs4 import BeautifulSoup
import pandas as pd

# Headers for the request
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

# Initialize empty list to store player data
all_player_data = []

# Function to extract player information for incoming transfers only
def extract_player_data(team_name, team_div, season_year):
    transfer_table = team_div.find_all('table')

    # Use the first table for incoming transfers (transfer_type = 0)
    if transfer_table and len(transfer_table) >= 2:
        headers = [th.text.strip() for th in transfer_table[0].find('thead').find_all('th')]  # First table is for 'In' transfers
        rows = transfer_table[0].find('tbody').find_all('tr')

        for row in rows:
            # Replace '-' with None (null) in each cell value
            data = [td.text.strip() if td.text.strip() != "-" else None for td in row.find_all('td')]
            player_data = [team_name, 'In', season_year] + data
            all_player_data.append(player_data)

# Iterate through each season from 2000 to 2023
for season_year in range(2000, 2024):
    # URL for both summer and winter transfers
    base_url = f"https://www.transfermarkt.co.uk/premier-league/transfers/wettbewerb/GB1/plus/?saison_id={season_year}&s_w=&leihe=1&intern=0&intern=1"

    # Request the page and set encoding
    pageTree = requests.get(base_url, headers=headers)
    pageTree.encoding = 'utf-8'  # Ensure UTF-8 encoding for the request
    soup = BeautifulSoup(pageTree.content, 'lxml', from_encoding='utf-8')  # Use 'lxml' parser with UTF-8 encoding

    # Extract teams from the page and filter out empty strings
    teams = soup.select('h2.content-box-headline a[href*="/transfers/verein/"]')
    teams_list = [(team.text.strip(), team) for team in teams if team.text.strip()]

    # Iterate through each team and extract player information for incoming transfers only
    for team_name, team_anchor in teams_list:
        
        # Using the previously selected 'team_anchor' directly instead of searching for it again and only process if the URL contains '/transfers/verein/'
        if '/transfers/verein/' in team_anchor['href']:
            team_div = team_anchor.find_parent('div', class_='box')

            # If not found, try finding a different div class (like 'responsive-table')
            if not team_div:
                print(f"Warning: No div with class 'box' found for {team_name}. Trying 'responsive-table'.")
                team_div = team_anchor.find_parent('div', class_='responsive-table')

            # Check if the team_div is found
            if team_div:
                # Extract incoming transfers only (transfer_type=0)
                extract_player_data(team_name, team_div, season_year)
            else:
                print(f"Warning: No div found for {team_name} after searching multiple classes.")

# Create a DataFrame from the collected player data
columns = ['Team', 'Transfer Direction', 'Year', 'Player', 'Age', 'Nationality', 'Position', 'Short Position',
           'Market Value', 'Left Team', 'Left Team Flag', 'Fee']
df = pd.DataFrame(all_player_data, columns=columns)

# Display the DataFrame
print(df)

# Export the DataFrame to a CSV file with UTF-8 encoding, treating None as empty strings in the CSV
df.to_csv('20Years_PL_transfers.csv', index=False, encoding='utf-8')
