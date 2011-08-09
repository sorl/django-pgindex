#coding=utf-8
import datetime
import time
from django.test import TestCase
from .models import *
from pgindex.models import Index
from pgindex.helpers import search


LOREM = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
LOREM_SV = u'Femton goa gubbar ifrån Göteborg, ingen hittade ut'


class SimpleTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(title='xyz', content=LOREM,
            content_sv=LOREM_SV)

    def test_common_words(self):
        item = Item.objects.create(title='the a me you can')
        result = search('the a me you can').filter(lang='')
        self.assertEqual(1, result.count())

    def test_create(self):
        idx = Index.objects.get_for_object(self.item)
        self.assertEqual(idx.data.pk, self.item.pk)

    def test_search(self):
        qs = search('Lorem')
        item = Item.objects.create(title='Lorem', content=LOREM)
        self.assertEqual(qs[0].data.pk, item.pk)

    def test_lang(self):
        qs = search('ut')
        idx_sv = qs.filter(lang='sv')
        self.assertEqual(qs.count(), 2)
        self.assertEqual(idx_sv.count(), 1)

    def test_delete(self):
        before = Index.objects.count()
        item = Item.objects.create(title='Ipsum', content=LOREM)
        # Two new indexes are created, ItemIndex and ItemIndexSv
        self.assertEqual(before + 2, Index.objects.count())
        item.delete()
        self.assertEqual(before, Index.objects.count())

    def test_url(self):
        self.assertEqual(
            self.item.get_absolute_url(),
            Index.objects.get_for_object(self.item).url,
            )

    def test_publish(self):
        before = Index.objects.all().count()
        item = ItemPubl.objects.create(title='invisible', content=LOREM)
        after = Index.objects.all().count()
        self.assertEqual(before, after)

    def test_start_publish_creation(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        before = Index.objects.count()
        item = ItemPublStart.objects.create(title='xyz', content=LOREM)
        after = Index.objects.count()
        self.assertEqual(before + 1, after)

    def test_end_publish_creation_past(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        before = Index.objects.count()
        item = ItemPublStop.objects.create(title='xyz', content=LOREM, stop_publish=past)
        after = Index.objects.count()
        self.assertEqual(before, after)

    def test_end_publish_creation_future(self):
        future = datetime.datetime.now() + datetime.timedelta(days=1)
        before = Index.objects.count()
        item = ItemPublStop.objects.create(title='xyz', content=LOREM, stop_publish=future)
        after = Index.objects.count()
        self.assertEqual(before + 1, after)

    def test_start_publish(self):
        future = datetime.datetime.now() + datetime.timedelta(days=1)
        item = ItemPublStart.objects.create(title='r0x', content=LOREM, start_publish=future)
        self.assertEqual(0, search('r0x').count())
        item.start_publish = datetime.datetime.now() - datetime.timedelta(days=1)
        item.save()
        self.assertEqual(1, search('r0x').count())

    def test_end_publish(self):
        t = datetime.datetime.now() + datetime.timedelta(microseconds=1)
        item = ItemPublStop.objects.create(title='woof', content=LOREM, stop_publish=t)
        time.sleep(0.01)
        self.assertEqual(0, search('woof').count())
        item.stop_publish = datetime.datetime.now() + datetime.timedelta(days=1)
        item.save()
        self.assertEqual(1, search('woof').count())

