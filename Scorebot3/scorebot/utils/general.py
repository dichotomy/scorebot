import json
import uuid
import inspect

from django.db import models
from django.contrib import admin
from scorebot.utils import logger
from scorebot_game.models import GameTeam
from scorebot_api import admin as sbe_admin
from django.core.handlers.wsgi import WSGIRequest
from scorebot_core.models import AccessToken, Token
from django.http import HttpResponseBadRequest, HttpResponseForbidden

try:
    from ipware.ip import get_ip
except ImportError:
    logger.error('SBE-GENERAL', 'Django IPware is missing, all IP address lookups will return fake data. '
                                'Please use "pip install django-ipware" to install the plugin.')

    def get_ip(request): return 'DJANGO-IPWARE-MISSING'

_MODELS_REGISTERED = []


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
                logger.error('SBE-AUTH', 'Client connected but no HTTP headers were found!')
                return HttpResponseBadRequest(content='SBE API: Invalid HTTP connection!')
            http_ip = get_ip(http_request)
            if 'HTTP_SBE_AUTH' not in http_request.META:
                logger.warning('SBE-AUTH', 'Client "%s" attempted to connect without a proper authentication header!' %
                               http_ip)
                return HttpResponseForbidden(content='SBE API: Missing authentication header!')
            try:
                http_request.authentication = AccessToken.objects.get(
                    token__uuid=uuid.UUID(http_request.META['HTTP_SBE_AUTH']))
            except ValueError:
                logger.warning('SBE-AUTH', 'Client "%s" attempted to connect with an invalid authentication token "%s"!'
                               % (http_ip, http_request.META['HTTP_SBE_AUTH']))
                return HttpResponseForbidden(content='SBE API: Invalid authentication token!')
            except AccessToken.DoesNotExist:
                logger.warning('SBE-AUTH', 'Client "%s" attempted to connect with an invalid authentication token "%s"!'
                               % (http_ip, http_request.META['HTTP_SBE_AUTH']))
                return HttpResponseForbidden(content='SBE API: Invalid authentication token!')
            except AccessToken.MultipleObjectsReturned:
                logger.warning('SBE-AUTH', 'Client "%s" attempted to connect with an invalid authentication token "%s"!'
                               % (http_ip, http_request.META['HTTP_SBE_AUTH']))
                return HttpResponseForbidden(content='SBE API: Invalid authentication token!')
            if not http_request.authentication:
                logger.warning('SBE-AUTH', 'Client "%s" is using an expired authentication token "%s"!' %
                               (http_ip, http_request.authentication.token.uuid))
                return HttpResponseForbidden(content='SBE API: Authentication token is expired!')
            if requires is not None:
                if isinstance(requires, list):
                    for requires_item in requires:
                        if not http_request.authentication[requires_item]:
                            logger.warning('SBE-AUTH',
                                           'Client "%s" attempted to access the API without proper permissions! (%s)'
                                           % (http_ip, requires_item))
                            return HttpResponseForbidden(
                                content='SBE API: Authentication Token missing "%s" permission!' % str(requires_item))
                elif isinstance(requires, str) or isinstance(requires, int):
                    if not http_request.authentication[requires]:
                        logger.warning('SBE-AUTH',
                                       'Client "%s" attempted to access the API without proper permissions! (%s)'
                                       % (http_ip, requires))
                        return HttpResponseForbidden(content='SBE API: Authentication Token missing "%s" permission!'
                                                             % str(requires))
            logger.debug('SBE-AUTH', 'Client "%s" successfully authenticated to the SBE API. '
                                     'Passing control back to function "%s".' % (http_ip, auth_function.__qualname__))
            return auth_function(*args, **kwargs)
        return _authenticate_wrapped
    return _authenticate_wrapper


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
                        logger.debug('SBE-GENERAL', 'Registering model "%s"' % model_class_object[1].__name__)
                        #print("%s.READ\n%s.UPDATE\n%s.CREATE\n%s.DELETE" %
                        #      (model_class_object[1].__name__,
                        #       model_class_object[1].__name__,
                        #       model_class_object[1].__name__,
                        #       model_class_object[1].__name__,))
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
        logger.warning('SBE-%s' % api_name.upper(), '%s API: Data submitted by Client "%s" is not encoded properly!'
                       % (api_name, client))
        return None, None, None, HttpResponseBadRequest(
            content='{"message": "SBE API: Incorrect encoding, please use UTF-8!"}')
    try:
        json_data = json.loads(decoded_data)
    except json.decoder.JSONDecodeError:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Data submitted by Client "%s" is not in correct JSON format!' % (api_name, client))
        return None, None, None, HttpResponseBadRequest(content='{"message": "SBE API: Not in valid JSON format!"}')
    if json_field not in json_data:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Data submitted by Client "%s" is not in correct JSON format!' % (api_name, client))
        return None, None, None, HttpResponseBadRequest(content='{"message": "SBE API: Not in valid JSON format!"}')
    if fields is not None and isinstance(fields, list):
        for field in fields:
            if field not in json_data:
                logger.warning('SBE-%s' % api_name.upper(),
                               '%s API: Data submitted by Client "%s" is not in correct JSON format!'
                               % (api_name, client))
                return None, None, None, HttpResponseBadRequest(
                    content='{"message": "SBE API: Not in valid JSON format!"}')
    try:
        token = Token.objects.get(uuid=uuid.UUID(json_data[json_field]))
    except ValueError:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Token submitted by Client "%s" was not found!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Token is not valid!"}')
    except Token.DoesNotExist:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Token submitted by Client "%s" was not found!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Token is not valid!"}')
    except Token.MultipleObjectsReturned:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Token submitted by Client "%s" was not found!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Token is not valid!"}')
    if token is None:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Token submitted by Client "%s" was not found!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Token is not valid!"}')
    if not token.__bool__():
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Token submitted by Client "%s" was expired!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Token is not valid (expired)!"}')
    try:
        if beacon:
            team = GameTeam.objects.get(beacons__in=token)
        else:
            team = GameTeam.objects.get(token=token)
    except GameTeam.DoesNotExist:
        logger.warning('SBE-%s' % api_name.upper()
                       , '%s API: Token submitted by Client "%s" was not found linked to a Team!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is not valid!"}')
    except GameTeam.MultipleObjectsReturned:
        logger.warning('SBE-%s' % api_name.upper(),
                       '%s API: Token submitted by Client "%s" matched multiple Teams!' % (api_name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Token is not valid!"}')
    logger.debug('SBE-%s' % api_name.upper(), 'Team "%s" authenticated to the %s API through Client "%s".'
                 % (team.get_canonical_name(), api_name, client))
    if offense:
        if not team.offensive:
            logger.warning('SBE-%s' % api_name.upper(), '%s API: Team "%s" submitted by Client "%s" is not Offensive!'
                           % (api_name, team.get_canonical_name(), client))
            return None, None, None, HttpResponseForbidden(
                content='{"message": "SBE API: Team is not authorized for this type of request!"}')
    if team.game.status != 1:
        logger.warning('SBE-%s' % api_name.upper(), '%s API: Game "%s" submitted by Client "%s" is not Running!'
                       % (api_name, team.game.name, client))
        return None, None, None, HttpResponseForbidden(content='{"message": "SBE API: Team Game "%s" is not Running!"}'
                                                               % team.game.name)
    del decoded_data
    return team, token, json_data, None
