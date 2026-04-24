# ARLS

Administrative Review Ledger System for Windows.

ARLS is a local case-management system for 行政复议答复事项台账、时限提醒、闭环管理、统计分析，以及人工触发的微信桌面通知。

## What it solves
Compared with managing everything only in Excel, ARLS adds:

- automatic deadline calculation
- remaining workday calculation
- warning states: 正常 / 临期 / 紧急 / 超期
- structured filtering and sorting
- import/export via Excel and CSV
- manual WeChat desktop notification flow
- basic audit trail and closed-loop status management

In one sentence:

> Excel helps you record; ARLS helps you track, warn, and follow through.

## Architecture
- Backend: FastAPI + SQLAlchemy + SQLite + APScheduler
- Frontend: Vue 3 + Element Plus + Vite
- Notification: Windows desktop WeChat automation via `uiautomation`
- Packaging: Windows `cmd` / `bat` install and start scripts

## Best-fit runtime
- Windows 10/11
- Local desktop environment
- Logged-in desktop WeChat client when using WeChat notification

## Important boundary
WeChat automation here is **desktop UI automation**.
It is best suited for **attended/manual sending** and desktop office scenarios.
It is not the ideal design for fully unattended background notification.

---

## Quick Start (Recommended for Windows users)

### 1. Prepare environment
Install:
- Python 3.11+ or Anaconda environment with Python available in PATH
- Node.js LTS

### 2. Install
Open the project folder and run:

```bat
install.cmd
```

If your machine has Python/Conda path quirks, use:

```bat
install_arls_safe_v3.cmd
```

### 3. Start
After installation completes, run:

```bat
start.cmd
```

Then open:

```text
http://localhost:18080/
```

### Default account
- username: `admin`
- password: `admin123`

---

## Developer Start

### Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:18080/
- Backend: http://127.0.0.1:18081/

---

## Repository Layout

```text
backend/                     FastAPI backend
  app/api/routes/            HTTP routes
  app/services/              business logic and WeChat automation
  app/models/                SQLAlchemy models
  app/utils/                 workday/security helpers
  data/                      runtime SQLite data (do not commit real data)
frontend/                    Vue 3 frontend
  src/pages/                 page-level UI
scripts/                     Windows helper scripts
docs/                        user and deployment docs
install.cmd                  recommended Windows installer entry
start.cmd                    recommended Windows start entry
PROJECT_ANALYSIS.md          project-level analysis and boundaries
```

---

## Key Features

### Case ledger
- create, edit, close, delete case items
- maintain seq_no / notice_no / applicant / department / status / dates

### Deadline and warning logic
- compute deadline from received date + configured workdays
- compute remaining workdays
- classify warning state automatically

### Import and export
- import from Excel/CSV template
- export case list to Excel/CSV
- resequence seq_no automatically to avoid duplicate sequence values

### List management
- filter by keyword, notice_no, applicant, department, type, status, warning state, date ranges
- sortable columns for:
  - seq_no
  - notice_no
  - received_date
  - deadline_date
  - remaining_workdays

### Notification
- manual case-based WeChat send
- local send queue and notify logs
- hardened WeChat desktop automation flow for manual desktop use

---

## Files already hardened in this repo
The synced version includes fixes for:

- Windows install script encoding issues
- `npm.cmd` / `npx.cmd` early-exit behavior in batch scripts
- npm 11 compatibility fallback to npm 10
- localhost startup behavior
- duplicate `seq_no` during import
- sortable case list columns
- improved first-run WeChat foreground/focus behavior for manual sending

---

## Data and source-control notes
The repository should keep **source code and scripts**, not real runtime data.

Recommended practice:
- do not commit `backend/data/app.db`
- do not commit backups / exports / caches / virtualenvs / node_modules
- keep runtime data local to each deployment machine

---

## Documents
- `PROJECT_ANALYSIS.md`: concise project analysis
- `docs/README.md`: documentation index
- `docs/USER_GUIDE.md`: user-facing guide
- `README_小白安装教程.md`: simplified Chinese beginner installation guide

---

## Future improvement directions
- stronger packaging/release workflow
- better runtime data separation
- optional non-WeChat notification channels
- more reliable unattended notification architecture
- tests for import rules and deadline logic
