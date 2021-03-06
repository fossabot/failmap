import logging
from datetime import datetime

import pytz
from django.core.management.commands.dumpdata import Command as DumpDataCommand
from django.core.serializers import serialize

from failmap.map.models import OrganizationRating, UrlRating
from failmap.organizations.models import Coordinate, Organization, OrganizationType, Promise, Url
from failmap.scanners.models import Endpoint, EndpointGenericScan, Screenshot, TlsQualysScan, UrlIp

log = logging.getLogger(__package__)


class Command(DumpDataCommand):
    help = "Create a smaller export for testing."

    FILENAME = "failmap_organization_export_{}.{options[format]}"

    APP_LABELS = ('organizations', 'scanners', 'map', 'django_celery_beat')

    # for testing it is nice to have a human editable serialization language
    FORMAT = 'yaml'

    def add_arguments(self, parser):
        parser.add_argument('organizations', type=str, nargs='+')
        # https://stackoverflow.com/questions/8203622/argparse-store-false-if-unspecified#8203679
        # https://edumaven.com/python-programming/argparse-boolean
        # --all / "all" is used by super.
        parser.add_argument('--yes', dest='yes', action='store_true')
        super(Command, self).add_arguments(parser)

    def handle(self, *app_labels, **options):
        log.info(options['yes'])

        options['format'] = self.FORMAT

        if options['output']:
            filename = options['output']
        else:
            # generate unique filename for every export
            filename = self.FILENAME.format(
                datetime.now(pytz.utc).strftime("%Y%m%d_%H%M%S"),
                options=options
            )

        objects = []

        objects += OrganizationType.objects.all()

        for organization in options['organizations']:
            organizations = Organization.objects.all().filter(name=organization)
            objects += organizations
            objects += Promise.objects.all().filter(organization__in=organizations)
            objects += Coordinate.objects.all().filter(organization__in=organizations)
            if options['yes']:
                objects += OrganizationRating.objects.all().filter(organization__in=organizations)

            urls = Url.objects.all().filter(organization__in=organizations)
            objects += urls
            objects += UrlIp.objects.all().filter(url__in=urls)
            if options['yes']:
                objects += UrlRating.objects.all().filter(url__in=urls)

            endpoints = Endpoint.objects.all().filter(url__in=urls)
            objects += endpoints
            objects += TlsQualysScan.objects.all().filter(endpoint__in=endpoints)
            objects += EndpointGenericScan.objects.all().filter(endpoint__in=endpoints)
            if options['yes']:
                objects += Screenshot.objects.all().filter(endpoint__in=endpoints)

            with open(filename, "w") as f:
                f.write(serialize(self.FORMAT, objects))

            log.info('Wrote %s', filename)
