import json
import random
import scorebot.utils.log as logger

from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden

from sbehost.models import Game, GameTeam, GameHost
from sbegame.models import Team
from scorebot.utils.general import val_auth, get_object_with_id, get_object_by_filter, get_json, save_json_or_error
"""
    Methods supported

    GET - Requesting a object
    PUT - Creating an object (Objects with IDs will be rejected!)
    POST - Updating and object (Objects must have IDs!)
    DELETE - Removes an object.
"""
"""
    SBE Game Views

    API Backend for Game related stuff
"""


class GameViews:
    """
        SBE Game API

        Methods: GET

        GET |   /game/
        GET |   /game/<game_id>/

        Returns game info.  Read-only.
    """
    @staticmethod
    @val_auth
    def game(request, game_id=None):
        if request.method == 'GET':
            return get_object_with_id(request, Game, game_id)
        elif request.method == 'POST':
            # Use the web interface to create games!
            return HttpResponseNotAllowed()
        return HttpResponseBadRequest()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_team(request, game_id=None, team_id=None):
        """
            SBE Game Teams API

            Methods: GET, PUT, POST, DELETE

            GET, PUT          | /game/<game_id>/team/
            GET, POST, DELETE | /game/<game_id>/team/<team_id>/

            Returns game team info.
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')

        if request.method == 'GET':
            r = None
            if not team_id:
                game = get_object_with_id(request, Game, game_id, object_response=False)
                r = HttpResponse(get_json(GameTeam.objects.filter(game=game)))
            else:
                filter_obj = {'team__id': team_id, 'game__id': game_id}
                r = get_object_by_filter(request, GameTeam, filter_obj)
            return r
        elif request.method == 'POST':
            if not team_id:
                return HttpResponseBadRequest('SBE [API]: A team ID must be provided!')

            filter_obj = {'team__id': team_id, 'game__id': game_id}
            r = get_object_by_filter(request, GameTeam, filter_obj, object_response=False)
            return save_json_or_error(request, r[0].id)

        return HttpResponseNotAllowed()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_host(request, game_id=None, host_id=None):
        """
            SBE Game Hosts API

            Methods: GET, PUT, POST, DELETE

            GET, PUT            | /game/<game_id>/host/
            GET, POST, DELETE   | /game/<game_id>/host/<host_id>/
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')

        if request.method == 'GET':
            r = None
            if not host_id:
                game = Game.objects.get(pk=game_id)
                r = HttpResponse(get_json(GameHost.objects.filter(game_team__game=game)))
            else:
                filter_obj = {'host_server__id': host_id, 'game_team__game_id': game_id}
                r = get_object_by_filter(request, GameHost, filter_obj)
            return r
        elif request.method == 'POST':
            if not host_id:
                return HttpResponseBadRequest('SBE [API]: A team ID must be provided!')

            filter_obj = {'host_server__id': host_id, 'game_team__game_id': game_id}
            r = get_object_by_filter(request, GameHost, filter_obj, object_response=False)
            return save_json_or_error(request, r[0].id)

        return HttpResponseNotAllowed()
