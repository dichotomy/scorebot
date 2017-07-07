from django.utils import timezone
# from scorebot.utils import logger
from scorebot_game.models import Game
from scorebot.utils.daemon import DaemonEntry


def init_daemon():
    return DaemonEntry('scoring', 15, score_round, 60)


def score_round():
    print('Checking games for scoring rounds..')
    # logger.debug('SBE-SCORING', 'Checking games for scoring rounds..')
    games = Game.objects.filter(finish__isnull=True, status=1)
    if games is not None and len(games) > 0:
        now = timezone.now()
        for game in games:
            game.round_score(now)
    del games
