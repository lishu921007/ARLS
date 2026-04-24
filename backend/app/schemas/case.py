from datetime import date, datetime
from pydantic import BaseModel

class CaseBase(BaseModel):
    notice_no: str = ''
    applicant: str = ''
    respondent_subject: str = ''
    review_content: str = ''
    review_item: str = ''
    handling_department: str = ''
    contact_name: str | None = None
    contact_wechat_remark: str | None = None
    received_date: date | None = None
    reply_date: date | None = None
    actual_reply_time: date | None = None
    judicial_bureau_date: date | None = None
    decision_date: date | None = None
    decision_content: str | None = None
    redo_status: str | None = None
    case_type: str | None = None
    current_status: str | None = None
    remark: str | None = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(CaseBase):
    pass

class CaseOut(CaseBase):
    id: int
    seq_no: int
    deadline_date: date | None = None
    warning_status: str
    remaining_workdays: int | None = None
    is_replied: bool
    is_closed: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
