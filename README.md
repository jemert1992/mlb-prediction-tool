# MLB Prediction Tool

A comprehensive MLB prediction tool that provides insights for baseball betting, focusing on first inning and early game predictions.

## Features

- Real-time data from the MLB Stats API
- Multiple prediction types:
  - Under 1 Run in 1st Inning
  - Over 2.5 Runs in First 3 Innings
  - Over 3.5 Runs in First 3 Innings
- Date navigation to view predictions for different days
- Detailed factor breakdown for each prediction
- Responsive design with dark mode support
- Automatic data refresh every 15 minutes

## Deployment on Render

This application is configured for deployment on Render.com.

### Deployment Steps

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Python Version**: 3.9.0

Alternatively, you can use the included `render.yaml` file for deployment:

```bash
render blueprint apply
```

## Local Development

To run the application locally:

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser to `http://localhost:8080`

## Project Structure

- `app.py` - Main Flask application
- `mlb_prediction_api.py` - Prediction engine
- `mlb_stats_api.py` - MLB data integration
- `templates/` - HTML templates
- `static/` - CSS and other static files
- `cache/` - Temporary data cache (created automatically)

## Data Sources

All MLB data is sourced from the official MLB Stats API, ensuring accurate and up-to-date information for predictions.

## License

MIT
