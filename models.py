from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.String(280), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship(
        "Review", backref="author", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def average_rating_given(self):
        ratings = [r.rating for r in self.reviews]
        return round(sum(ratings) / len(ratings), 1) if ratings else None


class Edition(db.Model):
    """One reviewable eFootball release/season (e.g. eFootball 2024)."""

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    season_year = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date, nullable=True)
    developer = db.Column(db.String(80), default="Konami")
    platforms = db.Column(db.String(200), default="")
    engine = db.Column(db.String(80), default="")
    synopsis = db.Column(db.Text, default="")
    accent = db.Column(db.String(20), default="#1F7A4D")

    reviews = db.relationship(
        "Review", backref="edition", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def average_rating(self):
        ratings = [r.rating for r in self.reviews]
        return round(sum(ratings) / len(ratings), 1) if ratings else None

    @property
    def rating_distribution(self):
        """Counts bucketed into 1-10 whole-number bins for the bar chart."""
        buckets = {i: 0 for i in range(1, 11)}
        for r in self.reviews:
            buckets[max(1, min(10, round(r.rating)))] += 1
        return buckets


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    edition_id = db.Column(db.Integer, db.ForeignKey("edition.id"), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    body = db.Column(db.Text, default="")
    played_on = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "edition_id", name="one_review_per_edition"),
    )

    @property
    def rating_tier(self):
        if self.rating >= 7:
            return "good"
        if self.rating >= 5:
            return "mid"
        return "poor"
