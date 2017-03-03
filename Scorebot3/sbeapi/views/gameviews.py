from sbehost.models import GameFlag, GameTicket
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest, HttpResponseNotAllowed
from sbehost.models import Game, GameTeam, GameHost, GameService, \
    GameCompromise, GameContent
from scorebot.utils.general import val_auth, get_object_with_id, \
    get_object_by_filter, get_json, save_json_or_error, get_object_by_query


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

            Methods: GET, POST

            GET         | /game/<game_id>/team/
            GET, POST   | /game/<game_id>/team/<team_id>/

            Returns game team info.
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')

        if request.method == 'GET':
            if not team_id:
                game_teams = Game.objects.get(game_id=game_id).game_teams.all()
                return get_object_by_query(request, game_teams)
            else:
                game_team = Game.objects.get(game_id=game_id).game_teams.get(team_id=team_id)
                return get_object_by_query(request, game_team)
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

            Methods: GET, POST

            GET          | /game/<game_id>/host/
            GET, POST    | /game/<game_id>/host/<host_id>/
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')

        if request.method == 'GET':
            r = None
            if not host_id:
                game = Game.objects.filter(pk=game_id)
                r = HttpResponse(get_json(GameHost.objects.filter(game_team__game=game)))
            else:
                filter_obj = {'host_server_id': host_id, 'game_team__game_id': game_id}
                r = get_object_by_filter(request, GameHost, filter_obj)
            return r
        elif request.method == 'POST':
            if not host_id:
                return HttpResponseBadRequest('SBE [API]: A team ID must be provided!')

            filter_obj = {'host_server_id': host_id, 'game_team__game_id': game_id}
            r = get_object_by_filter(request, GameHost, filter_obj, object_response=False)
            r = r[0].id if r and len(r) > 0 else r
            return save_json_or_error(request, r)

        return HttpResponseNotAllowed()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_service(request, game_id=None, host_id=None, service_id=None):
        """
            SBE Game Services

            Methods: GET, POST

            GET         | /game/<game_id>/host/<host_id>/service/
            GET, POST   | /game/<game_id>/host/<host_id>/service/<service_id>/
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')
        if not host_id:
            return HttpResponseBadRequest('SBE [API]: A host ID must be provided!')

        if request.method == 'GET':
            r = None
            if not service_id:
                game_host = GameHost.objects.filter(host_server_id=host_id)
                r = HttpResponse(get_json(GameService.objects.filter(game_host=game_host)))
            else:
                filter_obj = {'pk': service_id, 'game_host__game_team__game_id': game_id, 'game_host__host_server_id': host_id}
                r = get_object_by_filter(request, GameService, filter_obj)
            return r
        elif request.method == 'POST':
            if not service_id:
                return HttpResponseBadRequest('SBE [API]: A service ID must be provided!')

            filter_obj = {'pk': service_id, 'game_host__game_team__game_id': game_id, 'game_host__host_server_id': host_id}
            r = get_object_by_filter(request, GameService, filter_obj, object_response=False)
            r = r[0].id if r and len(r) > 0 else r
            return save_json_or_error(request, r)

        return HttpResponseNotAllowed()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_content(request, game_id=None, host_id=None, service_id=None, content_id=None):
        """
            SBE Game Content

            Methods: GET, POST, PUT, DELETE

            GET             | /game/<game_id>/host/<host_id>/service/<service_id>/content/
            POST, DELETE    | /game/<game_id>/host/<host_id>/service/<service_id>/content/<content_id>
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')
        if not host_id:
            return HttpResponseBadRequest('SBE [API]: A host ID must be provided!')
        if not service_id:
            return HttpResponseBadRequest('SBE [API]: A service ID must be provided!')

        if request.method == 'GET':
            r = None
            if not content_id:
                game_host = GameHost.objects.filter(pk=host_id)
                r = HttpResponse(get_json(GameContent.objects.filter(
                    game_service_id=service_id,
                    game_service__game_host=game_host,
                    game_service__game_host__game_team__game_id=game_id)))
            else:
                filter_obj = {
                        'pk': content_id,
                        'game_service__game_host__game_team__game__id': game_id,
                        'game_service__game_host_id': host_id,
                        'game_service_id': service_id
                }
                r = get_object_by_filter(request, GameContent, filter_obj)
            return r
        if request.method == 'POST':
            filter_obj = {
                    'pk': content_id,
                    'game_service__game_host__game_team__game__id': game_id,
                    'game_service__game_host_id': host_id,
                    'game_service_id': service_id
            }
            game_content = get_object_by_filter(request, GameContent, filter_obj, object_response=False)
            if not game_content or not len(game_content):
                return HttpResponseNotFound()

            return save_json_or_error(request, content_id)

        return HttpResponseNotAllowed()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_compromise(request, game_id=None, host_id=None, compromise_id=None):
        """
            SBE Game Compromise

            Methods: GET, POST, PUT

            GET, PUT            | /game/<game_id>/host/<host_id>/compromise/
            GET, POST, DELETE   | /game/<game_id>/host/<host_id>/compromise/<compromise_id>/
        """

        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')
        if not host_id:
            return HttpResponseBadRequest('SBE [API]: A host ID must be provided!')

        if request.method == 'GET':
            r = None
            if not compromise_id:
                game_host = GameHost.objects.filter(pk=host_id)
                r = HttpResponse(get_json(GameCompromise.objects.filter(game_host=game_host, game_host__game_team__game__id=game_id)))
            else:
                filter_obj = {'pk': compromise_id, 'game_host__game_team__game_id': game_id, 'game_host__host_server_id': host_id}
                r = get_object_by_filter(request, GameCompromise, filter_obj)
            return r
        elif request.method == 'PUT':
            filter_obj = {'game_team__game_id': game_id, 'host_server_id': host_id}
            game_host = get_object_by_filter(request, GameHost, filter_obj, object_response=False)
            if not game_host or not len(game_host):
                return HttpResponseNotFound()

            return save_json_or_error(request)
        elif request.method == 'POST':
            if not compromise_id:
                return HttpResponseBadRequest('SBE [API]: A compromise ID must be provided!')

            filter_obj = {'pk': compromise_id, 'game_host__game_team__game_id': game_id, 'game_host__host_server_id': host_id}
            r = get_object_by_filter(request, GameCompromise, filter_obj, object_response=False)
            r = r[0].id if r and len(r) > 0 else r
            return save_json_or_error(request, r)
        elif request.method == 'DELETE':
            if not compromise_id:
                return HttpResponseBadRequest('SBE [API]: A compromise ID must be provided!')

            filter_obj = {'pk': compromise_id, 'game_host__game_team__game_id': game_id, 'game_host__host_server_id': host_id}
            r = get_object_by_filter(request, GameCompromise, filter_obj, object_response=False)
            if r and len(r) == 1:
                r.delete()

            return HttpResponse()

        return HttpResponseNotAllowed()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_flag(request, game_id=None, flag_id=None):
        """
            SBE Game Flag

            Methods: GET, POST

            GET         | /game/<game_id>/flag/
            GET, POST   | /game/<game_id>/flag/<flag_id>/
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')

        if request.method == 'GET':
            r = None
            if not flag_id:
                flags = GameFlag.objects.filter(game_id=game_id)
                r = HttpResponse(get_json(flags))
            else:
                filter_obj = {'pk': flag_id, 'game_id': game_id}
                r = get_object_by_filter(request, GameFlag, filter_obj)
            return r
        elif request.method == 'POST':
            if not flag_id:
                return HttpResponseBadRequest('SBE [API]: A flag ID must be provided!')

            filter_obj = {'pk': flag_id, 'game_id': game_id}
            r = get_object_by_filter(request, GameFlag, filter_obj, object_response=False)
            r = r[0].id if r and len(r) > 0 else r
            return save_json_or_error(request, r)

        return HttpResponseNotAllowed()

    @staticmethod
    @csrf_exempt
    @val_auth
    def game_ticket(request, game_id=None, ticket_id=None):
        """
            SBE Game Ticket

            Methods: GET, POST, PUT, DELETE
            GET, PUT            | /game/<game_id>/ticket/
            GET, POST, DELETE   | /game/<game_id>/ticket/<ticket_id>/
        """
        if not game_id:
            return HttpResponseBadRequest('SBE [API]: A game ID must be provided!')

        if request.method == 'GET':
            r = None
            if not ticket_id:
                filter_obj = {'game_team__game_id': game_id}
                r = get_object_by_filter(request, GameTicket, filter_obj)
            else:
                filter_obj = {'pk': ticket_id, 'game_team__game_id': game_id}
                r = get_object_by_filter(request, GameTicket, filter_obj)
            return r
        elif request.method == 'POST':
            if not ticket_id:
                return HttpResponseBadRequest('SBE [API]: A ticket ID must be provided!')

            filter_obj = {'pk': ticket_id, 'game_team__game_id': game_id}
            r = get_object_by_filter(request, GameTicket, filter_obj, object_response=False)
            r = r[0].id if r and len(r) > 0 else r
            return save_json_or_error(request, r)
        elif request.method == 'PUT':
            return save_json_or_error(request)
        elif request.method == 'DELETE':
            if not ticket_id:
                return HttpResponseBadRequest('SBE [API]: A ticket ID must be provided!')

            filter_obj = {'pk': ticket_id, 'game_team__game_id': game_id}
            ticket = get_object_by_filter(request, GameTicket, filter_obj, object_response=False)
            if not ticket:
                return HttpResponseNotFound()

            ticket = GameTicket.objects.get(pk=ticket_id)
            ticket.delete()

            return HttpResponse()

        return HttpResponseNotAllowed()
