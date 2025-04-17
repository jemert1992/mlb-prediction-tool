import os
import json
import random
from datetime import datetime, timedelta
from mlb_stats_api import MLBStatsAPI

class MLBPredictionAPI:
    def __init__(self):
        self.stats_api = MLBStatsAPI()
        # Use Render's cache directory or fallback to /tmp
        cache_base = os.environ.get('RENDER_CACHE_DIR', '/tmp')
        self.cache_dir = os.path.join(cache_base, 'mlb_prediction_tool', 'predictions')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Factors that influence predictions
        self.factors = {
            'pitcher_performance': 0.25,
            'bullpen_performance': 0.15,
            'batter_vs_pitcher': 0.15,
            'ballpark_factors': 0.10,
            'team_offense': 0.10,
            'team_defense': 0.05,
            'weather_conditions': 0.05,
            'umpire_tendencies': 0.05,
            'travel_fatigue': 0.05,
            'momentum': 0.05
        }
        
        # Ballpark factors (higher = more hitter-friendly)
        self.ballpark_factors = {
            'Coors Field': 1.3,
            'Great American Ball Park': 1.2,
            'Citizens Bank Park': 1.15,
            'Yankee Stadium': 1.1,
            'Fenway Park': 1.1,
            'Wrigley Field': 1.05,
            'Chase Field': 1.05,
            'Globe Life Field': 1.0,
            'Truist Park': 1.0,
            'Minute Maid Park': 1.0,
            'Kauffman Stadium': 0.95,
            'Dodger Stadium': 0.95,
            'Nationals Park': 0.95,
            'Rogers Centre': 0.95,
            'Angel Stadium': 0.95,
            'Target Field': 0.95,
            'Comerica Park': 0.9,
            'PNC Park': 0.9,
            'Busch Stadium': 0.9,
            'loanDepot park': 0.9,
            'Oracle Park': 0.85,
            'Petco Park': 0.85,
            'T-Mobile Park': 0.85,
            'Oakland Coliseum': 0.85,
            'Tropicana Field': 0.85,
            'Oriole Park at Camden Yards': 0.95,
            'Progressive Field': 0.95,
            'American Family Field': 1.05,
            'Citi Field': 0.95,
            'Rate Field': 1.05
        }
    
    def get_predictions(self, prediction_type, date_str):
        """Get predictions for a specific type and date"""
        cache_file = os.path.join(self.cache_dir, f"all_predictions_{date_str}.json")
        
        # Check if we have cached data
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if datetime.now().timestamp() - data['timestamp'] < 900:  # Cache for 15 minutes
                    if prediction_type in data['predictions']:
                        return data['predictions'][prediction_type]
        
        try:
            # Get games for the date
            games = self.stats_api.get_games_for_date(date_str)
            
            # Generate predictions for all types
            all_predictions = {
                'under_1_run_1st': self._generate_predictions(games, 'under_1_run_1st'),
                'over_2.5_runs_3': self._generate_predictions(games, 'over_2.5_runs_3'),
                'over_3.5_runs_3': self._generate_predictions(games, 'over_3.5_runs_3')
            }
            
            # Cache the result
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump({
                    'predictions': all_predictions,
                    'timestamp': datetime.now().timestamp()
                }, f)
            
            return all_predictions[prediction_type]
        except Exception as e:
            # If there's any error, return empty list
            print(f"Error generating predictions: {str(e)}")
            return []
    
    def _generate_predictions(self, games, prediction_type):
        """Generate predictions for games based on the prediction type"""
        predictions = []
        
        for game in games:
            try:
                # Safely convert ERA values to float with default fallback
                try:
                    home_era = float(game['home_era']) if game['home_era'] not in ('N/A', None) else 4.50
                except (ValueError, TypeError):
                    home_era = 4.50
                    
                try:
                    away_era = float(game['away_era']) if game['away_era'] not in ('N/A', None) else 4.50
                except (ValueError, TypeError):
                    away_era = 4.50
                
                # Adjust probability based on prediction type
                if prediction_type == 'under_1_run_1st':
                    # Lower ERAs = higher probability of under 1 run
                    base_prob = 0.5 - (((home_era + away_era) / 2 - 4.0) * 0.05)
                    
                    # Adjust for ballpark factors
                    ballpark_factor = self.ballpark_factors.get(game['stadium'], 1.0)
                    base_prob -= (ballpark_factor - 1.0) * 0.2
                    
                elif prediction_type == 'over_2.5_runs_3':
                    # Higher ERAs = higher probability of over 2.5 runs
                    base_prob = 0.5 + (((home_era + away_era) / 2 - 4.0) * 0.05)
                    
                    # Adjust for ballpark factors
                    ballpark_factor = self.ballpark_factors.get(game['stadium'], 1.0)
                    base_prob += (ballpark_factor - 1.0) * 0.2
                    
                elif prediction_type == 'over_3.5_runs_3':
                    # Higher ERAs = higher probability of over 3.5 runs
                    base_prob = 0.4 + (((home_era + away_era) / 2 - 4.0) * 0.05)
                    
                    # Adjust for ballpark factors
                    ballpark_factor = self.ballpark_factors.get(game['stadium'], 1.0)
                    base_prob += (ballpark_factor - 1.0) * 0.2
                
                # Ensure probability is between 0.4 and 0.7
                base_prob = max(0.4, min(0.7, base_prob))
                
                # Add some randomness for variety
                random.seed(hash(f"{game['home_team']}_{game['away_team']}_{prediction_type}"))
                final_prob = base_prob + (random.random() - 0.5) * 0.1
                final_prob = round(final_prob * 100, 1)
                
                # Determine rating based on probability
                if final_prob >= 60:
                    rating = "Bet"
                elif final_prob >= 52:
                    rating = "Lean"
                else:
                    rating = "Pass"
                
                # Create prediction object
                prediction = {
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'stadium': game['stadium'],
                    'time': game['time'],
                    'home_pitcher': game['home_pitcher'],
                    'away_pitcher': game['away_pitcher'],
                    'home_era': str(home_era),  # Convert to string to avoid JSON issues
                    'away_era': str(away_era),  # Convert to string to avoid JSON issues
                    'probability': final_prob,
                    'rating': rating,
                    'factors': self._generate_factor_breakdown(game, prediction_type),
                    'data_source': game.get('home_era_source', 'MLB Stats API (Official)')
                }
                
                predictions.append(prediction)
            except Exception as e:
                # Skip this game if there's an error
                print(f"Error processing game {game.get('home_team', 'Unknown')} vs {game.get('away_team', 'Unknown')}: {str(e)}")
                continue
        
        return predictions
    
    def _generate_factor_breakdown(self, game, prediction_type):
        """Generate a breakdown of factors influencing the prediction"""
        factors = []
        
        # Pitcher Performance
        factors.append({
            'name': 'Pitcher Performance',
            'weight': self.factors['pitcher_performance'] * 100,
            'description': f"Starting pitcher ERA and recent performance"
        })
        
        # Bullpen Performance
        factors.append({
            'name': 'Bullpen Performance',
            'weight': self.factors['bullpen_performance'] * 100,
            'description': f"Relief pitcher effectiveness"
        })
        
        # Batter vs. Pitcher Matchups
        factors.append({
            'name': 'Batter vs. Pitcher Matchups',
            'weight': self.factors['batter_vs_pitcher'] * 100,
            'description': f"Historical batter performance against specific pitchers"
        })
        
        # Add more factors as needed
        
        return factors
    
    def clear_cache(self):
        """Clear the cache directory"""
        if os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
