from django.db import models


class Ingredient(models.Model):
    """A model representing an Ingredient for a Receipt."""
    name = models.CharField(max_length=200, verbose_name='Name')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Unit of measurement'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
