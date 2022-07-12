def django_init():
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threatintel.settings')
    django.setup()