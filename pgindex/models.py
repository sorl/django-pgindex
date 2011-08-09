#coding=utf-8
import datetime
from cerial import PickleField
from django.db import models, connection, transaction
from django.db.models import Q, signals
from django.utils.encoding import force_unicode
from django.utils.encoding import smart_str
from pgindex.fields import TSVectorField
from stringfield import StringField


class IndexManager(models.Manager):
    def filter_for_object(self, obj):
        opts = obj._meta
        params = {
            'obj_app_label': force_unicode(opts.app_label),
            'obj_model_name': force_unicode(opts.object_name),
            'obj_pk': force_unicode(obj.pk),
            }
        return self.get_query_set().filter(**params)

    def get_for_object(self, obj, lang='', create=False):
        opts = obj._meta
        params = {
            'obj_app_label': force_unicode(opts.app_label),
            'obj_model_name': force_unicode(opts.object_name),
            'obj_pk': force_unicode(obj.pk),
            'lang': lang,
            }
        try:
            return self.get_query_set().get(**params)
        except self.model.DoesNotExist:
            if create:
                params.update({
                    'obj_model_verbose_name': force_unicode(opts.verbose_name),
                    'obj_model_verbose_name_plural': force_unicode(opts.verbose_name_plural),
                })
                return self.create(**params)

class IndexPublManager(IndexManager):
    def get_query_set(self):
        qs = super(IndexPublManager, self).get_query_set()
        now = datetime.datetime.now()
        return qs.filter(
            (Q(start_publish__isnull=True) | Q(start_publish__lte=now)) &
            (Q(stop_publish__isnull=True) | Q(stop_publish__gte=now))
            )

class Index(models.Model):
    title = StringField()
    description = models.TextField(blank=True)
    url = StringField()
    image = models.ImageField(upload_to='index', blank=True)
    data = PickleField(null=True)
    ts = TSVectorField()
    start_publish = models.DateTimeField(db_index=True, null=True)
    stop_publish = models.DateTimeField(db_index=True, null=True)
    # generic foreign key kind of.
    obj_app_label = StringField()
    obj_model_name = StringField()
    obj_pk = StringField()
    lang = StringField()

    obj_model_verbose_name = StringField()
    obj_model_verbose_name_plural = StringField()

    objects = IndexManager()
    publ = IndexPublManager()

    def get_absolute_url(self):
        return self.url

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
        unique_together = (('obj_app_label', 'obj_model_name', 'obj_pk', 'lang'),)


def create_index(app, created_models, verbosity, **kwargs):
    if Index in created_models:
        cursor = connection.cursor()
        opts = Index._meta
        sql = "CREATE INDEX pgindex_ts_idx ON %s USING gin(ts)" % opts.db_table
        cursor.execute(sql)
        transaction.commit_unless_managed()

signals.post_syncdb.connect(
    create_index,
    sender=models,
    dispatch_uid="pgindex.models.create_index"
    )

