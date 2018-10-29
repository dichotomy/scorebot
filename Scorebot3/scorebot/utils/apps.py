from django.apps import AppConfig


class ScorebotAPI(AppConfig):
    name = 'scorebot_api'
    verbose_name = 'Scorebot API'


class ScorebotCore(AppConfig):
    name = 'scorebot_core'
    verbose_name = 'Scorebot Core Models'


class ScorebotGrid(AppConfig):
    name = 'scorebot_grid'
    verbose_name = 'Scorebot Grid Models'


class ScorebotGame(AppConfig):
    name = 'scorebot_game'
    verbose_name = 'Scorebot Game Models'
