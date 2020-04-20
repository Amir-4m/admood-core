from rest_framework import serializers


class MediumSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = instance[0]
        data["title"] = instance[1]
        return data
