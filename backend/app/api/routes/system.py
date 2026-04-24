import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db, engine
from app.core.config import settings
from app.models.models import BackupRecord, AuditLog
from app.services.audit_service import write_audit

router = APIRouter(prefix='/system', tags=['system'])


def _copy_db_file(src: Path, dst: Path):
    if not src.exists():
        raise HTTPException(404, '数据库文件不存在')
    dst.parent.mkdir(parents=True, exist_ok=True)
    engine.dispose()
    shutil.copy2(src, dst)


@router.get('/audit-logs')
def audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.id.desc()).all()


@router.post('/backup')
def create_backup(db: Session = Depends(get_db)):
    src = Path(settings.db_path)
    dst = Path(settings.backup_dir) / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    _copy_db_file(src, dst)
    row = BackupRecord(file_name=dst.name, file_path=str(dst), remark='manual backup')
    db.add(row)
    db.commit()
    write_audit(db, 'system.backup', 'backup', str(row.id), detail=dst.name)
    return row


@router.get('/backups')
def list_backups(db: Session = Depends(get_db)):
    return db.query(BackupRecord).order_by(BackupRecord.id.desc()).all()


@router.post('/restore/{backup_id}')
def restore_backup(backup_id: int, db: Session = Depends(get_db)):
    row = db.query(BackupRecord).filter(BackupRecord.id == backup_id).first()
    if not row:
        raise HTTPException(404, '备份记录不存在')
    src = Path(row.file_path)
    if not src.exists():
        raise HTTPException(404, '备份文件不存在，请检查文件路径')
    live_db = Path(settings.db_path)
    safety_backup = Path(settings.backup_dir) / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    _copy_db_file(live_db, safety_backup)
    _copy_db_file(src, live_db)
    safety_row = BackupRecord(file_name=safety_backup.name, file_path=str(safety_backup), remark=f'auto backup before restore #{backup_id}')
    db.add(safety_row)
    db.commit()
    write_audit(db, 'system.restore', 'backup', str(backup_id), detail=row.file_name)
    return {'success': True, 'restored_from': row.file_name, 'pre_restore_backup': safety_backup.name}


@router.post('/restore-upload')
async def restore_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.db'):
        raise HTTPException(400, '仅支持上传 .db 数据库文件')
    upload_path = Path(settings.backup_dir) / f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    upload_path.write_bytes(content)
    row = BackupRecord(file_name=upload_path.name, file_path=str(upload_path), remark='uploaded restore file')
    db.add(row)
    db.commit()
    write_audit(db, 'system.restore.upload', 'backup', str(row.id), detail=upload_path.name)
    return restore_backup(row.id, db)
