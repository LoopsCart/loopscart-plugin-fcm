import json

import firebase_admin
from firebase_admin import messaging
from firebase_admin.messaging import BatchResponse

from .models import FCMCertificate, FCMLog, UserDevice

# return format
# success, message


def initialize_firebase_app():
    """Initializes the Firebase app if it hasn't been already."""
    if firebase_admin._apps:
        return True, None

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


def send_message_tokens(title, body, tokens):
    """Sends a notification to a list of FCM tokens."""
    initialized, message = initialize_firebase_app()
    if not initialized:
        return initialized, message
    try:
        # Build multicast message
        multicast_message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens,
        )

        # Send the message to all tokens at once
        response = messaging.send_each_for_multicast(multicast_message)
        log_fcm_response(tokens=tokens, message_title=title, message_body=body, response=response)
        return True, format_batch_response(response)
    except Exception as e:
        print(e)
        return False, "Notification sending failed"


def send_message_token(title, body, token):
    """Sends a notification to a single FCM token."""
    initialized, message = initialize_firebase_app()
    if not initialized:
        return initialized, message
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        response = messaging.send(message)
        log_fcm_response(tokens=token, message_title=title, message_body=body, response=response)
        return True, response
    except Exception:
        return False, "Notification sending failed"


def send_message_usernames(title, body, usernames):
    """Sends a notification to a list of usernames."""
    initialized, message = initialize_firebase_app()
    if not initialized:
        return initialized, message
    try:
        user_devices = UserDevice.objects.filter(username__in=usernames)
        tokens = [ud.token for ud in user_devices]

        if not tokens:
            return False, "No valid tokens found for the given usernames."

        # Build multicast message
        multicast_message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens,
        )

        # Send the message to all tokens at once
        response = messaging.send_each_for_multicast(multicast_message)
        log_fcm_response(usernames=usernames, message_title=title, message_body=body, response=response)
        return True, format_batch_response(response)
    except UserDevice.DoesNotExist:
        return False, "One or more users not found"
    except Exception:
        return False, "Notification sending failed"


def send_message_username(title, body, username):
    """Sends a notification to a single username."""
    initialized, message = initialize_firebase_app()
    if not initialized:
        return initialized, message
    try:
        user_devices = UserDevice.objects.filter(username=username)
        tokens = [ud.token for ud in user_devices]

        if not tokens:
            return False, "No valid tokens found for the given username."

        # Build multicast message
        multicast_message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens,
        )

        # Send the message to all tokens at once
        response = messaging.send_each_for_multicast(multicast_message)
        log_fcm_response(usernames=username, message_title=title, message_body=body, response=response)
        return True, format_batch_response(response)
    except UserDevice.DoesNotExist:
        return False, "User not found"
    except Exception as e:
        print(e)
        return False, "Notification sending failed"


def format_batch_response(response):
    if isinstance(response, BatchResponse):
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count,
            "responses": [
                {"success": r.success, "message_id": r.message_id, "error": str(r.exception) if r.exception else None}
                for r in response.responses
            ],
        }
    else:
        # Handle the case where the response is not a BatchResponse
        return {"message": "Notification sent successfully."}


def log_fcm_response(message_body, response, usernames=None, tokens=None, message_title=None):
    """
    Logs FCM responses for BatchResponse, TopicManagementResponse, or single send.
    - usernames: list of usernames, comma-separated string, or None
    - tokens: list of FCM tokens, comma-separated string, or None
    - message_title: notification title
    - message_body: notification body
    - response: FCM send result object
    """

    # Convert to comma-separated strings if lists/tuples
    if isinstance(usernames, (list, tuple)):
        usernames = ", ".join(usernames)
    if isinstance(tokens, (list, tuple)):
        tokens = ", ".join(tokens)

    usernames = usernames or ""
    tokens = tokens or ""

    responses_list = []
    success_count = 0
    failure_count = 0

    # BatchResponse (multicast or send_all)
    if isinstance(response, messaging.BatchResponse):
        success_count = response.success_count
        failure_count = response.failure_count
        for r in response.responses:
            if r.success:
                responses_list.append({"success": True, "message_id": r.message_id})
            else:
                responses_list.append({"success": False, "error": str(r.exception)})

    # TopicManagementResponse (subscribe/unsubscribe to topics)
    elif isinstance(response, messaging.TopicManagementResponse):
        success_count = response.success_count
        failure_count = response.failure_count
        responses_list = [{"index": e.index, "reason": e.reason} for e in response.errors]

    # Single message (send())
    else:
        if isinstance(response, str):
            success_count = 1
            responses_list.append({"success": True, "message_id": response})
        else:
            failure_count = 1
            responses_list.append({"success": False, "error": str(response)})

    # Save log
    FCMLog.objects.create(
        usernames=usernames,
        tokens=tokens,
        message_title=message_title,
        message_body=message_body,
        success_count=success_count,
        failure_count=failure_count,
        responses=responses_list,
    )
