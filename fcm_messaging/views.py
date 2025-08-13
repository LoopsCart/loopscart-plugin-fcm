import json

import firebase_admin
from firebase_admin import messaging
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FCMCertificate, User
from .serializers import FCMCertificateSerializer, UserSerializer
from firebase_admin.messaging import TopicManagementResponse

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


# #########
# CRUD for User


class SendNotificationMultipleDevicesView(APIView):
    def post(self, request):
        device_tokens = request.data.get("device_tokens")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([device_tokens, title, body]):
            return Response(
                {"success": False, "error": "device_tokens, title, and body are required."},
                status=status.HTTP_200_OK,
            )

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response(
                {"success": False, "error": error_message},
                status=status.HTTP_200_OK,
            )

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                tokens=device_tokens,
            )

            response = messaging.send_multicast(message)
            return Response({"success": True, "message_id": response}, status=status.HTTP_200_OK)

        except Exception:
            return Response({"success": False, "error": "Notification sending failed."}, status=status.HTTP_200_OK)


class GetUserView(APIView):
    def get(self, request):
        user_instances = User.objects.all()
        serializer = UserSerializer(user_instances, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    def get(self, request):
        data = request.data
        username = data.get("username")
        if not id:
            return Response(
                {"error": "username is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_instance = User.objects.get(username=username)
            serializer = UserSerializer(user_instance)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        data = request.data
        username = data.get("username")
        if not id:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_instance = User.objects.get(username=username)
            user_instance.delete()
            return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = request.data
        username = data.get("username")
        token = data.get("token")
        if not all([username, token]):
            return Response(
                {"error": "username and token are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_instance, created = User.objects.get_or_create(username=username)
        serializer = UserSerializer(user_instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificateUploadView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        cert_instances = FCMCertificate.objects.all()
        serializer = FCMCertificateSerializer(cert_instances, many=True)
        data = [{"id": cert["id"], "name": cert["name"], "certificate_json": cert["certificate_json"]} for cert in serializer.data]
        return Response(data)

    def post(self, request):
        instance = FCMCertificate.objects.first()
        serializer = FCMCertificateSerializer(instance=instance, data=request.data)
        
        if serializer.is_valid():
            status_code = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
            serializer.save()
            return Response(serializer.data, status=status_code)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        cert_instance = FCMCertificate.objects.first()
        if not cert_instance:
            return Response({"error": "No certificate found to update."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FCMCertificateSerializer(cert_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        cert_instance = FCMCertificate.objects.first()
        if not cert_instance:
            return Response({"error": "No certificate found to update."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FCMCertificateSerializer(cert_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({"error": "Deleting the certificate is not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
        username = request.data.get("username")
        group_name = request.data.get("group_name")
        action = request.data.get("action")  # subscribe or unsubscribe

        if not (device_token or username):
            return Response(
                {"error": "Either device_token or user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if device_token and username:
            return Response(
                {"error": "Only one of device_token or user_id should be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not all([group_name, action]):
            return Response(
                {"error": "group_name and action are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action not in ["subscribe", "unsubscribe"]:
            return Response(
                {"error": "action must be either subscribe or unsubscribe"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if username:
            try:
                user_instance = User.objects.get(username=username)
                device_token = user_instance.token
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response({"error": error_message}, status=500)

        try:
            if action == "subscribe":
                response = messaging.subscribe_to_topic(device_token, group_name)
            elif action == "unsubscribe":
                response = messaging.unsubscribe_from_topic(device_token, group_name)

            if isinstance(response, TopicManagementResponse):
                response_data = {
                    'success_count': response.success_count, 'failure_count': response.failure_count,
                    'errors': [{'index': e.index, 'reason': e.reason} for e in response.errors]
                    }
            else:
                response_data = {'message': 'Operation successful', 'result': str(response)}
    
            return Response({"message": "Device token has been {} to group {}".format(action, group_name), "result": response_data })
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
            return Response(
                {"status": "failed", "error": error_message},
                status=status.HTTP_200_OK,  # <-- returning 200 even on init failure
            )

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                topic=group_name,
            )

            response = messaging.send(message)
            return Response({"status": "success", "message_id": response}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": "failed", "error": f"Failed to send message: {str(e)}"},
                status=status.HTTP_200_OK,  # <-- returning 200 even on send failure
            )


class SendNotificationDeviceView(APIView):
    def post(self, request):
        device_token = request.data.get("device_token")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([device_token, title, body]):
            return Response(
                {"success": False, "error": "device_token, title, and body are required."},
                status=status.HTTP_200_OK,
            )

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response(
                {"success": False, "error": error_message},
                status=status.HTTP_200_OK,
            )

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=device_token,
            )

            response = messaging.send(message)
            return Response({"success": True, "message_id": response}, status=status.HTTP_200_OK)

        except Exception:
            return Response({"success": False, "error": "Notification sending failed."}, status=status.HTTP_200_OK)


class SendNotificationViewByUsername(APIView):
    def post(self, request):
        username = request.data.get("username")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([username, title, body]):
            return Response(
                {"success": False, "error": "username, title, and body are required."},
                status=status.HTTP_200_OK,
            )

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response(
                {"success": False, "error": error_message},
                status=status.HTTP_200_OK,
            )

        try:
            user_instance = User.objects.get(username=username)
            device_token = user_instance.token
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=device_token,
            )

            response = messaging.send(message)
            return Response({"success": True, "message_id": response}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"success": False, "error": "User not found"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"success": False, "error": "Notification sending failed."}, status=status.HTTP_200_OK)
