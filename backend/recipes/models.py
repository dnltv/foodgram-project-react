from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    """A model representing an Ingredient for a Receipt."""
    name = models.CharField(max_length=200, verbose_name='Name', required=True)
    measurement_unit = models.CharField(max_length=200, verbose_name='Unit of measurement')

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
