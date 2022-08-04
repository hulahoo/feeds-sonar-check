from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'indicators', views.IndicatorListView)
router.register(r'feeds', views.FeedListView)
router.register(r'dashboard', views.Dashboard)
router.register(r'source', views.SourceView)
urlpatterns = router.urls
urlpatterns += [
    path("new/", views.feed_add, name="feed_add"),
    path('feed_create/', views.feed_create, name="feed_create"),
]
