from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.feed_add, name="feed_add"),
    # path("add/", views.add_to_query, name="add_to_query"),
    # path("from/", views.read_from_query, name="read_from_query"),
]
