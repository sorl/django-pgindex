from django.db import models, connection, transaction
from django.utils.encoding import smart_str
from pgindex.fields import TSVectorField


class IndexManager(models.Manager):
    def search(self, q, weight=None, dictionary='simple'):
        """
        Helper function to search the index
        """
        if weight is None:
            weight = '{0.1, 0.2, 0.4, 1.0}' # default weight in postgres
        extra = {
            'select': {
                'rank': ("ts_rank_cd('%s', ts, plainto_tsquery(%%s), 0)" % weight)
            },
            'select_params': (q,),
            'where': ("ts @@ plainto_tsquery('%s', %%s)" % dictionary,),
            'params': (q,),
            'order_by': ('-rank',)
        }
        return self.extra(**extra)


class IndexModel(models.Model):
    ts = TSVectorField()

    index = IndexManager()

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

    def get_vectors(self):
        raise NotImplemented

    def save(self, **kwargs):
        super(IndexModel, self).save(**kwargs)
        tsvectors = [ v.tsvector for v in self.get_vectors() ]
        ts = u' || '.join(tsvectors)
        self.set_ts(ts)

    class Meta:
        abstract = True

