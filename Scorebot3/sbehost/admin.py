import sbehost.models

from django.contrib import admin
from scorebot.utils.general import all_models_for_mod
from sbegame.forms.adminforms import GameContentAdminPanel


class GameContentAdmin(admin.ModelAdmin):
    form = GameContentAdminPanel


for mod in all_models_for_mod(sbehost.models):
    if 'GameContent' in mod.__name__:
        admin.site.register(mod, GameContentAdmin)
    else:
        admin.site.register(mod)
