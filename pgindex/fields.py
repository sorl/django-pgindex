import cPickle
from django.db import models


class SouthMixin(object):
    """
    A south introspection Mixin
    """
    def south_field_triple(self):
        from south.modelsinspector import introspector
        cls_name = '%s.%s' % (self.__class__.__module__ , self.__class__.__name__)
        args, kwargs = introspector(self)
        return (cls_name, args, kwargs)


class TSVectorField(SouthMixin, models.Field):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'null': True,
            'editable': False,
            'serialize': False,
        })
        super(TSVectorField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'tsvector'



class PickleDescriptor(object):
    """
    PickleDescriptor field.
    Use like::

        class MyModel(models.Model):
            _data = models.TextField(null=True)
            data = PickleDescriptor('_data')
            ...
    """
    def __init__(self, field_name):
        self.field_name = field_name
        self.cache_name = '%s_cache' % field_name

    def __get__(self, obj, owner):
        if not hasattr(obj, self.cache_name):
            data = getattr(obj, self.field_name)
            if data is None:
                value = None
            else:
                value = cPickle.loads(str(data).decode('base64'))
            setattr(obj, self.cache_name, value)
        return getattr(obj, self.cache_name)

    def __set__(self, obj, value):
        setattr(obj, self.cache_name, value)
        if value is None:
            data = None
        else:
            data = cPickle.dumps(value).encode('base64')
        setattr(obj, self.field_name, data)

