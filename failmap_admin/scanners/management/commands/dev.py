import logging
from datetime import datetime

import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from failmap_admin.map.determineratings import DetermineRatings
from failmap_admin.scanners.models import Endpoint
from failmap_admin.organizations.models import Organization, Url
from failmap_admin.scanners.scanner_dns import ScannerDns
from failmap_admin.scanners.state_manager import StateManager
from failmap_admin.scanners.scanner_security_headers import scan_all_urls_celery, scan_headers

logger = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Development command'

    def handle(self, *args, **options):
        Command.develop_celery()
        # Command.develop_celery_advanced()
        Command.develop_celery_test_async_tasks()

    @staticmethod
    def develop_celery_test_async_tasks():
        scan_all_urls_celery()

    @staticmethod
    def develop_celery_advanced():
        url = Url.objects.all().filter(url='www.ibdgemeenten.nl').get()
        http_endpoints = Endpoint.objects.all().filter(url=url, is_dead=False, protocol='http')
        https_endpoints = Endpoint.objects.all().filter(url=url, is_dead=False, protocol='https')
        endpoints = list(http_endpoints) + list(https_endpoints)
        eps = []
        for endpoint in endpoints:
            if endpoint.is_ipv4():
                eps.append(endpoint)

        # for endpoint in eps:
        #     dispatch_scan_security_headers(endpoint)

    @staticmethod
    def develop_celery():
        from celery_test import add
        add.delay(1,2)

    @staticmethod
    def develop_security_headers_scanner():
        u = Url.objects.all().filter(url='zoeken.haarlemmermeer.nl').get()
        u = Url.objects.all().filter(url='www.ibdgemeenten.nl').get()
        scan_headers(u)


    @staticmethod
    def develop_determineratings():
        # DetermineRatings.default_ratings()
        # return

        # DetermineRatings.significant_times(organization=organization)
        # urls = Url.objects.all().filter(organization=organization)
        # for url in urls:
        #     DetermineRatings.get_url_score_modular(url)

        when = datetime(2016, 12, 31, 0, 0, tzinfo=pytz.utc)
        # when = datetime.now(pytz.utc)

        organization = Organization.objects.filter(name="Arnhem").get()
        DetermineRatings.clear_organization_and_urls(organization)
        DetermineRatings.rate_organization_urls_efficient(organization, create_history=True)
        # ratings are always different since we now also save last scan date.
        # only creates things for near midnight. Should check if today, and then save for now.
        DetermineRatings.rate_organization_efficient(organization, create_history=True)
        # create one for NOW, not this night. This is a bug :)
        DetermineRatings.rate_organization_efficient(organization)