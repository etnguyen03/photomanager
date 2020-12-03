import uuid

from django.conf import settings
from django.urls import reverse_lazy

from ...test.photomanger_test import PhotomanagerTestCase
from .models import Album, AlbumShareLink


class AlbumsTestCase(PhotomanagerTestCase):
    """Tests the Album app"""

    def test_view_album(self):
        """Test cases for the view_album view"""
        user = self.login()
        album = Album.objects.create(name=uuid.uuid4(), owner=user)

        response = self.client.get(
            reverse_lazy("albums:display", kwargs={"album_id": album.id})
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(album, response.context["album"])

        self.client.logout()

        # Since the album is not publicly visible, this should redirect to the login page
        response = self.client.get(
            reverse_lazy("albums:display", kwargs={"album_id": album.id})
        )
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response, settings.LOGIN_URL, status_code=302, target_status_code=302
        )

        # Now, make the album publicly visible
        album.publicly_accessible = True
        album.save()

        response = self.client.get(
            reverse_lazy("albums:display", kwargs={"album_id": album.id})
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(album, response.context["album"])

        # Log in as someone else
        self.login("jdoe2")

        response = self.client.get(
            reverse_lazy("albums:display", kwargs={"album_id": album.id})
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(album, response.context["album"])

        # Make the album not publicly visible
        album.publicly_accessible = False
        album.save()

        response = self.client.get(
            reverse_lazy("albums:display", kwargs={"album_id": album.id})
        )
        self.assertEqual(403, response.status_code)

    def test_view_album_share(self):
        user = self.login()
        album = Album.objects.create(name=uuid.uuid4(), owner=user)
        albumsharelink = AlbumShareLink.objects.create(
            album=album, description="", creator=user
        )

        response = self.client.get(
            reverse_lazy(
                "albums:share_display",
                kwargs={"album_id": album.id, "share_album_id": albumsharelink.id},
            )
        )
        self.assertEqual(200, response.status_code)

        # Now, delete the share link; that should now 404
        old_id = albumsharelink.id
        albumsharelink.delete()

        response = self.client.get(
            reverse_lazy(
                "albums:share_display",
                kwargs={"album_id": album.id, "share_album_id": old_id},
            )
        )
        self.assertEqual(404, response.status_code)

    def test_albumeditview(self):
        user = self.login()
        album = Album.objects.create(name=uuid.uuid4(), owner=user)

        response = self.client.get(reverse_lazy("albums:edit", kwargs={"pk": album.id}))
        self.assertEqual(200, response.status_code)

        # Test editing
        new_name = str(uuid.uuid4())
        new_description = str(uuid.uuid4())
        response = self.client.post(
            reverse_lazy("albums:edit", kwargs={"pk": album.id}),
            data={"name": new_name, "description": new_description},
        )

        self.assertEqual(
            302, response.status_code
        )  # Redirect to different page on success
        album_updated = Album.objects.get(id=album.id)
        self.assertEqual(new_name, album_updated.name)
        self.assertEqual(new_description, album_updated.description)

    def test_albumcreateview(self):
        self.login()

        response = self.client.get(reverse_lazy("albums:create"))
        self.assertEqual(200, response.status_code)

        new_name = str(uuid.uuid4())
        new_description = str(uuid.uuid4())
        response = self.client.post(
            reverse_lazy("albums:create"),
            data={"name": new_name, "description": new_description},
        )

        self.assertEqual(
            302, response.status_code
        )  # Redirect to different page on success
        self.assertEqual(
            1, Album.objects.filter(name=new_name, description=new_description).count()
        )

    def test_albumlistview(self):
        # We are not logged in
        response = self.client.get(reverse_lazy("albums:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Authenticate and try again
        user = self.login()

        response = self.client.get(reverse_lazy("albums:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Now add an album
        album = Album.objects.create(
            owner=user, name=uuid.uuid4(), description=uuid.uuid4()
        )

        response = self.client.get(reverse_lazy("albums:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["object_list"]))
        self.assertIn(album, response.context["object_list"])

        # Log out and try again
        self.client.logout()

        response = self.client.get(reverse_lazy("albums:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        album.publicly_accessible = True
        album.save()

        response = self.client.get(reverse_lazy("albums:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["object_list"]))
        self.assertIn(album, response.context["object_list"])
