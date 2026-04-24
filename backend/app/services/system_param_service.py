from sqlalchemy.orm import Session
from app.models.models import SystemParam
from app.core.config import settings


def get_param(db: Session, key: str, default=None):
    row = db.query(SystemParam).filter(SystemParam.param_key == key).first()
    if row is None:
        return default
    return row.param_value


def get_bool_param(db: Session, key: str, default: bool = False) -> bool:
    value = get_param(db, key, None)
    if value is None:
        return default
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on', 'enabled'}


def get_int_param(db: Session, key: str, default: int) -> int:
    value = get_param(db, key, None)
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def get_runtime_config(db: Session) -> dict:
    return {
        'near_threshold': get_int_param(db, 'near_threshold', settings.near_threshold),
        'urgent_threshold': get_int_param(db, 'urgent_threshold', settings.urgent_threshold),
        'deadline_workdays': get_int_param(db, 'deadline_workdays', 10),
        'auto_notify_enabled': get_bool_param(db, 'auto_notify_enabled', settings.auto_notify_enabled),
        'preview_only_mode': get_bool_param(db, 'preview_only_mode', settings.preview_only_mode),
        'max_retry': get_int_param(db, 'max_retry', settings.max_retry),
        'throttle_seconds': get_int_param(db, 'throttle_seconds', settings.throttle_seconds),
        'auto_scan_minutes': get_int_param(db, 'auto_scan_minutes', 120),
        'queue_process_interval_seconds': get_int_param(db, 'queue_process_interval_seconds', 120),
        'wechat_window_name': get_param(db, 'wechat_window_name', settings.wechat_window_name) or settings.wechat_window_name,
    }
