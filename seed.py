"""Populate the database with real eFootball / PES season entries.

Run once after the tables exist:
    python seed.py
"""
from datetime import date
from app import create_app
from extensions import db
from models import Edition

EDITIONS = [
    dict(
        slug="pes-2021",
        title="eFootball PES 2021 Season Update",
        season_year=2021,
        release_date=date(2020, 9, 15),
        developer="Konami",
        platforms="PS4, Xbox One, PC",
        engine="Fox Engine",
        accent="#1F7A4D",
        synopsis=(
            "The final entry under the Pro Evolution Soccer name before the "
            "rebrand — a squad-and-kit update on the PES 2020 engine, released "
            "alongside a handful of paid Club Editions for Barcelona, Juventus, "
            "Man United, Bayern and Arsenal."
        ),
    ),
    dict(
        slug="efootball-2022",
        title="eFootball 2022",
        season_year=2022,
        release_date=date(2021, 9, 30),
        developer="Konami",
        platforms="PS4, PS5, Xbox One, Xbox Series X/S, PC, Android, iOS",
        engine="Unreal Engine 4",
        accent="#1D5C9E",
        synopsis=(
            "The rebrand of PES into a free-to-play platform, rebuilt on Unreal "
            "Engine 4. Launched as a bare-bones preview missing Master League "
            "and most modes, and widely remembered as one of the roughest "
            "AAA-adjacent launches in recent sports-game history."
        ),
    ),
    dict(
        slug="efootball-2023",
        title="eFootball 2023",
        season_year=2023,
        release_date=date(2022, 8, 25),
        developer="Konami",
        platforms="PS4, PS5, Xbox One, Xbox Series X/S, PC, Android, iOS",
        engine="Unreal Engine 4",
        accent="#8A2BE2",
        synopsis=(
            "The recovery season: Master League returned, dribbling and defending "
            "were reworked, and myClub carried over progress. Still free-to-play, "
            "with the game's tone shifting from apology tour to actual content."
        ),
    ),
    dict(
        slug="efootball-2024",
        title="eFootball 2024",
        season_year=2024,
        release_date=date(2023, 9, 7),
        developer="Konami",
        platforms="PS4, PS5, Xbox One, Xbox Series X/S, PC, Android, iOS",
        engine="Unreal Engine 4",
        accent="#C9A227",
        synopsis=(
            "A stability-focused season with refined player ID and animation "
            "work, expanded licensed clubs and stadiums, and cross-platform "
            "myClub events becoming the game's main live-service hook."
        ),
    ),
    dict(
        slug="efootball-2025",
        title="eFootball 2025",
        season_year=2025,
        release_date=date(2024, 9, 12),
        developer="Konami",
        platforms="PS4, PS5, Xbox One, Xbox Series X/S, PC, Android, iOS",
        engine="Unreal Engine 4",
        accent="#D64545",
        synopsis=(
            "Added the Camp Nou, Allianz Arena and San Siro among newly scanned "
            "stadiums, plus deeper player likeness updates and limited-time "
            "online events layered on top of the now-mature myClub loop."
        ),
    ),
    dict(
        slug="efootball-2026",
        title="eFootball 2026",
        season_year=2026,
        release_date=date(2025, 8, 14),
        developer="Konami",
        platforms="PS4, PS5, Xbox One, Xbox Series X/S, PC, Android, iOS, Switch 2",
        engine="Unreal Engine 4",
        accent="#2E8B57",
        synopsis=(
            "The current season, bringing the platform to Nintendo Switch 2 via "
            "eFootball Kick Off!, with continued squad, stadium and myClub "
            "content rolling out through the year."
        ),
    ),
]


def run():
    app = create_app()
    with app.app_context():
        db.create_all()
        created = 0
        for data in EDITIONS:
            if not Edition.query.filter_by(slug=data["slug"]).first():
                db.session.add(Edition(**data))
                created += 1
        db.session.commit()
        print(f"Seeded {created} new edition(s). Total: {Edition.query.count()}")


if __name__ == "__main__":
    run()
