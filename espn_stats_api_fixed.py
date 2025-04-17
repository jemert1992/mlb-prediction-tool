import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime

class ESPNStatsAPIFixed:
    """
    Improved class to fetch real MLB statistics from ESPN with more robust scraping
    """
    
    def __init__(self):
        """Initialize the ESPN Stats API client"""
        self.base_url = "https://www.espn.com/mlb"
        self.cache_dir = 'cache/espn'
        self.cache_expiry = 3600 * 3  # Cache expiry in seconds (3 hours)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # User agents to rotate for avoiding scraping detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
    
    def get_random_user_agent(self):
        """Get a random user agent to avoid detection"""
        return random.choice(self.user_agents)
    
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
    
    def get_team_abbreviation(self, team_name):
        """
        Get ESPN team abbreviation from team name
        """
        team_map = {
            'Arizona Diamondbacks': 'ari',
            'Atlanta Braves': 'atl',
            'Baltimore Orioles': 'bal',
            'Boston Red Sox': 'bos',
            'Chicago Cubs': 'chc',
            'Chicago White Sox': 'chw',
            'Cincinnati Reds': 'cin',
            'Cleveland Guardians': 'cle',
            'Colorado Rockies': 'col',
            'Detroit Tigers': 'det',
            'Houston Astros': 'hou',
            'Kansas City Royals': 'kc',
            'Los Angeles Angels': 'laa',
            'Los Angeles Dodgers': 'lad',
            'Miami Marlins': 'mia',
            'Milwaukee Brewers': 'mil',
            'Minnesota Twins': 'min',
            'New York Mets': 'nym',
            'New York Yankees': 'nyy',
            'Oakland Athletics': 'oak',
            'Philadelphia Phillies': 'phi',
            'Pittsburgh Pirates': 'pit',
            'San Diego Padres': 'sd',
            'Seattle Mariners': 'sea',
            'San Francisco Giants': 'sf',
            'St. Louis Cardinals': 'stl',
            'Tampa Bay Rays': 'tb',
            'Texas Rangers': 'tex',
            'Toronto Blue Jays': 'tor',
            'Washington Nationals': 'wsh'
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
    
    def get_team_pitchers(self, team_name):
        """
        Get list of pitchers for a team from ESPN
        """
        cache_key = f"espn_team_pitchers_{team_name}".replace(" ", "_")
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Get team abbreviation
            team_abbr = self.get_team_abbreviation(team_name)
            if not team_abbr:
                return []
            
            # Get team roster page
            url = f"{self.base_url}/team/roster/_/name/{team_abbr}"
            headers = {'User-Agent': self.get_random_user_agent()}
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error fetching team roster: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find pitchers in roster
            pitchers = []
            
            # Look for table rows
            for row in soup.select('tr.Table__TR'):
                cells = row.select('td')
                if len(cells) >= 3:  # Position is typically in the 3rd column
                    name_cell = cells[1] if len(cells) > 1 else None
                    position_cell = cells[2] if len(cells) > 2 else None
                    
                    if name_cell and position_cell and position_cell.text.strip() in ['P', 'SP', 'RP']:
                        name = name_cell.text.strip()
                        link_elem = name_cell.select_one('a')
                        link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                        
                        if name and link:
                            # Extract player ID from link
                            player_id = link.split('/')[-2] if '/' in link else None
                            
                            pitchers.append({
                                'name': name,
                                'position': position_cell.text.strip(),
                                'link': link,
                                'id': player_id
                            })
            
            # Save to cache
            self.save_to_cache(cache_key, pitchers)
            
            return pitchers
        except Exception as e:
            print(f"Error fetching team pitchers: {e}")
            return []
    
    def scrape_pitcher_era(self, team_name, pitcher_name):
        """
        Scrape pitcher ERA from ESPN website with improved robustness
        """
        cache_key = f"espn_era_{team_name}_{pitcher_name}".replace(" ", "_")
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Get team pitchers
            pitchers = self.get_team_pitchers(team_name)
            
            # Find matching pitcher
            pitcher_info = None
            for p in pitchers:
                if pitcher_name.lower() in p['name'].lower():
                    pitcher_info = p
                    break
            
            if not pitcher_info or not pitcher_info.get('link'):
                print(f"Pitcher {pitcher_name} not found for {team_name}")
                return {"era": 4.50, "source": "default"}
            
            # Get pitcher stats page
            pitcher_url = f"https://www.espn.com{pitcher_info['link']}"
            headers = {'User-Agent': self.get_random_user_agent()}
            
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            response = requests.get(pitcher_url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error fetching pitcher page: {response.status_code}")
                return {"era": 4.50, "source": "default"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find ERA in stats table - multiple approaches for robustness
            era = 4.50  # Default value
            
            # Approach 1: Look for stat blocks
            for stat_item in soup.select('.StatBlock__Content'):
                label = stat_item.select_one('.StatBlock__Label')
                value = stat_item.select_one('.StatBlock__Value')
                
                if label and value and 'ERA' in label.text:
                    try:
                        era = float(value.text)
                        break
                    except ValueError:
                        pass
            
            # Approach 2: Look in the stats table
            if era == 4.50:
                stats_table = soup.select_one('.Table__Scroller')
                if stats_table:
                    headers = [th.text.strip() for th in stats_table.select('thead th')]
                    
                    # Find ERA column index
                    era_index = -1
                    for i, header in enumerate(headers):
                        if header == 'ERA':
                            era_index = i
                            break
                    
                    if era_index >= 0:
                        # Get the first row of data (current season)
                        rows = stats_table.select('tbody tr')
                        if rows:
                            cells = rows[0].select('td')
                            if era_index < len(cells):
                                try:
                                    era = float(cells[era_index].text.strip())
                                except ValueError:
                                    pass
            
            # Approach 3: Look for ERA in any text on the page
            if era == 4.50:
                era_texts = soup.find_all(string=lambda text: 'ERA' in text)
                for text in era_texts:
                    # Look for patterns like "ERA: 3.25" or "ERA 3.25"
                    if ':' in text:
                        parts = text.split(':')
                        if len(parts) > 1 and 'ERA' in parts[0]:
                            try:
                                era = float(parts[1].strip())
                                break
                            except ValueError:
                                pass
            
            result = {
                "era": era,
                "source": "espn",
                "url": pitcher_url,
                "name": pitcher_name,
                "team": team_name
            }
            
            # Save to cache
            self.save_to_cache(cache_key, result)
            
            return result
        except Exception as e:
            print(f"Error scraping ESPN pitcher ERA: {e}")
            return {"era": 4.50, "source": "default"}

# Test the improved ESPN Stats API
if __name__ == "__main__":
    espn_api = ESPNStatsAPIFixed()
    
    # Test pitcher ERA scraping for multiple teams
    teams_pitchers = [
        ('New York Yankees', 'Gerrit Cole'),
        ('Los Angeles Dodgers', 'Clayton Kershaw'),
        ('Boston Red Sox', 'Chris Sale'),
        ('Houston Astros', 'Justin Verlander')
    ]
    
    for team, pitcher in teams_pitchers:
        era_data = espn_api.scrape_pitcher_era(team, pitcher)
        print(f"{pitcher} ({team}): ERA {era_data['era']} (Source: {era_data['source']})")
