from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User
from app.utils.security import verify_password, create_access_token
from app.services.audit_service import write_audit

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/login')
def login(payload: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.get('username')).first()
    if not user or not verify_password(payload.get('password', ''), user.password_hash):
        raise HTTPException(401, '用户名或密码错误')
    token = create_access_token({'sub': user.username})
    write_audit(db, 'auth.login', 'user', str(user.id), detail=user.username, username=user.username)
    return {'token': token, 'username': user.username, 'display_name': user.display_name}
