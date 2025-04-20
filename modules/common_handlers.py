from aiogram import Router, types, html
from aiogram.filters import Command

router: Router = Router()


@router.message(Command(commands=["help"]))
async def command_help(message: types.Message) -> None:
    manual: str = (
        "Привет!\n\n"
        "<b>Бот умеет связывать аккаунт в ТГ с профилем в ГВ</b>\n\n"
        "Команды:\n\n"
        "/help — помощь (эта страница).\n\n"
        f"/this <code>{html.quote('<ник в ГВ>')}</code> — привязать аккаунт.\n"
        "Команда обязательно должна быть дана реплаем на сообщение "
        "человека, которого требуется связать с аккаунтом в ГВ. "
        "После команды должен быть никнейм.\n\n"
        f"/who [<code>{html.quote('<ник в ГВ>')}</code>] — показать привязанный аккаунт.\n"
        "Команду можно дать либо реплаем (тогда бот пришлет ссылку на профиль игрока в ГВ), "
        "либо после команды указать ник в ГВ (тогда бот пришлет ссылку на аккаунт в ТГ).\n\n"
        f"/del [<code>{html.quote('<ник в ГВ>')}</code>] — удалить привязку.\n"
        "Команду можно дать либо реплаем, либо после команды указать ник в ГВ.\n\n"
        "<i>By <a href='tg://user?id=391639940'>Tiny🍀Ton</a></i>"
    )

    await message.reply(manual)
