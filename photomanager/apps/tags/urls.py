from django.urls import path

from . import views

app_name = "tags"

urlpatterns = [
    path("", views.ListTagView.as_view(), name="list"),
    path("create", views.CreateTagView.as_view(), name="create"),
    path("<slug:pk>", views.DetailTagView.as_view(), name="display"),
    path("<slug:pk>/delete", views.DeleteTagView.as_view(), name="delete"),
]
