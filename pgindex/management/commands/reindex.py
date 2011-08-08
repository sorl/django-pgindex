import pgindex
import sys
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from optparse import make_option
from pgindex.models import Index


class Command(BaseCommand):
    help = _('Reindex for django-pgindex')

    option_list = BaseCommand.option_list + (
        make_option('--apps',
            action='store',
            dest='apps',
            default='',
            help=_('specify apps to reindex for.'),
            ),
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help=_('reindex all apps.'),
            )
        )
    def handle(self, *args, **options):
        registry = pgindex.helpers._registry
        if options['all']:
            Index._default_manager.all().delete()
        elif options['apps']:
            apps = [ app.strip() for app in options['apps'].split(',') ]
            Index._default_manager.filter(obj_app_label__in=apps).delete()
        else:
            raise CommandError(_('No apps to reindex.'))
        for model, idx_classes in registry.iteritems():
            opts = model._meta
            if options['all'] or opts.app_label in apps:
                sys.stdout.write(_('Reindexing %s.%s') % (
                    opts.app_label, opts.object_name
                    ))
                for obj in model._default_manager.all():
                    for idx_cls in idx_classes:
                        idx = idx_cls(obj)
                        idx.update()
                        sys.stdout.write('.')
                        sys.stdout.flush()
                sys.stdout.write('OK\n')

