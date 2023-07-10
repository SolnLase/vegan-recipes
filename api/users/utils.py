import re


def check_password_strength(password):
    # Criteria
    length = len(password) >= 8
    contains_uppercase = re.search(r"[A-Z]", password) is not None
    contains_lowercase = re.search(r"[a-z]", password) is not None
    contains_digit = re.search(r"\d", password) is not None
    contains_special_char = (
        re.search(r"[!@#$%^&*()_+\-=[\]{};':\"\\|,.<>/?]", password) is not None
    )

    # Evaluate password strength
    if all(
        (
            length,
            contains_uppercase,
            contains_lowercase,
            contains_digit,
            contains_special_char,
        )
    ):
        return "Strong"
    elif any((length, (contains_uppercase and contains_lowercase), contains_digit)):
        return "Moderate"
    else:
        return "Weak"
