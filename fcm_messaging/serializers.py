from rest_framework import serializers

from .models import FCMCertificate, FCMLog, UserDevice


class FCMCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMCertificate
        fields = ["certificate_json", "firebase_config", "vapid_key"]


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = ["username", "token", "uuid", "platform", "is_dashboard_login", "is_active", "os_version", "device_model"]


class FCMLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMLog
        fields = ["usernames", "tokens", "message_title", "message_body", "success_count", "failure_count", "responses", "created_at"]
