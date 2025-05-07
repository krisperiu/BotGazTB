from sqlalchemy import BigInteger, String, ForeignKey, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from sqlalchemy import DateTime
import datetime as dt
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))

async_session = async_sessionmaker(engine)

class Base (AsyncAttrs, DeclarativeBase):
    pass

class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(20))
    text_rep: Mapped[str] = mapped_column(String(250))
    ranked: Mapped[int] = mapped_column()
    date: Mapped[dt.date] = mapped_column(Date)
    status: Mapped[int] = mapped_column()
    comment_moder: Mapped[str] = mapped_column(String(250))
    reviewed_at: Mapped[dt.datetime] = mapped_column(DateTime, default=None, nullable=True)

class Photo(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey('reports.id'))
    photo_id: Mapped[str] = mapped_column(String(250))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)