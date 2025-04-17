# Vercel-GitHub Integration Guide for MLB Prediction Tool

This guide will help your buddy connect Vercel to your GitHub repository and deploy the MLB prediction tool to mlb.c1632.com.

## 1. Create a Vercel Account

1. Go to [Vercel](https://vercel.com) and sign up for an account
2. Complete the registration process
3. Choose the free Hobby plan (sufficient for this application)

## 2. Connect Vercel to GitHub

1. In the Vercel dashboard, click "Add New..." > "Project"
2. Select "Continue with GitHub" and authorize Vercel to access GitHub
3. Select your "mlb-prediction-tool" repository from the list
4. Vercel will automatically detect the Python application

## 3. Configure Project Settings

1. In the project configuration screen:
   - **Framework Preset**: Select "Other"
   - **Root Directory**: Leave as `.` (default)
   - **Build Command**: Leave blank (Vercel will use the vercel.json configuration)
   - **Output Directory**: Leave blank
   - **Install Command**: `pip install -r requirements.txt`

2. Click "Deploy" to start the deployment process

## 4. Set Up Custom Domain (mlb.c1632.com)

1. After deployment completes, go to the project dashboard
2. Click on "Domains" in the left sidebar
3. Click "Add" and enter `mlb.c1632.com`
4. Vercel will provide DNS configuration instructions:
   - **Record Type**: CNAME
   - **Name**: @ or mlb (depending on DNS provider)
   - **Value**: The Vercel-provided domain (e.g., mlb-prediction-tool.vercel.app)
   - **TTL**: 3600 (or as recommended by your DNS provider)

5. Configure these DNS settings with your domain provider
6. Return to Vercel and click "Verify" to confirm the domain setup

## 5. Automatic Deployments

1. Vercel is now connected to your GitHub repository
2. Any changes pushed to GitHub will automatically trigger a new deployment
3. Your buddy doesn't need to do anything for future updates
4. The website at mlb.c1632.com will always have your latest changes

## Troubleshooting

### If the deployment fails:
1. Check the build logs in Vercel for error messages
2. Ensure all dependencies are listed in requirements.txt
3. Verify the vercel.json configuration is correct

### If the domain doesn't connect:
1. Ensure DNS records are correctly configured
2. DNS propagation can take up to 24-48 hours
3. Use [dnschecker.org](https://dnschecker.org) to verify DNS propagation

## Monitoring and Analytics

1. Vercel provides basic analytics for your deployment
2. View deployment status, performance metrics, and logs in the Vercel dashboard
3. Set up alerts for deployment failures (optional)

## Contact

If your buddy encounters any issues during the Vercel setup, they can refer to the [Vercel documentation](https://vercel.com/docs) or contact you for assistance.
