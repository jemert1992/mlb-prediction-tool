import os
import json
import logging
import time
from datetime import datetime
from espn_direct_scraper import ESPNDirectScraper
from espn_live_data_api import ESPNLiveDataAPI

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='integrated_espn_data_api.log')
logger = logging.getLogger('integrated_espn_data_api')

class IntegratedESPNDataAPI:
    """
    A class that integrates both the ESPN Live Data API and the ESPN Direct Scraper
    to ensure accurate pitcher statistics, especially ERA values.
    """
    
    def __init__(self, cache_dir="/home/ubuntu/final_deploy/cache/integrated_espn"):
        """
        Initialize the Integrated ESPN Data API
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize both data sources
        self.espn_api = ESPNLiveDataAPI()
        self.espn_scraper = ESPNDirectScraper()
        
        # Cache expiration time (15 minutes)
        self.cache_expiration = 15 * 60  # seconds
    
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
    
    def get_todays_games(self, force_refresh=False):
        """
        Get today's MLB games with enhanced data
        
        Args:
            force_refresh: Force refresh of cache
            
        Returns:
            List of today's MLB games with enhanced data
        """
        cache_key = "todays_games_enhanced"
        
        if force_refresh:
            self.clear_cache(cache_key)
        
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Get games from ESPN API
        games = self.espn_api.get_todays_games(force_refresh)
        
        # Enhance each game with accurate pitcher data
        for game in games:
            # Enhance home pitcher data
            if game['home_team'].get('probable_pitcher'):
                home_pitcher = game['home_team']['probable_pitcher']
                home_team_name = game['home_team']['name']
                home_pitcher_name = home_pitcher['name']
                
                # Get accurate ERA from direct scraper
                era_data = self.get_pitcher_era(home_team_name, home_pitcher_name, force_refresh)
                
                if era_data and 'era' in era_data and era_data['era'] != 'N/A':
                    # Update pitcher stats with accurate ERA
                    if 'stats' not in home_pitcher:
                        home_pitcher['stats'] = {}
                    
                    home_pitcher['stats']['era'] = era_data['era']
                    home_pitcher['stats']['era_source'] = era_data['source']
                    home_pitcher['stats']['era_method'] = era_data['method']
            
            # Enhance away pitcher data
            if game['away_team'].get('probable_pitcher'):
                away_pitcher = game['away_team']['probable_pitcher']
                away_team_name = game['away_team']['name']
                away_pitcher_name = away_pitcher['name']
                
                # Get accurate ERA from direct scraper
                era_data = self.get_pitcher_era(away_team_name, away_pitcher_name, force_refresh)
                
                if era_data and 'era' in era_data and era_data['era'] != 'N/A':
                    # Update pitcher stats with accurate ERA
                    if 'stats' not in away_pitcher:
                        away_pitcher['stats'] = {}
                    
                    away_pitcher['stats']['era'] = era_data['era']
                    away_pitcher['stats']['era_source'] = era_data['source']
                    away_pitcher['stats']['era_method'] = era_data['method']
        
        # Save enhanced games to cache
        self.save_to_cache(cache_key, games)
        
        return games
    
    def get_pitcher_era(self, team_name, pitcher_name, force_refresh=False):
        """
        Get pitcher ERA using multiple methods to ensure accuracy
        
        Args:
            team_name: Name of the team
            pitcher_name: Name of the pitcher
            force_refresh: Force refresh of cache
            
        Returns:
            Pitcher ERA data
        """
        cache_key = f"pitcher_era_{team_name}_{pitcher_name}".replace(" ", "_")
        
        if force_refresh:
            self.clear_cache(cache_key)
        
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Try multiple methods to get accurate ERA
        
        # Method 1: Try ESPN Direct Scraper first (most accurate)
        era_data = self.espn_scraper.get_pitcher_era(team_name, pitcher_name)
        
        if era_data and 'era' in era_data and era_data['era'] != 'N/A':
            logger.info(f"Got ERA for {pitcher_name} ({team_name}) from ESPN Direct Scraper: {era_data['era']}")
            self.save_to_cache(cache_key, era_data)
            return era_data
        
        # Method 2: Try ESPN API
        api_era_data = self.espn_api.get_pitcher_era(team_name, pitcher_name, force_refresh)
        
        if api_era_data and 'era' in api_era_data and api_era_data['era'] != 'N/A':
            logger.info(f"Got ERA for {pitcher_name} ({team_name}) from ESPN API: {api_era_data['era']}")
            self.save_to_cache(cache_key, api_era_data)
            return api_era_data
        
        # If we couldn't find the pitcher with either method, return a default value
        default_data = {
            'name': pitcher_name,
            'team': team_name,
            'era': 'N/A',
            'source': 'not-found',
            'method': 'default',
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'note': 'Pitcher not found in ESPN data'
        }
        
        logger.warning(f"Could not find ERA for {pitcher_name} ({team_name})")
        self.save_to_cache(cache_key, default_data)
        
        return default_data
    
    def get_all_game_data(self, force_refresh=False):
        """
        Get all game data including accurate pitcher statistics
        
        Args:
            force_refresh: Force refresh of cache
            
        Returns:
            All game data with accurate pitcher statistics
        """
        cache_key = "all_game_data"
        
        if force_refresh:
            self.clear_cache(cache_key)
        
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Get today's games with enhanced data
        games = self.get_todays_games(force_refresh)
        
        # Add metadata
        result = {
            'games': games,
            'metadata': {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': 'Integrated ESPN Data API',
                'game_count': len(games),
                'data_freshness': 'real-time'
            }
        }
        
        # Save to cache
        self.save_to_cache(cache_key, result)
        
        return result
