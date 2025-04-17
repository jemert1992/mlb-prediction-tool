import os
import json
import logging
import time
from datetime import datetime
from mlb_stats_api import MLBStatsAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='mlb_data_fetcher.log')
logger = logging.getLogger('mlb_data_fetcher')

class MLBDataFetcher:
    """
    A class to fetch MLB data from various sources with real-time accuracy
    """
    
    def __init__(self, cache_dir="/home/ubuntu/final_deploy/cache/mlb_data"):
        """
        Initialize the MLB data fetcher
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize MLB Stats API
        self.mlb_stats_api = MLBStatsAPI()
        
        # Cache expiration time (15 minutes)
        self.cache_expiration = 15 * 60  # seconds
        
        # Last refresh time
        self.last_refresh_time = 0
    
    def get_cached_data(self, cache_key):
        """
        Get data from cache if it exists and is not expired
        
        Args:
            cache_key: Key to identify the cache file
            
        Returns:
            Cached data if it exists and is not expired, None otherwise
        """
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Check if cache is expired
            file_modified_time = os.path.getmtime(cache_file)
            current_time = time.time()
            
            if current_time - file_modified_time < self.cache_expiration:
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        logger.info(f"Using cached data for {cache_key}")
                        return data
                except Exception as e:
                    logger.error(f"Error reading cache file: {e}")
            else:
                logger.info(f"Cache expired for {cache_key}")
        
        return None
    
    def save_to_cache(self, cache_key, data):
        """
        Save data to cache
        
        Args:
            cache_key: Key to identify the cache file
            data: Data to save
        """
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
                logger.info(f"Saved data to cache for {cache_key}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def clear_cache(self, cache_key=None):
        """
        Clear cache for a specific key or all cache
        
        Args:
            cache_key: Key to identify the cache file, or None to clear all cache
        """
        if cache_key:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    logger.info(f"Cleared cache for {cache_key}")
                except Exception as e:
                    logger.error(f"Error clearing cache for {cache_key}: {e}")
        else:
            try:
                for file in os.listdir(self.cache_dir):
                    if file.endswith('.json'):
                        os.remove(os.path.join(self.cache_dir, file))
                logger.info("Cleared all cache")
            except Exception as e:
                logger.error(f"Error clearing all cache: {e}")
    
    def refresh_data_if_needed(self, force_refresh=False):
        """
        Refresh data if needed or forced
        
        Args:
            force_refresh: Force refresh of data
            
        Returns:
            True if data was refreshed, False otherwise
        """
        current_time = time.time()
        
        # Refresh if forced or if last refresh was more than 15 minutes ago
        if force_refresh or current_time - self.last_refresh_time > self.cache_expiration:
            logger.info("Refreshing MLB data")
            
            # Clear all cache
            self.clear_cache()
            
            # Clear MLB Stats API cache
            self.mlb_stats_api.clear_cache()
            
            # Update last refresh time
            self.last_refresh_time = current_time
            
            return True
        
        return False
    
    def get_pitcher_era(self, team_name, pitcher_name, force_refresh=False):
        """
        Get pitcher ERA from MLB Stats API
        
        Args:
            team_name: Name of the team
            pitcher_name: Name of the pitcher
            force_refresh: Force refresh of data
            
        Returns:
            Pitcher ERA data
        """
        # Refresh data if needed
        self.refresh_data_if_needed(force_refresh)
        
        # Get pitcher ERA from MLB Stats API
        era_data = self.mlb_stats_api.get_pitcher_era(team_name, pitcher_name, force_refresh)
        
        return era_data
    
    def get_todays_games(self, force_refresh=False):
        """
        Get today's MLB games with accurate pitcher data
        
        Args:
            force_refresh: Force refresh of data
            
        Returns:
            List of today's MLB games with accurate pitcher data
        """
        # Refresh data if needed
        self.refresh_data_if_needed(force_refresh)
        
        # Get all game data from MLB Stats API
        all_game_data = self.mlb_stats_api.get_all_game_data(force_refresh)
        
        if not all_game_data or 'games' not in all_game_data:
            logger.error("No game data found")
            return []
        
        # Transform the data into the format expected by the prediction tool
        transformed_games = []
        
        for game in all_game_data['games']:
            # Create a transformed game object
            transformed_game = {
                'id': game.get('id'),
                'date': game.get('date'),
                'time': game.get('time'),
                'venue': game.get('venue'),
                'home_team': {
                    'name': game.get('home_team', {}).get('name'),
                    'abbreviation': game.get('home_team', {}).get('abbreviation'),
                    'display_name': game.get('home_team', {}).get('display_name'),
                    'logo': game.get('home_team', {}).get('logo'),
                    'probable_pitcher': {
                        'name': game.get('home_pitcher', {}).get('name'),
                        'stats': {
                            'era': game.get('home_pitcher', {}).get('era'),
                            'whip': game.get('home_pitcher', {}).get('whip'),
                            'strikeouts': game.get('home_pitcher', {}).get('strikeouts'),
                            'innings_pitched': game.get('home_pitcher', {}).get('innings_pitched'),
                            'era_source': 'MLB Stats API',
                            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                },
                'away_team': {
                    'name': game.get('away_team', {}).get('name'),
                    'abbreviation': game.get('away_team', {}).get('abbreviation'),
                    'display_name': game.get('away_team', {}).get('display_name'),
                    'logo': game.get('away_team', {}).get('logo'),
                    'probable_pitcher': {
                        'name': game.get('away_pitcher', {}).get('name'),
                        'stats': {
                            'era': game.get('away_pitcher', {}).get('era'),
                            'whip': game.get('away_pitcher', {}).get('whip'),
                            'strikeouts': game.get('away_pitcher', {}).get('strikeouts'),
                            'innings_pitched': game.get('away_pitcher', {}).get('innings_pitched'),
                            'era_source': 'MLB Stats API',
                            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                },
                'weather': game.get('weather', {}),
                'ballpark_factor': game.get('ballpark_factor', 1.0)
            }
            
            transformed_games.append(transformed_game)
        
        return transformed_games
    
    def get_all_game_data(self, force_refresh=False):
        """
        Get all game data including accurate pitcher statistics
        
        Args:
            force_refresh: Force refresh of data
            
        Returns:
            All game data with accurate pitcher statistics
        """
        # Refresh data if needed
        self.refresh_data_if_needed(force_refresh)
        
        # Get all game data from MLB Stats API
        all_game_data = self.mlb_stats_api.get_all_game_data(force_refresh)
        
        # Add metadata
        result = {
            'games': self.get_todays_games(force_refresh),
            'metadata': {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': 'MLB Data Fetcher with MLB Stats API',
                'game_count': len(all_game_data.get('games', [])),
                'data_freshness': 'real-time',
                'last_refresh': datetime.fromtimestamp(self.last_refresh_time).strftime("%Y-%m-%d %H:%M:%S") if self.last_refresh_time > 0 else 'Never'
            }
        }
        
        return result
