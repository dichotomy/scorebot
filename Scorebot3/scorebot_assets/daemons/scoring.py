from django.utils import timezone

from daemon import DaemonEntry
from scorebot_game.models import Game, game_event_create
from scorebot.utils.logger import log_debug
from scorebot.utils.constants import CONST_GAME_GAME_RUNNING


def init_daemon():
    return DaemonEntry("scoring", 15, score_round, 60)


def score_round():
    log_debug("DAEMON", "Checking games for scoring rounds..")
    games = Game.objects.filter(finish__isnull=True, status=CONST_GAME_GAME_RUNNING)
    if games is not None and len(games) > 0:
        score_time = timezone.now()
        for game in games:
            game.round_score(score_time)
        del score_time
    del games
