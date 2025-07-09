import json

from django.core.exceptions import ValidationError
from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255)


class FCMCertificate(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A unique name for this Firebase project/certificate.",
    )
    certificate_json = models.JSONField()

    def clean(self):
        if self.name and FCMCertificate.objects.filter(name=self.name).exists() and not self.pk:
            raise ValidationError("Only one certificate can exist with this name.")

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
        return self.name
