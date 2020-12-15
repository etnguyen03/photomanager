import io
from pathlib import Path, PurePosixPath

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from PIL import Image

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

    def write_photo(self, path: PurePosixPath, raise_exception: bool = False) -> None:
        """
        Write a photo to use for testing purposes to /data.

        :param path: Path under `/data` to write the photo to. For instance, `/ethan/image.jpg`.
                     Subdirectories are created automatically if they do not exist.
                     Must end in ".jpg".
        :param raise_exception: Network access is required to download a photo. If the photo is not downloadable, then
                                if raise_exception is True, a ConnectionError is raised. If raise_exception is False, then
                                a blank file is created.
        :raises ConnectionError if raise_exception is True and no image could be downloaded.
        :return: None
        """
        assert path.suffix == ".jpg", "Path must have a .jpg file extension"
        path = PurePosixPath(f"/data/{str(path).lstrip('/')}")

        # Make directories if they don't exist
        Path(path.parent).mkdir(parents=True, exist_ok=True)

        # A list of image URLs that can be downloaded from.
        # URLs are tried in succession until the first
        # one succeeds, and is written to the path given.
        IMAGE_URLS = [
            # Puppy by Lisa L Wiedmeier, CC-BY-SA 2.0
            "https://live.staticflickr.com/8068/8165497065_f4ae999991_o_d.jpg",
            # Puppy by David J, CC-BY 2.0
            "https://live.staticflickr.com/7217/7335671690_48d31181bc_o_d.jpg",
            # Chesapeake Bay Retriever puppy (6weeks old) by Benbas
            # CC-BY-SA 3.0 or GFDL-1.2-no-invariants-or-later
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Bas_20060903_021.JPG/800px-Bas_20060903_021.JPG",
            # Chiemsee2016 (Pixabay)
            # Pixabay License
            "https://cdn.pixabay.com/photo/2016/02/18/18/37/puppy-1207816_960_720.jpg",
        ]
        downloaded_image = False
        for url in IMAGE_URLS:
            try:
                response = requests.get(url, timeout=1)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                image.verify()
                with Path(path).open(mode="wb") as file:
                    file.write(response.content)
                downloaded_image = True
            except Exception:
                pass

        if not downloaded_image:
            if raise_exception:
                raise ConnectionError()
            else:
                # Write an empty file
                with Path(path).open(mode="wb") as file:
                    pass
