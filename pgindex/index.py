import datetime
import re
from django.utils.encoding import force_unicode
from abc import ABCMeta, abstractmethod
from django.db import connection, transaction
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from pgindex.models import Index


class IndexBase(object):
    __meta__ = ABCMeta

    def __init__(self, obj):
        self.obj = obj

    def get_title(self):
        """
        Get the object index title.
        """
        return self.obj.title

    def get_description(self):
        """
        Get the object index description.
        """
        return ''

    def get_url(self):
        """
        Get the object url.
        """
        return self.obj.get_absolute_url()

    def get_data(self):
        """
        This additional data will be pickled and stored in the index model. It
        could be anything that you want to access from the index, for example
        the model instance it self.
        """
        return None

    def get_published(self):
        """
        Controls if the object is published for index.
        """
        return True

    def get_expires(self):
        """
        Controls published end datetime for the index.
        ``None`` means the end of time.
        """
        return None

    @abstractmethod
    def get_vectors(self):
        """
        This is weher you return your search vectors. It should be an iterable
        with instances of ``pgindex.helpers.Vector``.
        """
        raise NotImplemented

    def get_tsvector(self):
        tsvectors = [ v.tsvector for v in self.get_vectors() ]
        return u' || '.join(tsvectors)

    def update(self):
        expires = self.get_expires()
        now = datetime.datetime.now()
        if (not self.get_published() or expires and expires < now):
            # the object should not be indexed
            idx = Index.objects.get_for_object(self.obj)
            if idx:
                idx.delete()
            return
        idx = Index.objects.get_for_object(self.obj, create=True)
        idx.title = self.get_title()
        idx.description = self.get_description()
        idx.url = self.get_url()
        idx.data = self.get_data()
        idx.save()
        idx.set_ts(self.get_tsvector())

