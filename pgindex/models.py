#coding=utf-8
import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection, transaction
from django.db.models import Q
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from pgindex.fields import TSVectorField


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
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    app = models.CharField(max_length=50)
    summary = models.TextField(blank=True)
    expired = models.DateTimeField(db_index=True, null=True)

    objects = IndexManager()
    publ = IndexPublManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

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

    def get_absolute_url(self):
        return self.url

    class Meta:
        unique_together = (('content_type', 'object_id'),)

