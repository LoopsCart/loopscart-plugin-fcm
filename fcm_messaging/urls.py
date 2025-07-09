from django.urls import path

from .views import (
    CertificateUploadView,
    DeviceGroupView,
    GetUserView,
    SendNotificationDeviceView,
    SendNotificationGroupView,
    SendNotificationMultipleDevicesView,
    SendNotificationViewById,
    UserDetailView,
)

urlpatterns = [
    path("fcm-config/upload/", CertificateUploadView.as_view(), name="upload-certificate"),
    path("fcm-config/device-group/", DeviceGroupView.as_view(), name="device-group"),
    path("fcm-config/send-notification-group/", SendNotificationGroupView.as_view(), name="send-notification-group"),
    path("fcm-config/send-notification-device/", SendNotificationDeviceView.as_view(), name="send-notification-device"),
    # path("fcm-config/user/<int:pk>/", UserDetailView.as_view(), name="user"),
    path("fcm-config/user/", UserDetailView.as_view(), name="user"),
    path("fcm-config/users/", GetUserView.as_view(), name="get all users"),
    path("fcm-config/send-notification-user/", SendNotificationViewById.as_view(), name="send-notification-user"),
    path(
        "fcm-config/send-notification-multiple-devices/",
        SendNotificationMultipleDevicesView.as_view(),
        name="send same notification to multiple devices",
    ),
]
