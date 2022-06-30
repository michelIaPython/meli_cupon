from rest_framework import serializers


class CuponSerializer(serializers.Serializer):
    item_id = serializers.CharField()
    price = serializers.FloatField()
