"""
WhatsApp Webhook Views — Evolution API.

في لوحة Evolution Manager، اضبط webhook الخاص بالـ instance على:
  URL:   https://dhaioptics.com/whatsapp/webhook/?token=<EVOLUTION_WEBHOOK_TOKEN>
  Events: messages.upsert

Evolution يرسل الأحداث كـ POST. صيغة رسالة واردة (messages.upsert):
  {
    "event": "messages.upsert",
    "instance": "dhai",
    "data": {
      "key": {"remoteJid": "9665XXXXXXXX@s.whatsapp.net", "fromMe": false, "id": "..."},
      "pushName": "اسم العميل",
      "message": {"conversation": "1"}   # أو extendedTextMessage.text
    }
  }
"""

import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import WhatsAppMessage, WebhookLog
from .service import whatsapp

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    """نقطة استقبال أحداث Evolution API."""
    # التحقق البسيط من السر (اختياري لكنه موصى به)
    expected = getattr(settings, 'EVOLUTION_WEBHOOK_TOKEN', '')
    if expected and request.GET.get('token') != expected:
        return HttpResponse('Forbidden', status=403)

    if request.method == 'GET':
        return HttpResponse('OK', status=200)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)

    WebhookLog.objects.create(payload=payload, processed=False)

    try:
        event = payload.get('event', '')
        if event in ('messages.upsert', 'MESSAGES_UPSERT'):
            _process_incoming(payload.get('data', {}))
    except Exception as e:
        logger.exception(f'Error processing Evolution webhook: {e}')

    return HttpResponse('OK', status=200)


def _extract_text(message: dict) -> str:
    """يستخرج نص الرسالة من صيغ Evolution/Baileys المختلفة."""
    if not isinstance(message, dict):
        return ''
    if message.get('conversation'):
        return message['conversation']
    ext = message.get('extendedTextMessage') or {}
    if ext.get('text'):
        return ext['text']
    # ردود الأزرار (نادرة على البوابات المجانية لكن نغطّيها)
    btn = message.get('buttonsResponseMessage') or {}
    if btn.get('selectedDisplayText'):
        return btn['selectedDisplayText']
    lst = message.get('listResponseMessage') or {}
    if (lst.get('title')):
        return lst['title']
    return ''


def _process_incoming(data):
    """يعالج رسالة/رسائل واردة من العميل."""
    # قد تأتي data كقائمة أو كعنصر واحد
    items = data if isinstance(data, list) else [data]

    for item in items:
        if not isinstance(item, dict):
            continue

        key = item.get('key', {}) or {}
        if key.get('fromMe'):
            continue  # تجاهل رسائلنا الصادرة

        remote_jid = key.get('remoteJid', '') or ''
        # نتجاهل رسائل المجموعات
        if remote_jid.endswith('@g.us'):
            continue

        sender_digits = ''.join(ch for ch in remote_jid.split('@')[0] if ch.isdigit())
        text = _extract_text(item.get('message', {})).strip()

        # تسجيل الرسالة الواردة
        WhatsAppMessage.objects.create(
            wa_message_id=key.get('id', ''),
            direction='inbound',
            recipient_phone=sender_digits,
            message_type='text',
            body=text[:500],
            status='delivered',
            raw_payload=item,
        )
        logger.info(f'Inbound WhatsApp from {sender_digits}: {text[:100]}')

        if text:
            _handle_delivery_reply(sender_digits, text)


def _handle_delivery_reply(sender_digits: str, text: str):
    """يربط رد العميل (1/2) بآخر فاتورة أُشعر بوصولها ويحدّثها."""
    from sales.models import Sale

    # آخر 9 أرقام تطابق حقل جوال العميل (المخزّن بدون مفتاح الدولة)
    local9 = sender_digits[-9:] if len(sender_digits) >= 9 else sender_digits

    # نحدّد الاختيار من نص الرد
    choice = None
    if text in ('1', '١') or 'استلام' in text or 'المحل' in text:
        choice = 'pickup'
    elif text in ('2', '٢') or 'توصيل' in text or 'توصيله' in text:
        choice = 'delivery'

    if not choice:
        return  # رد غير مفهوم — نتجاهله (يمكن لاحقاً إرسال رسالة توضيح)

    # نبحث عن آخر فاتورة لهذا العميل أُشعرت بالوصول ولم يُحدَّد لها اختيار بعد
    sale = (
        Sale.objects
        .filter(customer__phone__endswith=local9,
                arrival_notified_at__isnull=False,
                delivery_choice='')
        .order_by('-arrival_notified_at')
        .first()
    )
    if not sale:
        return

    sale.delivery_choice = choice
    sale.delivery_choice_at = timezone.now()
    sale.save(update_fields=['delivery_choice', 'delivery_choice_at', 'updated_at'])

    label = 'الاستلام من المحل' if choice == 'pickup' else 'التوصيل'
    confirm = (
        f"تم تسجيل رغبتكم في *{label}* للطلب رقم {sale.order_number}.\n"
        f"سنتواصل معكم لإتمام ذلك. شكراً لكم 🌟"
    )
    try:
        whatsapp.send_text(sender_digits, confirm)
    except Exception:
        logger.exception('Failed to send delivery confirmation')
