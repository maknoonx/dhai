"""
WhatsApp Cloud API Service for Dhai Optics.

Usage from anywhere in your Django project:
    from whatsapp.service import whatsapp

    # Send a text message
    whatsapp.send_text('+966512345678', 'مرحبا! طلبك جاهز للاستلام')

    # Send a template message (e.g. hello_world)
    whatsapp.send_template('+966512345678', 'hello_world', language='en_US')
"""

import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Meta Graph API base ──────────────────────────────────────
GRAPH_API_VERSION = 'v22.0'
GRAPH_API_BASE = f'https://graph.facebook.com/{GRAPH_API_VERSION}'


class WhatsAppService:
    """Thin wrapper around the WhatsApp Cloud API."""

    def __init__(self):
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
        self.verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '')
        self.api_url = f'{GRAPH_API_BASE}/{self.phone_number_id}/messages'

    @property
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

    # ── Send a plain text message ────────────────────────────
    def send_text(self, to: str, body: str) -> dict:
        """
        Send a text message.
        `to` must include country code, e.g. '966512345678' or '+966512345678'
        """
        to = self._normalize_phone(to)
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'text',
            'text': {'body': body},
        }
        return self._send(to, payload, message_type='text', body=body)

    # ── Send a template message ──────────────────────────────
    def send_template(self, to: str, template_name: str,
                      language: str = 'ar', components: list = None) -> dict:
        """
        Send a pre-approved template message.
        `components` is optional list of template components (header, body params, etc.)
        """
        to = self._normalize_phone(to)
        template_obj = {
            'name': template_name,
            'language': {'code': language},
        }
        if components:
            template_obj['components'] = components

        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'template',
            'template': template_obj,
        }
        return self._send(to, payload, message_type='template',
                          body=f'template:{template_name}')

    # ── Send an image ────────────────────────────────────────
    def send_image(self, to: str, image_url: str, caption: str = '') -> dict:
        """Send an image message by URL."""
        to = self._normalize_phone(to)
        image_obj = {'link': image_url}
        if caption:
            image_obj['caption'] = caption

        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'image',
            'image': image_obj,
        }
        return self._send(to, payload, message_type='image', body=caption or image_url)

    # ── Send a document (PDF, etc.) ──────────────────────────
    def send_document(self, to: str, document_url: str,
                      filename: str = 'document.pdf', caption: str = '') -> dict:
        """Send a document message by URL."""
        to = self._normalize_phone(to)
        doc_obj = {'link': document_url, 'filename': filename}
        if caption:
            doc_obj['caption'] = caption

        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to,
            'type': 'document',
            'document': doc_obj,
        }
        return self._send(to, payload, message_type='document', body=caption or filename)

    # ── Internal send & log ──────────────────────────────────
    def _send(self, to: str, payload: dict,
              message_type: str = 'text', body: str = '') -> dict:
        """Execute the API call, log to DB, return response."""
        from .models import WhatsAppMessage  # avoid circular import

        msg_record = WhatsAppMessage.objects.create(
            direction='outbound',
            recipient_phone=to,
            message_type=message_type,
            body=body[:500],
            status='pending',
            raw_payload=payload,
        )

        try:
            resp = requests.post(
                self.api_url,
                headers=self._headers,
                json=payload,
                timeout=30,
            )
            data = resp.json()

            if resp.status_code == 200 and 'messages' in data:
                wa_id = data['messages'][0].get('id', '')
                msg_record.wa_message_id = wa_id
                msg_record.status = 'sent'
                msg_record.save(update_fields=['wa_message_id', 'status', 'updated_at'])
                logger.info(f'WhatsApp message sent to {to}: {wa_id}')
            else:
                error_info = json.dumps(data, ensure_ascii=False)
                msg_record.status = 'failed'
                msg_record.error_message = error_info[:1000]
                msg_record.save(update_fields=['status', 'error_message', 'updated_at'])
                logger.error(f'WhatsApp send failed to {to}: {error_info}')

            return data

        except requests.RequestException as e:
            msg_record.status = 'failed'
            msg_record.error_message = str(e)[:1000]
            msg_record.save(update_fields=['status', 'error_message', 'updated_at'])
            logger.exception(f'WhatsApp request exception to {to}')
            return {'error': str(e)}

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Strip +, spaces, dashes — API expects digits only."""
        return phone.replace('+', '').replace(' ', '').replace('-', '')


# ── Module-level singleton ───────────────────────────────────
whatsapp = WhatsAppService()