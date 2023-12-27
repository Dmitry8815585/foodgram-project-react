import json
import os

from django.core.management import CommandError
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file_path',
            type=str,
            help='Path to the JSON file with ingredients data'
        )

    def handle(self, *args, **options):
        json_file_path = options['json_file_path']

        if not os.path.isfile(json_file_path):
            raise CommandError(
                f'The specified file "{json_file_path}" does not exist.'
            )

        with open(json_file_path, 'r') as file:
            data = json.load(file)

            for item in data:
                ingredient = Ingredient.objects.create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Ingredient "{ingredient}" created')
                )

        self.stdout.write(self.style.SUCCESS('Import completed successfully'))
