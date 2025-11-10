from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Language(Base):
    """
    A reference table for languages.
    """
    __tablename__ = "languages"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    quotes: Mapped[list["Quote"]] = relationship(back_populates="language")

    def __repr__(self) -> str:
        return f"Language(id={self.id!r}, name={self.name!r})"


class Quote(Base):
    """
    A table to store memorable quotes, linked to a specific language.
    """
    __tablename__ = "quotes"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(100), default="Unknown")
    img_path: Mapped[str | None] = mapped_column(String(100))
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"))
    language: Mapped["Language"] = relationship(back_populates="quotes")
    is_rendered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )

    def __repr__(self) -> str:
        return f"Quote(id={self.id!r}, title={self.title!r}, lang_id={self.language_id!r})"
