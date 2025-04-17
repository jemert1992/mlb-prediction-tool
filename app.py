import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from mlb_prediction_api import MLBPredictionAPI
from mlb_stats_api import MLBStatsAPI

app = Flask(__name__)
prediction_api = MLBPredictionAPI()
stats_api = MLBStatsAPI()

@app.route('/')
def index():
    """Render the main page"""
    # Get current date in YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', date=today, now=now)

@app.route('/api/predictions')
def get_predictions():
    """API endpoint to get predictions"""
    prediction_type = request.args.get('type', 'under_1_run_1st')
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Map prediction type to internal type
    type_mapping = {
        'under_1_run_1st': 'under_1_run_1st',
        'over_2.5_runs_3': 'over_2.5_runs_3',
        'over_3.5_runs_3': 'over_3.5_runs_3'
    }
    
    internal_type = type_mapping.get(prediction_type, 'under_1_run_1st')
    
    try:
        predictions = prediction_api.get_predictions(internal_type, date_str)
        return jsonify(predictions)
    except Exception as e:
        app.logger.error(f"Error getting predictions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh')
def refresh_data():
    """API endpoint to refresh data"""
    try:
        # Clear caches
        stats_api.clear_cache()
        prediction_api.clear_cache()
        return jsonify({"status": "success", "message": "Data refreshed successfully"})
    except Exception as e:
        app.logger.error(f"Error refreshing data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('index.html', error="Server error occurred"), 500

# Create cache directories in a location Render can write to
cache_dir = os.path.join(os.environ.get('RENDER_CACHE_DIR', '/tmp'), 'mlb_prediction_tool')
os.makedirs(os.path.join(cache_dir, 'mlb_stats'), exist_ok=True)
os.makedirs(os.path.join(cache_dir, 'predictions'), exist_ok=True)

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
