"""
Bilim Jangi — bot orqali to'lov tasdiqlash oqimi (3-bosqich).

Oqim:
  1. Foydalanuvchi Web App'da pulga mahsulot/Premium/VIP-Vaucher sotib olishni
     boshlaydi -> backend PaymentOrder yaratadi (status=awaiting_screenshot).
  2. Foydalanuvchi karta raqamiga pul o'tkazadi va screenshot rasmni
     TO'G'RIDAN-TO'G'RI shu botga (Telegram chatga) yuboradi.
  3. Bot rasmni qabul qilib, foydalanuvchining eng oxirgi "awaiting_screenshot"
     buyurtmasini topadi, screenshot'ni tasdiqlovchiga (sotuvchi yoki admin)
     ✅/❌ tugmalari bilan yuboradi.
  4. Tasdiqlovchi ✅ bossa — mahsulot/Premium/Vaucher foydalanuvchiga beriladi.
     ❌ bossa (agar tasdiqlovchi sotuvchi bo'lsa) — buyurtma adminga yuboriladi.
"""
import logging

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app import crud
from app.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger("bilim_jangi.bot.payment")

payment_router = Router()


def _approve_reject_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_approve_{order_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_reject_{order_id}"),
            ]
        ]
    )


@payment_router.message(F.photo)
async def handle_payment_screenshot(message: Message, bot: Bot) -> None:
    async with AsyncSessionLocal() as db:
        user = await crud.get_user_by_telegram_id(db, message.from_user.id)
        if user is None:
            return  # Bilim Jangi foydalanuvchisi emas — e'tiborsiz qoldiramiz

        order = await crud.get_latest_awaiting_order(db, user)
        if order is None:
            await message.answer(
                "Hozircha kutilayotgan to'lov topilmadi. Avval Web App orqali xarid boshlang."
            )
            return

        product = await crud.get_product(db, order.product_id)
        photo_file_id = message.photo[-1].file_id
        order.screenshot_file_id = photo_file_id
        order.status = "pending_approval"
        await db.commit()

        # Tasdiqlovchini aniqlaymiz
        approver_telegram_id = None
        if order.approver_role == "seller" and product and product.seller_user_id:
            seller = await crud.get_user_by_id(db, product.seller_user_id)
            if seller:
                approver_telegram_id = seller.telegram_id
        if approver_telegram_id is None:
            approver_telegram_id = settings.ADMIN_TELEGRAM_ID

    await message.answer(
        "✅ Screenshot qabul qilindi! Tasdiqlanishini kuting — bu odatda tez amalga oshadi."
    )

    if approver_telegram_id:
        caption = (
            f"💳 Yangi to'lov tasdig'i so'rovi\n\n"
            f"Xaridor: {message.from_user.full_name} (@{message.from_user.username or '—'})\n"
            f"Mahsulot: {product.name if product else '—'}\n"
            f"Summa: {float(order.amount):.0f} so'm\n"
            f"Buyurtma ID: {order.id}"
        )
        try:
            await bot.send_photo(
                chat_id=approver_telegram_id,
                photo=photo_file_id,
                caption=caption,
                reply_markup=_approve_reject_keyboard(order.id),
            )
        except Exception:
            logger.exception("Tasdiqlovchiga xabar yuborib bo'lmadi (chat topilmagan bo'lishi mumkin)")


@payment_router.callback_query(F.data.startswith("pay_approve_"))
async def handle_approve(callback: CallbackQuery, bot: Bot) -> None:
    order_id = int(callback.data.split("_")[-1])
    async with AsyncSessionLocal() as db:
        from app import models

        order = await db.get(models.PaymentOrder, order_id)
        if order is None or order.status != "pending_approval":
            await callback.answer("Bu buyurtma allaqachon ko'rib chiqilgan", show_alert=True)
            return

        approver_user = await crud.get_user_by_telegram_id(db, callback.from_user.id)
        product = await crud.get_product(db, order.product_id)
        is_seller_owner = product and product.seller_user_id and approver_user and product.seller_user_id == approver_user.id
        is_admin = approver_user and approver_user.is_admin
        if not (is_seller_owner or is_admin):
            await callback.answer("Sizda bu amalni bajarish huquqi yo'q", show_alert=True)
            return

        await crud.finalize_payment_order(db, order, approved=True)
        buyer = await crud.get_user_by_id(db, order.user_id)

    await callback.message.edit_caption(caption=(callback.message.caption or "") + "\n\n✅ TASDIQLANDI")
    await callback.answer("Tasdiqlandi ✅")
    if buyer:
        try:
            await bot.send_message(
                buyer.telegram_id,
                f"🎉 To'lovingiz tasdiqlandi! \"{product.name if product else ''}\" hisobingizga qo'shildi.",
            )
        except Exception:
            pass


@payment_router.callback_query(F.data.startswith("pay_reject_"))
async def handle_reject(callback: CallbackQuery, bot: Bot) -> None:
    order_id = int(callback.data.split("_")[-1])
    async with AsyncSessionLocal() as db:
        from app import models

        order = await db.get(models.PaymentOrder, order_id)
        if order is None or order.status != "pending_approval":
            await callback.answer("Bu buyurtma allaqachon ko'rib chiqilgan", show_alert=True)
            return

        approver_user = await crud.get_user_by_telegram_id(db, callback.from_user.id)
        product = await crud.get_product(db, order.product_id)
        is_seller_owner = product and product.seller_user_id and approver_user and product.seller_user_id == approver_user.id
        is_admin = approver_user and approver_user.is_admin
        if not (is_seller_owner or is_admin):
            await callback.answer("Sizda bu amalni bajarish huquqi yo'q", show_alert=True)
            return

        buyer = await crud.get_user_by_id(db, order.user_id)

        if order.approver_role == "seller" and not is_admin:
            # Sotuvchi rad etdi -> adminga yuboriladi (spec talabi)
            order.approver_role = "admin"
            order.status = "pending_approval"
            await db.commit()
            escalate = True
        else:
            order.status = "rejected"
            from datetime import datetime, timezone

            order.decided_at = datetime.now(timezone.utc)
            await db.commit()
            escalate = False

    await callback.message.edit_caption(
        caption=(callback.message.caption or "") + ("\n\n⏫ ADMINGA YUBORILDI" if escalate else "\n\n❌ RAD ETILDI")
    )
    await callback.answer("Bajarildi")

    if escalate and settings.ADMIN_TELEGRAM_ID and order.screenshot_file_id:
        caption = (
            f"💳 (Sotuvchi rad etdi) To'lov tasdig'i so'rovi\n\n"
            f"Mahsulot: {product.name if product else '—'}\n"
            f"Summa: {float(order.amount):.0f} so'm\n"
            f"Buyurtma ID: {order.id}"
        )
        try:
            await bot.send_photo(
                chat_id=settings.ADMIN_TELEGRAM_ID,
                photo=order.screenshot_file_id,
                caption=caption,
                reply_markup=_approve_reject_keyboard(order.id),
            )
        except Exception:
            logger.exception("Adminga eskalatsiya xabari yuborilmadi")
    elif not escalate and buyer:
        try:
            await bot.send_message(buyer.telegram_id, "❌ Afsuski, to'lovingiz rad etildi. Admin bilan bog'laning.")
        except Exception:
            pass
