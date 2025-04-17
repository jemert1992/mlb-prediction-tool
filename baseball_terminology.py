import requests
import json
import os
from datetime import datetime

class BaseballTerminology:
    """
    Class to provide baseball-specific terminology for predictions
    """
    
    def __init__(self):
        """Initialize the baseball terminology provider"""
        pass
    
    def get_rating_label(self, probability, prediction_type):
        """
        Get baseball-specific rating label based on probability and prediction type
        
        Args:
            probability: Prediction probability (0-100)
            prediction_type: Type of prediction ('under_1_run', 'over_2_5_runs', 'over_3_5_runs')
        
        Returns:
            Dictionary with label, icon, description, and tooltip
        """
        if prediction_type == 'under_1_run':
            # Under 1 run in first inning
            if probability >= 80:
                return {
                    "label": "Lock 🔒",
                    "icon": "🔒",
                    "description": "Elite Pitching Matchup",
                    "tooltip": "Top-tier pitchers facing struggling offenses, extremely high confidence"
                }
            elif probability >= 70:
                return {
                    "label": "Green Light 🟢",
                    "icon": "🟢",
                    "description": "Strong Pitching Edge",
                    "tooltip": "Quality starters with history of scoreless first innings"
                }
            elif probability >= 60:
                return {
                    "label": "Favorable ⚾️",
                    "icon": "⚾️",
                    "description": "Pitching Advantage",
                    "tooltip": "Pitchers have edge over opposing lineups in first inning"
                }
            elif probability >= 50:
                return {
                    "label": "Even Odds",
                    "icon": "⚖️",
                    "description": "Balanced Matchup",
                    "tooltip": "Neither pitching nor hitting has a significant advantage"
                }
            elif probability >= 40:
                return {
                    "label": "Caution",
                    "icon": "⚠️",
                    "description": "Hitting Advantage",
                    "tooltip": "Offenses likely to score in the first inning"
                }
            else:
                return {
                    "label": "Avoid",
                    "icon": "🚫",
                    "description": "Strong Hitting Matchup",
                    "tooltip": "High probability of first inning scoring, avoid this under bet"
                }
        else:
            # Over runs predictions
            if probability >= 80:
                return {
                    "label": "Lock 🔒",
                    "icon": "🔒",
                    "description": "Elite Hitting Matchup",
                    "tooltip": "Top offenses facing struggling pitchers, extremely high confidence"
                }
            elif probability >= 70:
                return {
                    "label": "Green Light 🟢",
                    "icon": "🟢",
                    "description": "Strong Hitting Edge",
                    "tooltip": "Quality offenses with history of early inning scoring"
                }
            elif probability >= 60:
                return {
                    "label": "Favorable ⚾️",
                    "icon": "⚾️",
                    "description": "Hitting Advantage",
                    "tooltip": "Batters have edge over opposing pitchers in early innings"
                }
            elif probability >= 50:
                return {
                    "label": "Even Odds",
                    "icon": "⚖️",
                    "description": "Balanced Matchup",
                    "tooltip": "Neither hitting nor pitching has a significant advantage"
                }
            elif probability >= 40:
                return {
                    "label": "Caution",
                    "icon": "⚠️",
                    "description": "Pitching Advantage",
                    "tooltip": "Pitchers likely to limit scoring in early innings"
                }
            else:
                return {
                    "label": "Avoid",
                    "icon": "🚫",
                    "description": "Strong Pitching Matchup",
                    "tooltip": "High probability of limited scoring, avoid this over bet"
                }
    
    def get_trend_description(self, trend):
        """
        Get description for trend indicator
        
        Args:
            trend: Trend indicator (↑↑, ↑, →, ↓, ↓↓)
        
        Returns:
            Description of the trend
        """
        if trend == "↑↑":
            return "Rapidly Improving"
        elif trend == "↑":
            return "Improving"
        elif trend == "→":
            return "Stable"
        elif trend == "↓":
            return "Declining"
        elif trend == "↓↓":
            return "Rapidly Declining"
        else:
            return "Unknown Trend"
    
    def get_factor_description(self, factor_name):
        """
        Get baseball-specific description for prediction factors
        
        Args:
            factor_name: Name of the factor
        
        Returns:
            Description of the factor
        """
        descriptions = {
            'pitcher_performance': "Starting Pitcher Quality",
            'batter_matchups': "Batter vs. Pitcher History",
            'ballpark_factors': "Stadium Run-Scoring Impact",
            'weather_impact': "Weather Conditions Effect",
            'umpire_impact': "Home Plate Umpire Tendencies",
            'bullpen': "Relief Pitcher Availability",
            'defense': "Defensive Metrics & Fielding",
            'momentum': "Team's Recent Performance Trend",
            'travel_fatigue': "Travel Schedule Impact",
            'baserunning': "Base Running Efficiency"
        }
        
        return descriptions.get(factor_name, factor_name.replace('_', ' ').title())
    
    def get_why_badges(self, features, factors):
        """
        Generate "Why" badges explaining prediction context
        
        Args:
            features: Game features
            factors: Factor scores
        
        Returns:
            List of badges with explanations
        """
        badges = []
        
        # Check for strong pitching
        if features.get('home_pitcher_era', 5.0) < 3.0 or features.get('away_pitcher_era', 5.0) < 3.0:
            badges.append({
                "label": "Ace Pitcher",
                "icon": "🔥",
                "description": "Elite starter on the mound"
            })
        
        # Check for ballpark factor
        if features.get('ballpark_runs_factor', 1.0) < 0.9:
            badges.append({
                "label": "Pitcher's Park",
                "icon": "🏟️",
                "description": "Stadium favors pitchers"
            })
        elif features.get('ballpark_runs_factor', 1.0) > 1.1:
            badges.append({
                "label": "Hitter's Park",
                "icon": "🏟️",
                "description": "Stadium favors hitters"
            })
        
        # Check for weather impact
        if features.get('weather_condition', '').lower() in ['rain', 'drizzle', 'thunderstorm']:
            badges.append({
                "label": "Weather Factor",
                "icon": "🌧️",
                "description": "Precipitation may affect play"
            })
        elif features.get('temperature', 70) < 50:
            badges.append({
                "label": "Cold Weather",
                "icon": "❄️",
                "description": "Cold temperatures favor pitchers"
            })
        elif features.get('temperature', 70) > 85:
            badges.append({
                "label": "Hot Weather",
                "icon": "🔥",
                "description": "Heat favors hitters"
            })
        
        # Check for wind
        if features.get('wind_speed', 5) > 15:
            badges.append({
                "label": "Wind Factor",
                "icon": "💨",
                "description": "Strong winds may affect ball flight"
            })
        
        # Check top factors
        top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:2]
        for factor, score in top_factors:
            if score > 70:
                badges.append({
                    "label": self.get_factor_description(factor),
                    "icon": "⭐",
                    "description": f"Strong {self.get_factor_description(factor).lower()} advantage"
                })
        
        return badges

# Test the baseball terminology
if __name__ == "__main__":
    terminology = BaseballTerminology()
    
    # Test rating labels
    for prob in [85, 75, 65, 55, 45, 35]:
        under_rating = terminology.get_rating_label(prob, 'under_1_run')
        over_rating = terminology.get_rating_label(prob, 'over_2_5_runs')
        
        print(f"Probability {prob}%:")
        print(f"  Under 1 Run: {under_rating['label']} - {under_rating['description']}")
        print(f"  Over 2.5 Runs: {over_rating['label']} - {over_rating['description']}")
    
    # Test trend descriptions
    for trend in ["↑↑", "↑", "→", "↓", "↓↓"]:
        print(f"Trend {trend}: {terminology.get_trend_description(trend)}")
    
    # Test factor descriptions
    factors = ['pitcher_performance', 'ballpark_factors', 'weather_impact']
    for factor in factors:
        print(f"Factor '{factor}': {terminology.get_factor_description(factor)}")
    
    # Test why badges
    features = {
        'home_pitcher_era': 2.5,
        'away_pitcher_era': 4.2,
        'ballpark_runs_factor': 0.85,
        'weather_condition': 'Clear',
        'temperature': 65,
        'wind_speed': 8
    }
    
    factors = {
        'pitcher_performance': 85,
        'batter_matchups': 60,
        'ballpark_factors': 75,
        'weather_impact': 50
    }
    
    badges = terminology.get_why_badges(features, factors)
    print("\nWhy Badges:")
    for badge in badges:
        print(f"  {badge['icon']} {badge['label']}: {badge['description']}")
