# -*- coding: utf-8 -*-

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from modules import common_handlers, gv_identifier

from config_data.config import load_config, Config


ALLOWED_CHATS = {-1001766161547, 391639940, 344326930}  # ДГК, Я, Г-жа

# Загружаем конфиг в переменную config
config: Config = load_config()
bot_token: str = config.tg_bot.token


async def main() -> None:
    dp: Dispatcher = Dispatcher()
    dp.message.filter(F.chat.id.in_(ALLOWED_CHATS))
    dp.include_router(common_handlers.router)
    dp.include_router(gv_identifier.router)
    bot: Bot = Bot(bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(391639940, "Поехали!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
