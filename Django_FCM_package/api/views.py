import json

import firebase_admin
from firebase_admin import messaging
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FCMCertificate
from .serializers import FCMCertificateSerializer

# APIs to test with Postman:

# 1. POST /upload/ - Upload a new certificate   => OK
#    Data: { "certificate_json": file }
# 2. GET /upload/ - get every certificate?      => OK
# 3. GET /certificates/<int:pk>/ - Get a specific certificate by ID         => OK
# 4. PUT /certificates/<int:pk>/ - Update a specific certificate by ID      => OK
#    Data: { "name" : , "certificate_json": file }
# 5. DELETE /certificates/<int:pk>/ - Delete a specific certificate by ID   => OK
# 6. POST /device-group/ - Subscribe or unsubscribe a device from a group   => OK
#    Data: { "device_token": token, "group_name": name, "action": "subscribe/unsubscribe" }
# 7. POST /send-notification-group/ - Send a notification to a group        => OK
#    Data: { "group_name": name, "title": title, "body": body }
# 8. POST /send-notification-device/ - Send a notification to a device      => OK
#    Data: { "device_token": token, "title": title, "body": body }


class CertificateUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if FCMCertificate.objects.exists():
            return Response(
                {"error": "Only one FCM certificate can be uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FCMCertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        cert_instances = FCMCertificate.objects.all()
        serializer = FCMCertificateSerializer(cert_instances, many=True)
        data = [{"id": cert["id"], "name": cert["name"]} for cert in serializer.data]
        return Response(data)


class CertificateDetailView(APIView):
    def get(self, request, pk):
        try:
            cert_instance = FCMCertificate.objects.get(pk=pk)
            serializer = FCMCertificateSerializer(cert_instance)
            return Response(serializer.data)
        except FCMCertificate.DoesNotExist:
            return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            cert_instance = FCMCertificate.objects.get(pk=pk)
            serializer = FCMCertificateSerializer(cert_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FCMCertificate.DoesNotExist:
            return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            cert_instance = FCMCertificate.objects.get(pk=pk)
            cert_instance.delete()
            return Response({"message": "Certificate deleted"}, status=status.HTTP_204_NO_CONTENT)
        except FCMCertificate.DoesNotExist:
            return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)


def initialize_firebase_app():
    """Initializes the Firebase app if it hasn't been already."""
    if not firebase_admin._apps:
        cert_instance = FCMCertificate.objects.first()
        if not cert_instance or not cert_instance.certificate_json:
            return False, "No FCM certificate found or certificate JSON is missing."
        try:
            cred = firebase_admin.credentials.Certificate(cert_instance.certificate_json)
            firebase_admin.initialize_app(cred)
            return True, None
        except json.JSONDecodeError:
            return False, "Invalid JSON format in FCM certificate."
        except Exception as e:
            return False, f"Failed to initialize Firebase: {str(e)}"
    return True, None


class DeviceGroupView(APIView):
    def post(self, request):
        device_token = request.data.get("device_token")
        group_name = request.data.get("group_name")
        action = request.data.get("action")  # subscribe or unsubscribe

        if not all([device_token, group_name, action]):
            return Response(
                {"error": "device_token, group_name, and action are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action not in ["subscribe", "unsubscribe"]:
            return Response(
                {"error": "action must be either subscribe or unsubscribe"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response({"error": error_message}, status=500)

        try:
            if action == "subscribe":
                response = messaging.subscribe_to_topic(device_token, group_name)
            elif action == "unsubscribe":
                response = messaging.unsubscribe_from_topic(device_token, group_name)

            return Response({"message": "Device token has been {} from {}".format(action, group_name), "response": response})
        except Exception as e:
            return Response(
                {"error": f"Failed to {action} device token from group: {str(e)}"},
                status=500,
            )


class SendNotificationGroupView(APIView):
    def post(self, request):
        group_name = request.data.get("group_name")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([group_name, title, body]):
            return Response(
                {"error": "group_name, title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response({"error": error_message}, status=500)

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                topic=group_name,
            )

            response = messaging.send(message)
            return Response({"message_id": response})
        except Exception as e:
            return Response({"error": f"Failed to send message: {str(e)}"}, status=500)


class SendNotificationDeviceView(APIView):
    def post(self, request):
        device_token = request.data.get("device_token")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([device_token, title, body]):
            return Response(
                {"error": "device_token, title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response({"error": error_message}, status=500)

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=device_token,
            )

            response = messaging.send(message)
            return Response({"message_id": response})
        except Exception as e:
            return Response({"error": f"Failed to send message: {str(e)}"}, status=500)
