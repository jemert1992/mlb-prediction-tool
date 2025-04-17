import requests
import json
import os
from datetime import datetime

class FirstInningStatsAPI:
    """
    Class to fetch and analyze first inning statistics for MLB teams
    """
    
    def __init__(self):
        """Initialize the First Inning Stats API client"""
        self.cache_dir = 'cache/first_inning'
        self.cache_expiry = 3600 * 12  # Cache expiry in seconds (12 hours)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # This would ideally connect to a specialized database of first inning stats
        # For now, we'll use a combination of MLB Stats API data and specialized calculations
        from mlb_stats_api import MLBStatsAPI
        self.mlb_api = MLBStatsAPI()
    
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
                print(f"Error reading first inning stats cache: {e}")
        
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
            print(f"Error saving first inning stats to cache: {e}")
            return False
    
    def get_first_inning_stats(self, team_id):
        """
        Get first inning scoring statistics for a team
        """
        cache_key = f"first_inning_{team_id}"
        cached_data = self.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # In a production environment, this would fetch from a specialized database
            # For now, we'll use team stats to estimate first inning performance
            
            # Get team's overall stats
            team_stats_data = self.mlb_api.get_team_stats(team_id)
            team_stats = {}
            
            if team_stats_data.get('stats') and len(team_stats_data['stats']) > 0:
                for stat in team_stats_data['stats'][0].get('splits', []):
                    team_stats = stat.get('stat', {})
            
            # Get team's pitching stats
            pitching_stats_data = self.mlb_api.get_team_stats(team_id, "pitching")
            pitching_stats = {}
            
            if pitching_stats_data.get('stats') and len(pitching_stats_data['stats']) > 0:
                for stat in pitching_stats_data['stats'][0].get('splits', []):
                    pitching_stats = stat.get('stat', {})
            
            # Calculate first inning stats
            games_played = team_stats.get('gamesPlayed', 0)
            if games_played == 0:
                games_played = 1  # Avoid division by zero
            
            # Estimate runs per first inning (typically about 10-15% of total runs)
            runs_per_game = team_stats.get('runs', 0) / games_played
            first_inning_runs = runs_per_game * 0.12
            
            # Estimate scoreless first inning percentage
            team_era = pitching_stats.get('era', 4.0)
            scoreless_pct = max(0.0, min(1.0, 0.7 - (team_era - 4.0) * 0.05))
            
            # Create first inning stats object
            first_inning_stats = {
                'runsPerFirstInning': first_inning_runs,
                'firstInningRunsLast10': first_inning_runs * 10,  # Total over 10 games
                'scorelessFirstInningPct': scoreless_pct,
                'gamesPlayed': games_played,
                'totalFirstInningRuns': first_inning_runs * games_played
            }
            
            # Save to cache
            self.save_to_cache(cache_key, first_inning_stats)
            
            return first_inning_stats
        except Exception as e:
            print(f"Error calculating first inning stats: {e}")
            return {
                'runsPerFirstInning': 0.5,
                'firstInningRunsLast10': 5.0,
                'scorelessFirstInningPct': 0.5,
                'gamesPlayed': 1,
                'totalFirstInningRuns': 0.5
            }
    
    def get_first_inning_matchup(self, home_team_id, away_team_id):
        """
        Analyze first inning matchup between two teams
        """
        home_stats = self.get_first_inning_stats(home_team_id)
        away_stats = self.get_first_inning_stats(away_team_id)
        
        # Calculate combined probability of scoreless first inning
        combined_scoreless_prob = (home_stats['scorelessFirstInningPct'] + away_stats['scorelessFirstInningPct']) / 2
        
        # Calculate expected runs in first inning
        expected_runs = home_stats['runsPerFirstInning'] + away_stats['runsPerFirstInning']
        
        # Calculate under 1 run probability
        under_1_run_prob = combined_scoreless_prob * 0.8  # Adjust for possibility of exactly 1 run
        
        return {
            'homeTeamStats': home_stats,
            'awayTeamStats': away_stats,
            'combinedScorelessProb': combined_scoreless_prob,
            'expectedRuns': expected_runs,
            'under1RunProb': under_1_run_prob
        }

# Test the First Inning Stats API
if __name__ == "__main__":
    first_inning_api = FirstInningStatsAPI()
    
    # Test with Yankees and Red Sox
    yankees_id = 147  # NYY
    red_sox_id = 111  # BOS
    
    yankees_stats = first_inning_api.get_first_inning_stats(yankees_id)
    red_sox_stats = first_inning_api.get_first_inning_stats(red_sox_id)
    
    print("Yankees First Inning Stats:")
    print(f"Runs per first inning: {yankees_stats['runsPerFirstInning']:.2f}")
    print(f"Scoreless first inning %: {yankees_stats['scorelessFirstInningPct']:.2f}")
    
    print("\nRed Sox First Inning Stats:")
    print(f"Runs per first inning: {red_sox_stats['runsPerFirstInning']:.2f}")
    print(f"Scoreless first inning %: {red_sox_stats['scorelessFirstInningPct']:.2f}")
    
    # Test matchup analysis
    matchup = first_inning_api.get_first_inning_matchup(yankees_id, red_sox_id)
    print("\nMatchup Analysis:")
    print(f"Expected runs in first inning: {matchup['expectedRuns']:.2f}")
    print(f"Under 1 run probability: {matchup['under1RunProb']:.2f}")
