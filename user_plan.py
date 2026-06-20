# user_plan.py

from backend_db import get_user_usage, get_user_plan_from_db

FREE_LIMIT = 1  # as you requested

def can_use_service(user_email):

    plan = get_user_plan_from_db(user_email)

    if plan == "premium":
        return True, "Premium user - unlimited access"

    usage = get_user_usage(user_email)

    if usage >= FREE_LIMIT:
        return False, "Daily limit reached (1 analysis/day for free users)"

    return True, f"{FREE_LIMIT - usage} free analyses left today"
