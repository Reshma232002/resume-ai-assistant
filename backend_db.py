import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


def get_user_doc(user_email):

    doc_ref = db.collection("users").document(
        user_email.replace(".", "_")
    )

    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()

    return {}


def get_user_usage(user_email):

    user_doc = get_user_doc(user_email)

    return user_doc.get("daily_usage", 0)


def increment_usage(user_email):

    user_ref = db.collection("users").document(
        user_email.replace(".", "_")
    )

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

    doc = user_ref.get()

    if not doc.exists:
        return

    user = doc.to_dict()

    last_reset = user.get("last_reset")

    today = datetime.now().date().isoformat()

    if last_reset != today:

        user_ref.set({
            "daily_usage": 0,
            "last_reset": today
        }, merge=True)


def get_user_plan_from_db(user_email):

    user_ref = db.collection("users").document(
        user_email.replace(".", "_")
    )

    doc = user_ref.get()

    if doc.exists:
        return doc.to_dict().get("plan", "free")

    return "free"
