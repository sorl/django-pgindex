from django.db import models
from .index import ItemIndex, ItemPublIndex, ItemExpiresIndex
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


class ItemExpires(ItemBase):
    expires = models.DateTimeField()


register(Item, ItemIndex)
register(ItemPubl, ItemPublIndex)
register(ItemExpires, ItemExpiresIndex)

