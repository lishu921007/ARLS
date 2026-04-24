CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  display_name TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS user_roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  role_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS case_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seq_no INTEGER DEFAULT 0,
  notice_no TEXT,
  applicant TEXT,
  review_content TEXT,
  review_item TEXT,
  handling_department TEXT,
  contact_name TEXT,
  contact_wechat_remark TEXT,
  received_date TEXT,
  deadline_date TEXT,
  reply_date TEXT,
  actual_reply_time TEXT,
  judicial_bureau_date TEXT,
  decision_date TEXT,
  decision_content TEXT,
  redo_status TEXT,
  case_type TEXT,
  current_status TEXT,
  warning_status TEXT DEFAULT '正常',
  remaining_workdays INTEGER,
  is_replied INTEGER DEFAULT 0,
  is_closed INTEGER DEFAULT 0,
  remark TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  deleted INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS dictionary_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dict_type TEXT,
  label TEXT,
  value TEXT,
  sort_order INTEGER DEFAULT 0,
  enabled INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS holiday_configs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  day TEXT UNIQUE,
  day_type TEXT,
  remark TEXT
);
CREATE TABLE IF NOT EXISTS responsible_mappings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_name TEXT,
  handling_department TEXT,
  case_type TEXT,
  contact_name TEXT,
  contact_wechat_remark TEXT,
  primary_name TEXT,
  primary_wechat_remark TEXT,
  backup_name TEXT,
  backup_wechat_remark TEXT,
  warning_days INTEGER DEFAULT 3,
  enabled INTEGER DEFAULT 1,
  remark TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS wechat_notify_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id INTEGER,
  notice_no TEXT,
  event_type TEXT,
  receiver_name TEXT,
  receiver_wechat_remark TEXT,
  actual_target TEXT,
  message_summary TEXT,
  send_status TEXT,
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  contact_search_result TEXT,
  wechat_window_state TEXT,
  chat_open_result TEXT,
  final_send_result TEXT,
  sent_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS send_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id INTEGER,
  event_type TEXT,
  target_name TEXT,
  target_wechat_remark TEXT,
  backup_wechat_remark TEXT,
  message_content TEXT,
  status TEXT DEFAULT 'pending',
  retry_count INTEGER DEFAULT 0,
  max_retry INTEGER DEFAULT 3,
  preview_only INTEGER DEFAULT 0,
  error_message TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  action TEXT,
  target_type TEXT,
  target_id TEXT,
  detail TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS system_params (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  param_key TEXT UNIQUE,
  param_value TEXT,
  remark TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS backup_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_name TEXT,
  file_path TEXT,
  remark TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS attachments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id INTEGER,
  file_name TEXT,
  file_path TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
