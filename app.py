import os
from datetime import date, datetime

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from sqlalchemy import func

from extensions import db, login_manager
from models import User, Edition, Review


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-me")
    db_url = os.environ.get("DATABASE_URL", "sqlite:///efootball_review.db")
    # Render/Heroku give postgres:// — SQLAlchemy wants postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    # ---------- Home / browse ----------

    @app.route("/")
    def index():
        q = request.args.get("q", "").strip()
        query = Edition.query
        if q:
            query = query.filter(Edition.title.ilike(f"%{q}%"))
        editions = query.order_by(Edition.release_date.desc()).all()

        recent_reviews = (
            Review.query.order_by(Review.created_at.desc()).limit(6).all()
        )
        return render_template(
            "index.html", editions=editions, q=q, recent_reviews=recent_reviews
        )

    # ---------- Auth ----------

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            error = None
            if not username or len(username) < 3:
                error = "Username must be at least 3 characters."
            elif not email or "@" not in email:
                error = "Enter a valid email."
            elif len(password) < 6:
                error = "Password must be at least 6 characters."
            elif User.query.filter_by(username=username).first():
                error = "That username is taken."
            elif User.query.filter_by(email=email).first():
                error = "That email is already registered."

            if error:
                flash(error, "error")
                return render_template("register.html", username=username, email=email)

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Welcome, {username}. Your squad is ready.", "success")
            return redirect(url_for("index"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        if request.method == "POST":
            identifier = request.form.get("identifier", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter(
                (func.lower(User.username) == identifier) | (User.email == identifier)
            ).first()
            if user and user.check_password(password):
                login_user(user)
                flash("Logged in.", "success")
                next_url = request.args.get("next")
                return redirect(next_url or url_for("index"))
            flash("Wrong username/email or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    # ---------- Editions ----------

    @app.route("/edition/<slug>")
    def edition_detail(slug):
        edition = Edition.query.filter_by(slug=slug).first_or_404()
        reviews = (
            edition.reviews.order_by(Review.created_at.desc()).all()
        )
        my_review = None
        if current_user.is_authenticated:
            my_review = edition.reviews.filter_by(user_id=current_user.id).first()
        return render_template(
            "edition_detail.html", edition=edition, reviews=reviews, my_review=my_review
        )

    # ---------- Reviews ----------

    @app.route("/edition/<slug>/review", methods=["GET", "POST"])
    @login_required
    def write_review(slug):
        edition = Edition.query.filter_by(slug=slug).first_or_404()
        existing = edition.reviews.filter_by(user_id=current_user.id).first()

        if request.method == "POST":
            try:
                rating = float(request.form.get("rating", ""))
            except ValueError:
                rating = None
            body = request.form.get("body", "").strip()
            played_on_raw = request.form.get("played_on", "")

            if rating is None or not (1 <= rating <= 10):
                flash("Give a rating between 1 and 10.", "error")
                draft = {
                    "rating": request.form.get("rating", ""),
                    "body": body,
                    "played_on": played_on_raw,
                }
                return render_template(
                    "write_review.html", edition=edition, review=existing, draft=draft
                )

            try:
                played_on = (
                    datetime.strptime(played_on_raw, "%Y-%m-%d").date()
                    if played_on_raw
                    else date.today()
                )
            except ValueError:
                played_on = date.today()

            if existing:
                existing.rating = rating
                existing.body = body
                existing.played_on = played_on
                flash("Review updated.", "success")
            else:
                review = Review(
                    user_id=current_user.id,
                    edition_id=edition.id,
                    rating=rating,
                    body=body,
                    played_on=played_on,
                )
                db.session.add(review)
                flash("Review posted.", "success")
            db.session.commit()
            return redirect(url_for("edition_detail", slug=edition.slug))

        return render_template("write_review.html", edition=edition, review=existing)

    @app.route("/review/<int:review_id>/delete", methods=["POST"])
    @login_required
    def delete_review(review_id):
        review = db.session.get(Review, review_id) or abort(404)
        if review.user_id != current_user.id:
            abort(403)
        slug = review.edition.slug
        db.session.delete(review)
        db.session.commit()
        flash("Review deleted.", "info")
        return redirect(url_for("edition_detail", slug=slug))

    # ---------- Profiles ----------

    @app.route("/user/<username>")
    def profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        reviews = user.reviews.order_by(Review.created_at.desc()).all()
        return render_template("profile.html", profile_user=user, reviews=reviews)

    # ---------- Errors ----------

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
