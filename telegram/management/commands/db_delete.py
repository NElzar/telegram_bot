from django.core.management.base import BaseCommand
from telegram.news_api import delete_all


class Command(BaseCommand):
    def handle(self, **options):
        delete_all()