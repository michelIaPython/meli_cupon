# REST FRAME WORK
from rest_framework import serializers

# MODELS
from cupon.models import CuponModel


class CuponSerializer(serializers.ModelSerializer):
    """
    This is the serializer of the API and return only two fields item_id, quantity
    """

    class Meta:
        model = CuponModel
        fields = ("item_id", "quantity")
