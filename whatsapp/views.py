"""
WhatsApp Webhook Views.

Step 3 from Meta dashboard — configure these URLs:
  Callback URL:  https://dhaioptics.com/whatsapp/webhook/
  Verify Token:  <your WHATSAPP_VERIFY_TOKEN from settings>
"""

import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import WhatsAppMessage, WebhookLog

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    """
    Single endpoint that handles both:
      GET  → Meta verification handshake
      POST → Incoming message / status notifications
    """
    if request.method == 'GET':
        return _verify(request)
    return _handle_event(request)


def _verify(request):
    """
    Meta sends a GET request with:
      hub.mode=subscribe
      hub.verify_token=<your token>
      hub.challenge=<random string>

    You must return hub.challenge as plain text with HTTP 200.
    """
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')

    verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '')

    if mode == 'subscribe' and token == verify_token:
        logger.info('WhatsApp webhook verified successfully')
        return HttpResponse(challenge, content_type='text/plain', status=200)

    logger.warning(f'WhatsApp webhook verification failed: mode={mode}')
    return HttpResponse('Verification failed', status=403)


def _handle_event(request):
    """
    Process incoming webhook notifications.
    Must return 200 quickly (< 30s) or Meta will retry.
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)

    # Log raw webhook for debugging
    WebhookLog.objects.create(payload=payload, processed=False)

    # Parse the webhook payload
    try:
        for entry in payload.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})

                # Handle incoming messages
                if 'messages' in value:
                    _process_messages(value)

                # Handle status updates (sent, delivered, read)
                if 'statuses' in value:
                    _process_statuses(value)

    except Exception as e:
        logger.exception(f'Error processing webhook: {e}')

    # Always return 200 to acknowledge receipt
    return HttpResponse('OK', status=200)


def _process_messages(value: dict):
    """Handle incoming messages from customers."""
    contacts = {c['wa_id']: c.get('profile', {}).get('name', '')
                for c in value.get('contacts', [])}

    for msg in value.get('messages', []):
        wa_id = msg.get('id', '')
        sender = msg.get('from', '')
        msg_type = msg.get('type', 'text')
        timestamp = msg.get('timestamp', '')

        # Extract message body based on type
        body = ''
        if msg_type == 'text':
            body = msg.get('text', {}).get('body', '')
        elif msg_type == 'image':
            body = msg.get('image', {}).get('caption', '[صورة]')
        elif msg_type == 'document':
            body = msg.get('document', {}).get('caption', '[مستند]')
        elif msg_type == 'audio':
            body = '[رسالة صوتية]'
        elif msg_type == 'video':
            body = '[فيديو]'
        elif msg_type == 'location':
            loc = msg.get('location', {})
            body = f"[موقع: {loc.get('latitude')}, {loc.get('longitude')}]"
        elif msg_type == 'interactive':
            interactive = msg.get('interactive', {})
            if interactive.get('type') == 'button_reply':
                body = interactive.get('button_reply', {}).get('title', '')
            elif interactive.get('type') == 'list_reply':
                body = interactive.get('list_reply', {}).get('title', '')

        sender_name = contacts.get(sender, '')

        WhatsAppMessage.objects.create(
            wa_message_id=wa_id,
            direction='inbound',
            recipient_phone=sender,
            message_type=msg_type if msg_type in ['text', 'image', 'document'] else 'text',
            body=body[:500],
            status='delivered',
            raw_payload=msg,
        )

        logger.info(f'Inbound WhatsApp from {sender} ({sender_name}): {body[:100]}')


def _process_statuses(value: dict):
    """Update message status (sent → delivered → read)."""
    for status_update in value.get('statuses', []):
        wa_id = status_update.get('id', '')
        new_status = status_update.get('status', '')

        # Map Meta status to our status choices
        status_map = {
            'sent': 'sent',
            'delivered': 'delivered',
            'read': 'read',
            'failed': 'failed',
        }

        mapped_status = status_map.get(new_status)
        if not mapped_status:
            continue

        updated = WhatsAppMessage.objects.filter(
            wa_message_id=wa_id
        ).update(status=mapped_status)

        if updated:
            logger.info(f'WhatsApp message {wa_id} status → {mapped_status}')

        # Log errors for failed messages
        if new_status == 'failed':
            errors = status_update.get('errors', [])
            if errors:
                error_msg = json.dumps(errors, ensure_ascii=False)[:1000]
                WhatsAppMessage.objects.filter(
                    wa_message_id=wa_id
                ).update(error_message=error_msg)