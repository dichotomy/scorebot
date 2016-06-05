import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scorebot.settings")

application = get_wsgi_application()

from scorebot.utils.initloader import load_init

load_init()
