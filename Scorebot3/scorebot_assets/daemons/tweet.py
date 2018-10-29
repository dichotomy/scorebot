import html

from tweepy import Stream, API
from datetime import timedelta
from daemon import DaemonEntry
from tweepy import OAuthHandler
from django.conf import settings
from django.utils import timezone
from tweepy.streaming import StreamListener
from scorebot_game.models import GameEvent, Game
from scorebot.utils.logger import log_debug, log_error

TWITTER = None


def tweet():
    for event in GameEvent.objects.all():
        if event.type == 0:
            TWITTER.tweet(event.data)
            event.delete()


def init_daemon():
    global TWITTER
    try:
        log_debug("TWITTER", "Attempting to setup twitter")
        TWITTER = TwitterAPI()
        log_debug("TWITTER", "Twitter initilized! Ready to russian spam!")
    except Exception as err:
        log_error("TWITTER", "Error setting up Twitter API! (%s)" % str(err))
    return DaemonEntry("tweet", 5, tweet, 10)


class TwitterAPI(StreamListener):
    def __init__(self):
        auth = OAuthHandler(
            consumer_key=settings.TWITTER_API["CONSUMER_KEY"],
            consumer_secret=settings.TWITTER_API["CONSUMER_SECRET"],
        )
        auth.set_access_token(
            key=settings.TWITTER_API["ACCESS_TOKEN"],
            secret=settings.TWITTER_API["ACCESS_TOKEN_SECRET"],
        )
        self.api = API(auth)
        self.stream = Stream(auth, self)
        self.stream.filter(track=settings.TWITTER_TRACKING, async=True)

    def tweet(self, content):
        log_debug("TWITTER", 'Preparing to tweet "%s".' % content)
        try:
            self.api.update_status(content)
        except Exception as err:
            log_error("TWITTER", 'Tweeting "%s" failed! (%s)' % (content, str(err)))

    def on_status(self, status):
        if not status.retweeted and status.user != 'scorebot1':
            # print(status)
            a = GameEvent()
            a.type = 1
            a.timeout = timezone.now() + timedelta(seconds=30)
            c = ""
            if 'extended_entities' in status._json and len(status.extended_entities['media']) > 0:
                c = '<div class="sbmeme"><img src="%s" /></div>' % status.extended_entities['media'][0]['media_url_https']
            a.data = (
                """<div class="sbtweet">%s<div class="sbtweeth"><img src="%s" alt="%s" />%s</div><div id="msg">%s</div></div>"""
                % (
                    c, status.user.profile_image_url_https,
                    html.escape(status.user.screen_name),
                    html.escape(status.user.screen_name),
                    html.escape(status.text)
                )
            )
            try:
                b = Game.objects.filter(
                    finish__isnull=True, status=1, start__isnull=False
                )
                a.game = b.first()
                a.save()
                log_debug("TWITTER", 'Added tweet by "%s"!' % (status.user.screen_name))
            except Exception as err:
                log_error("TWITTER", "Error Getting tweet! (%s)" % str(err))
