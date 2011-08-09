#coding=utf-8
import re
from django.db.models import signals
from pgindex.models import Index


_registry = {}
non_alpha_pat = re.compile(r'[\.\^\$\*\+\?\{\[\]\}\\\\|\(\)!"#%&/=\',;:]')


def register(model, idx_cls):
    idx_classes = _registry.setdefault(model, [])
    if idx_cls not in idx_classes:
        idx_classes.append(idx_cls)
    signals.post_save.connect(update_index, sender=model)
    signals.post_delete.connect(delete_index, sender=model)


def delete_index(sender, instance, **kwargs):
    idx = Index.objects.filter_for_object(instance)
    if idx:
        idx.delete()


def update_index(sender, instance, **kwargs):
    idx_classes = _registry[sender]
    for idx_cls in idx_classes:
        idx = idx_cls(instance)
        idx.update()


def search(q, weight=None, dictionary='simple'):
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
    return Index.publ.extra(**extra)


class Vector(object):
    weight = 'B'
    dictionary = 'simple'
    clean = True

    def __init__(self, value, weight=None, dictionary=None, clean=None):
        if weight is not None:
            self.weight = weight
        if dictionary is not None:
            self.dictionary = dictionary
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
        return u"setweight(to_tsvector('%s', E'%s'), '%s')" % (
            self.dictionary, self.value, self.weight
            )

