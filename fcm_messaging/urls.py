from django.urls import path

from .views import (
    CertificateDetailView,
    CertificateUploadView,
    DeviceGroupView,
    SendNotificationDeviceView,
    SendNotificationGroupView,
)

urlpatterns = [
    path("fcm-config/upload/", CertificateUploadView.as_view(), name="upload-certificate"),
    path("fcm-config/device-group/", DeviceGroupView.as_view(), name="device-group"),
    path("fcm-config/send-notification-group/", SendNotificationGroupView.as_view(), name="send-notification-group"),
    path("fcm-config/send-notification-device/", SendNotificationDeviceView.as_view(), name="send-notification-device"),
]
