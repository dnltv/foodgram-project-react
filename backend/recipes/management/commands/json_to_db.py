import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag
from users.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="file path")

    def handle(self, *args, **options):
        file_path = options["path"]

        with open(file_path, encoding='utf-8') as f:
            jsondata = json.load(f)
            if 'color' in jsondata[0]:
                for line in jsondata:
                    Tag.objects.create(
                        name=line['name'],
                        color=line['color'],
                        slug=line['slug'],
                    )
            elif 'measurement_unit' in jsondata[0]:
                for line in jsondata:
                    Ingredient.objects.create(
                        name=line['name'],
                        measurement_unit=line['measurement_unit']
                    )
            elif 'email' in jsondata[0]:
                for line in jsondata:
                    User.objects.create(
                        email=line['email'],
                        username=line['username'],
                        first_name=line['first_name'],
                        last_name=line['last_name'],
                        password=line['password'],
                    )
