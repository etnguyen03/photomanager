from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Lower
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import PhotoTag


class CreateTagView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View to create a tag."""

    model = PhotoTag

    # TODO: accept human readable name and convert to tag
    fields = ["tag"]

    success_message = "Tag created successfully."

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.is_auto_generated = False
        return super(CreateTagView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tags:display", kwargs={"pk": self.object.tag})


class ListTagView(ListView):
    """View to list existing tags."""

    model = PhotoTag
    paginate_by = 25

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # If the user is not authenticated, they can only see publicly accessible images
            return PhotoTag.objects.filter(photo__publicly_accessible=True).order_by(
                Lower("tag")
            )
        else:
            # If the user is authenticated, they can see all the tags
            return PhotoTag.objects.all().order_by(Lower("tag"))


class DetailTagView(DetailView):
    model = PhotoTag

    def get_context_data(self, **kwargs):
        context = super(DetailTagView, self).get_context_data(**kwargs)

        # If the user is authenticated, they can see their photos that are tagged with this tag
        if self.request.user.is_authenticated:
            context["photos"] = self.object.photo_set.filter(user=self.request.user)
        else:
            # If there are no publicly accessible images for this tag, we 404
            if self.object.photo_set.filter(publicly_accessible=True).count() == 0:
                raise Http404(
                    "No publicly accessible images exist for this tag. Are you logged in?"
                )

            # Otherwise, we show the publicly accessible images
            context["photos"] = self.object.photo_set.filter(publicly_accessible=True)

        return context
