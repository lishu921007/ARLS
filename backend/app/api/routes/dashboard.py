from datetime import date
from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import CaseRecord
from app.services.case_service import compute_case_fields

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


def _quarter_label(d):
    q = (d.month - 1) // 3 + 1
    return f'{d.year}Q{q}'


def _filter_cases(cases, handling_department=None, case_type=None, current_status=None, warning_status=None, received_start=None, received_end=None):
    result = cases
    if handling_department:
        result = [c for c in result if c.handling_department == handling_department]
    if case_type:
        result = [c for c in result if c.case_type == case_type]
    if current_status:
        result = [c for c in result if c.current_status == current_status]
    if warning_status:
        result = [c for c in result if c.warning_status == warning_status]
    if received_start:
        result = [c for c in result if c.received_date >= received_start]
    if received_end:
        result = [c for c in result if c.received_date <= received_end]
    return result


@router.get('')
def dashboard(
    handling_department: str | None = None,
    case_type: str | None = None,
    current_status: str | None = None,
    warning_status: str | None = None,
    received_start: date | None = None,
    received_end: date | None = None,
    db: Session = Depends(get_db),
):
    cases = db.query(CaseRecord).filter(CaseRecord.deleted == False).all()
    for c in cases:
        compute_case_fields(db, c)
    db.commit()
    cases = _filter_cases(cases, handling_department, case_type, current_status, warning_status, received_start, received_end)
    year = date.today().year
    quarter = (date.today().month - 1) // 3 + 1
    by_quarter = defaultdict(int)
    by_department = defaultdict(int)
    by_type = defaultdict(int)
    by_status = defaultdict(int)
    by_decision = defaultdict(int)
    by_warning = defaultdict(int)
    for c in cases:
        by_quarter[_quarter_label(c.received_date)] += 1
        by_department[c.handling_department or '未填'] += 1
        by_type[c.case_type or '未填'] += 1
        by_status[c.current_status or '未填'] += 1
        by_decision[c.decision_content or '未填'] += 1
        by_warning[c.warning_status or '正常'] += 1
    return {
        'total': len(cases),
        'quarter_count': len([c for c in cases if c.received_date.year == year and ((c.received_date.month - 1)//3 +1) == quarter]),
        'near_count': len([c for c in cases if c.warning_status == '临期']),
        'urgent_count': len([c for c in cases if c.warning_status == '紧急']),
        'overdue_count': len([c for c in cases if c.warning_status == '超期']),
        'closed_count': len([c for c in cases if c.is_closed]),
        'by_department': [{'name': k, 'value': v} for k, v in sorted(by_department.items())],
        'by_type': [{'name': k, 'value': v} for k, v in sorted(by_type.items())],
        'by_status': [{'name': k, 'value': v} for k, v in sorted(by_status.items())],
        'by_decision': [{'name': k, 'value': v} for k, v in sorted(by_decision.items())],
        'by_warning': [{'name': k, 'value': v} for k, v in sorted(by_warning.items())],
        'by_quarter': [{'name': k, 'value': v} for k, v in sorted(by_quarter.items())],
    }
