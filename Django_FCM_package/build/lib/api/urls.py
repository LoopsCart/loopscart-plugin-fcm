from django.urls import path

from .views import (
    CertificateDetailView,
    CertificateUploadView,
    DeviceGroupView,
    SendNotificationDeviceView,
    SendNotificationGroupView,
)

urlpatterns = [
    path("upload/", CertificateUploadView.as_view(), name="upload-certificate"),
    path("certificates/", CertificateDetailView.as_view(), name="certificate-detail"),
    path("certificates/<int:pk>/", CertificateDetailView.as_view(), name="certificate-detail-pk"),
    path("device-group/", DeviceGroupView.as_view(), name="device-group"),
    path("send-notification-group/", SendNotificationGroupView.as_view(), name="send-notification-group"),
    path("send-notification-device/", SendNotificationDeviceView.as_view(), name="send-notification-device"),
]
