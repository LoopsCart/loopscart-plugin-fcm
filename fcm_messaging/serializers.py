from rest_framework import serializers

from .models import FCMCertificate, User


class FCMCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMCertificate
        fields = ["id", "name", "certificate_json"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "token"]
