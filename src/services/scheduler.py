import asyncio
from datetime import datetime, timedelta
import logging
import aiohttp
from sqlalchemy import select
from src.database.connector import db
from src.models.avito_accounts import AvitoAccount
from src.services.auth import refresh_avito_token

logger = logging.getLogger(__name__)

class TokenRefresher:
    def __init__(self):
        self._task = None
        self._running = False

    async def start(self):
        """Запускает периодическое обновление токенов"""
        self._running = True
        self._task = asyncio.create_task(self._run_forever())

    async def stop(self):
        """Останавливает обновление токенов"""
        self._running = False
        if self._task:
            await self._task

    async def _run_forever(self):
        """Бесконечный цикл обновления"""
        while self._running:
            try:
                await self._refresh_tokens()
                await asyncio.sleep(180)  # Проверка каждые 5 минут
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                await asyncio.sleep(60)

    async def _refresh_tokens(self):
        """Основная логика обновления токенов"""
        async with db.session_factory() as session:
            try:
                result = await session.execute(
                    select(AvitoAccount).where(
                        AvitoAccount.expires_at < datetime.now() + timedelta(minutes=30)
                    )
                )
                accounts = result.scalars().all()

                if not accounts:
                    logger.debug("No tokens to refresh")
                    return

                for account in accounts:
                    try:
                        if not account.refresh_token:
                            logger.warning(f"Account {account.id} has no refresh token")
                            continue

                        new_tokens = await refresh_avito_token(account.refresh_token)
                        
                        account.access_token = new_tokens['access_token']
                        account.refresh_token = new_tokens.get('refresh_token', account.refresh_token)
                        account.expires_at = datetime.now() + timedelta(
                            seconds=new_tokens['expires_in']
                        )
                        
                        await session.commit()
                        logger.info(f"Tokens refreshed for account {account.id}")

                    except aiohttp.ClientResponseError as e:
                        logger.error(f"HTTP error for account {account.id}: {e.status}")
                        if e.status == 400:
                            logger.warning(f"Invalidating refresh token for account {account.id}")
                            account.refresh_token = None
                            await session.commit()
                    except Exception as e:
                        logger.error(f"Error refreshing account {account.id}: {str(e)}")
                        await session.rollback()

            except Exception as e:
                logger.error(f"Global refresh error: {str(e)}")
                await session.rollback()
                raise

# Глобальный экземпляр
token_refresher = TokenRefresher()

        
