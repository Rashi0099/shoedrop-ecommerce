from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email instead of username.
    This ensures admin_login (and any view calling authenticate(email=..., password=...))
    works correctly with the custom User model that uses email as USERNAME_FIELD.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Run the default password hasher to mitigate timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
