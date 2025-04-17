import os
import json
import logging
import shutil
from datetime import datetime
from integrated_espn_data_api import IntegratedESPNDataAPI
from espn_direct_scraper import ESPNDirectScraper
from espn_live_data_api import ESPNLiveDataAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='test_integrated_espn_api.log')
logger = logging.getLogger('test_integrated_espn_api')

def clear_all_caches():
    """Clear all cache directories to ensure fresh data"""
    cache_dirs = [
        '/home/ubuntu/final_deploy/cache',
        '/home/ubuntu/final_deploy/cache/espn',
        '/home/ubuntu/final_deploy/cache/espn_direct',
        '/home/ubuntu/final_deploy/cache/integrated_espn'
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                print(f"Cleared cache directory: {cache_dir}")
            except Exception as e:
                print(f"Error clearing cache directory {cache_dir}: {e}")
        else:
            os.makedirs(cache_dir, exist_ok=True)
            print(f"Created cache directory: {cache_dir}")

def test_integrated_espn_api():
    """Test the integrated ESPN API with various pitchers"""
    
    # Initialize all APIs for comparison
    integrated_api = IntegratedESPNDataAPI()
    direct_scraper = ESPNDirectScraper()
    espn_api = ESPNLiveDataAPI()
    
    # Force cache refresh for testing
    force_refresh = True
    
    # Test pitcher ERA for multiple teams
    teams_pitchers = [
        ('Chicago Cubs', 'Matthew Boyd'),
        ('San Diego Padres', 'Nick Pivetta'),
        ('New York Yankees', 'Gerrit Cole'),
        ('Los Angeles Dodgers', 'Clayton Kershaw'),
        ('Boston Red Sox', 'Chris Sale'),
        ('Houston Astros', 'Justin Verlander'),
        ('New York Mets', 'Max Scherzer'),
        ('Texas Rangers', 'Jacob deGrom'),
        ('Cleveland Guardians', 'Shane Bieber'),
        ('Philadelphia Phillies', 'Zack Wheeler')
    ]
    
    results = []
    
    print("\nTesting Integrated ESPN API vs Direct Scraper vs ESPN API:")
    print("=" * 100)
    print(f"{'Pitcher':<20} {'Team':<25} {'Integrated API':<15} {'Direct Scraper':<15} {'ESPN API':<15} {'Source':<15}")
    print("-" * 100)
    
    for team, pitcher in teams_pitchers:
        # Get ERA from integrated API
        integrated_era_data = integrated_api.get_pitcher_era(team, pitcher, force_refresh)
        integrated_era = integrated_era_data.get('era', 'N/A')
        integrated_source = integrated_era_data.get('source', 'unknown')
        
        # Get ERA from direct scraper
        direct_era_data = direct_scraper.get_pitcher_era(team, pitcher, force_refresh)
        direct_era = direct_era_data.get('era', 'N/A')
        direct_source = direct_era_data.get('source', 'unknown')
        
        # Get ERA from ESPN API
        api_era_data = espn_api.get_pitcher_era(team, pitcher, force_refresh)
        api_era = api_era_data.get('era', 'N/A') if api_era_data else 'N/A'
        
        # Print results
        print(f"{pitcher:<20} {team:<25} {integrated_era:<15} {direct_era:<15} {api_era:<15} {direct_source:<15}")
        
        results.append({
            'name': pitcher,
            'team': team,
            'integrated_era': integrated_era,
            'direct_era': direct_era,
            'api_era': api_era,
            'source': direct_source
        })
    
    print("-" * 100)
    
    # Check if integrated API is using direct scraper values
    direct_match_count = 0
    real_data_count = 0
    
    for result in results:
        if result['integrated_era'] == result['direct_era'] and result['integrated_era'] != 'N/A':
            direct_match_count += 1
        
        if result['source'] != 'espn-hardcoded' and result['source'] != 'not-found' and result['source'] != 'unknown':
            real_data_count += 1
    
    direct_match_percentage = (direct_match_count / len(results)) * 100 if results else 0
    real_data_percentage = (real_data_count / len(results)) * 100 if results else 0
    
    print(f"Integrated API matches Direct Scraper: {direct_match_count}/{len(results)} ({direct_match_percentage:.1f}%)")
    print(f"Real-time data sources: {real_data_count}/{len(results)} ({real_data_percentage:.1f}%)")
    
    return results

def test_todays_games():
    """Test getting today's games with accurate pitcher data"""
    
    integrated_api = IntegratedESPNDataAPI()
    
    # Force cache refresh for testing
    force_refresh = True
    
    # Get today's games
    games = integrated_api.get_todays_games(force_refresh)
    
    print("\nToday's Games with Accurate Pitcher Data:")
    print("=" * 100)
    
    for game in games:
        home_team = game['home_team']['name']
        away_team = game['away_team']['name']
        
        home_pitcher = "TBD"
        home_era = "N/A"
        home_era_source = "N/A"
        
        away_pitcher = "TBD"
        away_era = "N/A"
        away_era_source = "N/A"
        
        if game['home_team'].get('probable_pitcher'):
            home_pitcher = game['home_team']['probable_pitcher']['name']
            if 'stats' in game['home_team']['probable_pitcher']:
                home_era = game['home_team']['probable_pitcher']['stats'].get('era', 'N/A')
                home_era_source = game['home_team']['probable_pitcher']['stats'].get('era_source', 'N/A')
        
        if game['away_team'].get('probable_pitcher'):
            away_pitcher = game['away_team']['probable_pitcher']['name']
            if 'stats' in game['away_team']['probable_pitcher']:
                away_era = game['away_team']['probable_pitcher']['stats'].get('era', 'N/A')
                away_era_source = game['away_team']['probable_pitcher']['stats'].get('era_source', 'N/A')
        
        print(f"{away_team} @ {home_team}")
        print(f"Home Pitcher: {home_pitcher}, ERA: {home_era} (Source: {home_era_source})")
        print(f"Away Pitcher: {away_pitcher}, ERA: {away_era} (Source: {away_era_source})")
        print("-" * 100)
    
    return games

def test_all_game_data():
    """Test getting all game data with accurate pitcher statistics"""
    
    integrated_api = IntegratedESPNDataAPI()
    
    # Force cache refresh for testing
    force_refresh = True
    
    # Get all game data
    all_game_data = integrated_api.get_all_game_data(force_refresh)
    
    print("\nAll Game Data with Accurate Pitcher Statistics:")
    print("=" * 100)
    print(f"Game Count: {all_game_data['metadata']['game_count']}")
    print(f"Data Source: {all_game_data['metadata']['source']}")
    print(f"Timestamp: {all_game_data['metadata']['timestamp']}")
    print("-" * 100)
    
    return all_game_data

if __name__ == "__main__":
    print("\nClearing all cache directories to ensure fresh data:")
    print("=" * 100)
    clear_all_caches()
    
    print("\nTesting Integrated ESPN API:")
    print("=" * 100)
    test_integrated_espn_api()
    
    print("\nTesting Today's Games:")
    print("=" * 100)
    test_todays_games()
    
    print("\nTesting All Game Data:")
    print("=" * 100)
    test_all_game_data()
