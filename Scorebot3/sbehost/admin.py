import sbehost.models

from django.contrib import admin
from django.db import models
from scorebot.utils.general import all_models_for_mod


for mod in all_models_for_mod(sbehost.models):
    if type(mod) is type:
        continue
    admin.site.register(mod)
