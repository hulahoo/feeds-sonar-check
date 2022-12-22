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


def feed_add(request):
    if request.method == "POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            feed = form.save()
            return HttpResponse("Succesfully added!")
    else:
        form = FeedForm()
    return render(request, "form_add.html", {"form": form})


def feed_create(request):
    """
    Парсит и создает фиды
    """
    data = request.data
    feed = Feed(**data["feed"])
    method = choose_type(data['type'])
    config = data.get('config', {})
    results = method(feed, data['raw_indicators'], config)
    return Response({'results': results})
