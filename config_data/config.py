from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class AllowedChatsAndAdmins:
    # Список чатов, в которых работает бот
    allowed_chats: set[int]
    # Список админов, команды которых обрабатывает бот
    allowed_admins: set[int]


@dataclass
class Config:
    tg_bot: TgBot
    chats_and_admins: AllowedChatsAndAdmins


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN')
        ),
        chats_and_admins=AllowedChatsAndAdmins(
            allowed_chats=set(map(int, env.list('ALLOWED_CHATS'))),
            allowed_admins=set(map(int, env.list('ALLOWED_ADMINS')))
        )
    )
