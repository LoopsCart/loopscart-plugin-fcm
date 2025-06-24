from rest_framework import serializers

from .models import FCMCertificate


class FCMCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMCertificate
        fields = ["id", "name", "certificate_json"]
