from scorebot.utils.logger import log_debug, log_error, log_info, log_warning

SCORE_EVENTS = []


def api_event(game_id, event_message):
    if not game_id:
        return
    try:
        from scorebot_game.models import game_event_create
        game_event_create(game_id, event_message)
    except Exception as eventError:
        log_error('EVENT', str(eventError))


def api_info(api_name, message, request=None):
    if request is not None:
        client = get_ip(request)
        log_info('API', '%s (%s): %s' % (api_name.upper(), client, message))
        del client
    else:
        log_info('API', '%s (NO-IP): %s' % (api_name.upper(), message))


def api_error(api_name, message, request=None):
    if request is not None:
        client = get_ip(request)
        log_error('API', '%s (%s): %s' % (api_name.upper(), client, message))
        del client
    else:
        log_error('API', '%s (NO-IP): %s' % (api_name.upper(), message))


def api_debug(api_name, message, request=None):
    if request is not None:
        client = get_ip(request)
        log_debug('API', '%s (%s): %s' % (api_name.upper(), client, message))
        del client
    else:
        log_debug('API', '%s (NO-IP): %s' % (api_name.upper(), message))


def api_warning(api_name, message, request=None):
    if request is not None:
        client = get_ip(request)
        log_warning('API', '%s (%s): %s' % (api_name.upper(), client, message))
        del client
    else:
        log_warning('API', '%s (NO-IP): %s' % (api_name.upper(), message))


def api_score(score_id, score_type, score_name, score_value, score_data=None):
    SCORE_EVENTS.append('%s,%s,%s,%s,%s' % (score_id, score_type, score_name, score_value, score_data))
