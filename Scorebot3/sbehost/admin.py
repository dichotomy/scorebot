import sbehost.models

from django.contrib import admin
from scorebot.utils.general import all_models_for_mod


for mod in all_models_for_mod(sbehost.models):
    admin.site.register(mod)
