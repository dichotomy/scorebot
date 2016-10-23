import json
import scorebot.utils.log as logger

from sbegame.models import MonitorJob
from sbehost.models import GameHost, GameDNS, GameTeam, GameService


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
    for svc in job.job_host.host_services.all():
        svc_d = {'service_port': svc.service_port, 'service_protocol': svc.service_protocol,
                 'service_connect': svc.get_text_status(), 'service_content': {}}
        if svc.service_content:
            svc_d['service_content'] = {'content_type': svc.service_content.content_type,
                                        'content_data': svc.service_content.content_data}
        job_header['fields']['job_host']['host_services'].append(svc_d)
    return json.dumps(job_header)


def from_job_json(monitor, jsond):
    try:
        json_data = json.loads(jsond)
    except ValueError:
        return None
    if 'wait' in json_data['status']:
        return None
    try:
        job_inst = MonitorJob.objects.get(pk=int(json_data['pk']))
    except ValueError:
        return None
    except MonitorJob.DoesNotExist:
        return None
    if json_data['fields']['job_host']['status']:
        logger.debug(__name__, 'Host "%s" was reported as IP %s' %
                     (job_inst.job_host.host_fqdn, json_data['fields']['job_host']['status']['ip_address']))
        try:
            ping_pass = int(json_data['fields']['job_host']['status']['ping_received'])
            ping_fail = int(json_data['fields']['job_host']['status']['ping_lost'])
        except ValueError:
            ping_pass = 0
            ping_fail = 100
        logger.debug(__name__, 'Host "%s" eas reported as %d passed and %d failed pings!' %
                     (job_inst.job_host.host_fqdn, ping_pass, ping_fail))
    if ping_pass / (ping_pass + ping_fail) < job_inst.job_host.get_pinback_percent():
        logger.info('Host "%s" was reported as down!' % job_inst.job_host.host_fqdn)
        job_inst.job_host.host_status = False
    for svc in json_data['fields']['job_host']['host_services']:
        for svri in job_inst.job_host.host_services:
            try:
                if svri.servicd_port == int(svc['service_port']) and svri.service_protocol == svc['service_protocol']:
                    svc_ins = svri
                    break
            except ValueError:
                pass
        if svc['service_connect']:
            if svc['service_connect'].upper() in GameService.SERVICE_STATUS:
                svc_ins.service_status = GameService.SERVICE_STATUS[svc['service_status']]
            else:
                svc_ins.service_status = GameService.SERVICE_STATUS['UNKNOWN']
        if svc['service_content']:
            if 'fail' in str(svc['content_status']).lower() or 'unknown' in str(svc['content_status']).lower():
                logger.debug(__name__, 'Service content for serivce "%s" on host "%s" has failed!' %
                             (svc_ins.service_name, job_inst.job_host.host_fqdn))
            svc_ins.service_status = GameService.SERVICE_STATUS['ERROR']
        svc_ins.save()
    job_inst.job_host.save()
    return job_inst.job_host





