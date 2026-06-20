from backend_db import get_user_usage

FREE_LIMIT = 3


def can_use_service(user_email):

    usage = get_user_usage(user_email)

    remaining = FREE_LIMIT - usage

    if usage >= FREE_LIMIT:

        return (
            False,
            f"Daily limit reached ({FREE_LIMIT}/{FREE_LIMIT}). Upgrade to Premium."
        )

    return (
        True,
        f"Free Plan • {remaining} analyses remaining today"
    )