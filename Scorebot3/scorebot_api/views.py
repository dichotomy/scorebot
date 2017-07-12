import json
import random

from django.utils import timezone
from scorebot.utils import logger
from scorebot_grid.models import Flag, Host
from django.shortcuts import render, reverse
from scorebot_api.forms import Scorebot2ImportForm
from django.views.decorators.csrf import csrf_exempt
from netaddr import IPNetwork, IPAddress, AddrFormatError
from scorebot_core.models import Monitor, token_create_new
from django.contrib.admin.views.decorators import staff_member_required
from scorebot.utils.general import authenticate, get_client_ip, game_team_from_token
from scorebot_game.models import GameMonitor, Job, Game, GamePort, GameTeam, Compromise, Purchase
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse, HttpResponseNotFound,\
    HttpResponseServerError, HttpResponseRedirect


class ScorebotAPI:
    @staticmethod
    @csrf_exempt
    @authenticate()
    def api_job(request):
        client = get_client_ip(request)
        try:
            monitor = Monitor.objects.get(access=request.authentication)
        except Monitor.DoesNotExist:
            logger.warning('SBE-JOB', 'Client "%s" attempted to request a Job but is not a Monitor!' % client)
            return HttpResponseForbidden('{"message": "SBE API: Only registered Monitors may request Jobs!"}')
        try:
            game_monitors = GameMonitor.objects.filter(monitor=monitor, game__status=1)
        except GameMonitor.DoesNotExist:
            logger.warning('SBE-JOB', 'Monitor "%s" attempted to request a Job but is not registered in any Games!'
                           % monitor.name)
            return HttpResponseForbidden('{"message": "SBE API: Not registered with any running Games!"}')
        if len(game_monitors) == 0:
            logger.warning('SBE-JOB', 'Monitor "%s" attempted to request a Job but is not registered in any Games!'
                           % monitor.name)
            return HttpResponseForbidden('{"message": "SBE API: Not registered with any running Games!"}')
        if request.method == 'GET':
            logger.debug('SBE-JOB', 'Monitor "%s" is requesting a Job!' % monitor.name)
            logger.debug('SBE-JOB', 'Monitor "%s" has "%d" Games to choose from.' % (monitor.name, len(game_monitors)))
            game_monitor = random.choice(game_monitors)
            logger.debug('SBE-JOB', 'Monitor "%s" has picked game "%s".' % (monitor.name, game_monitor.game.name))
            job = game_monitor.get_job()
            del client
            del monitor
            del game_monitor
            del game_monitors
            if job:
                return HttpResponse(status=201, content=job)
            return HttpResponse(status=204, content='{"message": "SBE API: No Hosts available! Try later."}')
        elif request.method == 'POST':
            logger.debug('SBE-JOB', 'Monitor "%s" is submitting a Job!' % monitor.name)
            try:
                decoded_data = request.body.decode('UTF-8')
            except UnicodeDecodeError:
                logger.debug('SBE-JOB', 'Job submitted by Monitor "%s" is not encoded properly!' % monitor.name)
                return HttpResponseBadRequest('{"message": "SBE API: Incorrect encoding, please use UTF-8!"}')
            try:
                job_json = json.loads(decoded_data)
                del decoded_data
            except json.decoder.JSONDecodeError:
                logger.debug('SBE-JOB', 'Job submitted by Monitor "%s" is not in correct JSON format!' % monitor.name)
                return HttpResponseBadRequest('{"message": "SBE API: Not in valid JSON format!"}')
            try:
                job = Job.objects.get(id=int(job_json['id']))
                if job.finish is not None:
                    logger.warning('SBE-JOB', 'Monitor "%s" returned a completed Job!' % monitor.name)
                    return HttpResponseBadRequest('{"message": "SBE API: Job already completed!"}')
            except ValueError:
                logger.warning('SBE-JOB', 'Monitor "%s" returned a Job with an invalid ID!' % monitor.name)
                return HttpResponseBadRequest('SBE API: Invalid Job ID!')
            except TypeError:
                logger.debug('SBE-JOB', 'Job submitted by Monitor "%s" is not in correct JSON format!' % monitor.name)
                return HttpResponseBadRequest('{"message": "SBE API: Not in valid JSON format!"}')
            except Job.DoesNotExist:
                logger.warning('SBE-JOB', 'Monitor "%s" returned a Job with an non-existent ID "%d" !' %
                               (monitor.name, job_json['id]']))
                return HttpResponseBadRequest('{"message:", "SBE API: Job with ID \'%d\' does not exist!"}'
                                              % job_json['id'])
            status, message = job.monitor.update_job(monitor, job, job_json)
            del job
            del client
            del monitor
            del game_monitors
            if status:
                return HttpResponse(status=202, content='{"message": "SBE API: Job Accepted"}')
            return HttpResponseBadRequest(content='{"message": "SBE API: %s"}' % message)
        return HttpResponseBadRequest(content='{"message": "SBE API: Not a supported method type!"}')

    @staticmethod
    @csrf_exempt
    @authenticate('__SYS_FLAG')
    def api_flag(request):
        if request.method == 'POST':
            team, token, data, exception = game_team_from_token(request, 'Flag', 'token', fields=['flag'])
            del token
            if exception is not None:
                return exception
            try:
                flag = Flag.objects.exclude(team=team).get(host__team__game=team.game, flag__exact=data['flag'],
                                                           enabled=True)
            except Flag.DoesNotExist:
                logger.warning('SBE-FLAG', 'Flag API: Flag submitted by Team "%s" was not found!'
                               % team.get_canonical_name())
                return HttpResponseNotFound(content='SBE API: Flag not valid!')
            except Flag.MultipleObjectsReturned:
                logger.warning('SBE-FLAG', 'Flag API: Flag submitted by Team "%s" returned multiple flags!'
                               % team.get_canonical_name())
                return HttpResponseNotFound(content='SBE API: Flag not valid!')
            if flag.captured is not None:
                logger.warning('SBE-FLAG', 'Flag API: Flag "%s" submitted by Team "%s" was already captured!'
                               % (flag.get_canonical_name(), team.get_canonical_name()))
                return HttpResponse(status=204)
            flag.capture(team)
            logger.info('SBE-FLAG', 'Flag API: Flag "%s" was captured by team "%s"!' % (flag.get_canonical_name(),
                                                                                        team.get_canonical_name()))
            try:
                flag_next = random.choice(Flag.objects.filter(enabled=True, team=flag.team, captured__isnull=True))
                del flag
                if flag_next is not None:
                    return HttpResponse('{"message": "%s"}' % flag_next.description)
            except IndexError:
                return HttpResponse(status=200)
            except Flag.DoesNotExist:
                return HttpResponse(status=200)
        return HttpResponseBadRequest(content='SBE API: Not a supported method type!')

    @staticmethod
    @csrf_exempt
    @authenticate('__SYS_BEACON')
    def api_beacon(request):
        if request.method == 'POST':
            team, token, data, exception = game_team_from_token(request, 'CLI', 'token', beacon=True,
                                                                fields=['address'])
            if exception is not None:
                return exception
            address_raw = data['address']
            try:
                address = IPAddress(address_raw)
            except AddrFormatError:
                logger.warning('SBE-BEACON',
                               'Beacon API: IP Reported by Team "%s" is invalid!' % team.get_canonical_name())
                return HttpResponseBadRequest(content='{"message": "SBE API: Invalid IP Address!"}')
            victim_team_instance = None
            for victim_team in team.game.teams.all():
                try:
                    victim_subnet = IPNetwork(victim_team.subnet)
                except AddrFormatError:
                    logger.warning('SBE-BEACON',
                               'Beacon API: Team "%s" subnet is invalid! Skipping!' % team.get_canonical_name())
                    continue
                if address in victim_subnet:
                    logger.warning('SBE-BEACON', 'Beacon API: Beacon from Team "%s" to Team "%s"\'s subnet!'
                                   % (team.get_canonical_name(), victim_team.get_canonical_name()))
                    victim_team_instance = victim_team
                    break
            try:
                host = Host.objects.get(ip=address_raw, team__game__status=1)
                if host.team.game.id != team.game.id:
                    logger.warning('SBE-BEACON',
                                   'Beacon API: Host accessed by Team "%s" is not in the same game as "%s"!'
                                   % (team.get_canonical_name(), host.team.get_canonical_name()))
                    return HttpResponseForbidden('SBE API: Host is not in the same Game!')
                try:
                    beacon = host.beacons.all().get(finish__isnull=True, attacker=team, token=token)
                    beacon.checkin = timezone.now()
                    beacon.save()
                    logger.info('SBE-CLI', 'Beacon API: Team "%s" updated a Beacon on Host "%s"!'
                                % (team.get_canonical_name(), host.get_canonical_name()))
                    return HttpResponse()
                except Compromise.DoesNotExist:
                    beacon = Compromise()
                    beacon.host = host
                    beacon.token = token
                    beacon.attacker = team
                    beacon.save()
                    logger.info('SBE-CLI', 'Beacon API: Team "%s" added a Beacon to Host "%s"!'
                                % (team.get_canonical_name(), host.get_canonical_name()))
                    return HttpResponse(status=201)
            except Host.DoesNotExist:
                logger.info('SBE-BEACON', 'Beacon API: Host accessed by Team "%s" does not exist! Creating new one!'
                            % team.get_canonical_name())
                beacon_host = Host()
                beacon_host.ip = address_raw
                beacon_host.fqdn = 'beacon-%d.generated' % random.randint(0, 4096)
                beacon_host.hidden = True
                beacon_host.team = victim_team_instance
                beacon_host.save()
                beacon = Compromise()
                beacon.host = beacon_host
                beacon.token = token
                beacon.attacker = team
                beacon.save()
                logger.info('SBE-CLI', 'Beacon API: Team "%s" added a Beacon to Host "%s"!'
                            % (team.get_canonical_name(), host.get_canonical_name()))
                return HttpResponse(status=201)
            except Host.MultipleObjectsReturned:
                logger.warning('SBE-BEACON',
                               'Beacon API: Host accessed by Team "%s" returned multiple Hosts!'
                               % team.get_canonical_name())
                return HttpResponseNotFound('SBE API: Host does not exist!')
        return HttpResponseBadRequest(content='SBE API: Not a supported method type!')

    @staticmethod
    @staff_member_required
    def api_import(request):
        if request.method == 'GET':
            import_form = Scorebot2ImportForm()
            return render(request, 'scorebot2_import.html', {'import_form': import_form.as_table()})
        elif request.method == 'POST':
            import_form = Scorebot2ImportForm(request.POST)
            if import_form.is_valid():
                if import_form:
                #try:
                    import_game = import_form.save()
                    if import_game is None:
                        return HttpResponseServerError('Error importing Game! Game is None!')
                    return HttpResponseRedirect(reverse('scorebot3:scoreboard', args=(import_game.id,)))
                #except Exception as importError:
                #    return HttpResponseServerError(str(importError))
            return render(request, 'scorebot2_import.html', {'import_form': import_form.as_table()})
        return HttpResponseBadRequest(content='SBE API: Not a supported method type!')

    @staticmethod
    @csrf_exempt
    @authenticate('__SYS_CLI')
    def api_register(request):
        if request.method == 'POST':
            team, token, data, exception = game_team_from_token(request, 'CLI', 'token')
            del token
            if exception is not None:
                return exception
            beacon = token_create_new(30)
            team.beacons.add(beacon)
            team.save()
            logger.info('SBE-CLI', 'CLI API: Team "%s" requested a new Beacon token!' % team.get_canonical_name())
            del team
            return HttpResponse(status=201, content='{"token": "%s"}' % str(beacon.uuid))
        return HttpResponseBadRequest(content='SBE API: Not a supported method type!')

    @staticmethod
    @csrf_exempt
    @authenticate('__SYS_CLI')
    def api_register_port(request):
        if request.method == 'GET':
            port_list = []
            for game in Game.objects.filter(status=1):
                for port in game.ports.all():
                    if port not in port_list:
                        port_list.append(port.port)
            return HttpResponse(content='{"ports":[%s]}' % ','.join([str(i) for i in port_list]))
        if request.method == 'POST':
            team, token, data, exception = game_team_from_token(request, 'CLI', 'token', fields=['port'])
            del token
            if exception is not None:
                return exception
            try:
                port = int(data['port'])
            except ValueError:
                logger.warning('SBE-CLI', 'CLI API: Port submitted by Team "%s" is not an Integer!'
                               % team.get_canonical_name())
                return HttpResponseBadRequest(content='SBE API: Port is not an Integer!')
            del data
            logger.info('SBE-CLI', 'CLI API: Team "%s" requested a new Beacon port "%d/tcp"!'
                        % (team.get_canonical_name(), port))
            try:
                team.game.ports.all().get(port=port)
                logger.debug('SBE-CLI', 'CPI API: Port requested by Team "%s" is already open!'
                             % team.get_canonical_name())
                del team
                return HttpResponse(status=418)
            except GamePort.DoesNotExist:
                game_port = GamePort()
                game_port.port = port
                game_port.save()
                team.game.ports.add(game_port)
                team.game.save()
                logger.debug('SBE-CLI', 'CLI API: Port "%d" requested by Team "%s" was opened!'
                             % (port, team.get_canonical_name()))
                del team
                del game_port
                return HttpResponse(status=201)
        return HttpResponseBadRequest(content='SBE API: Not a supported method type!')

    @staticmethod
    @csrf_exempt
    @authenticate('__SYS_STORE')
    def api_purchase(request, team_id=None):
        client = get_client_ip(request)
        if request.method == 'GET':
            logger.debug('SBE-STORE', 'Store API: Client "%s" is requesting the exchange rate for Team "%d".'
                         % (client, team_id))
            if team_id is None:
                logger.warning('SBE-STORE', 'Store API: Client "%s" attempted to use Null Team ID!' % client)
                return HttpResponseNotFound('{"message": "SBE API: Team could not be found!"}')
            try:
                team = GameTeam.objects.get(store_id=int(team_id), game__status=1)
            except ValueError:
                logger.warning('SBE-STORE', 'Store API: Client "%s" attempted to use an invalid Team ID "%s"!'
                               % (client, str(team_id)))
                return HttpResponseNotFound('{"message": "SBE API: Invalid Team ID!"}')
            except GameTeam.DoesNotExist:
                logger.warning('SBE-STORE', 'Store API: Client "%s" attempted to use an non-existent Team ID!' % client)
                return HttpResponseNotFound('{"message": "SBE API: Team could not be found!"}')
            except GameTeam.MultipleObjectsReturned:
                logger.warning('SBE-STORE',
                               'Store API: Client "%s" attempted to use a Team ID which returned multiple Teams!'
                               % client)
                return HttpResponseNotFound('{"message": "SBE API: Team could not be found!"}')
            rate = float(team.game.get_option('score_exchange_rate'))/100.0
            logger.debug('SBE-STORE', 'Store API: The exchange rate for Team "%s" is "%d"!'
                         % (team.get_canonical_name(), rate))
            return HttpResponse(status=200, content='{"rate": %.2f}' % rate)
        if request.method == 'POST':
            try:
                decoded_data = request.body.decode('UTF-8')
            except UnicodeDecodeError:
                logger.warning('SBE-STORE', 'Store API: Data submitted by Client "%s" is not encoded properly!'
                               % client)
                return HttpResponseBadRequest(content='{"message": "SBE API: Incorrect encoding, please use UTF-8!"}')
            try:
                json_data = json.loads(decoded_data)
            except json.decoder.JSONDecodeError:
                logger.warning('SBE-STORE', 'Store API: Data submitted by Client "%s" is not in correct JSON format!'
                               % client)
                return HttpResponseBadRequest(content='SBE API: Not in valid JSON format!')
            if 'team' not in json_data and 'order' not in json_data:
                logger.warning('SBE-STORE', 'Store API: Data submitted by Client "%s" is not in correct JSON format!'
                              % client)
                return HttpResponseBadRequest(content='{"message": "SBE API: Not in valid JSON format!"}')
            try:
                team = GameTeam.objects.get(store_id=int(json_data['team']), game__status=1)
            except ValueError:
                logger.warning('SBE-STORE', 'Store API: Client "%s" attempted to use an invalid Team ID "%s"!'
                               % (client, str(team_id)))
                return HttpResponseNotFound('{"message": "SBE API: Invalid Team ID!"}')
            except GameTeam.DoesNotExist:
                logger.warning('SBE-STORE', 'Store API: Client "%s" attempted to use an non-existent Team ID!' % client)
                return HttpResponseNotFound('{"message": "SBE API: Team could not be found!"}')
            except GameTeam.MultipleObjectsReturned:
                logger.warning('SBE-STORE',
                               'Store API: Client "%s" attempted to use a Team ID which returned multiple Teams!'
                               % client)
                return HttpResponseNotFound('{"message": "SBE API: Team could not be found!"}')
            logger.debug('SBE-STORE', 'Store API: Client "%s" is attempting to add Purchase records for Team "%s".'
                         % (client, team.get_canonical_name()))
            if not isinstance(json_data['order'], list):
                logger.warning('SBE-STORE', 'Store API: Data submitted by Client "%s" is not in correct JSON format!'
                              % client)
                return HttpResponseBadRequest(content='{"message": "SBE API: Not in valid JSON format!"}')
            for order in json_data['order']:
                if 'item' in order and 'price' in order:
                    try:
                        purchase = Purchase()
                        purchase.team = team
                        purchase.amount = int(order['price'])
                        purchase.item = (order['item'] if len(order['item']) < 150 else order['item'][:150])
                        team.score.set_uptime(-1 * purchase.amount)
                        purchase.save()
                        logger.warning('SBE-STORE', 'Store API: Client "%s" processed order of "%s" "%d" for team "%s"!'
                                       % (client, purchase.item, purchase.amount, team.get_canonical_name()))
                        del purchase
                    except ValueError:
                        logger.warning('SBE-STORE', 'Store API: Order "%s" has invalid integers!' % str(order))
                else:
                    logger.warning('SBE-STORE', 'Store API: Order "%s" does not have the correct items!' % str(order))
            return HttpResponse('{"message": "processed"}')
        return HttpResponseBadRequest(content='{"message": "SBE API: Not a supported method type!"}')

    @staticmethod
    def api_scoreboard(request, game_id):
        return render(request, 'scoreboard.html', {'game_id': game_id})

    @staticmethod
    def api_scoreboard_json(request, game_id):
        if request.method == 'GET':
            try:
                return HttpResponse(content=Game.objects.get(id=int(game_id)).get_json_scoreboard())
            except Game.DoesNotExist:
                return HttpResponseNotFound()
        return HttpResponseBadRequest()
