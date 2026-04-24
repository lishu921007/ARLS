from datetime import datetime
import platform
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import CaseRecord, SendQueue, WechatNotifyLog
from app.services.case_service import build_message, resolve_mapping
from app.services.queue_service import queue_service
from app.services.audit_service import write_audit
from app.services.system_param_service import get_runtime_config

router = APIRouter(prefix='/notify', tags=['notify'])

@router.post('/case/{case_id}/manual')
def manual_send(case_id: int, preview_only: bool | None = None, db: Session = Depends(get_db)):
    case = db.query(CaseRecord).filter(CaseRecord.id == case_id).first()
    if not case:
        raise HTTPException(404, '事项不存在')
    target = resolve_mapping(db, case)
    if not (target.get('remark') or target.get('backup')):
        raise HTTPException(400, '该事项未配置可用的微信备注名，无法发送')
    runtime = get_runtime_config(db)
    final_preview = runtime['preview_only_mode'] if preview_only is None else preview_only
    task = queue_service.enqueue(db, case.id, '手工发送', target.get('name'), target.get('remark'), target.get('backup'), build_message(case, '手工提醒'), preview_only=final_preview)
    write_audit(db, 'notify.manual', 'case', str(case.id), detail=case.notice_no)
    return task

@router.post('/test')
def test_send(payload: dict, db: Session = Depends(get_db)):
    runtime = get_runtime_config(db)
    remark = payload.get('receiver_wechat_remark')
    if not remark:
        raise HTTPException(400, '请填写微信备注名')
    preview_only = runtime['preview_only_mode'] if payload.get('preview_only') is None else payload.get('preview_only')
    task = queue_service.enqueue(db, None, '测试', payload.get('receiver_name'), remark, payload.get('backup_wechat_remark'), payload.get('message_content', '这是一条测试消息'), preview_only=preview_only)
    write_audit(db, 'notify.test', 'send_queue', str(task.id), detail=payload.get('receiver_wechat_remark'))
    return task

@router.get('/queue')
def list_queue(db: Session = Depends(get_db)):
    return db.query(SendQueue).order_by(SendQueue.id.desc()).all()

@router.post('/queue/process-once')
def process_queue_once(db: Session = Depends(get_db)):
    task = queue_service.process_once(db)
    return {'success': True, 'task': task}

@router.post('/queue/{task_id}/retry')
def retry_queue(task_id: int, db: Session = Depends(get_db)):
    task = db.query(SendQueue).filter(SendQueue.id == task_id).first()
    if not task:
        raise HTTPException(404, '任务不存在')
    task.status = 'pending'
    task.error_message = None
    db.commit()
    write_audit(db, 'notify.retry', 'send_queue', str(task.id), detail='manual retry')
    return task

@router.post('/queue/{task_id}/cancel')
def cancel_queue(task_id: int, db: Session = Depends(get_db)):
    task = db.query(SendQueue).filter(SendQueue.id == task_id).first()
    if not task:
        raise HTTPException(404, '任务不存在')
    task.status = 'cancelled'
    db.commit()
    write_audit(db, 'notify.cancel', 'send_queue', str(task.id), detail='manual cancel')
    return task

@router.get('/logs')
def logs(db: Session = Depends(get_db)):
    return db.query(WechatNotifyLog).order_by(WechatNotifyLog.id.desc()).all()

@router.post('/logs/{log_id}/confirm')
def confirm_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(WechatNotifyLog).filter(WechatNotifyLog.id == log_id).first()
    if not log:
        raise HTTPException(404, '发送日志不存在')
    log.send_confirmed = True
    log.confirmed_at = datetime.utcnow()
    log.confirmed_by = 'admin'
    db.commit()
    write_audit(db, 'notify.confirm', 'wechat_log', str(log.id), detail=log.notice_no or log.receiver_wechat_remark or '')
    return log

@router.get('/status')
def notify_status(db: Session = Depends(get_db)):
    runtime = get_runtime_config(db)
    pending_count = db.query(SendQueue).filter(SendQueue.status == 'pending').count()
    failed_count = db.query(SendQueue).filter(SendQueue.status == 'failed').count()
    latest_log = db.query(WechatNotifyLog).order_by(WechatNotifyLog.id.desc()).first()
    return {
        'runtime': runtime,
        'pending_count': pending_count,
        'failed_count': failed_count,
        'latest_log': latest_log,
        'host_os': platform.system(),
    }
