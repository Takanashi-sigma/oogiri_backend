from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from app.core.database import AsyncSessionLocal
from app.service.contest_service import refresh_active_contest_status

scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Tokyo"))

async def update_contest_status_job():
    async with AsyncSessionLocal as db:
        await refresh_active_contest_status(db=db)

def start_scheduler():
    scheduler.add_job(
        update_contest_status_job,
        trigger="cron",
        hour=0,
        minute=0,
        second=0,
        id="update_contest_status_job",
        replace_existing=True
    )
    scheduler.start()
