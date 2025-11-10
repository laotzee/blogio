from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from .models import Quote, Language, Base
from sqlalchemy.exc import IntegrityError


DATABASE_URL: str = "sqlite:///./data/app.db"
engine: Engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def initialize_database(eng: Engine | None = None):
    """Initializes the database by creating all tables defined models """
    print("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=eng or engine)
        print("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")


def add_quote(quote: str, post_title: str, language_id: int, db):
    """Create a new instance of quote"""
    quote = Quote(
            text=quote,
            title=post_title,
            language_id=language_id
        )
    db.add(quote)


def save_quotes(quotes: list, post_title: str, lang: int):
    """
    Saves to the database a list of quotes keeping track of their title and
    language
    """
    db = SessionLocal()
    for quote in quotes:
        add_quote(quote, post_title, lang, db)
    db.commit()


def update_rendered_quote(quote: Quote, img_path: str, db):
    """Update is_used state and img_name for a quote"""
    db = SessionLocal()
    quote.is_rendered = True
    quote.img_path = img_path
    db.commit()


def unrendered_quotes(lang, db):
    stmt = select(Quote).where(Quote.is_rendered == False,
                               Quote.language_id == lang)
    quotes = db.scalars(stmt).all()
    return quotes

def unpublished_quote(lang):

    db = SessionLocal()
    stmt = (
        select(Quote)
        .where(Quote.language_id==lang, Quote.is_published == False)
        .order_by(func.random())
        .limit(1)
    )
    quote = db.scalar(stmt)
    return quote


def update_published_quote(quote_id: int):
    """Update is_used state and img_name for a quote"""
    db = SessionLocal()
    quote = db.get(Quote, quote_id)
    quote.is_published = True
    db.commit()


if __name__ == '__main__':

    initialize_database()
    db = SessionLocal()
    lang1 = Language(
            name='English',
        )
    lang2 = Language(
            name='Spanish',
        )
    db.add(lang1)
    db.add(lang2)
    try:
        db.commit()
    except IntegrityError:
        pass






