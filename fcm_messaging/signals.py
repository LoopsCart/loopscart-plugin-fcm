from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FCMCertificate, FCMLog


@receiver(post_save, sender=FCMCertificate)
def log_fcm_certificate_changes(sender, instance, created, **kwargs):
    if created:
        FCMLog.objects.create(
            usernames="N/A",
            tokens="N/A",
            message_title="FCMCertificate was created",
            success_count=0,
            failure_count=0,
            responses=instance.certificate_json,
        )
    else:
        FCMLog.objects.create(
            usernames="N/A",
            tokens="N/A",
            message_title="FCMCertificate was updated",
            success_count=0,
            failure_count=0,
            responses=instance.certificate_json,
        )
