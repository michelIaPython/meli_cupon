from django.db import models


class CuponModel(models.Model):
    item_id = models.CharField(max_length=35, null=False, blank=False)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False, blank=False)
    quantity = models.BigIntegerField()

    class Meta:
        db_table = "meli_cupon"
