import requests
import json
import os
import re
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup

class MLBStatsDirectAPI:
    """
    Class to fetch real MLB statistics directly from MLB.com's Stats API
    """
    
    def __init__(self):
        """Initialize the MLB Stats Direct API client"""
        self.base_url = "https://statsapi.mlb.com/api"
        self.cache_dir = 'cache/mlb_direct'
        self.cache_expiry = 3600 * 3  # Cache expiry in seconds (3 hours)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cached_data(self, cache_key):
        """Get data from cache if available and not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is expired
                cache_time = cached_data.get('cache_time', 0)
                if (datetime.now() - datetime.fromtimestamp(cache_time)).total_seconds() < self.cache_expiry:
                    return cached_data.get('data')
            except Exception as e:
                print(f"Error reading MLB direct cache: {e}")
        
        return None
    
    def save_to_cache(self, cache_key, data):
        """Save data to cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'data': data,
                    'cache_time': datetime.now().timestamp()
                }, f)
            
            return True
        except Exception as e:
            print(f"Error saving MLB direct data to cache: {e}")
            return False
    
    def get_team_id(self, team_name):
        """
        Get MLB team ID from team name
        """
        team_map = {
            'Arizona Diamondbacks': 109,
            'Atlanta Braves': 144,
            'Baltimore Orioles': 110,
            'Boston Red Sox': 111,
            'Chicago Cubs': 112,
            'Chicago White Sox': 145,
            'Cincinnati Reds': 113,
            'Cleveland Guardians': 114,
            'Colorado Rockies': 115,
            'Detroit Tigers': 116,
            'Houston Astros': 117,
            'Kansas City Royals': 118,
            'Los Angeles Angels': 108,
            'Los Angeles Dodgers': 119,
            'Miami Marlins': 146,
            'Milwaukee Brewers': 158,
            'Minnesota Twins': 142,
            'New York Mets': 121,
            'New York Yankees': 147,
            'Oakland Athletics': 133,
            'Philadelphia Phillies': 143,
            'Pittsburgh Pirates': 134,
            'San Diego Padres': 135,
            'Seattle Mariners': 136,
            'San Francisco Giants': 137,
            'St. Louis Cardinals': 138,
            'Tampa Bay Rays': 139,
            'Texas Rangers': 140,
            'Toronto Blue Jays': 141,
            'Washington Nationals': 120
        }
        
        # Try exact match first
        if team_name in team_map:
            return team_map[team_name]
        
        # Try partial match
        for full_name, team_id in team_map.items():
            if team_name in full_name:
                return team_id
        
        # Return default if no match
        return None
    
    def get_team_roster(self, team_name):
        """
        Get team roster from MLB Stats API
        """
        team_id = self.get_team_id(team_name)
        if not team_id:
            print(f"Team ID not found for {team_name}")
            return []
        
        cache_key = f"mlb_direct_roster_{team_id}"
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/v1/teams/{team_id}/roster"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Error fetching team roster: {response.status_code}")
                return []
            
            data = response.json()
            roster = data.get('roster', [])
            
            # Filter for pitchers
            pitchers = [player for player in roster if player.get('position', {}).get('code') == 'P']
            
            # Save to cache
            self.save_to_cache(cache_key, pitchers)
            
            return pitchers
        except Exception as e:
            print(f"Error fetching team roster: {e}")
            return []
    
    def get_pitcher_stats(self, team_name, pitcher_name):
        """
        Get pitcher statistics from MLB Stats API
        """
        cache_key = f"mlb_direct_pitcher_{team_name}_{pitcher_name}".replace(" ", "_")
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Get team roster
            roster = self.get_team_roster(team_name)
            
            # Find pitcher in roster
            pitcher_id = None
            for player in roster:
                if pitcher_name.lower() in player.get('person', {}).get('fullName', '').lower():
                    pitcher_id = player.get('person', {}).get('id')
                    break
            
            if not pitcher_id:
                print(f"Pitcher {pitcher_name} not found in {team_name} roster")
                return {
                    "era": 4.50,
                    "whip": 1.30,
                    "strikeouts": 0,
                    "innings": 0,
                    "source": "default"
                }
            
            # Get pitcher stats
            url = f"{self.base_url}/v1/people/{pitcher_id}/stats?stats=season&group=pitching"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Error fetching pitcher stats: {response.status_code}")
                return {
                    "era": 4.50,
                    "whip": 1.30,
                    "strikeouts": 0,
                    "innings": 0,
                    "source": "default"
                }
            
            data = response.json()
            stats_groups = data.get('stats', [])
            
            # Default values
            era = 4.50
            whip = 1.30
            strikeouts = 0
            innings = 0
            
            # Extract stats
            for group in stats_groups:
                if group.get('group', {}).get('displayName') == 'pitching':
                    stats = group.get('splits', [])
                    if stats:
                        stat = stats[0].get('stat', {})
                        era = stat.get('era', 4.50)
                        whip = stat.get('whip', 1.30)
                        strikeouts = stat.get('strikeOuts', 0)
                        innings = stat.get('inningsPitched', 0)
                        
                        # Convert innings from string to float if needed
                        if isinstance(innings, str):
                            try:
                                innings = float(innings)
                            except ValueError:
                                innings = 0
            
            result = {
                "era": era,
                "whip": whip,
                "strikeouts": strikeouts,
                "innings": innings,
                "source": "mlb-direct",
                "player_id": pitcher_id
            }
            
            # Save to cache
            self.save_to_cache(cache_key, result)
            
            return result
        except Exception as e:
            print(f"Error fetching pitcher stats: {e}")
            return {
                "era": 4.50,
                "whip": 1.30,
                "strikeouts": 0,
                "innings": 0,
                "source": "default"
            }

class MultiSourceStatsAPI:
    """
    Class that combines multiple data sources to ensure accurate MLB statistics
    """
    
    def __init__(self):
        """Initialize the multi-source stats API"""
        # Import here to avoid circular imports
        from baseball_reference_api import BaseballReferenceAPI
        
        self.mlb_direct_api = MLBStatsDirectAPI()
        self.bbref_api = BaseballReferenceAPI()
        self.cache_dir = 'cache/multi_source'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_pitcher_stats(self, team_name, pitcher_name):
        """
        Get pitcher statistics from multiple sources
        
        Strategy:
        1. Try MLB.com's direct API first (most authoritative)
        2. Fall back to Baseball Reference if needed
        3. Use default values only as a last resort
        """
        cache_key = f"multi_source_pitcher_{team_name}_{pitcher_name}".replace(" ", "_")
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Check if cached data exists and is recent
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Use cached data if it's from today
                cache_date = datetime.fromtimestamp(cached_data.get('timestamp', 0))
                if cache_date.date() == datetime.now().date():
                    print(f"Using cached multi-source data for {pitcher_name}")
                    return cached_data.get('stats', {})
            except Exception as e:
                print(f"Error reading multi-source cache: {e}")
        
        # Try MLB direct API first
        mlb_stats = self.mlb_direct_api.get_pitcher_stats(team_name, pitcher_name)
        
        # If MLB direct API returned real data, use it
        if mlb_stats.get('source') != 'default':
            result = mlb_stats
            print(f"Using MLB direct data for {pitcher_name}")
        else:
            # Try Baseball Reference as fallback
            bbref_team_abbr = self.bbref_api.get_team_abbreviation(team_name)
            bbref_stats = self.bbref_api.scrape_pitcher_stats(bbref_team_abbr, pitcher_name)
            
            # If Baseball Reference returned real data, use it
            if bbref_stats.get('source') != 'default':
                result = bbref_stats
                print(f"Using Baseball Reference data for {pitcher_name}")
            else:
                # Use default values as last resort
                result = {
                    "era": 4.50,
                    "whip": 1.30,
                    "strikeouts": 0,
                    "innings": 0,
                    "source": "default"
                }
                print(f"Using default data for {pitcher_name}")
        
        # Add metadata
        result['name'] = pitcher_name
        result['team'] = team_name
        result['timestamp'] = datetime.now().timestamp()
        
        # Save to cache
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'stats': result,
                    'timestamp': datetime.now().timestamp()
                }, f)
            print(f"Saved multi-source data to cache for {pitcher_name}")
        except Exception as e:
            print(f"Error saving multi-source data to cache: {e}")
        
        return result

# Test the multi-source stats API
if __name__ == "__main__":
    multi_api = MultiSourceStatsAPI()
    
    # Test pitcher stats for multiple teams
    teams_pitchers = [
        ('New York Yankees', 'Gerrit Cole'),
        ('Los Angeles Dodgers', 'Clayton Kershaw'),
        ('Boston Red Sox', 'Chris Sale'),
        ('Houston Astros', 'Justin Verlander')
    ]
    
    for team, pitcher in teams_pitchers:
        stats = multi_api.get_pitcher_stats(team, pitcher)
        print(f"{pitcher} ({team}): ERA {stats['era']}, WHIP {stats['whip']}, SO {stats['strikeouts']} (Source: {stats['source']})")
