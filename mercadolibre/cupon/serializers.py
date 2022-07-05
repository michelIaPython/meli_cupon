# REST FRAME WORK
from rest_framework import serializers

# MODELS
from cupon.models import CuponModel


class CuponSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponModel
        fields = ("item_id", "quantity")
