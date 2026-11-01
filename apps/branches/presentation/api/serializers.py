from rest_framework import serializers


class CreateBranchSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=120)
    max_weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    is_active = serializers.BooleanField(default=True)


class UpdateBranchSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=120)
    max_weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    is_active = serializers.BooleanField(required=True)

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({"unknown_fields": sorted(unknown)})
        if not attrs:
            raise serializers.ValidationError("Envía al menos un campo para actualizar.")
        return attrs


class BranchOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    city = serializers.CharField()
    max_weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    is_active = serializers.BooleanField()
