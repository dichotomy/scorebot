import json
import html
import random

from django.db import models
from scorebot.utils import logger
from django.utils import timezone
from scorebot.utils.constants import *
from django.contrib.auth.models import User
from scorebot_core.models import Team, score_create_new, token_create_new, team_create_new_color


class GameTeamManager(models.Manager):
    def create_from_team(self, team_game, team, team_offensive=False):
        if team is None:
            return ValueError('Parameter "team" cannot be None!')
        if team_game is None:
            return ValueError('Parameter "team_game" cannot be None!')
        if isinstance(team, Team):
            if isinstance(team_game, Game):
                team_object = Team()
                team_object.name = team.name
                team_object.game = team_game
                team_object.offensive = team_offensive
                team_object.color = team.color
                team_object.logo = team.logo
                team_object.save()
                for player in team.players.all():
                    team_object.players.add(player)
                team_object.save()
                return team_object
            else:
                return ValueError('Parameter "team_game" must be a "Game" object type!')
        else:
            return ValueError('Parameter "team" must be a "Team" object type!')


# TODO: Expand this class with automated functions
class GameModel(models.Model):
    class Meta:
        abstract = True

    def finished(self):
        pass


class Job(GameModel):
    """
    Scorebot v3: Job

    One of the core socreing processes in Scorebot.  This model stores the checking on a host and services on the
    targeted host
    """

    class Meta:
        verbose_name = 'Monitor Job'
        verbose_name_plural = 'Monitor Jobs'

    start = models.DateTimeField('Job Start', auto_now_add=True)
    finish = models.DateTimeField('Job Finish', null=True, blank=True)
    monitor = models.ForeignKey('scorebot_game.GameMonitor', on_delete=models.CASCADE)
    host = models.ForeignKey('scorebot_grid.Host', on_delete=models.CASCADE, related_name='jobs')

    def __len__(self):
        if self.finish is not None:
            return 0
        return (timezone.now() - self.host).seconds

    def __str__(self):
        return '[Job] %s <%s> (%s)' % (self.monitor.monitor.name, self.host.get_canonical_name(),
                                       ('DONE' if self.finish is not None else
                                        'WAIT %s' % (timezone.now() - self.start).seconds))

    def __bool__(self):
        return self.finish is not None

    def finished(self):
        self.delete()

    def get_finish_time(self):
        if self.finish is None:
            return self.__len__()
        return (timezone.now() - self.finish).seconds


# TODO: Work on history on game finish hook
class Game(GameModel):
    """
    Scorebot v3: Game

    Stores all the Game related data, basically is the Game.
    """

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

    name = models.CharField('Game Name', max_length=150)
    start = models.DateTimeField('Game Start Time', null=True, blank=True)
    finish = models.DateTimeField('Game Finish Time', blank=True, null=True)
    ports = models.ManyToManyField('scorebot_game.GamePort', blank=True, editable=False)
    scored = models.DateTimeField('Game Last Scored', blank=True, null=True, editable=False)
    message = models.CharField('Game Scoreboard Message', max_length=150, null=True, blank=True)
    mode = models.SmallIntegerField('Game Mode', default=0, choices=CONST_GAME_GAME_MODE_CHOICES)
    options = models.ForeignKey('scorebot_core.Options', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.PositiveSmallIntegerField('Game Status', default=0, choices=CONST_GAME_GAME_STATUS_CHOICES)

    def __str__(self):
        return '[Game] %s <%s|%d>' % (self.name, self.get_status_display(), self.teams.all().count())

    def get_message(self):
        if self.status == 1:
            return self.message if self.message is not None else CONST_GAME_GAME_MESSAGE
        return '[%s] %s' % (self.get_status_display(),
                            self.message if self.message is not None else CONST_GAME_GAME_MESSAGE)

    def round_score(self, now):
        if self.scored is None:
            self.scored = now
            self.save()
        if (now - self.scored).seconds > int(self.get_option('round_time')):
            logger.info('SBE-SCORING', 'Starting round based scoring on Game "%s".' % self.name)
            for team in self.teams.all():
                for host in team.hosts.all():
                    host.round_score()
            self.scored = now
            self.save()

    def get_json_scoreboard(self):
        game_json = {'name': html.escape(self.name), 'message': html.escape(self.get_message()), 'mode': self.mode,
                     'teams': [t.get_json_scoreboard() for t in self.teams.all()]}
        game_json_data = json.dumps(game_json)
        del game_json
        return game_json_data

    def get_option(self, option_name):
        if self.options is None:
            try:
                return CONST_GAME_GAME_OPTIONS_DEFAULTS[option_name]
            except KeyError:
                return None
        try:
            return getattr(self.options, option_name)
        except AttributeError:
            return None


# TODO: Work on history on game finish hook
class GameTeam(GameModel):
    class Meta:
        verbose_name = '[Game] Team'
        verbose_name_plural = '[Game] Teams'

    objects = GameTeamManager()
    name = models.CharField('Team Name', max_length=150)
    dns = models.ManyToManyField('scorebot_grid.DNS', blank=True)
    offensive = models.BooleanField('Team is Offensive', default=False)
    color = models.IntegerField('Team Color', default=team_create_new_color)
    store_id = models.PositiveIntegerField('Team Store ID', null=True, blank=True, unique=True)
    game = models.ForeignKey('scorebot_game.Game', on_delete=models.CASCADE, related_name='teams')
    players = models.ManyToManyField('scorebot_core.Player', blank=True, related_name='game_teams')
    token = models.ForeignKey('scorebot_core.Token', on_delete=models.SET_NULL, blank=True, null=True)
    logo = models.ImageField('Team Logo', upload_to=CONST_GAME_GAME_TEAM_LOGO_DIR, null=True, blank=True)
    score = models.OneToOneField('scorebot_core.Score', on_delete=models.SET_NULL, blank=True, null=True)
    beacons = models.ManyToManyField('scorebot_core.Token', blank=True, editable=False, related_name='beacon_tokens')
    mail_server = models.GenericIPAddressField('SMTP Server', protocol='both', unpack_ipv4=True, null=True, blank=True)

    def __str__(self):
        return '[GameTeam] %s <%s>%s' % (self.name, self.score, ('OF' if self.offensive else ''))

    def __len__(self):
        return self.score.__len__()

    def finished(self):
        pass #self.delete()

    def __lt__(self, other):
        return isinstance(other, Team) and other.score > self.score

    def __gt__(self, other):
        return isinstance(other, Team) and other.score < self.score

    def __eq__(self, other):
        return isinstance(other, Team) and other.score == self.score

    def get_beacon_count(self):
        beacons = 0
        for host in self.hosts.all():
            beacons = beacons + host.beacons.filter(finish__isnull=True).count()
        return beacons

    def get_canonical_name(self):
        if self.game is not None:
            return '%s\\%s' % (self.game.name, self.name)
        return self.name

    def get_json_scoreboard(self):
        team_json = {'id': self.id, 'name': html.escape(self.name),
                     'color': '#%s' % str(hex(self.color)).replace('0x', ''),
                     'score': {'total': self.score.__len__(), 'health': self.score.uptime}, 'offense': self.offensive,
                     'flags': {'open': self.flags.filter(enabled=True, captured__isnull=True).count(),
                               'lost': self.flags.filter(enabled=True, captured__isnull=False).count(),
                               'captured': self.attacker_flags.filter(enabled=True).count()},
                     'tickets': {'open': self.tickets.filter(completed__isnull=True, started__isnull=False).count(),
                                 'closed': self.tickets.filter(completed__isnull=False, started__isnull=False,
                                                               expired=False).count()},
                     'hosts': [h.get_json_scoreboard() for h in self.hosts.all()], 'beacons': self.get_beacon_count(),
                     'logo': (self.logo.url if self.logo.__bool__() else 'default.png'),
                     'compromises': self.attacker_beacons.all().count()}
        return team_json

    def save(self, *args, **kwargs):
        if self.score is None:
            self.score = score_create_new()
        if self.token is None:
            self.token = token_create_new(90)
        super(GameTeam, self).save(*args, **kwargs)


class GamePort(GameModel):
    class Meta:
        verbose_name = '[Game] Beacon Port'
        verbose_name_plural = '[Game] Beacon Ports'

    port = models.PositiveSmallIntegerField('Port Number')

    def __str__(self):
        return '[GamePort] %d' % self.port

    def get_port(self):
        return GamePort._convert_port_number(self.port)

    def finished(self):
        self.delete()

    @staticmethod
    def _convert_port_number(port_number, direction=True):
        if direction is False:
            return port_number - 65534
        if port_number < 0:
            return 65534 - port_number
        return port_number


class Purchase(GameModel):
    """
    Scorebot v3: Purchase

    This model repersents the transaction history of the teams in the new economy update.
    Each Purchase will be tracked here.
    """

    class Meta:
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'

    item = models.CharField('Purchase Item', max_length=150)
    amount = models.PositiveSmallIntegerField('Purchase Amount')
    date = models.DateTimeField('Purchase Date', auto_now_add=True)
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.CASCADE, related_name='purchases')

    def __len__(self):
        return self.amount

    def __str__(self):
        return '[Purchase] <%s|%d> -> %s' % (self.item, self.amount, self.team.get_canonical_name())

    def finished(self):
        self.delete()


class Compromise(GameModel):
    """
    Scorebot v3: Compromise

    Stores the status of a system when an offensive team has RCE on an opposing team's system.

    Also called a Beacon
    """

    class Meta:
        verbose_name = 'Beacon'
        verbose_name_plural = 'Beacons'

    finish = models.DateTimeField('Beacon Completed', null=True, blank=True)
    start = models.DateTimeField('Beacon Start', auto_now_add=True, editable=False)
    token = models.ForeignKey('scorebot_core.Token', null=True, blank=True, editable=False)
    checkin = models.DateTimeField('Beacon Checkedin', null=True, blank=True, editable=False)
    host = models.ForeignKey('scorebot_grid.Host', on_delete=models.CASCADE, related_name='beacons')
    attacker = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.CASCADE, related_name='attacker_beacons')

    def __len__(self):
        if self.finish:
            return (self.finish - self.start).seconds
        return (timezone.now() - self.start).seconds

    def __str__(self):
        return '[Beacon] %s -> %s (%d seconds)' % (self.attacker.name, self.host.fqdn, self.__len__())

    def __bool__(self):
        return self.finish is None

    def round_score(self):
        if self.__bool__():
            self.host.team.score.set_beacons(-1 * self.host.team.game.get_option('beacon_value'))


class GameMonitor(GameModel):
    """
    Scorebot v3: GameMonitor

    This is a Django through class that specifies the additional attributes needed by a Monitor to do its job.
    """

    class Meta:
        verbose_name = '[Game] Monitor'
        verbose_name_plural = '[Game] Monitors'

    only = models.BooleanField('Monitor Only List', default=True)
    game = models.ForeignKey('scorebot_game.Game', on_delete=models.CASCADE)
    monitor = models.ForeignKey('scorebot_core.Monitor', on_delete=models.CASCADE)
    selected_hosts = models.ManyToManyField('scorebot_grid.Host', related_name='monitor', blank=True)

    def __str__(self):
        return '%s <%s:%d>' % (self.monitor.__str__(), ('I' if self.only else 'E'), self.selected_hosts.all().count())

    def get_job(self):
        if self.game.status == 1:
            team = random.choice(self.game.teams.all())
            logger.debug('SBE-JOB', 'Monitor "%s" selected team "%s".' % (self.monitor.name, team.name))
            hosts = team.hosts.filter(scored__isnull=True)
            logger.debug('SBE-JOB', 'Team "%s" has "%d" hosts to pick from.' % (team.name, len(hosts)))
            for host_round in range(0, len(hosts)):
                logger.debug('SBE-JOB', 'Monitor "%s" start host selection round %d.' % (self.monitor.name, host_round))
                host = random.choice(hosts)
                logger.debug('SBE-JOB', 'Monitor "%s" attempting to select host "%s".' % (self.monitor.name, host.fqdn))
                if host.scored is not None:
                    logger.debug('SBE-JOB', 'Host "%s" has already been scored this round, moving on.' % host.fqdn)
                    continue
                if host.jobs.filter(finish__isnull=True).count() > 0:
                    logger.debug('SBE-JOB', 'Host "%s" has currently open Jobs, moving on.' % host.fqdn)
                    continue
                if self.selected_hosts.all().count() > 0:
                    logger.debug('SBE-JOB', 'Monitor "%s" has host selection rules in place. Type %s' %
                                 (self.monitor.name, ('Include' if self.only else 'Exclude')))
                    host_rules = self.selected_hosts.filter(id=host.id).count()
                    if host_rules == 0 and self.only:
                        logger.debug('SBE-JOB', 'Monitor "%s" host selection rules denied host "%s".' %
                                     (self.monitor.name, host.fqdn))
                        continue
                    if host_rules != 0 and not self.only:
                        logger.debug('SBE-JOB', 'Monitor "%s" host selection rules denied host "%s".' %
                                     (self.monitor.name, host.fqdn))
                        continue
                logger.info('SBE-JOB', 'Monitor "%s" selected host "%s".' % (self.monitor.name, host.fqdn))
                job = Job()
                job.monitor = self
                job.host = host
                job.host.scored = timezone.now()
                job.host.save()
                job.save()
                logger.info('SBE-JOB', 'Gave Monitor "%s" Job "%d" for Host "%s".' % (self.monitor.name, job.id,
                                                                                      host.fqdn))
                del team
                del hosts
                job_json_dict = host.get_json_job()
                job_json_dict['id'] = job.id
                del job
                job_json = json.dumps(job_json_dict)
                del job_json_dict
                return job_json
        return None

    def update_job(self, monitor, job, job_data):
        if self.monitor.id != monitor.id:
            logger.warning('SBE-JOB', 'Monitor "%s" returned a Job created by Monitor "%s"!' %
                           (monitor.name, job.monitor.name))
            return False, 'Job was submitted by a different monitor!'
        logger.info('SBE-JOB', 'Processing Job "%d" send by Monitor "%s".' % (job.id, monitor.name))
        job.host.score_job(job, job_data['host'])
        logger.info('SBE-JOB', 'Job "%d" processing finished!' % job.id)
        job.finish = timezone.now()
        job.save()
        return True, None
