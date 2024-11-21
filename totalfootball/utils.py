# The following file contains the code that makes the initial API requests to Rapid API
# It also provides a functionality such that the user can reset the draft

import requests
import time
from django.db import transaction
from .models import Player, LeagueTeam, League, DraftPick, Team

API_URL = "https://api-football-v1.p.rapidapi.com/v3"
API_KEY = "9f340e84c7msh3a8fcf6665f37f2p134bc1jsn68c53749acd7"

HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY,
}

# The following function ensures that we space out requests to make sure there isn't an overload. 
def fetch_with_rate_limit(url, headers, params):
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 429:  # Rate limit exceeded error
            print("Rate limit exceeded. Retrying after delay...")
            time.sleep(60)  # Wait for 60 seconds as a kind of pause
        elif response.status_code == 200:
            return response
        else:
            response.raise_for_status()

# Safely obtain a player statistic and return the default if None or missing.

def safe_stat_value(stat, default=0):
    return stat if stat is not None else default

# Obtains 36 of the best performing players from each of the top 5 leagues in Europe.
# To ensure that there are enough players of each position, we balance out the number of players picked at each position. 
def fetch_balanced_top_36():
    # Example league id for La Liga (Spanish soccer league)
    league_id = 140  
    season = "2024"
    players_by_position = {"Goalkeeper": [], "Defender": [], "Midfielder": [], "Attacker": []}
    page = 1

    while True:
        url = f"{API_URL}/players"
        params = {"league": league_id, "season": season, "page": page}

        # Fetch data with rate limit
        response = fetch_with_rate_limit(url, HEADERS, params)
        data = response.json()

        # Iterate through players
        for player_data in data.get("response", []):
            try:
                stats = player_data["statistics"][0]
                position = stats["games"]["position"]

                # The following computes each player's score based on position-specific weights
                if position == "Goalkeeper":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.1 +
                        safe_stat_value(stats["goals"]["saves"]) * 0.5 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.15 +
                        safe_stat_value(stats["duels"]["won"]) * 0.25
                    )
                elif position == "Defender":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.15 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.3 +
                        safe_stat_value(stats["tackles"]["interceptions"]) * 0.3 +
                        safe_stat_value(stats["tackles"]["blocks"]) * 0.15 +
                        safe_stat_value(stats["goals"]["assists"]) * 0.1
                    )
                elif position == "Midfielder":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.15 +
                        safe_stat_value(stats["goals"]["total"]) * 0.25 +
                        safe_stat_value(stats["goals"]["assists"]) * 0.35 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.15 +
                        safe_stat_value(stats["tackles"]["interceptions"]) * 0.1
                    )
                elif position == "Attacker":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.15 +
                        safe_stat_value(stats["goals"]["total"]) * 0.45 +
                        safe_stat_value(stats["goals"]["assists"]) * 0.2 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.1 +
                        safe_stat_value(stats["tackles"]["interceptions"]) * 0.1
                    )
                else:
                    continue

                players_by_position[position].append({
                    "name": player_data["player"]["name"],
                    "team": stats["team"]["name"],
                    "league": stats["league"]["name"],
                    "position": position,
                    "goals": safe_stat_value(stats["goals"]["total"]),
                    "assists": safe_stat_value(stats["goals"]["assists"]),
                    "tackles": safe_stat_value(stats["tackles"]["total"]) + safe_stat_value(stats["tackles"]["interceptions"]) + safe_stat_value(stats["tackles"]["blocks"]),
                    "saves": safe_stat_value(stats["goals"]["saves"]),
                    "duels": safe_stat_value(stats["duels"]["won"]),
                    "api_football_id": player_data["player"]["id"],
                    "stats": stats,
                    "score": score,
                })
            except KeyError:
                continue

        # Check if there are more pages
        if page >= data["paging"]["total"]:
            break
        page += 1

        # Add a delay between requests to ensure rate limit compliance
        time.sleep(2)  # 2 seconds per request to meet 30 requests per minute

    # Sort players by score within each position
    for position in players_by_position:
        players_by_position[position] = sorted(
            players_by_position[position], key=lambda x: x["score"], reverse=True
        )

    # Select the top players at each position (3 Goalkeepers, 4 Defenders, 5 Midfielders, 3 Attackers)
    selected_players = (
        players_by_position["Goalkeeper"][:5] +
        players_by_position["Defender"][:10] +
        players_by_position["Midfielder"][:12] +
        players_by_position["Attacker"][:9]
    )

    # Save players to the database using transaction library
    with transaction.atomic():
        for player in selected_players:
            Player.objects.update_or_create(
                api_football_id=player["api_football_id"],
                defaults={
                    "name": player["name"],
                    "team": player["team"],
                    "league": player["league"],
                    "position": player["position"],
                    "goals": player["goals"],
                    "assists": player["assists"],
                    "tackles": player["tackles"],
                    "saves": player["saves"],
                    "duels": player["duels"],
                    "price": 0,  # Set default price or calculate dynamically
                    "points": 0,  # Initialized to 0 because we have not obtained data from any live games yet
                    "past_points": int(player["score"]),  # Historical points (from previous soccer games)
                    "team_api_id": player["stats"]["team"]["id"],
                    "league_api_id": player["stats"]["league"]["id"],
                }
            )

    print("Top 36 balanced players saved successfully!")

# Resets the draft process if necessary
def reset_draft(league_id):
    """
    Resets the draft for a specific league.
    """
    try:
        # Fetch the league
        league = League.objects.get(id=league_id)

        # Remove all draft picks
        DraftPick.objects.filter(league=league).delete()

        # Clear all players from LeagueTeams in the league
        league_teams = LeagueTeam.objects.filter(league=league)
        for league_team in league_teams:
            league_team.players.clear()
            league_team.captain = None
            league_team.save()

        # Reset league draft 
        league.draft_started = False
        league.current_pick = 1
        league.round_number = 1
        league.save()

        print(f"Draft for league '{league.name}' has been reset.")
    except League.DoesNotExist:
        # In the case that we gave a wrong league id
        print("League not found.")

