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

