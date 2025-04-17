import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='espn_direct_scraper.log')
logger = logging.getLogger('espn_direct_scraper')

class ESPNDirectScraper:
    """
    Class to directly scrape ERA values from ESPN's website in real-time
    """
    
    def __init__(self):
        """Initialize the ESPN direct scraper"""
        self.base_url = "https://www.espn.com/mlb"
        self.cache_dir = 'cache/espn_direct'
        self.cache_expiry = 3600 * 1  # Cache expiry in seconds (1 hour)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # User agents to rotate for avoiding scraping detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Team name to ESPN team ID mapping
        self.team_id_map = {
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
                    logger.info(f"Using cached data for {cache_key}")
                    return cached_data.get('data')
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
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
            
            logger.info(f"Saved data to cache for {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to cache: {e}")
            return False
    
    def clear_cache(self, cache_key=None):
        """Clear cache for a specific key or all cache"""
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
    
    def get_team_id(self, team_name):
        """Get ESPN team ID from team name"""
        # Try exact match first
        if team_name in self.team_id_map:
            return self.team_id_map[team_name]
        
        # Try partial match
        for full_name, team_id in self.team_id_map.items():
            if team_name.lower() in full_name.lower() or full_name.lower() in team_name.lower():
                return team_id
        
        # Return default if no match
        logger.warning(f"Team ID not found for {team_name}")
        return None
    
    def get_team_roster(self, team_name):
        """Get team roster from ESPN"""
        team_id = self.get_team_id(team_name)
        if not team_id:
            logger.error(f"Team ID not found for {team_name}")
            return []
        
        cache_key = f"espn_roster_{team_id}"
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Get team roster page
            url = f"{self.base_url}/team/roster/_/name/{team_id}"
            headers = {'User-Agent': self.get_random_user_agent()}
            
            logger.info(f"Fetching team roster from {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error fetching team roster: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find pitchers in roster
            players = []
            
            # Look for table rows
            for row in soup.select('tr'):
                cells = row.select('td')
                if len(cells) >= 3:
                    name_cell = cells[1] if len(cells) > 1 else None
                    position_cell = cells[2] if len(cells) > 2 else None
                    
                    if name_cell and position_cell:
                        name = name_cell.text.strip()
                        position = position_cell.text.strip()
                        
                        # Get player link if available
                        link_elem = name_cell.select_one('a')
                        link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                        
                        # Extract player ID from link
                        player_id = None
                        if link and '/id/' in link:
                            player_id = link.split('/id/')[1].split('/')[0]
                        
                        players.append({
                            'name': name,
                            'position': position,
                            'link': link,
                            'id': player_id
                        })
            
            # Save to cache
            self.save_to_cache(cache_key, players)
            
            logger.info(f"Found {len(players)} players for {team_name}")
            return players
        except Exception as e:
            logger.error(f"Error fetching team roster: {e}")
            return []
    
    def get_pitcher_stats_from_roster_page(self, team_name, pitcher_name):
        """Get pitcher stats from team roster page"""
        players = self.get_team_roster(team_name)
        
        # Find matching pitcher
        pitcher_info = None
        for player in players:
            if (pitcher_name.lower() in player['name'].lower() or 
                player['name'].lower() in pitcher_name.lower()):
                if player['position'] in ['P', 'SP', 'RP']:
                    pitcher_info = player
                    break
        
        if not pitcher_info:
            logger.warning(f"Pitcher {pitcher_name} not found in {team_name} roster")
            return None
        
        return pitcher_info
    
    def get_pitcher_stats_from_player_page(self, player_link, pitcher_name):
        """Get pitcher stats from player page"""
        if not player_link:
            logger.error(f"No player link available for {pitcher_name}")
            return None
        
        try:
            # Ensure the link is absolute
            if not player_link.startswith('http'):
                player_link = f"https://www.espn.com{player_link}"
            
            # Get player page
            headers = {'User-Agent': self.get_random_user_agent()}
            
            logger.info(f"Fetching player page from {player_link}")
            response = requests.get(player_link, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error fetching player page: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find ERA in stats section
            era = None
            
            # Method 1: Look for stat blocks
            stat_blocks = soup.select('.PlayerStats__stat-item')
            for block in stat_blocks:
                label = block.select_one('.PlayerStats__stat-label')
                value = block.select_one('.PlayerStats__stat-value')
                
                if label and value and 'ERA' in label.text:
                    try:
                        era = float(value.text)
                        logger.info(f"Found ERA {era} for {pitcher_name} using method 1")
                        break
                    except ValueError:
                        pass
            
            # Method 2: Look for ERA in table
            if not era:
                tables = soup.select('table')
                for table in tables:
                    headers = [th.text.strip() for th in table.select('th')]
                    
                    # Find ERA column index
                    era_index = -1
                    for i, header in enumerate(headers):
                        if header == 'ERA':
                            era_index = i
                            break
                    
                    if era_index >= 0:
                        # Get the first row of data
                        rows = table.select('tbody tr')
                        if rows:
                            cells = rows[0].select('td')
                            if era_index < len(cells):
                                try:
                                    era = float(cells[era_index].text.strip())
                                    logger.info(f"Found ERA {era} for {pitcher_name} using method 2")
                                    break
                                except ValueError:
                                    pass
            
            # Method 3: Look for ERA in any text
            if not era:
                era_pattern = r'ERA[:\s]+([0-9.]+)'
                for text in soup.stripped_strings:
                    if 'ERA' in text:
                        match = re.search(era_pattern, text)
                        if match:
                            try:
                                era = float(match.group(1))
                                logger.info(f"Found ERA {era} for {pitcher_name} using method 3")
                                break
                            except ValueError:
                                pass
            
            # Method 4: Look for ERA in script data
            if not era:
                scripts = soup.select('script')
                for script in scripts:
                    if script.string and 'window.espn.playerInfo' in script.string:
                        try:
                            # Extract JSON data
                            json_str = script.string.split('window.espn.playerInfo = ')[1].split(';</script>')[0]
                            data = json.loads(json_str)
                            
                            # Look for ERA in player stats
                            stats = data.get('stats', {}).get('baseball', {})
                            for stat_type, stat_data in stats.items():
                                if 'era' in stat_data:
                                    era = float(stat_data['era'])
                                    logger.info(f"Found ERA {era} for {pitcher_name} using method 4")
                                    break
                        except Exception as e:
                            logger.error(f"Error parsing script data: {e}")
            
            if era is not None:
                return {
                    'era': era,
                    'source': 'espn-direct',
                    'url': player_link
                }
            else:
                logger.warning(f"ERA not found for {pitcher_name}")
                return None
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return None
    
    def search_pitcher(self, pitcher_name):
        """Search for pitcher on ESPN"""
        cache_key = f"espn_search_{pitcher_name}".replace(" ", "_")
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Search for pitcher
            search_url = f"https://www.espn.com/mlb/players/search?search={pitcher_name.replace(' ', '+')}"
            headers = {'User-Agent': self.get_random_user_agent()}
            
            logger.info(f"Searching for pitcher at {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error searching for pitcher: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find pitcher in search results
            results = []
            
            # Look for player links
            for link in soup.select('a'):
                href = link.get('href', '')
                if '/player/_/id/' in href and link.text:
                    name = link.text.strip()
                    
                    # Check if this is a pitcher
                    parent = link.parent
                    position = None
                    if parent and parent.next_sibling:
                        position_text = parent.next_sibling.text.strip()
                        if 'P,' in position_text or position_text.endswith(', P'):
                            position = 'P'
                    
                    if position == 'P' or not position:  # Include if position is unknown
                        results.append({
                            'name': name,
                            'link': href,
                            'position': position
                        })
            
            # Save to cache
            self.save_to_cache(cache_key, results)
            
            logger.info(f"Found {len(results)} search results for {pitcher_name}")
            return results
        except Exception as e:
            logger.error(f"Error searching for pitcher: {e}")
            return None
    
    def get_pitcher_era_from_espn_stats_page(self, pitcher_name):
        """Get pitcher ERA from ESPN stats page"""
        try:
            # Search for the pitcher on ESPN stats page
            search_url = f"https://www.espn.com/mlb/stats/player/_/view/pitching"
            headers = {'User-Agent': self.get_random_user_agent()}
            
            logger.info(f"Searching for pitcher on stats page: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error accessing stats page: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table with pitcher stats
            tables = soup.select('table.Table')
            
            for table in tables:
                # Find the ERA column index
                headers = table.select('thead th')
                era_index = -1
                
                for i, header in enumerate(headers):
                    if header.text.strip() == 'ERA':
                        era_index = i
                        break
                
                if era_index == -1:
                    continue
                
                # Look for the pitcher in the table rows
                rows = table.select('tbody tr')
                
                for row in rows:
                    cells = row.select('td')
                    if len(cells) <= era_index:
                        continue
                    
                    # Get player name
                    name_cell = cells[0]
                    name_link = name_cell.select_one('a')
                    
                    if not name_link:
                        continue
                    
                    player_name = name_link.text.strip()
                    
                    # Check if this is the pitcher we're looking for
                    if pitcher_name.lower() in player_name.lower() or player_name.lower() in pitcher_name.lower():
                        # Get ERA
                        era_cell = cells[era_index]
                        try:
                            era = float(era_cell.text.strip())
                            logger.info(f"Found ERA {era} for {pitcher_name} on stats page")
                            
                            # Get player link
                            player_link = name_link.get('href', '')
                            
                            return {
                                'era': era,
                                'source': 'espn-stats-page',
                                'url': player_link
                            }
                        except ValueError:
                            pass
            
            logger.warning(f"Pitcher {pitcher_name} not found on stats page")
            return None
        except Exception as e:
            logger.error(f"Error searching stats page: {e}")
            return None
    
    def get_pitcher_era_from_team_page(self, team_name, pitcher_name):
        """Get pitcher ERA from team page"""
        team_id = self.get_team_id(team_name)
        if not team_id:
            logger.error(f"Team ID not found for {team_name}")
            return None
        
        try:
            # Get team stats page
            url = f"{self.base_url}/team/stats/_/name/{team_id}/view/pitching"
            headers = {'User-Agent': self.get_random_user_agent()}
            
            logger.info(f"Fetching team stats from {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error fetching team stats: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table with pitcher stats
            tables = soup.select('table.Table')
            
            for table in tables:
                # Find the ERA column index
                headers = table.select('thead th')
                era_index = -1
                
                for i, header in enumerate(headers):
                    if header.text.strip() == 'ERA':
                        era_index = i
                        break
                
                if era_index == -1:
                    continue
                
                # Look for the pitcher in the table rows
                rows = table.select('tbody tr')
                
                for row in rows:
                    cells = row.select('td')
                    if len(cells) <= era_index:
                        continue
                    
                    # Get player name
                    name_cell = cells[0]
                    name_link = name_cell.select_one('a')
                    
                    if not name_link:
                        continue
                    
                    player_name = name_link.text.strip()
                    
                    # Check if this is the pitcher we're looking for
                    if pitcher_name.lower() in player_name.lower() or player_name.lower() in pitcher_name.lower():
                        # Get ERA
                        era_cell = cells[era_index]
                        try:
                            era = float(era_cell.text.strip())
                            logger.info(f"Found ERA {era} for {pitcher_name} on team stats page")
                            
                            # Get player link
                            player_link = name_link.get('href', '')
                            
                            return {
                                'era': era,
                                'source': 'espn-team-page',
                                'url': player_link
                            }
                        except ValueError:
                            pass
            
            logger.warning(f"Pitcher {pitcher_name} not found on team stats page")
            return None
        except Exception as e:
            logger.error(f"Error searching team stats page: {e}")
            return None
    
    def get_pitcher_era(self, team_name, pitcher_name, force_refresh=False):
        """
        Get pitcher ERA from ESPN using multiple methods
        """
        cache_key = f"espn_era_{team_name}_{pitcher_name}".replace(" ", "_")
        
        # Clear cache if force refresh
        if force_refresh:
            self.clear_cache(cache_key)
        
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Method 1: Try to get pitcher from team roster
            pitcher_info = self.get_pitcher_stats_from_roster_page(team_name, pitcher_name)
            
            if pitcher_info and pitcher_info.get('link'):
                # Get stats from player page
                stats = self.get_pitcher_stats_from_player_page(pitcher_info['link'], pitcher_name)
                
                if stats and stats.get('era') is not None:
                    result = {
                        'name': pitcher_name,
                        'team': team_name,
                        'era': stats['era'],
                        'source': stats['source'],
                        'method': 'roster',
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Save to cache
                    self.save_to_cache(cache_key, result)
                    
                    return result
            
            # Method 2: Try to get pitcher from team stats page
            team_stats = self.get_pitcher_era_from_team_page(team_name, pitcher_name)
            
            if team_stats and team_stats.get('era') is not None:
                result = {
                    'name': pitcher_name,
                    'team': team_name,
                    'era': team_stats['era'],
                    'source': team_stats['source'],
                    'method': 'team-stats',
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save to cache
                self.save_to_cache(cache_key, result)
                
                return result
            
            # Method 3: Try to get pitcher from ESPN stats page
            stats_page = self.get_pitcher_era_from_espn_stats_page(pitcher_name)
            
            if stats_page and stats_page.get('era') is not None:
                result = {
                    'name': pitcher_name,
                    'team': team_name,
                    'era': stats_page['era'],
                    'source': stats_page['source'],
                    'method': 'stats-page',
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save to cache
                self.save_to_cache(cache_key, result)
                
                return result
            
            # Method 4: Try to search for pitcher
            search_results = self.search_pitcher(pitcher_name)
            
            if search_results and len(search_results) > 0:
                # Use the first result
                pitcher_result = search_results[0]
                
                # Get stats from player page
                stats = self.get_pitcher_stats_from_player_page(pitcher_result['link'], pitcher_name)
                
                if stats and stats.get('era') is not None:
                    result = {
                        'name': pitcher_name,
                        'team': team_name,
                        'era': stats['era'],
                        'source': stats['source'],
                        'method': 'search',
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Save to cache
                    self.save_to_cache(cache_key, result)
                    
                    return result
            
            # If we couldn't find the pitcher with any method, return a default value
            logger.warning(f"Could not find ERA for {pitcher_name} ({team_name}) with any method")
            
            result = {
                'name': pitcher_name,
                'team': team_name,
                'era': 'N/A',
                'source': 'not-found',
                'method': 'none',
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'note': 'Pitcher not found in ESPN data'
            }
            
            # Save to cache with shorter expiry
            self.save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting pitcher ERA: {e}")
            
            # Return error result
            result = {
                'name': pitcher_name,
                'team': team_name,
                'era': 'N/A',
                'source': 'error',
                'method': 'none',
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'note': f'Error: {str(e)}'
            }
            
            return result
