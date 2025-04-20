from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from SQL.db_manipuation import delete_user, find_user_by_tg_id, find_user_by_gv_name, upsert_user

router: Router = Router()

@router.message(Command("this"), F.reply_to_message, ~F.reply_to_message.from_user.is_bot)
async def set_link_to_gv(message: Message, command: CommandObject) -> None:
    """Записывает в БД id пользователя и его никнеймы в ТГ и ГВ."""
    gv_name = command.args
    if gv_name:
        if find_user_by_gv_name(gv_name, ) is None:
            user = message.reply_to_message.from_user
            tg_name = f'{user.first_name} {user.last_name}' if user.last_name else user.first_name
            upsert_user(user.id, tg_name, gv_name)
            await message.answer(
                f'Записал:\n\n'
                f'Ник в ГВ — <a href="https://godville.net/gods/{gv_name}">{gv_name}</a>\n'
                f'Юзер в ТГ — <a href="tg://user?id={user.id}">{tg_name}</a>'
            )
        else:
            await message.answer('Ошибка! Такой никнейм уже есть.')
    else:
        await message.answer(text='После команды укажите никнейм.')


@router.message(Command("who"))
async def get_user_from_db(message: Message, command: CommandObject) -> None:
    """Получает из БД никнейм юзера и возвращает ссылку на профиль в ГВ или в ТГ."""
    if command.args and not message.reply_to_message:
        # Если пользователь найден, то возвращаем кортеж (tg_id, tg_name)
        user = find_user_by_gv_name(command.args)
        if user:
            tg_id, tg_name = user
            await message.answer(
                f'В ТГ это <a href="tg://user?id={tg_id}">{tg_name}</a>'
            )
            return
        # Если не найден, то возвращаем None
        else:
            await message.answer('Не знаю, кто это.')
            return
    if message.reply_to_message and not command.args:
        user_gv_name = find_user_by_tg_id(message.reply_to_message.from_user.id)
        if user_gv_name:
            await message.answer(
                f'В ГВ это <a href="https://godville.net/gods/{user_gv_name}">{user_gv_name}</a>'
            )
            return
        else:
            await message.answer('Не знаю, кто это.')
            return
    await message.answer('Мне нужен либо ник в ГВ, либо реплай на сообщение.')

@router.message(Command("del"))
async def delete_user_from_db(message: Message, command: CommandObject) -> None:
    """Удаляет из БД пользователя по id в ТГ или нику в ГВ."""
    if command.args and not message.reply_to_message:
        result = delete_user(command.args)
    elif message.reply_to_message and not command.args:
        result = delete_user(message.reply_to_message.from_user.id)
    else:
        result = 'Непонятно, кого удаляем.'
    await message.answer(result)
