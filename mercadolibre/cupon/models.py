from django.db import models


class CuponModel(models.Model):
    """
    This is the model for the API it contais three fields

    item_id
    price
    quantity

    the table names meli_cupon
    """

    item_id = models.CharField(max_length=35, null=False, blank=False)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False, blank=False)
    quantity = models.BigIntegerField(default=0)

    class Meta:
        db_table = "meli_cupon"

    def __str__(self):
        return self.item_id
