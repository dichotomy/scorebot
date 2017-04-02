import scorebot.utils.log as logger

from django.views.decorators.csrf import csrf_exempt
from sbegame.models import Player, Team, MonitorJob, MonitorServer
from sbehost.models import GameService
from scorebot.utils.general import val_auth, get_object_with_id, save_json_or_error
from scorebot.utils.json2 import translator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from ipware.ip import get_real_ip


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


def get_job_from_queue(monitor):
    job = None
    try:
        job = MonitorJob.get_job_pending(monitor=monitor)
    except Exception:
        logger.exception(__name__,
                         'Exception while selecting pending jobs')
    if job is None:
        services = GameService.get_current_services()
        MonitorJob.create_new_jobs(services)
        job = MonitorJob.get_job_pending(monitor=monitor)

    return job


class ManageViews:
    """
        SBE Player API

        Methods: GET, PUT, POST

        GET  |  /player/
        GET  |  /player/<game_id>/
        PUT  |  /player/
        POST |  /player/<player_id>/

        Returns player info.  Deletes are not allowed
    """
    @staticmethod
    @csrf_exempt
    @val_auth
    def team(request, team_id=None):
        if request.method == 'GET':
            return get_object_with_id(request, Team, team_id)
        elif request.method == 'POST' or request.method == 'PUT':
            return save_json_or_error(request, team_id)
        return HttpResponseBadRequest()

    @staticmethod
    @csrf_exempt
    @val_auth
    def player(request, player_id=None):
        if request.method == 'GET':
            return get_object_with_id(request, Player, player_id)
        elif request.method == 'POST' or request.method == 'PUT':
            return save_json_or_error(request, player_id)
        return HttpResponseBadRequest()

    @staticmethod
    @csrf_exempt
    @val_auth
    def bakjob(request):
        return HttpResponse(request.authkey.key_uuid)

    @staticmethod
    @csrf_exempt
    @val_auth
    def job(request, job_id=None):
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
            monitor = MonitorServer.objects.get(key__id=request.authkey.id)
        except MonitorServer.DoesNotExist:
            logger.warning(__name__, '"%s" attempted to request a job, but is not assigned as a Monitor!' %
                           get_real_ip(request))
            return HttpResponseForbidden('SBE [API]: You do not have permission to request a job!')

        # TODO: Do we need this every time or at all?
        #
        monitor.monitor_address = get_real_ip(request)
        monitor.save()

        if request.method == 'GET':
            logger.info(__name__,
                        'Job requested by monitor <%d>!' % monitor.id)
            ''' TODO:
                1. Create queue of necessary checks or pull from current queue
                2. For every GET request,
                        pop a job off the queue
            '''
            job = get_job_from_queue(monitor=monitor)

            return HttpResponse(content=translator.to_job_json(job), status=201)

            '''
            monitor_games = Game.objects.filter(paused=False,
                                                finish__isnull=True,
                                                monitors__id=monitor.id)
            if len(monitor_games):
                for x in range(0, min(len(monitor_games) * 2, 10)):
                    mon_sel = monitor_games[random.randint(0, len(monitor_games) - 1)]  # random pick a game
                    mon_opt = GameMonitor.objects.get(monitor_game=mon_sel, monitor_inst_id=monitor.id)   # get options
                    logger.debug(__name__, 'Monitor "%s" selected game "%s"!' % (monitor.monitor_name,
                                                                                 mon_sel.game_name))
                    if mon_opt.monitor_hosts.all().count() > 0:     # Do we have assigned hosts?
                        logger.debug(__name__, 'Monitor "%s" has an assigned host list!' % monitor.monitor_name)
                        mon_hosts = mon_opt.monitor_hosts.all().filter(game=mon_sel)   # Save list of assigned hosts
                    else:
                        mon_hosts = GameHost.objects.filter(game__isnull=False, game=mon_sel)
                    logger.debug(__name__, 'Monitor "%s" has "%d" hosts to choose from!' % (monitor.monitor_name,
                                                                                            len(mon_hosts)))
                    mon_count = len(mon_hosts)
                    mon_tries = 0
                    while mon_tries < mon_count:
                        host = mon_hosts[random.randint(0, mon_count - 1)]
                        try:
                            # If you need to test job functions nuke this try:except, excepts will pass.
                            # Uncommenting the next line will work
                            # MonitorJob.objects.get(job_start__isnull=True)
                            # - idf
                            MonitorJob.objects.get(job_finish__isnull=True, host=host)
                        except MonitorJob.DoesNotExist:
                            # We got a host!
                            job = MonitorJob()
                            job.host = host
                            job.monitor = monitor
                            job.save()
                            logger.debug(__name__, 'Job id "%d" given to monitor "%s"!' % (job.id,
                                                                                           monitor.monitor_name))
                            return HttpResponse(content=translator.to_job_json(job), status=201)
                        mon_tries += 1
                logger.debug(__name__, 'Monitor "%s" told to wait due to no available hosts!' % monitor.monitor_name)
                return HttpResponse(content='{ "status": "wait" }', status=204)
            else:
                logger.debug(__name__, 'Monitor "%s" told to wait due to no games!' % monitor.monitor_name)
                return HttpResponse(content='{ "status": "wait" }', status=204)
            '''
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
            except Exception:
                logger.exception(
                    __name__,
                    'Invalid Job response by Monitor "%s"!' % monitor.monitor_name
                )
                return HttpResponseBadRequest('SBE [API]: Invalid POST data!')
        return HttpResponseBadRequest('SBE [API]: Job only supports GET and POST!')
