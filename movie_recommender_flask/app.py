import os
import pickle
import pandas as pd
import numpy as np
from ast import literal_eval
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

import urllib.request

def download_datasets():
    base = "https://huggingface.co/datasets/PandaBear900/cineai-tmdb/resolve/main"
    files = {
        "tmdb_5000_movies.csv": f"{base}/tmdb_5000_movies.csv",
        "tmdb_5000_credits.csv": f"{base}/tmdb_5000_credits.csv"
    }
    for filename, url in files.items():
        if not os.path.exists(filename):
            print(f"Downloading {filename} from HuggingFace...")
            urllib.request.urlretrieve(url, filename)
            print(f"✅ {filename} ready!")

download_datasets()

app = Flask(__name__)
app.secret_key = "movie_recommender_secret_2024"

# ─── In-memory user store (replace with DB in production) ───
USERS = {}
USER_RATINGS = {}  # {username: {movie_title: rating}}

# ─── Load & Prepare Data ────────────────────────────────────
def load_data():
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")
    credits.columns = ["id", "title", "cast", "crew"]
    movies = movies.merge(credits, on="id").reset_index(drop=True)

    features = ["cast", "crew", "keywords", "genres"]
    for f in features:
        movies[f] = movies[f].apply(literal_eval)

    def get_director(crew):
        for m in crew:
            if m.get("job") == "Director":
                return m["name"]
        return ""

    def get_list(x):
        names = [i["name"] for i in x] if isinstance(x, list) else []
        return names[:3]

    def clean(x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        elif isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        return ""

    movies["director"] = movies["crew"].apply(get_director)
    movies["cast_list"] = movies["cast"].apply(get_list)
    movies["keywords_list"] = movies["keywords"].apply(get_list)
    movies["genres_list"] = movies["genres"].apply(get_list)

    for col in ["cast_list", "keywords_list", "genres_list", "director"]:
        movies[col] = movies[col].apply(clean)

    def soup(x):
        return " ".join(x["keywords_list"]) + " " + " ".join(x["cast_list"]) + " " + x["director"] + " " + " ".join(x["genres_list"])

    movies["soup"] = movies.apply(soup, axis=1)
    movies["overview"] = movies["overview"].fillna("")

    count = CountVectorizer(stop_words="english")
    count_matrix = count.fit_transform(movies["soup"])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    indices = pd.Series(movies.index, index=movies["title_x"]).drop_duplicates()
    return movies, cosine_sim, indices

print("Loading data...")
try:
    movies_df, cosine_sim, indices = load_data()
    print(f"Data loaded: {len(movies_df)} movies")
    DATA_LOADED = True
except Exception as e:
    print(f"Warning: Could not load data - {e}")
    DATA_LOADED = False
    movies_df = pd.DataFrame()
    cosine_sim = None
    indices = None

# ─── Weighted Rating ────────────────────────────────────────
def get_top_movies(n=20):
    C = movies_df["vote_average"].mean()
    m = movies_df["vote_count"].quantile(0.9)
    q = movies_df[movies_df["vote_count"] >= m].copy()
    q["score"] = q.apply(lambda x: (x["vote_count"]/(x["vote_count"]+m)*x["vote_average"]) + (m/(m+x["vote_count"])*C), axis=1)
    q = q.sort_values("score", ascending=False)
    return q[["title_x", "vote_average", "vote_count", "genres", "overview", "score"]].head(n).to_dict("records")

# ─── Content-Based Recs ──────────────────────────────────────
def get_content_recs(title, n=10):
    if not DATA_LOADED or title not in indices:
        return []
    idx = indices[title]
    sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)[1:n+1]
    movie_indices = [i[0] for i in sim_scores]
    results = movies_df.iloc[movie_indices][["title_x", "vote_average", "vote_count", "overview", "genres"]].copy()
    results["similarity"] = [round(s[1]*100, 1) for s in sim_scores]
    return results.to_dict("records")

# ─── SVD Collaborative Filtering ────────────────────────────
def get_svd_recs(username, n=10):
    if username not in USER_RATINGS or len(USER_RATINGS[username]) < 3:
        return [], "Rate at least 3 movies to get personalized recommendations!"

    user_ratings = USER_RATINGS[username]
    rated_titles = set(user_ratings.keys())

    # Build user preference profile from rated movies
    liked = [t for t, r in user_ratings.items() if r >= 4]

    if not liked:
        return [], "Rate some movies 4+ stars to get personalized recommendations!"

    # Aggregate content vectors of liked movies and find similar ones
    candidate_scores = {}
    for liked_title in liked:
        recs = get_content_recs(liked_title, n=20)
        for rec in recs:
            t = rec["title_x"]
            if t not in rated_titles:
                score = rec.get("similarity", 0) * user_ratings.get(liked_title, 5) / 5
                candidate_scores[t] = candidate_scores.get(t, 0) + score

    if not candidate_scores:
        return [], "Not enough data for personalized recs yet."

    # Blend with vote quality
    top_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:30]
    results = []
    for title, score in top_candidates:
        row = movies_df[movies_df["title_x"] == title]
        if not row.empty:
            results.append({
                "title_x": title,
                "vote_average": float(row.iloc[0]["vote_average"]),
                "overview": str(row.iloc[0]["overview"])[:200],
                "personalized_score": round(score, 2)
            })
    return results[:n], None

# ─── Hybrid Recs ─────────────────────────────────────────────
def hybrid_recommend(title, n=10):
    recs = get_content_recs(title, n=25)
    if not recs:
        return []
    df = pd.DataFrame(recs)
    m = df["vote_count"].quantile(0.6)
    C = df["vote_average"].mean()
    df["hybrid_score"] = df.apply(
        lambda x: (x["vote_count"]/(x["vote_count"]+m)*x["vote_average"]) + (m/(m+x["vote_count"])*C), axis=1
    )
    df = df.sort_values("hybrid_score", ascending=False)
    return df.head(n).to_dict("records")

# ─── Auth Helpers ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── Routes ──────────────────────────────────────────────────
@app.route("/")
def index():
    top_movies = get_top_movies(20) if DATA_LOADED else []
    for m in top_movies:
        if isinstance(m["genres"], str):
            try:
                m["genres"] = [g["name"] for g in literal_eval(m["genres"])][:3]
            except:
                m["genres"] = []
    return render_template("index.html", top_movies=top_movies, data_loaded=DATA_LOADED)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query or not DATA_LOADED:
        return render_template("search.html", results=[], query=query)
    mask = movies_df["title_x"].str.contains(query, case=False, na=False)
    results = movies_df[mask][["title_x", "vote_average", "vote_count", "overview", "genres"]].head(20).to_dict("records")
    for r in results:
        if isinstance(r["genres"], str):
            try:
                r["genres"] = [g["name"] for g in literal_eval(r["genres"])][:3]
            except:
                r["genres"] = []
    return render_template("search.html", results=results, query=query)

@app.route("/recommend/<path:title>")
def recommend(title):
    content_recs = get_content_recs(title, 10)
    hybrid_recs = hybrid_recommend(title, 10)
    for recs in [content_recs, hybrid_recs]:
        for r in recs:
            if isinstance(r.get("genres"), str):
                try:
                    r["genres"] = [g["name"] for g in literal_eval(r["genres"])][:3]
                except:
                    r["genres"] = []
    movie_info = movies_df[movies_df["title_x"] == title]
    movie = movie_info.iloc[0].to_dict() if not movie_info.empty else {}
    if isinstance(movie.get("genres"), str):
        try:
            movie["genres"] = [g["name"] for g in literal_eval(movie["genres"])][:3]
        except:
            movie["genres"] = []
    return render_template("recommend.html", title=title, movie=movie,
                           content_recs=content_recs, hybrid_recs=hybrid_recs)

@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    user_ratings = USER_RATINGS.get(username, {})
    svd_recs, message = get_svd_recs(username)
    return render_template("dashboard.html", username=username,
                           user_ratings=user_ratings, svd_recs=svd_recs, message=message)

@app.route("/rate", methods=["POST"])
@login_required
def rate_movie():
    username = session["username"]
    title = request.form.get("title")
    rating = float(request.form.get("rating", 0))
    if title and 1 <= rating <= 5:
        if username not in USER_RATINGS:
            USER_RATINGS[username] = {}
        USER_RATINGS[username][title] = rating
        flash(f"Rated '{title}' — {rating}⭐", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if username in USERS and check_password_hash(USERS[username], password):
            session["username"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Username and password required.", "danger")
        elif username in USERS:
            flash("Username already taken.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        else:
            USERS[username] = generate_password_hash(password)
            USER_RATINGS[username] = {}
            session["username"] = username
            flash(f"Account created! Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/api/movies")
def api_movies():
    q = request.args.get("q", "")
    if not DATA_LOADED:
        return jsonify([])
    mask = movies_df["title_x"].str.contains(q, case=False, na=False)
    titles = movies_df[mask]["title_x"].head(10).tolist()
    return jsonify(titles)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

