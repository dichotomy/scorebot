import json
import random
import scorebot.utils.log as logger

from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden

from sbehost.models import Game, GameTeam
from sbegame.models import Team
from scorebot.utils.general import val_auth, get_object_with_id, get_object_by_filter, get_json
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
    @staticmethod
    @val_auth
    def game(request, game_id=None):
        """
            SBE Game API

            Methods: GET

            GET |   /game/
            GET |   /game/<game_id>/

            Returns game info.  Read-only.
        """
        if request.method == 'GET':
            return get_object_with_id(request, Game, game_id)
        elif request.method == 'POST':
            # Use the web interface to create games!
            return HttpResponseNotAllowed()
        return HttpResponseBadRequest()

    @staticmethod
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
        elif request.method == 'PUT':
            data = json.loads(request.body)
        elif request.method == 'POST':
            pass
        elif request.method == 'DELETE':
            pass

        return HttpResponseBadRequest()

