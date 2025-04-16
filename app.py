import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from mlb_prediction_api import MLBPredictionAPI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='web_app.log')
logger = logging.getLogger('web_app')

app = Flask(__name__, static_folder='static', template_folder='templates')

# Initialize MLB prediction API
mlb_prediction_api = MLBPredictionAPI()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get predictions for all games"""
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    date_str = request.args.get('date')
    
    # If date is provided, use it; otherwise use today's date
    if date_str:
        try:
            # Parse the date string (format: YYYY-MM-DD)
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # If date format is invalid, use today's date
            target_date = datetime.now()
    else:
        target_date = datetime.now()
    
    # Format the date as string (YYYY-MM-DD)
    formatted_date = target_date.strftime('%Y-%m-%d')
    
    # Get predictions for the specified date
    predictions = mlb_prediction_api.get_all_predictions(force_refresh, target_date=formatted_date)
    return jsonify(predictions)

@app.route('/api/dates', methods=['GET'])
def get_available_dates():
    """Get available dates for MLB games"""
    # Get today's date
    today = datetime.now()
    
    # Generate dates for the next 7 days
    dates = []
    for i in range(7):
        date = today + timedelta(days=i)
        dates.append({
            'date': date.strftime('%Y-%m-%d'),
            'display': date.strftime('%A, %B %d, %Y')
        })
    
    return jsonify({'dates': dates})

@app.route('/api/prediction/<game_id>', methods=['GET'])
def get_prediction(game_id):
    """Get prediction for a specific game"""
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    prediction = mlb_prediction_api.get_prediction_for_game_id(game_id, force_refresh)
    
    if prediction:
        return jsonify(prediction)
    else:
        return jsonify({'error': f'Prediction not found for game ID {game_id}'}), 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version': '2.2.0',
        'data_source': 'MLB Stats API (Official)',
        'last_refresh': datetime.fromtimestamp(mlb_prediction_api.last_refresh_time).strftime("%Y-%m-%d %H:%M:%S") if mlb_prediction_api.last_refresh_time > 0 else 'Never'
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Force refresh of all data"""
    mlb_prediction_api.refresh_data_if_needed(force_refresh=True)
    return jsonify({
        'status': 'success',
        'message': 'Data refreshed successfully',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
