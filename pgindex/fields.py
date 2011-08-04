from django.db import models


class TSVectorField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'null': True,
            'editable': False,
            'serialize': False,
        })
        super(TSVectorField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """
        It is not possible to set the vector value this way, you need to
        execute SQL using UPDATE.
        """
        return None

    def db_type(self, connection=None):
        return 'tsvector'

    def south_field_triple(self):
        from south.modelsinspector import introspector
        cls = self.__class__
        dot_name = '%s.%s' % (cls.__module__ , cls.__name__)
        args, kwargs = introspector(self)
        return (dot_name, args, kwargs)

