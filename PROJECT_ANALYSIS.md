# ARLS Project Analysis

## Overview
ARLS is a Windows-first local case-management system for administrative review reply work. It combines a FastAPI backend, Vue 3 frontend, SQLite storage, deadline/warning logic, and desktop WeChat automation for attended notification workflows.

## Main modules
- `backend/app/api/routes/cases.py`: case CRUD, import/export, filtering
- `backend/app/services/case_service.py`: deadline and warning computation
- `backend/app/services/wechat_service.py`: Windows WeChat desktop automation
- `frontend/src/pages/CaseListPage.vue`: main case list UI and sorting/filtering
- install/start scripts at repo root: Windows deployment entrypoints

## What this project does well
- Structured ledger management beyond plain Excel
- Automatic deadline / remaining-workday calculation
- Warning states for near/urgent/overdue work
- Import/export to Excel and CSV
- Manual attended WeChat send flow
- Windows-friendly one-click install/start scripts

## Key risks / boundaries
- WeChat automation is desktop UI automation, so it is best for attended/manual sending rather than true unattended background messaging.
- The project is strongly Windows-oriented.
- Runtime data (`backend/data/app.db`, exports, backups) should stay out of source control.

## Improvements included in this sync
- Fixed duplicate `seq_no` generation on import and added automatic resequencing
- Added sortable columns in case list for seq_no / notice_no / received_date / deadline_date / remaining_workdays
- Synced a hardened WeChat automation implementation that improves first-run focus behavior for manual send
- Included stable Windows install/start scripts (`install.cmd`, `start.cmd`, `install_arls_safe_v3.cmd`)
