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


class IndicatorWithFeedsSerializer(serializers.ModelSerializer):
    feeds = FeedSerializer(many=True, read_only=True)

    class Meta:
        model = Indicator
        exclude = []

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('feeds')

        return queryset
