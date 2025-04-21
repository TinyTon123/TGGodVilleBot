from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
	pass


class UserBase(Base):
	__tablename__ = "users"

	tg_id: Mapped[int] = mapped_column(primary_key=True)
	tg_name: Mapped[str] = mapped_column(String(30))
	gv_name: Mapped[str] = mapped_column(String(30), unique=True)
	gv_name_lower: Mapped[str] = mapped_column(String(30), unique=True)
