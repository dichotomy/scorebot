import json

from sbegame.models import MonitorJob
from sbehost.models import GameTeam, GameService
from scorebot.utils import log as logger


def to_job_json(job):
    job_header = {'status': 'job', 'model': 'scorebot.job', 'pk': job.id, 'fields': {}}
    try:
        job_team = GameTeam.objects.filter(team_hosts__id=job.job_host.id)
    except GameTeam.DoesNotExist:
        return None
    job_header['fields']['job_dns'] = []
    job_dns = job_team.team_dns.all()
    for dns_server in job_dns:
        job_header['fields']['job_dns'].append(dns_server)
    job_header['fields']['job_host'] = {'host_fqdn': job.job_host.host_fqdn,
                                        'host_services': [],
                                        'host_ping_ratio': job.job_host.get_pinback_percent()}
    for service in job.job_host.host_services.all():
        service_d = {'service_port': service.service_port,
                     'service_protocol': service.service_protocol,
                     'service_connect': service.get_text_status(),
                     'service_content': {}}
        if service.service_content:
            service_d['service_content'] = {
                'content_type': service.service_content.content_type,
                'content_data': service.service_content.content_data
            }
        job_header['fields']['job_host']['host_services'].append(service_d)
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

    if MonitorJob.json_get_host_status(data):
        logger.debug(__name__, 'Host "%s" was reported as IP %s' % (
            job.job_host.fqdn,
            MonitorJob.json_get_host_ip_address(data)
        ))

        try:
            ping_pass = int(MonitorJob.json_get_ping_received(data))
            ping_fail = int(MonitorJob.json_get_ping_lost(data))
        except TypeError: # None returned by exception
            ping_pass = 0
            ping_fail = 100

        logger.debug(__name__,
                     'Host "%s" eas reported as %d passed and %d failed pings!' %
                     (job.job_host.host_fqdn, ping_pass, ping_fail)
        )

    if ping_pass / (ping_pass + ping_fail) < job.host.get_pinback_percent():
        logger.info(__name__, 'Host "%s" was reported as down!' % job.host.fqdn)
        job.host.status = False

    for json_service in MonitorJob.json_get_host_services(data):
        '''
        Gotta find out how this translates to the new JSON structure
        '''
        try:
            service = GameService.objects.get(pk=json_service['id'])

            if json_service['service_connect']:
                if json_service['service_connect'].upper() in GameService.SERVICE_STATUS:
                    service.status = GameService.SERVICE_STATUS[json_service['service_status']]
                else:
                    service.service_status = GameService.SERVICE_STATUS['UNKNOWN']
            if json_service['service_content']:
                if 'fail' in str(json_service['content_status']).lower() or \
                        'unknown' in str(json_service['content_status']).lower():
                    logger.debug(__name__, 'Service content for serivce "%s" on host "%s" has failed!' %
                                 (service.service_name, job.host.host_fqdn))
                service.service_status = GameService.SERVICE_STATUS['ERROR']
            service.save()
        except Exception:
            pass
    job.host.save()
    return job.host





