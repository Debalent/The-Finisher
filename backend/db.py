from sqlmodel import SQLModel, Field, create_engine, Session, select
import os
from typing import Optional


DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./the_finisher.db')

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {})


class Lyric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    genre: str
    bpm: int
    mood: str
    theme: str
    lyrics: str
    provider: str


def init_db():
    SQLModel.metadata.create_all(engine)


def save_lyric(genre: str, bpm: int, mood: str, theme: str, lyrics: str, provider: str = 'local') -> Lyric:
    with Session(engine) as session:
        record = Lyric(genre=genre, bpm=bpm, mood=mood, theme=theme, lyrics=lyrics, provider=provider)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def get_recent(limit: int = 10):
    with Session(engine) as session:
        stmt = select(Lyric).order_by(Lyric.id.desc()).limit(limit)
        return session.exec(stmt).all()
