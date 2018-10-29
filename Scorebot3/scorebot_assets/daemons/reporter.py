from django.utils import timezone

from daemon import DaemonEntry
from scorebot_game.models import Game
from scorebot.utils.logger import log_debug
from scorebot.utils.constants import CONST_GAME_GAME_RUNNING


def init_daemon():
    return DaemonEntry('reporter', 60, report_round, 120)


def report_round():
    log_debug('DAEMON', 'Reporting on Scores..')
    games = Game.objects.filter(finish__isnull=True, status=CONST_GAME_GAME_RUNNING)
    if games is not None and len(games) > 0:
        check_time = timezone.now()
        for game in games:
            game.reporter_check(check_time)
    del games
