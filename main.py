# -*- coding: utf-8 -*-

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot_modules import common_handlers, gv_identifier
from config_data.config import Config, load_config


# Загружаем конфиг в переменную config
config: Config = load_config()
bot_token: str = config.tg_bot.token
allowed_chats: set[int] = config.chats_and_admins.allowed_chats


async def main() -> None:
    dp: Dispatcher = Dispatcher()
    dp.message.filter(F.chat.id.in_(allowed_chats))
    dp.include_router(common_handlers.router)
    dp.include_router(gv_identifier.router)
    bot: Bot = Bot(bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(391639940, "Поехали!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
