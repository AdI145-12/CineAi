# 🚀 Deployment Guide — GitHub + Render

## Step 1: Push to GitHub

```bash
# Inside movie_recommender_flask folder
git init
git add .
git commit -m "Initial commit: CineAI Flask app"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/cineai.git
git branch -M main
git push -u origin main
```

## Step 2: Add datasets to GitHub (or use Kaggle API)
Since CSVs are large, add them before pushing:
- Remove *.csv from .gitignore temporarily
- git add *.csv && git commit -m "Add datasets"

## Step 3: Deploy on Render (Free)
1. Go to https://render.com and sign up
2. Click "New Web Service"
3. Connect your GitHub repo
4. Settings:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Click Deploy!

## Add gunicorn for production
```bash
pip install gunicorn
echo "gunicorn>=21.0.0" >> requirements.txt
```
