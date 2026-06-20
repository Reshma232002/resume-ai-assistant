import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


def save_analysis(
    user_email,
    resume_text,
    job_description,
    ats_score,
    matched_skills,
    missing_skills,
    cover_letter,
    linkedin_summary,
    ai_insights,
):
    db.collection("resume_analyses").add(
        {
            "user_email": user_email,
            "resume_text": resume_text,
            "job_description": job_description,
            "ats_score": ats_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "cover_letter": cover_letter,
            "linkedin_summary": linkedin_summary,
            "ai_insights": ai_insights,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )
    

def get_user_history(user_email):
    docs = (
        db.collection("resume_analyses")
        .where("user_email", "==", user_email)
        .stream()
    )

    return [doc.to_dict() for doc in docs]
def get_dashboard_stats(user_email):

    docs = (
        db.collection("resume_analyses")
        .where("user_email", "==", user_email)
        .stream()
    )

    analyses = [doc.to_dict() for doc in docs]

    if not analyses:
        return {
            "total": 0,
            "avg_score": 0,
            "max_score": 0
        }

    scores = [
        item.get("ats_score", 0)
        for item in analyses
    ]

    return {
        "total": len(scores),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores)
    }