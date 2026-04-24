from datetime import datetime, date
from sqlalchemy import String, Integer, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

class UserRole(Base):
    __tablename__ = 'user_roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))

class CaseRecord(Base, TimestampMixin):
    __tablename__ = 'case_records'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seq_no: Mapped[int] = mapped_column(Integer, default=0, index=True)
    notice_no: Mapped[str] = mapped_column(String(120), index=True)
    applicant: Mapped[str] = mapped_column(String(120), index=True)
    respondent_subject: Mapped[str] = mapped_column(Text, default='')
    review_content: Mapped[str] = mapped_column(Text, default='')
    review_item: Mapped[str] = mapped_column(Text, default='')
    handling_department: Mapped[str] = mapped_column(String(120), index=True)
    contact_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    contact_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    received_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    deadline_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    reply_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_reply_time: Mapped[date | None] = mapped_column(Date, nullable=True)
    judicial_bureau_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    decision_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    decision_content: Mapped[str | None] = mapped_column(String(120), nullable=True)
    redo_status: Mapped[str | None] = mapped_column(String(200), nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    current_status: Mapped[str] = mapped_column(String(80), index=True)
    warning_status: Mapped[str] = mapped_column(String(40), default='正常', index=True)
    remaining_workdays: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_replied: Mapped[bool] = mapped_column(Boolean, default=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

class DictionaryItem(Base, TimestampMixin):
    __tablename__ = 'dictionary_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dict_type: Mapped[str] = mapped_column(String(50), index=True)
    label: Mapped[str] = mapped_column(String(120))
    value: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

class HolidayConfig(Base):
    __tablename__ = 'holiday_configs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[date] = mapped_column(Date, unique=True)
    day_type: Mapped[str] = mapped_column(String(20))
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)

class ResponsibleMapping(Base, TimestampMixin):
    __tablename__ = 'responsible_mappings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_name: Mapped[str] = mapped_column(String(120))
    handling_department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    contact_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    primary_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    primary_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    backup_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    backup_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    warning_days: Mapped[int] = mapped_column(Integer, default=3)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

class WechatNotifyLog(Base, TimestampMixin):
    __tablename__ = 'wechat_notify_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notice_no: Mapped[str | None] = mapped_column(String(120), nullable=True)
    event_type: Mapped[str] = mapped_column(String(40))
    receiver_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    receiver_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    actual_target: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message_summary: Mapped[str] = mapped_column(Text)
    send_status: Mapped[str] = mapped_column(String(40), default='pending')
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_search_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    wechat_window_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    chat_open_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_send_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    send_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confirmed_by: Mapped[str | None] = mapped_column(String(80), nullable=True)

class SendQueue(Base, TimestampMixin):
    __tablename__ = 'send_queue'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_type: Mapped[str] = mapped_column(String(40))
    target_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    target_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    backup_wechat_remark: Mapped[str | None] = mapped_column(String(120), nullable=True)
    message_content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default='pending')
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retry: Mapped[int] = mapped_column(Integer, default=3)
    preview_only: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

class AuditLog(Base, TimestampMixin):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(String(80), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

class SystemParam(Base, TimestampMixin):
    __tablename__ = 'system_params'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    param_key: Mapped[str] = mapped_column(String(120), unique=True)
    param_value: Mapped[str] = mapped_column(Text)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)

class BackupRecord(Base, TimestampMixin):
    __tablename__ = 'backup_records'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)

class Attachment(Base, TimestampMixin):
    __tablename__ = 'attachments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
