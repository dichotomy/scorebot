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
            2. Get a pending MonitorJob or create a queue of jobs then pick one
            3. If no hosts are available
                Return 204 (No Jobs) and Job wait JSON
            4. Return 201 (Job Provided) and Job JSON
        """
        try:
            monitor = MonitorServer.objects.get(key__id=request.authkey.id)
        except MonitorServer.DoesNotExist:
            logger.warning(
                __name__,
                '"%s" attempted to request a job, but is not a Monitor!' %
                get_real_ip(request)
            )
            return HttpResponseForbidden(
                'SBE [API]: You do not have permission to request a job!'
            )

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

            if job:
                return HttpResponse(content=translator.to_job_json(job), status=201)
            else:
                logger.debug(__name__, 'Monitor "%s" told to wait due to no games!' % monitor.name)
                logger.debug(__name__, 'Monitor "%s" told to wait due to no available hosts!' % monitor.name)
                return HttpResponse(content='{ "status": "wait" }', status=204)
        elif request.method == 'POST':
            try:
                job_response = translator.from_job_json(monitor, request.body.decode('utf-8'))
                if job_response:
                    logger.info(__name__, 'Successful Job response by Monitor "%s"!' % monitor.name)
                    return HttpResponse(content='{ "status": "completed" }', status=202)
            except ValueError:
                pass
            except UnicodeDecodeError:
                pass
            except Exception:
                logger.exception(
                    __name__,
                    'Invalid Job response by Monitor "%s"!' % monitor.name
                )
                return HttpResponseBadRequest('SBE [API]: Invalid POST data!')
        return HttpResponseBadRequest('SBE [API]: Job only supports GET and POST!')
