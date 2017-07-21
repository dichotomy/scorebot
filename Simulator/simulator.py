
import collections
import csv
import datetime
import dateutil
import dateutil.parser
import sys
import os.path


class Config(object):

    # Health & welfare
    HW_INTERVAL = 5 * 60  # 5 minutes
    HW_SERVICES = {
            # Names don't matter, they're just strings
            'A_21/tcp': 50,
            'A_80/tcp': 100,
            'B_80/tcp': 100,
            }
    HW_SCORES = {
            # Keys are state names, percent of service score
            'DOWN': 0,
            'UP': 100,
            'HALFUP': 50,
            }

    # Tickets
    TICKET_INTERVAL = 5 * 60  # 5 minutes
    TICKET_GRACE_PERIOD = 15 * 60  # 15 minutes
    TICKET_COST = 100
    TICKET_AGGRAVATION_COST = TICKET_COST * 300
    TICKET_REOPEN_COST = int(TICKET_COST * 1.5)

    # Beacons
    BEACON_INTERVAL = 5 * 60  # 5 minutes
    BEACON_COST = 100

    # Flags
    FLAG_INTERVAL = 5 * 60
    FLAG_VALUE = 100
    FLAG_STOLEN_VALUE = FLAG_VALUE * 3


class Event(object):

    BEACON = 'BEACON'
    SERVICE = 'SERVICE'
    FLAG = 'FLAG'
    TICKET = 'TICKET'

    def __init__(self, timestamp, team, event_type, event_id, value):
        self.timestamp = dateutil.parser.parse(timestamp)
        self.team = team
        assert event_type in (self.BEACON, self.SERVICE, self.FLAG, self.TICKET)
        self.event_type = event_type
        self.event_id = event_id
        self.value = value
        self.impact = None
        self.current_score = None

    @property
    def time_str(self):
        return self.timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    def to_csv(self):
        return (self.time_str, self.team, self.event_type, self.event_id,
                self.value, self.impact, self.current_score)


class GenericService(object):

    def __init__(self, start_time):
        self.elements = collections.defaultdict(self.ELEMENT_TYPE)
        self.start_time = start_time

    @property
    def interval(self):
        return datetime.timedelta(seconds=self.INTERVAL)

    def add_event(self, event):
        entity_id = (event.team, event.event_id)
        self.elements[entity_id].update_state(event.value, event.timestamp)
        return self.elements[entity_id].round_score(
                self.get_round(event.timestamp))

    def get_round(self, when):
        delta = when - self.start_time
        return delta.seconds / self.interval.seconds


class RoundObject(object):

    def round_score(self, rnd):
        try:
            if self.rnd == rnd:
                return 0
        except AttributeError:
            pass
        self.rnd = rnd
        return self.score


class Flag(RoundObject):

    SAFE = 0
    STOLEN = 1
    STOLEN_OLD = 2

    def __init__(self):
        self.state = self.SAFE

    def update_state(self, value, unused_timestamp):
        if value == 'SAFE':
            self.state = self.SAFE
            return
        if value == 'STOLEN' and self.state == self.SAFE:
            self.state = self.STOLEN

    @property
    def score(self):
        if self.state == self.SAFE:
            return Config.FLAG_VALUE
        if self.state == self.STOLEN:
            self.state = self.STOLEN_OLD
            return -Config.FLAG_STOLEN_VALUE
        return 0


class FlagService(GenericService):

    ELEMENT_TYPE = Flag
    INTERVAL = Config.FLAG_INTERVAL


class Ticket(RoundObject):

    GRACE = 0
    OPEN = 1
    CLOSED = 2
    REOPENED_FIRST = 3
    REOPENED = 4

    def __init__(self):
        self.state = self.GRACE
        self.start = None

    def update_state(self, value, timestamp):
        """Complex states for reopening, grace periods."""
        if value == 'CLOSED':
            self.state = self.CLOSED
        elif value == 'OPEN':
            if self.start is None:
                self.start = timestamp
            elif ((timestamp - self.start) <
                    datetime.timedelta(seconds=Config.TICKET_GRACE_PERIOD)):
                return
            if self.state == self.CLOSED:
                self.state = self.REOPENED_FIRST
            elif self.state not in (self.REOPENED, self.REOPENED_FIRST):
                self.state = self.OPEN

    @property
    def score(self):
        if self.state == self.OPEN:
            return -Config.TICKET_COST
        elif self.state == self.REOPENED_FIRST:
            self.state = self.REOPENED
            return -(Config.TICKET_REOPEN_COST + Config.TICKET_AGGRAVATION_COST)
        elif self.state == self.REOPENED:
            return -Config.TICKET_REOPEN_COST
        return 0


class TicketService(GenericService):

    ELEMENT_TYPE = Ticket
    INTERVAL = Config.TICKET_INTERVAL


class Beacon(RoundObject):

    ALIVE = 0
    SILENT = 1

    def __init__(self):
        self.state = self.ALIVE
        self.last_alive = None

    def update_state(self, value, timestamp):
        if value == 'ALIVE':
            self.state = self.ALIVE
            self.last_alive = timestamp
        else:
            self.state = self.SILENT

    @property
    def score(self):
        if self.state == self.SILENT:
            return 0
        return -Config.BEACON_COST


class BeaconService(GenericService):

    ELEMENT_TYPE = Beacon
    INTERVAL = Config.BEACON_INTERVAL


class Service(RoundObject):

    UP = 0
    HALFUP = 1
    DOWN = 2

    STATE_STR = {
            0: 'UP',
            1: 'HALFUP',
            2: 'DOWN',
            }

    def __init__(self):
        self.state = self.UP
        self.ts = None

    def update_state(self, value, timestamp):
        self.ts = timestamp
        self.state = getattr(self, value)

    @property
    def score(self):
        try:
            base_score = Config.HW_SERVICES[self.service_id]
        except KeyError:
            raise ValueError('Unconfigured service %s' % self.service_id)
        base_score *= Config.HW_SCORES[self.STATE_STR[self.state]]
        return base_score / 100


class WelfareService(GenericService):

    ELEMENT_TYPE = Service
    INTERVAL = Config.HW_INTERVAL

    def add_event(self, event):
        entity_id = (event.team, event.event_id)
        self.elements[entity_id].service_id = event.event_id
        self.elements[entity_id].update_state(event.value, event.timestamp)
        return self.elements[entity_id].round_score(
                self.get_round(event.timestamp))


class Game(object):

    def __init__(self):
        self.scores = collections.defaultdict(int)
        self.game_time = None
        self.scores_changed = False

    def start_services(self, start_time):
        self.game_time = start_time
        self.flags = FlagService(start_time)
        self.beacons = BeaconService(start_time)
        self.tickets = TicketService(start_time)
        self.welfare = WelfareService(start_time)
        self.services = {
                'FLAG': self.flags,
                'BEACON': self.beacons,
                'TICKET': self.tickets,
                'SERVICE': self.welfare,
                }

    def add_event(self, event):
        if self.game_time is None:
            self.start_services(event.timestamp)
        if self.game_time != event.timestamp:
            self.game_time = event.timestamp
        score = self.services[event.event_type].add_event(event)
        if score > 0:
            self.scores_changed = True
        event.impact = score
        self.scores[event.team] += score
        event.current_score = self.scores[event.team]
        self.print_scores()

    def print_scores(self):
        if not self.scores_changed:
            return
        sc = []
        for k, v in self.scores.iteritems():
            sc.append('%12s: %8d' % (k, v))
        print '\t'.join(sc)
        self.scores_changed = False


class FileLoader(object):

    def __init__(self, filename, game):
        self.game = game
        with open(filename, 'rb') as fp:
            outname = os.path.splitext(filename)
            outname = outname[0] + '-out' + outname[1]
            with open(outname, 'wb') as outfp:
                outcsv = csv.writer(outfp)
                csvfp = csv.reader(fp)
                for line in csvfp:
                    event = Event(*line)
                    game.add_event(event)
                    outcsv.writerow(event.to_csv())


def main(argv):
    game = Game()
    FileLoader(argv[1], game)


if __name__ == '__main__':
    main(sys.argv)
