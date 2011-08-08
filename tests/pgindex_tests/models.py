from django.db import models
from .index import ItemIndex, ItemIndexSv, ItemPublIndex, ItemPublStartIndex, ItemPublStopIndex
from pgindex import register


class ItemBase(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    content_sv = models.TextField()

    def get_absolute_url(self):
        return '/item/'

    class Meta:
        abstract = True


class Item(ItemBase):
    pass

class ItemPubl(ItemBase):
    pass

class ItemPublStart(ItemBase):
    start_publish = models.DateTimeField(null=True)


class ItemPublStop(ItemBase):
    stop_publish = models.DateTimeField(null=True)


register(Item, ItemIndex)
register(Item, ItemIndexSv)
register(ItemPubl, ItemPublIndex)
register(ItemPublStart, ItemPublStartIndex)
register(ItemPublStop, ItemPublStopIndex)
