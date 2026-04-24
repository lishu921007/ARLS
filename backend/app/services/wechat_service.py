from datetime import datetime
import platform
import ctypes
import time
from contextlib import contextmanager
from ctypes import wintypes
from sqlalchemy.orm import Session
from app.models.models import WechatNotifyLog

CURRENT_OS = platform.system().lower()

try:
    import uiautomation as auto
except Exception:
    auto = None

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
SW_RESTORE = 9

user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
ole32 = ctypes.WinDLL('ole32', use_last_error=True)

user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.GetForegroundWindow.argtypes = []
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL

kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalFree.restype = wintypes.HGLOBAL

ole32.CoInitialize.argtypes = [wintypes.LPVOID]
ole32.CoInitialize.restype = ctypes.c_long
ole32.CoUninitialize.argtypes = []
ole32.CoUninitialize.restype = None


@contextmanager
def com_initialized():
    initialized = False
    if CURRENT_OS == 'windows':
        try:
            hr = ole32.CoInitialize(None)
            if hr in (0, 1):
                initialized = True
        except Exception:
            initialized = False
    try:
        yield
    finally:
        if initialized:
            try:
                ole32.CoUninitialize()
            except Exception:
                pass


@contextmanager
def open_clipboard():
    opened = False
    for _ in range(10):
        if user32.OpenClipboard(None):
            opened = True
            break
        time.sleep(0.05)
    if not opened:
        raise RuntimeError('无法打开系统剪贴板')
    try:
        yield
    finally:
        user32.CloseClipboard()


def get_foreground_title() -> str:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ''
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ''
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value or ''


def set_clipboard_text(text: str):
    data = text.encode('utf-16-le') + b'\x00\x00'
    hglobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not hglobal:
        raise RuntimeError('GlobalAlloc 失败')
    locked = kernel32.GlobalLock(hglobal)
    if not locked:
        kernel32.GlobalFree(hglobal)
        raise RuntimeError('GlobalLock 失败')
    try:
        ctypes.memmove(locked, data, len(data))
    finally:
        kernel32.GlobalUnlock(hglobal)
    with open_clipboard():
        if not user32.EmptyClipboard():
            kernel32.GlobalFree(hglobal)
            raise RuntimeError('EmptyClipboard 失败')
        handle = user32.SetClipboardData(CF_UNICODETEXT, hglobal)
        if not handle:
            kernel32.GlobalFree(hglobal)
            raise RuntimeError('SetClipboardData 失败')


def click_point(x: int, y: int):
    auto.MoveTo(x, y)
    time.sleep(0.05)
    auto.Click(x, y)
    time.sleep(0.15)


def focus_wechat_window(win, window_name: str, debug: dict, retries: int = 6) -> bool:
    debug.setdefault('foreground_checks', [])
    rect = win.BoundingRectangle
    left = int(rect.left)
    top = int(rect.top)
    right = int(rect.right)
    bottom = int(rect.bottom)
    width = right - left
    height = bottom - top
    title_x = left + max(120, width // 3)
    title_y = top + min(24, max(10, height // 30))
    body_x = left + width // 2
    body_y = top + min(120, max(60, height // 6))

    for i in range(retries):
        try:
            try:
                win.ShowWindow()
            except Exception:
                pass
            try:
                hwnd = int(win.NativeWindowHandle)
                if hwnd:
                    user32.ShowWindow(hwnd, SW_RESTORE)
                    user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
            try:
                win.SetActive()
            except Exception:
                pass
            time.sleep(0.2)
            click_point(title_x, title_y)
            click_point(body_x, body_y)
            time.sleep(0.25)
            title = get_foreground_title()
            debug['foreground_checks'].append({'attempt': i + 1, 'title': title})
            if window_name in title or '微信' in title or 'WeChat' in title:
                return True
        except Exception as e:
            debug['foreground_checks'].append({'attempt': i + 1, 'error': str(e)})
            time.sleep(0.2)
    return False


def click_message_input_area(win):
    rect = win.BoundingRectangle
    left = int(rect.left)
    top = int(rect.top)
    right = int(rect.right)
    bottom = int(rect.bottom)
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        raise RuntimeError('微信聊天窗口尺寸异常，无法定位输入区')
    points = [
        (left + width // 2, top + int(height * 0.82)),
        (left + width // 2, top + int(height * 0.78)),
        (left + int(width * 0.62), top + int(height * 0.82)),
    ]
    for x, y in points:
        click_point(x, y)


class WechatAutomationService:
    def send_text(self, target_remark: str, message: str, preview_only: bool = False, window_name: str = '微信') -> dict:
        debug = {'steps': []}

        def step(msg: str):
            debug['steps'].append(msg)

        if preview_only:
            return {'success': True, 'preview': True, 'detail': '预览模式，未实际发送', 'debug': debug}
        if CURRENT_OS != 'windows':
            return {'success': False, 'detail': f'当前运行环境为 {platform.system()}，微信桌面自动化仅支持 Windows 客户端环境', 'debug': debug}
        if auto is None:
            return {'success': False, 'detail': 'uiautomation 未安装或不可用，请在 Windows 运行环境中检查依赖', 'debug': debug}

        try:
            with com_initialized():
                step('search_main_window')
                win = auto.WindowControl(searchDepth=1, Name=window_name)
                if not win.Exists(3):
                    return {'success': False, 'detail': f'未找到微信主窗口：{window_name}，请先启动并登录微信', 'debug': debug}

                step('focus_wechat_window')
                if not focus_wechat_window(win, window_name, debug, retries=6):
                    return {'success': False, 'detail': '未能将微信切到前台，请先确认微信已打开且未被系统拦截焦点', 'debug': debug}

                step('open_search_by_ctrl_f')
                auto.SendKeys('{Ctrl}f', waitTime=0.2)
                time.sleep(0.6)

                step('paste_target_remark')
                set_clipboard_text(target_remark)
                auto.SendKeys('{Ctrl}a', waitTime=0.1)
                auto.SendKeys('{Del}', waitTime=0.1)
                auto.SendKeys('{Ctrl}v', waitTime=0.2)
                time.sleep(0.8)

                step('confirm_target')
                auto.SendKeys('{Enter}', waitTime=0.2)
                time.sleep(1.0)

                step('refocus_chat_window')
                if not focus_wechat_window(win, window_name, debug, retries=3):
                    return {'success': False, 'detail': '打开聊天窗口后无法重新聚焦微信', 'debug': debug}

                step('click_input_area')
                click_message_input_area(win)

                step('paste_message')
                set_clipboard_text(message)
                auto.SendKeys('{Ctrl}v', waitTime=0.2)
                time.sleep(0.6)

                step('send_message')
                auto.SendKeys('{Alt}s', waitTime=0.2)
                time.sleep(0.25)
                auto.SendKeys('{Enter}', waitTime=0.2)
                time.sleep(0.35)

                return {'success': True, 'detail': '发送成功', 'debug': debug}
        except Exception as e:
            return {'success': False, 'detail': str(e), 'debug': debug}


wechat_service = WechatAutomationService()


def log_notify(db: Session, **kwargs):
    send_status = kwargs.get('send_status')
    is_real_success = send_status == 'success'
    log = WechatNotifyLog(**kwargs, sent_at=datetime.utcnow() if is_real_success else None)
    db.add(log)
    db.commit()
    return log
