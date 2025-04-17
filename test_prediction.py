import os
import json
import logging
from datetime import datetime
from mlb_prediction_api import MLBPredictionAPI
from mlb_stats_api import MLBStatsAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='test_prediction.log')
logger = logging.getLogger('test_prediction')

def clear_all_caches():
    """Clear all cache directories to ensure fresh data"""
    cache_dirs = [
        '/home/ubuntu/final_deploy/cache',
        '/home/ubuntu/final_deploy/cache/mlb_stats',
        '/home/ubuntu/final_deploy/cache/mlb_data',
        '/home/ubuntu/final_deploy/cache/predictions'
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                for file in os.listdir(cache_dir):
                    if file.endswith('.json'):
                        os.remove(os.path.join(cache_dir, file))
                print(f"Cleared cache directory: {cache_dir}")
            except Exception as e:
                print(f"Error clearing cache directory {cache_dir}: {e}")
        else:
            os.makedirs(cache_dir, exist_ok=True)
            print(f"Created cache directory: {cache_dir}")

def test_mlb_stats_api():
    """Test the MLB Stats API integration"""
    print("\nTesting MLB Stats API Integration:")
    print("=" * 100)
    
    # Initialize MLB Stats API
    mlb_stats_api = MLBStatsAPI()
    
    # Force cache refresh for testing
    force_refresh = True
    
    # Test pitcher ERA for multiple teams
    teams_pitchers = [
        ('New York Yankees', 'Gerrit Cole'),
        ('Los Angeles Dodgers', 'Clayton Kershaw'),
        ('Boston Red Sox', 'Chris Sale'),
        ('Houston Astros', 'Justin Verlander'),
        ('New York Mets', 'Max Scherzer'),
        ('Texas Rangers', 'Jacob deGrom'),
        ('Cleveland Guardians', 'Shane Bieber'),
        ('Philadelphia Phillies', 'Zack Wheeler'),
        ('Chicago Cubs', 'Matthew Boyd'),
        ('San Diego Padres', 'Nick Pivetta')
    ]
    
    print(f"{'Pitcher':<20} {'Team':<25} {'ERA':<10} {'Source':<15} {'Method':<15}")
    print("-" * 100)
    
    for team, pitcher in teams_pitchers:
        # Get ERA from MLB Stats API
        era_data = mlb_stats_api.get_pitcher_era(team, pitcher, force_refresh)
        era = era_data.get('era', 'N/A')
        source = era_data.get('source', 'unknown')
        method = era_data.get('method', 'unknown')
        
        # Print results
        print(f"{pitcher:<20} {team:<25} {era:<10} {source:<15} {method:<15}")
    
    print("-" * 100)
    
    # Test getting today's games
    print("\nToday's MLB Games:")
    print("=" * 100)
    
    games_data = mlb_stats_api.get_all_game_data(force_refresh)
    
    if games_data and 'games' in games_data:
        print(f"Found {len(games_data['games'])} games for today")
        
        for i, game in enumerate(games_data['games']):
            home_team = game.get('home_team', {}).get('name', 'Unknown')
            away_team = game.get('away_team', {}).get('name', 'Unknown')
            
            home_pitcher = game.get('home_pitcher', {}).get('name', 'TBD')
            away_pitcher = game.get('away_pitcher', {}).get('name', 'TBD')
            
            home_era = game.get('home_pitcher', {}).get('era', 'N/A')
            away_era = game.get('away_pitcher', {}).get('era', 'N/A')
            
            print(f"Game {i+1}: {away_team} @ {home_team}")
            print(f"  Home Pitcher: {home_pitcher} (ERA: {home_era})")
            print(f"  Away Pitcher: {away_pitcher} (ERA: {away_era})")
            print("-" * 50)
    else:
        print("No games found for today")
    
    print("-" * 100)
    
    return games_data

def test_mlb_prediction_api():
    """Test the MLB Prediction API with real-time data"""
    print("\nTesting MLB Prediction API with Real-Time Data:")
    print("=" * 100)
    
    # Initialize MLB Prediction API
    mlb_prediction_api = MLBPredictionAPI()
    
    # Force cache refresh for testing
    force_refresh = True
    
    # Get all predictions
    predictions = mlb_prediction_api.get_all_predictions(force_refresh)
    
    if predictions and 'games' in predictions:
        print(f"Generated predictions for {len(predictions['games'])} games")
        print(f"Data Source: {predictions['metadata']['data_source']}")
        print(f"Timestamp: {predictions['metadata']['timestamp']}")
        
        for i, game in enumerate(predictions['games']):
            home_team = game.get('home_team', 'Unknown')
            away_team = game.get('away_team', 'Unknown')
            
            home_pitcher = game.get('home_pitcher', 'TBD')
            away_pitcher = game.get('away_pitcher', 'TBD')
            
            home_era = game.get('home_pitcher_era', 'N/A')
            away_era = game.get('away_pitcher_era', 'N/A')
            
            under_1_run = game.get('predictions', {}).get('under_1_run_first_inning', {})
            over_2_5_runs = game.get('predictions', {}).get('over_2_5_runs_first_three_innings', {})
            over_3_5_runs = game.get('predictions', {}).get('over_3_5_runs_first_three_innings', {})
            
            print(f"Game {i+1}: {away_team} @ {home_team}")
            print(f"  Home Pitcher: {home_pitcher} (ERA: {home_era})")
            print(f"  Away Pitcher: {away_pitcher} (ERA: {away_era})")
            print(f"  Under 1 Run 1st Inning: {under_1_run.get('probability', 'N/A'):.1f}% - {under_1_run.get('recommendation', 'N/A')}")
            print(f"  Over 2.5 Runs First 3 Innings: {over_2_5_runs.get('probability', 'N/A'):.1f}% - {over_2_5_runs.get('recommendation', 'N/A')}")
            print(f"  Over 3.5 Runs First 3 Innings: {over_3_5_runs.get('probability', 'N/A'):.1f}% - {over_3_5_runs.get('recommendation', 'N/A')}")
            
            # Verify ERA source in stats comparison
            stats = game.get('stats_comparison', {}).get('pitchers', {})
            home_era_source = stats.get('home', {}).get('era_source', 'N/A')
            away_era_source = stats.get('away', {}).get('era_source', 'N/A')
            
            print(f"  Home ERA Source: {home_era_source}")
            print(f"  Away ERA Source: {away_era_source}")
            print("-" * 50)
    else:
        print("No predictions generated")
    
    print("-" * 100)
    
    return predictions

def save_test_results(mlb_stats_data, prediction_data):
    """Save test results to file for review"""
    test_results = {
        'mlb_stats_data': mlb_stats_data,
        'prediction_data': prediction_data,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("\nTest results saved to test_results.json")

if __name__ == "__main__":
    print("\nClearing all cache directories to ensure fresh data:")
    print("=" * 100)
    clear_all_caches()
    
    # Test MLB Stats API
    mlb_stats_data = test_mlb_stats_api()
    
    # Test MLB Prediction API
    prediction_data = test_mlb_prediction_api()
    
    # Save test results
    save_test_results(mlb_stats_data, prediction_data)
    
    print("\nTesting complete!")
