import json
import random
from datetime import datetime

from django.db import models
from django.db.models import Max, Min
from django.utils import timezone

"""
    SBE Host Models

    Contains all Models that would be considered in game
"""

CONNECT_STATUS_CHOICES = (
    ('1', 'success'),
    ('2', 'reset'),
    ('3', 'timeout'),
)


class Game(models.Model):
    GAME_MODES = {
        'RVB': 0,       # Standard Red vs Blue
        'BVB': 1,       # Blue vs Blue (Binjutisu)
        'KING': 2,      # King of the Box
        'RUSH': 3,      # Offense Time Trial
        'DEFEND': 4,    # Defense Time Trial
    }

    __desc__ = """
        SBE Game

        The Game object is a struct that holds all the data for a Scorebot game.
    """
    __historical__ = True

    class Meta:
        verbose_name = 'SBE Game'
        verbose_name_plural = 'SBE Games'

    name = models.CharField('Game Name', max_length=250)
    mode = models.SmallIntegerField('Game Mode', default=0)
    paused = models.BooleanField('Game Pause', default=False)
    start = models.DateTimeField('Game Start', auto_now_add=True)
    finish = models.DateTimeField('Game Finish', blank=True, null=True)
    options_cool = models.SmallIntegerField('Game Cool Down', default=300)
    options_flag_percent = models.SmallIntegerField('Game Flag Percentage', default=60)
    options_ticket_percent = models.SmallIntegerField('Game Ticket Percentage', default=65)
    monitors = models.ManyToManyField('sbegame.MonitorServer', through='sbehost.GameMonitor')
    host_default_ping_ratio = models.SmallIntegerField('Game Host Pinback Percent', default=50)
    options_ticket_wait = models.SmallIntegerField('Game Ticket First Hold Time (Sec)', default=180)
    offensive = models.ManyToManyField('sbegame.Player', through='sbehost.GamePlayer',
                                            through_fields=('game', 'player'))

    def __str__(self):
        return '%s Game %s (%s-%s) %d Teams' % (('[Running]' if not self.paused else '[Paused]'),
                                               self.name, self.start.strftime('%m/%d/%y %H:%M'),
                                               (self.finish.strftime('%m/%d/%y %H:%M')
                                                if self.finish else 'Present'), self.gameteam_set.all().count())


class GameDNS(models.Model):
    __desc__ = """
        SBE Game DNS

        SBE Game DNS is basically a placeholder for a Team's DNS server(s).
    """

    class Meta:
        verbose_name = 'SBE DNS Server'
        verbose_name_plural = 'SBE DNS Servers'

    address = models.CharField('DNS Server Address', max_length=140)

    def __str__(self):
        return 'Game DNS (%s)' % self.address


class GameTeam(models.Model):
    BASIC_TEAM_NAMES = [
        'ALPHA',
        'BETA',
        'CHARLIE',
        'DELTA',
        'ECHO',
        'ZETA',
        'EPSILON',
    ]

    __desc__ = """
        SBE Game Team

        The Game Team object is a reference to the players on a team and the
        data that keeps together the game during play, specified by the team.
    """
    __historical__ = True

    static_name = None
    static_color = None

    class Meta:
        verbose_name = 'SBE Game Team'
        verbose_name_plural = 'SBE Game Team'

    game = models.ForeignKey(Game)
    dns = models.ManyToManyField('sbehost.GameDNS')
    flags = models.ManyToManyField('sbehost.GameFlag')
    tickets = models.ManyToManyField('sbehost.GameTicket')
    team = models.ForeignKey('sbegame.Team', blank=True, null=True)  # Reference to existing team, null if auto
    score_flags = models.IntegerField('Team Score (Flags)', default=0)
    score_basic = models.IntegerField('Team Score (Uptime)', default=0)
    score_beacons = models.IntegerField('Team Score (Becons)', default=0)
    score_tickets = models.IntegerField('Team Score (Tickets)', default=0)
    players = models.ManyToManyField('sbegame.Player', through='sbehost.GamePlayer',
                                          through_fields=('team', 'player'))

    def __len__(self):
        return self.score_basic + self.score_beacons + self.score_flags + self.score_tickets

    def __str__(self):
        return 'GameTeam (%s:%d) %s' % (self.get_name(), self.get_color(), self.__len__())

    def get_name(self):
        # Use this instead of .name
        if self.team:
            return self.team.name
        if not self.static_name:
            self.static_name = GameTeam.BASIC_TEAM_NAMES[random.randint(0, len(GameTeam.BASIC_TEAM_NAMES)-1)]
        return self.static_name

    def get_color(self):
        # Use this instead of .color
        if self.team:
            return self.team.color
        if not self.static_color:
            self.static_color = random.randint(0, 66113)
        return self.static_color


class GameCompromise(models.Model):
    __desc__ = """
        SBE Game Host Compromise

        This will be created when a host is compromised.  Will store the compromises as start/end times
        to easier facilitate the timespan that a host is compromised.
    """
    __historical__ = True

    class Meta:
        verbose_name = 'SBE Host Compromise'
        verbose_name_plural = 'SBE Host Compromises'

    game_host = models.ForeignKey('GameHost', null=True, blank=True)
    player = models.ForeignKey('sbegame.Player', null=True, blank=True)
    start = models.DateTimeField('Compromise Start', default=datetime.now)
    finish = models.DateTimeField('Compromise End', null=True, blank=True)

    def __len__(self):
        if self.finish:
            return (self.finish - self.start).seconds
        return (timezone.now() - self.start).seconds

    def __str__(self):
        return '%s (%d seconds)' % (self.player.name, self.__len__())

    def __bool__(self):
        return self.finish is None

    def __nonzero__(self):
        return self.__bool__()


class GameHost(models.Model):
    __desc__ = """
        SBE Game Host

        The SBE Game Host is the central structure of the SBE Database.  This struct will host the compromises, flags
        tickets and services that operate with this host.
    """

    class Meta:
        verbose_name = 'SBE Game Host'
        verbose_name_plural = 'SBE Game Hosts'

    game_team = models.ForeignKey(GameTeam)
    server = models.ForeignKey('sbegame.HostServer')
    flags = models.ManyToManyField('sbehost.GameFlag')
    fqdn = models.CharField('Host Name', max_length=250)
    tickets = models.ManyToManyField('sbehost.GameTicket')
    # Trying to design a setup that dosen't need this
    used = models.BooleanField('Host in Game', default=False)
    status = models.BooleanField('Host Online', default=False)
    ping_ratio = models.SmallIntegerField('Host Pingback Percentage', default=0)
    ping_lost = models.IntegerField(default=0)
    ping_received = models.IntegerField(default=0)
    name = models.CharField('Host VM Name', max_length=250, null=True, blank=True)

    def __str__(self):
        return 'Host %s (%s)' % (self.fqdn,
                                 '; '.join(
                                     ['%d' % f.application.port
                                      for f in self.gameservice_set.all()]))

    def __bool__(self):
        if GameCompromise.objects.filter(game_host__id=self.id).count() > 0:
            return True
        return False

    def __nonzero__(self):
        return self.__bool__()


class GameFlag(models.Model):
    FLAG_VALUES = {
        'FLAG_TAKEN': 1,
        'FLAG_ENABLED': 2,
        'FLAG_HIDDEN': 3,
        'FLAG_PERMA': 4,
    }

    __desc__ = """
        SBE Game Flag

        The SBE Flag struct holds the information of flags, mainly what the flag value is and if the flag has been
        taken.
    """

    class Meta:
        verbose_name = 'SBE Game Flag'
        verbose_name_plural = 'SBE Game Flags'

    name = models.CharField('Flag Name', max_length=250)
    answer = models.CharField('Flag Answer', max_length=500)
    value = models.SmallIntegerField('Flag Value', default=100)
    options = models.SmallIntegerField('Flag Options', default=2)
    owner = models.ForeignKey('sbegame.Player', null=True, blank=True)

    def __str__(self):
        return 'Flag %s (%d)' % (self.name, self.value)

    def __bool__(self):
        return self.get_option(1) is False and self.online

    def __nonzero__(self):
        return self.__bool__()

    def get_option(self, option):
        if isinstance(option, int):
            level = option
        elif isinstance(option, str):
            if option in GameFlag.FLAG_VALUES:
                level = GameFlag.FLAG_VALUES[option]
            else:
                raise IndexError('The option value "%s" does not exist!' % option)
        else:
            raise TypeError('Must be an integer or key option string!')
        return (self.options & (1 << level)) > 0

    def __getitem__(self, item):
        return self.check_rule(item)

    def set_rule(self, option, value):
        if isinstance(option, int):
            level = option
        elif isinstance(option, str):
            if option in GameFlag.FLAG_VALUES:
                level = GameFlag.FLAG_VALUES[option]
            else:
                raise IndexError('The option value "%s" does not exist!' % option)
        else:
            raise TypeError('Must be an integer or key option string!')
        if value:
            self.options = (self.options | (1 << level))
        else:
            self.options = (self.options & (~(1 << level)))

    def __setitem__(self, key, value):
        self.set_rule(key, value)


class GamePlayer(models.Model):
    __desc__ = """
        SBE Game Player

        This is a Djando through field for Many to Many with player to store additional data, such as score.
    """

    class Meta:
        verbose_name = 'SBE Game Player'
        verbose_name_plural = 'SBE Game Players'

    player = models.ForeignKey('sbegame.Player')
    score = models.IntegerField('Player Current Score', default=0)
    game = models.ForeignKey('sbehost.Game', null=True, blank=True)      # Only Red Players
    team = models.ForeignKey('sbehost.GameTeam', null=True, blank=True)  # Only Blue Players

    def __str__(self):
        return '%s (Score: %d)' % (self.player.name, self.score)


class GameTicket(models.Model):
    __desc__ = """
        SBE Game Ticket

        A SBE Game Ticket holds the data for the a ticket generated for teams.
    """

    class Meta:
        verbose_name = 'SBE Ticket'
        verbose_name_plural = 'SBE Tickets'

    name = models.CharField('Ticket Name', max_length=250)
    value = models.SmallIntegerField('Ticket Value', default=500)
    expired = models.BooleanField('Ticket Expired', default=False)
    content = models.CharField('Ticket Body Content', max_length=1000)
    expires = models.DateTimeField('Ticket Expires', blank=True, null=True)
    started = models.DateTimeField('Ticket Assigned', blank=True, null=True)
    completed = models.DateTimeField('Ticket Completed', blank=True, null=True)
    reopened_count = models.IntegerField(default=0)

    def __len__(self):
        if not self.started:
            return 0
        if self.completed:
            return (self.completed - self.started).seconds
        return (self.expires - self.started).seconds

    def __str__(self):
        return 'Ticket %s (%d) %d sec' % (self.name, self.value, self.__len__())

    def __bool__(self):
        return self.completed or self.expired

    def __nonzero__(self):
        return self.__bool__()


class GameMonitor(models.Model):
    __desc__ = """
        SBE Game Monitor

        This is a Django through object to store additional data for a Many to Many relationship
    """

    class Meta:
        verbose_name = 'SBE Game Monitor'
        verbose_name_plural = 'SBE Game Monitors'

    game = models.ForeignKey('sbehost.Game')
    server = models.ForeignKey('sbegame.MonitorServer')
    hosts = models.ManyToManyField('sbehost.GameHost')

    def __str__(self):
        return 'Montor %s (%s) Hosts' % (self.server.monitor_name, self.hosts.all().count())


class ServiceApplication(models.Model):
    __desc__ = """
        SBE Service Application

        The SBE Application describes the port, L4 protocol, and
        application level protocol
    """

    class Meta:
        verbose_name = 'SBE Application'
        verbose_name_plural = 'SBE Applications'

    port = models.SmallIntegerField('Service Port', default=0)
    application_protocol = models.CharField('Application Protocol',
                                            max_length=64,
                                            default='http')
    layer4_protocol = models.CharField('Service Protocol',
                                       max_length=4,
                                       default='tcp')

    def __str__(self):
        return 'Application %s:%d using %s' % (self.application_protocol,
                                               self.port,
                                               self.layer4_protocol)


class GameService(models.Model):
    __desc__ = """
        SBE Game Service

        The SBE Service contains the port/protocol status and
        configuration for a host service.
    """

    class Meta:
        verbose_name = 'SBE Service'
        verbose_name_plural = 'SBE Services'

    name = models.CharField('Service Name', max_length=128)
    value = models.SmallIntegerField('Service Value', default=50)
    status = models.CharField('Service Status', max_length=16, default='1',
                              choices=CONNECT_STATUS_CHOICES)
    bonus = models.BooleanField('Service is Bonus', default=False)
    application = models.ForeignKey(ServiceApplication)
    game_host = models.ForeignKey(GameHost)

    def __str__(self):
        return '%s (%d/%s) %s' % (self.name, self.application.port,
                                  self.application.application_protocol,
                                  self.value)

    def __bool__(self):
        return self.status == 0

    def __nonzero__(self):
        return self.__bool__()

    @classmethod
    def get_random(cls):
        max_min = cls.objects.filter(game_host__finished__isnull=True).\
                              aggregate(Max('id'), Min('id'))
        max = max_min['id__max']
        min = max_min['id__min']
        return random.randint(min, max)

    @classmethod
    def get_current_services(cls):
        return cls.objects.filter(
            game_host__game_team__game__finish__isnull=True
        )

    def get_text_status(self):
        for k, v in GameService.SERVICE_STATUS:
            if self.status == v:
                return k
        return 'UP'


class GameContent(models.Model):
    __desc___ = """
        SBE Service Content

        Contains the content for a service (if any).
        Content is stored in a text field and can be text or binary.
        Content type is used to understand the data type
    """

    class Meta:
        verbose_name = 'SBE Service Content'
        verbose_name_plural = 'SBE Service Contents'

    HTTP_VERB_CHOICES = (
        ('1', 'GET'),
        ('2', 'POST'),
    )

    service = models.ForeignKey(GameService)
    data = models.TextField('Data', null=True, blank=True)
    content_type = models.CharField('Content Type', max_length=75,
                                    default='text')
    http_verb = models.CharField(max_length=16,
                                 choices=HTTP_VERB_CHOICES,
                                 null=True,
                                 blank=True)
    url = models.URLField(null=True, blank=True)
    connect_status = models.CharField(max_length=16,
                                      choices=CONNECT_STATUS_CHOICES,
                                      null=True,
                                      blank=True)

    def __str__(self):
        return 'Content (%s=%s)' % (self.content_type, self.data)

    def monitor_json(self):
        return '{ "content_type": "%s", "content_data": %s }' % (
            self.content_type,
            json.dumps(self.data)
        )



