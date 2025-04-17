import requests
import json
import os
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='test_espn_scraper.log')
logger = logging.getLogger('test_espn_scraper')

def test_espn_direct_scraper():
    """Test the ESPN direct scraper with various pitchers"""
    from espn_direct_scraper import ESPNDirectScraper
    
    scraper = ESPNDirectScraper()
    
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
        ('Milwaukee Brewers', 'Corbin Burnes'),
        ('San Diego Padres', 'Yu Darvish')
    ]
    
    results = []
    
    for team, pitcher in teams_pitchers:
        era_data = scraper.get_pitcher_era(team, pitcher)
        print(f"{pitcher} ({team}): ERA {era_data['era']} (Source: {era_data['source']}, Method: {era_data['method']})")
        
        results.append({
            'name': pitcher,
            'team': team,
            'era': era_data['era'],
            'source': era_data['source'],
            'method': era_data['method']
        })
    
    return results

def test_mlb_prediction_api():
    """Test the MLB prediction API with the new ESPN direct scraper integration"""
    from mlb_prediction_api import MLBDataFetcher
    
    api = MLBDataFetcher()
    
    # Test pitcher stats for multiple teams
    teams_pitchers = [
        ('nyy', 'New York Yankees', 'Gerrit Cole'),
        ('lad', 'Los Angeles Dodgers', 'Clayton Kershaw'),
        ('bos', 'Boston Red Sox', 'Chris Sale'),
        ('hou', 'Houston Astros', 'Justin Verlander'),
        ('nym', 'New York Mets', 'Max Scherzer'),
        ('tex', 'Texas Rangers', 'Jacob deGrom'),
        ('cle', 'Cleveland Guardians', 'Shane Bieber'),
        ('phi', 'Philadelphia Phillies', 'Zack Wheeler'),
        ('mil', 'Milwaukee Brewers', 'Corbin Burnes'),
        ('sd', 'San Diego Padres', 'Yu Darvish')
    ]
    
    results = []
    
    for team_id, team_name, pitcher in teams_pitchers:
        stats = api.get_pitcher_stats(team_id, team_name, pitcher)
        print(f"{pitcher} ({team_name}): ERA {stats['era']} (Sources: {', '.join(stats['sources'])}, Method: {stats.get('era_method', 'unknown')})")
        
        results.append({
            'name': pitcher,
            'team': team_name,
            'era': stats['era'],
            'sources': stats['sources'],
            'method': stats.get('era_method', 'unknown')
        })
    
    return results

def compare_with_espn_app():
    """Compare ERA values with known values from ESPN app"""
    espn_app_values = {
        'Gerrit Cole': 2.63,
        'Clayton Kershaw': 3.21,
        'Chris Sale': 3.84,
        'Justin Verlander': 3.15,
        'Max Scherzer': 3.38,
        'Jacob deGrom': 2.45,
        'Shane Bieber': 3.52,
        'Zack Wheeler': 3.07,
        'Corbin Burnes': 2.94,
        'Yu Darvish': 3.76
    }
    
    # Test direct scraper
    direct_results = test_espn_direct_scraper()
    
    # Test MLB prediction API
    api_results = test_mlb_prediction_api()
    
    # Compare results
    print("\nComparing ERA values with ESPN app:")
    print("=" * 80)
    print(f"{'Pitcher':<20} {'ESPN App':<10} {'Direct Scraper':<15} {'MLB API':<10} {'Match':<10}")
    print("-" * 80)
    
    all_match = True
    
    for pitcher, espn_app_era in espn_app_values.items():
        # Find in direct results
        direct_era = None
        for result in direct_results:
            if result['name'] == pitcher:
                direct_era = result['era']
                break
        
        # Find in API results
        api_era = None
        for result in api_results:
            if result['name'] == pitcher:
                api_era = result['era']
                break
        
        # Check if values match
        direct_match = direct_era == espn_app_era if direct_era is not None else False
        api_match = api_era == espn_app_era if api_era is not None else False
        
        match_status = "✓" if direct_match and api_match else "✗"
        if not (direct_match and api_match):
            all_match = False
        
        print(f"{pitcher:<20} {espn_app_era:<10.2f} {direct_era:<15.2f} {api_era:<10.2f} {match_status:<10}")
    
    print("-" * 80)
    print(f"Overall match: {'✓' if all_match else '✗'}")
    print("=" * 80)
    
    return all_match

if __name__ == "__main__":
    print("\nTesting ESPN Direct Scraper:")
    print("=" * 80)
    test_espn_direct_scraper()
    
    print("\nTesting MLB Prediction API:")
    print("=" * 80)
    test_mlb_prediction_api()
    
    print("\nComparing with ESPN App:")
    print("=" * 80)
    match_result = compare_with_espn_app()
    
    if match_result:
        print("\nSUCCESS: All ERA values match ESPN app!")
    else:
        print("\nWARNING: Some ERA values don't match ESPN app.")
