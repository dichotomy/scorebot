import random
import scorebot.utils.log as logger

from ipware.ip import get_real_ip
from scorebot.utils.json2 import translator
from django.views.decorators.csrf import csrf_exempt
from sbehost.models import Game, GameHost, GameTeam, GameMonitor
from sbegame.models import Player, Team, MonitorJob, MonitorServer
from scorebot.utils.general import val_auth, get_object_with_id, save_json_or_error
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

"""
    Methods supported

    GET - Requesting a object
    PUT - Creating an object (Objects with IDs will be rejected!)
    POST - Updating and object (Objects must have IDs!)
    DELETE - Removes an object.
"""
"""
    SBE Manage Views

    API Backend for SBE Management related stuff
"""


class ManageViews:
    @staticmethod
    @csrf_exempt
    @val_auth
    def job(request):
        """
            SBE Job API

            Methods: GET, POST

            GET  | /job/
            POST | /job/

            Requests a Job (GET) and submits a completed Job (POST)

            How it works

            1. Check if AccessKey is tied to MonitorServer
                -> if not return 403
            2. List Games that are Running (Not Done & Paused) and have the requesting Monitor Server assigned
            3. Randomly select a game (if > 1)
            4. Check if Monitor Server is assigned to any specific hosts for that game
                -> if goto 5
                -> if not goto 6
            5. Set list of available hosts to the host list that is set. goto 7
            6. Query the GameTeams through the Game object and enumerate all hosts in the game, store in list
            7. Enumerate each host in the list randomly and check if a running Job is open for that host.
                -> if goto 7, repeat until empty, goto 10
                -> if not goto 8
            8. Create a Job for that host.
            9. Return 201 (Job Created) and Job JSON
            10. Return 204 (No Jobs) and Job wait JSON
        """
        try:
            monitor = MonitorServer.objects.get(monitor_key_id=request.authkey.id)
        except MonitorServer.DoesNotExist:
            logger.warning(__name__, '"%s" attempted to request a job, but is not assigned as a Monitor!' %
                           get_real_ip(request))
            return HttpResponseForbidden('SBE [API]: You do not have permission to request a job!')
        monitor.monitor_address = get_real_ip(request)
        monitor.save()
        if request.method == 'GET':
            logger.info(__name__, 'Job requested by monitor "%s"!' % monitor.monitor_name)
            mon_games = Game.objects.filter(game_paused=False, game_finish__isnull=True, game_monitors__id=monitor.id)
            if len(mon_games) > 0:
                for x in range(0, min(len(mon_games) * 2, 10)):
                    mon_sel = mon_games[random.randint(0, len(mon_games) - 1)]  # random pick a game
                    mon_opt = GameMonitor.objects.get(monitor_game=mon_sel, monitor_inst_id=monitor.id)  # get options
                    logger.debug(__name__, 'Monitor "%s" selected game "%s"!' % (monitor.monitor_name,
                                                                                 mon_sel.game_name))
                    if mon_opt.monitor_hosts.all().count() > 0:  # Do we have assigned hosts?
                        logger.debug(__name__, 'Monitor "%s" has an assigned host list!' % monitor.monitor_name)
                        mon_hosts = mon_opt.monitor_hosts.all()  # Save list of assigned hosts
                    else:
                        mon_hosts = GameHost.objects.filter(gameteam__in=GameTeam.objects.filter(game=mon_sel))
                    logger.debug(__name__, 'Monitor "%s" has "%d" hosts to choose from!' % (monitor.monitor_name,
                                                                                            len(mon_hosts)))
                    mon_count = len(mon_hosts)
                    mon_tries = 0
                    while mon_tries < mon_count:
                        host = mon_hosts[random.randint(0, mon_count - 1)]
                        try:
                            MonitorJob.objects.get(job_finish__isnull=True, job_host=host)
                        except MonitorJob.DoesNotExist:
                            # We got a host!
                            mon_job = MonitorJob()
                            mon_job.job_host = host
                            mon_job.job_monitor = monitor
                            mon_job.save()
                            logger.debug(__name__, 'Job id "%d" given to monitor "%s"!' % (mon_job.id,
                                                                                           monitor.monitor_name))
                            return HttpResponse(content=translator.to_job_json(mon_job), status=201)
                        mon_tries += 1
                logger.debug(__name__, 'Monitor "%s" told to wait due to no available hosts!' % monitor.monitor_name)
                return HttpResponse(content='{ "status": "wait" }', status=204)
            else:
                logger.debug(__name__, 'Monitor "%s" told to wait due to no games!' % monitor.monitor_name)
                return HttpResponse(content='{ "status": "wait" }', status=204)
        elif request.method == 'POST':
            try:
                job_response = translator.from_job_json(monitor, request.body.decode('utf-8'))
                if job_response:
                    logger.info(__name__, 'Successful Job response by Monitor "%s"!' % monitor.monitor_name)
                    return HttpResponse(content='{ "status": "completed" }', status=202)
            except ValueError:
                pass
            except UnicodeDecodeError:
                pass
            logger.error(__name__, 'Invalid Job response by Monitor "%s"!' % monitor.monitor_name)
            return HttpResponseBadRequest('SBE [API]: Invalid POST data!')
        return HttpResponseBadRequest('SBE [API]: Job only supports GET and POST!')

    @staticmethod
    @csrf_exempt
    @val_auth
    def team(request, team_id=None):
        """
            SBE Team API

            Methods: GET, PUT, POST

            GET  |  /team/
            GET  |  /team/<game_id>/
            PUT  |  /team/
            POST |  /team/<player_id>/

            Returns Team info.  Deletes are not allowed

            JSON Example:



            Permissions:
                Team.(READ | UPDATE | CREATE | DELETE)
        """
        if request.method == 'GET':
            return get_object_with_id(request, Team, team_id)
        elif request.method == 'POST' or request.method == 'PUT':
            return save_json_or_error(request, team_id)
        return HttpResponseBadRequest()

    @staticmethod
    @csrf_exempt
    @val_auth
    def player(request, player_id=None):
        """
            SBE Player API

            Methods: GET, PUT, POST

            GET  |  /player/
            GET  |  /player/<game_id>/
            PUT  |  /player/
            POST |  /player/<player_id>/

            Returns Player info.  Deletes are not allowed

            JSON Example:



            Permissions:
                Player.(READ | UPDATE | CREATE | DELETE)
        """
        if request.method == 'GET':
            return get_object_with_id(request, Player, player_id)
        elif request.method == 'POST' or request.method == 'PUT':
            return save_json_or_error(request, player_id)
        return HttpResponseBadRequest()
