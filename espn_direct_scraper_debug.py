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
                    filename='espn_direct_scraper_debug.log')
logger = logging.getLogger('espn_direct_scraper_debug')

def debug_espn_scraping(team_name, pitcher_name):
    """Debug function to test different scraping methods for ESPN pitcher data"""
    
    print(f"\nDebugging ESPN scraping for {pitcher_name} ({team_name})")
    print("=" * 80)
    
    # User agents to rotate for avoiding scraping detection
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    ]
    
    # Team name to ESPN team ID mapping
    team_id_map = {
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
    
    # Get team ID
    team_id = None
    for full_name, tid in team_id_map.items():
        if team_name.lower() in full_name.lower() or full_name.lower() in team_name.lower():
            team_id = tid
            break
    
    print(f"Team ID for {team_name}: {team_id}")
    
    # Method 1: Try ESPN team page
    print("\nMethod 1: ESPN Team Page")
    print("-" * 80)
    
    if team_id:
        try:
            url = f"https://www.espn.com/mlb/team/_/name/{team_id}"
            headers = {'User-Agent': random.choice(user_agents)}
            
            print(f"Fetching URL: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"Successfully fetched team page (Status: {response.status_code})")
                
                # Save HTML for inspection
                with open(f"{team_id}_team_page.html", "w") as f:
                    f.write(response.text)
                print(f"Saved HTML to {team_id}_team_page.html")
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for pitcher name
                found = False
                for element in soup.find_all(text=re.compile(pitcher_name, re.IGNORECASE)):
                    print(f"Found mention of {pitcher_name}: {element.strip()}")
                    parent = element.parent
                    print(f"Parent element: {parent.name}")
                    found = True
                
                if not found:
                    print(f"No mention of {pitcher_name} found on team page")
            else:
                print(f"Failed to fetch team page (Status: {response.status_code})")
        except Exception as e:
            print(f"Error fetching team page: {e}")
    else:
        print(f"Cannot fetch team page without team ID")
    
    # Method 2: Try ESPN team stats page
    print("\nMethod 2: ESPN Team Stats Page")
    print("-" * 80)
    
    if team_id:
        try:
            url = f"https://www.espn.com/mlb/team/stats/_/name/{team_id}/view/pitching"
            headers = {'User-Agent': random.choice(user_agents)}
            
            print(f"Fetching URL: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"Successfully fetched team stats page (Status: {response.status_code})")
                
                # Save HTML for inspection
                with open(f"{team_id}_team_stats_page.html", "w") as f:
                    f.write(response.text)
                print(f"Saved HTML to {team_id}_team_stats_page.html")
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for pitcher name
                found = False
                for element in soup.find_all(text=re.compile(pitcher_name, re.IGNORECASE)):
                    print(f"Found mention of {pitcher_name}: {element.strip()}")
                    parent = element.parent
                    print(f"Parent element: {parent.name}")
                    
                    # Try to find ERA
                    row = parent
                    while row and row.name != 'tr':
                        row = row.parent
                    
                    if row and row.name == 'tr':
                        cells = row.select('td')
                        if len(cells) > 8:  # Assuming ERA is in a specific column
                            print(f"Row cells: {[cell.text.strip() for cell in cells]}")
                    
                    found = True
                
                if not found:
                    print(f"No mention of {pitcher_name} found on team stats page")
            else:
                print(f"Failed to fetch team stats page (Status: {response.status_code})")
        except Exception as e:
            print(f"Error fetching team stats page: {e}")
    else:
        print(f"Cannot fetch team stats page without team ID")
    
    # Method 3: Try ESPN search
    print("\nMethod 3: ESPN Search")
    print("-" * 80)
    
    try:
        search_url = f"https://www.espn.com/mlb/players/search?search={pitcher_name.replace(' ', '+')}"
        headers = {'User-Agent': random.choice(user_agents)}
        
        print(f"Fetching URL: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"Successfully fetched search results (Status: {response.status_code})")
            
            # Save HTML for inspection
            with open(f"{pitcher_name.replace(' ', '_')}_search.html", "w") as f:
                f.write(response.text)
            print(f"Saved HTML to {pitcher_name.replace(' ', '_')}_search.html")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for player links
            found = False
            for link in soup.select('a'):
                href = link.get('href', '')
                if '/player/_/id/' in href and link.text:
                    name = link.text.strip()
                    if pitcher_name.lower() in name.lower() or name.lower() in pitcher_name.lower():
                        print(f"Found player link: {name} - {href}")
                        found = True
                        
                        # Try to fetch player page
                        player_url = f"https://www.espn.com{href}" if not href.startswith('http') else href
                        print(f"\nFetching player page: {player_url}")
                        
                        try:
                            player_response = requests.get(player_url, headers={'User-Agent': random.choice(user_agents)}, timeout=15)
                            
                            if player_response.status_code == 200:
                                print(f"Successfully fetched player page (Status: {player_response.status_code})")
                                
                                # Save HTML for inspection
                                with open(f"{name.replace(' ', '_')}_player.html", "w") as f:
                                    f.write(player_response.text)
                                print(f"Saved HTML to {name.replace(' ', '_')}_player.html")
                                
                                # Parse HTML
                                player_soup = BeautifulSoup(player_response.text, 'html.parser')
                                
                                # Look for ERA
                                era_found = False
                                
                                # Method 1: Look for stat blocks
                                stat_blocks = player_soup.select('.PlayerStats__stat-item')
                                for block in stat_blocks:
                                    label = block.select_one('.PlayerStats__stat-label')
                                    value = block.select_one('.PlayerStats__stat-value')
                                    
                                    if label and value and 'ERA' in label.text:
                                        print(f"Found ERA in stat block: {value.text}")
                                        era_found = True
                                
                                # Method 2: Look for ERA in table
                                if not era_found:
                                    tables = player_soup.select('table')
                                    for table in tables:
                                        headers = [th.text.strip() for th in table.select('th')]
                                        
                                        # Find ERA column index
                                        era_index = -1
                                        for i, header in enumerate(headers):
                                            if header == 'ERA':
                                                era_index = i
                                                break
                                        
                                        if era_index >= 0:
                                            print(f"Found ERA column in table at index {era_index}")
                                            # Get the first row of data
                                            rows = table.select('tbody tr')
                                            if rows:
                                                cells = rows[0].select('td')
                                                if era_index < len(cells):
                                                    print(f"ERA value in table: {cells[era_index].text.strip()}")
                                                    era_found = True
                                
                                # Method 3: Look for ERA in any text
                                if not era_found:
                                    era_pattern = r'ERA[:\s]+([0-9.]+)'
                                    for text in player_soup.stripped_strings:
                                        if 'ERA' in text:
                                            match = re.search(era_pattern, text)
                                            if match:
                                                print(f"Found ERA in text: {match.group(1)}")
                                                era_found = True
                                
                                # Method 4: Look for ERA in script data
                                if not era_found:
                                    scripts = player_soup.select('script')
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
                                                        print(f"Found ERA in script data: {stat_data['era']}")
                                                        era_found = True
                                            except Exception as e:
                                                print(f"Error parsing script data: {e}")
                                
                                if not era_found:
                                    print("Could not find ERA on player page")
                            else:
                                print(f"Failed to fetch player page (Status: {player_response.status_code})")
                        except Exception as e:
                            print(f"Error fetching player page: {e}")
            
            if not found:
                print(f"No search results found for {pitcher_name}")
        else:
            print(f"Failed to fetch search results (Status: {response.status_code})")
    except Exception as e:
        print(f"Error searching for pitcher: {e}")
    
    # Method 4: Try MLB Stats API
    print("\nMethod 4: MLB Stats API")
    print("-" * 80)
    
    try:
        url = "https://statsapi.mlb.com/api/v1/teams"
        headers = {'User-Agent': random.choice(user_agents)}
        
        print(f"Fetching MLB teams: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"Successfully fetched MLB teams (Status: {response.status_code})")
            
            teams_data = response.json()
            team_id = None
            
            # Find team ID
            for team in teams_data.get('teams', []):
                if team_name.lower() in team.get('name', '').lower() or team.get('name', '').lower() in team_name.lower():
                    team_id = team.get('id')
                    print(f"Found MLB team ID for {team_name}: {team_id}")
                    break
            
            if team_id:
                # Get team roster
                roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
                print(f"Fetching team roster: {roster_url}")
                
                roster_response = requests.get(roster_url, headers=headers, timeout=15)
                
                if roster_response.status_code == 200:
                    print(f"Successfully fetched team roster (Status: {roster_response.status_code})")
                    
                    roster_data = roster_response.json()
                    player_id = None
                    
                    # Find player ID
                    for player in roster_data.get('roster', []):
                        if pitcher_name.lower() in player.get('person', {}).get('fullName', '').lower() or player.get('person', {}).get('fullName', '').lower() in pitcher_name.lower():
                            player_id = player.get('person', {}).get('id')
                            print(f"Found MLB player ID for {pitcher_name}: {player_id}")
                            break
                    
                    if player_id:
                        # Get player stats
                        stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&group=pitching"
                        print(f"Fetching player stats: {stats_url}")
                        
                        stats_response = requests.get(stats_url, headers=headers, timeout=15)
                        
                        if stats_response.status_code == 200:
                            print(f"Successfully fetched player stats (Status: {stats_response.status_code})")
                            
                            stats_data = stats_response.json()
                            
                            # Find ERA
                            for group in stats_data.get('stats', []):
                                for split in group.get('splits', []):
                                    for stat, value in split.get('stat', {}).items():
                                        if stat.lower() == 'era':
                                            print(f"Found ERA in MLB Stats API: {value}")
                        else:
                            print(f"Failed to fetch player stats (Status: {stats_response.status_code})")
                    else:
                        print(f"Could not find player ID for {pitcher_name}")
                else:
                    print(f"Failed to fetch team roster (Status: {roster_response.status_code})")
            else:
                print(f"Could not find MLB team ID for {team_name}")
        else:
            print(f"Failed to fetch MLB teams (Status: {response.status_code})")
    except Exception as e:
        print(f"Error accessing MLB Stats API: {e}")
    
    print("\nDebugging complete")
    print("=" * 80)

if __name__ == "__main__":
    # Test with a few pitchers
    debug_espn_scraping("Chicago Cubs", "Matthew Boyd")
    debug_espn_scraping("San Diego Padres", "Nick Pivetta")
    debug_espn_scraping("New York Yankees", "Gerrit Cole")
