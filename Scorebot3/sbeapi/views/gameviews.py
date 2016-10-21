import json
import random
import scorebot.utils.log as logger

from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from sbehost.models import Game
from sbegame.models import GameTeam
from scorebot.utils.general import val_auth, get_object_with_id, save_json_or_error
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden

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
    @val_auth
    def game_team(request, team_id=None):
        if request.method == 'GET':
            return get_object_with_id(request, GameTeam, team_id)
        elif request.method == 'POST':
            return save_json_or_error(request, team_id)
        return HttpResponseBadRequest()
