from flask import Flask, jsonify, render_template, request
import os
import json
import logging
from datetime import datetime, timedelta
from mlb_prediction_api import MLBPredictionAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log')
logger = logging.getLogger('app')

# Initialize Flask app
app = Flask(__name__)

# Initialize MLB prediction API
mlb_prediction_api = MLBPredictionAPI()

@app.route('/')
def index():
    """
    Render the index page
    """
    return render_template('index.html')

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """
    Get all predictions for a specific date
    """
    try:
        # Get query parameters
        date_str = request.args.get('date')
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Get predictions
        predictions = mlb_prediction_api.get_all_predictions(force_refresh, date_str)
        
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<prediction_type>', methods=['GET'])
def get_predictions_by_type(prediction_type):
    """
    Get predictions for a specific type and date
    """
    try:
        # Get query parameters
        date_str = request.args.get('date')
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Map prediction type to key
        prediction_type_map = {
            'under_1_run_1st': 'under_1_run_first_inning',
            'over_2.5_runs_first_3': 'over_2.5_runs_first_3_innings',
            'over_3.5_runs_first_3': 'over_3.5_runs_first_3_innings'
        }
        
        prediction_key = prediction_type_map.get(prediction_type)
        
        if not prediction_key:
            return jsonify({'error': 'Invalid prediction type'}), 400
        
        # Get predictions
        all_predictions = mlb_prediction_api.get_all_predictions(force_refresh, date_str)
        
        # Get predictions for the specified type
        predictions = all_predictions.get(prediction_key, [])
        
        # Add metadata
        result = {
            'predictions': predictions,
            'metadata': all_predictions.get('metadata', {})
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting predictions by type: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dates', methods=['GET'])
def get_available_dates():
    """
    Get available dates for predictions
    """
    try:
        # Generate dates (7 days before and after today)
        today = datetime.now()
        dates = []
        
        for i in range(-7, 8):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            date_display = date.strftime('%A, %B %d, %Y')
            
            dates.append({
                'date': date_str,
                'display': date_display,
                'is_today': i == 0
            })
        
        return jsonify(dates)
    except Exception as e:
        logger.error(f"Error getting available dates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """
    Refresh all data
    """
    try:
        # Force refresh
        mlb_prediction_api.refresh_data_if_needed(True)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get API status
    """
    try:
        # Get current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get last refresh time
        last_refresh_time = datetime.fromtimestamp(mlb_prediction_api.last_refresh_time).strftime('%Y-%m-%d %H:%M:%S') if mlb_prediction_api.last_refresh_time > 0 else 'Never'
        
        return jsonify({
            'status': 'online',
            'current_time': current_time,
            'last_refresh_time': last_refresh_time,
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create cache directories in a location Render can write to
    cache_base = os.environ.get('RENDER_CACHE_DIR', '/tmp')
    os.makedirs(os.path.join(cache_base, 'mlb_prediction_tool', 'mlb_stats'), exist_ok=True)
    os.makedirs(os.path.join(cache_base, 'mlb_prediction_tool', 'predictions'), exist_ok=True)
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
