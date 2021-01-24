from django.urls import path

from . import views

app_name = "faces"

urlpatterns = [
    path("", views.FacesListView.as_view(), name="list"),
    path("<slug:pk>", views.FaceDetailView.as_view(), name="display"),
    path("<slug:pk>/edit", views.FaceUpdateView.as_view(), name="edit"),
]
