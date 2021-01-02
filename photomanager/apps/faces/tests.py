import json
import os
import uuid
from pathlib import PurePosixPath

import numpy as np
from django.urls import reverse_lazy

from photomanager.test.photomanger_test import PhotomanagerTestCase

from ..photos.models import Photo
from .models import Face


class FacesTestCase(PhotomanagerTestCase):
    def test_list_face_view(self):
        """
        Tests the list face view.

        :return: None
        """

        # First, clear out all the faces that already exist
        Face.objects.all().delete()

        # Add some faces
        faces = []
        for i in range(10):
            faces.append(
                Face.objects.create(
                    face_data=json.dumps(np.random.rand(128, 1).tolist()[0])
                )
            )

        # Since we are not logged in, this should be empty
        response = self.client.get(reverse_lazy("faces:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Log us in, the list should be empty because the user
        # doesn't have any photos associated with them yet
        user = self.login()
        response = self.client.get(reverse_lazy("faces:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # While I'm at it, take the first Face in the list and make
        # its user the user that we are logged in as
        faces[0].user = user
        faces[0].save()

        # Also create a second user and set the second in the list to that user
        user2 = self.login("user2")
        user2.first_name = "hello"
        user2.last_name = "there"
        user2.save()
        faces[1].user = user2
        faces[1].save()

        # Add a photo for testing purposes
        path = f"/{uuid.uuid4()}/{uuid.uuid4()}.jpg"
        self.write_photo(PurePosixPath(path), raise_exception=True)

        photo = Photo.objects.create(file=path, user=user, publicly_accessible=False)
        photo.faces.add(faces[0])
        photo.save()

        # Remove the file from disk now, we no longer need it
        os.remove(f"/data/{path.lstrip('/')}")
        os.removedirs(f"/data/{str(PurePosixPath(path).parent).lstrip('/')}")

        # We should now see no faces because the first doesn't belong to user2,
        # which is the currently logged in user
        response = self.client.get(reverse_lazy("faces:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["object_list"]))

        # Log in as user
        self.login()

        # Try again, we should see one now
        response = self.client.get(reverse_lazy("faces:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["object_list"]))

        # Set that photo to publicly visible then logout
        photo.publicly_accessible = True
        photo.save()

        self.client.logout()

        # Try again, we should now see one face
        response = self.client.get(reverse_lazy("faces:list"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["object_list"]))

    def test_face_detail_view(self):
        """
        Test the face detail view (.views.FaceDetailView).

        :return: None
        """
        face = Face.objects.create(
            face_data=json.dumps(np.random.rand(128, 1).tolist()[0])
        )

        # Since we are not logged in, and there are no images
        # associated with this face, a request should 404
        response = self.client.get(
            reverse_lazy("faces:display", kwargs={"pk": face.id})
        )
        self.assertEqual(404, response.status_code)

        # Log in
        user1 = self.login()
        user2 = self.login(username="user2")

        # We are logged in as user2

        # Add a photo for this face
        path = f"/{uuid.uuid4()}/{uuid.uuid4()}.jpg"
        self.write_photo(PurePosixPath(path), raise_exception=True)

        # Add the photo, but belonging to user1
        photo = Photo.objects.create(file=path, user=user1, publicly_accessible=False)
        photo.faces.add(face)
        photo.save()

        # Remove the file from disk now, we no longer need it
        os.remove(f"/data/{path.lstrip('/')}")
        os.removedirs(f"/data/{str(PurePosixPath(path).parent).lstrip('/')}")

        # This request should 404 since user2 doesn't own any photos
        response = self.client.get(
            reverse_lazy("faces:display", kwargs={"pk": face.id})
        )
        self.assertEqual(404, response.status_code)

        # Change this photo to user2
        photo.user = user2
        photo.save()

        # This request should 200 since user2 now owns this photo
        response = self.client.get(
            reverse_lazy("faces:display", kwargs={"pk": face.id})
        )
        self.assertEqual(200, response.status_code)

        # Now, log out and make this photo publicly accessible
        self.client.logout()
        photo.publicly_accessible = True
        photo.save()

        # A request to the face page should 200 because the photo is public
        response = self.client.get(
            reverse_lazy("faces:display", kwargs={"pk": face.id})
        )
        self.assertEqual(200, response.status_code)
