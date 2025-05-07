from database.models import async_session
from database.models import Report, Photo
from sqlalchemy import select, update, asc, desc
import datetime as dt

async def ins_report (tg_id,
                      name,
                      text_rep,
                      ranked,
                      photo_ids=[]):
    async with async_session() as session:
        async with session.begin():
            date = dt.date.today()
            new_report = Report(
                tg_id=tg_id,
                text_rep=text_rep,
                ranked=ranked,
                date=date,
                status=0,
                name= name,
                comment_moder='Жалоба еще не рассмотрена.'
            )
            session.add(new_report)

            await session.flush()
            report_id = new_report.id

            for photo_id in photo_ids:
                new_photo = Photo(report_id=report_id, photo_id=photo_id)
                session.add(new_photo)
        await session.commit()

async def check_reps(tg_id):
    async with async_session() as session:
        stmt = select(Report).where(Report.tg_id == tg_id).order_by(desc(Report.date), desc(Report.id))
        result = await session.execute(stmt)
        reps = result.scalars().all()
        return reps

async def get_report_by_id(report_id):
    async with async_session() as session:
        stmt_report = select(Report).where(Report.id == report_id)
        result_report = await session.execute(stmt_report)
        report = result_report.scalars().first()
        
        if report:
            stmt_photos = select(Photo).where(Photo.report_id == report.id)
            result_photos = await session.execute(stmt_photos)
            photos = result_photos.scalars().all()
            report.photos = photos
            
        return report