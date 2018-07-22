from django.conf.urls import url
from scorebot_api.views import ScorebotAPI

urlpatterns = [
    url(r'^job$', ScorebotAPI.api_job),
    url(r'^job/$', ScorebotAPI.api_job),
    url(r'^flag$', ScorebotAPI.api_flag),
    url(r'^flag/$', ScorebotAPI.api_flag),
    url(r'^beacon$', ScorebotAPI.api_beacon),
    url(r'^ticket$', ScorebotAPI.api_ticket),
    url(r'^beacon/$', ScorebotAPI.api_beacon),
    url(r'^ticket/$', ScorebotAPI.api_ticket),
    url(r'^register$', ScorebotAPI.api_register),
    url(r'^purchase$', ScorebotAPI.api_purchase),
    url(r'^transfer$', ScorebotAPI.api_transfer),
    url(r'^register/$', ScorebotAPI.api_register),
    url(r'^purchase/$', ScorebotAPI.api_purchase),
    url(r'^transfer/$', ScorebotAPI.api_transfer),
    url(r'^new_resource$', ScorebotAPI.api_new_resource),
    url(r'^beacon/port$', ScorebotAPI.api_register_port),
    url(r'^beacon/port/$', ScorebotAPI.api_register_port),
    url(r'^mapper/(?P<game_id>[0-9]+)$', ScorebotAPI.api_uuid),
    url(r'^mapper/(?P<game_id>[0-9]+)/$', ScorebotAPI.api_uuid),
    url(r'^purchase/(?P<team_id>[0-9]+)$', ScorebotAPI.api_purchase),
    url(r'^purchase/(?P<team_id>[0-9]+)/$', ScorebotAPI.api_purchase),
    url(r'^scoreboard/(?P<game_id>[0-9]+)$', ScorebotAPI.api_scoreboard_json),
    url(r'^scoreboard/(?P<game_id>[0-9]+)/$', ScorebotAPI.api_scoreboard_json),
]
