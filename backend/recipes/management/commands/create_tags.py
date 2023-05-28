from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Breakfast', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Lunch', 'color': '#49B64E', 'slug': 'lunch'},
            {'name': 'Dinner', 'color': '#8775D2', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Tags are loaded.'))
