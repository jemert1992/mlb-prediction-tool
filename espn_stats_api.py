import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

class ESPNStatsAPI:
    """
    Class to fetch real MLB statistics from ESPN
    """
    
    def __init__(self):
        """Initialize the ESPN Stats API client"""
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb"
        self.cache_dir = 'cache/espn'
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
                print(f"Error reading ESPN cache: {e}")
        
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
            print(f"Error saving ESPN data to cache: {e}")
            return False
    
    def get_schedule(self, date):
        """
        Get MLB schedule for a specific date from ESPN
        """
        cache_key = f"espn_schedule_{date}"
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Format date as YYYYMMDD for ESPN API
            formatted_date = date.replace('-', '')
            url = f"{self.base_url}/scoreboard?dates={formatted_date}"
            response = requests.get(url)
            data = response.json()
            
            # Save to cache
            self.save_to_cache(cache_key, data)
            
            return data
        except Exception as e:
            print(f"Error fetching ESPN schedule: {e}")
            return {"events": []}
    
    def get_team_stats(self, team_id):
        """
        Get team statistics from ESPN
        """
        cache_key = f"espn_team_{team_id}"
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/teams/{team_id}"
            response = requests.get(url)
            data = response.json()
            
            # Save to cache
            self.save_to_cache(cache_key, data)
            
            return data
        except Exception as e:
            print(f"Error fetching ESPN team stats: {e}")
            return {}
    
    def get_pitcher_stats(self, player_id):
        """
        Get pitcher statistics from ESPN
        """
        cache_key = f"espn_pitcher_{player_id}"
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            url = f"{self.base_url}/athletes/{player_id}"
            response = requests.get(url)
            data = response.json()
            
            # Save to cache
            self.save_to_cache(cache_key, data)
            
            return data
        except Exception as e:
            print(f"Error fetching ESPN pitcher stats: {e}")
            return {}
    
    def scrape_pitcher_era(self, team_name, pitcher_name):
        """
        Scrape pitcher ERA from ESPN website
        """
        cache_key = f"espn_era_{team_name}_{pitcher_name}".replace(" ", "_")
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Convert team name to ESPN format
            team_name_formatted = team_name.lower().replace(" ", "-")
            
            # Search for pitcher
            search_url = f"https://www.espn.com/mlb/team/roster/_/name/{team_name_formatted}"
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find pitcher in roster
            pitcher_found = False
            pitcher_link = None
            
            for row in soup.select('tr.Table__TR'):
                cells = row.select('td')
                if len(cells) >= 2:
                    name_cell = cells[1]
                    if pitcher_name.lower() in name_cell.text.lower():
                        pitcher_found = True
                        link_elem = name_cell.select_one('a')
                        if link_elem and 'href' in link_elem.attrs:
                            pitcher_link = link_elem['href']
                            break
            
            if not pitcher_found or not pitcher_link:
                return {"era": 4.50, "source": "default"}
            
            # Get pitcher stats page
            pitcher_url = f"https://www.espn.com{pitcher_link}"
            response = requests.get(pitcher_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find ERA in stats table
            era = 4.50  # Default value
            
            for stat_item in soup.select('.StatBlock__Content'):
                label = stat_item.select_one('.StatBlock__Label')
                value = stat_item.select_one('.StatBlock__Value')
                
                if label and value and 'ERA' in label.text:
                    try:
                        era = float(value.text)
                        break
                    except ValueError:
                        pass
            
            result = {"era": era, "source": "espn", "url": pitcher_url}
            
            # Save to cache
            self.save_to_cache(cache_key, result)
            
            return result
        except Exception as e:
            print(f"Error scraping ESPN pitcher ERA: {e}")
            return {"era": 4.50, "source": "default"}
    
    def get_espn_team_id(self, team_name):
        """
        Get ESPN team ID from team name
        """
        team_map = {
            'Arizona Diamondbacks': '29',
            'Atlanta Braves': '15',
            'Baltimore Orioles': '1',
            'Boston Red Sox': '2',
            'Chicago Cubs': '16',
            'Chicago White Sox': '4',
            'Cincinnati Reds': '17',
            'Cleveland Guardians': '5',
            'Colorado Rockies': '27',
            'Detroit Tigers': '6',
            'Houston Astros': '18',
            'Kansas City Royals': '7',
            'Los Angeles Angels': '3',
            'Los Angeles Dodgers': '19',
            'Miami Marlins': '28',
            'Milwaukee Brewers': '8',
            'Minnesota Twins': '9',
            'New York Mets': '21',
            'New York Yankees': '10',
            'Oakland Athletics': '11',
            'Philadelphia Phillies': '22',
            'Pittsburgh Pirates': '23',
            'San Diego Padres': '25',
            'Seattle Mariners': '12',
            'San Francisco Giants': '26',
            'St. Louis Cardinals': '24',
            'Tampa Bay Rays': '30',
            'Texas Rangers': '13',
            'Toronto Blue Jays': '14',
            'Washington Nationals': '20'
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

# Test the ESPN Stats API
if __name__ == "__main__":
    espn_api = ESPNStatsAPI()
    
    # Test schedule
    schedule = espn_api.get_schedule("2025-04-16")
    if schedule.get('events'):
        print(f"Found {len(schedule['events'])} games for 2025-04-16")
    
    # Test pitcher ERA scraping
    era_data = espn_api.scrape_pitcher_era("New York Yankees", "Gerrit Cole")
    print(f"Gerrit Cole ERA: {era_data['era']} (Source: {era_data['source']})")
    
    era_data = espn_api.scrape_pitcher_era("Los Angeles Dodgers", "Clayton Kershaw")
    print(f"Clayton Kershaw ERA: {era_data['era']} (Source: {era_data['source']})")
