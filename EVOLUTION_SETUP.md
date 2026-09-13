# تشغيل واتساب (Evolution API) لموقع بصريات ضي على Railway

هذا الدليل يشرح تشغيل بوابة Evolution API المجانية وربط رقم واتساب المحل، ثم
ربطها بموقع Django. الكود في الموقع جاهز ويقرأ الإعدادات من متغيرات البيئة.

---

## 1) إضافة الخدمات في مشروع Railway

افتح مشروعك في Railway (نفس مشروع dhaioptics.com) ثم:

1. **+ New → Database → PostgreSQL** (لقاعدة بيانات Evolution).
2. **+ New → Database → Redis** (للتخزين المؤقت).
3. **+ New → Docker Image** واكتب الصورة:
   ```
   atendai/evolution-api:v2.1.1
   ```
   (أو أحدث إصدار v2 متاح).

## 2) متغيرات بيئة خدمة Evolution

في خدمة Evolution → تبويب **Variables** أضف:

```
AUTHENTICATION_API_KEY=<اختر مفتاحاً سرياً قوياً هنا>
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=${{Postgres.DATABASE_URL}}
DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=true
DATABASE_SAVE_MESSAGE_UPDATE=true
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=${{Redis.REDIS_URL}}
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_LOCAL_ENABLED=false
CONFIG_SESSION_PHONE_CLIENT=Dhai Optics
CONFIG_SESSION_PHONE_NAME=Chrome
```

> ملاحظة: `${{Postgres.DATABASE_URL}}` و`${{Redis.REDIS_URL}}` مراجع Railway —
> تأكد أن أسماء خدمتي Postgres وRedis مطابقة، وإلا عدّل الاسم.

ثم في تبويب **Settings** لخدمة Evolution:
- **Networking → Generate Domain** (المنفذ الداخلي 8080).
- ستحصل على رابط عام مثل: `https://dhai-evolution.up.railway.app`

## 3) إنشاء instance وربط رقم واتساب

1. افتح لوحة الإدارة في المتصفح:
   ```
   https://dhai-evolution.up.railway.app/manager
   ```
2. سجّل الدخول بـ `AUTHENTICATION_API_KEY`.
3. **Create Instance** → الاسم: `dhai` → Create.
4. سيظهر **QR Code**.
5. على جوال المحل: **واتساب ← الإعدادات ← الأجهزة المرتبطة ← ربط جهاز ← امسح الـ QR**.
6. تتحول الحالة إلى **open (متصل)** = تم الربط ✅

## 4) ضبط webhook داخل Evolution

في إعدادات الـ instance (`dhai`) → **Webhook**:
- **URL**:
  ```
  https://dhaioptics.com/whatsapp/webhook/?token=<EVOLUTION_WEBHOOK_TOKEN>
  ```
- فعّل الحدث: **MESSAGES_UPSERT** فقط.
- احفظ.

(اختر أي قيمة سرية لـ `EVOLUTION_WEBHOOK_TOKEN` وستضعها أيضاً في متغيرات الموقع بالخطوة التالية.)

## 5) متغيرات بيئة موقع Django (خدمة dhaioptics على Railway)

في خدمة الموقع الأساسية → **Variables** أضف:

```
EVOLUTION_BASE_URL=https://dhai-evolution.up.railway.app
EVOLUTION_API_KEY=<نفس AUTHENTICATION_API_KEY>
EVOLUTION_INSTANCE=dhai
EVOLUTION_WEBHOOK_TOKEN=<نفس السر المستخدم في رابط الـ webhook>
SITE_URL=https://dhaioptics.com
```

بعد الحفظ ستعيد Railway نشر الموقع تلقائياً، وسيطبّق الـ migration الجديد
(أضفنا ذلك في `Procfile`).

---

## 6) الاختبار

1. أنشئ فاتورة تجريبية من `/sales/add/` مع إبقاء خيار «إرسال الفاتورة عبر واتساب» مفعّلاً
   → يصل للعميل ملف PDF + ملاحظة «سيتم التواصل معكم عند استلام النظارة».
2. من صفحة الفاتورة اضغط **«إشعار بوصول النظارة»**
   → تصل رسالة تسأل: ردّ بـ 1 للاستلام أو 2 للتوصيل.
3. ردّ من جوال العميل بـ `1` أو `2`
   → يصل تأكيد، وتظهر طريقة الاستلام في صفحة الفاتورة.

## ملاحظات مهمة

- **رقم العميل**: مخزّن بـ 9 أرقام سعودية (5XXXXXXXX)، والنظام يضيف 966 تلقائياً.
- **الأزرار**: البوابات المجانية لا تدعم أزرار واتساب التفاعلية بثبات، لذلك نعتمد الرد برقم (1/2).
- **خطر الحظر**: Evolution غير رسمية؛ تجنّب الرسائل الجماعية المكثفة لتقليل احتمال حظر الرقم.
- **بقاء الاتصال**: افتح جوال المحل من وقت لآخر حتى لا ينفصل الجهاز المرتبط.
- **أمان**: التوكن القديم من Meta أصبح غير مستخدم — يُفضّل إبطاله من لوحة Meta.
