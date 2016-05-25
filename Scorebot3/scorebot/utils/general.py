import inspect
import scorebot.utils.log as logger

from ipware.ip import get_real_ip
from django.core import serializers
from sbegame.models import AccessKey
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.db.models.manager import Manager
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError


def get_json(object_data):
    if object_data:
        field_data = None
        try:
            field_data = object.__fields__
        except AttributeError:
            pass
        return serializers.serialize('json', object_data, fields=field_data)
    return ''


def val_auth(api_function):
    def _val_function(*args, **kwargs):
        request = None
        for argd in args:
            if isinstance(argd, WSGIRequest):
                request = argd
                break
        if request is None:
            for k,v in kwargs.items():
                if isinstance(v, WSGIRequest):
                    request = v
                    break
        if request is None:
            logger.error(__name__, 'Connection to SBE without proper HTTP was made!')
            return HttpResponseForbidden(content='SBE [AUTH]: No HTTP header could be found!')
        if 'HTTP_SBE_AUTH' not in request.META:
            logger.warning(__name__, 'Connection to SBE by "%s" was made without authentication header!' %
                           get_real_ip(request))
            return HttpResponseForbidden(content='SBE [AUTH]: Missing SBE authentication header!')
        try:
            request.authkey = AccessKey.objects.get(key_uuid=request.META['HTTP_SBE_AUTH'])
        except AccessKey.DoesNotExist:
            logger.warning(__name__, 'Connection to SBE by "%s" was made with an incorrect authentication header "%s"!'
                           % (get_real_ip(request), request.META['HTTP_SBE_AUTH']))
            return HttpResponseForbidden(content='SBE [AUTH]: Incorrect SBE authentication header!')
        logger.debug(__name__, 'Successful connection by "%s" to SBE API! Requesting function "%s"' %
                     (get_real_ip(request), api_function.__name__))
        return api_function(*args, **kwargs)
    return _val_function


def all_models_for_mod(module):
    model_list = []
    for ml in module.__dict__.keys():
        mclass = getattr(module, ml)
        if inspect.isclass(mclass) and module.__name__ in str(mclass.__module__):
            model_list.append(mclass)
    return model_list


def get_query_set(object_class):
    if isinstance(object_class, QuerySet):
        return object_class
    elif isinstance(object_class, Manager):
        manager = object_class
    elif isinstance(object_class, ModelBase):
        manager = object_class._default_manager
    else:
        if isinstance(object_class, type):
            object_class__name = object_class.__name__
        else:
            object_class__name = object_class.__class__.__name__
        raise ValueError('Object is of type "%s", but must be a Django Model, Manager, or QuerySet' %
                         object_class__name)
    return manager.all()


def save_json_or_error(request, json_id=None, json_response=True):
    if request is None:
        return HttpResponseBadRequest('SBE [API]: Incorrect HTTP headers!') if json_response else None
    if request.method == 'PUT' and json_id:
        logger.warning(__name__, 'Request by "%s" attempted to use PUT to update an existing object!' %
                       get_real_ip(request))
        return HttpResponseBadRequest('SBE [API]: PUT cannot update objects! Use POST!') if json_response else None
    if request.method == 'POST' and not json_id:
        logger.warning(__name__, 'Request by "%s" attempted to use POST to create an object!' % get_real_ip(request))
        return HttpResponseBadRequest('SBE [API]: POST cannot create objects! Use PUT!') if json_response else None
    if request.method == 'DELETE' and not json_id:
        logger.warning(__name__, 'Request by "%s" attempted to use DELETE with no ID!' % get_real_ip(request))
        return HttpResponseBadRequest('SBE [API]: DELETE requires an ID value!') if json_response else None
    if not request.body or len(request.body) == 0:
        logger.warning(__name__, 'Request by "%s" attempted to send an empty request body!' % get_real_ip(request))
        return HttpResponseBadRequest('SBE [API]: Request body cannot be empty!') if json_response else None
    json_results = []
    try:
        for jobject in serializers.deserialize('json', request.body):
            if request.method == 'POST':
                if request.authkey['ALL_UPDATE'] or request.authkey['%s.UPDATE' % jobject.__class__.name__]:
                    logger.debug(__name__, '"%s" value "%s" was updated by "%s"' %
                                 (jobject.__class__.__name__, str(jobject), get_real_ip(request)))
                    jobject.save()
                else:
                    logger.warning(__name__, '"%s" value "%s" was not updated by "%s" due to permissions!' %
                                 (jobject.__class__.__name__, str(jobject), get_real_ip(request)))
            if request.method == 'PUT':
                if request.authkey['ALL_CREATE'] or request.authkey['%s.CREATE' % jobject.__class__.name__]:
                    jobject.save()
                    logger.debug(__name__, '"%s" value "%s" was created by "%s"' %
                                 (jobject.__class__.__name__, str(jobject), get_real_ip(request)))
                else:
                    logger.warning(__name__, '"%s" value "%s" was not created by "%s" due to permissions!' %
                                 (jobject.__class__.__name__, str(jobject), get_real_ip(request)))
            if request.method == 'DELETE':
                if request.authkey['ALL_DELETE'] or request.authkey['%s.DELETE' % jobject.__class__.name__]:
                    logger.debug(__name__, '"%s" value "%s" was deleted by "%s"' %
                                 (jobject.__class__.__name__, str(jobject), get_real_ip(request)))
                    jobject.delete()
                else:
                    logger.warning(__name__, '"%s" value "%s" was not deleted by "%s" due to permissions!' %
                                 (jobject.__class__.__name__, str(jobject), get_real_ip(request)))
            json_results.append(jobject)
    except ValueError:
        logger.warning(__name__, 'Request by "%s" attempted to send an invalid request body!' % get_real_ip(request))
        return HttpResponseBadRequest('SBE [API]: Request body was not in JSON format!') if json_response else None
    except Exception:
        logger.get_logger(__name__).error('Exception occured during "save_json_or_error" by "%s"' %
                                          get_real_ip(request), exec_info=True)
        return HttpResponseServerError('SBE [API]: Server error in processing request!') if json_response else None
    return HttpResponse(status=(200 if request.method == 'POST' else 201), content=get_json(json_results)) \
        if json_response else json_results


def get_object_with_id(request, object_class, object_id=None, object_limit=200, object_page=0, object_response=True):
    if object_class is not None:
        object_model = get_query_set(object_class)
        if object_model is not None:
            if not request.authkey['ALL_READ'] and not request.authkey['%s.READ' % object_class.__name__]:
                logger.warning(__name__, 'Model "%s" could not be requested from the database due to permissions!'
                               % object_class.__name__)
                return HttpResponseForbidden(content='SBE [API]: You do not have permissions to read "%s"!' %
                                                     object_class.__name__) if object_response else None
            logger.debug(__name__, 'Model "%s" was requested from the database!' % object_class.__name__)
            if object_id is not None:
                try:
                    object_data = object_model.filter(pk=int(object_id))
                    return HttpResponse(get_json(object_data)) if object_response else object_data
                except ValueError:
                    logger.debug(__name__, 'Requested bad value "%s" for model "%s"!' % (object_id,
                                                                                         object_class.__name__))
                    return HttpResponseBadRequest(content='SBE [API]: Bad Value: "%s"' % object_id) \
                        if object_response else None
                except object_class.DoesNotExist:
                    logger.debug(__name__, 'Requested invalid value "%s" for model "%s"!' % (object_id,
                                                                                         object_class.__name__))
                    return HttpResponseNotFound(
                        content='SBE [API]: Object with "%s" does not exist in the requested data set!' % object_id)\
                        if object_response else None
            else:
                try:
                    object_data = object_model.all()
                    if len(object_data) > object_limit:
                        object_data = object_data[(object_page * object_limit):((object_page + 1) * object_limit)]
                    return HttpResponse(get_json(object_data)) if object_response else object_data
                except object_class.DoesNotExist:
                    return HttpResponseNotFound(content='SBE [API]: There is no data in the requested data set!') \
                        if object_response else None
        else:
            logger.warning(__name__, 'Requested invalid data set model "%s"!' % object_class.__name__)
            return HttpResponseNotFound(content='SBE [API]: The requested data set does not exist!') \
                if object_response else None
    logger.warning(__name__, 'Requested non-existent data set model "%s"!' % object_class.__name__)
    return HttpResponseNotFound(content='SBE [API]: The requested data set does not exist!') \
        if object_response else None
