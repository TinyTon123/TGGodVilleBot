from aiogram.filters import Command, CommandObject
from aiogram import Router, F, html
from aiogram.types import Message

import redis

redis_db: redis = redis.Redis(db=1)
router: Router = Router()


# Функция для фильтра, который определяет, правильный ли тип запоминаемого сообщения:
# текст, фото, гифка, видео, кружочек, аудиозапись, голос или стикер
def content_type_filter(message: Message) -> bool | dict[str, any]:
    reply: Message | None = message.reply_to_message
    if reply:
        # если тип сообщения соответствует одному из указанных,
        # то в content будет записано содержимое соответствующего поля сообщения
        content = (reply.text or reply.photo or reply.animation or reply.voice or
                   reply.video or reply.sticker or reply.video_note or reply.audio)
        # если content не пустой, то функция вернет его содержимое,
        # которое нужно будет использовать в хендлере
        if content:
            return {'content': content}
        return False
    else:
        return False


# хендлер для сохранения триггера
@router.message(Command(commands=["add_trigger"]), content_type_filter)
async def display_trigger(message: Message, content: any, command: CommandObject) -> None:

    # Если пользователь указал имя триггера (то есть command.args не пустой),
    # то во избежание дублей удаляем из БД соответствующий ключ
    if command.args:
        redis_db.delete(f"{message.chat.id}_{command.args.lower()}")

        # Если тип запоминаемого сообщения — текст, то в БД вносится пара ключ-значение
        # по шаблону <id чата>_<имя триггера>: <текст сообщения, в ответ на которое дана команда>
        if isinstance(content, str):
            redis_db.set(f"{message.chat.id}_{command.args.lower()}", f"{content}")

        # Если тип запоминаемого сообщения — фотография или картинка, то в переменную content
        # будет записан список из трех элементов, каждый из которых содержит поле file_id.
        # Вносим в БД пару ключ-значение по шаблону
        # <id чата>_<имя триггера>: <photo> _|_ <значение file_id> _|_ <подпись к фото/картинке>
        elif isinstance(content, list):
            redis_db.set(f"{message.chat.id}_{command.args.lower()}",
                  f"photo _|_ {content[-1].file_id} _|_ {message.reply_to_message.caption}")

        # Если тип сообщения любой другой из допустимых, то в БД добавляем запись по шаблону
        # <id чата>_<имя триггера>: <тип сообщения> _|_ <значение file_id> _|_ <подпись к фото/картинке>
        else:
                                                                    # костыль для перевода
                                                                    # 'VideoNote' в 'video_note'
            content_type_str = str(type(content)).split('.')[-1][:-2].replace('N', '_n').lower()
            redis_db.set(f"{message.chat.id}_{command.args.lower()}",
                  f"{content_type_str} _|_ {content.file_id} _|_ {message.reply_to_message.caption}")

        # Отправляем сообщение, что новый триггер успешно добавлен
        await message.answer(f'Триггер <code>{html.quote(f"{command.args.lower()}")}</code> добавлен')

    else:
        await message.answer(f"После команды необходимо указать название триггера")


# Хендлер для удаления триггера
@router.message(Command(commands=["del_trigger"]))
async def delete_trigger(message: Message, command: CommandObject) -> None:
    # Если после команды /del_tigger есть имя триггера, то БД пытается удалить
    # соответствующую строку
    if command.args:
        deleted: int = redis_db.delete(f"{message.chat.id}_{command.args.lower()}")

        # В случае, если такой ключ в БД был, в переменную deleted будет записана единица,
        # в ином случае — ноль
        if deleted:
            # Отправляем сообщение, что триггер успешно удален
            await message.answer(f'Триггер <code>{html.quote(f"{command.args.lower()}")}</code> удален')
        else:
            # Отправляем сообщение, что такого триггера не было
            await message.answer(f'Такого триггера не было, но я его на всякий случай удалил {html.quote(">.<")}')

    # Если пользователь не указал имя триггера, бот не поймет, что именно нужно удалить
    else:
        await message.answer('Что удаляем? Укажите название триггера')


# Хендлер для отображения списка триггеров
@router.message(Command(commands=["show_triggers"]))
async def show_triggers(message: Message) -> None:

    # Создаем кортеж со всеми ключами, которые соответствуют шаблону
    # <id чата, в котором вызывают команду_*>.
    # Метод scan возвращает количество найденных ключей и их список.
    triggers: set = {i.decode("utf-8") for i in redis_db.scan(match=f'{message.chat.id}_*', count=1000)[1]}

    # Выстраиваем ключи построчно и отвечаем пользователю
    text: str = 'Список триггеров:\n\n'
    for trigger in triggers:
        text += f'<code>{trigger[trigger.find("_")+1:]}</code>\n'

    await message.answer(text)


# Хендлер для вызова триггера
@router.message(F.text)
async def display_trigger(message: Message) -> None:
    # Переводим текст в байтовую строку и ищем в БД соответствующий ключ
    # по шаблону <id чата>_<имя триггера>
    chat_trigger: bytes = f'{message.chat.id}_{message.text.lower().strip(".")}'.encode("utf-8")
    if chat_trigger in redis_db.scan(match=f'{message.chat.id}_*', count=1000)[1]:

        # Если ключ найден, то вытаскиваем его значение и делим строку по комбинации символов ' _|_ '
        trigger_text: str = redis_db.get(chat_trigger).decode("utf-8")
        trigger_text: list[str] = trigger_text.split(' _|_ ')

        # Если значение ключа не текст, то вернется список по шаблону
        # ['<тип сообщения>', '<file_id контента>', '<caption> (или None, если подписи к контенту не было)']
        if len(trigger_text) > 1:
            # Из списка формируем метод ответа по шаблону message.answer_<тип сообщения>,
            # и передаем ему file_id, а также caption, если он неравен None
            await (getattr(message, f"answer_{trigger_text[0]}")
                   (trigger_text[1], caption=trigger_text[2] if trigger_text[2] != 'None' else ''))

        # Если значение ключа — это текст, то им и отвечаем, предварительно распаковав список,
        # образовавшийся после метода .split(' _|_ ') выше
        else:
            await message.answer(*trigger_text)
