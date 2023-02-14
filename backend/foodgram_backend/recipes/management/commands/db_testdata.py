import csv
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = ('../../data/ingredients.csv')
        print(f'импорт из {path}')

        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)
                if Ingredient.objects.filter(name=row[0]).exists():
                    Ingredient.objects.filter(name=row[0]).delete()
                    print(f'Строка с {row[0]} существует, строка будет перезаписана')
                ingredient = Ingredient(
                    name=row[0],
                    measurement_unit=row[1]
                )
                ingredient.save()
        print('Импорт завершен')