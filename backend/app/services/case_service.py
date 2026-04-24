from datetime import date
from sqlalchemy.orm import Session
from app.models.models import CaseRecord, ResponsibleMapping
from app.utils.workday import add_workdays, remaining_workdays
from app.services.queue_service import queue_service
from app.services.system_param_service import get_runtime_config

CLOSED_STATUSES = {'已办结', '已终止'}
REPLIED_STATUSES = {'已答复', '已交司法局', '已决定', '已办结'}


def compute_case_fields(db: Session, case: CaseRecord, today: date | None = None):
    today = today or date.today()
    runtime = get_runtime_config(db)
    workday_limit = runtime['deadline_workdays']
    if case.received_date:
        case.deadline_date = add_workdays(db, case.received_date, workday_limit)
    else:
        case.deadline_date = None
    case.is_replied = case.current_status in REPLIED_STATUSES or bool(case.actual_reply_time)
    case.is_closed = case.current_status in CLOSED_STATUSES
    case.remaining_workdays = remaining_workdays(db, today, case.deadline_date) if case.deadline_date else None
    if case.is_closed or case.is_replied:
        case.warning_status = '正常'
    elif case.remaining_workdays is None:
        case.warning_status = '正常'
    elif case.remaining_workdays < 0:
        case.warning_status = '超期'
    elif case.remaining_workdays <= runtime['urgent_threshold']:
        case.warning_status = '紧急'
    elif case.remaining_workdays <= runtime['near_threshold']:
        case.warning_status = '临期'
    else:
        case.warning_status = '正常'
    return case


def priority_rank(case: CaseRecord) -> int:
    if case.warning_status == '超期' and not case.is_closed:
        return 1
    if case.warning_status == '紧急' and not case.is_closed:
        return 2
    if case.warning_status == '临期' and not case.is_closed:
        return 3
    if not case.is_closed and case.current_status not in CLOSED_STATUSES:
        return 4
    if case.is_closed:
        return 5
    return 6


def build_message(case: CaseRecord, event_type: str):
    title_map = {
        '临期': '行政复议事项临近答复时限提醒',
        '紧急': '行政复议事项紧急提醒',
        '超期': '行政复议事项超期提醒',
        '手工提醒': '行政复议事项办理提醒',
    }
    title = title_map.get(event_type, '行政复议事项提醒')
    lines = [
        f'您好，您有一条{title}：',
        f'通知书编号：{case.notice_no or "-"}',
        f'申请人：{case.applicant or "-"}',
        f'涉案主体：{case.respondent_subject or "-"}',
        f'行政复议事项：{case.review_item or "-"}',
        f'经办部门：{case.handling_department or "-"}',
        f'当前状态：{case.current_status or "-"}',
        f'签收日期：{case.received_date or "-"}',
        f'最晚答复日：{case.deadline_date or "-"}',
        f'当前预警：{case.warning_status or "-"}',
    ]
    if case.remaining_workdays is not None:
        if case.remaining_workdays >= 0:
            lines.append(f'距时限还有：{case.remaining_workdays} 个工作日')
        else:
            lines.append(f'已超期：{abs(case.remaining_workdays)} 个工作日')
    if case.review_content:
        text = str(case.review_content).strip().replace('\n', ' ')
        lines.append(f'复议内容：{text[:60]}{"…" if len(text) > 60 else ""}')
    lines.append('请及时关注并处理。')
    return '\n'.join(lines)


def resolve_mapping(db: Session, case: CaseRecord):
    if case.contact_wechat_remark:
        return {'name': case.contact_name, 'remark': case.contact_wechat_remark, 'backup': None}
    query = db.query(ResponsibleMapping).filter(ResponsibleMapping.enabled == True)
    query = query.filter(ResponsibleMapping.handling_department.in_([case.handling_department, None]))
    mapping = query.order_by(ResponsibleMapping.id.asc()).first()
    if not mapping:
        return {'name': case.contact_name or '', 'remark': case.contact_wechat_remark or '', 'backup': None}
    return {'name': mapping.primary_name, 'remark': mapping.primary_wechat_remark, 'backup': mapping.backup_wechat_remark}


def enqueue_warning_if_needed(db: Session, case: CaseRecord):
    runtime = get_runtime_config(db)
    if not runtime['auto_notify_enabled']:
        return
    if case.is_closed:
        return
    if case.warning_status not in {'临期', '紧急', '超期'}:
        return
    target = resolve_mapping(db, case)
    if not (target.get('remark') or target.get('backup')):
        return
    queue_service.enqueue(db, case.id, case.warning_status, target.get('name'), target.get('remark'), target.get('backup'), build_message(case, case.warning_status), preview_only=runtime['preview_only_mode'])
