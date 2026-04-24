from sqlalchemy.orm import Session
from app.models.models import AuditLog

def write_audit(db: Session, action: str, target_type: str, target_id: str | None = None, detail: str | None = None, username: str | None = 'system'):
    db.add(AuditLog(username=username, action=action, target_type=target_type, target_id=target_id, detail=detail))
    db.commit()
