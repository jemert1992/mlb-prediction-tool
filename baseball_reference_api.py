import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

class BaseballReferenceAPI:
    """
    Class to fetch real MLB statistics from Baseball Reference
    """
    
    def __init__(self):
        """Initialize the Baseball Reference API client"""
        self.base_url = "https://www.baseball-reference.com"
        self.cache_dir = 'cache/bbref'
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
                print(f"Error reading Baseball Reference cache: {e}")
        
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
            print(f"Error saving Baseball Reference data to cache: {e}")
            return False
    
    def scrape_pitcher_stats(self, team_abbr, pitcher_name):
        """
        Scrape pitcher statistics from Baseball Reference
        """
        cache_key = f"bbref_pitcher_{team_abbr}_{pitcher_name}".replace(" ", "_")
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Get team page
            team_url = f"{self.base_url}/teams/{team_abbr}/2025.shtml"
            response = requests.get(team_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find pitcher in roster
            pitcher_found = False
            pitcher_url = None
            
            # Look in pitching table
            pitching_table = soup.select_one('#team_pitching')
            if pitching_table:
                for row in pitching_table.select('tbody tr'):
                    name_cell = row.select_one('td[data-stat="player"]')
                    if name_cell and pitcher_name.lower() in name_cell.text.lower():
                        pitcher_found = True
                        link_elem = name_cell.select_one('a')
                        if link_elem and 'href' in link_elem.attrs:
                            pitcher_url = link_elem['href']
                            break
            
            if not pitcher_found or not pitcher_url:
                return {
                    "era": 4.50,
                    "whip": 1.30,
                    "strikeouts": 0,
                    "innings": 0,
                    "source": "default"
                }
            
            # Get pitcher stats page
            full_pitcher_url = f"{self.base_url}{pitcher_url}"
            response = requests.get(full_pitcher_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find stats in standard pitching table
            stats_table = soup.select_one('#pitching_standard')
            
            # Default values
            era = 4.50
            whip = 1.30
            strikeouts = 0
            innings = 0
            
            if stats_table:
                # Get current season stats (last row)
                current_season_row = stats_table.select('tbody tr')[-1]
                
                # Extract ERA
                era_cell = current_season_row.select_one('td[data-stat="earned_run_avg"]')
                if era_cell:
                    try:
                        era = float(era_cell.text)
                    except ValueError:
                        pass
                
                # Extract WHIP
                whip_cell = current_season_row.select_one('td[data-stat="whip"]')
                if whip_cell:
                    try:
                        whip = float(whip_cell.text)
                    except ValueError:
                        pass
                
                # Extract strikeouts
                so_cell = current_season_row.select_one('td[data-stat="SO"]')
                if so_cell:
                    try:
                        strikeouts = int(so_cell.text)
                    except ValueError:
                        pass
                
                # Extract innings pitched
                ip_cell = current_season_row.select_one('td[data-stat="IP"]')
                if ip_cell:
                    try:
                        innings = float(ip_cell.text)
                    except ValueError:
                        pass
            
            result = {
                "era": era,
                "whip": whip,
                "strikeouts": strikeouts,
                "innings": innings,
                "source": "baseball-reference",
                "url": full_pitcher_url
            }
            
            # Save to cache
            self.save_to_cache(cache_key, result)
            
            return result
        except Exception as e:
            print(f"Error scraping Baseball Reference pitcher stats: {e}")
            return {
                "era": 4.50,
                "whip": 1.30,
                "strikeouts": 0,
                "innings": 0,
                "source": "default"
            }
    
    def get_team_abbreviation(self, team_name):
        """
        Get Baseball Reference team abbreviation from team name
        """
        team_map = {
            'Arizona Diamondbacks': 'ARI',
            'Atlanta Braves': 'ATL',
            'Baltimore Orioles': 'BAL',
            'Boston Red Sox': 'BOS',
            'Chicago Cubs': 'CHC',
            'Chicago White Sox': 'CHW',
            'Cincinnati Reds': 'CIN',
            'Cleveland Guardians': 'CLE',
            'Colorado Rockies': 'COL',
            'Detroit Tigers': 'DET',
            'Houston Astros': 'HOU',
            'Kansas City Royals': 'KCR',
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
            'San Diego Padres': 'SDP',
            'Seattle Mariners': 'SEA',
            'San Francisco Giants': 'SFG',
            'St. Louis Cardinals': 'STL',
            'Tampa Bay Rays': 'TBR',
            'Texas Rangers': 'TEX',
            'Toronto Blue Jays': 'TOR',
            'Washington Nationals': 'WSN'
        }
        
        # Try exact match first
        if team_name in team_map:
            return team_map[team_name]
        
        # Try partial match
        for full_name, abbr in team_map.items():
            if team_name in full_name:
                return abbr
        
        # Return default if no match
        return None

# Test the Baseball Reference API
if __name__ == "__main__":
    bbref_api = BaseballReferenceAPI()
    
    # Test pitcher stats scraping
    stats = bbref_api.scrape_pitcher_stats("NYY", "Gerrit Cole")
    print(f"Gerrit Cole: ERA {stats['era']}, WHIP {stats['whip']}, SO {stats['strikeouts']} (Source: {stats['source']})")
    
    stats = bbref_api.scrape_pitcher_stats("LAD", "Clayton Kershaw")
    print(f"Clayton Kershaw: ERA {stats['era']}, WHIP {stats['whip']}, SO {stats['strikeouts']} (Source: {stats['source']})")
