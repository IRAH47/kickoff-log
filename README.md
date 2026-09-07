# Kickoff Log

A Letterboxd-style review site for **eFootball** (Konami's football game) — browse
every season since PES 2021, rate them out of 10, write reviews, and see what
other players thought of each year's Master League/myClub update.

Built with Flask + SQLAlchemy + Flask-Login. Server-rendered pages, SQLite by
default, Postgres in production.

## What's included

- Browsable grid of eFootball seasons (2021–2026, real release dates/platforms)
- Accounts: sign up, log in, log out
- Rate & review any season (1.0–10.0, decimal, like a match rating), one review per user per edition, editable/deletable
- Edition page: average rating, rating distribution bar chart, all reviews
- User profile pages with review history and stats
- Search by title
- A distinct dark "pitch" visual theme (not a Bootstrap/Tailwind default)

## Run it locally

Requires Python 3.10+.

```bash
cd efootball_review
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed.py                  # creates the SQLite db + seeds the 6 seasons
python app.py                   # starts on http://localhost:5000
```

Open **http://localhost:5000**, sign up, and start rating seasons.

## Making it live for everyone

This app is a normal Flask app — it needs a real host to stay online, since it
can't run "live" from inside this chat. The easiest free option is **Render**:

### Option A — Render (free, recommended, includes a database)

1. Push this folder to a new GitHub repo.
2. Go to [render.com](https://render.com) → New → **Blueprint** → connect the repo.
   Render will read `render.yaml` in this project and automatically:
   - create a free Postgres database
   - create a free web service, install `requirements.txt`, run `seed.py`, then start with `gunicorn`
3. Click **Apply**. After the build finishes (~2 minutes) you'll get a public URL like
   `https://kickoff-log.onrender.com` that anyone can visit.

No manual environment variable setup needed — `render.yaml` wires the database
URL and a random `SECRET_KEY` for you.

*Free-tier note:* Render's free web services sleep after 15 minutes of no
traffic and take ~30–50 seconds to wake up on the next visit. That's fine for
sharing with friends; upgrade to a paid instance later if you want it always-on.

### Option B — Railway

1. Push to GitHub, then on [railway.app](https://railway.app) choose **New Project → Deploy from GitHub repo**.
2. Add a **PostgreSQL** plugin from Railway's marketplace — it sets `DATABASE_URL` automatically.
3. Set a `SECRET_KEY` variable to any random string.
4. Set the start command to `python seed.py && gunicorn app:app` (Railway auto-detects `Procfile` too).
5. Railway gives you a public `*.up.railway.app` URL.

### Option C — PythonAnywhere (simplest, no credit card)

1. Create a free account at [pythonanywhere.com](https://pythonanywhere.com).
2. Upload this folder (or `git clone` your repo) via their Bash console.
3. `pip install --user -r requirements.txt` then `python seed.py`.
4. Use the **Web** tab → "Add a new web app" → Flask → point it at `app.py`.
5. Your site is live at `yourusername.pythonanywhere.com`. Note: the free tier
   uses SQLite fine here since the disk is persistent, unlike Render's free tier.

## Project structure

```
efootball_review/
├── app.py              # routes
├── models.py           # User, Edition, Review
├── extensions.py        # db, login_manager
├── seed.py             # populates the 6 eFootball seasons
├── requirements.txt
├── Procfile             # for Render/Railway/Heroku-style hosts
├── render.yaml          # one-click Render blueprint
├── templates/
└── static/style.css
```

## Extending it

Ideas that fit naturally on top of this schema:
- Following other users / activity feed
- "Diary" of individual matches played, separate from the season review
- Lists (e.g. "Best myClub seasons")
- Likes/comments on reviews
- Player or club sub-pages within a season

All of these follow the same pattern already in `models.py` and `app.py`.
