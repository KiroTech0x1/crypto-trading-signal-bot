"""
SignalX - Telegram User Bot
=============================
Handles /start, buttons, payments, language selection.
Run this alongside bot.py for full functionality.
"""

import json
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

from config import TELEGRAM_BOT_TOKEN, PREMIUM_CHANNEL_ID, BOT_NAME

# === Database (simple JSON) ===
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"lang": "en", "vip": False, "joined": ""}
        save_users(users)
    return users[uid]

def set_user_lang(user_id, lang):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"lang": lang, "vip": False, "joined": ""}
    else:
        users[uid]["lang"] = lang
    save_users(users)


# === Translations ===
TEXTS = {
    "en": {
        "welcome": (
            "🤖 <b>Welcome to SignalX!</b>\n\n"
            "📊 The most accurate crypto trading signals\n\n"
            "✅ High Quality Premium Signals\n"
            "✅ 85%+ Success Rate\n"
            "✅ 30+ Signals Daily (Faster Than Others)\n"
            "✅ Entry – Targets – StopLoss – Leverage\n\n"
            "🏆 <b>Available Plans:</b>\n"
            "▪️ 1 Month Access — $39 (was $80)\n"
            "▪️ Lifetime Access — $99 (was $250)\n\n"
            "👇 Select an option below:"
        ),
        "buy_vip": "🛒 Buy | VIP 🏷",
        "my_account": "👤 My Account 🧑",
        "stats": "📊 Stats 📈",
        "support": "💬 Support 📩",
        "language": "🌐 Language 🏳️",
        "back": "⬅️ Back",
        "select_plan": (
            "🏆 <b>Our subscription prices:</b>\n\n"
            "▪️ 1 Month — <b>$39</b> <s>($80)</s>\n"
            "▪️ Lifetime — <b>$99</b> <s>($250)</s>\n\n"
            "💎 Note: Payment in crypto. Your subscription will be "
            "activated automatically after confirmation.\n\n"
            "📌 <b>Select your payment option:</b>"
        ),
        "account_info": (
            "👤 <b>My Account</b>\n\n"
            "🆔 User ID: <code>{user_id}</code>\n"
            "🌐 Language: {lang}\n"
            "💎 VIP Status: {vip_status}\n\n"
            "📌 To upgrade, click Buy VIP below."
        ),
        "stats_text": (
            "📊 <b>SignalX Performance (Last 7 Days)</b>\n\n"
            "✅ Total Signals: {total}\n"
            "🟢 Wins: {wins}\n"
            "🔴 Losses: {losses}\n"
            "🎯 Win Rate: {win_rate}%\n"
            "💰 Total Profit: {profit}%\n\n"
            "📈 Updated in real-time"
        ),
        "support_text": (
            "💬 <b>Support</b>\n\n"
            "For any questions or issues:\n\n"
            "📩 Contact: @Liberty_Help\n"
            "⏰ Response time: Within 24 hours\n\n"
            "Common questions:\n"
            "• How to activate VIP?\n"
            "• Payment not confirmed?\n"
            "• Need help with signals?"
        ),
        "select_language": "🌐 <b>Select your language:</b>",
        "lang_changed": "✅ Language changed to English!",
        "payment_info": (
            "💳 <b>Payment - {method}</b>\n\n"
            "After depositing to Wallet, send the screenshot below.\n"
            "Usually less than 30 minutes is confirmed.\n\n"
            "▪️ 1 Month — <b>$39</b> <s>($80)</s>\n"
            "▪️ Lifetime — <b>$99</b> <s>($250)</s>\n\n"
            "{method}:\n"
            "<code>{address}</code>"
        ),
        "receipt_text": (
            "🧾 <b>Send Receipt</b>\n\n"
            "Please send your payment screenshot/transaction ID "
            "to @Liberty_Help\n\n"
            "Include:\n"
            "• Your Telegram username\n"
            "• Payment amount\n"
            "• Transaction screenshot\n\n"
            "⏰ Your VIP will be activated within 30 minutes - 12 hours."
        ),
        "vip_active": "✅ Active",
        "vip_inactive": "❌ Not Active",
    },
    "tr": {
        "welcome": (
            "🤖 <b>SignalX'e Hoş Geldiniz!</b>\n\n"
            "📊 En doğru kripto trading sinyalleri\n\n"
            "✅ Yüksek Kaliteli Premium Sinyaller\n"
            "✅ %85+ Başarı Oranı\n"
            "✅ Günde 30+ Sinyal (Diğerlerinden Hızlı)\n"
            "✅ Giriş – Hedefler – StopLoss – Kaldıraç\n\n"
            "🏆 <b>Mevcut Planlar:</b>\n"
            "▪️ 1 Aylık Erişim — $39 (önce $80)\n"
            "▪️ Ömür Boyu Erişim — $99 (önce $250)\n\n"
            "👇 Aşağıdan bir seçenek seçin:"
        ),
        "buy_vip": "🛒 VIP Satın Al 🏷",
        "my_account": "👤 Hesabım 🧑",
        "stats": "📊 İstatistikler 📈",
        "support": "💬 Destek 📩",
        "language": "🌐 Dil 🏳️",
        "back": "⬅️ Geri",
        "select_plan": (
            "🏆 <b>Abonelik fiyatlarımız:</b>\n\n"
            "▪️ 1 Ay — <b>$39</b> <s>($80)</s>\n"
            "▪️ Ömür Boyu — <b>$99</b> <s>($250)</s>\n\n"
            "💎 Not: Kripto ile ödeme. Onay sonrası aboneliğiniz "
            "otomatik aktifleştirilecektir.\n\n"
            "📌 <b>Ödeme yönteminizi seçin:</b>"
        ),
        "account_info": (
            "👤 <b>Hesabım</b>\n\n"
            "🆔 Kullanıcı ID: <code>{user_id}</code>\n"
            "🌐 Dil: {lang}\n"
            "💎 VIP Durumu: {vip_status}\n\n"
            "📌 Yükseltmek için VIP Satın Al'a tıklayın."
        ),
        "stats_text": (
            "📊 <b>SignalX Performansı (Son 7 Gün)</b>\n\n"
            "✅ Toplam Sinyal: {total}\n"
            "🟢 Kazanç: {wins}\n"
            "🔴 Kayıp: {losses}\n"
            "🎯 Başarı Oranı: %{win_rate}\n"
            "💰 Toplam Kar: %{profit}\n\n"
            "📈 Gerçek zamanlı güncellenir"
        ),
        "support_text": (
            "💬 <b>Destek</b>\n\n"
            "Sorularınız için:\n\n"
            "📩 İletişim: @Liberty_Help\n"
            "⏰ Yanıt süresi: 24 saat içinde\n\n"
            "Sık sorulan sorular:\n"
            "• VIP nasıl aktifleştirilir?\n"
            "• Ödeme onaylanmadı mı?\n"
            "• Sinyallerle ilgili yardım?"
        ),
        "select_language": "🌐 <b>Dilinizi seçin:</b>",
        "lang_changed": "✅ Dil Türkçe olarak değiştirildi!",
        "payment_info": (
            "💳 <b>Ödeme - {method}</b>\n\n"
            "Cüzdana yatırma işleminden sonra ekran görüntüsünü gönderin.\n"
            "Genellikle 30 dakikadan kısa sürede onaylanır.\n\n"
            "▪️ 1 Ay — <b>$39</b> <s>($80)</s>\n"
            "▪️ Ömür Boyu — <b>$99</b> <s>($250)</s>\n\n"
            "{method}:\n"
            "<code>{address}</code>"
        ),
        "receipt_text": (
            "🧾 <b>Dekont Gönder</b>\n\n"
            "Lütfen ödeme ekran görüntünüzü/işlem ID'nizi "
            "@Liberty_Help adresine gönderin.\n\n"
            "Şunları ekleyin:\n"
            "• Telegram kullanıcı adınız\n"
            "• Ödeme tutarı\n"
            "• İşlem ekran görüntüsü\n\n"
            "⏰ VIP'iniz 30 dakika - 12 saat içinde aktifleştirilecektir."
        ),
        "vip_active": "✅ Aktif",
        "vip_inactive": "❌ Aktif Değil",
    },
    "ru": {
        "welcome": (
            "🤖 <b>Добро пожаловать в SignalX!</b>\n\n"
            "📊 Самые точные крипто торговые сигналы\n\n"
            "✅ Высококачественные премиум сигналы\n"
            "✅ 85%+ Успешность\n"
            "✅ 30+ Сигналов ежедневно (Быстрее других)\n"
            "✅ Вход – Цели – СтопЛосс – Плечо\n\n"
            "🏆 <b>Доступные планы:</b>\n"
            "▪️ 1 Месяц — $39 (было $80)\n"
            "▪️ Навсегда — $99 (было $250)\n\n"
            "👇 Выберите опцию ниже:"
        ),
        "buy_vip": "🛒 Купить VIP 🏷",
        "my_account": "👤 Мой аккаунт 🧑",
        "stats": "📊 Статистика 📈",
        "support": "💬 Поддержка 📩",
        "language": "🌐 Язык 🏳️",
        "back": "⬅️ Назад",
        "select_plan": (
            "🏆 <b>Наши цены на подписку:</b>\n\n"
            "▪️ 1 Месяц — <b>$39</b> <s>($80)</s>\n"
            "▪️ Навсегда — <b>$99</b> <s>($250)</s>\n\n"
            "💎 Примечание: Оплата в крипто. Подписка будет "
            "активирована автоматически после подтверждения.\n\n"
            "📌 <b>Выберите способ оплаты:</b>"
        ),
        "account_info": (
            "👤 <b>Мой аккаунт</b>\n\n"
            "🆔 ID: <code>{user_id}</code>\n"
            "🌐 Язык: {lang}\n"
            "💎 VIP Статус: {vip_status}\n\n"
            "📌 Для обновления нажмите Купить VIP."
        ),
        "stats_text": (
            "📊 <b>Статистика SignalX (7 дней)</b>\n\n"
            "✅ Всего сигналов: {total}\n"
            "🟢 Прибыль: {wins}\n"
            "🔴 Убыток: {losses}\n"
            "🎯 Успешность: {win_rate}%\n"
            "💰 Общая прибыль: {profit}%\n\n"
            "📈 Обновляется в реальном времени"
        ),
        "support_text": (
            "💬 <b>Поддержка</b>\n\n"
            "По любым вопросам:\n\n"
            "📩 Контакт: @Liberty_Help\n"
            "⏰ Время ответа: в течение 24 часов"
        ),
        "select_language": "🌐 <b>Выберите язык:</b>",
        "lang_changed": "✅ Язык изменён на Русский!",
        "payment_info": (
            "💳 <b>Оплата - {method}</b>\n\n"
            "После перевода на кошелёк отправьте скриншот.\n"
            "Обычно подтверждение менее 30 минут.\n\n"
            "▪️ 1 Месяц — <b>$39</b> <s>($80)</s>\n"
            "▪️ Навсегда — <b>$99</b> <s>($250)</s>\n\n"
            "{method}:\n"
            "<code>{address}</code>"
        ),
        "receipt_text": (
            "🧾 <b>Отправить чек</b>\n\n"
            "Отправьте скриншот оплаты @Liberty_Help\n\n"
            "Укажите:\n"
            "• Ваш Telegram\n"
            "• Сумму оплаты\n"
            "• Скриншот транзакции\n\n"
            "⏰ VIP будет активирован в течение 30 мин - 12 часов."
        ),
        "vip_active": "✅ Активен",
        "vip_inactive": "❌ Не активен",
    },
    "ar": {
        "welcome": (
            "🤖 <b>مرحباً بك في SignalX!</b>\n\n"
            "📊 أدق إشارات تداول العملات الرقمية\n\n"
            "✅ إشارات بريميوم عالية الجودة\n"
            "✅ نسبة نجاح +85%\n"
            "✅ +30 إشارة يومياً (أسرع من الآخرين)\n"
            "✅ دخول – أهداف – وقف خسارة – رافعة\n\n"
            "🏆 <b>الخطط المتاحة:</b>\n"
            "▪️ شهر واحد — $39 (كان $80)\n"
            "▪️ مدى الحياة — $99 (كان $250)\n\n"
            "👇 اختر خياراً أدناه:"
        ),
        "buy_vip": "🛒 شراء VIP 🏷",
        "my_account": "👤 حسابي 🧑",
        "stats": "📊 الإحصائيات 📈",
        "support": "💬 الدعم 📩",
        "language": "🌐 اللغة 🏳️",
        "back": "⬅️ رجوع",
        "select_plan": (
            "🏆 <b>أسعار الاشتراك:</b>\n\n"
            "▪️ شهر — <b>$39</b> <s>($80)</s>\n"
            "▪️ مدى الحياة — <b>$99</b> <s>($250)</s>\n\n"
            "💎 ملاحظة: الدفع بالعملات الرقمية. سيتم تفعيل "
            "اشتراكك تلقائياً بعد التأكيد.\n\n"
            "📌 <b>اختر طريقة الدفع:</b>"
        ),
        "account_info": (
            "👤 <b>حسابي</b>\n\n"
            "🆔 المعرف: <code>{user_id}</code>\n"
            "🌐 اللغة: {lang}\n"
            "💎 حالة VIP: {vip_status}\n\n"
            "📌 للترقية، اضغط شراء VIP."
        ),
        "stats_text": (
            "📊 <b>أداء SignalX (آخر 7 أيام)</b>\n\n"
            "✅ إجمالي الإشارات: {total}\n"
            "🟢 ربح: {wins}\n"
            "🔴 خسارة: {losses}\n"
            "🎯 نسبة النجاح: {win_rate}%\n"
            "💰 إجمالي الربح: {profit}%\n\n"
            "📈 يتم التحديث في الوقت الفعلي"
        ),
        "support_text": (
            "💬 <b>الدعم</b>\n\n"
            "لأي أسئلة:\n\n"
            "📩 التواصل: @Liberty_Help\n"
            "⏰ وقت الرد: خلال 24 ساعة"
        ),
        "select_language": "🌐 <b>اختر لغتك:</b>",
        "lang_changed": "✅ تم تغيير اللغة إلى العربية!",
        "payment_info": (
            "💳 <b>الدفع - {method}</b>\n\n"
            "بعد الإيداع في المحفظة، أرسل لقطة الشاشة.\n"
            "عادة يتم التأكيد في أقل من 30 دقيقة.\n\n"
            "▪️ شهر — <b>$39</b> <s>($80)</s>\n"
            "▪️ مدى الحياة — <b>$99</b> <s>($250)</s>\n\n"
            "{method}:\n"
            "<code>{address}</code>"
        ),
        "receipt_text": (
            "🧾 <b>إرسال الإيصال</b>\n\n"
            "أرسل لقطة شاشة الدفع إلى @Liberty_Help\n\n"
            "أرفق:\n"
            "• اسم مستخدم Telegram\n"
            "• مبلغ الدفع\n"
            "• لقطة شاشة المعاملة\n\n"
            "⏰ سيتم تفعيل VIP خلال 30 دقيقة - 12 ساعة."
        ),
        "vip_active": "✅ مفعّل",
        "vip_inactive": "❌ غير مفعّل",
    },
    "es": {
        "welcome": (
            "🤖 <b>¡Bienvenido a SignalX!</b>\n\n"
            "📊 Las señales de trading crypto más precisas\n\n"
            "✅ Señales Premium de Alta Calidad\n"
            "✅ +85% Tasa de Éxito\n"
            "✅ +30 Señales Diarias (Más Rápido que Otros)\n"
            "✅ Entrada – Objetivos – StopLoss – Apalancamiento\n\n"
            "🏆 <b>Planes Disponibles:</b>\n"
            "▪️ 1 Mes — $39 (antes $80)\n"
            "▪️ De por vida — $99 (antes $250)\n\n"
            "👇 Selecciona una opción:"
        ),
        "buy_vip": "🛒 Comprar VIP 🏷",
        "my_account": "👤 Mi Cuenta 🧑",
        "stats": "📊 Estadísticas 📈",
        "support": "💬 Soporte 📩",
        "language": "🌐 Idioma 🏳️",
        "back": "⬅️ Volver",
        "select_plan": (
            "🏆 <b>Nuestros precios:</b>\n\n"
            "▪️ 1 Mes — <b>$39</b> <s>($80)</s>\n"
            "▪️ De por vida — <b>$99</b> <s>($250)</s>\n\n"
            "💎 Nota: Pago en crypto. Tu suscripción se "
            "activará automáticamente tras la confirmación.\n\n"
            "📌 <b>Selecciona tu método de pago:</b>"
        ),
        "account_info": (
            "👤 <b>Mi Cuenta</b>\n\n"
            "🆔 ID: <code>{user_id}</code>\n"
            "🌐 Idioma: {lang}\n"
            "💎 Estado VIP: {vip_status}\n\n"
            "📌 Para actualizar, haz clic en Comprar VIP."
        ),
        "stats_text": (
            "📊 <b>Rendimiento SignalX (7 días)</b>\n\n"
            "✅ Total Señales: {total}\n"
            "🟢 Ganancias: {wins}\n"
            "🔴 Pérdidas: {losses}\n"
            "🎯 Tasa de Éxito: {win_rate}%\n"
            "💰 Beneficio Total: {profit}%\n\n"
            "📈 Actualizado en tiempo real"
        ),
        "support_text": (
            "💬 <b>Soporte</b>\n\n"
            "Para cualquier pregunta:\n\n"
            "📩 Contacto: @Liberty_Help\n"
            "⏰ Tiempo de respuesta: 24 horas"
        ),
        "select_language": "🌐 <b>Selecciona tu idioma:</b>",
        "lang_changed": "✅ ¡Idioma cambiado a Español!",
        "payment_info": (
            "💳 <b>Pago - {method}</b>\n\n"
            "Después de depositar en la billetera, envía la captura.\n"
            "Normalmente se confirma en menos de 30 minutos.\n\n"
            "▪️ 1 Mes — <b>$39</b> <s>($80)</s>\n"
            "▪️ De por vida — <b>$99</b> <s>($250)</s>\n\n"
            "{method}:\n"
            "<code>{address}</code>"
        ),
        "receipt_text": (
            "🧾 <b>Enviar Recibo</b>\n\n"
            "Envía tu captura de pago a @Liberty_Help\n\n"
            "Incluye:\n"
            "• Tu usuario de Telegram\n"
            "• Monto del pago\n"
            "• Captura de la transacción\n\n"
            "⏰ Tu VIP se activará en 30 min - 12 horas."
        ),
        "vip_active": "✅ Activo",
        "vip_inactive": "❌ No Activo",
    },
    "zh": {
        "welcome": (
            "🤖 <b>欢迎来到 SignalX！</b>\n\n"
            "📊 最准确的加密货币交易信号\n\n"
            "✅ 高质量优质信号\n"
            "✅ 85%+ 成功率\n"
            "✅ 每日30+信号（比其他人更快）\n"
            "✅ 入场 – 目标 – 止损 – 杠杆\n\n"
            "🏆 <b>可用计划：</b>\n"
            "▪️ 1周 — $29（原价 $60）\n"
            "▪️ 1个月 — $49（原价 $100）\n"
            "▪️ 终身 — $149（原价 $500）\n\n"
            "👇 请选择以下选项："
        ),
        "buy_vip": "🛒 购买 VIP 🏷",
        "my_account": "👤 我的账户 🧑",
        "stats": "📊 统计 📈",
        "support": "💬 支持 📩",
        "language": "🌐 语言 🏳️",
        "back": "⬅️ 返回",
        "select_plan": (
            "🏆 <b>订阅价格：</b>\n\n"
            "▪️ 1个月 — <b>$39</b> <s>($80)</s>\n"
            "▪️ 终身 — <b>$99</b> <s>($250)</s>\n\n"
            "💎 注意：加密货币支付。确认后您的订阅将自动激活。\n\n"
            "📌 <b>选择支付方式：</b>"
        ),
        "account_info": (
            "👤 <b>我的账户</b>\n\n"
            "🆔 用户ID: <code>{user_id}</code>\n"
            "🌐 语言: {lang}\n"
            "💎 VIP状态: {vip_status}\n\n"
            "📌 升级请点击购买VIP。"
        ),
        "stats_text": (
            "📊 <b>SignalX 表现（7天）</b>\n\n"
            "✅ 总信号: {total}\n"
            "🟢 盈利: {wins}\n"
            "🔴 亏损: {losses}\n"
            "🎯 成功率: {win_rate}%\n"
            "💰 总利润: {profit}%\n\n"
            "📈 实时更新"
        ),
        "support_text": (
            "💬 <b>支持</b>\n\n"
            "如有任何问题：\n\n"
            "📩 联系: @Liberty_Help\n"
            "⏰ 回复时间: 24小时内"
        ),
        "select_language": "🌐 <b>选择语言：</b>",
        "lang_changed": "✅ 语言已更改为中文！",
        "payment_info": (
            "💳 <b>支付 - {method}</b>\n\n"
            "存入钱包后，发送截图。\n"
            "通常30分钟内确认。\n\n"
            "▪️ 1个月 — <b>$39</b> <s>($80)</s>\n"
            "▪️ 终身 — <b>$99</b> <s>($250)</s>\n\n"
            "{method}:\n"
            "<code>{address}</code>"
        ),
        "receipt_text": (
            "🧾 <b>发送收据</b>\n\n"
            "请将付款截图发送至 @Liberty_Help\n\n"
            "包括：\n"
            "• 您的Telegram用户名\n"
            "• 付款金额\n"
            "• 交易截图\n\n"
            "⏰ VIP将在30分钟-12小时内激活。"
        ),
        "vip_active": "✅ 已激活",
        "vip_inactive": "❌ 未激活",
    },
}

def t(user_id, key):
    """Get translated text for user."""
    user = get_user(user_id)
    lang = user.get("lang", "en")
    return TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, ""))


# === Payment Addresses ===
PAYMENT_ADDRESSES = {
    "USDT_TRC20": "YOUR_USDT_TRC20_ADDRESS",
    "USDT_BEP20": "YOUR_USDT_SOL_ADDRESS",
    "BTC": "YOUR_BTC_ADDRESS",
    "TRX": "YOUR_TRX_ADDRESS",
    "DOGE": "YOUR_DOGE_ADDRESS",
    "LTC": "YOUR_LTC_ADDRESS",
}

PLAN_PRICES = {
    "1month": "$39",
    "lifetime": "$99",
}


# === Keyboard Builders ===

def main_keyboard(user_id):
    """Main menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "buy_vip"), callback_data="buy_vip")],
        [
            InlineKeyboardButton(t(user_id, "my_account"), callback_data="my_account"),
            InlineKeyboardButton(t(user_id, "stats"), callback_data="stats"),
        ],
        [
            InlineKeyboardButton(t(user_id, "support"), callback_data="support"),
            InlineKeyboardButton(t(user_id, "language"), callback_data="language"),
        ],
    ])


def payment_keyboard(user_id):
    """Payment method selection keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("USDT TRC-20 ₮", callback_data="pay_USDT_TRC20"),
            InlineKeyboardButton("USDT SOL Network", callback_data="pay_USDT_BEP20"),
        ],
        [
            InlineKeyboardButton("BTC/Bitcoin ₿", callback_data="pay_BTC"),
            InlineKeyboardButton("TRX/Tron ₮", callback_data="pay_TRX"),
        ],
        [InlineKeyboardButton("⚡ DOGECoin Ð", callback_data="pay_DOGE")],
        [InlineKeyboardButton("⚡ LiteCoin Ł", callback_data="pay_LTC")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="back_main")],
    ])


def plan_keyboard(user_id):
    """Plan selection keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 Month — $39", callback_data="plan_1month")],
        [InlineKeyboardButton("Lifetime — $99", callback_data="plan_lifetime")],
        [InlineKeyboardButton(t(user_id, "back"), callback_data="back_main")],
    ])


def language_keyboard():
    """Language selection keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
        ],
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        ],
        [
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
            InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
        ],
    ])


def back_keyboard(user_id):
    """Simple back button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "back"), callback_data="back_main")],
    ])


# === Handlers ===

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = update.effective_user.id
    get_user(user_id)  # Ensure user exists in DB

    await update.message.reply_text(
        t(user_id, "welcome"),
        parse_mode="HTML",
        reply_markup=main_keyboard(user_id),
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button presses."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # === BACK TO MAIN ===
    if data == "back_main":
        await query.edit_message_text(
            t(user_id, "welcome"),
            parse_mode="HTML",
            reply_markup=main_keyboard(user_id),
        )

    # === BUY VIP ===
    elif data == "buy_vip":
        await query.edit_message_text(
            t(user_id, "select_plan"),
            parse_mode="HTML",
            reply_markup=payment_keyboard(user_id),
        )

    # === PLAN SELECTED (no longer needed, kept for compatibility) ===
    elif data.startswith("plan_"):
        plan = data.replace("plan_", "")
        context.user_data["selected_plan"] = plan
        await query.edit_message_text(
            t(user_id, "select_plan"),
            parse_mode="HTML",
            reply_markup=payment_keyboard(user_id),
        )

    # === PAYMENT METHOD SELECTED ===
    elif data.startswith("pay_"):
        method = data.replace("pay_", "")
        address = PAYMENT_ADDRESSES.get(method, "ADDRESS_NOT_SET")

        method_names = {
            "USDT_TRC20": "USDT TRC-20",
            "USDT_BEP20": "USDT SOL Network",
            "BTC": "Bitcoin (BTC)",
            "TRX": "Tron (TRX)",
            "LTC": "LiteCoin (LTC)",
            "DOGE": "DOGECoin (DOGE)",
        }

        text = t(user_id, "payment_info").format(
            method=method_names.get(method, method),
            address=address,
            amount="See plans above",
        )

        # Send Receipt + Back buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧾 Send Receipt", callback_data="send_receipt")],
            [InlineKeyboardButton(t(user_id, "back"), callback_data="buy_vip")],
        ])

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    # === SEND RECEIPT ===
    elif data == "send_receipt":
        text = t(user_id, "receipt_text")
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=back_keyboard(user_id),
        )

    # === MY ACCOUNT ===
    elif data == "my_account":
        user = get_user(user_id)
        lang_names = {
            "en": "English 🇬🇧",
            "tr": "Türkçe 🇹🇷",
            "ru": "Русский 🇷🇺",
            "ar": "العربية 🇸🇦",
            "es": "Español 🇪🇸",
            "zh": "中文 🇨🇳",
        }
        vip_status = t(user_id, "vip_active") if user.get("vip") else t(user_id, "vip_inactive")

        text = t(user_id, "account_info").format(
            user_id=user_id,
            lang=lang_names.get(user.get("lang", "en"), "English"),
            vip_status=vip_status,
        )

        # Account page has Buy VIP + Back buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, "buy_vip"), callback_data="buy_vip")],
            [InlineKeyboardButton(t(user_id, "back"), callback_data="back_main")],
        ])

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    # === STATS ===
    elif data == "stats":
        from config import ADMIN_USER_ID
        from fake_stats import format_fake_stats_message

        # Everyone sees fake stats (including admin via button)
        text = format_fake_stats_message()

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=back_keyboard(user_id),
        )

    # === SUPPORT ===
    elif data == "support":
        await query.edit_message_text(
            t(user_id, "support_text"),
            parse_mode="HTML",
            reply_markup=back_keyboard(user_id),
        )

    # === LANGUAGE ===
    elif data == "language":
        await query.edit_message_text(
            t(user_id, "select_language"),
            parse_mode="HTML",
            reply_markup=language_keyboard(),
        )

    # === LANGUAGE SELECTED ===
    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        set_user_lang(user_id, lang)

        await query.edit_message_text(
            t(user_id, "lang_changed") + "\n\n" + t(user_id, "welcome"),
            parse_mode="HTML",
            reply_markup=main_keyboard(user_id),
        )

    # === ADMIN: CONFIRM VIP (1 Month) ===
    elif data.startswith("admin_vip1m_"):
        from config import ADMIN_USER_ID
        if user_id != ADMIN_USER_ID:
            return

        target_uid = data.replace("admin_vip1m_", "")
        await _activate_vip(query, target_uid, plan="1month")

    # === ADMIN: CONFIRM VIP (Lifetime) ===
    elif data.startswith("admin_viplt_"):
        from config import ADMIN_USER_ID
        if user_id != ADMIN_USER_ID:
            return

        target_uid = data.replace("admin_viplt_", "")
        await _activate_vip(query, target_uid, plan="lifetime")

    # === ADMIN: REMOVE VIP ===
    elif data.startswith("admin_rmvip_"):
        from config import ADMIN_USER_ID
        if user_id != ADMIN_USER_ID:
            return

        target_uid = data.replace("admin_rmvip_", "")
        users = load_users()
        if target_uid in users:
            users[target_uid]["vip"] = False
            save_users(users)
            await query.edit_message_text(
                f"✅ VIP removed from user <code>{target_uid}</code>",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text(
                f"❌ User {target_uid} not found.",
                parse_mode="HTML",
            )


# === ADMIN COMMANDS ===

async def _activate_vip(query, target_uid, plan="lifetime"):
    """Activate VIP for a user with plan (1month or lifetime)."""
    import requests
    from datetime import datetime, timedelta
    from config import PREMIUM_CHANNEL_ID

    users = load_users()
    if target_uid not in users:
        # Create user entry if not exists
        users[target_uid] = {"lang": "en", "vip": False, "joined": ""}

    users[target_uid]["vip"] = True
    users[target_uid]["vip_plan"] = plan

    if plan == "1month":
        expire_date = (datetime.now() + timedelta(days=30)).isoformat()
        users[target_uid]["vip_expires"] = expire_date
        plan_text = "📅 1 Month (expires in 30 days)"
    else:
        users[target_uid]["vip_expires"] = None
        plan_text = "♾ Lifetime (never expires)"

    save_users(users)

    # Try to create invite link and send to user
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/createChatInviteLink"
        payload = {
            "chat_id": PREMIUM_CHANNEL_ID,
            "member_limit": 1,
            "name": f"VIP-{target_uid}-{plan}",
        }
        r = requests.post(url, json=payload, timeout=10)
        invite_data = r.json()

        if invite_data.get("ok"):
            invite_link = invite_data["result"]["invite_link"]

            # Send invite to user
            send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            if plan == "1month":
                expire_text = f"\n⏰ Your VIP expires in 30 days."
            else:
                expire_text = "\n♾ Your VIP never expires!"

            msg_payload = {
                "chat_id": int(target_uid),
                "text": (
                    "🎉 <b>Congratulations! Your VIP is now ACTIVE!</b>\n\n"
                    f"💎 Plan: <b>{plan_text}</b>{expire_text}\n\n"
                    "Click below to join the Premium channel:\n\n"
                    f"👉 {invite_link}\n\n"
                    "✅ You now have access to:\n"
                    "• Instant signals\n"
                    "• Full entry/target/SL details\n"
                    "• Priority support\n\n"
                    "Welcome to SignalX VIP! 🚀"
                ),
                "parse_mode": "HTML",
            }
            requests.post(send_url, json=msg_payload, timeout=10)

            await query.edit_message_text(
                f"✅ <b>VIP Activated!</b>\n\n"
                f"User: <code>{target_uid}</code>\n"
                f"Plan: {plan_text}\n"
                f"Invite link sent to user ✅",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text(
                f"✅ VIP activated for <code>{target_uid}</code>\n"
                f"Plan: {plan_text}\n"
                f"⚠️ Could not create invite link. Add manually.",
                parse_mode="HTML",
            )
    except Exception as e:
        await query.edit_message_text(
            f"✅ VIP activated for <code>{target_uid}</code>\n"
            f"Plan: {plan_text}\n"
            f"⚠️ Error: {e}",
            parse_mode="HTML",
        )


def check_expired_vips():
    """Check and remove expired VIP users. Call this periodically."""
    import requests
    from datetime import datetime
    from config import PREMIUM_CHANNEL_ID

    users = load_users()
    expired = []

    for uid, data in users.items():
        if not data.get("vip"):
            continue
        if data.get("vip_plan") == "lifetime":
            continue
        if data.get("vip_expires"):
            try:
                expire_date = datetime.fromisoformat(data["vip_expires"])
                if datetime.now() > expire_date:
                    expired.append(uid)
            except:
                continue

    for uid in expired:
        users[uid]["vip"] = False
        users[uid]["vip_plan"] = None
        users[uid]["vip_expires"] = None

        # Try to kick from premium channel
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/banChatMember"
            requests.post(url, json={
                "chat_id": PREMIUM_CHANNEL_ID,
                "user_id": int(uid),
            }, timeout=10)

            # Immediately unban so they can rejoin if they pay again
            url2 = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/unbanChatMember"
            requests.post(url2, json={
                "chat_id": PREMIUM_CHANNEL_ID,
                "user_id": int(uid),
                "only_if_banned": True,
            }, timeout=10)
        except:
            pass

        # Notify user
        try:
            send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(send_url, json={
                "chat_id": int(uid),
                "text": (
                    "⏰ <b>Your VIP subscription has expired!</b>\n\n"
                    "Your access to the Premium channel has been removed.\n\n"
                    "💎 To renew, click /start and select Buy VIP.\n\n"
                    "We hope to see you back! 🙏"
                ),
                "parse_mode": "HTML",
            }, timeout=10)
        except:
            pass

        print(f"[VIP] Expired: {uid} removed from VIP")

    if expired:
        save_users(users)

    return expired


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - admin panel."""
    from config import ADMIN_USER_ID
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    users = load_users()
    total_users = len(users)
    vip_users = len([u for u in users.values() if u.get("vip")])

    text = (
        "🔐 <b>ADMIN PANEL</b>\n\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"💎 VIP Users: <b>{vip_users}</b>\n\n"
        "Commands:\n"
        "/addvip <code>USER_ID</code> — Give VIP to user\n"
        "/rmvip <code>USER_ID</code> — Remove VIP from user\n"
        "/users — List all users\n"
        "/viplist — List VIP users\n"
    )

    await update.message.reply_text(text, parse_mode="HTML")


async def addvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addvip USER_ID - give VIP to a user."""
    from config import ADMIN_USER_ID
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /addvip <code>USER_ID</code>\n\n"
            "Example: /addvip 123456789",
            parse_mode="HTML",
        )
        return

    target_uid = context.args[0]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 1 Month", callback_data=f"admin_vip1m_{target_uid}"),
            InlineKeyboardButton("♾ Lifetime", callback_data=f"admin_viplt_{target_uid}"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="back_main")],
    ])

    await update.message.reply_text(
        f"🔐 <b>Add VIP</b>\n\n"
        f"User ID: <code>{target_uid}</code>\n\n"
        f"Select plan:\n"
        f"• 📅 <b>1 Month</b> — Auto-expires after 30 days\n"
        f"• ♾ <b>Lifetime</b> — Never expires\n",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def rmvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rmvip USER_ID - remove VIP from a user."""
    from config import ADMIN_USER_ID
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /rmvip <code>USER_ID</code>",
            parse_mode="HTML",
        )
        return

    target_uid = context.args[0]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Remove VIP", callback_data=f"admin_rmvip_{target_uid}"),
            InlineKeyboardButton("❌ Cancel", callback_data="back_main"),
        ],
    ])

    await update.message.reply_text(
        f"🔐 <b>Remove VIP</b>\n\n"
        f"User ID: <code>{target_uid}</code>\n\n"
        f"Confirm removal?",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users - list all users."""
    from config import ADMIN_USER_ID
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        return

    users = load_users()
    if not users:
        await update.message.reply_text("No users yet.")
        return

    lines = []
    for uid, data in list(users.items())[:50]:  # Max 50
        vip_icon = "💎" if data.get("vip") else "👤"
        lang = data.get("lang", "en")
        lines.append(f"{vip_icon} <code>{uid}</code> [{lang}]")

    text = f"👥 <b>Users ({len(users)} total)</b>\n\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="HTML")


async def viplist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /viplist - list VIP users only."""
    from config import ADMIN_USER_ID
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        return

    users = load_users()
    vip_users = {uid: data for uid, data in users.items() if data.get("vip")}

    if not vip_users:
        await update.message.reply_text("No VIP users yet.")
        return

    lines = []
    for uid, data in vip_users.items():
        lang = data.get("lang", "en")
        plan = data.get("vip_plan", "?")
        expires = data.get("vip_expires", "never")
        lines.append(f"💎 <code>{uid}</code> [{lang}] Plan: {plan} Exp: {expires}")

    text = f"💎 <b>VIP Users ({len(vip_users)})</b>\n\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="HTML")


async def realstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /realstats - show REAL stats (admin only)."""
    from config import ADMIN_USER_ID
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    try:
        from signal_tracker import get_all_time_stats
        stats = get_all_time_stats()

        text = (
            "🔐 <b>REAL STATS (Admin Only)</b>\n\n"
            f"📡 Total Signals: <b>{stats['total_signals']}</b>\n"
            f"🟢 Wins: <b>{stats['wins']}</b>\n"
            f"🔴 Losses: <b>{stats['losses']}</b>\n"
            f"⏳ Pending: <b>{stats['pending']}</b>\n"
            f"🎯 Win Rate: <b>{stats['win_rate']:.1f}%</b>\n"
            f"💰 Total Profit: <b>{stats['total_profit_percent']:.2f}%</b>\n"
            f"💹 Avg Profit: <b>{stats['avg_profit_percent']:.2f}%</b>\n"
        )
    except Exception as e:
        text = f"❌ Error loading stats: {e}"

    await update.message.reply_text(text, parse_mode="HTML")


def main():
    """Start the user-facing bot."""
    print("""
    ╔══════════════════════════════════════════╗
    ║     🤖 SignalX - User Bot               ║
    ║     ━━━━━━━━━━━━━━━━━━━━━━━━━━          ║
    ║     Handling /start, payments, etc.     ║
    ╚══════════════════════════════════════════╝
    """)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # User Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Admin Handlers
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("addvip", addvip_command))
    app.add_handler(CommandHandler("rmvip", rmvip_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("viplist", viplist_command))
    app.add_handler(CommandHandler("realstats", realstats_command))

    print("[✅] SignalX User Bot is running!")
    print("[*] Waiting for /start commands...\n")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
