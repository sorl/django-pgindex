#coding=utf-8
import datetime
import time
from django.test import TestCase
from .models import *
from pgindex.models import Index
from pgindex.helpers import search, register


LOREM = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'


class SimpleTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(title='xyz', content=LOREM)
        self.item2 = Item.objects.create(title='Lorem', content=LOREM)

    def test_create(self):
        idx = Index.objects.get_for_object(self.item)
        self.assertEqual(idx.data.pk, self.item.pk)

    def test_search(self):
        qs = search('Lorem')
        self.assertEqual(qs[0].data.pk, self.item2.pk)

    def test_delete(self):
        item = Item.objects.create(title='Ipsum', content=LOREM)
        self.assertEqual(Index.objects.count(), 3)
        item.delete()
        self.assertEqual(Index.objects.count(), 2)

    def test_url(self):
        self.assertEqual(
            self.item.get_absolute_url(),
            Index.objects.get_for_object(self.item).url,
            )

    def test_published_creation(self):
        before = Index.objects.count()
        item = ItemPubl.objects.create(title='xyz', content=LOREM)
        after = Index.objects.count()
        self.assertEqual(before, after)

    def test_expires_creation_past(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        before = Index.objects.count()
        item = ItemExpires.objects.create(title='xyz', content=LOREM, expires=past)
        after = Index.objects.count()
        self.assertEqual(before, after)

    def test_expires_creation_future(self):
        future = datetime.datetime.now() + datetime.timedelta(days=1)
        before = Index.objects.count()
        item = ItemExpires.objects.create(title='xyz', content=LOREM, expires=future)
        after = Index.objects.count()
        self.assertEqual(before + 1, after)

    def test_expires(self):
        t = datetime.datetime.now() + datetime.timedelta(microseconds=1)
        item = ItemExpires.objects.create(title='woof', content=LOREM, expires=t)
        time.sleep(0.01)
        self.assertEqual(0, search('woof').count())
        item.expires = datetime.datetime.now() + datetime.timedelta(days=1)
        item.save()
        self.assertEqual(1, search('woof').count())

