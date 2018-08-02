CONST_GRID_FLAG_VALUE = 100
CONST_GAME_GAME_RUNNING = 1
CONST_GAME_GAME_MODE_CHOICES = (
    (0, 'Red-v-Blue'),
    (1, 'Blue-v-Blue'),
    (2, 'King'),
    (3, 'Rush'),
    (4, 'Defend'),
)
CONST_FORM_EVENT_CREATE_CHOICES = (
    ('message', 'message'),
    ('window', 'window'),
    ('effect', 'effect'),
)
CONST_CORE_ACCESS_KEY_LEVELS = {
    '__ALL_READ': 1,
    '__ALL_WRITE': 2,
    '__ALL_UPDATE': 3,
    '__ALL_DELETE': 4,
    '__SYS_CLI': 5,
    '__SYS_FLAG': 6,
    '__SYS_BEACON': 7,
    '__SYS_STORE': 61,
    '__SYS_TICKET': 62,
    'Monitor.READ': 8,
    'Monitor.UPDATE': 9,
    'Monitor.CREATE': 10,
    'Monitor.DELETE': 11,
    'Options.READ': 12,
    'Options.UPDATE': 13,
    'Options.CREATE': 14,
    'Options.DELETE': 15,
    'Player.READ': 16,
    'Player.CREATE': 17,
    'Score.READ': 18,
    'Score.UPDATE': 19,
    'Score.CREATE': 20,
    'Score.DELETE': 21,
    'Team.READ': 22,
    'Team.CREATE': 23,
    'Compromise.READ': 24,
    'Content.READ': 25,
    'Content.UPDATE': 26,
    'Content.CREATE': 27,
    'Content.DELETE': 28,
    'DNS.READ': 29,
    'DNS.UPDATE': 30,
    'DNS.CREATE': 31,
    'DNS.DELETE': 32,
    'Flag.READ': 33,
    'Flag.UPDATE': 34,
    'Flag.CREATE': 35,
    'Flag.DELETE': 36,
    'GameTeam.READ': 37,
    'GameTeam.UPDATE': 38,
    'GameTeam.CREATE': 39,
    'GameTeam.DELETE': 40,
    'Host.READ': 41,
    'Host.UPDATE': 42,
    'Host.CREATE': 43,
    'Host.DELETE': 44,
    'Service.READ': 45,
    'Service.UPDATE': 46,
    'Service.CREATE': 47,
    'Service.DELETE': 48,
    'Ticket.READ': 49,
    'Ticket.UPDATE': 50,
    'Ticket.CREATE': 51,
    'Ticket.DELETE': 52,
    'Game.READ': 53,
    'Game.UPDATE': 54,
    'Game.CREATE': 55,
    'Game.DELETE': 56,
    'GameMonitor.READ': 57,
    'GameMonitor.UPDATE': 58,
    'GameMonitor.CREATE': 59,
    'GameMonitor.DELETE': 60,
}
CONST_GAME_GAME_STATUS_CHOICES = (
    (0, 'Stopped'),
    (1, 'Running'),
    (2, 'Paused'),
    (3, 'Canceled'),
    (4, 'Completed'),
)
CONST_GAME_EVENT_TYPE_CHOICES = (
    (0, 'Message'),
    (1, 'Window'),
    (2, 'Effect'),
)
CONST_EVENT_DEFAULT_TIMEOUT = 10
CONST_GAME_EVENT_TIMEOUT_DEFAULT = 5
CONST_GAME_GAME_OPTIONS_DEFAULTS = {
    'ticket_cost': 125,
    'round_time': 300,
    'beacon_time': 300,
    'job_timeout': 300,
    'beacon_value': 100,
    'host_ping_ratio': 50,
    'job_cleanup_time': 900,
    'ticket_max_score': 6000,
    'flag_stolen_rate': 8400,
    'score_exchange_rate': 100,
    'ticket_grace_period': 900,
    'ticket_max_scoring': 14400,
    'ticket_reopen_multiplier': 10,
    'flag_captured_multiplier': 300,
}
CONST_GRID_SERVICE_STATUS_CHOICES = (
    (0, 'pass'),
    (1, 'reset'),
    (2, 'timeout'),
    (3, 'refused'),
    (4, 'invalid'),
)
CONST_GRID_SERVICE_APPLICATION = 'http'
CONST_GRID_TICKET_CATEGORIES_CHOICES = (
    (0, 'No Category'),
    (1, 'Outage'),
    (2, 'Service Request'),
    (3, 'Change'),
    (4, 'Issue'),
    (5, 'Deliverable'),
)
CONST_GRID_SERVICE_PROTOCOL_CHOICES = (
    (0, 'tcp'),
    (1, 'udp'),
    (2, 'icmp'),
)
CONST_GRID_CONTENT_TYPE_DEFAULT = 'text'
CONST_GRID_TICKET_EXPIRE_TIME_DEFAULT = 1800
CONST_GAME_GAME_MESSAGE = 'This is Scorebot v3'
