from django.contrib.auth import get_user_model
from django.test import TestCase

from photomanager.apps.users.models import User


class PhotomanagerTestCase(TestCase):
    def login(self, username: str = "jdoe", is_admin: bool = False) -> User:
        """
        Log the test client in.
        :param username: Username to log in as. If this user doesn't exist, it will be created.
        :param is_admin: Whether this user should be an admin (is_superuser, is_staff).
        :return: The user object.
        """
        user = get_user_model().objects.update_or_create(
            username=username, defaults={"is_superuser": is_admin, "is_staff": is_admin}
        )[0]
        self.client.force_login(user)
        return user
