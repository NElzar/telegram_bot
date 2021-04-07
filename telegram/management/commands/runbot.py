from django.core.management.base import BaseCommand
from telegram.api_telegram import run_telegram_bot


class Command(BaseCommand):
    def handle(self, **options):
        run_telegram_bot()