"""
Evolution API (WhatsApp) Service for Dhai Optics.

بوابة واتساب مجانية ذاتية الاستضافة (Evolution API) — بديلة عن Meta.
الإعدادات تُقرأ من settings (متغيرات البيئة):
    EVOLUTION_BASE_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE

Usage from anywhere in your Django project:
    from whatsapp.service import whatsapp

    # إرسال رسالة نصية
    whatsapp.send_text('512345678', 'مرحبا! طلبك جاهز للاستلام')

    # إرسال فاتورة PDF (bytes)
    whatsapp.send_document_pdf('512345678', pdf_bytes,
                               filename='INV-00338.pdf',
                               caption='فاتورتكم مرفقة')
"""

import base64
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EvolutionWhatsAppService:
    """غلاف بسيط حول Evolution API."""

    def __init__(self):
        self.base_url = getattr(settings, 'EVOLUTION_BASE_URL', '').rstrip('/')
        self.api_key = getattr(settings, 'EVOLUTION_API_KEY', '')
        self.instance = getattr(settings, 'EVOLUTION_INSTANCE', 'dhai')

    @property
    def _headers(self):
        return {
            'apikey': self.api_key,
            'Content-Type': 'application/json',
        }

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.instance)

    # ── إرسال رسالة نصية ─────────────────────────────────────
    def send_text(self, to: str, body: str) -> dict:
        to = self._normalize_phone(to)
        url = f'{self.base_url}/message/sendText/{self.instance}'
        payload = {'number': to, 'text': body}
        return self._send(to, url, payload, message_type='text', body=body)

    # ── إرسال مستند PDF عبر bytes (base64) ───────────────────
    def send_document_pdf(self, to: str, pdf_bytes: bytes,
                          filename: str = 'document.pdf', caption: str = '') -> dict:
        to = self._normalize_phone(to)
        url = f'{self.base_url}/message/sendMedia/{self.instance}'
        payload = {
            'number': to,
            'mediatype': 'document',
            'mimetype': 'application/pdf',
            'media': base64.b64encode(pdf_bytes).decode(),
            'fileName': filename,
        }
        if caption:
            payload['caption'] = caption
        return self._send(to, url, payload, message_type='document',
                          body=caption or filename)

    # ── إرسال مستند/صورة عبر رابط ────────────────────────────
    def send_document_url(self, to: str, media_url: str,
                          filename: str = 'document.pdf', caption: str = '') -> dict:
        to = self._normalize_phone(to)
        url = f'{self.base_url}/message/sendMedia/{self.instance}'
        payload = {
            'number': to,
            'mediatype': 'document',
            'media': media_url,
            'fileName': filename,
        }
        if caption:
            payload['caption'] = caption
        return self._send(to, url, payload, message_type='document',
                          body=caption or filename)

    # ── التنفيذ والتسجيل ─────────────────────────────────────
    def _send(self, to: str, url: str, payload: dict,
              message_type: str = 'text', body: str = '') -> dict:
        from .models import WhatsAppMessage  # avoid circular import

        msg_record = WhatsAppMessage.objects.create(
            direction='outbound',
            recipient_phone=to,
            message_type=message_type,
            body=body[:500],
            status='pending',
            raw_payload=payload if message_type != 'document' else {'number': to, 'type': 'document'},
        )

        if not self.is_configured:
            msg_record.status = 'failed'
            msg_record.error_message = 'Evolution API غير مُعدّة (تحقق من متغيرات البيئة)'
            msg_record.save(update_fields=['status', 'error_message', 'updated_at'])
            logger.error('Evolution API not configured; message not sent.')
            return {'error': 'not_configured'}

        try:
            resp = requests.post(url, headers=self._headers, json=payload, timeout=30)
            try:
                data = resp.json()
            except ValueError:
                data = {'raw': resp.text}

            # Evolution يعيد 200/201 مع key.id عند النجاح
            wa_id = ''
            if isinstance(data, dict):
                wa_id = (data.get('key') or {}).get('id', '')

            if resp.status_code in (200, 201) and wa_id:
                msg_record.wa_message_id = wa_id
                msg_record.status = 'sent'
                msg_record.save(update_fields=['wa_message_id', 'status', 'updated_at'])
                logger.info(f'WhatsApp (Evolution) sent to {to}: {wa_id}')
            elif resp.status_code in (200, 201):
                # نجح الطلب لكن بدون معرف واضح
                msg_record.status = 'sent'
                msg_record.save(update_fields=['status', 'updated_at'])
                logger.info(f'WhatsApp (Evolution) sent to {to} (no id)')
            else:
                import json as _json
                msg_record.status = 'failed'
                msg_record.error_message = _json.dumps(data, ensure_ascii=False)[:1000]
                msg_record.save(update_fields=['status', 'error_message', 'updated_at'])
                logger.error(f'Evolution send failed to {to}: {msg_record.error_message}')

            return data

        except requests.RequestException as e:
            msg_record.status = 'failed'
            msg_record.error_message = str(e)[:1000]
            msg_record.save(update_fields=['status', 'error_message', 'updated_at'])
            logger.exception(f'Evolution request exception to {to}')
            return {'error': str(e)}

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """
        يحوّل الرقم إلى الصيغة الدولية بأرقام فقط.
        عملاء المحل مخزّنون بـ 9 أرقام سعودية (5XXXXXXXX) بدون مفتاح الدولة،
        فنُضيف 966 تلقائياً. Evolution يقبل الرقم بأرقام فقط بدون + أو @.
        """
        digits = ''.join(ch for ch in str(phone) if ch.isdigit())
        if digits.startswith('00'):
            digits = digits[2:]
        if digits.startswith('966'):
            return digits
        if digits.startswith('0'):
            digits = digits[1:]
        if len(digits) == 9 and digits.startswith('5'):
            return '966' + digits
        return digits


# ── Module-level singleton ───────────────────────────────────
whatsapp = EvolutionWhatsAppService()
