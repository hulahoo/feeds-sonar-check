import django_filters
from django.shortcuts import render
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from worker.services import choose_type
from .filters import IndicatorFilter, FeedFilter
from .forms import FeedForm
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

# Create your views here.
from .models import Feed, Indicator, Source
from .serializers import IndicatorSerializer, FeedSerializer, IndicatorWithFeedsSerializer, SourceSerializer


def feed_add(request):
    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed = form.save()
            return HttpResponse("Succesfully added!")
    else:
        form = FeedForm()
    return render(request, "form_add.html", {"form": form})


@api_view(["POST"])
def feed_create(request):
    data = request.data
    feed = Feed(**data["feed"])
    method = choose_type(data['type'])
    config = data.get('config', {})
    results = method(feed, data['raw_indicators'], config)
    return Response({'results': results})


class IndicatorListView(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IndicatorFilter


class FeedListView(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FeedFilter


class Dashboard(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    serializer_class = IndicatorWithFeedsSerializer
    queryset = Indicator.objects.all().prefetch_related('feeds')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IndicatorFilter


class SourceView(viewsets.ModelViewSet):
    serializer_class = SourceSerializer
    queryset = Source.objects.all()
