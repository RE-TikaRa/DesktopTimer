DEFAULT_SHORTCUTS = {
    'pause_resume': 'Ctrl+Space',
    'reset': 'Ctrl+R',
    'show_hide': 'Ctrl+H',
    'open_settings': 'Ctrl+,',
    'lock_unlock': 'Ctrl+L',
    'toggle_fullscreen': 'F11',
}

DEFAULT_COUNTDOWN_PRESETS = [
    {"id": "builtin_pomodoro", "name_key": "pomodoro", "mode": "countdown", "hours": 0, "minutes": 25, "seconds": 0},
    {"id": "builtin_short_break", "name_key": "short_break", "mode": "countdown", "hours": 0, "minutes": 5, "seconds": 0},
    {"id": "builtin_long_break", "name_key": "long_break", "mode": "countdown", "hours": 0, "minutes": 15, "seconds": 0},
    {"id": "builtin_10m", "mode": "countdown", "hours": 0, "minutes": 10, "seconds": 0},
    {"id": "builtin_20m", "mode": "countdown", "hours": 0, "minutes": 20, "seconds": 0},
    {"id": "builtin_30m", "mode": "countdown", "hours": 0, "minutes": 30, "seconds": 0},
    {"id": "builtin_45m", "mode": "countdown", "hours": 0, "minutes": 45, "seconds": 0},
    {"id": "builtin_1h", "mode": "countdown", "hours": 1, "minutes": 0, "seconds": 0},
    {"id": "builtin_1h30", "mode": "countdown", "hours": 1, "minutes": 30, "seconds": 0},
    {"id": "builtin_2h", "mode": "countdown", "hours": 2, "minutes": 0, "seconds": 0},
    {"id": "builtin_3h", "mode": "countdown", "hours": 3, "minutes": 0, "seconds": 0},
]

APP_VERSION = "2.0.2"
PROJECT_URL = "https://github.com/RE-TikaRa/DesktopTimer"


class TimerConstants:
    """计时器常量配置"""

    # 计时器刷新（毫秒）
    TIMER_UPDATE_INTERVAL = 1000
    FLASH_INTERVAL = 500

    # 闪烁次数
    FLASH_COUNT_MAX = 6

    # 通知持续时间（秒）
    NOTIFICATION_DURATION_SHORT = 3
    NOTIFICATION_DURATION_LONG = 5

    # 托盘消息持续时间（毫秒）
    TRAY_MESSAGE_DURATION = 1000
