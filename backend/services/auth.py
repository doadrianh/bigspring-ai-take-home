from database.models import SessionLocal, User, PlayAssignment, Rep, Submission, Feedback


def get_user(user_id: str) -> dict | None:
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        return None
    result = {
        "id": user.id, "username": user.username,
        "display_name": user.display_name, "company_id": user.company_id,
        "role": user.role, "segment": user.segment,
    }
    session.close()
    return result


def get_user_accessible_asset_ids(user_id: str) -> set[str]:
    """Get all asset_ids from Watch Reps in the user's assigned plays."""
    session = SessionLocal()
    # Get assigned play_ids
    assignments = session.query(PlayAssignment).filter(PlayAssignment.user_id == user_id).all()
    play_ids = {a.play_id for a in assignments}

    # Get watch rep asset_ids from those plays
    reps = session.query(Rep).filter(
        Rep.play_id.in_(play_ids),
        Rep.prompt_type == "watch",
        Rep.asset_id.isnot(None),
    ).all()
    asset_ids = {r.asset_id for r in reps if r.asset_id}

    session.close()
    return asset_ids


def get_user_submission_asset_ids(user_id: str) -> set[str]:
    """Get asset_ids for the user's own submissions only."""
    session = SessionLocal()
    submissions = session.query(Submission).filter(Submission.user_id == user_id).all()
    asset_ids = {s.asset_id for s in submissions}
    session.close()
    return asset_ids


def get_user_submissions_with_feedback(user_id: str) -> list[dict]:
    """Get the user's submissions with their feedback for history context."""
    session = SessionLocal()
    submissions = session.query(Submission).filter(Submission.user_id == user_id).all()
    results = []
    for sub in submissions:
        fb = session.query(Feedback).filter(Feedback.submission_id == sub.id).first()
        rep = session.query(Rep).filter(Rep.id == sub.rep_id).first()
        results.append({
            "submission_id": sub.id,
            "rep_title": rep.prompt_title if rep else "",
            "rep_prompt": rep.prompt_text if rep else "",
            "submitted_at": sub.submitted_at,
            "submission_type": sub.submission_type,
            "asset_id": sub.asset_id,
            "feedback_score": fb.score if fb else None,
            "feedback_text": fb.text if fb else "",
        })
    session.close()
    return results
