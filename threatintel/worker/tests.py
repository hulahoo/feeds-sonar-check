import os

a=os.path.abspath(os.path.join(__file__, '..','..'))
print(a)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "threatintel.settings")

import django

django.setup()
