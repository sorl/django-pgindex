from django.db import models
from .index import ItemIndex, ItemPublIndex, ItemPublStartIndex, ItemPublStopIndex
from pgindex import register


class ItemBase(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

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
register(ItemPubl, ItemPublIndex)
register(ItemPublStart, ItemPublStartIndex)
register(ItemPublStop, ItemPublStopIndex)
