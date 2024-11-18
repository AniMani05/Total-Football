import requests

# Your API key
# api_key = 'f718776270mshdd18e7b443cbdc3p18da49jsn5614850c11a8'
api_key = '9f340e84c7msh3a8fcf6665f37f2p134bc1jsn68c53749acd7'

# Headers
headers = {
    'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
    'x-rapidapi-key': api_key
}

# API endpoint
# url = 'https://api-football-v1.p.rapidapi.com/v3/players/topscorers'

# # Parameters
# params = {
#     'league': '39',  # Premier League
#     'season': '2023'
# }

# # Make the request
# response = requests.get(url, headers=headers, params=params)

# # Check for successful response
# if response.status_code == 200:
#     data = response.json()
#     for player in data['response']:
#         print(f"{player['player']['name']} - {player['statistics'][0]['goals']['total']} goals")
# else:
#     print(f"Error: {response.status_code} - {response.text}")

# url = 'https://api-football-v1.p.rapidapi.com/v3/players'
# params = {
#     'id': 302,  # Example: Marcus Rashford's API ID
#     'season': '2023'
# }
# response = requests.get(url, headers=headers, params=params)

# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Error: {response.status_code} - {response.text}")


def find_player_stats(team_id, league_id, player_name, season="2024"):
    """
    Search for a player's API-Football ID in a specific team and league and retrieve their stats.
    """
    page = 1
    while True:
        url = "https://api-football-v1.p.rapidapi.com/v3/players"
        params = {
            "team": team_id,
            "league": league_id,
            "season": season,
            "page": page,
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        for player in data.get("response", []):
            if player["player"]["name"].lower() == player_name.lower():
                # Fetch player statistics
                player_id = player["player"]["id"]
                print(f"Found {player_name} with API ID: {player_id}")
                return {
                    "id": player_id,
                    "name": player["player"]["name"],
                    "stats": player["statistics"]
                }

        # Check if there are more pages
        if page >= data["paging"]["total"]:
            break
        page += 1

    print(f"No match found for player: {player_name}")
    return None

# Example usage
team_id = 33  # Manchester United (First Team)
league_id = 39  # Premier League
player_name = "A. Onana"
player_data = find_player_stats(team_id, league_id, player_name)

if player_data:
    print(f"Player: {player_data['name']}")
    print("Statistics:")
    for stat in player_data["stats"]:
        print(stat)

