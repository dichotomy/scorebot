from django.utils import timezone

from daemon import DaemonEntry
from scorebot.utils.logger import log_debug
from scorebot_game.models import Job, GameCompromise, GameEvent


def init_daemon():
    return DaemonEntry('cleanup', 30, daemon_cleanup, 120)


def job_cleanup():
    log_debug('DAEMON', 'Looking for old Jobs to cleanup..')
    job_expired = Job.objects.filter(finish__isnull=True)
    if job_expired is not None and len(job_expired) > 0:
        expire_time = timezone.now()
        for job in job_expired:
            if job.is_expired(expire_time):
                log_debug('DAEMON', 'Deleted stale job "%d" after passing timeout!' % job.id)
                job.delete()
        del expire_time
    jobs_closed = Job.objects.filter(finish__isnull=False)
    if jobs_closed is not None and len(jobs_closed) > 0:
        closed_time = timezone.now()
        for job in jobs_closed:
            if job.can_cleanup(closed_time):
                log_debug('DAEMON', 'Deleted finished job "%d" after cleanup timeout!' % job.id)
                job.delete()
        del closed_time
    beacons_open = GameCompromise.objects.filter(finish__isnull=True)
    log_debug('DAEMON', 'Looking for expired Beacons..')
    if beacons_open is not None and len(beacons_open) > 0:
        expire_time = timezone.now()
        for beacon in beacons_open:
            if beacon.is_expired(expire_time):
                log_debug('DAEMON', 'Closing an expired Beacon "%s"..' % beacon.__str__())
                beacon.finish = expire_time
                beacon.save()
        del expire_time
    events_open = GameEvent.objects.all()
    if len(events_open) > 0:
        expire_time = timezone.now()
        for event in events_open:
            if event.is_expired(expire_time):
                event.delete()
                log_debug('DAEMON', 'Deleting an expired Event "%s"..' % event.__str__())
    del job_expired
    del jobs_closed
    del beacons_open


def daemon_cleanup():
    job_cleanup()
