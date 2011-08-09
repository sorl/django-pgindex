import datetime
from pgindex.models import Index


class IndexBase(object):
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

    def get_image(self):
        """
        Get an image for the object.
        """
        return ''

    def get_data(self):
        """
        This additional data will be pickled and stored in the index model. It
        could be anything that you want to access from the index, for example
        the model instance it self.
        """
        return None

    def get_publish(self):
        """
        ``False`` means not to index this object at all
        """
        return True

    def get_start_publish(self):
        """
        Controls published stop datetime for the index.
        ``None`` means the beginning of time.
        """
        return None

    def get_stop_publish(self):
        """
        Controls published stop datetime for the index.
        ``None`` means the end of time.
        """
        return None

    def get_lang(self):
        """
        Get language code, if any
        """
        return ''

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
        stop_publish = self.get_stop_publish()
        now = datetime.datetime.now()
        lang = self.get_lang()
        if (not self.get_publish() or stop_publish and stop_publish < now):
            # no point in indexing this object
            idx = Index.objects.get_for_object(self.obj, lang=lang)
            if idx:
                idx.delete()
            return
        idx = Index.objects.get_for_object(self.obj, lang=lang, create=True)
        idx.title = self.get_title()
        idx.description = self.get_description()
        idx.image = self.get_image()
        idx.url = self.get_url()
        idx.data = self.get_data()
        idx.start_publish = self.get_start_publish()
        idx.stop_publish = stop_publish
        idx.lang = lang
        idx.save()
        idx.set_ts(self.get_tsvector())

