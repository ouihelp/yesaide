# -*- coding: utf-8 -*-
import inspect

from voluptuous import Schema

from zombase.database import MetaBase


class RawWorker(object):
    """Deepest worker, root of all the interactions, only ensure there
    a sqlalchemy database session is available in `self._dbsession`."""

    def __init__(self, dbsession, check_sanity=True):
        if check_sanity and not hasattr(dbsession, 'cache'):
            raise ValueError(
                'Cache region not associated w/ database session.')

        self._dbsession = dbsession


class SupervisedWorker(RawWorker):
    """Worker intended to be used inside a foreman."""

    def __init__(self, foreman, foreman_name=None):
        RawWorker.__init__(self, foreman._dbsession)

        if not foreman_name:
            foreman_name = '_foreman'

        setattr(self, foreman_name, foreman)


class ObjectManagingWorker(SupervisedWorker):
    """Worker intended to be used inside a foreman, to take care of a
    specific sqlalchemy mapping.

    """

    def __init__(self, foreman=None, foreman_name=None, managed_object=None,
                 managed_object_name=None):
        SupervisedWorker.__init__(self, foreman, foreman_name)

        self._managed_object = managed_object
        self._managed_object_name = managed_object_name

    def _get(self, instance_id=None, instance=None):
        """Unified internal get for an object present in `instance_id`
        or `instance`, whose type is `self._managed_object`.

        Keyword arguments:
            instance_id -- id of the requested object
            instance -- object (internal use)

        """
        if instance:
            if not isinstance(instance, type):
                raise AttributeError('`instance` doesn\'t match with the '
                                     'registered type.')
            return instance

        elif instance_id:
            return self._dbsession.query(type)\
                .filter(type.id == instance_id)\
                .one()

        raise TypeError('No criteria provided.')

    def _update(self, instance=None, schema=None, **kwargs):
        """Update an `instance`. Return False if there is no update and
        True otherwise.

        Do not raise error if too many arguments are given.

        Do not commit the database session.

        Keyword arguments:
            instance -- instance to update
            schema -- voluptuous schema to perform data validation

        """
        if not instance:
            raise TypeError('`instance` not provided.')

        if not schema:
            raise TypeError('`schema` not provided.')

        if not isinstance(schema, Schema):
            raise AttributeError('`schema` must be a voluptuous schema.')

        # Explicitely cast to string properties which come from schema
        # to deal with `voluptuous.Required` stuff.
        schema_keys = set([str(k) for k in schema.schema])

        obj_current_dict = {
            k: getattr(instance, k) for k in schema_keys
            if not getattr(instance, k) is None
        }
        obj_update_dict = obj_current_dict.copy()

        to_update = schema_keys.intersection(kwargs.keys())

        for item in to_update:
            obj_update_dict[item] = kwargs[item]

        obj_update_dict = schema(obj_update_dict)

        for item in to_update:
            setattr(instance, item, obj_update_dict[item])

        return obj_update_dict != obj_current_dict

    def _resolve_id(self, a_dict, schema, allow_none_id=False):
        """Return a dict fulfilled with the missing objects according to
        the given dict (in `a_dict`) and `schema`.

        Will fetch `instance` if `instance_id` is in the dict keys, if
        `instance` is accepted by the schema and is supposed to be a
        sqlalchemy mapping.

        Additionnally if `instance_id` is not in the schema, it will be
        removed from the dict.

        If `allow_none_id` is true, passing `instance_id` with value
        'None' or '""' (empty string) will result in setting `instance`
        to 'None'.

        """
        _a_dict = a_dict.copy()

        for key, v in schema.schema.iteritems():
            key_id = '{}_id'.format(key)

            if (not key in _a_dict.keys() and inspect.isclass(v)
                    and issubclass(v, MetaBase) and key_id in _a_dict.keys()):

                val_id = _a_dict.get(key_id)
                if not val_id and allow_none_id:
                    val = None

                else:
                    val = self._dbsession.query(v)\
                        .filter(v.id == val_id).one()

                _a_dict[str(key)] = val
                if not key_id in schema.schema:
                    _a_dict.pop(key_id)

        return _a_dict

    def get(self, instance_id=None, instance=None, **kwargs):
        """Unified external get for an object present in `instance_id`
        or `instance`.

        See also `ObjectManagingWorker._get()`.

        """
        if not instance_id and not instance:
            if not self._managed_object_name:
                raise TypeError('No criteria provided.')

            instance_key = '{}'.format(self._managed_object_name)
            instance_id_key = '{}_id'.format(self._managed_object_name)

            if instance_key in kwargs:
                instance = kwargs[instance_key]

            elif instance_id_key in kwargs:
                instance_id = kwargs[instance_id_key]

        return self._get(instance_id, instance)

    def find(self):
        """Return a query to fetch multiple objects."""
        return self._dbsession.query(self._managed_object)

    def serialize(self, items, **kwargs):
        """Transform the given list of `items` into an easily
        serializable list.

        Requires `self.serialize_one()` to be implemented. See this
        method and `self._serialize_one()` for informations about
        `kwargs`.

        """
        serialized = []
        for item in items:
            serialized.append(self.serialize_one(item, **kwargs))
        return serialized

    def _serialize_one(self, serialized, item, **kwargs):
        """Execute functions in `kwargs` with `item` as argument and add
        the results to `serialized`.

        See `self._serialize_one()` for more explanations.

        """
        for key in kwargs:
            serialized[key] = kwargs[key](item)

        return serialized

    def serialize_one(self, item, **kwargs):
        """Transform the given item into an easily serializable item.

        Most of the time it transforms a sqlalchemy mapped object into a
        dict with strings as keys and strings as values.

        Additional functions may be passed in `kwargs`, their results
        will be added to the serialized object once they have been
        executed with the item as single argument. Eg (with key=func):

            result[key] = func(item)

        A simple implementation would be:

            serialized = {'id': item.id}
            return self._serialize_one(serialized, item, **kwargs)

        Subclasses must implement this method to enable
        `self.serialize()`.

        """
        raise NotImplementedError