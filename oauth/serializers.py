from rest_framework import serializers


class StateCodeSerializer(serializers.Serializer):
    state = serializers.CharField()
    code = serializers.CharField()
