from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    app_name: str = 'Administrative Review Local System'
    debug: bool = True
    secret_key: str = 'change-me-in-production'
    access_token_expire_minutes: int = 60 * 24
    db_path: str = str(DATA_DIR / 'app.db')
    backup_dir: str = str(DATA_DIR / 'backups')
    export_dir: str = str(DATA_DIR / 'exports')
    auto_notify_enabled: bool = True
    preview_only_mode: bool = True
    near_threshold: int = 3
    urgent_threshold: int = 1
    max_retry: int = 3
    throttle_seconds: int = 4
    auto_scan_cron: str = '0 9 * * *'
    unit_name: str = '某单位'
    wechat_window_name: str = '微信'
    model_config = SettingsConfigDict(env_file='.env', env_prefix='ARLS_')

settings = Settings()
Path(settings.backup_dir).mkdir(parents=True, exist_ok=True)
Path(settings.export_dir).mkdir(parents=True, exist_ok=True)
