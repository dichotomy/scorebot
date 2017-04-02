from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User

from random import shuffle

import scorebot.utils.log as logger



class Team(models.Model):
    __desc__ = """
        SBE Team Object

        The Team Object holds the data for the teams in all games.  The Team object is unique per team and state is
        kept through games.  This will hold the reference to the players in the team and the Team overall score.
    """

    class Meta:
        verbose_name = 'SBE Team'
        verbose_name_plural = 'SBE Teams'

    players = models.ManyToManyField('sbegame.Player')
    score = models.BigIntegerField('Team Overall Score', default=0)
    name = models.CharField('Team Name', max_length=250, unique=True)
    color = models.IntegerField('Team Color', default=int('FFFFFF', 16))
    registered = models.DateField('Team Registration Date', auto_now_add=True)
    last_played = models.DateTimeField('Team Last Played', null=True, blank=True)

    def __len__(self):
        return self.players.all().count()

    def __str__(self):
        return '%s (Score: %d)' % (self.name, self.score)

    def get_color(self):
        return hex(self.color)

    def __getitem__(self, item):
        if isinstance(item, int):
            val = int(item)
            if 0 < val < len(self.players.all().count()):
                return self.players.all()[val]
            else:
                raise IndexError(val)
        elif isinstance(item, str):
            try:
                return self.players.all().filter(name=item).first()
            except Player.DoesNotExist:
                raise KeyError(item)
        raise TypeError(item)


class Player(models.Model):
    __desc__ = """
        SBE Player Object

        The Player Object holds the data for the individual players in all games.  The Player object is unique
        per player and state is kept through games.  This will contain references to the user login for the player
        and overall score.
    """

    class Meta:
        verbose_name = 'SBE Player'
        verbose_name_plural = 'SBE Players'

    user = models.ForeignKey(User, null=True, blank=True)
    score = models.BigIntegerField('Player Overall Score', default=0)
    name = models.CharField('Player Display Name', max_length=150, unique=True)

    def __len__(self):
        return self.score

    def __str__(self):
        return '%s (Score: %d)' % (self.name, self.score)

    def __lt__(self, other):
        return isinstance(other, Player) and other.score > self.score

    def __gt__(self, other):
        return isinstance(other, Player) and other.score < self.score

    def __eq__(self, other):
        return isinstance(other, Player) and other.score == self.score


class AccessKey(models.Model):
    KEY_LEVELS = {
        'ALL_READ': 1,
        'ALL_UPDATE': 2,
        'ALL_CREATE': 3,
        'ALL_DELETE': 4,
        'GamePlayer.READ': 5,
        'GamePlayer.UPDATE': 6,
        'GamePlayer.CREATE': 7,
        'GamePlayer.DELETE': 8,
        'GameCompromise.READ': 9,
        'GameCompromise.UPDATE': 10,
        'GameCompromise.CREATE': 11,
        'GameCompromise.DELETE': 12,
        'GameHost.READ': 13,
        'GameHost.UPDATE': 14,
        'GameHost.CREATE': 15,
        'GameHost.DELETE': 16,
        'GameTicket.READ': 17,
        'GameTicket.UPDATE': 18,
        'GameTicket.CREATE': 19,
        'GameTicket.DELETE': 20,
        'GameDNS.READ': 21,
        'GameDNS.UPDATE': 22,
        'GameDNS.CREATE': 23,
        'GameDNS.DELETE': 24,
        'GameContent.READ': 25,
        'GameContent.UPDATE': 26,
        'GameContent.CREATE': 27,
        'GameContent.DELETE': 28,
        'Game.READ': 29,
        'Game.UPDATE': 30,
        'Game.CREATE': 31,
        'Game.DELETE': 32,
        'GameService.READ': 33,
        'GameService.UPDATE': 34,
        'GameService.CREATE': 35,
        'GameService.DELETE': 36,
        'GameTeam.READ': 37,
        'GameTeam.UPDATE': 38,
        'GameTeam.CREATE': 39,
        'GameTeam.DELETE': 40,
        'GameFlag.READ': 41,
        'GameFlag.UPDATE': 42,
        'GameFlag.CREATE': 43,
        'GameFlag.DELETE': 44,
        'Player.READ': 45,
        'Player.UPDATE': 46,
        'Player.CREATE': 47,
        'Player.DELETE': 48,
        'Team.READ': 49,
        'Team.UPDATE': 50,
        'Team.CREATE': 51,
        'Team.DELETE': 52,
    }

    __desc__ = """
        SBE AccessKey

        And AccessKey grants a user/service access to the SBE API. Each API Key has a permission level that allows it
        to read/write to structures.  AccessKeys given to Monitors will use the Monitor permissions, regardless of
        the current permissions set.  Monitor permissions allow the user/service to read and write to the host currently
        assigned to the Monitor.
    """

    class Meta:
        verbose_name = 'SBE Access Key'
        verbose_name_plural = 'SBE Access Keys'

    key_level = models.BigIntegerField('Key Access Level', default=1)
    key_uuid = models.CharField('Key UUID', max_length=250, unique=True)

    def __str__(self):
        return 'Key %s (%d)' % (self.key_uuid, self.key_level)

    def __bool__(self):
        return self.__nonzero()

    def __nonzero(self):
        return self.key_level > 0

    def check_rule(self, rule):
        if isinstance(rule, int):
            level = rule
        elif isinstance(rule, str):
            if rule in AccessKey.KEY_LEVELS:
                level = AccessKey.KEY_LEVELS[rule]
            else:
                raise IndexError('The rule value "%s" does not exist!' % rule)
        else:
            raise TypeError('Must be an integer or key level string!')
        return (self.key_level & (1 << level)) > 0

    def __getitem__(self, item):
        return self.check_rule(item)

    def set_rule(self, rule, value):
        if isinstance(rule, int):
            level = rule
        elif isinstance(rule, str):
            if rule in AccessKey.KEY_LEVELS:
                level = AccessKey.KEY_LEVELS[rule]
            else:
                raise IndexError('The rule value "%s" does not exist!' % rule)
        else:
            raise TypeError('Must be an integer or key level string!')
        if value:
            self.key_level = (self.key_level | (1 << level))
        else:
            self.key_level = (self.key_level & (~(1 << level)))

    def __setitem__(self, key, value):
        self.set_rule(key, value)


class HostServer(models.Model):
    __desc__ = """
        SBE Host Server

        A Host Server is a bare metal VM that hosts the game hosts.
        This model enables SBE to send a command through
        the Monitors to start/stop/revert hosts on demand.
    """

    class Meta:
        verbose_name = 'SBE Host Server'
        verbose_name_plural = 'SBE Host Servers'

    name = models.CharField('Host Server Name', max_length=250)
    address = models.CharField('Host Server Address', max_length=150)

    def __str__(self):
        return 'Host %s (%s)' % (self.name, self.address)


class MonitorJob(models.Model):
    __desc__ = """
        SBE Monitor Job

        SBE Monitor Jobs keep track of all the on-goings on the monitors.
        The jobs allow fast and efficient scheduling
        and sync between monitors.
    """

    class Meta:
        verbose_name = 'SBE Monitor Job'
        verbose_name_plural = 'SBE Monitor Jobs'

    monitor = models.ForeignKey('sbegame.MonitorServer', null=True, blank=True)
    start = models.DateTimeField('Job Start', blank=True, null=True)
    finish = models.DateTimeField('Job End', blank=True, null=True)
    service = models.ForeignKey('sbehost.GameService')

    @staticmethod
    def get_jobs_pending():
        return MonitorJob.objects.filter(
            service__game_host__game_team__game__finish__isnull=True,
            start__isnull=True,
            finish__isnull=True,
            monitor__isnull=True
        )

    @staticmethod
    def get_job_pending(monitor, service_id=None):
        job = None
        if service_id is None:
            #  Get single pending job randomly
            with transaction.atomic():
                jobs = MonitorJob.get_jobs_pending()

                if len(jobs):
                    job = MonitorJob.create_pending_job(jobs, monitor)
        else:
            try:
                job = MonitorJob.objects.get(start__isnull=True,
                                             finish__isnull=True,
                                             service__id=service_id)
            except MonitorJob.DoesNotExist:
                logger.warning(__name__,
                               'Job for service <%d> is not pending' % service_id)
        return job

    @staticmethod
    def create_pending_job(jobs, monitor):
        jobs = [j for j in jobs]
        shuffle(jobs)
        job = jobs.pop()
        job.monitor = monitor
        job.start = timezone.now()
        job.save()

        return job

    @staticmethod
    def create_new_jobs(services):
        jobs = []
        for s in services:
            job = MonitorJob(service=s)
            job.save()
            jobs.append(job)

        return jobs

    @staticmethod
    def json_get_job_status(data):
        val = None
        try:
            val = data['status']
        except KeyError:
            logger.exception(__name__, 'job status key does not exist.')
        return val

    @staticmethod
    def json_get_host_ip_address(data):
        val = None
        try:
            val = data['fields']['job_host']['ip_address']
        except KeyError:
            logger.exception(__name__, 'ip_address key does not exists.')
        return val

    @staticmethod
    def json_get_host_status(data):
        val = None
        try:
            val = data['status']
        except KeyError:
            logger.exception(__name__, 'job_host => status key does not exist.')
        return val

    @staticmethod
    def json_get_host_services(data):
        val = None
        try:
            val = data['fields']['job_host']['services']
        except KeyError:
            logger.exception(__name__, 'host_services key does not exist.')
        return val

    @staticmethod
    def json_get_ping_ratio(data):
        val = None
        try:
            val = data['fields']['job_host']['host_ping_ratio']
        except KeyError:
            logger.exception(__name__, 'host_ping_ratio does not exist')
        return val

    @staticmethod
    def json_has_connect_status(service_data):
        val = False
        try:
            val = service_data['connect']
        except KeyError:
            logger.exception(
                __name__,
                'service <%d>: has no connect status' % service_data['id']
            )
        return val

    def __len__(self):
        if self.finish:
            return (self.finish - self.start).seconds
        return (timezone.now() - self.start).seconds

    def __str__(self):
        return 'Job %d [%s]' % (self.id, 'Done' if self.finish else 'Running')


class MonitorServer(models.Model):
    __desc__ = """
        SBE Monitor

        The SBE Monitor is the core of the game management.  Monitors detect, check and routes some forms of
        traffic.
    """

    class Meta:
        verbose_name = 'SBE Monitor'
        verbose_name_plural = 'SBE Monitors'

    key = models.ForeignKey('sbegame.AccessKey')
    name = models.CharField('Monitor Name', max_length=250)
    address = models.CharField('Monitor Last IP', max_length=140, blank=True, null=True)

    def __str__(self):
        return 'Monitor %s' % self.name
