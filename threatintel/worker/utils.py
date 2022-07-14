def django_init():
    import os
    import django

    import django

    ph = os.path.abspath(os.path.join(__file__, '..', '..'))
    os.chdir(ph)


    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threatintel.settings')
    django.setup()

if __name__ == '__main__':
    django_init()
