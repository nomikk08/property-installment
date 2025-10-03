from django.contrib.auth import get_user_model as django_get_user_model

from accounts.models import User


def get_user_model() -> type[User]:
    return django_get_user_model()
