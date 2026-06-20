import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ===============================
# Firebase Initialization
# ===============================
if not firebase_admin._apps:

    firebase_config = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    }

    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ===============================
# FUNCTIONS
# ===============================

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

    db.collection("resume_analyses").add({
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
    })


def get_user_history(user_email):

    docs = db.collection("resume_analyses") \
             .where("user_email", "==", user_email) \
             .stream()

    return [doc.to_dict() for doc in docs]


def get_dashboard_stats(user_email):

    docs = db.collection("resume_analyses") \
             .where("user_email", "==", user_email) \
             .stream()

    analyses = [doc.to_dict() for doc in docs]

    if not analyses:
        return {"total": 0, "avg_score": 0, "max_score": 0}

    scores = [item.get("ats_score", 0) for item in analyses]

    return {
        "total": len(scores),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores)
    }
def get_user_doc(user_email):
    doc_ref = db.collection("users").document(user_email.replace(".", "_"))
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}


def get_user_usage(user_email):
    user_doc = get_user_doc(user_email)
    return user_doc.get("daily_usage", 0)


def increment_usage(user_email):
    user_ref = db.collection("users").document(user_email.replace(".", "_"))

    user_doc = user_ref.get()

    if user_doc.exists:
        current = user_doc.to_dict().get("daily_usage", 0)
    else:
        current = 0

    user_ref.set({
        "daily_usage": current + 1
    }, merge=True)

def reset_daily_usage_if_needed(user_email):

    user_ref = db.collection("users").document(
        user_email.replace(".", "_")
    )

    user = user_ref.get().to_dict()

    if not user:
        return

    last_reset = user.get("last_reset")

    today = datetime.now().date().isoformat()

    # If never reset or new day → reset usage
    if last_reset != today:
        user_ref.set({
            "daily_usage": 0,
            "last_reset": today
        }, merge=True)    
def get_user_plan_from_db(user_email):
    data = db.collection("users").document(user_email).get().to_dict()
    if data:
        return data.get("plan", "free")
    return "free"        
