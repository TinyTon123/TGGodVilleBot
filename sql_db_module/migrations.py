from sqlalchemy import create_engine
from sql_db_module.users_model import UserBase

engine = create_engine("sqlite:///GVBot.db", echo=True)

def create_db_and_tables() -> None:
	UserBase.metadata.create_all(engine)

create_db_and_tables()
