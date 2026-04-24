import time
from sqlalchemy.orm import Session
from app.models.models import SendQueue, CaseRecord
from app.services.wechat_service import wechat_service, log_notify
from app.services.audit_service import write_audit
from app.services.system_param_service import get_runtime_config


class QueueService:
    def enqueue(self, db: Session, case_id: int | None, event_type: str, target_name: str | None, target_wechat_remark: str | None, backup_wechat_remark: str | None, message_content: str, preview_only: bool = False):
        runtime = get_runtime_config(db)
        duplicate = db.query(SendQueue).filter(
            SendQueue.case_id == case_id,
            SendQueue.event_type == event_type,
            SendQueue.target_wechat_remark == target_wechat_remark,
            SendQueue.status.in_(['pending', 'sending'])
        ).first() if case_id is not None else None
        if duplicate:
            return duplicate
        task = SendQueue(
            case_id=case_id,
            event_type=event_type,
            target_name=target_name,
            target_wechat_remark=target_wechat_remark,
            backup_wechat_remark=backup_wechat_remark,
            message_content=message_content,
            preview_only=preview_only,
            max_retry=runtime['max_retry'],
        )
        db.add(task)
        db.commit()
        return task

    def process_once(self, db: Session):
        task = db.query(SendQueue).filter(SendQueue.status == 'pending').order_by(SendQueue.id.asc()).first()
        if not task:
            return None
        runtime = get_runtime_config(db)
        task.status = 'sending'
        db.commit()
        target = task.target_wechat_remark or task.backup_wechat_remark or ''
        preview_only = task.preview_only or runtime['preview_only_mode']
        result = wechat_service.send_text(target, task.message_content, preview_only=preview_only, window_name=runtime['wechat_window_name'])
        is_preview = bool(result.get('preview'))
        if result['success']:
            task.status = 'success'
        else:
            task.retry_count += 1
            if task.retry_count >= task.max_retry and task.backup_wechat_remark and task.backup_wechat_remark != task.target_wechat_remark:
                backup = task.backup_wechat_remark
                task.target_wechat_remark = backup
                task.status = 'pending'
                task.error_message = f"主联系人失败，切备用：{result['detail']}"
            elif task.retry_count >= task.max_retry:
                task.status = 'failed'
                task.error_message = result['detail']
            else:
                task.status = 'pending'
                task.error_message = result['detail']
        db.commit()
        notice_no = None
        if task.case_id:
            case = db.query(CaseRecord).filter(CaseRecord.id == task.case_id).first()
            notice_no = case.notice_no if case else None
        log_notify(
            db,
            case_id=task.case_id,
            notice_no=notice_no,
            event_type=task.event_type,
            receiver_name=task.target_name,
            receiver_wechat_remark=task.target_wechat_remark,
            actual_target=task.target_wechat_remark,
            message_summary=task.message_content[:300],
            send_status='preview' if is_preview else ('success' if result['success'] else 'failed'),
            retry_count=task.retry_count,
            error_message=None if result['success'] else result['detail'],
            contact_search_result=result['detail'],
            wechat_window_state='preview' if is_preview else ('ok' if result['success'] else 'error'),
            chat_open_result=result['detail'],
            final_send_result=result['detail'],
        )
        write_audit(db, 'queue.process', 'send_queue', str(task.id), detail=result['detail'])
        time.sleep(max(runtime['throttle_seconds'], 0))
        return task


queue_service = QueueService()
