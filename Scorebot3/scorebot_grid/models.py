import json
import math
import html

from django.db import models
from datetime import timedelta
from django.utils import timezone
from scorebot.utils import logger
from scorebot.utils.constants import *
from scorebot_game.models import GameTeam
from django.core.exceptions import ValidationError


# TODO: Expand this class with automated functions
class GridModel(models.Model):
    """
    Scorebot v3: GridModel

    Provides a baseline for models to be 'tagged' as GridModels.
    GridModels are 'reset' after a game to default settings, such as status and options.  This keeps the game
    environment clean and eliminates the need to manually 'reset' data in the database.
    """
    class Meta:
        abstract = True

    def reset(self):
        pass

    def on_start(self):
        pass

    def on_finish(self):
        pass

    def get_canonical_name(self):
        return self.__class__.__name__


class DNS(GridModel):
    """
    Scorebot v3: DNS

    Simple string array placeholder for multi DNS instances
    """

    class Meta:
        verbose_name = 'DNS Server'
        verbose_name_plural = 'DNS Servers'

    address = models.GenericIPAddressField('DNS Server', protocol='both', unpack_ipv4=True)

    def __str__(self):
        return '[DNS] %s' % str(self.address)

    def get_json_export(self):
        return {'dns': str(self.address)}


class Flag(GridModel):
    """
    Scorebot v3: Flag

    Contains data for keeping track of Flags and flag based data
    """

    class Meta:
        verbose_name = 'Flag'
        verbose_name_plural = 'Flags'

    name = models.SlugField('Flag Name', max_length=150)
    flag = models.CharField('Flag Data Value', max_length=120)
    enabled = models.BooleanField('Flag Enabled', default=True)
    description = models.TextField('Flag Description', max_length=500)
    value = models.PositiveSmallIntegerField('Flag Value', default=CONST_GRID_FLAG_VALUE)
    host = models.ForeignKey('scorebot_grid.Host', on_delete=models.CASCADE, related_name='flags')
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='flags')
    captured = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.SET_NULL, null=True, blank=True,
                                 editable=False, related_name='attacker_flags')

    def reset(self):
        self.captured = None
        self.save()

    def __str__(self):
        return '[Flag] %s <%s|%d>' % (self.get_canonical_name(), self.name, self.value)

    def __bool__(self):
        return self.captured is None

    def round_score(self):
        if self.__bool__() and self.enabled:
            self.team.score.set_flags(self.value)

    def get_json_export(self):
        return {'name': self.name, 'flag': self.flag, 'enabled': self.enabled, 'description': self.description,
                'value': self.value, 'captured': (self.captured.id if self.captured is not None else None),
                'team': (self.team.id if self.team is not None else None)}

    def capture(self, attacker):
        if attacker is None:
            raise ValueError('Parameter "attacker" cannot be None!')
        if isinstance(attacker, GameTeam):
            self.captured = attacker
            multiplier = self.team.game.get_option('flag_captured_multiplier')
            self.team.score.set_flags(-1 * self.value * multiplier)
            attacker.score.set_flags(self.value * multiplier)
            del multiplier
            self.save()
        else:
            raise ValueError('Parameter "attacker" must be a "GameTeam" object type!')

    def get_canonical_name(self):
        if self.team is not None:
            return '%s\\%s' % (self.team.get_canonical_name(), self.name)
        return self.name

    def save(self, *args, **kwargs):
        if self.team is not None:
            try:
                flags_find = self.team.flags.all().get(flag=self.flag)
                if flags_find.id != self.id:
                    raise ValidationError({'flag': 'Flags on a Team cannot have the same flag value! %s-%s' % (self.name, flags_find.name)})
                del flags_find
            except Flag.DoesNotExist:
                pass
            except Flag.MultipleObjectsReturned:
                raise ValidationError({'flag': 'Flags on a Team cannot have the same flag value!'})
        super(Flag, self).save(*args, **kwargs)


class Host(GridModel):
    """
    Scorebot v3: Host

    Represents a Hosts used in a game
    """

    class Meta:
        verbose_name = 'Host'
        verbose_name_plural = 'Hosts'

    fqdn = models.CharField('Host Full Domain Name', max_length=150)
    online = models.BooleanField('Host Online', default=False, editable=False)
    name = models.SlugField('Host Display Name', max_length=150, null=True, blank=True)
    ping_min = models.PositiveSmallIntegerField('Host Minimum Pingback Percentage', default=0)
    scored = models.DateTimeField('Host has been Scored', null=True, blank=True, editable=False)
    ip = models.GenericIPAddressField('Host Address', protocol='both', unpack_ipv4=True, null=True)
    ping_last = models.PositiveSmallIntegerField('Host Last Pingback Percentage', default=0, editable=False)
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='hosts')
    server = models.ForeignKey('scorebot_grid.Hypervisor', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='guests')

    def reset(self):
        self.online = False
        self.ping_last = 0
        for service in self.services.all():
            service.reset()
        for flag in self.flags.all():
            flag.reset()
        for beacon in self.beacons.all():
            beacon.delete()
        self.save()

    def __str__(self):
        return '[Host] %s <%s> %s' % (self.get_canonical_name(), self.fqdn, ('UP' if self.online else 'DOWN'))

    def __bool__(self):
        return self.get_beacon_count() > 0

    def get_score(self):
        if not self.online:
            return 0
        host_score = 0
        for service in self.services.all():
            host_score = host_score + service.get_score()
        return host_score

    def round_score(self):
        self.scored = None
        for beacon in self.beacons.filter(finish__isnull=True):
            beacon.round_score()
        for flag in self.flags.filter(captured__isnull=True, enabled=True):
            flag.round_score()
        self.save()

    def get_json_job(self):
        if self.team is None:
            return None
        return {'host': {'fqdn': self.fqdn, 'services': [s.get_json_job() for s in self.services.all()]},
                'dns': [str(dns.address) for dns in self.team.dns.all()],
                'timeout': self.team.game.get_option('round_time')}

    def get_json_export(self):
        return {'name': self.name}

    def get_beacon_count(self):
        return self.beacons.all().filter(finish__isnull=True).count()

    def get_canonical_name(self):
        if self.team is not None:
            return '%s\\%s' % (self.team.get_canonical_name(), self.name)
        return self.name

    def get_json_scoreboard(self):
        if self.team is None:
            return None
        host_json = {'name': html.escape(self.name), 'id': self.id, 'online': self.online,
                     'services': [s.get_json_scoreboard() for s in self.services.all()]}
        return host_json

    def save(self, *args, **kwargs):
        if self.team is not None:
            if self.ip is not None:
                try:
                    host_find = self.team.hosts.all().get(ip=self.ip)
                    if host_find.id != self.id:
                        raise ValidationError({'ip': 'Hosts on a Team cannot have the same IP address!'})
                    del host_find
                except Host.DoesNotExist:
                    pass
                except Host.MultipleObjectsReturned:
                    raise ValidationError({'ip': 'Hosts on a Team cannot have the same IP address!'})
            else:
                logger.warning('SBE-GENERAL',
                               'Host "%s" has a null value IP address and will not receive beacon scoring!' % self.fqdn)
        if self.name is None or len(self.name) == 0:
            if '.' in self.fqdn:
                self.name = self.fqdn.split('.')[0]
            else:
                self.name = self.fqdn
        super(Host, self).save(*args, **kwargs)

    def score_job(self, job, job_data):
        if self.ping_min == 0:
            ping_ratio = int(self.team.game.get_option('host_ping_ratio'))
        else:
            ping_ratio = self.ping_min
        if 'ping_sent' not in job_data or 'ping_respond' not in job_data:
            logger.warning('SBE-JOB', 'Invalid Host "%s" JSON data by Job "%d"!' % (self.fqdn, job.id))
            return
        try:
            ping_sent = int(job_data['ping_sent'])
            ping_respond = int(job_data['ping_respond'])
            try:
                self.ping_last = math.floor((float(ping_respond) / float(ping_sent)) * 100)
                self.online = (self.ping_last >= ping_ratio)
            except ZeroDivisionError:
                self.online = False
                self.ping_last = 0
            logger.debug('SBE-JOB', 'Host "%s" was set "%s" by Job "%d".' % (self.fqdn,
                                                                             ('Online' if self.online else 'Offline'),
                                                                             job.id))
            self.save()
        except ValueError:
            logger.warning('SBE-JOB', 'Error translating ping responses from Job "%d"!' % job.id)
            self.online = False
            self.ping_last = 0
            self.save()
        if 'services' not in job_data and self.online:
            logger.warning('SBE-JOB', 'Host "%s" was set online by Job "%d" but is missing services!'
                           % (self.fqdn, job.id))
            return
        for service in self.services.all():
            if not self.online:
                service.status = 2
                service.save()
            else:
                for job_service in job_data['services']:
                    try:
                        if service.port == int(job_service['port']) and \
                                        service.get_protocol_display().lower() == job_service['protocol'].lower():
                            service.score_job(job, job_service)
                            break
                    except ValueError:
                        pass
        self.team.score.set_uptime(self.get_score())
        logger.info('SBE-JOB', 'Finished scoring Host "%s" by Job "%d".' % (self.fqdn, job.id))


class Ticket(GridModel):
    """
    Scorebot v3: GameTicket

    Stores the data related to tickets assigned to teams in a game. Tickets can be included and excluded from a game.
    This is based on the option (ticket_start_percent) which chooses a random percentage of tickets to be enabled.
    Tickets, once assigned, will be checked by the SBE daemon for expire time.

    Also referred to as an Inject
    """

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    name = models.SlugField('Ticket Name', max_length=150)
    expired = models.BooleanField('Ticket Expired', default=False)
    description = models.TextField('Ticket Description', max_length=1000)
    started = models.DateTimeField('Ticket Assigned', blank=True, null=True)
    completed = models.DateTimeField('Ticket Completed', blank=True, null=True)
    reopen_count = models.PositiveSmallIntegerField('Ticket Reopen Count', default=0)
    ticket_id = models.PositiveIntegerField('Ticket System ID', null=True, blank=True)
    value = models.SmallIntegerField('Ticket Value', default=CONST_GRID_TICKET_VALUE_DEFAULT)
    expires_date = models.DateTimeField('Ticket Expires DateTime', editable=False, null=True)
    expires = models.PositiveSmallIntegerField('Ticket Expires (seconds)',
                                               default=CONST_GRID_TICKET_EXPIRE_TIME_DEFAULT)
    team = models.ForeignKey('scorebot_game.GameTeam', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='tickets')
    category = models.PositiveSmallIntegerField('Ticket Category', default=CONST_GRID_TICKET_CATEGORY_DEFAULT,
                                                choices=CONST_GRID_TICKET_CATEGORY_CHOICES)

    def reset(self):
        self.started = None
        self.expired = False
        self.completed = None
        self.expires_date = None
        self.reopen_count = 0
        self.save()

    def __str__(self):
        return '[Ticket] %s <%s|%d> %s' % (self.get_canonical_name(), self.get_category_display(), self.reopen_count,
                                           ('Open' if self.completed is None else 'Expired'
                                           if self.expired else 'Completed'))

    def __bool__(self):
        return self.started is not None and (self.completed is not None or self.expired is not None)

    def time_open(self):
        if self.started is None:
            return 0
        if self.completed is not None:
            return (self.completed - self.started).seconds
        return (timezone.now() - self.started).seconds

    def get_canonical_name(self):
        if self.team is not None:
            return '%s\\%s' % (self.team.get_canonical_name(), self.name)
        return self.name

    def close(self, expired=False):
        self.reopen_count = self.reopen_count + 1
        self.completed = timezone.now()
        if expired:
            self.expired = True
        self.save()

    def assign(self, reassign=False):
        if self.completed is not None or reassign:
            if reassign:
                self.completed = None
            self.started = timezone.now()
            self.expired = False
            self.expires_date = self.started + timedelta(seconds=self.expires)
            self.save()


class Service(GridModel):
    """
    Scorebot v3: Service

    Stores the data related to a in game service.  The service consists of a port check and returns the status based
    on the outcome of the port check (pass | timeout | reset | refused).  Services can also be marked as bouns ports
    which have no value when no opened at all.
    """

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    port = models.PositiveIntegerField('Service Port')
    name = models.SlugField('Service Name', max_length=64)
    bonus = models.BooleanField('Service is Bonus', default=False)
    value = models.PositiveSmallIntegerField('Service Value', default=50)
    bonus_started = models.BooleanField('Service Bonus Enabled', default=False, editable=False)
    host = models.ForeignKey('scorebot_grid.Host', on_delete=models.SET_NULL, null=True, related_name='services')
    application = models.SlugField('Service Application Type', default=CONST_GRID_SERVICE_APPLICATION, max_length=64)
    protocol = models.PositiveSmallIntegerField('Service Protocol', default=0,
                                                choices=CONST_GRID_SERVICE_PROTOCOL_CHOICES)
    status = models.PositiveSmallIntegerField('Service Status', default=2, choices=CONST_GRID_SERVICE_STATUS_CHOICES,
                                              editable=False)
    content = models.ForeignKey('scorebot_grid.Content', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='service')

    def reset(self):
        self.status = 1
        self.bonus_started = False
        self.save()

    def __str__(self):
        return '[Service] %s %s<%s|%d/%s> %s' % (self.get_canonical_name(), ('(B) ' if self.bonus else ''),
                                                 self.application, self.port, self.get_protocol_display(),
                                                 self.get_status_display().upper())

    def __bool__(self):
        if self.bonus and not self.bonus_started:
            return False
        return self.status == 0

    def get_score(self):
        if self.__bool__():
            if self.content is not None:
                return math.floor(self.value * (self.content.status / 100))
            return self.value
        return 0

    def get_json_job(self):
        content = None
        if self.content is not None:
            content = self.content.get_json_job()
        return {'port': self.port, 'application': self.application, 'protocol': self.get_protocol_display(),
                'content': content}

    def get_canonical_name(self):
        if self.host is not None:
            return '%s\\%s' % (self.host.get_canonical_name(), self.name)
        return self.name

    def get_json_scoreboard(self):
        return {'status': ('green' if self.status == 0 else 'yellow' if self.status == 4 else 'red'), 'id': self.id,
                'protocol': html.escape(self.get_protocol_display()[0].lower()), 'port': self.port, 'bonus': self.bonus}

    def save(self, *args, **kwargs):
        if self.content is not None:
            self.content.save()
        super(Service, self).save(*args, **kwargs)

    def score_job(self, job, job_data):
        if 'status' not in job_data:
            logger.warning('SBE-JOB', 'Invalid Service "%s" JSON data by Job "%d"!' % (self.get_canonical_name(),
                                                                                       job.id))
            return
        service_status = self.status
        job_status = job_data['status'].lower()
        for status_value in CONST_GRID_SERVICE_STATUS_CHOICES:
            if status_value[1].lower() == job_status:
                service_status = status_value[0]
                break
        if service_status == 0 and self.bonus and not self.bonus_started:
            self.bonus_started = True
        self.status = service_status
        self.save()
        logger.debug('SBE-JOB', 'Service "%s" was set "%s" by Job "%d".' % (self.get_canonical_name(),
                                                                            self.get_status_display(), job.id))
        if 'content' in job_data and self.content is not None:
            if 'status' in job_data['content']:
                try:
                    self.content.status = int(job_data['content']['status'])
                    logger.debug('SBE-JOB', 'Service Content for "%s" was set to "%d" by Job "%d".' %
                                 (self.get_canonical_name(), self.content.status, job.id))
                except ValueError:
                    self.content.status = 0
                    logger.warning('SBE-JOB', 'Service Content for "%s" was invalid in Job "%d".' %
                                   (self.get_canonical_name(), job.id))
            else:
                self.content.status = 0
                logger.warning('SBE-JOB', 'Service Content for "%s" was invalid in Job "%d".' %
                               (self.get_canonical_name(), job.id))
            self.content.save()
        elif self.content is not None:
            self.content.status = 0
            self.content.save()
            logger.warning('SBE-JOB', 'Service Content for "%s" was ignored by Job "%d".' %
                           (self.get_canonical_name(), job.id))
        logger.info('SBE-JOB', 'Finished scoring Service "%s" by Job "%d".' % (self.get_canonical_name(), job.id))


class Content(GridModel):
    """
    Scorebot v3: Content

    Stores data to be checked against by Monitors.  The "data" attribute stores the checked data in string format.
    More complex data types, will be stored in JSON format.  The type attribute specifies what the data contains and
    how the monitor should use the data to validate the returned content.
    """

    class Meta:
        verbose_name = 'Service Content'
        verbose_name_plural = 'Service Content'

    data = models.TextField('Content Data', null=True, blank=True)
    status = models.SmallIntegerField('Content Passed Percentage', default=0, editable=False)
    type = models.CharField('Content Type', max_length=64, default=CONST_GRID_CONTENT_TYPE_DEFAULT)

    def reset(self):
        self.status = 0
        self.save()

    def __str__(self):
        return '[Content] %s <%s>' % ((self.service.all().last().get_canonical_name()
                                       if self.service.all().count() > 0 is not None else '(null)'), self.type)

    def get_json_job(self):
        try:
            content = json.loads(self.data)
        except json.decoder.JSONDecodeError:
            content = self.data
        return {'type': self.type, 'content': content}

    def save(self, *args, **kwargs):
        if self.service.all().count() > 1:
            raise ValidationError({'service': 'Content objects cannot be linked to multiple Service objects!'})
        super(Content, self).save(*args, **kwargs)


# TODO: Add Hypervisor hooks to this class
class Hypervisor(GridModel):
    """
    Scorebot v3: Hypervisor

    Represents a Hypervisor Host on the Grid.  Used for automation.
    """

    class Meta:
        verbose_name = 'VM Hypervisor'
        verbose_name_plural = 'VM Hypervisors'

    name = models.SlugField('Hypervisor Name', max_length=150)
    address = models.GenericIPAddressField('DNS Server', protocol='both', unpack_ipv4=True)

    def __str__(self):
        return '[Hypervisor] %s' % self.name

    # TODO: Make methods to revert VMs
    def reset(self):
        hosts = self.guests.all()
        for host in hosts:
            print('Hypervisor "%s" would reset VM "%s" if implemented' % (self.name, host.name))

    # TODO: Make methods to power on VMs
    def on_start(self):
        hosts = self.guests.all()
        for host in hosts:
            print('Hypervisor "%s" would power on VM "%s" if implemented' % (self.name, host.name))

    # TODO: Make methods to power off VMs
    def on_finish(self):
        hosts = self.guests.all()
        for host in hosts:
            print('Hypervisor "%s" would power off VM "%s" if implemented' % (self.name, host.name))
