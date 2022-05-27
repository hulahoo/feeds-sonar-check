from django.contrib import admin
from .models import Email, IPAddress, Domains, FullURL, FileHash

# Register your models here.

admin.site.register(Email)
admin.site.register(IPAddress)
admin.site.register(Domains)
admin.site.register(FullURL)
admin.site.register(FileHash)
