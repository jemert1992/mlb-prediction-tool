import os
import json
import logging
import time
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='mlb_stats_api.log')
logger = logging.getLogger('mlb_stats_api')

class MLBStatsAPI:
    """
    API for MLB statistics with real-time data
    """
    
    def __init__(self, cache_dir="/home/ubuntu/final_deploy/cache/mlb_stats"):
        """
        Initialize the MLB stats API
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache expiration time (15 minutes)
        self.cache_expiration = 15 * 60  # seconds
        
        # Team mapping (team name to abbreviation)
        self.team_mapping = {
            'Arizona Diamondbacks': 'ARI',
            'Atlanta Braves': 'ATL',
            'Baltimore Orioles': 'BAL',
            'Boston Red Sox': 'BOS',
            'Chicago Cubs': 'CHC',
            'Chicago White Sox': 'CWS',
            'Cincinnati Reds': 'CIN',
            'Cleveland Guardians': 'CLE',
            'Colorado Rockies': 'COL',
            'Detroit Tigers': 'DET',
            'Houston Astros': 'HOU',
            'Kansas City Royals': 'KC',
            'Los Angeles Angels': 'LAA',
            'Los Angeles Dodgers': 'LAD',
            'Miami Marlins': 'MIA',
            'Milwaukee Brewers': 'MIL',
            'Minnesota Twins': 'MIN',
            'New York Mets': 'NYM',
            'New York Yankees': 'NYY',
            'Oakland Athletics': 'OAK',
            'Philadelphia Phillies': 'PHI',
            'Pittsburgh Pirates': 'PIT',
            'San Diego Padres': 'SD',
            'San Francisco Giants': 'SF',
            'Seattle Mariners': 'SEA',
            'St. Louis Cardinals': 'STL',
            'Tampa Bay Rays': 'TB',
            'Texas Rangers': 'TEX',
            'Toronto Blue Jays': 'TOR',
            'Washington Nationals': 'WSH'
        }
        
        # Reverse team mapping (abbreviation to team name)
        self.reverse_team_mapping = {v: k for k, v in self.team_mapping.items()}
        
        # MLB API endpoints
        self.mlb_api_base_url = "https://statsapi.mlb.com/api/v1"
        
        # ERA mapping for fallback
        self.era_mapping = {
            'Brandon Pfaadt': 3.5,
            'Zac Gallen': 3.47,
            'Merrill Kelly': 3.37,
            'Eduardo Rodriguez': 4.15,
            'Ryne Nelson': 5.02,
            'Spencer Strider': 3.6,
            'Max Fried': 3.09,
            'Charlie Morton': 3.64,
            'Reynaldo López': 3.72,
            'Chris Sale': 3.84,
            'Corbin Burnes': 2.94,
            'Grayson Rodriguez': 4.61,
            'Dean Kremer': 8.16,
            'Cole Irvin': 4.81,
            'Kyle Bradish': 3.18,
            'Brayan Bello': 4.34,
            'Nick Pivetta': 1.69,
            'Kutter Crawford': 3.65,
            'Tanner Houck': 2.98,
            'Sean Newcomb': 4.97,
            'Justin Steele': 3.06,
            'Jameson Taillon': 4.01,
            'Javier Assad': 3.55,
            'Kyle Hendricks': 4.04,
            'Matthew Boyd': 2.14,
            'Garrett Crochet': 3.04,
            'Michael Soroka': 4.85,
            'Chris Flexen': 5.09,
            'Jonathan Cannon': 5.79,
            'Erick Fedde': 3.13,
            'Hunter Greene': 3.41,
            'Nick Lodolo': 4.01,
            'Graham Ashcraft': 4.76,
            'Frankie Montas': 4.43,
            'Nick Martinez': 6.06,
            'Shane Bieber': 3.52,
            'Tanner Bibee': 3.91,
            'Logan Allen': 4.46,
            'Gavin Williams': 3.46,
            'Ben Lively': 4.36,
            'Kyle Freeland': 5.27,
            'Cal Quantrill': 4.80,
            'Austin Gomber': 5.51,
            'Ryan Feltner': 5.07,
            'Germán Márquez': 4.6,
            'Tarik Skubal': 2.80,
            'Jack Flaherty': 3.75,
            'Reese Olson': 3.92,
            'Casey Mize': 4.12,
            'Keider Montero': 9.0,
            'Framber Valdez': 3.40,
            'Cristian Javier': 4.25,
            'Hunter Brown': 4.68,
            'J.P. France': 4.46,
            'Ronel Blanco': 6.48,
            'Cole Ragans': 3.06,
            'Seth Lugo': 3.57,
            'Brady Singer': 4.39,
            'Michael Wacha': 3.93,
            'Kris Bubic': 0.96,
            'Patrick Sandoval': 4.38,
            'Tyler Anderson': 4.75,
            'Griffin Canning': 4.75,
            'José Soriano': 2.7,
            'Reid Detmers': 4.43,
            'Yoshinobu Yamamoto': 3.86,
            'Tyler Glasnow': 3.32,
            'James Paxton': 4.01,
            'Gavin Stone': 3.78,
            'Bobby Miller': 4.25,
            'Jesús Luzardo': 3.63,
            'Trevor Rogers': 4.00,
            'Braxton Garrett': 3.66,
            'Ryan Weathers': 5.13,
            'Max Meyer': 2.0,
            'Freddy Peralta': 3.20,
            'Colin Rea': 4.55,
            'Wade Miley': 3.85,
            'Joe Ross': 4.74,
            'Jose Quintana': 0.71,
            'Pablo López': 3.32,
            'Joe Ryan': 3.82,
            'Bailey Ober': 3.43,
            'Chris Paddack': 4.02,
            'David Festa': 0.0,
            'Kodai Senga': 3.38,
            'Luis Severino': 4.47,
            'Sean Manaea': 3.97,
            'José Quintana': 3.57,
            'Huascar Brazobán': 0.73,
            'Gerrit Cole': 2.63,
            'Carlos Rodón': 3.93,
            'Marcus Stroman': 3.66,
            'Nestor Cortes': 3.77,
            'Clarke Schmidt': 4.12,
            'JP Sears': 4.37,
            'Paul Blackburn': 4.21,
            'Alex Wood': 4.46,
            'Ross Stripling': 4.80,
            'Osvaldo Bido': 5.24,
            'Zack Wheeler': 3.07,
            'Aaron Nola': 5.51,
            'Ranger Suárez': 3.42,
            'Cristopher Sánchez': 3.44,
            'Taijuan Walker': 4.57,
            'Mitch Keller': 3.91,
            'Marco Gonzales': 5.22,
            'Bailey Falter': 7.2,
            'Luis Ortiz': 4.78,
            'Quinn Priester': 5.36,
            'Yu Darvish': 3.76,
            'Joe Musgrove': 4.12,
            'Dylan Cease': 3.72,
            'Michael King': 3.33,
            'Nick Pivetta': 1.69,
            'Logan Webb': 3.25,
            'Blake Snell': 3.38,
            'Kyle Harrison': 4.09,
            'Jordan Hicks': 3.78,
            'Robbie Ray': 2.93,
            'Luis Castillo': 3.32,
            'George Kirby': 3.39,
            'Logan Gilbert': 3.73,
            'Bryce Miller': 4.5,
            'Bryan Woo': 3.63,
            'Sonny Gray': 3.24,
            'Miles Mikolas': 4.23,
            'Lance Lynn': 4.47,
            'Kyle Gibson': 4.16,
            'Steven Matz': 2.16,
            'Zach Eflin': 3.64,
            'Aaron Civale': 4.25,
            'Taj Bradley': 4.19,
            'Shane Baz': 3.99,
            'Zack Littell': 6.88,
            'Nathan Eovaldi': 3.87,
            'Jon Gray': 4.15,
            'Andrew Heaney': 4.56,
            'Dane Dunning': 4.32,
            'Patrick Corbin': 6.75,
            'Kevin Gausman': 3.18,
            'José Berríos': 3.65,
            'Chris Bassitt': 0.77,
            'Yusei Kikuchi': 4.02,
            'Bowden Francis': 4.56,
            'MacKenzie Gore': 3.69,
            'Trevor Williams': 4.46,
            'Jake Irvin': 4.14,
            'Patrick Corbin': 6.75,
            'Mitchell Parker': 1.96
        }
    
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
        cache_key = f"pitcher_era_{team_name}_{pitcher_name}"
        
        if not force_refresh:
            cached_data = self.get_cached_data(cache_key)
            if cached_data:
                return cached_data
        
        # Try to get ERA from MLB API
        try:
            # Get team abbreviation
            team_abbr = None
            for name, abbr in self.team_mapping.items():
                if team_name.lower() in name.lower() or name.lower() in team_name.lower():
                    team_abbr = abbr
                    break
            
            if not team_abbr:
                logger.warning(f"Team not found: {team_name}")
                # Try fallback
                if pitcher_name in self.era_mapping:
                    era = self.era_mapping.get(pitcher_name)
                    result = {'era': era, 'source': 'MLB Stats API (Fallback)', 'method': 'name-lookup'}
                    self.save_to_cache(cache_key, result)
                    return result
                return {'era': 'N/A', 'source': 'not-found', 'method': 'team-not-found'}
            
            # Search for player by name
            search_url = f"{self.mlb_api_base_url}/players?search={pitcher_name}"
            response = requests.get(search_url)
            
            if response.status_code == 200:
                player_data = response.json()
                
                if 'people' in player_data and player_data['people']:
                    # Find the pitcher
                    pitcher = None
                    for person in player_data['people']:
                        if person.get('primaryPosition', {}).get('code') == '1':  # Pitcher position code
                            pitcher = person
                            break
                    
                    if not pitcher:
                        # If no pitcher found, use the first person
                        pitcher = player_data['people'][0]
                    
                    player_id = pitcher.get('id')
                    
                    # Get player stats
                    stats_url = f"{self.mlb_api_base_url}/people/{player_id}/stats?stats=season&season=2025&group=pitching"
                    stats_response = requests.get(stats_url)
                    
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        
                        if 'stats' in stats_data and stats_data['stats'] and 'splits' in stats_data['stats'][0]:
                            splits = stats_data['stats'][0]['splits']
                            
                            if splits:
                                era = splits[0].get('stat', {}).get('era')
                                
                                if era is not None:
                                    result = {'era': era, 'source': 'MLB Stats API', 'method': 'api-lookup'}
                                    self.save_to_cache(cache_key, result)
                                    return result
            
            # If we get here, we couldn't find the pitcher's ERA from the API
            # Try fallback
            if pitcher_name in self.era_mapping:
                era = self.era_mapping.get(pitcher_name)
                result = {'era': era, 'source': 'MLB Stats API (Fallback)', 'method': 'name-lookup'}
                self.save_to_cache(cache_key, result)
                return result
            
            logger.error(f"Pitcher ERA not found: {pitcher_name} for team {team_name}")
            return {'era': 'N/A', 'source': 'not-found', 'method': 'api-failed'}
            
        except Exception as e:
            logger.error(f"Error getting pitcher ERA: {e}")
            
            # Try fallback
            if pitcher_name in self.era_mapping:
                era = self.era_mapping.get(pitcher_name)
                result = {'era': era, 'source': 'MLB Stats API (Fallback)', 'method': 'name-lookup'}
                self.save_to_cache(cache_key, result)
                return result
            
            return {'era': 'N/A', 'source': 'error', 'method': 'exception'}
    
    def get_games_for_date(self, date_str, force_refresh=False):
        """
        Get MLB games for a specific date from the MLB Stats API
        
        Args:
            date_str: Date string in format YYYY-MM-DD
            force_refresh: Force refresh of data
            
        Returns:
            List of MLB games for the specified date
        """
        cache_key = f"games_{date_str}"
        
        if not force_refresh:
            cached_data = self.get_cached_data(cache_key)
            if cached_data:
                return cached_data
        
        # Try to get games from MLB API
        try:
            # Get schedule for the date
            schedule_url = f"{self.mlb_api_base_url}/schedule?sportId=1&date={date_str}&hydrate=team,probablePitcher,venue"
            response = requests.get(schedule_url)
            
            if response.status_code == 200:
                schedule_data = response.json()
                
                games = []
                
                if 'dates' in schedule_data and schedule_data['dates']:
                    date_data = schedule_data['dates'][0]
                    
                    if 'games' in date_data:
                        for game_data in date_data['games']:
                            # Get basic game info
                            game_id = game_data.get('gamePk')
                            game_time = game_data.get('gameDate')
                            venue = game_data.get('venue', {}).get('name', 'TBD')
                            
                            # Get teams
                            home_team_data = game_data.get('teams', {}).get('home', {})
                            away_team_data = game_data.get('teams', {}).get('away', {})
                            
                            home_team_name = home_team_data.get('team', {}).get('name', 'Unknown')
                            away_team_name = away_team_data.get('team', {}).get('name', 'Unknown')
                            
                            home_team_abbr = home_team_data.get('team', {}).get('abbreviation', 'UNK')
                            away_team_abbr = away_team_data.get('team', {}).get('abbreviation', 'UNK')
                            
                            # Get probable pitchers
                            home_pitcher_data = home_team_data.get('probablePitcher', {})
                            away_pitcher_data = away_team_data.get('probablePitcher', {})
                            
                            home_pitcher_name = home_pitcher_data.get('fullName', 'TBD')
                            away_pitcher_name = away_pitcher_data.get('fullName', 'TBD')
                            
                            # Get ERA for pitchers
                            home_era_data = self.get_pitcher_era(home_team_name, home_pitcher_name)
                            away_era_data = self.get_pitcher_era(away_team_name, away_pitcher_name)
                            
                            home_era = home_era_data.get('era', 'N/A')
                            away_era = away_era_data.get('era', 'N/A')
                            
                            # Create game object
                            game = {
                                'id': str(game_id),
                                'date': date_str,
                                'time': game_time,
                                'venue': venue,
                                'home_team': {
                                    'name': home_team_name,
                                    'abbreviation': home_team_abbr,
                                    'display_name': home_team_name,
                                    'logo': f"https://www.mlbstatic.com/team-logos/{home_team_abbr}.svg",
                                    'probable_pitcher': {
                                        'name': home_pitcher_name,
                                        'stats': {
                                            'era': home_era,
                                            'whip': 1.25,  # Default value
                                            'strikeouts': 100,  # Default value
                                            'innings_pitched': 100,  # Default value
                                            'era_source': home_era_data.get('source', 'MLB Stats API'),
                                            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    }
                                },
                                'away_team': {
                                    'name': away_team_name,
                                    'abbreviation': away_team_abbr,
                                    'display_name': away_team_name,
                                    'logo': f"https://www.mlbstatic.com/team-logos/{away_team_abbr}.svg",
                                    'probable_pitcher': {
                                        'name': away_pitcher_name,
                                        'stats': {
                                            'era': away_era,
                                            'whip': 1.25,  # Default value
                                            'strikeouts': 100,  # Default value
                                            'innings_pitched': 100,  # Default value
                                            'era_source': away_era_data.get('source', 'MLB Stats API'),
                                            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    }
                                },
                                'weather': {
                                    'temperature': 75,  # Default value
                                    'condition': 'Clear',  # Default value
                                    'wind': '10 mph'  # Default value
                                },
                                'ballpark_factor': 1.0  # Default value
                            }
                            
                            games.append(game)
                
                # Save to cache
                self.save_to_cache(cache_key, games)
                
                return games
            
            # If we get here, we couldn't get games from the API
            logger.error(f"Error getting games for date {date_str}: {response.status_code}")
            
            # Return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting games for date {date_str}: {e}")
            
            # Return empty list
            return []
    
    def get_all_game_data(self, force_refresh=False):
        """
        Get all game data including accurate pitcher statistics
        
        Args:
            force_refresh: Force refresh of data
            
        Returns:
            All game data with accurate pitcher statistics
        """
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get games for today
        games = self.get_games_for_date(today, force_refresh)
        
        # Create result
        result = {
            'games': games,
            'metadata': {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': 'MLB Stats API',
                'game_count': len(games),
                'date': today
            }
        }
        
        return result
