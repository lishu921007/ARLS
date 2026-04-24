from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.models import HolidayConfig

HOLIDAY = 'holiday'
WORKDAY = 'workday'

try:
    import chinese_calendar as china_calendar
except Exception:
    china_calendar = None


def is_workday(db: Session, d: date) -> bool:
    """
    判断优先级：
    1. 本地人工覆盖表（holiday_configs）
    2. chinese_calendar 中国法定节假日/调休判断
    3. 兜底：周一到周五为工作日
    """
    special = db.query(HolidayConfig).filter(HolidayConfig.day == d).first()
    if special:
        return special.day_type == WORKDAY
    if china_calendar is not None:
        try:
            return china_calendar.is_workday(d)
        except Exception:
            pass
    return d.weekday() < 5


def add_workdays(db: Session, start: date, days: int) -> date:
    current = start
    counted = 0
    while counted < days:
        current += timedelta(days=1)
        if is_workday(db, current):
            counted += 1
    return current


def remaining_workdays(db: Session, today: date, deadline: date) -> int:
    if today == deadline:
        return 0 if is_workday(db, today) else -1
    step = 1 if today < deadline else -1
    cur = today
    count = 0
    while cur != deadline:
        cur += timedelta(days=step)
        if is_workday(db, cur):
            count += step
    return count
