from django.contrib import admin
from .models import (
    Feed,
    Indicator,
    Tag,
)


class IndicatorInline(admin.TabularInline):
    model = Indicator


class TagInline(admin.TabularInline):
    model = Tag


class FeedAdmin(admin.ModelAdmin):
    inlines = (
        IndicatorInline,
        TagInline,
    )


class IndicatorAdmin(admin.ModelAdmin):
    inlines = (TagInline,)


admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(Tag)
