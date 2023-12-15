import os
import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from JSON file'

    def handle(self, *args, **options):

        json_file_path = os.path.join(
            'data', 'ingredients.json'
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
