from django.conf.urls import url
from scorebot_api.views import ScorebotAPI

urlpatterns = [
    url(r'^job$', ScorebotAPI.api_job),
    url(r'^job/$', ScorebotAPI.api_job),
    url(r'^flag$', ScorebotAPI.api_flag),
    url(r'^flag/$', ScorebotAPI.api_flag),
    url(r'^beacon$', ScorebotAPI.api_beacon),
    url(r'^beacon/$', ScorebotAPI.api_beacon),
    url(r'^register$', ScorebotAPI.api_register),
    url(r'^purchase$', ScorebotAPI.api_purchase),
    url(r'^register/$', ScorebotAPI.api_register),
    url(r'^purchase/$', ScorebotAPI.api_purchase),
    url(r'^beacon/port$', ScorebotAPI.api_register_port),
    url(r'^beacon/port/$', ScorebotAPI.api_register_port),
    url(r'^scoreboard/(?P<game_id>[0-9]+)$', ScorebotAPI.api_scoreboard_json),
    url(r'^scoreboard/(?P<game_id>[0-9]+)/$', ScorebotAPI.api_scoreboard_json),
]
