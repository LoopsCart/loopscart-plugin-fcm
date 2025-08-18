from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FCMCertificate, FCMLog


@receiver(post_save, sender=FCMCertificate)
def log_fcm_certificate_changes(sender, instance, created, **kwargs):
    log_message = "FCMCertificate was created" if created else "FCMCertificate was updated"
    FCMLog.objects.create(
        usernames="N/A",
        tokens="N/A",
        message_title=log_message,
        success_count=0,
        failure_count=0,
        responses={
            "certificate_json": instance.certificate_json,
            "firebase_config": instance.firebase_config,
            "vapid_key": instance.vapid_key,
        },
    )
