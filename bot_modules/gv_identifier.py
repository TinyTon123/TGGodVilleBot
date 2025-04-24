from asyncio import sleep

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
import requests

from config_data.config import Config, load_config
from sql_db_module.db_manipuation import (
    delete_user,
    find_user_by_gv_name,
    find_user_by_tg_id,
    get_all_names,
    upsert_user
)

router: Router = Router()

config: Config = load_config()
allowed_admins: set[int] = config.chats_and_admins.allowed_admins


@router.message(
    Command("this"),
    F.reply_to_message,
    F.from_user.id.in_(allowed_admins),
    ~F.reply_to_message.from_user.is_bot,
)
async def set_link_to_gv(message: Message, command: CommandObject) -> None:
    """Записывает в БД id пользователя и его никнеймы в ТГ и ГВ."""
    gv_name = command.args
    if gv_name:
        if find_user_by_gv_name(gv_name) is None:
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


@router.message(Command("del"), F.from_user.id.in_(allowed_admins))
async def delete_user_from_db(message: Message, command: CommandObject) -> None:
    """Удаляет из БД пользователя по id в ТГ или нику в ГВ."""
    if command.args and not message.reply_to_message:
        result = delete_user(command.args)
    elif message.reply_to_message and not command.args:
        result = delete_user(message.reply_to_message.from_user.id)
    else:
        result = 'Непонятно, кого удаляем.'
    await message.answer(result)


@router.message(Command("members"), F.from_user.id.in_(allowed_admins))
async def check_guild_members(message: Message) -> None:
    await message.answer('Задачу понял — запрашиваю сервер ГВ')
    all_names: list[str] = get_all_names()
    url: str = 'https://godville.net/gods/api/'
    in_guild: list = []
    left_guild: list = []
    error_names: list = []
    for name in all_names:
        response = requests.get(url + name)
        if response.status_code == 200:
            clan = response.json()['clan']
            string = f'<a href="https://godville.net/gods/{name}">{name}</a>'
            if clan == 'Дом горячих кузнецов':
                in_guild.append(string)
            else:
                left_guild.append(string)
        else:
            error_names.append(name)
        await sleep(1)

    reply_text: str = '\---===== Дом горячих кузнецов =====---/\n\n'
    for player in in_guild:
        reply_text += f'{player}\n'

    reply_text += '\n------- Покинули ДГК -------\n\n'
    for player in left_guild:
        reply_text += f'{player}\n'

    reply_text += '\n------- Сменили имя -------\n\n'
    for player in error_names:
        reply_text += f'{player}\n'

    await message.answer(reply_text)
