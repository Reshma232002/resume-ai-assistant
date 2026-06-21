 import razorpay
import streamlit as st
import hmac
import hashlib
from backend_db import db


# =========================
# SAFE CLIENT INIT
# =========================
def get_client():
    return razorpay.Client(
        auth=(
            st.secrets["RAZORPAY_KEY_ID"],
            st.secrets["RAZORPAY_KEY_SECRET"]
        )
    )


# =========================
# CREATE ORDER
# =========================
def create_order(amount):
    try:
        order = client.order.create({
            "amount": int(amount * 100),
            "currency": "INR"
        })

        return order

    except Exception as e:
        import streamlit as st

        st.error(f"Razorpay Error: {str(e)}")

        raise


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
