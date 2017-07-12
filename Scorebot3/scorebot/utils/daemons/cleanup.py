from django.utils import timezone
# from scorebot.utils import logger
from scorebot.utils.daemon import DaemonEntry
from scorebot_game.models import Job, Compromise


def init_daemon():
    return DaemonEntry('cleanup', 30, daemon_cleanup, 120)


def job_cleanup():
    print('Looking for old Jobs to cleanup..')
    # logger.debug('SBE-CLEANUP', 'Looking for old Jobs to cleanup..')
    open_jobs = Job.objects.filter(finish__isnull=True)
    if open_jobs is not None and len(open_jobs) > 0:
        now = timezone.now()
        for job in open_jobs:
            if job.is_expired(now):
                # logger.info('SBE-CLEANUP', 'Deleted stale job "%s" after passing timeout!' % str(job))
                print('Deleted stale job "%s" after passing timeout!' % str(job))
                job.delete()
    closed_jobs = Job.objects.filter(finish__isnull=False)
    if closed_jobs is not None and len(closed_jobs) > 0:
        now = timezone.now()
        for job in closed_jobs:
            if job.can_cleanup(now):
                print('Deleted finished job "%s" after cleanup timeout!' % str(job))
                # logger.info('SBE-CLEANUP', 'Deleted finished job "%s" after cleanup timeout!' % str(job))
                job.delete()
    open_beacons = Compromise.objects.filter(finish__isnull=True)
    print('Looking for expired Beacons..')
    # logger.debug('SBE-CLEANUP', 'Looking for expired Beacons..')
    if open_beacons is not None and len(open_beacons) > 0:
        now = timezone.now()
        for beacon in open_beacons:
            if beacon.is_expired(now):
                print('Closing an expired Beacon..')
                # logger.debug('SBE-CLEANUP', 'Closing an expired Beacon..')
                beacon.finish = now
                beacon.save()
    del open_jobs
    del closed_jobs
    del open_beacons


def daemon_cleanup():
    job_cleanup()
