from django.contrib import admin

import sbegame.models
from scorebot.utils.general import all_models_for_mod
from sbegame.forms.adminforms import AccessKeyAdminPanel


class AccessKeyAdmin(admin.ModelAdmin):
    form = AccessKeyAdminPanel


for mod in all_models_for_mod(sbegame.models):
    if 'AccessKey' in mod.__name__:
        admin.site.register(mod, AccessKeyAdmin)
    else:
        admin.site.register(mod)

