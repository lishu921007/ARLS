from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import DictionaryItem, HolidayConfig, ResponsibleMapping, SystemParam
from app.services.audit_service import write_audit

router = APIRouter(prefix='/config', tags=['config'])

@router.get('/dictionary/{dict_type}')
def list_dictionary(dict_type: str, db: Session = Depends(get_db)):
    return db.query(DictionaryItem).filter(DictionaryItem.dict_type == dict_type).order_by(DictionaryItem.sort_order.asc(), DictionaryItem.id.asc()).all()

@router.post('/dictionary')
def create_dictionary(payload: dict, db: Session = Depends(get_db)):
    item = DictionaryItem(**payload)
    db.add(item)
    db.commit()
    write_audit(db, 'dictionary.create', 'dictionary', str(item.id), detail=item.dict_type)
    return item

@router.put('/dictionary/{item_id}')
def update_dictionary(item_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.query(DictionaryItem).filter(DictionaryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, '字典项不存在')
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    write_audit(db, 'dictionary.update', 'dictionary', str(item.id), detail=item.dict_type)
    return item

@router.delete('/dictionary/{item_id}')
def delete_dictionary(item_id: int, db: Session = Depends(get_db)):
    item = db.query(DictionaryItem).filter(DictionaryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, '字典项不存在')
    db.delete(item)
    db.commit()
    write_audit(db, 'dictionary.delete', 'dictionary', str(item_id), detail=item.dict_type)
    return {'success': True}

@router.get('/holidays')
def list_holidays(db: Session = Depends(get_db)):
    return db.query(HolidayConfig).order_by(HolidayConfig.day.asc()).all()

@router.post('/holidays')
def create_holiday(payload: dict, db: Session = Depends(get_db)):
    day_value = payload.get('day')
    if not day_value:
        raise HTTPException(400, '日期不能为空')
    if db.query(HolidayConfig).filter(HolidayConfig.day == day_value).first():
        raise HTTPException(400, '该日期已存在人工覆盖配置')
    item = HolidayConfig(**payload)
    db.add(item)
    db.commit()
    write_audit(db, 'holiday.create', 'holiday', str(item.id), detail=str(item.day))
    return item

@router.put('/holidays/{item_id}')
def update_holiday(item_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.query(HolidayConfig).filter(HolidayConfig.id == item_id).first()
    if not item:
        raise HTTPException(404, '人工覆盖配置不存在')
    target_day = payload.get('day', item.day)
    duplicate = db.query(HolidayConfig).filter(HolidayConfig.day == target_day, HolidayConfig.id != item_id).first()
    if duplicate:
        raise HTTPException(400, '该日期已存在人工覆盖配置')
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    write_audit(db, 'holiday.update', 'holiday', str(item.id), detail=str(item.day))
    return item

@router.delete('/holidays/{item_id}')
def delete_holiday(item_id: int, db: Session = Depends(get_db)):
    item = db.query(HolidayConfig).filter(HolidayConfig.id == item_id).first()
    if not item:
        raise HTTPException(404, '人工覆盖配置不存在')
    detail = str(item.day)
    db.delete(item)
    db.commit()
    write_audit(db, 'holiday.delete', 'holiday', str(item_id), detail=detail)
    return {'success': True}

@router.get('/mappings')
def list_mappings(db: Session = Depends(get_db)):
    return db.query(ResponsibleMapping).order_by(ResponsibleMapping.id.desc()).all()

@router.post('/mappings')
def create_mapping(payload: dict, db: Session = Depends(get_db)):
    item = ResponsibleMapping(**payload)
    db.add(item)
    db.commit()
    write_audit(db, 'mapping.create', 'mapping', str(item.id), detail=item.rule_name)
    return item

@router.put('/mappings/{item_id}')
def update_mapping(item_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.query(ResponsibleMapping).filter(ResponsibleMapping.id == item_id).first()
    if not item:
        raise HTTPException(404, '负责人映射不存在')
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    write_audit(db, 'mapping.update', 'mapping', str(item.id), detail=item.rule_name)
    return item

@router.delete('/mappings/{item_id}')
def delete_mapping(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ResponsibleMapping).filter(ResponsibleMapping.id == item_id).first()
    if not item:
        raise HTTPException(404, '负责人映射不存在')
    db.delete(item)
    db.commit()
    write_audit(db, 'mapping.delete', 'mapping', str(item_id), detail=item.rule_name)
    return {'success': True}

@router.get('/params')
def list_params(db: Session = Depends(get_db)):
    return db.query(SystemParam).order_by(SystemParam.param_key.asc()).all()

@router.post('/params')
def upsert_param(payload: dict, db: Session = Depends(get_db)):
    row = db.query(SystemParam).filter(SystemParam.param_key == payload['param_key']).first()
    if row:
        row.param_value = payload['param_value']
        row.remark = payload.get('remark')
    else:
        row = SystemParam(**payload)
        db.add(row)
    db.commit()
    write_audit(db, 'param.upsert', 'system_param', str(row.id), detail=row.param_key)
    return row
