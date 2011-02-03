import datetime
import re
from abc import ABCMeta, abstractmethod
from django.db import connection, transaction
from django.utils.html import strip_tags


class IndexBase(object):
    __meta__ = ABCMeta

    def __init__(self, obj):
        self.obj = obj

    def get_url(self):
        return self.obj.get_absolute_url()

    def get_title(self):
        return self.obj.title

    def get_app(self):
        return self.obj._meta.app_label

    @abstractmethod
    def get_summary(self):
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
        params = {
            'ts': self.get_tsvector(),
            'url': self.get_url(),
            'title': self.get_title(),
            'app': self.get_app(),
            'summary': self.get_summary(),
            'expired': self.get_expired() or None,
        }
        index = self.obj._index.create(**params)

