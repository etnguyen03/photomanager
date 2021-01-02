from django.urls import path

from . import views

app_name = "faces"

urlpatterns = [
    path("", views.FacesListView.as_view(), name="list"),
    path("<slug:pk>", views.FaceDetailView.as_view(), name="display"),
]
