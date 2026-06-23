import razorpay
import streamlit as st
import hmac
import hashlib
from backend_db import db


# ==============================
# RAZORPAY CLIENT
# ==============================
def get_client():
    return razorpay.Client(
        auth=(
            st.secrets["RAZORPAY_KEY_ID"],
            st.secrets["RAZORPAY_KEY_SECRET"]
        )
    )


# ==============================
# CREATE ORDER
# ==============================
def create_order(amount):
    client = get_client()

    order = client.order.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "receipt": f"receipt_{amount}"
    })

    return order


# ==============================
# VERIFY PAYMENT
# ==============================
def verify_payment(order_id, payment_id, signature):
    secret = st.secrets["RAZORPAY_KEY_SECRET"]

    body = f"{order_id}|{payment_id}"

    generated_signature = hmac.new(
        bytes(secret, "utf-8"),
        bytes(body, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    return generated_signature == signature


# ==============================
# STANDARDIZE EMAIL KEY (IMPORTANT FIX)
# ==============================
def get_user_doc_ref(user_email):
    clean_email = user_email.strip().replace(".", "_")
    return db.collection("users").document(clean_email)


# ==============================
# SAVE / UPGRADE USER PLAN
# ==============================
def upgrade_user(user_email, plan):
    user_ref = get_user_doc_ref(user_email)

    user_ref.set(
        {
            "plan": plan
        },
        merge=True
    )

    return True


# ==============================
# GET USER PLAN
# ==============================
def get_user_plan(user_email):
    user_ref = get_user_doc_ref(user_email)

    doc = user_ref.get()

    if doc.exists:
        return doc.to_dict().get("plan", "free")

    return "free"
