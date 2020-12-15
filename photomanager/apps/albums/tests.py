import uuid

from django.conf import settings
from django.urls import reverse_lazy

from photomanager.apps.albums.models import Album, AlbumShareLink
from photomanager.test.photomanger_test import PhotomanagerTestCase


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

    def test_albumdeleteview(self):
        user = self.login()
        album = Album.objects.create(
            name=uuid.uuid4(), description=uuid.uuid4(), owner=user
        )

        album_id = album.id

        # Attempt to delete this album
        response = self.client.post(
            reverse_lazy("albums:delete", kwargs={"pk": album_id})
        )
        self.assertEqual(302, response.status_code)  # Redirect to list page on success
        self.assertEqual(0, Album.objects.filter(id=album_id).count())

        # Create an album, and try to delete it after you log out
        self.client.logout()
        album2 = Album.objects.create(
            name=uuid.uuid4(), description=uuid.uuid4(), owner=user
        )
        album2_id = album2.id

        response = self.client.post(
            reverse_lazy("albums:delete", kwargs={"pk": album2_id})
        )
        self.assertEqual(302, response.status_code)  # Redirects to auth page
        self.assertEqual(1, Album.objects.filter(id=album2_id).count())

    def test_album_share_link_create(self):
        user = self.login()
        album = Album.objects.create(
            name=uuid.uuid4(), description=uuid.uuid4(), owner=user
        )

        # Create a share link
        response = self.client.post(
            reverse_lazy("albums:share_links_create", kwargs={"album_id": album.id})
        )
        self.assertEqual(302, response.status_code)  # Redirects to list share link page
        self.assertEqual(1, AlbumShareLink.objects.filter(album=album).count())

        # Create another one
        response = self.client.post(
            reverse_lazy("albums:share_links_create", kwargs={"album_id": album.id})
        )
        self.assertEqual(302, response.status_code)  # Redirects to list share link page
        self.assertEqual(2, AlbumShareLink.objects.filter(album=album).count())

        # Now, logout and try again
        self.client.logout()
        response = self.client.post(
            reverse_lazy("albums:share_links_create", kwargs={"album_id": album.id})
        )
        self.assertEqual(302, response.status_code)  # Redirects to login page
        self.assertEqual(2, AlbumShareLink.objects.filter(album=album).count())

        # Log in as someone else
        self.login("hello")
        response = self.client.post(
            reverse_lazy("albums:share_links_create", kwargs={"album_id": album.id})
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(2, AlbumShareLink.objects.filter(album=album).count())

    def test_album_share_link_list(self):
        user = self.login()
        album = Album.objects.create(
            name=uuid.uuid4(), description=uuid.uuid4(), owner=user
        )

        response = self.client.get(
            reverse_lazy("albums:share_links", kwargs={"album_id": album.id})
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        sharelink = AlbumShareLink.objects.create(album=album, creator=user)

        response = self.client.get(
            reverse_lazy("albums:share_links", kwargs={"album_id": album.id})
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["object_list"]))
        self.assertIn(sharelink, response.context["object_list"])

    def test_album_share_link_delete(self):
        user = self.login()
        album = Album.objects.create(
            name=uuid.uuid4(), description=uuid.uuid4(), owner=user
        )
        sharelink = AlbumShareLink.objects.create(album=album, creator=user)

        # A GET should not delete the link.
        response = self.client.get(
            reverse_lazy(
                "albums:share_links_delete",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            )
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, AlbumShareLink.objects.filter(id=sharelink.id).count())

        # But a POST should.
        response = self.client.post(
            reverse_lazy(
                "albums:share_links_delete",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            )
        )
        self.assertEqual(302, response.status_code)  # Redirect to list page
        self.assertEqual(0, AlbumShareLink.objects.filter(id=sharelink.id).count())

        # Try again with an unauthorized user.
        sharelink = AlbumShareLink.objects.create(album=album, creator=user)
        self.client.logout()

        response = self.client.post(
            reverse_lazy(
                "albums:share_links_delete",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            )
        )
        self.assertEqual(302, response.status_code)  # Redirect to login page
        self.assertEqual(1, AlbumShareLink.objects.filter(id=sharelink.id).count())

        self.login("helo")
        response = self.client.post(
            reverse_lazy(
                "albums:share_links_delete",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            )
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(1, AlbumShareLink.objects.filter(id=sharelink.id).count())

    def test_album_share_link_edit(self):
        user = self.login()
        album = Album.objects.create(
            name=uuid.uuid4(), description=uuid.uuid4(), owner=user
        )
        old_description = uuid.uuid4()
        sharelink = AlbumShareLink.objects.create(
            album=album, creator=user, description=old_description
        )

        response = self.client.get(
            reverse_lazy(
                "albums:share_links_edit",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            )
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1,
            AlbumShareLink.objects.filter(
                description=old_description, id=sharelink.id
            ).count(),
        )

        new_description = uuid.uuid4()

        response = self.client.post(
            reverse_lazy(
                "albums:share_links_edit",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            ),
            data={"description": new_description},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            0,
            AlbumShareLink.objects.filter(
                description=old_description, id=sharelink.id
            ).count(),
        )
        self.assertEqual(
            1,
            AlbumShareLink.objects.filter(
                description=new_description, id=sharelink.id
            ).count(),
        )

        # Now, try with a logged out user
        self.client.logout()
        response = self.client.post(
            reverse_lazy(
                "albums:share_links_edit",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            ),
            data={"description": old_description},
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            0,
            AlbumShareLink.objects.filter(
                description=old_description, id=sharelink.id
            ).count(),
        )
        self.assertEqual(
            1,
            AlbumShareLink.objects.filter(
                description=new_description, id=sharelink.id
            ).count(),
        )

        # Try with an unauthorized user
        self.login("helo")
        response = self.client.post(
            reverse_lazy(
                "albums:share_links_edit",
                kwargs={"album_id": album.id, "pk": sharelink.id},
            ),
            data={"description": new_description},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            0,
            AlbumShareLink.objects.filter(
                description=old_description, id=sharelink.id
            ).count(),
        )
        self.assertEqual(
            1,
            AlbumShareLink.objects.filter(
                description=new_description, id=sharelink.id
            ).count(),
        )
