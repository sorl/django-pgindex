#coding=utf-8
import datetime
import re
from django.contrib.contenttypes import generic
from django.db.models import signals
from pgindex.models import Index


_registry = {}
non_alpha_pat = re.compile(r'[\.\^\$\*\+\?\{\[\]\}\\\\|\(\)!"#%&/=\',;:]')


def register(model, search_cls):
    generic.GenericRelation(Index).contribute_to_class(model, '_index')
    _registry[model] = search_cls
    signals.post_save.connect(update_index, sender=model, weak=False)


def update_index(sender, instance, **kwargs):
    index_cls = _registry[sender]
    index = index_cls(instance)
    index.update()


def search(q, weight=None):
    """
    Helper function to search the index
    """
    if weight is None:
        weight = weight or '{0.1, 0.2, 0.4, 1.0}' # default weight in postgres
    extra = {
        'select': {
            'rank': ("ts_rank_cd('%s', ts, plainto_tsquery(%s), 0)" % weight)
        },
        'select_params': (q,),
        'where': ('ts @@ plainto_tsquery(%s)',),
        'params': (q,),
        'order_by': ('-rank',)
    }
    return Index.publ.extra(**extra)


class Vector(object):
    weight = 'B'
    lang = 'swedish'
    clean = True

    def __init__(self, value, weight=None, lang=None, clean=None):
        if weight is not None:
            self.weight = weight
        if lang is not None:
            self.lang = lang
        if clean is not None:
            self.clean = clean
        if self.clean is True:
            # clean out html, django template vars, django comments
            for pat in [r'<[^>]*?>', r'{{[^}]*?}}', r'{#[^#}]*?#}']:
                value = re.sub(pat, '', value)
            # clean out not characters, ' and % can break stuff
            value = non_alpha_pat.sub('', value)
        self.value = value

    @property
    def tsvector(self):
        return u"setweight(to_tsvector('%s', E'%s'), '%s')" % (self.lang, self.value, self.weight)

