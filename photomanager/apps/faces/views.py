from django.db.models.functions import Lower
from django.http import Http404
from django.views.generic import DetailView, ListView

from photomanager.apps.faces.models import Face


class FacesListView(ListView):
    """View for listing all the faces."""

    model = Face
    paginate_by = 100

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # If the user is not authenticated, they can only see publicly accessible images
            return (
                Face.objects.filter(photo__publicly_accessible=True)
                .distinct()
                .order_by(Lower("user"), Lower("defined_name"), "id")
            )
        else:
            # If the user is authenticated, they can see faces for which they have
            # at least one image
            return (
                Face.objects.filter(photo__user=self.request.user)
                .distinct()
                .order_by(Lower("user"), Lower("defined_name"), "id")
            )


class FaceDetailView(DetailView):
    """View for listing all the photos that contain the given face."""

    model = Face

    def get_context_data(self, **kwargs):
        context = super(FaceDetailView, self).get_context_data(**kwargs)

        # If the user is authenticated, they can see their photos that are tagged with this face
        if self.request.user.is_authenticated:
            # However, if there are no such photos, we need to 404.
            if self.object.photo_set.filter(user=self.request.user).count() == 0:
                raise Http404(
                    "You cannot access this face because you have no photos with this face."
                )

            context["photos"] = self.object.photo_set.filter(user=self.request.user)
        else:
            # If there are no publicly accessible images for this tag, we 404
            if self.object.photo_set.filter(publicly_accessible=True).count() == 0:
                raise Http404(
                    "No publicly accessible images exist for this face. Are you logged in?"
                )

            # Otherwise, we show the publicly accessible images
            context["photos"] = self.object.photo_set.filter(publicly_accessible=True)

        return context
