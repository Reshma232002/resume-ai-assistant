# user_plan.py

FREE_LIMIT = 1  # ✅ 1 analysis per day for free users


def get_user_plan(user_doc):
    return user_doc.get("plan", "free")


def can_use_service(user_doc):
    """
    Returns:
    - True if user can use service
    - False if limit exceeded
    """

    plan = get_user_plan(user_doc)

    # Premium users → unlimited
    if plan == "premium":
        return True, "Premium user: Unlimited access"

    usage = user_doc.get("daily_usage", 0)

    if usage >= FREE_LIMIT:
        return False, "Free limit reached (1 analysis/day). Upgrade to continue."

    return True, f"Free plan: {usage}/{FREE_LIMIT} used today"
