# 🎬 CineAI — Movie Recommendation System

> An AI-powered, full-stack movie recommendation web application built with Flask, scikit-learn, and the TMDB 5000 dataset. Combines content-based filtering, metadata analysis, and personalized user-based recommendations into one clean interface.

---

## 🚀 Live Demo Features

| Feature | Description |
|---|---|
| 🏆 Top Movies | IMDB-style Weighted Rating formula to surface the best films |
| 🔍 Smart Search | Real-time autocomplete search across 4,800+ movies |
| 🎭 Content-Based Filtering | Metadata soup using Cast + Director + Genre + Keywords |
| 🔀 Hybrid Recommender | Content similarity re-ranked by vote quality score |
| 👤 User Authentication | Secure register / login / logout with hashed passwords |
| ⭐ Movie Ratings | Rate any movie from 1–5 stars directly from cards |
| 🤖 Personalized Recs | Dashboard-based recommendations powered by your rating history |

---

## 🧠 How the Recommendation Engines Work

### 1. Demographic Filtering (Top Movies)
Uses the IMDB Weighted Rating formula:

```
WR = (v / (v + m)) × R + (m / (m + v)) × C
```

Where `v` = movie vote count, `m` = minimum votes threshold (90th percentile), `R` = movie average rating, `C` = global mean rating.

### 2. Content-Based Filtering (Metadata Soup)
Each movie is converted into a **metadata soup** string by combining:
- Top 3 cast members (lowercased, space-removed)
- Director name
- Top 3 genres
- Top 3 keywords

A `CountVectorizer` builds a term matrix and **cosine similarity** finds the closest matches.

### 3. Hybrid Recommender
Takes the top 25 content-similar movies and re-ranks them using the weighted rating formula — combining relevance with quality.

### 4. Personalized Recommendations (User-Based)
When a user rates 3+ movies:
- Identifies movies rated 4⭐ or higher
- Finds content-similar candidates for each liked movie
- Scores candidates by similarity × user rating weight
- Filters out already-rated movies

---

## 📁 Project Structure

```
movie_recommender_flask/
├── app.py                    # Main Flask application (routes, logic, auth)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── DEPLOY.md                 # GitHub + Render deployment guide
├── .gitignore
├── templates/
│   ├── base.html             # Shared layout (navbar, flash messages, footer)
│   ├── index.html            # Homepage — top movies grid
│   ├── search.html           # Search results page
│   ├── recommend.html        # Movie recommendations (tabs: hybrid / content)
│   ├── dashboard.html        # User dashboard — ratings + personalized recs
│   ├── login.html            # Login page
│   └── register.html         # Registration page
└── static/
    ├── css/style.css         # Full design system (dark/light mode)
    └── js/main.js            # Autocomplete, tabs, flash dismiss
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+ installed
- TMDB 5000 dataset CSV files

### Step 1 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Download Dataset
Download from Kaggle and place both files in the same folder as `app.py`:

👉 [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)

- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

### Step 3 — Run the App
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🌐 Deployment

### Deploy to Render (Free)

1. Push your project to GitHub (see `DEPLOY.md` for full steps)
2. Sign up at [render.com](https://render.com)
3. Create **New Web Service** → connect your GitHub repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click Deploy 🚀

Add gunicorn first:
```bash
pip install gunicorn
echo "gunicorn>=21.0.0" >> requirements.txt
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| ML / Recommendations | scikit-learn (CountVectorizer, cosine_similarity) |
| Dataset | TMDB 5000 Movies & Credits |
| Auth | Werkzeug (password hashing) |
| Frontend | Jinja2 templates, vanilla JS, CSS custom properties |
| Styling | Custom design system — dark/light mode, fluid type scale |
| Deployment | Render / Gunicorn |

---

## 📊 Dataset

**TMDB 5000 Movie Dataset** — 4,803 movies with:
- Title, overview, genres, keywords
- Cast (actors) and crew (director)
- Vote count, vote average, popularity, revenue

Source: [Kaggle — tmdb/tmdb-movie-metadata](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)

---

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Homepage — top rated movies |
| `/search?q=` | GET | Search movies by title |
| `/recommend/<title>` | GET | Content + hybrid recommendations |
| `/dashboard` | GET | User dashboard (login required) |
| `/rate` | POST | Submit a movie rating |
| `/login` | GET/POST | User login |
| `/register` | GET/POST | New user registration |
| `/logout` | GET | Logout |
| `/api/movies?q=` | GET | JSON autocomplete API |

---

## 🔮 Future Improvements

- [ ] Add TMDB poster images to movie cards
- [ ] Integrate `scikit-surprise` SVD for true matrix factorization
- [ ] PostgreSQL or SQLite persistent storage for user ratings
- [ ] Email verification and password reset
- [ ] Movie detail pages with cast, trailer links
- [ ] Collaborative filtering using MovieLens `ratings_small.csv`
- [ ] Docker containerization for portable deployment

---

## 👤 Author

**Aditya Singh**  
B.E. Computer Science — Dronacharya Group of Institutions  
GitHub: [github.com/aditya-singh](https://github.com)  
Email: singh.masteraditya14@gmail.com

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

*Built as part of a Data Science portfolio project. Dataset credits: TMDB / Kaggle.*
