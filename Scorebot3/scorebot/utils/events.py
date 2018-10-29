from datetime import timedelta
from django.utils import timezone
from scorebot.utils.logger import log_debug, log_error
from scorebot.utils.constants import CONST_GAME_GAME_MESSAGE


class EventHost(object):
    def __init__(self):
        self.games = dict()

    def post_tweet(self, status):
        post_tweet(status)


EVENT_HOST = EventHost()


def post_tweet(message):
    # Hack
    from scorebot_game.models import GameEvent, Game

    a = GameEvent()
    a.type = 0
    a.timeout = timezone.now() + timedelta(minutes=5)
    a.data = '%s #PvJCTF #CTF #BSidesDC' % message
    try:
        b = Game.objects.filter(finish__isnull=True, status=1, start__isnull=False)
        a.game = b.first()
        a.save()
        log_debug("TWITTER", 'Added tweet to be sent "%s"!' % message)
    except Exception as err:
        log_error("TWITTER", "Error adding tweet! (%s)" % str(err))


def get_scoreboard_message(game_id):
    if game_id in EVENT_HOST.games:
        return EVENT_HOST.games[game_id]
    return CONST_GAME_GAME_MESSAGE
