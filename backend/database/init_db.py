import json
import pandas as pd
from pathlib import Path
from config import DATABASE_DIR
from database.models import (
    engine, SessionLocal, Base,
    Company, User, Play, PlayAssignment, Rep, Asset, Submission, Feedback,
)


def load_all():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()

    try:
        # Companies
        with open(DATABASE_DIR / "BigSpring_takehome_data - comapny.json") as f:
            data = json.load(f)
        for c in data["companies"]:
            session.add(Company(id=c["id"], name=c["name"], description=c["description"]))
        session.flush()

        # Assets (load before reps since reps reference assets)
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - asset.csv")
        for _, r in df.iterrows():
            session.add(Asset(
                id=r["id"], type=r["type"], file_name=r["file_name"],
                created_at=r["created_at"], company_id=r["company_id"],
            ))
        session.flush()

        # Users
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - users.csv")
        for _, r in df.iterrows():
            session.add(User(
                id=r["id"], username=r["username"], display_name=r["display_name"],
                role=r["role"], segment=r["segment"], created_at=r["created_at"],
                is_active=str(r["is_active"]).upper() == "TRUE",
                company_id=r["company_id"],
            ))
        session.flush()

        # Plays
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - play.csv")
        for _, r in df.iterrows():
            session.add(Play(
                id=r["id"], company_id=r["company_id"], title=r["title"],
                description=r["description"], created_at=r["created_at"],
                is_active=str(r["is_active"]).upper() == "TRUE",
            ))
        session.flush()

        # Play Assignments
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - play_assignment.csv")
        for _, r in df.iterrows():
            completed = r["completed_at"] if pd.notna(r["completed_at"]) else None
            session.add(PlayAssignment(
                id=r["id"], user_id=r["user_id"], play_id=r["play_id"],
                assigned_date=r["assigned_date"], status=r["status"],
                completed_at=completed,
            ))
        session.flush()

        # Reps
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - rep.csv")
        for _, r in df.iterrows():
            asset_id = r["asset_id"] if pd.notna(r["asset_id"]) else None
            session.add(Rep(
                id=r["id"], prompt_text=r["prompt_text"], prompt_title=r["prompt_title"],
                prompt_type=r["prompt_type"], play_id=r["play_id"],
                company_id=r["company_id"], asset_id=asset_id,
                created_at=r["created_at"],
            ))
        session.flush()

        # Submissions
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - submission.csv")
        for _, r in df.iterrows():
            session.add(Submission(
                id=r["id"], user_id=r["user_id"], rep_id=r["rep_id"],
                submitted_at=r["submitted_at"], submission_type=r["submission_type"],
                asset_id=r["asset_id"], company_id=r["company_id"],
            ))
        session.flush()

        # Feedback
        df = pd.read_csv(DATABASE_DIR / "BigSpring_takehome_data - feedback.csv")
        for _, r in df.iterrows():
            session.add(Feedback(
                id=r["id"], submission_id=r["submission_id"],
                company_id=r["company_id"], score=int(r["score"]),
                text=r["text"], created_at=r["created_at"],
            ))

        session.commit()
        print(f"Loaded all data into SQLite successfully.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    load_all()
