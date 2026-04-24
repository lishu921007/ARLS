from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.db.session import Base, engine, SessionLocal
from app.models.models import User, Role, UserRole, DictionaryItem, ResponsibleMapping, SystemParam
from app.utils.security import hash_password

DEFAULT_DICTIONARIES = {
    'department': ['浆洗所', '红牌楼所', '玉林所', '簇锦所', '火南所', '望江所'],
    'decision_content': ['撤销重新作出', '维持', '撤回申请复议终止'],
    'case_type': ['食品', '广告', '质量', '药品', '多种'],
    'review_item': ['投诉举报处理', '信息公开', '行政处罚', '行政复议事项'],
    'current_status': ['待处理', '处理中', '已答复', '已交司法局', '已决定', '已办结', '已终止'],
    'warning_status': ['正常', '临期', '紧急', '超期'],
}

DEFAULT_PARAMS = {
    'near_threshold': '3',
    'urgent_threshold': '1',
    'deadline_workdays': '10',
    'auto_notify_enabled': 'true',
    'preview_only_mode': 'true',
    'max_retry': '3',
    'throttle_seconds': '4',
    'auto_scan_minutes': '120',
    'queue_process_interval_seconds': '120',
    'wechat_window_name': '微信',
}


def ensure_sqlite_columns():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    with engine.begin() as conn:
        if 'wechat_notify_logs' in table_names:
            columns = {col['name'] for col in inspector.get_columns('wechat_notify_logs')}
            if 'send_confirmed' not in columns:
                conn.execute(text("ALTER TABLE wechat_notify_logs ADD COLUMN send_confirmed BOOLEAN DEFAULT 0"))
            if 'confirmed_at' not in columns:
                conn.execute(text("ALTER TABLE wechat_notify_logs ADD COLUMN confirmed_at DATETIME"))
            if 'confirmed_by' not in columns:
                conn.execute(text("ALTER TABLE wechat_notify_logs ADD COLUMN confirmed_by VARCHAR(80)"))
        if 'case_records' in table_names:
            case_columns = {col['name'] for col in inspector.get_columns('case_records')}
            if 'respondent_subject' not in case_columns:
                conn.execute(text("ALTER TABLE case_records ADD COLUMN respondent_subject TEXT DEFAULT ''"))


def init_db():
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()
    db: Session = SessionLocal()
    try:
        if not db.query(Role).count():
            admin = Role(name='admin')
            operator = Role(name='operator')
            db.add_all([admin, operator])
            db.flush()
            user = User(username='admin', password_hash=hash_password('admin123'), display_name='系统管理员')
            db.add(user)
            db.flush()
            db.add(UserRole(user_id=user.id, role_id=admin.id))
        existing = {(x.dict_type, x.value) for x in db.query(DictionaryItem).all()}
        for dict_type, values in DEFAULT_DICTIONARIES.items():
            for idx, value in enumerate(values):
                if (dict_type, value) not in existing:
                    db.add(DictionaryItem(dict_type=dict_type, label=value, value=value, sort_order=idx, enabled=True))
        if not db.query(ResponsibleMapping).count():
            db.add(ResponsibleMapping(rule_name='默认浆洗所负责人', handling_department='浆洗所', primary_name='张三', primary_wechat_remark='张三', backup_name='李四', backup_wechat_remark='李四', enabled=True, warning_days=3))
        existing_params = {x.param_key for x in db.query(SystemParam).all()}
        for k, v in DEFAULT_PARAMS.items():
            if k not in existing_params:
                db.add(SystemParam(param_key=k, param_value=v))
        db.commit()
    finally:
        db.close()
