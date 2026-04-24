from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, cases, dashboard, config, notify, system
from app.db.init_db import init_db
from app.services.scheduler_service import start_scheduler

app = FastAPI(title='本地行政复议答复事项管理系统')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

app.include_router(auth.router, prefix='/api')
app.include_router(cases.router, prefix='/api')
app.include_router(dashboard.router, prefix='/api')
app.include_router(config.router, prefix='/api')
app.include_router(notify.router, prefix='/api')
app.include_router(system.router, prefix='/api')

@app.on_event('startup')
def startup_event():
    init_db()
    start_scheduler()

@app.get('/api/health')
def health():
    return {'status': 'ok'}
