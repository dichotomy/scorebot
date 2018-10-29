import os
import json
import uuid
import inspect
import scorebot.utils

from django.db import models
from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from scorebot_game.models import GameTeam
from scorebot_api import admin as sbe_admin
from django.core.handlers.wsgi import WSGIRequest
from scorebot_core.models import AccessToken, Token
from scorebot.utils.logger import log_debug, log_error
from scorebot.utils.constants import CONST_GAME_GAME_RUNNING
from django.http import HttpResponseBadRequest, HttpResponseForbidden

try:
    from ipware.ip import get_ip
except ImportError:
    log_error('BACKEND', 'Django IPware is missing, all IP address lookups will return fake data. '
                         'Please use "pip install django-ipware" to install the plugin.')

    def get_ip(request): return 'ERR-DJANGO-IPWARE-MISSING'


_MODELS_REGISTERED = []
scorebot.utils.get_ip = get_ip


def get_client_ip(request):
    return get_ip(request)


def authenticate(requires=None):
    def _authenticate_wrapper(auth_function):
        def _authenticate_wrapped(*args, **kwargs):
            http_request = None
            for argument in args:
                if isinstance(argument, WSGIRequest):
                    http_request = argument
                    break
            if http_request is None:
                for value in kwargs.values():
                    if isinstance(value, WSGIRequest):
                        http_request = value
                        break
            if http_request is None:
                log_error('API', 'AUTH (NO-IP): Connected but no HTTP headers were found!')
                return HttpResponseBadRequest(content='{"message": "SBE API: Invalid HTTP connection!"}')
            http_ip = get_ip(http_request)
            if 'HTTP_SBE_AUTH' not in http_request.META:
                log_error('API', 'AUTH (%s): Attempted to connect without a proper authentication header!' %
                          http_ip)
                return HttpResponseForbidden(content='{"message": "SBE API: Missing authentication header!"}')
            try:
                http_request.authentication = AccessToken.objects.get(
                    token__uuid=uuid.UUID(http_request.META['HTTP_SBE_AUTH']))
            except ValueError:
                log_error('API',
                          'AUTH (%s): Attempted to connect with an invalid authentication token format "%s"!'
                          % (http_ip, http_request.META['HTTP_SBE_AUTH']))
                return HttpResponseForbidden(content='{"message": "SBE API: Invalid authentication token format!"}')
            except AccessToken.DoesNotExist:
                log_error('API',
                          'AUTH (%s): Attempted to connect with an non-existent authentication token "%s"!'
                          % (http_ip, http_request.META['HTTP_SBE_AUTH']))
                return HttpResponseForbidden(content='{"message": "SBE API: Invalid authentication token!"}')
            except AccessToken.MultipleObjectsReturned:
                log_error('API', 'AUTH (%s): Submitted token returned multiple entries, token "%s" must be invalid!'
                          % (http_ip, http_request.META['HTTP_SBE_AUTH']))
                return HttpResponseForbidden(content='{"message": "SBE API: Invalid authentication token!"}')
            if not http_request.authentication:
                log_error('API', 'AUTH (%s): Attempted to use an expired authentication token "%s"!' %
                          (http_ip, http_request.authentication.token.uuid))
                return HttpResponseForbidden(content='{"message": "SBE API: Authentication token is expired!"}')
            if requires is not None:
                if isinstance(requires, list):
                    for requires_item in requires:
                        if not http_request.authentication[requires_item]:
                            log_error('API',
                                      'AUTH (%s): Attempted to access the API without the proper '
                                      'permissions! (%s)' % (http_ip, str(requires_item)))
                            return HttpResponseForbidden(
                                content='{"message": "SBE API: Authentication Token missing "%s" permission!"}'
                                        % str(requires_item))
                elif isinstance(requires, str) or isinstance(requires, int):
                    if not http_request.authentication[requires]:
                        log_error('API',
                                  'AUTH (%s): Attempted to access the API without the proper '
                                  'permissions! (%s)' % (http_ip, str(requires)))
                        return HttpResponseForbidden(
                            content='{"message": "SBE API: Authentication Token missing "%s" permission!"}'
                                    % str(requires))
            log_debug('API', 'AUTH (%s): Successfully authenticated to the SBE API. Passing control to function "%s".'
                      % (http_ip, auth_function.__qualname__))
            return auth_function(*args, **kwargs)
        return _authenticate_wrapped
    return _authenticate_wrapper


def dump_data(dump_name, data_to_dump):
    if dump_name is None or data_to_dump is None:
        return
    if settings.DUMP_DATA:
        try:
            if not os.path.exists(settings.DUMP_DIR):
                os.mkdir(settings.DUMP_DIR)
            dump_file = open('dump-%s-%s' % (dump_name, timezone.now().strftime('%m.%d.%y-%H.%M.%S')), 'w')
            dump_file.write(str(data_to_dump))
            dump_file.closed()
        except:
            pass


def import_all_models(models_class, models_ignore=list()):
    if models_class is None:
        return ValueError('Parameter "models_class" cannot be None!')
    if not isinstance(models_ignore, list):
        return ValueError('Parameter "models_ignore" must be a "list" object type!')
    for model_class_object in inspect.getmembers(models_class, inspect.isclass):
        if model_class_object is not None and model_class_object[1] not in _MODELS_REGISTERED:
            if model_class_object not in models_ignore or model_class_object.__name__ not in models_ignore:
                if issubclass(model_class_object[1], models.Model) and not model_class_object[1]._meta.abstract:
                    if 'django.contrib' not in model_class_object[1].__module__:
                        log_debug('BACKEND', 'Registering model "%s"' % model_class_object[1].__name__)
                        try:
                            admin_model = getattr(sbe_admin, '%sAdmin' % model_class_object[1].__name__)
                            admin.site.register(model_class_object[1], admin_model)
                        except AttributeError:
                            admin.site.register(model_class_object[1])
                        _MODELS_REGISTERED.append(model_class_object[1])


def game_team_from_token(request, api_name, json_field, offense=True, beacon=False, fields=None):
    client = get_ip(request)
    try:
        decoded_data = request.body.decode('UTF-8')
    except UnicodeDecodeError:
        log_error('API', '%s (%s): Data submitted by is not encoded properly!' % (api_name.upper(), client))
        return None, None, None, HttpResponseBadRequest(
            content='{"message": "SBE API: Incorrect encoding, please use UTF-8!"}')
    try:
        json_data = json.loads(decoded_data)
    except json.decoder.JSONDecodeError:
        log_error('API', '%s (%s): Data submitted is not in a valid JSON format!' % (api_name.upper(), client))
        return None, None, None, HttpResponseBadRequest(content='{"message": "SBE API: Not in a valid JSON format!"}')
    if json_field not in json_data:
        log_error('API', '%s (%s): Data submitted is missing field "%s"!' % (api_name.upper(), client, json_field))
        return None, None, None, HttpResponseBadRequest(content='{"message": "SBE API: Missing JSON field \'%s\'!"}' %
                                                        json_field)
    if fields is not None and isinstance(fields, list):
        for field in fields:
            if field not in json_data:
                log_error('API', '%s (%s): Data submitted is missing field "%s"!' % (api_name.upper(), client, field))
                return None, None, None, HttpResponseBadRequest(
                    content='{"message": "SBE API: Missing JSON field \'%s\'!"}' % field)
    log_debug('API', '%s (%s): Team Token submitted is "%s"!' % (api_name.upper(), client, json_data[json_field]))
    try:
        token = Token.objects.get(uuid=uuid.UUID(json_data[json_field]))
    except ValueError:
        log_error('API', '%s (%s): Team Token submitted is not a valid format!' % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(
            content='{"message": "SBE API: Team Token is not a valid format!"}')
    except Token.DoesNotExist:
        log_error('API', '%s (%s): Team Token submitted does not exist!' % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is not valid!"}')
    except Token.MultipleObjectsReturned:
        log_error('API', '%s (%s): Team Token submitted returns multiple objects, must be invalid!'
                  % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is not valid!"}')
    if token is None:
        log_error('API', '%s (%s): Team Token submitted does not exist!' % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is not valid!"}')
    if not token.__bool__():
        log_error('API', '%s (%s): Team Token submitted is expired!' % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is expired!"}')
    try:
        if beacon:
            team = GameTeam.objects.get(beacons__in=[token])
        else:
            team = GameTeam.objects.get(token=token)
    except GameTeam.DoesNotExist:
        log_error('API', '%s (%s): Token submitted is not linked to a Team!' % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Not a Team Token!"}')
    except GameTeam.MultipleObjectsReturned:
        log_error('API', '%s (%s): Token submitted by matched multiple Teams, must be invalid!'
                  % (api_name.upper(), client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is not valid!"}')
    log_debug('API', '%s (%s): Team "%s" was authenticated to the API!'
              % (api_name.upper(), client, team.get_canonical_name()))
    if offense:
        if not team.offensive:
            log_error('API', '%s (%s): Attempted to authenticate a non Offensive team "%s" to an Offensive service!'
                      % (api_name.upper(), client, team.get_canonical_name()))
            return None, None, None, HttpResponseForbidden(
                content='{"message": "SBE API: Team is not authorized for this type of request!"}')
    if team.game.status != CONST_GAME_GAME_RUNNING:
        log_error('API', '%s (%s): Game "%s" submitted is not Running!' % (api_name.upper(), client, team.game.name))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Game "%s" is not Running!"}'
                                                               % team.game.name)
    del decoded_data
    return team, token, json_data, None
