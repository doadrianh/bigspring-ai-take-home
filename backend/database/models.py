from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import SQLITE_DB_PATH

Base = declarative_base()
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    display_name = Column(String)
    role = Column(String)
    segment = Column(String)
    created_at = Column(String)
    is_active = Column(Boolean, default=True)
    company_id = Column(String, ForeignKey("companies.id"))


class Play(Base):
    __tablename__ = "plays"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    title = Column(String)
    description = Column(Text)
    created_at = Column(String)
    is_active = Column(Boolean, default=True)


class PlayAssignment(Base):
    __tablename__ = "play_assignments"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    play_id = Column(String, ForeignKey("plays.id"))
    assigned_date = Column(String)
    status = Column(String)
    completed_at = Column(String, nullable=True)


class Rep(Base):
    __tablename__ = "reps"
    id = Column(String, primary_key=True)
    prompt_text = Column(Text)
    prompt_title = Column(String)
    prompt_type = Column(String)  # "watch" or "practice"
    play_id = Column(String, ForeignKey("plays.id"))
    company_id = Column(String, ForeignKey("companies.id"))
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)
    created_at = Column(String)


class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    type = Column(String)  # pdf, video, image, text, audio
    file_name = Column(String)
    created_at = Column(String)
    company_id = Column(String, ForeignKey("companies.id"))


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    rep_id = Column(String, ForeignKey("reps.id"))
    submitted_at = Column(String)
    submission_type = Column(String)
    asset_id = Column(String, ForeignKey("assets.id"))
    company_id = Column(String, ForeignKey("companies.id"))


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id"))
    company_id = Column(String, ForeignKey("companies.id"))
    score = Column(Integer)
    text = Column(Text)
    created_at = Column(String)


def init_tables():
    Base.metadata.create_all(engine)
