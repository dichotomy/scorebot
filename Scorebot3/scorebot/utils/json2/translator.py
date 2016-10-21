import json
import scorebot.utils.log as logger

from django.utils import timezone
from sbegame.models import MonitorJob
from sbehost.models import GameTeam, GameService


def to_job_json(job):
    job_header = {'status': 'job', 'model': 'scorebot.job', 'pk': job.id, 'fields': {}}
    try:
        job_team = GameTeam.objects.get(team_hosts__id=job.job_host.id)
    except GameTeam.DoesNotExist:
        return None
    job_header['fields']['job_dns'] = []
    job_dns = job_team.team_dns.all()
    for dns_server in job_dns:
        job_header['fields']['job_dns'].append(dns_server.dns_address)
    job_header['fields']['job_host'] = {'host_fqdn': job.job_host.host_fqdn,
                                        'host_services': [],
                                        'host_ping_ratio': job.job_host.get_pinback_percent()}
    for svc in job.job_host.host_services.all():
        svc_d = {'service_port': svc.service_port, 'service_protocol': svc.service_protocol,
                 'service_connect': svc.get_text_status(), 'service_content': {}}
        if svc.service_content:
            svc_d['service_content'] = {'content_type': svc.service_content.content_type,
                                        'content_data': svc.service_content.content_data,
                                        'content_status': 'UNKNOWN'}
        job_header['fields']['job_host']['host_services'].append(svc_d)
    return json.dumps(job_header)


def from_job_json(monitor, jsond):
    try:
        json_data = json.loads(jsond)
    except ValueError:
        logger.warning(__name__, 'Monitor "%s" submitted incorrect JSON data!' % monitor.monitor_name)
        return None
    if 'wait' in json_data['status']:
        logger.warning(__name__, 'Monitor "%s" submitted a stale Job!' % monitor.monitor_name)
        return None
    try:
        job_inst = MonitorJob.objects.get(pk=int(json_data['pk']))
    except ValueError:
        logger.warning(__name__, 'Monitor "%s" and invalid Job!' % monitor.monitor_name)
        return None
    except MonitorJob.DoesNotExist:
        logger.warning(__name__, 'Monitor "%s" and non-existent Job!' % monitor.monitor_name)
        return None
    if 'status' in json_data['fields']['job_host']:
        logger.debug(__name__, '"%s": Host "%s" was reported as IP %s' %
                     (monitor.monitor_name, job_inst.job_host.host_fqdn,
                      json_data['fields']['job_host']['status']['ip_address']))
        try:
            ping_pass = int(json_data['fields']['job_host']['status']['ping_received'])
            ping_fail = int(json_data['fields']['job_host']['status']['ping_lost'])
        except ValueError:
            ping_pass = 0
            ping_fail = 100
        except IndexError:
            ping_pass = 0
            ping_fail = 100
        logger.debug(__name__, 'Host "%s" eas reported as %d passed and %d failed pings!' %
                     (job_inst.job_host.host_fqdn, ping_pass, ping_fail))
    else:
        logger.warning(__name__, 'Monitor "%s" did not return a status block!' % monitor.monitor_name)
        return None
    if ping_pass / (ping_pass + ping_fail) < job_inst.job_host.get_pinback_percent():
        logger.info(__name__, '"%s": Host "%s" was reported as down!' % (monitor.monitor_name, job_inst.job_host.host_fqdn))
        job_inst.job_host.host_status = False
    for svc in json_data['fields']['job_host']['host_services']:
        for svri in job_inst.job_host.host_services.all():
            try:
                if svri.service_port == int(svc['service_port']) and svri.service_protocol == svc['service_protocol']:
                    svc_ins = svri
                    break
            except ValueError:
                pass
        if 'service_connect' in svc:
            if svc['service_connect'].upper() in GameService.SERVICE_STATUS:
                svc_ins.service_status = GameService.SERVICE_STATUS[svc['service_connect']]
            else:
                svc_ins.service_status = GameService.SERVICE_STATUS['UNKNOWN']
        if 'service_content' in svc and 'content_status' in svc['service_content']:
            if 'fail' in str(svc['service_content']['content_status']).lower() \
                    or 'unknown' in str(svc['service_content']['content_status']).lower():
                logger.debug(__name__, '"%s": Service content for service "%s" on host "%s" has failed!' %
                             (monitor.monitor_name, svc_ins.service_name, job_inst.job_host.host_fqdn))
                svc_ins.service_status = GameService.SERVICE_STATUS['ERROR']
        svc_ins.save()
    job_inst.job_finish = timezone.now()
    job_inst.job_host.save()
    job_inst.save()
    return job_inst




