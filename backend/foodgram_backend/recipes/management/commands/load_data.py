import csv
from recipes.models import Ingredient
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load data from CSV file'

    def handle(self, *args, **kwargs):
        with open('ingredients.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Ingredient.objects.create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
