#coding=utf-8
import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection, transaction
from django.db.models import Q
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from pgindex.fields import TSVectorField
from cerial import PickleField
from stringfield import StringField


class IndexManager(models.Manager):
    pass

class IndexPublManager(IndexManager):
    def get_query_set(self):
        qs = super(IndexPublManager, self).get_query_set()
        return qs.filter(
            Q(expired__gte=datetime.datetime.now()) |
            Q(expired__isnull=True)
            )

class Index(models.Model):
    ts = TSVectorField()
    data = PickleField()
    start_publish = models.DateTimeField(db_index=True, null=True)
    end_publish = models.DateTimeField(db_index=True, null=True)

    objects = IndexManager()
    publ = IndexPublManager()

    obj_app_label = StringField()
    obj_model_name = StringField()
    obj_pk = StringField()

    def save(self, **kwargs):
        ts = self.ts
        self.ts = None
        super(Index, self).save(**kwargs)
        self.set_ts(ts)

    def set_ts(self, ts):
        """
        Performs *raw* update on ts
        """
        ts = smart_str(ts)
        sql = "UPDATE %s SET ts = %s WHERE id = %s;" % (
            self._meta.db_table, ts, self.pk
            )
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()

    class Meta:
        unique_together = (('obj_app_label', 'obj_model_name', 'obj_pk'),)

