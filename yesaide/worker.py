from yesaide import YesaideRuntimeError


class RawWorker(object):
    """Deepest worker, root of all the interactions, only ensure that
    a sqlalchemy database session is available in `self._dbsession`."""

    def __init__(self, dbsession):
        self._dbsession = dbsession


class SupervisedWorker(RawWorker):
    """Worker intended to be used inside a foreman."""

    def __init__(self, foreman, foreman_name=None):
        RawWorker.__init__(self, foreman._dbsession)

        if not foreman_name:
            foreman_name = "_foreman"

        setattr(self, foreman_name, foreman)


class MappingManagingWorker(SupervisedWorker):
    """Worker intended to be used inside a foreman, to take care of a
    specific SQLAlchemy mapping.

    """

    def __init__(
        self,
        foreman=None,
        foreman_name=None,
        managed_sqla_map=None,
        managed_sqla_map_name=None,
        id_type=None,
    ):
        SupervisedWorker.__init__(self, foreman, foreman_name)

        self._sqla_map = managed_sqla_map
        self._sqla_map_name = managed_sqla_map_name

        if id_type and id_type not in ("id", "uuid"):
            raise AttributeError("Wrong `id_type`.")
        self._with_id = id_type == "id" or hasattr(self._sqla_map, "id")
        self._with_uuid = id_type == "uuid" or hasattr(self._sqla_map, "uuid")

    def _get(self, sqla_obj_id=None, sqla_obj=None, options=None, **kwargs):
        """Unified internal get for a SQLAlchemy object present in
        `sqla_obj_id` or `sqla_obj`, whose type is `self._sqla_map`.

        Keyword arguments:
            sqla_obj_id -- id (could be a "real" integer id or an uuid)
                           of the requested object
            sqla_obj -- SQLAlchemy object (internal use)
            options -- list of SQLAchemy options to apply to the SQL
                       request

        """
        if sqla_obj:
            if not isinstance(sqla_obj, self._sqla_map):
                raise ValueError("`sqla_obj` doesn't match with the " "registered type.")
            return sqla_obj

        elif sqla_obj_id:
            query = self.base_query(**kwargs)

            if self._with_id:
                query = query.filter(self._sqla_map.id == sqla_obj_id)
            elif self._with_uuid:
                query = query.filter(self._sqla_map.uuid == sqla_obj_id)
            else:
                raise YesaideRuntimeError("Can't determine id field.")

            if options is None:
                options = []

            return query.options(*options).one()

        raise TypeError("No criteria provided.")

    def get(self, sqla_obj_id=None, sqla_obj=None, options=None, **kwargs):
        """Unified external get for an object present in `sqla_obj_id`
        or `sqla_obj`.

        See also `ObjectManagingWorker._get()`.

        """
        if not sqla_obj_id and not sqla_obj:
            if not self._sqla_map_name:
                raise TypeError("No criteria provided.")

            sqla_obj_key = "{}".format(self._sqla_map_name)
            if self._with_id:
                sqla_obj_id_key = "{}_id".format(self._sqla_map_name)
            elif self._with_uuid:
                sqla_obj_id_key = "{}_uuid".format(self._sqla_map_name)
            else:
                raise YesaideRuntimeError("Can't determine id field.")

            if sqla_obj_key in kwargs:
                sqla_obj = kwargs[sqla_obj_key]

            elif sqla_obj_id_key in kwargs:
                sqla_obj_id = kwargs[sqla_obj_id_key]

            else:
                raise TypeError("No criteria provided.")

        return self._get(sqla_obj_id, sqla_obj, options, **kwargs)

    def base_query(self, **kwargs):
        """Base sqlalchemy query for this kind of object

        Subclasses can override this method to implement custom logic
        (filtering inactive objects, security features, etc).
        """
        return self._dbsession.query(self._sqla_map)

    def serialize(self, items, **kwargs):
        """Transform the given item into an easily serializable item.

        Most of the time it transforms a sqlalchemy mapped object into a
        dict with strings as keys and strings as values.

        A simple implementation would be:

            return {'id': item.id}

        """
        raise NotImplementedError("Subclasses must implement `serialize()`.")
