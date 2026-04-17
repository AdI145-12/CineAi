# 🎬 CineAI — Movie Recommendation System

A full-stack Flask app with Content-Based, Hybrid, and Personalized Collaborative Filtering.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add datasets
Place these files in the project root (same folder as app.py):
- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

Download from: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

### 3. Run the app
```bash
python app.py
```

Open: http://localhost:5000

## Features
- 🏆 Top movies via IMDB Weighted Rating formula
- 🔍 Movie search with live autocomplete
- 🎭 Content-Based filtering (Cast + Director + Genre + Keywords)
- 🔀 Hybrid recommendations (Content + Quality score)
- 👤 User registration & login
- ⭐ Rate movies to unlock personalized recommendations
- 🤖 Personalized recs based on your ratings history

## Deploy to GitHub + Render
See DEPLOY.md for full deployment instructions.
