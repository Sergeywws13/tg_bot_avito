from datetime import timezone, datetime
from aiogram import F, Router, types
from aiogram.filters import Command
from sqlalchemy import select
import sqlalchemy
from src.models import AvitoAccount
from src.database.connector import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from src.models.manager import Manager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = Router()

@router.message(Command("accounts"))
async def handle_accounts_command(message: types.Message):
    """Показывает список подключенных аккаунтов"""
    async with db.session_factory() as session:
        try:
            # Получаем менеджера
            result = await session.execute(
                select(Manager)
                .where(Manager.telegram_id == message.from_user.id)
            )
            manager = result.scalar_one_or_none()

            # Создаем менеджера если не существует
            if not manager:
                try:
                    manager = Manager(telegram_id=message.from_user.id)
                    session.add(manager)
                    await session.commit()
                except sqlalchemy.exc.IntegrityError:
                    await session.rollback()
                    result = await session.execute(
                        select(Manager)
                        .where(Manager.telegram_id == message.from_user.id)
                    )
                    manager = result.scalar_one_or_none()

            if not manager:
                return await message.answer("🚫 Ошибка доступа")

            # Инициализируем переменную accounts
            accounts = []
            
            # Получаем аккаунты
            result = await session.execute(
                select(AvitoAccount)
                .where(AvitoAccount.manager_id == manager.id)
            )
            accounts = result.scalars().all()  # Теперь accounts всегда будет списком

            if not accounts:
                return await message.answer("🚫 Нет подключенных аккаунтов")

            # Формируем сообщение
            builder = InlineKeyboardBuilder()
            text = "📋 Список подключенных аккаунтов:\n\n"
            
            for i, acc in enumerate(accounts, 1):
                status = "✅ Активен" if acc.expires_at > datetime.now(timezone.utc) else "❌ Истек"
                text += (
                    f"{i}. {acc.account_name}\n"
                    f"ID: {acc.id}\n"
                    f"Статус: {status}\n"
                    f"Добавлен: {acc.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                )
                
                builder.button(
                    text=f"❌ Удалить {acc.id}", 
                    callback_data=f"delete_account_{acc.id}"
                )

            builder.adjust(2)
            await message.answer(
                text,
                reply_markup=builder.as_markup()
            )

        except Exception as e:
            logger.error(f"Error in accounts command: {str(e)}")
            await message.answer("⚠️ Произошла ошибка при получении данных")


@router.callback_query(F.data.startswith("delete_account_"))
async def handle_delete_account(callback: types.CallbackQuery):
    try:
        # Получаем ID аккаунта из callback_data
        account_id_str = callback.data.removeprefix("delete_account_")
        
        # Проверяем что ID - число
        if not account_id_str.isdigit():
            await callback.answer("⚠️ Неверный формат ID аккаунта")
            return
            
        account_id = int(account_id_str)

        async with db.session_factory() as session:
            # Получаем аккаунт с проверкой прав доступа
            result = await session.execute(
                select(AvitoAccount)
                .join(Manager)
                .where(
                    AvitoAccount.id == account_id,
                    Manager.telegram_id == callback.from_user.id
                )
            )
            account = result.scalar_one_or_none()

            if not account:
                await callback.answer("⚠️ Аккаунт не найден или нет прав доступа")
                return

            # Удаляем аккаунт
            account_name = account.account_name
            await session.delete(account)
            await session.commit()

            # Обновляем сообщение
            await callback.message.edit_text(
                f"✅ Аккаунт успешно удален:\n{account_name} (ID: {account_id})",
                reply_markup=None
            )
            await callback.answer()

    except ValueError as ve:
        logger.error(f"Value error in delete account: {ve}")
        await callback.answer("⚠️ Ошибка в формате запроса")
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка при удалении")