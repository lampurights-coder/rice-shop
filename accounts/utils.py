import re

from accounts.models import Profile


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("98") and len(digits) >= 12:
        digits = "0" + digits[2:]
    if len(digits) == 10 and digits.startswith("9"):
        digits = "0" + digits
    return digits


def valid_phone(raw: str) -> bool:
    phone = normalize_phone(raw)
    return bool(re.fullmatch(r"09\d{9}", phone))


def get_user_profile(user):
    if not user.is_authenticated:
        return None
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None
