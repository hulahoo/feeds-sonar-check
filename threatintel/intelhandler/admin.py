from django.contrib import admin
from .models import (
    Feed,
    Indicator,
    MispEvent,
    MispObject,
    Attribute,
    Tag,
    OrganizationContact,
)

# Register your models here.

admin.site.register(Indicator)
admin.site.register(Feed)
admin.site.register(MispEvent)
admin.site.register(MispObject)
admin.site.register(Attribute)
admin.site.register(Tag)
admin.site.register(OrganizationContact)
