from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

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
        context["photos"] = self.object.photo_set.all()
        return context
