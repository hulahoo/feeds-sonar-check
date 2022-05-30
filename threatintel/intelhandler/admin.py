from django.contrib import admin
from .models import Email, IPAddress, Domain, FullURL, FileHash, Feed

# Register your models here.

admin.site.register(Email)
admin.site.register(IPAddress)
admin.site.register(Domain)
admin.site.register(FullURL)
admin.site.register(FileHash)
admin.site.register(Feed)
