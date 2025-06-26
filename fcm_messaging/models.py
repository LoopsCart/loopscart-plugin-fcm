import json

from django.core.exceptions import ValidationError
from django.db import models

# When saving a certificate:
# 1. The `certificate_json` FileField will store the file content in Django's configured media storage (e.g., local filesystem, S3).
#    The field itself will store a path or reference to the file.
# 2. To use the JSON data, you retrieve the FCMCertificate object and access its `certificate_json` attribute.
#    This attribute will be a Django File object.
# 3. Read the content of the File object, decode it (assuming UTF-8), and parse it as JSON.
#
# Example of retrieving and using the certificate:
#
# from .models import FCMCertificate
# import json
# import firebase_admin
# from firebase_admin import credentials
#
# try:
#     fcm_cert_obj = FCMCertificate.objects.get(name="your_cert_name")
#     certificate_file = fcm_cert_obj.certificate_json
#
#     # Ensure the file is loaded and seek to the beginning if it was already read
#     if certificate_file:
#         certificate_file.seek(0)
#         cert_content = certificate_file.read().decode('utf-8')
#         cert_data = json.loads(cert_content)
#
#         # Initialize Firebase Admin SDK with the certificate data
#         # Check if Firebase app is already initialized to avoid re-initialization errors
#         if not firebase_admin._apps:
#             cred = credentials.Certificate(cert_data)
#             firebase_admin.initialize_app(cred)
#             print("Firebase Admin SDK initialized successfully.")
#         else:
#             print("Firebase Admin SDK already initialized.")
#
# except FCMCertificate.DoesNotExist:
#     print("FCM Certificate not found.")
# except (json.JSONDecodeError, UnicodeDecodeError) as e:
#     print(f"Error processing certificate file: {e}")
# except Exception as e: # Catch other potential Firebase initialization errors
#     print(f"Error initializing Firebase Admin SDK: {e}")


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
