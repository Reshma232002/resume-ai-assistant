import razorpay
import streamlit as st
import hmac
import hashlib
from backend_db import db


# Razorpay client
client = razorpay.Client(
    auth=(st.secrets["RAZORPAY_KEY_ID"], st.secrets["RAZORPAY_KEY_SECRET"])
)


# =========================
# CREATE ORDER
# =========================
def create_order(amount):
    return client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })


# =========================
# VERIFY PAYMENT
# =========================
def verify_payment(order_id, payment_id, signature):

    secret = st.secrets["RAZORPAY_KEY_SECRET"]

    msg = f"{order_id}|{payment_id}"

    generated_signature = hmac.new(
        secret.encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()

    return generated_signature == signature


# =========================
# UPGRADE USER
# =========================
def upgrade_user(user_email, plan="premium"):

    user_ref = db.collection("users").document(user_email.replace(".", "_"))

    user_ref.set({
        "plan": plan
    }, merge=True)
