from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


def build_user_data(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "birth_date": user.birth_date,
        "school_grade": user.school_grade,
        "competition_grade_group": user.competition_grade_group,
        "region": user.region_id,
        "identity_type": user.identity_type,
        "identity_number": user.identity_number,
    }


def build_token_response(user: User, status: int | None = None) -> dict:
    token = RefreshToken.for_user(user)
    return {
        "refresh": str(token),
        "access": str(token.access_token),
        "user": build_user_data(user),
    }


__all__ = ["build_user_data", "build_token_response"]
