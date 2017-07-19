import uuid
import random

from django.db import models
from datetime import timedelta
from django.utils import timezone
from scorebot.utils.constants import *
from django.contrib.auth.models import User


def score_create_new():
    score_object = Score()
    score_object.save()
    return score_object


def token_create_new_uuid():
    return uuid.uuid4()


def team_create_new_color():
    return random.randint(0, 0xFFFFFF)


def token_create_new(expire_days=0):
    token_object = Token()
    if expire_days > 0:
        token_object.expires = (timezone.now() + timedelta(days=expire_days))
    token_object.save()
    return token_object


class PlayerManager(models.Manager):
    """
    Scorebot v3: PlayerManager

    Enables the "get_player" method to call on players by username or create new ones on the fly.
    """

    def get_player(self, player_name):
        try:
            player_object = self.get(name=player_name)
        except Player.DoesNotExist:
            player_object = Player()
            player_object.name = player_name
            player_object.save()
        return player_object


class Team(models.Model):
    """
    Scorebot v3: Team

    Basic Team representation class, can save data per team to save scores and track data.
    These teams persist beyond games.  Team object in game.Team is separate from this model!
    """

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    name = models.CharField('Team Name', max_length=150, unique=True)
    players = models.ManyToManyField('scorebot_core.Player', blank=True)
    color = models.IntegerField('Team Color', default=team_create_new_color)
    last = models.DateTimeField('Team Last Game', null=True, blank=True, editable=False)
    created = models.DateTimeField('Team Registration', auto_now_add=True, editable=False)
    logo = models.ImageField('Team Logo', upload_to=CONST_GAME_GAME_TEAM_LOGO_DIR, null=True, blank=True)
    score = models.OneToOneField('scorebot_core.Score', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '[Team] %s (%d)' % (self.name, self.score.get_score())

    def __len__(self):
        return self.score.__len__()

    def __lt__(self, other):
        return isinstance(other, Team) and other.score > self.score

    def __gt__(self, other):
        return isinstance(other, Team) and other.score < self.score

    def __eq__(self, other):
        return isinstance(other, Team) and other.score == self.score

    def save(self, *args, **kwargs):
        if self.score is None:
            self.score = score_create_new()
        super(Team, self).save(*args, **kwargs)


class Token(models.Model):
    """
    Scorebot v3: Token

    Class that can store a time dependent key for use with authentication.
    """

    class Meta:
        verbose_name = 'Token'
        get_latest_by = 'expires'
        verbose_name_plural = 'Tokens'

    expires = models.DateTimeField('Token Expire', null=True, blank=True)
    uuid = models.UUIDField('Token ID', primary_key=True, default=token_create_new_uuid, editable=False)

    def __str__(self):
        return '[Token] %s - %s' % (self.uuid, (self.expires.strftime('%m/%d/%y %H:%M:%S')
                                                if self.expires is not None else 'Forever'))

    def __len__(self):
        return max((self.expires - timezone.now()).seconds, 0) if self.expires is not None else 0

    def __bool__(self):
        return self.__len__() > 0 if self.expires is not None else True

    def get_json_export(self):
        return {'expires': (self.expires.toordinal() if self.expires is not None else None), 'uuid': self.uuid}


class Score(models.Model):
    """
    Scorebot v3: Score

    Stores Score based data in separate integers for tracking.  Stores date to save time scored.
    """

    class Meta:
        verbose_name = 'Score'
        get_latest_by = 'date'
        verbose_name_plural = 'Scores'

    flags = models.IntegerField('Flags', default=0)
    uptime = models.IntegerField('Uptime', default=0)
    tickets = models.IntegerField('Tickets', default=0)
    beacons = models.IntegerField('Beacons', default=0)
    date = models.DateTimeField('Time', auto_now_add=True)

    def __str__(self):
        return '[Score] F:%d U:%d T:%d B:%d @ %s' % (self.flags, self.uptime, self.tickets, self.beacons,
                                                     self.date.strftime('%m/%d/%y;%H:%M.%S'))

    def __len__(self):
        return max(self.get_score(), 0)

    def __bool__(self):
        return self.__len__() > 0

    def get_score(self):
        return self.flags + self.uptime + self.tickets + self.beacons

    def __lt__(self, other):
        return isinstance(other, Score) and len(other) < self.__len__()

    def __gt__(self, other):
        return isinstance(other, Score) and len(other) > self.__len__()

    def __eq__(self, other):
        return isinstance(other, Score) and len(other) == self.__len__()

    def get_json_export(self):
        return {'flags': self.flags, 'uptime': self.uptime, 'tickets': self.tickets, 'beacons': self.beacons,
                'date': self.date.toordinal()}

    def set_flags(self, flags_score):
        self.flags = self.flags + flags_score
        self.save()

    def set_uptime(self, uptime_score):
        self.uptime = self.uptime + uptime_score
        self.save()

    def set_tickets(self, tickets_score):
        self.tickets = self.tickets + tickets_score
        self.save()

    def set_beacons(self, beacons_score):
        self.beacons = self.beacons + beacons_score
        self.save()


class Player(models.Model):
    """
    Scorebot v3: Player

    Basic Player representation class, can save data per player to save scores and track data.
    These players persist beyond games
    """

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'

    objects = PlayerManager()
    name = models.CharField('Player Display Name', max_length=150, unique=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    token = models.ForeignKey('scorebot_core.Token', on_delete=models.SET_NULL, blank=True, null=True)
    score = models.OneToOneField('scorebot_core.Score', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '[Player] %s <%d>' % (self.name, self.score.get_score())

    def __len__(self):
        return self.score.__len__()

    def __lt__(self, other):
        return isinstance(other, Player) and other.score > self.score

    def __gt__(self, other):
        return isinstance(other, Player) and other.score < self.score

    def __eq__(self, other):
        return isinstance(other, Player) and other.score == self.score

    def get_json_export(self):
        return {'name': self.name, 'score': self.score.get_json_export(), 'token': self.token.get_json_export()}

    def save(self, *args, **kwargs):
        if self.score is None:
            self.score = score_create_new()
        if self.token is None:
            self.token = token_create_new(90)
        super(Player, self).save(*args, **kwargs)


class Options(models.Model):
    """
    Scorebot v3: Options

    This object exists to have a basic 'defaults' for games, or presets.  These are shared between games if needed.
    The objects dictate the game settings, but may be null in the game.  If null a game takes the defaults from
    the scorebot constants file.
    """

    class Meta:
        verbose_name = 'Game Preset'
        verbose_name_plural = 'Game Presets'

    name = models.SlugField('Preset Name', max_length=150)
    round_time = models.PositiveSmallIntegerField('Round Time (seconds)', default=300)
    beacon_value = models.PositiveSmallIntegerField('Beacon Scoring Value', default=100)
    host_ping_ratio = models.PositiveSmallIntegerField('Default Host Ping Percent', default=50)
    beacon_time = models.PositiveSmallIntegerField('Default Beacon Timeout (seconds)', default=300)
    job_timeout = models.PositiveSmallIntegerField('Unfinished Job Timeout (seconds)', default=300)
    ticket_expire_time_modify = models.SmallIntegerField('Ticket Expire Modifiy (seconds)', default=0)
    flag_captured_multiplier = models.PositiveSmallIntegerField('Flag Captured Multiplier', default=300)
    ticket_severity_level_modify = models.SmallIntegerField('Ticket Severity Level Modifier', default=0)
    flag_start_percent = models.PositiveSmallIntegerField('Starting Flag Enabled Percentage', default=60)
    job_cleanup_time = models.PositiveSmallIntegerField('Finished Job Cleanup Time (seconds)', default=900)
    score_exchange_rate = models.PositiveIntegerField('Score to Coin Exchange Rate Percentage', default=100)
    ticket_start_percent = models.PositiveSmallIntegerField('Starting Ticket Enabled Percentage', default=65)
    ticket_start_wait = models.PositiveSmallIntegerField('Starting Ticket First Deploy Time (seconds)', default=180)

    def __str__(self):
        return '[Options] %s' % self.name

    def get_json_export(self):
        return {'name': self.name, 'round_time': self.round_time, 'beacon_value': self.beacon_value,
                'host_ping_ratio': self.host_ping_ratio, 'beacon_time': self.beacon_time,
                'ticket_expire_time_modify': self.ticket_expire_time_modify,
                'flag_captured_multiplier': self.flag_captured_multiplier,
                'ticket_severity_level_modify': self.ticket_severity_level_modify,
                'flag_start_percent': self.flag_start_percent, 'score_exchange_rate': self.score_exchange_rate,
                'ticket_start_percent': self.ticket_start_percent, 'ticket_start_wait': self.ticket_start_wait}


class Monitor(models.Model):
    """
    Scorebot v3: Monitor

    Monitors are the servers that run the checking algorithms on the Hosts.  Monitors require an access key with
    the '__SYS_MONITOR' bit set.
    """

    class Meta:
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitors'

    name = models.SlugField('Monitor Name', max_length=150)
    access = models.ForeignKey('scorebot_core.AccessToken', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '[Monitor] %s' % self.name

    def __bool__(self):
        return self.access.token.__bool__() if self.access is not None else False


class AccessToken(models.Model):
    """
    Scorebot v3: Access Token

    Gives granular access to the API backend and connectors.
    """

    class Meta:
        verbose_name = 'Access Token'
        verbose_name_plural = 'Access Tokens'

    level = models.BigIntegerField('Key Access Level', default=0)
    token = models.ForeignKey('scorebot_core.Token', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '[Access] %s <%d>' % ((self.token.uuid if self.token is not None else '(null)'), self.level)

    def save(self, *args, **kwargs):
        if self.token is None:
            self.token = token_create_new()
        super(AccessToken, self).save(*args, **kwargs)

    def __getitem__(self, access_level):
        if isinstance(access_level, int):
            access_object = access_level
        elif isinstance(access_level, str):
            if access_level in CONST_CORE_ACCESS_KEY_LEVELS:
                access_object = CONST_CORE_ACCESS_KEY_LEVELS[access_level]
            else:
                raise IndexError('The Access Level "%s" does not exist!' % access_level)
        else:
            raise TypeError('Parameter "access_level" must be a "integer" or "string" type!')
        if not self.token:
            return False
        return (self.level & (1 << access_object)) > 0

    def __setitem__(self, access_level, access_value):
        if isinstance(access_level, int):
            access_object = access_level
        elif isinstance(access_level, str):
            if access_level in CONST_CORE_ACCESS_KEY_LEVELS:
                access_object = CONST_CORE_ACCESS_KEY_LEVELS[access_level]
            else:
                raise IndexError('The Access Level "%s" does not exist!' % access_level)
        else:
            raise TypeError('Parameter "access_level" must be a "integer" or "string" type!')
        if bool(access_value):
            self.level = (self.level | (1 << access_object))
        else:
            self.level = (self.level & (~(1 << access_object)))
