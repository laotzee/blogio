from sqlalchemy import create_engine, select, func, update
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

session = SessionLocal()

def initialize_database(eng: Engine | None = None):
    """Initializes the database by creating all tables defined models """
    print("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=eng or engine)
        print("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")


def add_quote(quote: str, post_title: str, language_id: int, 
              session: SessionLocal):
    """Create a new instance of quote"""
    quote = Quote(
            text=quote,
            title=post_title,
            language_id=language_id
        )
    session.add(quote)


def save_quotes(quotes: list, post_title: str, lang: int):
    """
    Saves to the database a list of quotes keeping track of their title and
    language
    """
    session = SessionLocal()
    for quote in quotes:
        add_quote(quote, post_title, lang, session)
    session.commit()


def update_rendered_quote(quote: Quote, img_path: str, session: SessionLocal):
    """Update is_used state and img_name for a quote"""
    session = SessionLocal()
    quote.is_rendered = True
    quote.img_path = img_path
    session.commit()


def unrendered_quotes(lang: int, session: SessionLocal):
    """Returns all unrendered quotes from a given language"""
    stmt = select(Quote).where(Quote.is_rendered == False,
                               Quote.language_id == lang)
    quotes = session.scalars(stmt).all()
    return quotes


def unpublished_quote(lang: int) -> Quote:
    """Returns all an unpublished quote from a given language"""

    session = SessionLocal()
    stmt = (
        select(Quote)
        .where(Quote.language_id==lang, Quote.is_published == False)
        .order_by(func.random())
        .limit(1)
    )
    quote = session.scalar(stmt)
    return quote


def update_published_quote(quote_id: int):
    """Update is_used state and img_name for a quote"""
    session = SessionLocal()
    quote = session.get(Quote, quote_id)
    quote.is_published = True
    session.commit()


def count_unique_titles(lang: int) -> int:
    """Return the number of unique posts from a given language"""
    session = SessionLocal()
    stmt = (select(func.count(Quote.title.distinct()))
            .where(Quote.language_id == lang))

    unique_titles_amount = session.execute(stmt).scalar()
    return unique_titles_amount


if __name__ == '__main__':

    initialize_database()
    session = SessionLocal()
    lang1 = Language(
            name='English',
        )
    lang2 = Language(
            name='Spanish',
        )
    session.add(lang1)
    session.add(lang2)
    try:
        session.commit()
    except IntegrityError:
        pass
