from django.urls import path

from .views import (
    CertificateUploadView,
    DeviceGroupView,
    GetUserDeviceView,
    SendNotificationGroupView,
    SendNotificationToTokensView,
    SendNotificationToTokenView,
    SendNotificationToUsernamesView,
    SendNotificationToUsernameView,
    UserDeviceDetailView,
)

urlpatterns = [
    path("fcm/certificate/", CertificateUploadView.as_view(), name="certificate-management"),
    # path("fcm/certificate/", CertificateDetailView.as_view(), name="certificate-detail"),
    path("fcm/devices/", GetUserDeviceView.as_view(), name="list-devices"),
    path("fcm/device/", UserDeviceDetailView.as_view(), name="device-detail"),
    path("fcm/group/", DeviceGroupView.as_view(), name="device-group-management"),
    path("fcm/send-notification-group/", SendNotificationGroupView.as_view(), name="send-notification-to-group"),
    path("fcm/send-notification-token/", SendNotificationToTokenView.as_view(), name="send-notification-to-token"),
    path("fcm/send-notification-tokens/", SendNotificationToTokensView.as_view(), name="send-notification-to-tokens"),
    path("fcm/send-notification-username/", SendNotificationToUsernameView.as_view(), name="send-notification-to-username"),
    path("fcm/send-notification-usernames/", SendNotificationToUsernamesView.as_view(), name="send-notification-to-usernames"),
]
