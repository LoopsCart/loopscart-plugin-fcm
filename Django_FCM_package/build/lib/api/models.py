import json

from django.core.exceptions import ValidationError
from django.db import models


class FCMCertificate(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A unique name for this Firebase project/certificate.",
    )
    certificate_json = models.FileField(upload_to="fcm_certificates/", null=True)

    def clean(self):
        if self.name and FCMCertificate.objects.filter(name=self.name).exists() and not self.pk:
            raise ValidationError("Only one certificate can exist with this name.")

        if self.certificate_json:
            try:
                content = self.certificate_json.read().decode("utf-8")
                json.loads(content)
            except json.JSONDecodeError:
                raise ValidationError({"certificate_file": "Invalid JSON format."})
            except UnicodeDecodeError:
                raise ValidationError({"certificate_file": "File is not UTF-8 encoded."})
            finally:
                if self.certificate_json:
                    self.certificate_json.seek(0)

    def save(self, *args, **kwargs):
        self.full_clean()  # calls clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
