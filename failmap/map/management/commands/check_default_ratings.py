import logging

from django.core.management.base import BaseCommand

from failmap.map.rating import default_organization_rating

logger = logging.getLogger(__package__)


class Command(BaseCommand):
    help = 'Gives a default rating to organizations. If they don\'t have one.'

    def handle(self, *args, **options):
        default_organization_rating()
