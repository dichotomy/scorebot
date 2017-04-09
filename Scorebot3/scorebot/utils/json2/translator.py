import json

from sbegame.models import MonitorJob
from sbehost.models import GameTeam, GameService
from scorebot.utils import log as logger


def to_job_json(job):
    job_header = {
        'status': 'job',
        'model': 'scorebot.job',
        'pk': job.id,
        'game_id': job.service.game_host.game_team.game.id,
        'fields': {}
    }

    game_host = job.service.game_host
    try:
        job_team = GameTeam.objects.get(
            gamehost__id=game_host.id
        )
    except GameTeam.DoesNotExist:
        return None

    job_header['fields']['job_duration'] = 60
    job_header['fields']['job_dns'] = []
    job_dns = job_team.dns.all()
    for dns_server in job_dns:
        job_header['fields']['job_dns'].append(dns_server.address)

    job_header['fields']['job_host'] = {
        'fqdn': game_host.fqdn,
        'ip_address': game_host.server.address,
        'services': [],
        'ping_received': 0,
        'ping_lost': 0
    }

    for service in game_host.gameservice_set.all():
        service_d = {
            'id': service.id,
            'port': service.application.port,
            'application': service.application.application_protocol,
            'protocol': service.application.layer4_protocol,
            'connect': service.status,
            'auth': [],
            'content': []
        }

        for content in service.gamecontent_set.all():
            c = {
                'url': content.url,
                'type': content.content_type,
                'data': content.data
            }

            if content.http_verb:
                c['verb'] = content.http_verb

            service_d['content'].append(c)

        job_header['fields']['job_host']['services'].append(service_d)

    return json.dumps(job_header)


def from_job_json(monitor, jsond):
    try:
        data = json.loads(jsond)
    except ValueError:
        return None

    if 'wait' in MonitorJob.json_get_job_status(data):
        return None

    try:
        job = MonitorJob.objects.get(pk=int(data['pk']))
    except ValueError:
        logger.exception(__name__, 'Primary key is invalid')
        return None
    except MonitorJob.DoesNotExist:
        logger.exception(__name__, 'Primary key is invalid')
        return None

    host = job.service.game_host
    if MonitorJob.json_get_host_status(data):
        logger.debug(__name__, 'Host "%s" was reported as IP %s' % (
            host.fqdn,
            MonitorJob.json_get_host_ip_address(data)
        ))

    if MonitorJob.json_get_ping_ratio(data) == 0:
        logger.info(__name__, 'Host "%s" was reported as down!' % host)

        host.status = False
        host.save()

    for json_service in MonitorJob.json_get_host_services(data):
        '''
        Gotta find out how this translates to the new JSON structure
        '''
        try:
            service = GameService.objects.get(pk=json_service['id'])
            connect_status = MonitorJob.json_has_connect_status(json_service)

            if connect_status:
                service.status = connect_status

            if json_service['content'] and json_service['content']['connect']:
                service.status = json_service['content']['connect']

            service.save()
        except Exception:
            logger.exception(__name__, 'Job JSON failed')

    return job





