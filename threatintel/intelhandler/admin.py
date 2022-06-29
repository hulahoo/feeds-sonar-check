from django.contrib import admin
from .models import (
    Feed,
    Indicator,
    Tag,
)

admin.site.register(Indicator)
admin.site.register(Feed)
admin.site.register(Tag)
