import secrets
import string

from app.models import Link


CHARACTERS = string.ascii_letters + string.digits


def generate_short_code(length=6):
    while True:
        code = "".join(
            secrets.choice(CHARACTERS)
            for _ in range(length)
        )

        existing_link = Link.query.filter_by(
            short_code=code
        ).first()

        if not existing_link:
            return code