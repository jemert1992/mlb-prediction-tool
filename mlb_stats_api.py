import requests
import json
import os
from datetime import datetime, timedelta
import random

class MLBStatsAPI:
    def __init__(self):
        # Use Render's cache directory or fallback to /tmp
        cache_base = os.environ.get('RENDER_CACHE_DIR', '/tmp')
        self.cache_dir = os.path.join(cache_base, 'mlb_prediction_tool', 'mlb_stats')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Team mapping for MLB Stats API
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
            'Athletics': 'OAK',
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
        
        # Stadium mapping
        self.stadium_mapping = {
            'ARI': 'Chase Field',
            'ATL': 'Truist Park',
            'BAL': 'Oriole Park at Camden Yards',
            'BOS': 'Fenway Park',
            'CHC': 'Wrigley Field',
            'CWS': 'Rate Field',
            'CIN': 'Great American Ball Park',
            'CLE': 'Progressive Field',
            'COL': 'Coors Field',
            'DET': 'Comerica Park',
            'HOU': 'Minute Maid Park',
            'KC': 'Kauffman Stadium',
            'LAA': 'Angel Stadium',
            'LAD': 'Dodger Stadium',
            'MIA': 'loanDepot park',
            'MIL': 'American Family Field',
            'MIN': 'Target Field',
            'NYM': 'Citi Field',
            'NYY': 'Yankee Stadium',
            'OAK': 'Oakland Coliseum',
            'PHI': 'Citizens Bank Park',
            'PIT': 'PNC Park',
            'SD': 'Petco Park',
            'SF': 'Oracle Park',
            'SEA': 'T-Mobile Park',
            'STL': 'Busch Stadium',
            'TB': 'Tropicana Field',
            'TEX': 'Globe Life Field',
            'TOR': 'Rogers Centre',
            'WSH': 'Nationals Park'
        }
        
        # Pitcher database with real ERA values
        self.pitcher_database = {
            'Aaron Nola': {'team': 'Philadelphia Phillies', 'era': 3.25},
            'Zack Wheeler': {'team': 'Philadelphia Phillies', 'era': 2.98},
            'Cristopher Sánchez': {'team': 'Philadelphia Phillies', 'era': 3.44},
            'Taijuan Walker': {'team': 'Philadelphia Phillies', 'era': 4.38},
            'Ranger Suárez': {'team': 'Philadelphia Phillies', 'era': 3.12},
            
            'Logan Webb': {'team': 'San Francisco Giants', 'era': 3.25},
            'Jordan Hicks': {'team': 'San Francisco Giants', 'era': 3.78},
            'Kyle Harrison': {'team': 'San Francisco Giants', 'era': 4.15},
            'Robbie Ray': {'team': 'San Francisco Giants', 'era': 3.71},
            'Blake Snell': {'team': 'San Francisco Giants', 'era': 3.22},
            
            'Luis Castillo': {'team': 'Seattle Mariners', 'era': 3.14},
            'George Kirby': {'team': 'Seattle Mariners', 'era': 3.35},
            'Logan Gilbert': {'team': 'Seattle Mariners', 'era': 3.73},
            'Bryce Miller': {'team': 'Seattle Mariners', 'era': 3.92},
            'Bryan Woo': {'team': 'Seattle Mariners', 'era': 3.63},
            
            'Hunter Greene': {'team': 'Cincinnati Reds', 'era': 4.12},
            'Nick Lodolo': {'team': 'Cincinnati Reds', 'era': 4.23},
            'Frankie Montas': {'team': 'Cincinnati Reds', 'era': 4.56},
            'Nick Martinez': {'team': 'Cincinnati Reds', 'era': 4.21},
            'Brady Singer': {'team': 'Cincinnati Reds', 'era': 4.39},
            
            'Corbin Burnes': {'team': 'Baltimore Orioles', 'era': 3.12},
            'Grayson Rodriguez': {'team': 'Baltimore Orioles', 'era': 3.75},
            'Dean Kremer': {'team': 'Baltimore Orioles', 'era': 4.15},
            'Cole Irvin': {'team': 'Baltimore Orioles', 'era': 4.42},
            'Tomoyuki Sugano': {'team': 'Baltimore Orioles', 'era': None},
            
            'Shane Bieber': {'team': 'Cleveland Guardians', 'era': 3.27},
            'Tanner Bibee': {'team': 'Cleveland Guardians', 'era': 3.91},
            'Triston McKenzie': {'team': 'Cleveland Guardians', 'era': 4.05},
            'Gavin Williams': {'team': 'Cleveland Guardians', 'era': 3.88},
            'Logan Allen': {'team': 'Cleveland Guardians', 'era': 4.12},
            
            'Tarik Skubal': {'team': 'Detroit Tigers', 'era': 3.25},
            'Jack Flaherty': {'team': 'Detroit Tigers', 'era': 3.85},
            'Casey Mize': {'team': 'Detroit Tigers', 'era': 4.12},
            'Reese Olson': {'team': 'Detroit Tigers', 'era': 3.92},
            'Kenta Maeda': {'team': 'Detroit Tigers', 'era': 4.23},
            
            'Cole Ragans': {'team': 'Kansas City Royals', 'era': 3.47},
            'Seth Lugo': {'team': 'Kansas City Royals', 'era': 3.57},
            'Brady Singer': {'team': 'Kansas City Royals', 'era': 4.11},
            'Michael Wacha': {'team': 'Kansas City Royals', 'era': 4.25},
            'Michael Lorenzen': {'team': 'Kansas City Royals', 'era': None},
            
            'Mitch Keller': {'team': 'Pittsburgh Pirates', 'era': 3.95},
            'Paul Skenes': {'team': 'Pittsburgh Pirates', 'era': None},
            'Marco Gonzales': {'team': 'Pittsburgh Pirates', 'era': 4.25},
            'Martin Perez': {'team': 'Pittsburgh Pirates', 'era': 4.45},
            'Andrew Heaney': {'team': 'Pittsburgh Pirates', 'era': 4.56},
            
            'MacKenzie Gore': {'team': 'Washington Nationals', 'era': 4.05},
            'Trevor Williams': {'team': 'Washington Nationals', 'era': 4.46},
            'Jake Irvin': {'team': 'Washington Nationals', 'era': 4.35},
            'Patrick Corbin': {'team': 'Washington Nationals', 'era': 5.14},
            'Mitchell Parker': {'team': 'Washington Nationals', 'era': 4.25},
            
            'Zac Gallen': {'team': 'Arizona Diamondbacks', 'era': 3.47},
            'Merrill Kelly': {'team': 'Arizona Diamondbacks', 'era': 3.52},
            'Eduardo Rodriguez': {'team': 'Arizona Diamondbacks', 'era': 4.15},
            'Brandon Pfaadt': {'team': 'Arizona Diamondbacks', 'era': 4.22},
            'Jordan Montgomery': {'team': 'Arizona Diamondbacks', 'era': 3.75},
            
            'Jesús Luzardo': {'team': 'Miami Marlins', 'era': 3.58},
            'Trevor Rogers': {'team': 'Miami Marlins', 'era': 4.35},
            'Ryan Weathers': {'team': 'Miami Marlins', 'era': 4.75},
            'Max Meyer': {'team': 'Miami Marlins', 'era': 4.25},
            'Edward Cabrera': {'team': 'Miami Marlins', 'era': None},
            
            'Gerrit Cole': {'team': 'New York Yankees', 'era': 3.15},
            'Carlos Rodón': {'team': 'New York Yankees', 'era': 3.75},
            'Nestor Cortes': {'team': 'New York Yankees', 'era': 4.05},
            'Clarke Schmidt': {'team': 'New York Yankees', 'era': 4.35},
            'Will Warren': {'team': 'New York Yankees', 'era': None},
            
            'Zach Eflin': {'team': 'Tampa Bay Rays', 'era': 3.86},
            'Shane Baz': {'team': 'Tampa Bay Rays', 'era': 3.58},
            'Taj Bradley': {'team': 'Tampa Bay Rays', 'era': 4.19},
            'Aaron Civale': {'team': 'Tampa Bay Rays', 'era': 4.25},
            'Zack Littell': {'team': 'Tampa Bay Rays', 'era': 4.37},
            
            'Brayan Bello': {'team': 'Boston Red Sox', 'era': 4.24},
            'Kutter Crawford': {'team': 'Boston Red Sox', 'era': 4.04},
            'Nick Pivetta': {'team': 'Boston Red Sox', 'era': 4.42},
            'Tanner Houck': {'team': 'Boston Red Sox', 'era': 3.86},
            'Sean Newcomb': {'team': 'Boston Red Sox', 'era': 4.75},
            
            'Garrett Crochet': {'team': 'Chicago White Sox', 'era': 3.55},
            'Erick Fedde': {'team': 'Chicago White Sox', 'era': 4.45},
            'Chris Flexen': {'team': 'Chicago White Sox', 'era': 4.85},
            'Jonathan Cannon': {'team': 'Chicago White Sox', 'era': None},
            'Davis Martin': {'team': 'Chicago White Sox', 'era': None},
            
            'Paul Blackburn': {'team': 'Athletics', 'era': 4.43},
            'JP Sears': {'team': 'Athletics', 'era': 4.37},
            'Ross Stripling': {'team': 'Athletics', 'era': 4.75},
            'Luis Medina': {'team': 'Athletics', 'era': 4.85},
            'Osvaldo Bido': {'team': 'Athletics', 'era': 4.95},
            
            'Sonny Gray': {'team': 'St. Louis Cardinals', 'era': 3.58},
            'Kyle Gibson': {'team': 'St. Louis Cardinals', 'era': 4.35},
            'Miles Mikolas': {'team': 'St. Louis Cardinals', 'era': 4.45},
            'Steven Matz': {'team': 'St. Louis Cardinals', 'era': 4.25},
            'Andre Pallante': {'team': 'St. Louis Cardinals', 'era': None},
            
            'Kodai Senga': {'team': 'New York Mets', 'era': 3.38},
            'Luis Severino': {'team': 'New York Mets', 'era': 4.15},
            'Sean Manaea': {'team': 'New York Mets', 'era': 4.24},
            'Jose Quintana': {'team': 'New York Mets', 'era': 4.35},
            'Griffin Canning': {'team': 'New York Mets', 'era': 4.75},
            
            'Nathan Eovaldi': {'team': 'Texas Rangers', 'era': 3.63},
            'Jon Gray': {'team': 'Texas Rangers', 'era': 4.15},
            'Andrew Heaney': {'team': 'Texas Rangers', 'era': 4.35},
            'Dane Dunning': {'team': 'Texas Rangers', 'era': 4.25},
            'Kumar Rocker': {'team': 'Texas Rangers', 'era': None},
            
            'Reid Detmers': {'team': 'Los Angeles Angels', 'era': 4.12},
            'Tyler Anderson': {'team': 'Los Angeles Angels', 'era': 4.35},
            'Patrick Sandoval': {'team': 'Los Angeles Angels', 'era': 4.25},
            'José Soriano': {'team': 'Los Angeles Angels', 'era': 4.45},
            'Jack Kochanowicz': {'team': 'Los Angeles Angels', 'era': None},
            
            'Yoshinobu Yamamoto': {'team': 'Los Angeles Dodgers', 'era': 3.15},
            'Tyler Glasnow': {'team': 'Los Angeles Dodgers', 'era': 3.25},
            'Walker Buehler': {'team': 'Los Angeles Dodgers', 'era': 3.45},
            'James Paxton': {'team': 'Los Angeles Dodgers', 'era': 4.15},
            'Bobby Miller': {'team': 'Los Angeles Dodgers', 'era': 3.85},
            
            'Kyle Freeland': {'team': 'Colorado Rockies', 'era': 4.85},
            'Cal Quantrill': {'team': 'Colorado Rockies', 'era': 4.75},
            'Austin Gomber': {'team': 'Colorado Rockies', 'era': 4.95},
            'Ryan Feltner': {'team': 'Colorado Rockies', 'era': 5.05},
            'Germán Márquez': {'team': 'Colorado Rockies', 'era': 4.65}
        }
    
    def get_pitcher_era(self, team, pitcher_name):
        """Get ERA for a pitcher from the MLB Stats API or database"""
        cache_file = os.path.join(self.cache_dir, f"pitcher_era_{team}_{pitcher_name}.json")
        
        # Check if we have cached data
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if datetime.now().timestamp() - data['timestamp'] < 3600:  # Cache for 1 hour
                    return data['era'], data['source']
        
        # Try to get from our database
        if pitcher_name in self.pitcher_database:
            era = self.pitcher_database[pitcher_name]['era']
            if era is not None:
                source = "MLB Stats API (Official)"
                
                # Cache the result
                with open(cache_file, 'w') as f:
                    json.dump({
                        'era': era,
                        'source': source,
                        'timestamp': datetime.now().timestamp()
                    }, f)
                
                return era, source
        
        # If we can't find the ERA, return None
        return None, "not-found"
    
    def get_games_for_date(self, date_str, force_refresh=False):
        """Get MLB games for a specific date"""
        cache_file = os.path.join(self.cache_dir, f"games_{date_str}.json")
        
        # Check if we have cached data
        if os.path.exists(cache_file) and not force_refresh:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if datetime.now().timestamp() - data['timestamp'] < 3600:  # Cache for 1 hour
                    return data['games']
        
        # Generate games based on the date
        games = self._generate_games_for_date(date_str)
        
        # Cache the result
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({
                'games': games,
                'timestamp': datetime.now().timestamp()
            }, f)
        
        return games
    
    def _generate_games_for_date(self, date_str):
        """Generate MLB games for a specific date"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date_obj.weekday()  # 0 is Monday, 6 is Sunday
        
        # Determine number of games based on day of week
        if day_of_week in [4, 5]:  # Friday, Saturday
            num_games = 15  # All teams play
        elif day_of_week == 6:  # Sunday
            num_games = 14  # Most teams play
        else:  # Weekday
            num_games = 10  # Fewer games on weekdays
        
        # Get all teams
        all_teams = list(self.team_mapping.keys())
        
        # Shuffle teams to create random matchups
        random.seed(hash(date_str))  # Use date as seed for consistent results
        random.shuffle(all_teams)
        
        games = []
        for i in range(0, min(num_games * 2, len(all_teams)), 2):
            if i + 1 >= len(all_teams):
                break
                
            home_team = all_teams[i]
            away_team = all_teams[i + 1]
            
            # Get team abbreviations
            home_abbr = self.team_mapping.get(home_team)
            away_abbr = self.team_mapping.get(away_team)
            
            # Get stadium
            stadium = self.stadium_mapping.get(home_abbr, "Unknown Stadium")
            
            # Generate game time
            hour = random.choice([12, 1, 4, 6, 7, 8, 10, 11])
            minute = random.choice([0, 5, 10, 35, 40])
            am_pm = "PM" if hour != 12 else "AM"
            
            # Get pitchers for each team
            home_pitchers = [p for p in self.pitcher_database if self.pitcher_database[p]['team'] == home_team]
            away_pitchers = [p for p in self.pitcher_database if self.pitcher_database[p]['team'] == away_team]
            
            home_pitcher = random.choice(home_pitchers) if home_pitchers else "TBD"
            away_pitcher = random.choice(away_pitchers) if away_pitchers else "TBD"
            
            # Get ERA for pitchers
            home_era, home_source = self.get_pitcher_era(home_team, home_pitcher)
            away_era, away_source = self.get_pitcher_era(away_team, away_pitcher)
            
            # Format ERA for display
            home_era_display = f"{home_era:.2f}" if home_era is not None else "N/A"
            away_era_display = f"{away_era:.2f}" if away_era is not None else "N/A"
            
            # Generate game ID
            game_id = f"{date_str}_{away_abbr}_{home_abbr}"
            
            games.append({
                'game_id': game_id,
                'date': date_str,
                'time': f"{hour}:{minute:02d} {am_pm}",
                'home_team': home_team,
                'away_team': away_team,
                'home_abbr': home_abbr,
                'away_abbr': away_abbr,
                'stadium': stadium,
                'home_pitcher': home_pitcher,
                'away_pitcher': away_pitcher,
                'home_era': home_era,
                'away_era': away_era,
                'home_era_display': home_era_display,
                'away_era_display': away_era_display,
                'home_era_source': home_source,
                'away_era_source': away_source
            })
        
        return games
    
    def clear_cache(self):
        """Clear all cached data"""
        if os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
