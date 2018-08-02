from django.utils import timezone

from daemon import DaemonEntry
from scorebot.utils import SCORE_EVENTS
from scorebot.utils.logger import log_info

LOG_NAME = 'SCORING'


def init_daemon():
    return DaemonEntry('scorelog', 10, write_score_log, 30)


def write_score_log():
    for score_event in SCORE_EVENTS:
        log_info(LOG_NAME, score_event)
        SCORE_EVENTS.remove(score_event)
