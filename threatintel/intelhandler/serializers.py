from rest_framework import serializers
from .models import Indicator, Feed


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        exclude = []


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        exclude = []
