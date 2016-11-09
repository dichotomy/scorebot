from django.conf.urls import url
from sbeapi.views.gameviews import GameViews
from sbeapi.views.manageviews import ManageViews

urlpatterns = [
    url(r'^job/$', ManageViews.job, name='jobs'),
    url(r'^game/$', GameViews.game, name='games'),
    url(r'^team/$', ManageViews.team, name='teams'),
    url(r'^player/$', ManageViews.player, name='players'),
    url(r'^team/(?P<team_id>[0-9]+)/$', ManageViews.team, name='team'),
    url(r'^player/(?P<player_id>[0-9]+)/$', ManageViews.player, name='player'),
    url(r'^game/(?P<game_id>[0-9]+)/$', GameViews.game, name='game'),
    url(r'^game/(?P<game_id>[0-9]+)/team/$', GameViews.game_team, name='game_team'),
    url(r'^game/(?P<game_id>[0-9]+)/team/(?P<team_id>[0-9]+)/$', GameViews.game_team, name='game_team'),
    url(r'^game/(?P<game_id>[0-9]+)/host/$', GameViews.game_host, name='game_host'),
    url(r'^game/(?P<game_id>[0-9]+)/host/(?P<host_id>[0-9]+)/$', GameViews.game_host, name='game_host'),

#
#    url(r'^job/$', views.SBE_Management.job_request, name='jobs'),
#    url(r'^game/(?P<game_id>[0-9]+)/$', views.SBE_Game.game, name='game'),
#    url(r'^team/(?P<team_id>[0-9]+)/$', views.SBE_Game.team, name='teams'),
#    url(r'^player/(?P<player_id>[0-9]+)/$', views.SBE_Game.player, name='player'),
#    url(r'^team/(?P<team_id>[0-9]+)/player/$', views.SBE_Game.team_players, name='team_players'),
#    url(r'^team/(?P<team_id>[0-9]+)/player/(?P<player_id>[0-9]+)/$', views.SBE_Game.team_players, name='team_players_id'),
]
