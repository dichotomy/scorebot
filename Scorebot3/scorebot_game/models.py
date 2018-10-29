import json
import html
import uuid
import random

from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from scorebot.utils.events import post_tweet, get_scoreboard_message
from scorebot.utils import api_info, api_debug, api_error, api_warning, api_score, api_event
from scorebot_core.models import Team, score_create_new, token_create_new, team_create_new_color, Credit, Token
from scorebot.utils.constants import CONST_GAME_GAME_RUNNING, CONST_GAME_GAME_MODE_CHOICES, \
    CONST_GAME_GAME_STATUS_CHOICES, CONST_GAME_GAME_OPTIONS_DEFAULTS, CONST_GAME_EVENT_TYPE_CHOICES, \
    CONST_GRID_TICKET_CATEGORIES_CHOICES


def store_score_history(team, score):
    if team is None:
        raise ValueError('Parameter "team" cannot be None!')
    if score is None:
        raise ValueError('Parameter "score" cannot be None!')
    history = GameScore()
    history.team = team
    history.flags = score.flags
    history.uptime = score.uptime
    history.tickets = score.tickets
    history.beacons = score.beacons
    history.save()
    del history


def game_event_create(game, event_message):
    #event = GameEvent()
    #event.game = game
    #event.data = event_message
    #event.timeout = timezone.now() + timedelta(minutes=3)
    if game.start is not None:
        try:
            event_dist = (timezone.now() - game.start).seconds
            post_tweet('%s %s%dm: %s' % (game.name, event_dist // 3600, (event_dist % 3600) // 60, event_message))
            del event_dist
        except:
            pass
    #event.save()


# TODO: Expand this class with automated functions
class GameModel(models.Model):
    class Meta:
        abstract = True

    def finished(self):
        api_debug('BACKEND', 'The class "%s" is not using the "finished" method to delete itself!' % self.__name__)


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
        return 0 if self.finish is not None else ((timezone.now() - self.start).seconds - 1200)

    def __str__(self):
        return '[Job] %s <%s> (%s)' % (self.monitor.monitor.name, self.host.get_canonical_name(),
                                       ('DONE' if self.finish is not None else
                                        'WAIT %s' % self.__len__()))

    def __bool__(self):
        return self.finish is not None

    def finished(self):
        self.delete()

    def is_expired(self, score_time):
        expired = self.finish is None and \
                  self.__len__() > int(self.monitor.game.get_option('job_timeout'))
                  #(score_time - self.start).seconds > int(self.monitor.game.get_option('job_timeout'))
        if expired:
            api_debug('CLEANUP', 'Job "%d" has expired!' % self.id)
        return expired

    def can_cleanup(self, score_time):
        cleanup = self.finish is not None and \
                  ((score_time - self.finish).seconds -1200) > int(self.monitor.game.get_option('job_cleanup_time'))
        if cleanup:
            api_debug('CLEANUP', 'Job "%d" has passed the cleanup time!' % self.id)
        return cleanup


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
    mode = models.SmallIntegerField('Game Mode', default=0, choices=CONST_GAME_GAME_MODE_CHOICES)
    options = models.ForeignKey('scorebot_core.Options', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.PositiveSmallIntegerField('Game Status', default=0, choices=CONST_GAME_GAME_STATUS_CHOICES)

    def __str__(self):
        return '[Game] %s <%s|%d>' % (self.name, self.get_status_display(), self.teams.all().count())

    def finished(self):
        # TODO: Add hook to delete all Game Models and reset all Grid Models
        pass

    def get_json_scoreboard(self):
        game_json = {'name': html.escape(self.name),
                     'message': html.escape('This ProsVJoes CTF!'), #get_scoreboard_message(self.id)),
                     'mode': self.mode,
                     'teams': [t.get_json_scoreboard() for t in self.teams.all()],
                     'events': [e.get_json_scoreboard() for e in GameEvent.objects.filter(game=self)],
                     'credit': Credit.get_next_credit(),
                     }
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

    def round_score(self, score_time):
        api_debug('SCORING', 'Checking if Game "%s" can be scored..' % self.name)
        if self.scored is None or (score_time - self.scored).seconds > int(self.get_option('round_time')):
            api_info('SCORING', 'Starting round scoring on Game "%s"..' % self.name)
            for team in self.teams.all():
                api_debug('SCORING', 'Scoring Team "%s" assets..' % team.get_canonical_name())
                for host in team.hosts.all():
                    host.round_score()
                for flag in team.flags.filter(enabled=True):
                    flag.round_score()
                for beacon in team.compromises.filter(beacon__finish__isnull=True):
                    beacon.beacon.round_score()
                for ticket in team.tickets.all():
                    ticket.round_score(score_time)
            self.scored = score_time
            self.save()
            api_debug('SCORING', 'Scoring round on Game "%s" complete!' % self.name)

    def reporter_check(self, check_time):
        if self.start is None:
            return
        game_time = (check_time - self.start).seconds % 3600
        if game_time > 3590 or game_time < 10:
            scores = ['%s: %d' % (t.name, t.score.get_score()) for t in self.teams.filter(minimal=False)]
            post_tweet('%s %dm: Scores so far: %s' %
                       (self.name, ((check_time - self.start).seconds % 3600) // 60, ', '.join(scores)))
            del scores
        del game_time


class GameTeam(GameModel):
    class Meta:
        verbose_name = '[Game] Team'
        verbose_name_plural = '[Game] Teams'

    name = models.CharField('Team Name', max_length=150)
    subnet = models.CharField('Team Subnet', max_length=90)
    logo = models.ImageField('Team Logo', null=True, blank=True)
    dns = models.ManyToManyField('scorebot_grid.DNS', blank=True)
    offensive = models.BooleanField('Team is Offensive', default=False)
    minimal = models.BooleanField('Team Score is Hidden', default=False)
    color = models.IntegerField('Team Color', default=team_create_new_color)
    store = models.PositiveIntegerField('Team Store ID', null=True, blank=True, unique=True)
    game = models.ForeignKey('scorebot_game.Game', on_delete=models.CASCADE, related_name='teams')
    players = models.ManyToManyField('scorebot_core.Player', blank=True, related_name='game_teams')
    token = models.ForeignKey('scorebot_core.Token', on_delete=models.SET_NULL, blank=True, null=True)
    score = models.OneToOneField('scorebot_core.Score', on_delete=models.SET_NULL, blank=True, null=True)
    beacons = models.ManyToManyField('scorebot_core.Token', blank=True, editable=False, related_name='beacon_tokens')

    def __str__(self):
        return '[GameTeam] %s <%s>%s' % (self.get_canonical_name(), self.score.get_score(),
                                         ('OF' if self.offensive else ''))

    def finished(self):
        # TODO: Add function calls to delete objects under this team
        self.delete()

    def get_beacons(self):
        beacons = []
        for beacon in self.compromises.filter(beacon__finish__isnull=True):
            beacons.append({'team': beacon.beacon.attacker.id,
                            'color': '#%s' % hex(beacon.beacon.attacker.color).replace('0x', '').zfill(6)})
        return beacons

    def __lt__(self, other):
        return isinstance(other, Team) and other.score > self.score

    def __gt__(self, other):
        return isinstance(other, Team) and other.score < self.score

    def __eq__(self, other):
        return isinstance(other, Team) and other.score == self.score

    def get_json_mapper(self):
        return {"name": self.name, "token": str(self.token.uuid), "id": self.id}

    def get_canonical_name(self):
        if self.game is not None:
            return '%s\\%s' % (self.game.name, self.name)
        return self.name

    def get_json_scoreboard(self):
        team_json = {'id': self.id,
                     'name': html.escape(self.name),
                     'color': '#%s' % str(hex(self.color)).replace('0x', '').zfill(6),
                     'score': {
                         'total': self.score.get_score(),
                         'health': self.score.uptime,
                         'beacons': self.score.beacons,
                         'tickets': self.score.tickets,
                         'flags': self.score.flags,
                         },
                     'offense': self.offensive,
                     'flags': {
                         'open': self.flags.filter(enabled=True, captured__isnull=True).count(),
                         'lost': self.flags.filter(enabled=True, captured__isnull=False).count(),
                         'captured': self.attacker_flags.filter(enabled=True).count()
                         },
                     'tickets': {
                         'open': self.tickets.filter(closed=False).count(),
                         'closed': self.tickets.filter(closed=True).count()
                         },
                     'hosts': [h.get_json_scoreboard() for h in self.hosts.all()],
                     'logo': (self.logo.url if self.logo.__bool__() else 'default.png'),
                     'beacons': self.get_beacons(), 'minimal': self.minimal}
        return team_json

    def save(self, *args, **kwargs):
        if '/' not in self.subnet:
            self.subnet = '%s/24' % self.subnet
            api_warning('BACKEND', 'Team "%s" subnet is not in slash notation, setting to class /24!'
                        % self.get_canonical_name())
        if self.score is None:
            self.score = score_create_new()
        if self.token is None:
            self.token = token_create_new(90)
        super(GameTeam, self).save(*args, **kwargs)

    def set_flags(self, flags_score):
        self.score.set_flags(flags_score)
        store_score_history(self, self.score)

    def set_uptime(self, uptime_score):
        self.score.set_uptime(uptime_score)
        store_score_history(self, self.score)

    def set_tickets(self, tickets_score):
        self.score.set_tickets(tickets_score)
        store_score_history(self, self.score)

    def set_beacons(self, beacons_score):
        self.score.set_beacons(beacons_score)
        store_score_history(self, self.score)


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


# TODO: Do we add evenets for purchases?
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


class GameScore(GameModel):
    class Meta:
        verbose_name = '[Game] Score'
        get_latest_by = 'date'
        verbose_name_plural = '[Game] Scores'

    flags = models.IntegerField('Flags', default=0)
    uptime = models.IntegerField('Uptime', default=0)
    tickets = models.IntegerField('Tickets', default=0)
    beacons = models.IntegerField('Beacons', default=0)
    date = models.DateTimeField('Time', auto_now_add=True)
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.CASCADE)

    def __str__(self):
        return '[GameScore] <%s> F:%d U:%d T:%d B:%d @ %s' %\
               (self.team.get_canonical_name(), self.flags, self.uptime, self.tickets, self.beacons,
                self.date.strftime('%m/%d/%y;%H:%M.%S'))

    def __len__(self):
        return max(self.get_score(), 0)

    def __bool__(self):
        return self.__len__() > 0

    def get_score(self):
        return self.flags + self.uptime + self.tickets + self.beacons

    def __lt__(self, other):
        return isinstance(other, GameScore) and len(other) < self.__len__()

    def __gt__(self, other):
        return isinstance(other, GameScore) and len(other) > self.__len__()

    def __eq__(self, other):
        return isinstance(other, GameScore) and len(other) == self.__len__()


class GameEvent(GameModel):
    class Meta:
        verbose_name = '[Game] Event'
        verbose_name_plural = '[Game] Events'

    timeout = models.DateTimeField('Event Timeout')
    data = models.TextField('Event Data', null=True, blank=True)
    game = models.ForeignKey('scorebot_game.Game', on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField('Event Type', choices=CONST_GAME_EVENT_TYPE_CHOICES, default=0)

    def __str__(self):
        return '[GameEvent] %s' % self.game.name

    def get_json_scoreboard(self):
        try:
            event_data = json.loads(self.data)
        except json.decoder.JSONDecodeError:
            event_data = str(self.data)
        return {'type': self.type, 'data': event_data}

    def is_expired(self, expire_time):
        return (self.timeout - expire_time).seconds <= 0


class GameTicket(GameModel):
    class Meta:
        verbose_name = '[Game] Ticket'
        verbose_name_plural = '[Game] Tickets'

    ticket_id = models.PositiveIntegerField('Ticket ID')
    name = models.CharField('Ticket Name', max_length=150)
    closed = models.BooleanField('Ticket Closed', default=False)
    started = models.DateTimeField('Ticket Start', auto_now_add=True)
    total = models.PositiveIntegerField('Ticket Total Cost', default=0)
    description = models.TextField('Ticket Description', max_length=1000)
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.CASCADE, related_name='tickets')
    type = models.PositiveSmallIntegerField('Ticket Category', default=0, choices=CONST_GRID_TICKET_CATEGORIES_CHOICES)

    def __str__(self):
        return '[Game Ticket] %s <%s|%d> %s' % (self.get_canonical_name(), self.get_type_display(), self.total,
                                                ('Closed' if self.closed else 'Open'))

    def close_ticket(self):
        if self.closed:
            return
        self.closed = True
        if self.type == 1:
            self.team.set_tickets(self.total)
            api_debug('SCORING-ASYNC', 'Giving Team "%s" back "%d" points for closing a Ticket "%s"!'
                      % (self.team.get_canonical_name(), self.total, self.name))
            api_score(self.id, 'TICKET-CLOSE', self.team.get_canonical_name(), self.total)
        else:
            self.team.set_tickets(self.total/2)
            api_debug('SCORING-ASYNC', 'Giving Team "%s" back "%d" points for closing a Ticket "%s"!'
                     % (self.team.get_canonical_name(), self.total/2, self.name))
            api_score(self.id, 'TICKET-CLOSE', self.team.get_canonical_name(), self.total/2)
        api_info('SCORING-ASYNC', 'Team "%s" closed Ticket "%s" type "%s"!'
                 % (self.team.get_canonical_name(), self.name, self.get_type_display()))
        api_event(self.team.game, 'Team %s just closed a Ticket "%s"!' % (self.team.name, self.name))
        self.save()

    def reopen_ticket(self):
        if not self.closed:
            return
        self.closed = False
        reopen_cost = float(float(self.team.game.get_option('ticket_reopen_multiplier'))/100)
        score_value = -1 * (reopen_cost * self.total)
        self.team.set_tickets(score_value)
        api_score(self.id, 'TICKET-REOPEN', self.team.get_canonical_name(), score_value)
        api_info('SCORING-ASYNC', 'Team "%s" had the Ticket "%s" reopened, negating "%d" points!'
                 % (self.team.get_canonical_name(), self.name, score_value))
        del score_value
        api_event(self.team.game, 'Ticket "%s" for %s was reopened!' % (self.name, self.team.name))
        self.save()

    def get_canonical_name(self):
        if self.team is not None:
            return '%s\\%s' % (self.team.get_canonical_name(), self.name)
        return self.name

    def can_score(self, score_time):
        if self.closed:
            return False
        open_time = (score_time - self.started).seconds
        if open_time >= int(self.team.game.get_option('ticket_max_scoring')):
            return False
        if open_time > int(self.team.game.get_option('ticket_grace_period')):
            return True
        return False

    def round_score(self, score_time):
        if self.can_score(score_time):
            api_debug('SCORING', 'Scoring Tickect "%s"..' % self.get_canonical_name())
            if self.total < int(self.team.game.get_option('ticket_max_score')):
                ticket_score = int(self.team.game.get_option('ticket_cost'))
                self.total = self.total + ticket_score
                self.team.set_tickets(-1 * ticket_score)
                api_score(self.id, 'TICKET', self.team.get_canonical_name(), -1 * ticket_score)
                api_info('SCORING', 'Team "%s" lost "%d" points to open Ticket "%s"!'
                          % (self.team.get_canonical_name(), ticket_score, self.name))
                self.save()

    @staticmethod
    def grab_ticket_json(request, json_data):
        if 'id' not in json_data or 'name' not in json_data or 'details' not in json_data or \
                        'type' not in json_data or 'status' not in json_data or 'team' not in json_data:
            api_error('TICKET', 'Attempted to create a Ticket without the proper values!', request)
            return None, 'Invalid JSON Data!'
        api_debug('TICKET', 'Attempting to grab a Ticket from JSON data!', request)
        ticket = None
        ticket_exists = False
        try:
            ticket = GameTicket.objects.get(ticket_id=int(json_data['id']))
            ticket_exists = True
        except ValueError:
            api_error('TICKET', 'Attempted to use an invalid ticket ID!', request)
            return None, 'Invalid Ticket ID!'
        except GameTicket.DoesNotExist:
            ticket = GameTicket()
            ticket.ticket_id = int(json_data['id'])
            api_info('TICKET', 'Created a new Ticket with ID "%d"!' % ticket.ticket_id, request)
        except GameTicket.MultipleObjectsReturned:
            api_error('TICKET', 'Multiple Tickets were returned with ID "%s", invalid!' % json_data['id'], request)
            return None, 'Invalid Ticket ID!'
        if not ticket_exists:
            try:
                team_token = Token.objects.get(uuid=uuid.UUID(json_data['team']))
                ticket.team = GameTeam.objects.get(token=team_token)
                del team_token
            except ValueError:
                api_error('TICKET', 'Token given for Team is invalid!', request)
                return None, 'Invalid Team Token!'
            except Token.DoesNotExist:
                api_error('TICKET', 'Token given for Team is invalid!', request)
                return None, 'Invalid Team Token!'
            except GameTeam.DoesNotExist:
                api_error('TICKET', 'Team given does not exist!', request)
                return None, 'Team does not exist!'
        else:
            api_info('TICKET', 'Updating a Ticket with ID "%d"!' % ticket.ticket_id, request)
        ticket.name = json_data['name']
        ticket.description = json_data['details']
        ticket_type = json_data['type'].lower()
        for type in CONST_GRID_TICKET_CATEGORIES_CHOICES:
            if type[1].lower() == ticket_type:
                ticket.type = type[0]
                break
        del ticket_type
        if json_data['status'].lower() == 'closed':
            if ticket_exists and not ticket.closed:
                ticket.close_ticket()
            elif not ticket_exists:
                ticket.closed = True
        else:
            if ticket_exists and ticket.closed:
                ticket.reopen_ticket()
        del json_data
        del ticket_exists
        ticket.save()
        return ticket, None


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

    def create_job(self):
        if self.game.status == CONST_GAME_GAME_RUNNING:
            teams = self.game.teams.all()
            teams_max = len(teams)
            for team_round in range(0, teams_max):
                team = random.choice(teams)
                api_debug('JOB', 'Monitor "%s" selected team "%s"!' % (self.monitor.name, team.name))
                hosts = team.hosts.filter(scored__isnull=True)
                api_debug('JOB', 'Team "%s" has "%d" hosts to pick from!' % (team.name, len(hosts)))
                for host_round in range(0, len(hosts)):
                    api_debug('JOB', 'Monitor "%s" start host selection round %d.' % (self.monitor.name, host_round))
                    host = random.choice(hosts)
                    api_debug('JOB', 'Monitor "%s" attempting to select host "%s".' % (self.monitor.name, host.fqdn))
                    if host.jobs.filter(finish__isnull=True).count() > 0:
                        api_debug('JOB', 'Host "%s" has currently open Jobs, moving on.' % host.fqdn)
                        del host
                        continue
                    if self.selected_hosts.all().count() > 0:
                        api_debug('JOB', 'Monitor "%s" has host selection rules in place. Type %s' %
                                     (self.monitor.name, ('Include' if self.only else 'Exclude')))
                        host_rules = self.selected_hosts.filter(id=host.id).count()
                        if host_rules == 0 and self.only:
                            api_debug('JOB', 'Monitor "%s" host selection rules denied host "%s".' %
                                      (self.monitor.name, host.fqdn))
                            del host
                            del host_rules
                            continue
                        if host_rules != 0 and not self.only:
                            api_debug('JOB', 'Monitor "%s" host selection rules denied host "%s".' %
                                      (self.monitor.name, host.fqdn))
                            del host
                            del host_rules
                            continue
                        del host_rules
                    api_debug('JOB', 'Monitor "%s" selected host "%s".' % (self.monitor.name, host.fqdn))
                    job = Job()
                    job.monitor = self
                    job.host = host
                    job.host.scored = timezone.now()
                    job.host.save()
                    job.save()
                    api_info('JOB', 'Gave Monitor "%s" Job "%d" for Host "%s".'
                             % (self.monitor.name, job.id, host.fqdn))
                    del team
                    del hosts
                    del teams
                    del teams_max
                    job_json = host.get_json_job()
                    del host
                    job_json['id'] = job.id
                    del job
                    job_json_raw = json.dumps(job_json)
                    del job_json
                    return job_json_raw
                del team
                del hosts
            del teams
            del teams_max
            api_debug('JOB', 'Monitor "%s" could not select any hosts, telling Monitor to wait.' % self.monitor.name)
        return None

    def score_job(self, monitor, job, job_data):
        if self.monitor.id != monitor.id:
            api_error('JOB', 'Monitor "%s" returned a Job created by Monitor "%s"!' % (monitor.name, job.monitor.name))
            return False, 'Job was submitted by a different monitor!'
        api_info('JOB', 'Processing Job "%d" send by Monitor "%s".' % (job.id, monitor.name))
        if self.game.status != CONST_GAME_GAME_RUNNING:
            api_error('JOB', 'Job Game "%s" submitted by Monitor "%s" is not Running!' % (self.game, job.monitor.name))
            return False, 'Game is not running!'
        try:
            job.host.score_job(job, job_data['host'])
        except KeyError:
            api_error('JOB', 'Job submitted by Monitor "%s" is not in a correct JSON format!' % self.monitor.name)
            return False, 'Not in a valid JSON format!'
        api_debug('JOB', 'Job "%d" processing finished!' % job.id)
        job.finish = timezone.now()
        job.save()
        return True, None


class GameCompromise(GameModel):
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
    token = models.ForeignKey('scorebot_core.Token', null=True, blank=True, editable=False, on_delete=models.SET_NULL)
    checkin = models.DateTimeField('Beacon Checkedin', null=True, blank=True, editable=False)
    attacker = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.CASCADE, related_name='attack_beacons')

    def __len__(self):
        return (self.finish - self.start).seconds if self.finish is not None else ((timezone.now() - self.start).seconds - 1200)

    def __str__(self):
        return '[Beacon] %s -> %s (%d seconds)' % (self.attacker.name, self.host.get_fqdn(), self.__len__())

    def __bool__(self):
        return self.finish is None

    def finished(self):
        self.delete()

    def round_score(self):
        if self.__bool__():
            api_debug('SCORING', 'Beacon "%d" by "%s" is still on Host "%s"!'
                      % (self.id, self.attacker.get_canonical_name(), self.host.get_fqdn()))
            beacon_value = -1 * int(self.host.team.game.get_option('beacon_value'))
            api_score(self.id, 'BEACON', self.host.team.get_canonical_name(), beacon_value,
                      self.attacker.get_canonical_name())
            self.host.team.set_beacons(beacon_value)
            del beacon_value

    def is_expired(self, now):
        return self.__len__() > int(self.host.team.game.get_option('beacon_time'))
#        if self.checkin is None:
#            return (now - self.start).seconds > int(self.host.team.game.get_option('beacon_time'))
#        return (now - self.checkin).seconds > int(self.host.team.game.get_option('beacon_time'))


class GameCompromiseHost(GameModel):
    class Meta:
        verbose_name = 'Beacon Host'
        verbose_name_plural = 'Beacon Hosts'

    ip = models.GenericIPAddressField('Host Address', protocol='both', unpack_ipv4=True, null=True)
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.CASCADE, related_name='compromises')
    beacon = models.OneToOneField('scorebot_game.GameCompromise', on_delete=models.CASCADE, related_name='host')
    host = models.ForeignKey('scorebot_grid.Host', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='beacons')

    def __str__(self):
        return '[Beacon Host] %s (%s)' % (self.get_fqdn(), self.team.name)

    def finished(self):
        self.delete()

    def get_fqdn(self):
        return self.host.fqdn if self.host is not None else self.ip


