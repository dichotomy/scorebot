from django.conf.urls import url
from scorebot_api.views import ScorebotAPI

urlpatterns = [
    url(r'^sb2import$', ScorebotAPI.api_import),
    url(r'^sb2import/$', ScorebotAPI.api_import, name='sb2import'),
    url(r'^scoreboard/(?P<game_id>[0-9]+)$', ScorebotAPI.api_scoreboard),
    url(r'^scoreboard/(?P<game_id>[0-9]+)/$', ScorebotAPI.api_scoreboard, name='scoreboard'),
]
