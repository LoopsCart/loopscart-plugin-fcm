from django.db import IntegrityError
from firebase_admin import messaging
from firebase_admin.messaging import TopicManagementResponse
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from fcm_messaging.utils import (
    initialize_firebase_app,
    send_message_admin,
    send_message_token,
    send_message_tokens,
    send_message_usernames,
)

from .models import FCMCertificate, UserDevice
from .serializers import FCMCertificateSerializer, UserDeviceSerializer

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


class FirebaseConfigView(APIView):
    def get(self, request):
        try:
            cert_instance = FCMCertificate.objects.get(pk=1)  # Assuming a single certificate with pk=1
            response_data = {
                "firebase_config": cert_instance.firebase_config,
                "vapid_key": cert_instance.vapid_key,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except FCMCertificate.DoesNotExist:
            return Response({"error": "No FCM certificate found."}, status=status.HTTP_404_NOT_FOUND)


# #########
# CRUD for User and certificate


class GetUserDeviceView(APIView):
    def get(self, request):
        user_device_instances = UserDevice.objects.all()
        serializer = UserDeviceSerializer(user_device_instances, many=True)
        return Response(serializer.data)


class UserDeviceDetailView(APIView):
    def get(self, request):
        username = request.query_params.get("username")  # Use query_params for GET requests
        if not username:
            return Response(
                {"error": "username is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_device_instances = UserDevice.objects.filter(username=username)
        if not user_device_instances.exists():
            return Response({"error": "User devices not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDeviceSerializer(user_device_instances, many=True)
        return Response(serializer.data)

    def delete(self, request):
        username = request.data.get("username")
        uuid = request.data.get("uuid")  # Need uuid to uniquely identify the device for deletion

        if not username or not uuid:
            return Response(
                {"error": "Both username and uuid are required for deletion."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_device_instance = UserDevice.objects.get(username=username, uuid=uuid)
            user_device_instance.delete()
            return Response({"message": "User device deleted"}, status=status.HTTP_204_NO_CONTENT)
        except UserDevice.DoesNotExist:
            return Response({"error": "User device not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = request.data
        username = data.get("username")
        token = data.get("token")
        uuid = data.get("uuid")  # uuid is also needed for creating/updating a specific device

        if not all([username, token, uuid]):
            return Response(
                {"error": "username, token, and uuid are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Use get_or_create with the unique fields to handle existing or new devices
            user_device_instance, created = UserDevice.objects.get_or_create(
                username=username,
                uuid=uuid,
                defaults={"token": token},  # Set default token if creating a new instance
            )

            # If the instance already existed, update its token if it changed
            if not created and user_device_instance.token != token:
                user_device_instance.token = token
                user_device_instance.save()

            serializer = UserDeviceSerializer(user_device_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except IntegrityError:
            return Response(
                {"error": "A device with this token already exists for this user."},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CertificateUploadView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        try:
            cert_instance = FCMCertificate.objects.get(pk=1)  # Assuming a single certificate with pk=1
            serializer = FCMCertificateSerializer(cert_instance)
            return Response(serializer.data)
        except FCMCertificate.DoesNotExist:
            return Response({"error": "No FCM certificate found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        instance, created = FCMCertificate.objects.get_or_create(pk=1)

        serializer = FCMCertificateSerializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            status_code = status.HTTP_200_OK if not created else status.HTTP_201_CREATED
            return Response(serializer.data, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        instance, created = FCMCertificate.objects.get_or_create(pk=1)
        if not instance and not created:  # Check if instance was actually created or if it was a retrieval
            return Response({"error": "No certificate found to update."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FCMCertificateSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Assuming there should only ever be one certificate configured.
        instance, created = FCMCertificate.objects.get_or_create(pk=1)
        if not instance and not created:
            return Response({"error": "No certificate found to update."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FCMCertificateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({"error": "Deleting the certificate is not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


########################


class SendNotificationToTokensView(APIView):
    def post(self, request):
        tokens = request.data.get("tokens")  # Expecting a list of tokens
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([tokens, title, body]):
            return Response(
                {"success": False, "error": "tokens, title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(tokens, list):
            return Response(
                {"success": False, "error": "tokens must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = send_message_tokens(title, body, tokens)

        return Response({"success": success, "detail": message}, status=status.HTTP_200_OK)


class SendNotificationToTokenView(APIView):
    def post(self, request):
        device_token = request.data.get("token")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([device_token, title, body]):
            return Response(
                {"success": False, "error": "token, title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = send_message_token(title, body, device_token)

        return Response({"success": success, "detail": message}, status=status.HTTP_200_OK)


class SendNotificationToUsernamesView(APIView):
    def post(self, request):
        usernames = request.data.get("usernames")  # Expecting a list of usernames
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([usernames, title, body]):
            return Response(
                {"success": False, "error": "usernames, title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(usernames, list):
            return Response(
                {"success": False, "error": "usernames must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = send_message_usernames(title, body, usernames)

        return Response({"success": success, "detail": message}, status=status.HTTP_200_OK)


class SendNotificationToUsernameView(APIView):
    def post(self, request):
        username = request.data.get("username")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([username, title, body]):
            return Response(
                {"success": False, "error": "username, title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = send_message_usernames(title, body, [username])

        return Response({"success": success, "detail": message}, status=status.HTTP_200_OK)


########################
# GROUP view


class DeviceGroupView(APIView):
    def post(self, request):
        device_token = request.data.get("token")
        group_name = request.data.get("group_name")
        action = request.data.get("action")

        if not device_token:
            return Response(
                {"error": "device_token is required."},
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

        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if action == "subscribe":
                response = messaging.subscribe_to_topic(device_token, group_name)
            else:
                response = messaging.unsubscribe_from_topic(device_token, group_name)

            if isinstance(response, TopicManagementResponse):
                response_data = {
                    "success_count": response.success_count,
                    "failure_count": response.failure_count,
                    "errors": [{"index": e.index, "reason": e.reason} for e in response.errors],
                }
            else:
                response_data = {"message": "Operation successful", "result": str(response)}

            return Response({"message": f"Device token has been {action}d to group {group_name}", "result": response_data})
        except Exception as e:
            return Response(
                {"error": f"Failed to {action} device token from group: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

        # Initialize Firebase app. This function is assumed to be defined elsewhere.
        initialized, error_message = initialize_firebase_app()
        if not initialized:
            return Response(
                {"status": "failed", "error": error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendNotificationAdminView(APIView):
    def post(self, request):
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([title, body]):
            return Response(
                {"success": False, "error": "title, and body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = send_message_admin(title, body)

        return Response({"success": success, "detail": message}, status=status.HTTP_200_OK)


#########################
# OLD views (to be removed)


# class SendNotificationDeviceView(APIView):
#     def post(self, request):
#         device_token = request.data.get("device_token")
#         title = request.data.get("title")
#         body = request.data.get("body")

#         if not all([device_token, title, body]):
#             return Response(
#                 {"success": False, "error": "device_token, title, and body are required."},
#                 status=status.HTTP_200_OK,
#             )

#         initialized, error_message = initialize_firebase_app()
#         if not initialized:
#             return Response(
#                 {"success": False, "error": error_message},
#                 status=status.HTTP_200_OK,
#             )

#         try:
#             message = messaging.Message(
#                 notification=messaging.Notification(title=title, body=body),
#                 token=device_token,
#             )

#             response = messaging.send(message)
#             return Response({"success": True, "message_id": response}, status=status.HTTP_200_OK)

#         except Exception:
#             return Response({"success": False, "error": "Notification sending failed."}, status=status.HTTP_200_OK)


# class SendNotificationViewByUsername(APIView):
#     def post(self, request):
#         username = request.data.get("username")
#         title = request.data.get("title")
#         body = request.data.get("body")

#         if not all([username, title, body]):
#             return Response(
#                 {"success": False, "error": "username, title, and body are required."},
#                 status=status.HTTP_200_OK,
#             )

#         success, message = send_message_username(title, body, username)

#         return Response({"success": success, "detail": message}, status=status.HTTP_200_OK)

#         # try:
#         #     user_instance = User.objects.get(username=username)
#         #     device_token = user_instance.token
#         #     message = messaging.Message(
#         #         notification=messaging.Notification(title=title, body=body),
#         #         token=device_token,
#         #     )

#         #     response = messaging.send(message)
#         #     return Response({"success": True, "message_id": response}, status=status.HTTP_200_OK)

#         # except UserDevice.DoesNotExist:
#         #     return Response({"success": False, "error": "User not found"}, status=status.HTTP_200_OK)
#         # except Exception as e:
#         #     print(e)
#         #     return Response({"success": False, "error": "Notification sending failed."}, status=status.HTTP_200_OK)


# class SendNotificationViewByUsernames(APIView):
#     def post(self, request):
#         usernames = request.data.get("usernames")  # Expecting a list of usernames
#         title = request.data.get("title")
#         body = request.data.get("body")

#         if not all([usernames, title, body]):
#             return Response(
#                 {"success": False, "error": "usernames, title, and body are required."},
#                 status=status.HTTP_200_OK,
#             )

#         if not isinstance(usernames, list):
#             return Response(
#                 {"success": False, "error": "usernames must be a list."},
#                 status=status.HTTP_200_OK,
#             )

#         initialized, error_message = initialize_firebase_app()
#         if not initialized:
#             return Response(
#                 {"success": False, "error": error_message},
#                 status=status.HTTP_200_OK,
#             )

#         # Get all matching users and their device tokens
#         users = UserDevice.objects.filter(username__in=usernames).exclude(token__isnull=True).exclude(token__exact="")
#         tokens = [user.token for user in users]

#         if not tokens:
#             return Response(
#                 {"success": False, "error": "No valid device tokens found for given usernames."},
#                 status=status.HTTP_200_OK,
#             )

#         response = send_message_tokens(title, body, tokens)

#         # Build results per user
#         results = []
#         for idx, user in enumerate(users):
#             send_result = response.responses[idx]
#             if send_result.success:
#                 results.append({"username": user.username, "success": True, "message_id": send_result.message_id})
#             else:
#                 results.append({"username": user.username, "success": False, "error": send_result.exception})

#         return Response(
#             {"success_count": response.success_count, "failure_count": response.failure_count, "results": results},
#             status=status.HTTP_200_OK,
#         )
