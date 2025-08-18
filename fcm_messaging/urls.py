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
    path("certificate/", CertificateUploadView.as_view(), name="certificate-management"),
    path("devices/", GetUserDeviceView.as_view(), name="list-devices"),
    path("device/", UserDeviceDetailView.as_view(), name="device-detail"),
    path("group/", DeviceGroupView.as_view(), name="device-group-management"),
    path("send-notification-group/", SendNotificationGroupView.as_view(), name="send-notification-to-group"),
    path("send-notification-token/", SendNotificationToTokenView.as_view(), name="send-notification-to-token"),
    path("send-notification-tokens/", SendNotificationToTokensView.as_view(), name="send-notification-to-tokens"),
    path("send-notification-username/", SendNotificationToUsernameView.as_view(), name="send-notification-to-username"),
    path("send-notification-usernames/", SendNotificationToUsernamesView.as_view(), name="send-notification-to-usernames"),
]
