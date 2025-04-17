# MLB Prediction Tool - GitHub Repository Setup Guide

This guide will help you set up a GitHub repository for your MLB prediction tool and connect it to Manus for seamless updates.

## 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in to your account
2. Click the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "mlb-prediction-tool")
4. Add a description (optional): "MLB Prediction Tool with real-time data from MLB Stats API"
5. Choose "Public" or "Private" visibility (Private recommended for personal projects)
6. Check "Add a README file"
7. Click "Create repository"

## 2. Upload Files to GitHub

### Option 1: Using GitHub Web Interface
1. In your new repository, click "Add file" > "Upload files"
2. Drag and drop all the files from the mlb_prediction_tool.zip package
3. Add a commit message: "Initial commit - MLB Prediction Tool"
4. Click "Commit changes"

### Option 2: Using Git Command Line
1. Extract the mlb_prediction_tool.zip package to a local folder
2. Open a terminal/command prompt in that folder
3. Run the following commands:
   ```
   git init
   git add .
   git commit -m "Initial commit - MLB Prediction Tool"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/mlb-prediction-tool.git
   git push -u origin main
   ```

## 3. Connect Manus to GitHub

1. In Manus, create a new task
2. Mention that you want to connect to your GitHub repository
3. Provide your GitHub repository URL: `https://github.com/YOUR_USERNAME/mlb-prediction-tool`
4. Manus will guide you through the authentication process
5. Once connected, you can make changes to your code in Manus
6. When you're ready to update, ask Manus to push the changes to GitHub

## 4. Making Updates via Manus

1. Make your desired changes to the MLB prediction tool in Manus
2. Test the changes to ensure they work correctly
3. Ask Manus to commit and push the changes to GitHub
4. Provide a commit message describing your changes
5. Manus will update your GitHub repository automatically

## Important Files

- `vercel.json`: Configuration file for Vercel deployment
- `app.py`: Main Flask application
- `mlb_prediction_api.py`: MLB prediction engine
- `mlb_stats_api.py`: Integration with MLB Stats API
- `templates/index.html`: Frontend HTML template
- `static/rating-styles.css`: CSS styles for the application
- `requirements.txt`: Python dependencies
- `wsgi.py`: WSGI entry point for production deployment

## Next Steps

After setting up your GitHub repository and connecting it to Manus, you'll need to:
1. Share the GitHub repository URL with your buddy
2. Have your buddy connect Vercel to your GitHub repository
3. Configure the custom domain (mlb.c1632.com) in Vercel

These steps are covered in the Vercel-GitHub Integration Guide.
