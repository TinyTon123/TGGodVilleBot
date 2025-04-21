
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from sql_db_module.migrations import engine
from sql_db_module.users_model import UserBase

Session = sessionmaker(engine)

def manipulate_db(func: callable):
    """Декоратор для открытия-закрытия сессий с БД."""
    def wrapper(*args):
        with Session() as session:
            try:
                result = func(*args, session=session)
            except Exception:
                session.rollback()
                raise
            else:
                session.commit()
        return result
    return wrapper

@manipulate_db
def find_user_by_tg_id(tg_id: int, session):
    """Получение пользователя из БД по id в ТГ."""
    statement = select(UserBase).where(UserBase.tg_id == tg_id)
    user = session.scalars(statement).one_or_none()
    if user:
        return user.gv_name

@manipulate_db
def find_user_by_gv_name(gv_name: str, session):
    """Получение пользователя из БД по имени в ГВ."""
    gv_name_lower = gv_name.lower()
    statement = select(UserBase).where(UserBase.gv_name_lower == gv_name_lower)
    user = session.scalars(statement).one_or_none()
    if user:
        return user.tg_id, user.tg_name

@manipulate_db
def upsert_user(tg_id: int, tg_name: str, gv_name: str, session) -> None:
    """Добавление или обновление пользователя в БД."""
    user = UserBase(
        tg_id=tg_id,
        tg_name=tg_name,
        gv_name=gv_name,
        gv_name_lower=gv_name.lower()
    )
    session.merge(user)

@manipulate_db
def delete_user(param: int | str, session) -> str:
    """Удаление пользователя из БД по id в ТГ или по имени в ГВ."""
    if isinstance(param, int):
        attr = 'tg_id'
    else:
        attr = 'gv_name_lower'
        param = param.lower()
    statement = select(UserBase).where(getattr(UserBase, attr) == param)
    user_to_delete = session.scalars(statement).one_or_none()
    if user_to_delete:
        session.delete(user_to_delete)
        return 'Юзер удален.'
    return 'Такого юзера нет.'
