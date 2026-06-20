import razorpay
import streamlit as st
import hmac
import hashlib


client = razorpay.Client(
    auth=(
        st.secrets["RAZORPAY_KEY_ID"],
        st.secrets["RAZORPAY_SECRET"]
    )
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
# VERIFY PAYMENT (REAL)
# =========================
def verify_payment(payment_id, order_id, signature):

    generated_signature = hmac.new(
        bytes(st.secrets["RAZORPAY_SECRET"], "utf-8"),
        bytes(f"{order_id}|{payment_id}", "utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(generated_signature, signature)


# =========================
# FETCH PAYMENT FROM RAZORPAY (IMPORTANT REAL CHECK)
# =========================
def fetch_payment(payment_id):
    return client.payment.fetch(payment_id)


# =========================
# FINAL VALIDATION (PRODUCTION SAFE)
# =========================
def validate_payment(payment_id, order_id, signature, expected_amount):

    # 1. Verify signature
    if not verify_payment(payment_id, order_id, signature):
        return False

    # 2. Fetch real payment from Razorpay server
    payment = fetch_payment(payment_id)

    if payment["status"] != "captured":
        return False

    # 3. Amount check (VERY IMPORTANT)
    if payment["amount"] != expected_amount * 100:
        return False

    return True