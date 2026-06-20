from payment import validate_payment
from backend_db import db


def upgrade_user(user_email, plan):

    db.collection("users").document(
        user_email.replace(".", "_")
    ).set({
        "plan": plan
    }, merge=True)


def process_payment(user_email, payment_id, order_id, signature, plan, amount):

    is_valid = validate_payment(
        payment_id,
        order_id,
        signature,
        amount
    )

    if is_valid:
        upgrade_user(user_email, plan)
        return True

    return False