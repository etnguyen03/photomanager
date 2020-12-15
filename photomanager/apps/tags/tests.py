import os
import uuid
from pathlib import PurePosixPath

from django.urls import reverse_lazy

from photomanager.apps.photos.models import Photo
from photomanager.apps.tags.models import PhotoTag
from photomanager.test.photomanger_test import PhotomanagerTestCase


class TagsTestCase(PhotomanagerTestCase):
    """Tests the tags app."""

    def test_create_tag_view(self):
        """
        Tests CreateTagView.

        :return: None
        """
        response = self.client.get(reverse_lazy("tags:create"))
        self.assertEqual(302, response.status_code)  # to login page

        user = self.login()

        response = self.client.get(reverse_lazy("tags:create"))
        self.assertEqual(200, response.status_code)

        name_of_tag = uuid.uuid4()
        response = self.client.post(
            reverse_lazy("tags:create"),
            data={"tag": name_of_tag},  # UUID as an arbitrary name
            follow=True,
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, PhotoTag.objects.filter(tag=name_of_tag).count())

    def test_list_tag_view(self):
        """
        Tests the list tag view.

        :return: None
        """

        # First, we need to clear out all PhotoTag objects that already exist.
        PhotoTag.objects.all().delete()

        # Now, we can add PhotoTag objects
        names = []
        for i in range(10):
            name = uuid.uuid4()
            PhotoTag.objects.create(tag=name, creator=None, is_auto_generated=True)
            names.append(name)

        # Since we are not logged in, this list should be empty
        response = self.client.get(reverse_lazy("tags:list"), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Add a publicly accessible photo
        path = f"/{uuid.uuid4()}/{uuid.uuid4()}.jpg"
        self.write_photo(PurePosixPath(path), raise_exception=True)

        # Login to get the user, then logout
        user = self.login()
        self.client.logout()

        photo = Photo.objects.create(file=path, user=user, publicly_accessible=True)

        # Remove the file from disk now, we no longer need it
        os.remove(f"/data/{path.lstrip('/')}")
        os.removedirs(f"/data/{str(PurePosixPath(path).parent).lstrip('/')}")

        # This list should still be empty
        response = self.client.get(reverse_lazy("tags:list"), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Add a tag to that image
        photo.tags.add(PhotoTag.objects.get(tag=names[0]))
        photo.save()

        # The list should now have one tag
        response = self.client.get(reverse_lazy("tags:list"), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["object_list"]))
        self.assertIn(
            PhotoTag.objects.get(tag=names[0]), response.context["object_list"]
        )

        # Make the photo not publicly visible, and this list should be zero
        photo.publicly_accessible = False
        photo.save()

        response = self.client.get(reverse_lazy("tags:list"), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Log in, and the list should now have ten tags
        self.login()

        response = self.client.get(reverse_lazy("tags:list"), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, len(response.context["object_list"]))
        self.assertSetEqual(
            set([PhotoTag.objects.get(tag=n) for n in names]),
            set(response.context["object_list"]),
        )

        # Clean up
        for tag in names:
            PhotoTag.objects.get(tag=tag).delete()

    def test_detail_tag_view(self):
        # First, we need to clear out all PhotoTag objects that already exist.
        PhotoTag.objects.all().delete()

        # Now, create a tag
        name = uuid.uuid4()

        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(404, response.status_code)

        tag = PhotoTag.objects.create(tag=name)

        # There are no publicly accessible photos so this should 404
        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(404, response.status_code)

        user = self.login()

        # Now, try again, and this should 200
        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["photos"]))

        # Add a photo so we can test tags
        path = f"/{uuid.uuid4()}/{uuid.uuid4()}.jpg"
        self.write_photo(PurePosixPath(path), raise_exception=True)

        photo = Photo.objects.create(file=path, user=user, publicly_accessible=False)
        photo.tags.add(tag)
        photo.save()

        # Remove the file from disk now, we no longer need it
        os.remove(f"/data/{path.lstrip('/')}")
        os.removedirs(f"/data/{str(PurePosixPath(path).parent).lstrip('/')}")

        # Log us out, and since the photo is not publicly accessible, this should 404
        self.client.logout()
        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(404, response.status_code)

        # Now, change the photo to publicly accessible and try again
        photo.publicly_accessible = True
        photo.save()

        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["photos"]))
        self.assertIn(photo, response.context["photos"])

        # Log myself in
        self.login()

        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["photos"]))
        self.assertIn(photo, response.context["photos"])

        # Set the photo to not publicly accessible and try again
        photo.publicly_accessible = False
        photo.save()
        response = self.client.get(
            reverse_lazy("tags:display", kwargs={"pk": name}), follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["photos"]))
        self.assertIn(photo, response.context["photos"])
