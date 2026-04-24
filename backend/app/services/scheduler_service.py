from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.session import SessionLocal
from app.models.models import CaseRecord
from app.services.case_service import compute_case_fields, enqueue_warning_if_needed
from app.services.queue_service import queue_service
from app.services.system_param_service import get_runtime_config

scheduler = BackgroundScheduler()


def scan_cases_job():
    db = SessionLocal()
    try:
        cases = db.query(CaseRecord).filter(CaseRecord.deleted == False).all()
        for case in cases:
            compute_case_fields(db, case, date.today())
            enqueue_warning_if_needed(db, case)
        db.commit()
    finally:
        db.close()


def send_queue_job():
    db = SessionLocal()
    try:
        queue_service.process_once(db)
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return
    db = SessionLocal()
    try:
        runtime = get_runtime_config(db)
    finally:
        db.close()
    scheduler.add_job(scan_cases_job, 'interval', minutes=max(runtime['auto_scan_minutes'], 1), id='scan_cases', replace_existing=True)
    scheduler.add_job(send_queue_job, 'interval', seconds=max(runtime['queue_process_interval_seconds'], 1), id='send_queue', replace_existing=True)
    scheduler.start()
