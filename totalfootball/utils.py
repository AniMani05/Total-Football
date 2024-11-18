import requests
import time
from django.db import transaction
from .models import Player

API_URL = "https://api-football-v1.p.rapidapi.com/v3"
API_KEY = "9f340e84c7msh3a8fcf6665f37f2p134bc1jsn68c53749acd7"

HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY,
}

def fetch_with_rate_limit(url, headers, params):
    """
    Fetch data from the API with rate-limit handling.
    """
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 429:  # Rate limit exceeded
            print("Rate limit exceeded. Retrying after delay...")
            time.sleep(60)  # Wait for 60 seconds
        elif response.status_code == 200:
            return response
        else:
            response.raise_for_status()


def safe_stat_value(stat, default=0):
    """
    Safely retrieve a stat value, returning the default if None or missing.
    """
    return stat if stat is not None else default


def fetch_balanced_top_36():
    """
    Fetch and save 36 balanced players (5 Goalkeepers, 10 Defenders, 12 Midfielders, 9 Attackers)
    """
    league_id = 78  # Premier League
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

                # Calculate score based on position-specific weights
                if position == "Goalkeeper":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.4 +
                        safe_stat_value(stats["goals"]["saves"]) * 0.4 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.2
                    )
                elif position == "Defender":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.3 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.25 +
                        safe_stat_value(stats["tackles"]["interceptions"]) * 0.25 +
                        safe_stat_value(stats["tackles"]["blocks"]) * 0.1 +
                        safe_stat_value(stats["goals"]["assists"]) * 0.1
                    )
                elif position == "Midfielder":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.25 +
                        safe_stat_value(stats["goals"]["total"]) * 0.25 +
                        safe_stat_value(stats["goals"]["assists"]) * 0.25 +
                        safe_stat_value(stats["tackles"]["total"]) * 0.15 +
                        safe_stat_value(stats["tackles"]["interceptions"]) * 0.1
                    )
                elif position == "Attacker":
                    score = (
                        safe_stat_value(stats["games"]["minutes"]) * 0.2 +
                        safe_stat_value(stats["goals"]["total"]) * 0.4 +
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
    # for position in players_by_position:
    #     players_by_position[position] = sorted(
    #         players_by_position[position], key=lambda x: x["score"], reverse=True
    #     )
    for position in players_by_position:
        players_by_position[position] = sorted(
            players_by_position[position], key=lambda x: x["score"], reverse=True
        )
        print(f"\nTop players for position {position}:")
        for player in players_by_position[position]:
            print(f"  {player['name']} - Score: {player['score']:.2f}")

    # Select the top players (3 Goalkeepers, 4 Defenders, 5 Midfielders, 3 Attackers)
    selected_players = (
        players_by_position["Goalkeeper"][:5] +
        players_by_position["Defender"][:10] +
        players_by_position["Midfielder"][:12] +
        players_by_position["Attacker"][:9]
    )

    # Save players to the database
    with transaction.atomic():
        for player in selected_players:
            Player.objects.update_or_create(
                api_football_id=player["api_football_id"],
                defaults={
                    "name": player["name"],
                    "team": player["team"],
                    "league": player["league"],
                    "position": player["position"],
                    "price": 0,  # Set default price or calculate dynamically
                    "points": int(player["score"]),  # Save the calculated score
                    "past_points": 0,  # Historical points (if needed)
                    "team_api_id": player["stats"]["team"]["id"],
                    "league_api_id": player["stats"]["league"]["id"],
                }
            )

    print("Top 36 balanced players saved successfully!")
    print("\nSelected Players:")
    for player in selected_players:
        print(f"{player['name']} - {player['position']} - Score: {player['score']:.2f}")
