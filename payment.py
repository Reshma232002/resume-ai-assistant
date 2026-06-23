import razorpay
import streamlit as st
import hmac
import hashlib
from backend_db import db


# -------------------------
# Razorpay Client
# -------------------------
def get_client():
    return razorpay.Client(
        auth=(
            st.secrets["RAZORPAY_KEY_ID"],
            st.secrets["RAZORPAY_KEY_SECRET"]
        )
    )


# -------------------------
# Create Order
# -------------------------
def create_order(amount):
    client = get_client()

    order = client.order.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "receipt": "receipt_001"
    })

    return order


# -------------------------
# Verify Payment
# -------------------------
def verify_payment(order_id, payment_id, signature):
    secret = st.secrets["RAZORPAY_KEY_SECRET"]

    body = f"{order_id}|{payment_id}"

    generated_signature = hmac.new(
        bytes(secret, "utf-8"),
        bytes(body, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    return generated_signature == signature


# -------------------------
# Update User Plan
# -------------------------
def upgrade_user(user_email, plan):
    user_ref = db.collection("users").document(
        user_email.replace(".", "_")
    )

    user_ref.set({"plan": plan}, merge=True)


# -------------------------
# Get User Plan
# -------------------------
def get_user_plan(user_email):
    user_ref = db.collection("users").document(
        user_email.replace(".", "_")
    )

    doc = user_ref.get()

    if doc.exists:
        return doc.to_dict().get("plan", "free")

    return "free"
