import json
from mlb_stats_api import MLBStatsAPI

def test_mlb_schedule_integration():
    """
    Test the MLB schedule integration to ensure it fetches real game data
    """
    print("Testing MLB schedule integration...")
    
    # Initialize MLB Stats API
    api = MLBStatsAPI()
    
    # Test dates
    test_dates = [
        '2025-04-16',  # Today
        '2025-04-17',  # Tomorrow
        '2025-04-18',  # Day after tomorrow
    ]
    
    for date in test_dates:
        print(f"\nFetching games for {date}...")
        
        # Force refresh to ensure we get fresh data
        games = api.get_games_for_date(date, force_refresh=True)
        
        print(f"Found {len(games)} games for {date}")
        
        if games:
            # Print first game details
            game = games[0]
            print(f"Sample game: {game['away_team']['name']} @ {game['home_team']['name']}")
            print(f"Venue: {game['venue']}")
            print(f"Home pitcher: {game['home_team']['probable_pitcher']['name']} (ERA: {game['home_team']['probable_pitcher']['stats']['era']})")
            print(f"Away pitcher: {game['away_team']['probable_pitcher']['name']} (ERA: {game['away_team']['probable_pitcher']['stats']['era']})")
            
            # Save games to file for inspection
            with open(f"games_{date}.json", "w") as f:
                json.dump(games, f, indent=2)
                print(f"Saved games to games_{date}.json")
        else:
            print(f"No games found for {date}")

if __name__ == "__main__":
    test_mlb_schedule_integration()
