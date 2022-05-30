from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.feed_add, name="feed_add"),
]
