import json

from django.core.exceptions import ValidationError
from django.db import models

"""
 Get all active devices for a specific user (e.g., to send them a notification)
    user_devices = UserDevice.objects.filter(username=current_username, is_active=True)
    print(f"\nFound {user_devices.count()} active devices for {current_user.username}")
    for dev in user_devices:
        print(f"  - Token: {dev.fcm_token[:15]}... ({dev.platform})")


# This would typically happen when a user logs out from a specific device.
# The client sends its device_id, and you deactivate it.
device_id_to_logout = 'ABC-123-XYZ-789'
try:
    device_to_deactivate = UserDevice.objects.get(
        user=current_user,
        device_id=device_id_to_logout
    )
    device_to_deactivate.is_active = False
    device_to_deactivate.save()
    print(f"\nDEACTIVATED device: {device_to_deactivate.device_id}")
except UserDevice.DoesNotExist:
    print(f"\nCould not find device {device_id_to_logout} to deactivate.")

"""


class UserDevice(models.Model):
    username = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255, null=True)  # aka device id

    # make platform ENUM?
    platform = models.CharField(max_length=255, null=True)  # android
    is_dashbaord_login = models.BooleanField(default=False, null=True)  # True if is Admin
    is_active = models.BooleanField(default=True, help_text="Is this device active and able to receive notifications?")

    # --- Optional Device Info ---
    os_version = models.CharField(max_length=255, null=True)  # 16
    device_model = models.CharField(max_length=255, null=True)  # S22

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A user should only have one entry per physical device_id.
        # This prevents a user from registering the same phone multiple times.
        unique_together = ("username", "uuid")
        verbose_name = "User Device"
        verbose_name_plural = "User Devices"

    def __str__(self):
        return f"{self.username}'s {self.platform} device"

    # TODO: cron job to remove stale tokens?
    # TODO: remove bad tokens when getting error from API


class FCMLog(models.Model):
    usernames = models.TextField()
    tokens = models.TextField()

    # request_payload = models.JSONField()  # What you sent
    message_title = models.CharField(max_length=200, null=True)
    message_body = models.CharField(max_length=1024, null=False)

    success_count = models.IntegerField()
    failure_count = models.IntegerField()
    responses = models.JSONField()  # Detailed results

    created_at = models.DateTimeField(auto_now_add=True)


class FCMCertificate(models.Model):
    certificate_json = models.JSONField()

    def clean(self):
        # if self.name and FCMCertificate.objects.filter(name=self.name).exists() and not self.pk:
        # raise ValidationError("Only one certificate can exist with this name.")

        if self.certificate_json:
            if isinstance(self.certificate_json, str):
                try:
                    json.loads(self.certificate_json)
                except json.JSONDecodeError:
                    raise ValidationError({"certificate_json": "Invalid JSON format."})
            # No need to seek for JSONField as it doesn't operate on file-like objects.

    def save(self, *args, **kwargs):
        self.full_clean()  # calls clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "certificate"
