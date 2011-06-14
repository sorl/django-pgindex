from django.db import models


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

    def south_field_triple(self):
        from south.modelsinspector import introspector
        cls = self.__class__
        dot_name = '%s.%s' % (cls.__module__ , cls.__name__)
        args, kwargs = introspector(self)
        return (dot_name, args, kwargs)

