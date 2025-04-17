# MLB Prediction Tool Deployment Package

This package contains all the necessary files to deploy the MLB Prediction Tool to a custom domain.

## Files Included

- `app.py`: Main Flask application
- `mlb_prediction_api.py`: MLB prediction engine
- `mlb_stats_api.py`: Integration with MLB Stats API
- `templates/index.html`: Frontend HTML template
- `static/rating-styles.css`: CSS styles for the application
- `requirements.txt`: Python dependencies
- `Procfile`: For deployment on platforms like Heroku
- `wsgi.py`: WSGI entry point for production deployment

## Deployment Instructions

### Option 1: Deploy on a VPS or Dedicated Server

1. Install Python 3.8+ and pip
2. Install required packages: `pip install -r requirements.txt`
3. Run the application with Gunicorn: `gunicorn --bind 0.0.0.0:5000 wsgi:app`
4. Set up Nginx or Apache as a reverse proxy (configuration provided in nginx.conf)
5. Configure your DNS to point to your server's IP address

### Option 2: Deploy on Heroku

1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app: `heroku create your-app-name`
3. Push the code to Heroku: `git push heroku main`
4. Configure your DNS to create a CNAME record pointing to your-app-name.herokuapp.com

### Option 3: Deploy on PythonAnywhere

1. Create a PythonAnywhere account
2. Upload the files to your PythonAnywhere account
3. Set up a web app with Flask and WSGI configuration
4. Configure your DNS to create a CNAME record pointing to your-username.pythonanywhere.com

## DNS Configuration

To point your domain (mlb.c1632.com) to this application, you'll need to set up the following DNS records:

### If using a VPS or dedicated server:
- A Record: Point mlb.c1632.com to your server's IP address

### If using Heroku or PythonAnywhere:
- CNAME Record: Point mlb.c1632.com to your application's provided domain

## Contact

If you encounter any issues during deployment, please contact the developer for assistance.
