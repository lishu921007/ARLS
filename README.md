# 行政复议答复事项管理系统（本地版 + 微信自动通知）

这是一个围绕 **行政复议答复事项台账、时限提醒、闭环管理、统计分析、个人微信自动通知** 的本地系统项目。

## 当前交付形态
- 可运行代码骨架（FastAPI + Vue3 + SQLite）
- 工作日计算与预警逻辑
- 本地发送队列与微信自动化服务骨架
- Windows 启停脚本
- Inno Setup 安装脚本
- Docker Compose 外网测试版方案

## 本地开发启动
### Backend
```bash
cd backend
python -m venv .venv
. .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
### Frontend
```bash
cd frontend
npm install
npm run dev
```

- 前端：http://127.0.0.1:18080
- 后端：http://127.0.0.1:18081

## 默认账号
- admin / admin123

## 技术栈
- 后端：FastAPI / SQLAlchemy / SQLite / APScheduler
- 前端：Vue3 / Element Plus
- 微信自动化：uiautomation（Windows UI Automation）
- 打包：PyInstaller + Inno Setup

## 重要说明
1. 正式环境必须是 Windows 10/11。
2. 微信自动发送依赖本机已登录的 Windows 个人微信客户端。
3. 当前仓库中的微信发送模块已按真实路径设计，但实际控件识别可能需要在目标微信版本上做少量适配。
4. 当前版本优先保证业务主流程、数据结构、预警逻辑、发送队列与可扩展打包结构先跑通。
