from rest_framework import serializers


class CreateShipmentSerializer(serializers.Serializer):
    origin_branch_id = serializers.UUIDField()
    description = serializers.CharField(max_length=500)
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    destination_country_code = serializers.RegexField(r"^[A-Za-z]{2}$")

    def validate_destination_country_code(self, value: str) -> str:
        return value.strip().upper()


class ShipmentOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    origin_branch_id = serializers.UUIDField()
    origin_branch_name = serializers.CharField()
    description = serializers.CharField()
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    destination_country_code = serializers.CharField()
    destination_country_name = serializers.CharField()
    currency = serializers.CharField()
    status = serializers.CharField()
