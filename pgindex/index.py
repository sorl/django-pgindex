import datetime
import re
from abc import ABCMeta, abstractmethod
from django.db import connection, transaction
from django.utils.html import strip_tags
from pgindex.models import Index


class IndexBase(object):
    __meta__ = ABCMeta

    def __init__(self, obj):
        self.obj = obj

    @abstractmethod
    def get_data(self):
        """
        This is where you return your entry data
        """
        raise NotImplemented

    def get_expired(self):
        """
        Sets an expiration date for the index.

        Alternatives
        ------------
        * True: expired
        * False: not expired
        * A datetime.datetime object: datetime to expire
        """
        return False

    @abstractmethod
    def get_vectors(self):
        raise NotImplemented

    def get_tsvector(self):
        tsvectors = [ v.tsvector for v in self.get_vectors() ]
        return u' || '.join(tsvectors)

    def update(self):
        self.obj._index.all().delete()
        expired = self.get_expired()
        if expired:
            if expired is True or expired < datetime.datetime.now():
                # no point in indexing this
                return
        idx = Index(ts=self.get_tsvector(), expired=expired)
        idx.data = self.get_data()
        self.obj._index.add(idx)

