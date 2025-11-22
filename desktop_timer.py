import sys
import json
import os
import random
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QSystemTrayIcon, 
                             QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QSlider, QComboBox, QSpinBox, QCheckBox,
                             QGroupBox, QColorDialog, QFontDialog, QTabWidget,
                             QWidget, QMessageBox, QShortcut, QGridLayout, QFileDialog,
                             QListWidget, QStyle, QScrollArea, QKeySequenceEdit, QFormLayout)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QPoint, QUrl, QTranslator, QLocale
from PyQt5.QtGui import QFont, QIcon, QColor, QKeySequence
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# 尝试导入 Windows 通知
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except ImportError:
    toaster = None

# ------- i18n 兼容层：从 lang 目录加载全局语言表 -------
import os as _os_i18n
import json as _json_i18n

def _load_lang_json(_code: str):
    try:
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            _base_path = _os_i18n.path.dirname(sys.executable)
        else:
            _base_path = _os_i18n.path.dirname(__file__)
        _p = _os_i18n.path.join(_base_path, 'lang', f'{_code}.json')
        with open(_p, 'r', encoding='utf-8') as _f:
            return _json_i18n.load(_f)
    except Exception as _e:
        print(f'[i18n] 加载语言文件失败 {_code}: {_e}')
        return {}

try:
    LANGUAGES
except NameError:
    LANGUAGES = {
        'zh_CN': _load_lang_json('zh_CN'),
        'en_US': _load_lang_json('en_US'),
    }
# ------------------------------------------------------

# ------- 快捷键默认映射（可被 settings 覆盖） -------
DEFAULT_SHORTCUTS = {
    'pause_resume': 'Ctrl+Space',
    'reset': 'Ctrl+R',
    'show_hide': 'Ctrl+H',
    'open_settings': 'Ctrl+,',
    'lock_unlock': 'Ctrl+L',
    'toggle_fullscreen': 'F11',
}

APP_VERSION = "1.0.3"
PROJECT_URL = "https://github.com/RE-TikaRa/DesktopTimer"


class TimerConstants:
    """定时器相关常量"""
    # 定时器间隔(毫秒)
    TIMER_UPDATE_INTERVAL = 1000  # 主定时器更新间隔：每秒
    FLASH_INTERVAL = 500  # 闪烁切换间隔：每0.5秒
    
    # 闪烁次数
    FLASH_COUNT_MAX = 6  # 闪烁6次状态切换 = 3次完整闪烁
    
    # 通知持续时间(秒)
    NOTIFICATION_DURATION_SHORT = 3  # 短通知：3秒
    NOTIFICATION_DURATION_LONG = 5  # 长通知：5秒
    
    # 托盘通知持续时间(毫秒)
    TRAY_MESSAGE_DURATION = 1000  # 托盘消息持续1秒


class L18n:
    def __init__(self, lang_code='zh_CN'):
        self.lang_code = lang_code
        self.translations = {}
        self.load(lang_code)
        
    def load(self, lang_code):
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        
        lang_path = os.path.join(base_path, 'lang', f'{lang_code}.json')
        try:
            with open(lang_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"语言包加载失败: {e}")
            self.translations = {}
            
    def tr(self, key):
        return self.translations.get(key, key)


class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # type: TimerWindow
        self.setWindowTitle(self.tr('settings_title'))
        
        # 设置窗口图标
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "img", "timer_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 隐藏帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.setMinimumSize(700, 800)  # 进一步增加尺寸确保内容显示完整
        self.resize(700, 800)  # 设置初始大小
        self.init_ui()
        
    def tr(self, key):
        """翻译函数"""
        lang = self.parent_window.settings.get("language", "zh_CN")
        return LANGUAGES.get(lang, LANGUAGES['zh_CN']).get(key, key)
    

    

        
    def init_ui(self):
        """初始化设置界面"""
        layout = QVBoxLayout()
        
        # 创建选项卡
        tabs = QTabWidget()
        
        # 外观设置选项卡
        appearance_tab = self.create_appearance_tab()
        tabs.addTab(appearance_tab, self.tr('appearance'))
        
        # 计时模式选项卡
        mode_tab = self.create_mode_tab()
        tabs.addTab(mode_tab, self.tr('timer_mode'))
        
        # 预设选项卡
        preset_tab = self.create_preset_tab()
        tabs.addTab(preset_tab, self.tr('presets'))
        
        # 通用设置选项卡
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, self.tr('general'))
        
        # 关于选项卡
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, self.tr('about'))
        
        layout.addWidget(tabs)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton(self.tr('apply'))
        apply_btn.clicked.connect(self.apply_settings)
        
        ok_btn = QPushButton(self.tr('ok'))
        ok_btn.clicked.connect(self.accept_settings)
        
        cancel_btn = QPushButton(self.tr('cancel'))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_about_tab(self):
        """创建关于选项卡"""
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 主容器
        about_container = QWidget()
        about_layout = QVBoxLayout()
        about_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        # ALP STUDIO LOGO
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        logo_path = os.path.join(base_path, "img", "ALP_STUDIO-logo-full.svg")
        if os.path.exists(logo_path):
            logo_widget = QSvgWidget(logo_path)
            # 设置更大的尺寸，保持logo原始比例
            logo_widget.setFixedSize(340, 200)  # 按用户要求设置尺寸
            logo_widget.setStyleSheet("background: transparent;")
            
            # 创建容器来居中logo
            logo_container = QWidget()
            logo_container.setStyleSheet("background: transparent;")
            logo_layout = QHBoxLayout(logo_container)
            logo_layout.addStretch()
            logo_layout.addWidget(logo_widget)
            logo_layout.addStretch()
            logo_layout.setContentsMargins(0, 0, 0, 10)
            
            about_layout.addWidget(logo_container)
        else:
            # 备用emoji logo
            logo_label = QLabel("🕒")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    margin-bottom: 10px;
                    background: transparent;
                }
            """)
            about_layout.addWidget(logo_label)
        
        # 应用名称
        app_name = QLabel("DesktopTimer")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
                background: transparent;
            }
        """)
        about_layout.addWidget(app_name)
        
        # 副标题
        subtitle = QLabel(self.tr('app_subtitle') if hasattr(self, 'tr') else "专注工作计时器 | 桌面效率工具")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
                background: transparent;
            }
        """)
        about_layout.addWidget(subtitle)
        
        # 分割线
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #bdc3c7; margin: 10px 50px;")
        about_layout.addWidget(line)
        
        # 信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        info_items = [
            ("版本号", f"{APP_VERSION}", None),
            ("作  者", "TikaRa", None),
            ("邮  箱", "163mail@re-TikaRa.fun", "mailto:163mail@re-TikaRa.fun"),
            ("个人网站", "re-tikara.fun", "https://re-tikara.fun"),
            ("代码仓库", PROJECT_URL, PROJECT_URL),
            ("B站主页", "夜雨安歌_TikaRa", "https://space.bilibili.com/374412219")
        ]
        
        for label_text, value_text, link_url in info_items:
            item_layout = QHBoxLayout()
            
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #34495e;
                    background: transparent;
                }
            """)
            label.setMinimumWidth(80)
            
            if link_url:
                value = QLabel(f'<a href="{link_url}" style="color: #3498db; text-decoration: none;">{value_text}</a>')
                value.setOpenExternalLinks(True)
                value.setStyleSheet("""
                    QLabel {
                        color: #3498db;
                        background: transparent;
                    }
                    QLabel:hover {
                        text-decoration: underline;
                    }
                """)
            else:
                value = QLabel(value_text)
                value.setStyleSheet("""
                    QLabel {
                        color: #2c3e50;
                        background: transparent;
                    }
                """)
            
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            item_layout.addStretch()
            
            info_layout.addLayout(item_layout)
        
        about_layout.addLayout(info_layout)
        
        # 底部空白
        about_layout.addStretch()
        
        about_container.setLayout(about_layout)
        layout.addWidget(about_container)
        layout.addStretch()
        
        widget.setLayout(layout)
        
        # 设置滚动区域
        scroll.setWidget(widget)
        
        # 创建包装器小部件
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(scroll)
        wrapper.setLayout(wrapper_layout)
        
        return wrapper
        
    def create_appearance_tab(self):
        """创建外观设置选项卡"""
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 字体设置组
        font_group = QGroupBox(self.tr('font_settings'))
        font_layout = QVBoxLayout()
        
        font_btn_layout = QHBoxLayout()
        font_label = QLabel(f'{self.tr("current_font")}: {self.parent_window.settings.get("font_family", "Consolas")}, {self.tr("font_size")}: {self.parent_window.settings.get("font_size", 96)}')
        self.font_label = font_label
        font_btn = QPushButton(self.tr('choose_font'))
        font_btn.clicked.connect(self.choose_font)
        font_btn_layout.addWidget(font_label)
        font_btn_layout.addWidget(font_btn)
        font_layout.addLayout(font_btn_layout)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # 颜色设置组
        color_group = QGroupBox(self.tr('color_settings'))
        color_layout = QVBoxLayout()
        
        # 字体颜色
        text_color_layout = QHBoxLayout()
        text_color_label = QLabel(self.tr('text_color') + ':')
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(80, 30)
        self.update_color_button(self.text_color_btn, self.parent_window.settings.get("text_color", "#E0E0E0"))
        self.text_color_btn.clicked.connect(self.choose_text_color)
        text_color_layout.addWidget(text_color_label)
        text_color_layout.addWidget(self.text_color_btn)
        text_color_layout.addStretch()
        color_layout.addLayout(text_color_layout)
        
        # 背景颜色
        bg_color_layout = QHBoxLayout()
        bg_color_label = QLabel(self.tr('bg_color') + ':')
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(80, 30)
        self.update_color_button(self.bg_color_btn, self.parent_window.settings.get("bg_color", "#1E1E1E"))
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        bg_color_layout.addWidget(bg_color_label)
        bg_color_layout.addWidget(self.bg_color_btn)
        bg_color_layout.addStretch()
        color_layout.addLayout(bg_color_layout)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # 透明度设置组
        opacity_group = QGroupBox(self.tr('opacity_settings'))
        opacity_layout = QVBoxLayout()
        
        opacity_slider_layout = QHBoxLayout()
        opacity_label = QLabel(self.tr('bg_opacity') + ':')
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(255)
        self.opacity_slider.setValue(self.parent_window.settings.get("bg_opacity", 200))
        self.opacity_value_label = QLabel(f'{self.parent_window.settings.get("bg_opacity", 200)}')
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_value_label.setText(f'{v}')
        )
        opacity_slider_layout.addWidget(opacity_label)
        opacity_slider_layout.addWidget(self.opacity_slider)
        opacity_slider_layout.addWidget(self.opacity_value_label)
        opacity_layout.addLayout(opacity_slider_layout)
        
        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)
        
        # 窗口样式设置
        style_group = QGroupBox(self.tr('window_style'))
        style_layout = QVBoxLayout()
        
        self.rounded_check = QCheckBox(self.tr('rounded_corners'))
        self.rounded_check.setChecked(self.parent_window.settings.get("rounded_corners", True))
        style_layout.addWidget(self.rounded_check)
        
        radius_layout = QHBoxLayout()
        radius_label = QLabel(self.tr('corner_radius') + ':')
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 50)
        self.radius_spin.setValue(self.parent_window.settings.get("corner_radius", 15))
        self.radius_spin.setSuffix(' px')
        radius_layout.addWidget(radius_label)
        radius_layout.addWidget(self.radius_spin)
        radius_layout.addStretch()
        style_layout.addLayout(radius_layout)
        
        # 窗口大小调整
        # 窗口大小设置 - 使用滑块控制字体大小
        size_layout = QVBoxLayout()
        size_label_row = QHBoxLayout()
        size_label = QLabel(self.tr('window_size') + ':')
        size_label_row.addWidget(size_label)
        size_label_row.addStretch()
        size_layout.addLayout(size_label_row)

        slider_row = QHBoxLayout()
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(48, 220)
        self.size_slider.setSingleStep(2)
        current_size = self.parent_window.settings.get("font_size", 96)
        self.size_slider.setValue(current_size)
        self.size_value_label = QLabel(f"{current_size}px")
        self.size_slider.valueChanged.connect(lambda v: self.size_value_label.setText(f"{v}px"))
        slider_row.addWidget(self.size_slider, 1)
        slider_row.addWidget(self.size_value_label)
        size_layout.addLayout(slider_row)
        style_layout.addLayout(size_layout)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # 夜读模式
        night_group = QGroupBox(self.tr('night_mode'))
        night_layout = QVBoxLayout()
        
        self.night_mode_check = QCheckBox(self.tr('night_mode_desc'))
        self.night_mode_check.setChecked(self.parent_window.settings.get("night_mode", False))
        night_layout.addWidget(self.night_mode_check)
        
        night_group.setLayout(night_layout)
        layout.addWidget(night_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # 设置滚动区域
        scroll.setWidget(widget)
        
        # 创建包装器小部件
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(scroll)
        wrapper.setLayout(wrapper_layout)
        
        return wrapper
        
    def create_mode_tab(self):
        """创建计时模式选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        mode_group = QGroupBox(self.tr('timer_mode'))
        mode_layout = QVBoxLayout()
        
        # 模式选择
        mode_select_layout = QHBoxLayout()
        mode_label = QLabel(self.tr('mode') + ':')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([self.tr('count_up_mode'), self.tr('countdown_mode'), self.tr('clock_mode')])
        # 根据语言无关的键设置选中项，兼容旧存储
        key = self.parent_window.settings.get('timer_mode_key')
        if not key:
            key = TimerWindow.derive_mode_key(self.parent_window.settings.get('timer_mode', ''))
            self.parent_window.settings['timer_mode_key'] = key
        index = {'countup': 0, 'countdown': 1, 'clock': 2}.get(key, 1)
        self.mode_combo.setCurrentIndex(index)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_select_layout.addWidget(mode_label)
        mode_select_layout.addWidget(self.mode_combo)
        mode_select_layout.addStretch()
        mode_layout.addLayout(mode_select_layout)
        
        # 倒计时设置
        self.countdown_widget = QWidget()
        countdown_layout = QVBoxLayout()
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel(self.tr('countdown_time') + ':'))
        
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 99)
        self.hours_spin.setSuffix(' ' + self.tr('hours'))
        self.hours_spin.setValue(self.parent_window.settings.get("countdown_hours", 0))
        
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setSuffix(' ' + self.tr('minutes'))
        self.minutes_spin.setValue(self.parent_window.settings.get("countdown_minutes", 25))
        
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setSuffix(' ' + self.tr('seconds'))
        self.seconds_spin.setValue(self.parent_window.settings.get("countdown_seconds", 0))
        
        time_layout.addWidget(self.hours_spin)
        time_layout.addWidget(self.minutes_spin)
        time_layout.addWidget(self.seconds_spin)
        time_layout.addStretch()
        
        countdown_layout.addLayout(time_layout)
        
        # 倒计时完成后的操作
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel(self.tr('countdown_action') + ':'))
        self.countdown_action = QComboBox()
        self.countdown_action.addItems([self.tr('beep'), self.tr('flash'), self.tr('beep_flash')])
        # 匹配现有设置
        current_action = self.parent_window.settings.get("countdown_action", "beep")
        for i in range(self.countdown_action.count()):
            if self.countdown_action.itemText(i) in current_action or current_action in self.countdown_action.itemText(i):
                self.countdown_action.setCurrentIndex(i)
                break
        action_layout.addWidget(self.countdown_action)
        action_layout.addStretch()
        countdown_layout.addLayout(action_layout)
        
        self.countdown_widget.setLayout(countdown_layout)
        mode_layout.addWidget(self.countdown_widget)
        
        # 时钟模式设置
        self.clock_widget = QWidget()
        clock_layout = QVBoxLayout()
        
        # 时间格式（24小时制 / 12小时制）
        format_layout = QHBoxLayout()
        format_label = QLabel(self.tr('time_format') + ':')
        self.clock_format_combo = QComboBox()
        self.clock_format_combo.addItems([
            self.tr('clock_24h_format'),
            self.tr('clock_12h_format') if 'clock_12h_format' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) else ('12小时制' if self.tr('quit') == '退出' else '12-Hour Format'),
        ])
        self.clock_format_combo.setCurrentIndex(0 if self.parent_window.settings.get("clock_format_24h", True) else 1)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.clock_format_combo)
        format_layout.addStretch()
        clock_layout.addLayout(format_layout)
        
        # 显示秒
        seconds_layout = QHBoxLayout()
        self.clock_seconds_check = QCheckBox(self.tr('clock_show_seconds'))
        self.clock_seconds_check.setChecked(self.parent_window.settings.get("clock_show_seconds", True))
        seconds_layout.addWidget(self.clock_seconds_check)
        seconds_layout.addStretch()
        clock_layout.addLayout(seconds_layout)
        
        # 显示日期
        date_layout = QHBoxLayout()
        self.clock_date_check = QCheckBox(self.tr('clock_show_date'))
        self.clock_date_check.setChecked(self.parent_window.settings.get("clock_show_date", True))
        date_layout.addWidget(self.clock_date_check)
        date_layout.addStretch()
        clock_layout.addLayout(date_layout)

        # 12小时制：显示 AM/PM/上午/下午 标签
        ampm_layout = QHBoxLayout()
        self.clock_am_pm_check = QCheckBox(self.tr('clock_show_am_pm'))
        self.clock_am_pm_check.setChecked(self.parent_window.settings.get("clock_show_am_pm", True))
        ampm_layout.addWidget(self.clock_am_pm_check)
        ampm_layout.addStretch()
        clock_layout.addLayout(ampm_layout)

        # 12小时制：AM/PM 样式选择（en: AM/PM, zh: 上午/下午）
        style_layout = QHBoxLayout()
        style_label = QLabel(self.tr('clock_am_pm_style') + ':')
        self.am_pm_style_combo = QComboBox()
        self.am_pm_style_combo.addItems([
            self.tr('am_pm_style_en') or 'AM/PM',
            self.tr('am_pm_style_zh') or '上午/下午',
        ])
        current_style = self.parent_window.settings.get("clock_am_pm_style", "zh")
        self.am_pm_style_combo.setCurrentIndex(0 if current_style == 'en' else 1)
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.am_pm_style_combo)
        style_layout.addStretch()
        clock_layout.addLayout(style_layout)

        # 12小时制：AM/PM 位置（时间前/时间后）
        pos_layout = QHBoxLayout()
        pos_label = QLabel(self.tr('clock_am_pm_position') + ':')
        self.am_pm_pos_combo = QComboBox()
        self.am_pm_pos_combo.addItems([
            self.tr('am_pm_pos_before') or 'Before time',
            self.tr('am_pm_pos_after') or 'After time',
        ])
        current_pos = self.parent_window.settings.get("clock_am_pm_position", "before")
        self.am_pm_pos_combo.setCurrentIndex(0 if current_pos == 'before' else 1)
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(self.am_pm_pos_combo)
        pos_layout.addStretch()
        clock_layout.addLayout(pos_layout)

        # 当切换24小时制时，禁用 AM/PM 相关配置
        def _update_ampm_enabled():
            is_24h = (self.clock_format_combo.currentIndex() == 0)
            self.clock_am_pm_check.setEnabled(not is_24h)
            # 仅当非24小时制且勾选显示上/下午时可编辑样式和位置
            enable_detail = (not is_24h) and self.clock_am_pm_check.isChecked()
            self.am_pm_style_combo.setEnabled(enable_detail)
            self.am_pm_pos_combo.setEnabled(enable_detail)
        self.clock_format_combo.currentIndexChanged.connect(lambda _: _update_ampm_enabled())
        self.clock_am_pm_check.toggled.connect(lambda _: _update_ampm_enabled())
        _update_ampm_enabled()
        
        self.clock_widget.setLayout(clock_layout)
        mode_layout.addWidget(self.clock_widget)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 根据当前模式显示/隐藏倒计时设置
        self.on_mode_changed(self.mode_combo.currentText())
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_preset_tab(self):
        """创建预设选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        preset_group = QGroupBox(self.tr('presets'))
        preset_layout = QVBoxLayout()
        
        preset_label = QLabel(self.tr('preset_hint'))
        preset_layout.addWidget(preset_label)
        
        # 预设按钮 - 扩展更多选项
        presets = [
            (self.tr('pomodoro'), 0, 25, 0),
            (self.tr('short_break'), 0, 5, 0),
            (self.tr('long_break'), 0, 15, 0),
            ('10 ' + self.tr('minutes'), 0, 10, 0),
            ('20 ' + self.tr('minutes'), 0, 20, 0),
            ('30 ' + self.tr('minutes'), 0, 30, 0),
            ('45 ' + self.tr('minutes'), 0, 45, 0),
            ('1 ' + self.tr('hours'), 1, 0, 0),
            ('1.5 ' + self.tr('hours'), 1, 30, 0),
            ('2 ' + self.tr('hours'), 2, 0, 0),
            ('3 ' + self.tr('hours'), 3, 0, 0),
            (self.tr('custom'), -1, -1, -1),
        ]
        
        # 使用网格布局
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        
        row, col = 0, 0
        for preset_name, hours, minutes, seconds in presets:
            btn = QPushButton(preset_name)
            btn.setMinimumHeight(35)
            if hours == -1:  # 自定义按钮
                btn.clicked.connect(self.show_custom_preset)
            else:
                btn.clicked.connect(lambda _, h=hours, m=minutes, s=seconds: 
                                  self.apply_preset(h, m, s))
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:  # 每行3个按钮
                col = 0
                row += 1
        
        grid_widget.setLayout(grid_layout)
        preset_layout.addWidget(grid_widget)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_general_tab(self):
        """创建通用设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 语言设置
        lang_group = QGroupBox(self.tr('language'))
        lang_layout = QVBoxLayout()
        
        lang_select_layout = QHBoxLayout()
        lang_label = QLabel(self.tr('language') + ':')
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['简体中文', 'English'])
        current_lang = '简体中文' if self.parent_window.settings.get("language", "zh_CN") == "zh_CN" else 'English'
        self.lang_combo.setCurrentText(current_lang)
        lang_select_layout.addWidget(lang_label)
        lang_select_layout.addWidget(self.lang_combo)
        lang_select_layout.addStretch()
        lang_layout.addLayout(lang_select_layout)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # 启动设置
        startup_group = QGroupBox(self.tr('auto_start'))
        startup_layout = QVBoxLayout()
        
        self.auto_start_check = QCheckBox(self.tr('auto_start_timer'))
        self.auto_start_check.setChecked(self.parent_window.settings.get("auto_start_timer", True))
        startup_layout.addWidget(self.auto_start_check)
        
        # 启动模式行为设置
        behavior_row = QHBoxLayout()
        behavior_label = QLabel(self.tr('startup_mode_behavior') + ':')
        self.startup_behavior_combo = QComboBox()
        self.startup_behavior_combo.addItems([
            LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}).get('startup_mode_restore_last', '恢复上次模式' if self.tr('quit') == '退出' else 'Restore last mode'),
            LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}).get('startup_mode_fixed', '固定为指定模式' if self.tr('quit') == '退出' else 'Always use fixed mode'),
        ])
        self.startup_behavior_combo.setCurrentIndex(0 if self.parent_window.settings.get('startup_mode_behavior', 'restore') == 'restore' else 1)
        behavior_row.addWidget(behavior_label)
        behavior_row.addWidget(self.startup_behavior_combo)
        behavior_row.addStretch()
        startup_layout.addLayout(behavior_row)
        
        fixed_row = QHBoxLayout()
        fixed_label = QLabel(self.tr('startup_fixed_mode') + ':')
        self.startup_fixed_combo = QComboBox()
        self.startup_fixed_combo.addItems([
            self.tr('count_up_mode'),
            self.tr('countdown_mode'),
            self.tr('clock_mode'),
        ])
        fixed_map = {'countup': 0, 'countdown': 1, 'clock': 2}
        self.startup_fixed_combo.setCurrentIndex(fixed_map.get(self.parent_window.settings.get('startup_fixed_mode_key', 'countdown'), 1))
        fixed_row.addWidget(fixed_label)
        fixed_row.addWidget(self.startup_fixed_combo)
        fixed_row.addStretch()
        startup_layout.addLayout(fixed_row)
        
        def _update_fixed_enabled():
            self.startup_fixed_combo.setEnabled(self.startup_behavior_combo.currentIndex() == 1)
        self.startup_behavior_combo.currentIndexChanged.connect(lambda _: _update_fixed_enabled())
        _update_fixed_enabled()
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # 声音设置
        sound_group = QGroupBox(self.tr('sound_settings'))
        sound_layout = QVBoxLayout()
        
        self.enable_sound_check = QCheckBox(self.tr('enable_sound'))
        self.enable_sound_check.setChecked(self.parent_window.settings.get("enable_sound", True))
        sound_layout.addWidget(self.enable_sound_check)
        
        self.enable_popup_check = QCheckBox(self.tr('enable_popup'))
        self.enable_popup_check.setChecked(self.parent_window.settings.get("enable_popup", True))
        sound_layout.addWidget(self.enable_popup_check)
        
        # 铃声选择
        sound_file_layout = QHBoxLayout()
        sound_file_label = QLabel(self.tr('sound_file') + ':')
        current_sound = self.parent_window.settings.get("sound_file", "")
        if current_sound and os.path.exists(current_sound):
            display_name = os.path.basename(current_sound)
        else:
            display_name = self.tr('no_sound_file')
        self.sound_file_label = QLabel(display_name)
        self.sound_file_label.setWordWrap(True)
        self.sound_file_label.setStyleSheet('QLabel { color: #666; }')
        choose_sound_btn = QPushButton(self.tr('choose_sound'))
        choose_sound_btn.clicked.connect(self.choose_sound_file)
        sound_file_layout.addWidget(sound_file_label)
        sound_file_layout.addWidget(self.sound_file_label, 1)
        sound_file_layout.addWidget(choose_sound_btn)
        sound_layout.addLayout(sound_file_layout)
        
        # 铃声文件夹和随机按钮
        folder_layout = QHBoxLayout()
        folder_btn = QPushButton(self.tr('open_folder'))
        folder_btn.clicked.connect(self.open_sound_folder)
        test_btn = QPushButton(self.tr('test_sound'))
        test_btn.clicked.connect(self.test_sound)
        random_btn = QPushButton('随机' if self.tr('quit') == '退出' else 'Random')
        random_btn.clicked.connect(self.random_sound)
        folder_layout.addWidget(folder_btn)
        folder_layout.addWidget(test_btn)
        folder_layout.addWidget(random_btn)
        folder_layout.addStretch()
        sound_layout.addLayout(folder_layout)
        
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        # 快捷键设置（可编辑）
        shortcut_group = QGroupBox(self.tr('shortcuts'))
        shortcut_layout = QVBoxLayout()

        # 读取当前快捷键设置（若不存在，用默认）
        current_shortcuts = dict(DEFAULT_SHORTCUTS)
        current_shortcuts.update(self.parent_window.settings.get('shortcuts', {}))

        # 准备字段：键 -> (翻译文本, setting_key)
        fields = [
            (self.tr('shortcut_pause') or '暂停/继续', 'pause_resume'),
            (self.tr('shortcut_reset') or '重置', 'reset'),
            (self.tr('shortcut_hide') or '显示/隐藏', 'show_hide'),
            (self.tr('shortcut_settings') or '打开设置', 'open_settings'),
            (getattr(self, 'tr', lambda k: None)('shortcut_lock') or '锁定/解锁', 'lock_unlock'),
            ((self.tr('shortcut_fullscreen') if 'shortcut_fullscreen' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) else ('\u5168\u5c4f' if self.tr('quit') == '\u9000\u51fa' else 'Toggle Fullscreen')), 'toggle_fullscreen'),
        ]

        self.shortcut_edits = {}
        for label_text, skey in fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text + ':'))
            editor = QKeySequenceEdit()
            try:
                editor.setKeySequence(QKeySequence(current_shortcuts.get(skey, DEFAULT_SHORTCUTS[skey])))
            except Exception:
                editor.setKeySequence(QKeySequence(DEFAULT_SHORTCUTS[skey]))
            row.addWidget(editor, 1)
            row.addStretch()
            shortcut_layout.addLayout(row)
            self.shortcut_edits[skey] = editor

        hint = QLabel(self.tr('shortcut_edit_hint') if 'shortcut_edit_hint' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) else '提示：点击后按下组合键（如 Ctrl+Space）。')
        hint.setStyleSheet('color:#666;')
        shortcut_layout.addWidget(hint)

        shortcut_group.setLayout(shortcut_layout)
        layout.addWidget(shortcut_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def on_mode_changed(self, mode):
        """模式改变时的处理"""
        is_countdown = self.tr('countdown_mode') in mode or '倒计时' in mode
        is_clock = self.tr('clock_mode') in mode or '时钟' in mode
        
        self.countdown_widget.setVisible(is_countdown)
        self.clock_widget.setVisible(is_clock)
        
    def choose_font(self):
        """选择字体"""
        current_font = QFont(self.parent_window.settings.get("font_family", "Consolas"), 
                           self.parent_window.settings.get("font_size", 96))
        
        # 创建字体对话框并设置中文标题和选项
        font_dialog = QFontDialog(current_font, self)
        font_dialog.setWindowTitle("选择字体")  # 直接使用中文标题
        
        # 强制使用非原生对话框以便更好地控制界面
        font_dialog.setOption(QFontDialog.DontUseNativeDialog, True)
        
        # 设置对话框的大小和位置
        font_dialog.resize(640, 480)
        
        if font_dialog.exec_() == QFontDialog.Accepted:
            font = font_dialog.selectedFont()
            self.parent_window.settings["font_family"] = font.family()
            self.parent_window.settings["font_size"] = font.pointSize()
            self.font_label.setText(f'{self.tr("current_font")}: {font.family()}, {self.tr("font_size")}: {font.pointSize()}')
            
    def choose_text_color(self):
        """选择文字颜色"""
        color = QColorDialog.getColor(QColor(self.parent_window.settings.get("text_color", "#E0E0E0")), self)
        if color.isValid():
            self.parent_window.settings["text_color"] = color.name()
            self.update_color_button(self.text_color_btn, color.name())
            
    def choose_bg_color(self):
        """选择背景颜色"""
        color = QColorDialog.getColor(QColor(self.parent_window.settings.get("bg_color", "#1E1E1E")), self)
        if color.isValid():
            self.parent_window.settings["bg_color"] = color.name()
            self.update_color_button(self.bg_color_btn, color.name())
            
    def update_color_button(self, button, color):
        """更新颜色按钮的显示"""
        button.setStyleSheet(f'background-color: {color}; border: 1px solid #ccc;')
        
    def apply_preset(self, hours, minutes, seconds):
        """应用预设"""
        self.mode_combo.setCurrentText(self.tr('countdown_mode'))
        self.hours_spin.setValue(hours)
        self.minutes_spin.setValue(minutes)
        self.seconds_spin.setValue(seconds)
        QMessageBox.information(self, self.tr('preset_applied'), 
                              self.tr('preset_applied_msg').format(hours, minutes, seconds))
        
    def show_custom_preset(self):
        """显示自定义预设对话框"""
        QMessageBox.information(self, self.tr('custom_preset_title'), 
                              self.tr('custom_preset_msg'))
    
    def choose_sound_file(self):
        """选择铃声文件"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        
        sound_dir = os.path.join(base_path, 'sounds')
        if not os.path.exists(sound_dir):
            sound_dir = base_path
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('choose_sound'),
            sound_dir,
            "Sound Files (*.wav *.mp3 *.ogg);;All Files (*.*)"
        )
        
        if file_path:
            # 如果文件在 sounds 文件夹内，保存相对路径
            try:
                rel_path = os.path.relpath(file_path, base_path)
                # 如果相对路径在 sounds 文件夹内，使用相对路径
                if rel_path.startswith('sounds'):
                    self.parent_window.settings["sound_file"] = rel_path
                else:
                    # 否则使用绝对路径（用户选择了外部文件）
                    self.parent_window.settings["sound_file"] = file_path
            except ValueError:
                # 不同盘符，使用绝对路径
                self.parent_window.settings["sound_file"] = file_path
            
            self.sound_file_label.setText(os.path.basename(file_path))
            
    def open_sound_folder(self):
        """打开铃声文件夹"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        
        sound_dir = os.path.join(base_path, 'sounds')
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            QMessageBox.information(
                self,
                self.tr('sound_folder_created'),
                self.tr('sound_folder_created_msg')
            )
        
        # 打开文件夹（跨平台兼容）
        import platform
        import subprocess
        
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(sound_dir)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", sound_dir])
            else:  # Linux and others
                subprocess.call(["xdg-open", sound_dir])
        except Exception as e:
            print(f"打开文件夹失败: {e}")
            QMessageBox.warning(
                self,
                "错误",
                f"无法打开文件夹: {sound_dir}\n请手动打开该路径。"
            )
        
    def test_sound(self):
        """测试铃声"""
        sound_file = self.parent_window.settings.get("sound_file", "")
        if sound_file:
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(sound_file):
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                else:
                    base_path = os.path.dirname(__file__)
                sound_file = os.path.join(base_path, sound_file)
            
            if os.path.exists(sound_file):
                self.parent_window.play_sound(sound_file)
            else:
                QApplication.beep()
        else:
            QApplication.beep()
    
    def random_sound(self):
        """随机选择铃声"""
        sound_files = self.parent_window.get_sound_files()
        if sound_files:
            selected_sound = random.choice(sound_files)
            # 保存相对路径
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(__file__)
            rel_path = os.path.relpath(selected_sound, base_path)
            self.parent_window.settings["sound_file"] = rel_path
            self.sound_file_label.setText(os.path.basename(selected_sound))
            # 播放选中的铃声
            self.parent_window.play_sound(selected_sound)
        else:
            QMessageBox.warning(
                self,
                self.tr('no_sound_files_found'),
                self.tr('no_sound_files_msg')
            )
    
    def _validate_shortcuts(self):
        """验证快捷键是否有冲突"""
        if not hasattr(self, 'shortcut_edits'):
            return True
        
        used_keys = {}
        conflicts = []
        
        for name, editor in self.shortcut_edits.items():
            seq = editor.keySequence().toString()
            if not seq:  # 空快捷键跳过
                continue
            if seq in used_keys:
                # 翻译键名
                name_map = {
                    'pause_resume': self.tr('shortcut_pause'),
                    'reset': self.tr('shortcut_reset'),
                    'show_hide': self.tr('shortcut_hide'),
                    'open_settings': self.tr('shortcut_settings'),
                    'lock_unlock': self.tr('shortcut_lock'),
                    'toggle_fullscreen': self.tr('shortcut_fullscreen') if 'shortcut_fullscreen' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) else 'Full Screen',
                }
                conflicts.append((name_map.get(name, name), 
                                name_map.get(used_keys[seq], used_keys[seq]), 
                                seq))
            else:
                used_keys[seq] = name
        
        if conflicts:
            # 显示冲突警告
            msg_text = (self.tr('shortcut_conflict_title') if 'shortcut_conflict_title' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) 
                       else '快捷键冲突' if self.tr('quit') == '退出' else 'Shortcut Conflict')
            msg_detail = '\n'.join([f"{key}: {old} ⚠ {new}" for new, old, key in conflicts])
            QMessageBox.warning(self, msg_text, msg_detail)
            return False
        return True
        
    def apply_settings(self):
        """应用设置"""
        self.parent_window.settings["bg_opacity"] = self.opacity_slider.value()
        self.parent_window.settings["night_mode"] = self.night_mode_check.isChecked()
        self.parent_window.settings["timer_mode"] = self.mode_combo.currentText()
        # 保存语言无关的键
        self.parent_window.settings["timer_mode_key"] = {0: 'countup', 1: 'countdown', 2: 'clock'}.get(self.mode_combo.currentIndex(), 'countdown')
        self.parent_window.settings["countdown_hours"] = self.hours_spin.value()
        self.parent_window.settings["countdown_minutes"] = self.minutes_spin.value()
        self.parent_window.settings["countdown_seconds"] = self.seconds_spin.value()
        self.parent_window.settings["countdown_action"] = self.countdown_action.currentText()
        # 时间格式：索引0为24小时制，1为12小时制
        self.parent_window.settings["clock_format_24h"] = (self.clock_format_combo.currentIndex() == 0)
        self.parent_window.settings["clock_show_seconds"] = self.clock_seconds_check.isChecked()
        self.parent_window.settings["clock_show_date"] = self.clock_date_check.isChecked()
        self.parent_window.settings["clock_show_am_pm"] = self.clock_am_pm_check.isChecked()
        self.parent_window.settings["clock_am_pm_style"] = 'en' if self.am_pm_style_combo.currentIndex() == 0 else 'zh'
        self.parent_window.settings["clock_am_pm_position"] = 'before' if self.am_pm_pos_combo.currentIndex() == 0 else 'after'
        self.parent_window.settings["language"] = "zh_CN" if self.lang_combo.currentText() == "简体中文" else "en_US"
        self.parent_window.settings["auto_start_timer"] = self.auto_start_check.isChecked()
        self.parent_window.settings["rounded_corners"] = self.rounded_check.isChecked()
        self.parent_window.settings["corner_radius"] = self.radius_spin.value()
        self.parent_window.settings["enable_sound"] = self.enable_sound_check.isChecked()
        self.parent_window.settings["enable_popup"] = self.enable_popup_check.isChecked()
        
        # 保存启动模式行为
        self.parent_window.settings['startup_mode_behavior'] = 'restore' if self.startup_behavior_combo.currentIndex() == 0 else 'fixed'
        self.parent_window.settings['startup_fixed_mode_key'] = {0: 'countup', 1: 'countdown', 2: 'clock'}.get(self.startup_fixed_combo.currentIndex(), 'countdown')

        # 保存快捷键到设置
        shortcuts_saved = dict(self.parent_window.settings.get('shortcuts', {}))
        for skey, editor in getattr(self, 'shortcut_edits', {}).items():
            seq = editor.keySequence().toString()
            # 若为空，使用默认
            shortcuts_saved[skey] = seq if seq else DEFAULT_SHORTCUTS.get(skey, '')
        self.parent_window.settings['shortcuts'] = shortcuts_saved
        
        # 应用窗口大小设置（滑块控制字体大小）
        self.parent_window.settings["font_size"] = self.size_slider.value()
        
        self.parent_window.apply_settings()
        # 让主窗口根据新快捷键重载绑定
        try:
            self.parent_window.reload_shortcuts()
        except Exception:
            pass
        self.parent_window.save_settings(immediate=True)  # 用户主动保存，立即执行
        
    def accept_settings(self):
        """确定设置（带快捷键冲突检测）"""
        # 先验证快捷键
        if not self._validate_shortcuts():
            return  # 有冲突，不保存
        self.apply_settings()
        self.accept()


class TimerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 计算基础路径（一次性，避免重复）
        self.base_path = self._get_base_path()
        
        self.l18n = L18n(lang_code=self.get_language())
        self.load_settings()
        # 启动时根据设置决定初始模式
        try:
            behavior = self.settings.get('startup_mode_behavior', 'restore')
            if behavior == 'fixed':
                fixed_key = self.settings.get('startup_fixed_mode_key', 'countdown')
                if fixed_key not in ('countup', 'countdown', 'clock'):
                    fixed_key = 'countdown'
                self.settings['timer_mode_key'] = fixed_key
                # 同步可读文本（仅用于 UI 展示，不参与逻辑判断）
                key_to_text = {
                    'countup': self.tr('count_up_mode'),
                    'countdown': self.tr('countdown_mode'),
                    'clock': self.tr('clock_mode'),
                }
                self.settings['timer_mode'] = key_to_text.get(fixed_key, self.tr('countdown_mode'))
        except Exception as _e:
            print(f"[DEBUG] enforce startup mode failed: {_e}")
        self.elapsed_seconds = 0
        self.is_running = self.settings.get("auto_start_timer", False)
        self.is_flashing = False
        self.is_locked = False  # 窗口锁定状态
        self.is_fullscreen = False  # ȫ��״̬
        self._stored_geometry = None
        self._stored_window_flags = None
        self.last_displayed_text = ""  # 缓存上一次显示的文本，用于优化窗口大小调整
        self.media_player = QMediaPlayer()
        
        # 延迟保存机制
        self._pending_save = False  # 标记是否有待保存的设置
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)  # 单次触发
        self._save_timer.timeout.connect(self._do_save_settings)
        self._save_delay_ms = 1000  # 延迟1秒保存
        
        # 设置窗口图标
        icon_path = self.get_resource_path("img", "timer_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.init_ui()
        self.init_tray()
        self.init_timer()
        self.init_shortcuts()
        self.apply_settings()
        self.ensure_sounds_folder()
    
    @staticmethod
    def _get_base_path():
        """获取应用程序基础路径"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    
    def get_resource_path(self, *paths):
        """
        获取资源文件路径
        
        Args:
            *paths: 路径组件，例如 'img', 'timer_icon.ico'
            
        Returns:
            完整的资源文件路径
        """
        return os.path.join(self.base_path, *paths)
    
    @staticmethod
    def derive_mode_key(mode_text):
        """
        从模式文本推断语言无关的模式键
        
        Args:
            mode_text: 模式文本（可能是中文或英文）
            
        Returns:
            'countup' | 'countdown' | 'clock'
        """
        if not isinstance(mode_text, str):
            return 'countdown'
        
        text_lower = mode_text.lower()
        
        # 正计时判断
        if any(keyword in text_lower for keyword in ['count up', '正计时']):
            return 'countup'
        
        # 时钟判断
        if any(keyword in text_lower for keyword in ['clock', '时钟']):
            return 'clock'
        
        # 默认倒计时
        return 'countdown'
        
    def get_language(self):
        """从设置获取语言代码"""
        try:
            settings_path = self.get_resource_path("settings", "timer_settings.json")
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings.get('language', 'zh_CN')
        except Exception:
            return 'zh_CN'
        
    def tr(self, key):
        return self.l18n.tr(key)
        
    def load_settings(self):
        """加载设置"""
        settings_dir = self.get_resource_path("settings")
        self.settings_file = os.path.join(settings_dir, "timer_settings.json")
        # 调试：打印设置文件路径
        try:
            print(f"[DEBUG] settings file: {self.settings_file}")
        except Exception:
            pass
        
        default_settings = {
            "font_family": "Consolas",
            "font_size": 96,  # 增加字体大小，窗口会更大
            "text_color": "#E0E0E0",
            "bg_color": "#1E1E1E",
            "bg_opacity": 200,
            "night_mode": False,
            "timer_mode": "倒计时",  # 默认倒计时模式
            # 语言无关的计时模式键（与 timer_mode 文本解耦）
            "timer_mode_key": "countdown",  # 可选: 'countup' | 'countdown' | 'clock'
            # 倒计时默认时间设置
            "countdown_hours": 0,
            "countdown_minutes": 25,
            "countdown_seconds": 0,
            # 倒计时结束动作
            "countdown_action": "beep",  # 可选: 'beep' | 'sound' | 'flash' | 'notify'
            # 音效文件设置
            "sound_file": "sounds/Alarm01.wav",  # 默认音效
            # 语言设置
            "language": "zh_CN",
            # 时钟模式设置
            "clock_format_24h": True,  # 24小时制
            "clock_show_seconds": True,  # 显示秒数
            "clock_show_date": False,  # 显示日期
            # 12小时制时的 AM/PM 显示与样式
            "clock_show_am_pm": True,
            "clock_am_pm_style": "zh",  # 可选: 'en' | 'zh'
            "clock_am_pm_position": "before",  # 可选: 'before' | 'after'
            # 启动行为：恢复上次/固定模式
            "startup_mode_behavior": "restore",  # 可选: 'restore' | 'fixed'
            "startup_fixed_mode_key": "countdown",  # 固定模式键
            # 自定义快捷键（如 settings 中不存在，则使用默认）
            "shortcuts": dict(DEFAULT_SHORTCUTS),
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                try:
                    print(f"[DEBUG] loaded timer_mode_key={self.settings.get('timer_mode_key')} timer_mode={self.settings.get('timer_mode')}")
                except Exception:
                    pass
                # 确保所有键都存在
                for key, value in default_settings.items():
                    if key not in self.settings:
                        self.settings[key] = value
                # 确保快捷键子项存在并合并默认
                if 'shortcuts' not in self.settings or not isinstance(self.settings['shortcuts'], dict):
                    self.settings['shortcuts'] = dict(DEFAULT_SHORTCUTS)
                else:
                    merged = dict(DEFAULT_SHORTCUTS)
                    merged.update(self.settings['shortcuts'])
                    self.settings['shortcuts'] = merged

                # 兼容旧版本：若没有 language-independent 模式键，则根据旧的文本推断
                if 'timer_mode_key' not in self.settings:
                    self.settings['timer_mode_key'] = self.derive_mode_key(self.settings.get('timer_mode', ''))
                    # 立即保存，确保后续启动稳定
                    try:
                        self.save_settings(immediate=True)
                    except Exception:
                        pass
                
                # 兼容旧版本：将绝对路径转换为相对路径
                if "sound_file" in self.settings and self.settings["sound_file"]:
                    sound_file = self.settings["sound_file"]
                    # 如果是绝对路径，尝试转换为相对路径
                    if os.path.isabs(sound_file):
                        try:
                            rel_path = os.path.relpath(sound_file, self.base_path)
                            # 如果文件在 sounds 文件夹内，转换为相对路径
                            if rel_path.startswith('sounds') and os.path.exists(sound_file):
                                self.settings["sound_file"] = rel_path
                                # 立即保存转换后的设置
                                self.save_settings(immediate=True)
                                print(f"[兼容] 已将声音文件路径从绝对路径转换为相对路径: {rel_path}")
                        except (ValueError, OSError):
                            # 转换失败，保持原样
                            pass
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
        # 再次确保 shortcuts 完整
        try:
            merged = dict(DEFAULT_SHORTCUTS)
            merged.update(self.settings.get('shortcuts', {}))
            self.settings['shortcuts'] = merged
        except Exception:
            self.settings['shortcuts'] = dict(DEFAULT_SHORTCUTS)
        
        # 验证并修正设置
        self._validate_and_fix_settings()
            
    def _validate_and_fix_settings(self):
        """验证设置值的有效性,并修正无效的设置"""
        fixed = False
        
        # 验证字体大小
        font_size = self.settings.get("font_size", 96)
        if not isinstance(font_size, int) or font_size < 12 or font_size > 500:
            self.settings["font_size"] = 96
            fixed = True
            
        # 验证背景透明度
        bg_opacity = self.settings.get("bg_opacity", 200)
        if not isinstance(bg_opacity, int) or bg_opacity < 0 or bg_opacity > 255:
            self.settings["bg_opacity"] = 200
            fixed = True
            
        # 验证定时器模式键
        mode_key = self.settings.get("timer_mode_key")
        if mode_key not in ('countup', 'countdown', 'clock'):
            self.settings["timer_mode_key"] = 'countdown'
            fixed = True
            
        # 验证倒计时时间设置
        for key in ['countdown_hours', 'countdown_minutes', 'countdown_seconds']:
            value = self.settings.get(key, 0)
            if not isinstance(value, int) or value < 0:
                self.settings[key] = 0
                fixed = True
        
        # 验证倒计时小时和分钟的合理范围
        if self.settings.get("countdown_hours", 0) > 99:
            self.settings["countdown_hours"] = 99
            fixed = True
        if self.settings.get("countdown_minutes", 0) > 59:
            self.settings["countdown_minutes"] = 59
            fixed = True
        if self.settings.get("countdown_seconds", 0) > 59:
            self.settings["countdown_seconds"] = 59
            fixed = True
            
        # 验证颜色格式
        for color_key in ['text_color', 'bg_color']:
            color = self.settings.get(color_key, '#000000')
            if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
                default_colors = {'text_color': '#E0E0E0', 'bg_color': '#1E1E1E'}
                self.settings[color_key] = default_colors[color_key]
                fixed = True
                
        # 验证语言设置
        language = self.settings.get("language")
        if language not in ('zh_CN', 'en_US'):
            self.settings["language"] = 'zh_CN'
            fixed = True
            
        # 验证启动模式行为
        startup_behavior = self.settings.get("startup_mode_behavior")
        if startup_behavior not in ('restore', 'fixed'):
            self.settings["startup_mode_behavior"] = 'restore'
            fixed = True
            
        # 如果修正了任何设置,立即保存
        if fixed:
            print("[验证] 检测到无效的设置值,已自动修正")
            self.save_settings(immediate=True)
    
    def save_settings(self, immediate=False):
        """
        延迟保存设置（防抖动）
        
        Args:
            immediate: 是否立即保存，跳过延迟机制
        """
        if immediate:
            # 立即保存
            self._do_save_settings()
        else:
            # 标记有待保存的设置，并重启定时器
            self._pending_save = True
            self._save_timer.stop()  # 停止之前的定时器
            self._save_timer.start(self._save_delay_ms)  # 重新开始计时
    
    def _do_save_settings(self):
        """实际执行保存设置"""
        if not self._pending_save:
            return
            
        try:
            # 确保 settings 目录存在
            settings_dir = os.path.dirname(self.settings_file)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            self._pending_save = False
            print("[保存] 设置已保存")
        except Exception as e:
            print(f"[错误] 保存设置失败: {e}")
    
    def ensure_sounds_folder(self):
        """确保sounds文件夹存在，并随机选择铃声"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        
        sounds_dir = os.path.join(base_path, 'sounds')
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
        
        # 如果用户没有指定铃声文件，或文件不存在，随机选择一个
        current_sound = self.settings.get("sound_file", "")
        # 如果是相对路径，转换为绝对路径检查
        if current_sound and not os.path.isabs(current_sound):
            current_sound = os.path.join(base_path, current_sound)
        
        if not self.settings.get("sound_file", "") or not os.path.exists(current_sound):
            sound_files = self.get_sound_files()
            if sound_files:
                # 随机选择一个铃声文件，保存为相对路径
                selected_sound = random.choice(sound_files)
                rel_path = os.path.relpath(selected_sound, base_path)
                self.settings["sound_file"] = rel_path
                self.save_settings()
                print(f"随机选择铃声: {os.path.basename(selected_sound)}")
    
    def get_sound_files(self):
        """获取sounds文件夹中的所有音频文件"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        
        sounds_dir = os.path.join(base_path, 'sounds')
        if not os.path.exists(sounds_dir):
            return []
        
        # 支持的音频格式
        audio_extensions = ['.wav', '.mp3', '.ogg', '.m4a', '.flac']
        sound_files = []
        
        try:
            for file in os.listdir(sounds_dir):
                file_path = os.path.join(sounds_dir, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in audio_extensions:
                        sound_files.append(file_path)
        except Exception as e:
            print(f"读取sounds文件夹失败: {e}")
        
        return sound_files
            
    def play_sound(self, sound_file):
        """播放铃声（停止旧音效后播放新音效）"""
        try:
            # 停止当前播放的音效
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.stop()
            
            if os.path.exists(sound_file):
                url = QUrl.fromLocalFile(sound_file)
                content = QMediaContent(url)
                self.media_player.setMedia(content)
                self.media_player.setVolume(80)  # 设置音量为80%
                self.media_player.play()
            else:
                print(f"音效文件不存在: {sound_file}")
                QApplication.beep()
        except Exception as e:
            print(f"播放声音失败: {e}")
            QApplication.beep()
    
    def init_ui(self):
        """初始化主窗口"""
        # 设置窗口属性
        self.setWindowTitle(self.tr('app_name'))
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # 窗口置顶
            Qt.FramelessWindowHint |    # 无边框
            Qt.Tool                      # 工具窗口
        )
        self._stored_window_flags = self.windowFlags()
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        
        # 创建时间显示标签
        self.time_label = QLabel('00:00:00', self)
        self.time_label.setAlignment(Qt.AlignCenter)
        
        # 设置窗口大小和位置
        self.time_label.adjustSize()
        self.resize(self.time_label.size())
        
        # 将窗口居中显示
        self.center_on_screen()
        
        self.setCentralWidget(self.time_label)
        
        # 使窗口可拖动
        self.dragging = False
        self.offset = QPoint()
    
    def center_on_screen(self):
        """将窗口居中显示在屏幕上"""
        # 确保窗口已经有正确的尺寸
        self.adjustSize()
        
        # 获取屏幕几何信息
        screen = QApplication.primaryScreen().geometry()
        
        # 计算居中位置
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        
        # 移动窗口到居中位置
        self.move(max(0, x), max(0, y))
        
    def apply_settings(self, preserve_elapsed=False):
        """应用设置"""
        # 应用字体
        font = QFont(self.settings.get("font_family", "Consolas"), self.settings.get("font_size", 96), QFont.Bold)
        self.time_label.setFont(font)
        
        # 应用颜色和透明度
        text_color = self.settings["text_color"]
        bg_color = self.settings["bg_color"]
        bg_opacity = self.settings["bg_opacity"]
        
        # 夜读模式调整
        if self.settings["night_mode"]:
            # 降低亮度
            text_color = self.adjust_brightness(text_color, 0.6)
            bg_opacity = min(bg_opacity, 150)
        
        if self.is_fullscreen:
            bg_opacity = 255
        
        # 转换RGB
        bg_rgb = self.hex_to_rgb(bg_color)
        
        # 圆角半径
        corner_radius = self.settings.get("corner_radius", 15) if (self.settings.get("rounded_corners", True) and not self.is_fullscreen) else 0
        padding = "0px" if self.is_fullscreen else "30px 60px"
        
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: rgba({bg_rgb[0]}, {bg_rgb[1]}, {bg_rgb[2]}, {bg_opacity});
                border-radius: {corner_radius}px;
                padding: {padding};  /* �����ڱ߾࣬�ô��ڸ����� */
            }}
        """)
        
        # 重置计时器根据模式键（语言无关）
        mode_key = self.settings.get('timer_mode_key')
        if not mode_key:
            # 兜底：从旧文本推断
            mode_key = self.derive_mode_key(self.settings.get('timer_mode', ''))
            self.settings['timer_mode_key'] = mode_key
        print(f"[DEBUG] apply_settings: mode_key={mode_key}")
        if not preserve_elapsed:
            if mode_key == 'countdown':
                total_seconds = (self.settings.get("countdown_hours", 0) * 3600 + 
                                   self.settings.get("countdown_minutes", 25) * 60 + 
                                   self.settings.get("countdown_seconds", 0))
                self.elapsed_seconds = total_seconds
            else:
                # countup �� clock ���� 0 ��ʼ��ʾ��clock ģʽ��ʹ�� elapsed_seconds��
                self.elapsed_seconds = 0
            
        self.update_time()
        
        # 重新计算窗口大小并居中
        if not self.is_fullscreen:
            self.time_label.adjustSize()
            self.resize(self.time_label.size())
            self.center_on_screen()
        
        # 更新托盘图标
        self.update_tray_icon()
        
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def adjust_brightness(self, hex_color, factor):
        """调整颜色亮度"""
        rgb = self.hex_to_rgb(hex_color)
        adjusted = tuple(int(c * factor) for c in rgb)
        return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'
        
    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        
        self.tray_icon.setIcon(self.style().standardIcon(
            self.style().SP_MediaPlay
        ))
        
        # 创建托盘菜单
        self.create_tray_menu()
        
        self.tray_icon.show()
        
        # 双击托盘图标显示/隐藏窗口
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
    def build_quick_presets_menu(self):
        """������ͼ��/�Ҽ��˵��еĿ��ٹ���˵�"""
        preset_menu = QMenu(self.tr('quick_presets'), self)

        countup_action = QAction(self.tr('count_up_mode'), self)
        countup_action.triggered.connect(self.switch_to_count_up)
        preset_menu.addAction(countup_action)

        preset_menu.addSeparator()

        countdown_menu = QMenu(self.tr('countdown_mode'), self)
        countdown_presets = [
            (self.tr('pomodoro'), 0, 25, 0),
            (self.tr('short_break'), 0, 5, 0),
            (self.tr('long_break'), 0, 15, 0),
            ('30 ' + self.tr('minutes'), 0, 30, 0),
            ('1 ' + self.tr('hours'), 1, 0, 0),
        ]
        for name, h, m, s in countdown_presets:
            action = QAction(name, self)
            action.triggered.connect(lambda _, hours=h, mins=m, secs=s:
                                     self.quick_countdown(hours, mins, secs))
            countdown_menu.addAction(action)
        preset_menu.addMenu(countdown_menu)

        preset_menu.addSeparator()

        clock_action = QAction(self.tr('clock_mode'), self)
        clock_action.triggered.connect(self.switch_to_clock_mode)
        preset_menu.addAction(clock_action)

        return preset_menu
        
    def create_tray_menu(self):
        """创建托盘菜单"""
        tray_menu = QMenu()
        
        # 开始/暂停动作
        self.pause_action = QAction(self.tr('pause'), self)
        self.pause_action.triggered.connect(self.toggle_pause)
        tray_menu.addAction(self.pause_action)
        
        # 重置动作
        reset_action = QAction(self.tr('reset'), self)
        reset_action.triggered.connect(self.reset_timer)
        tray_menu.addAction(reset_action)
        
        tray_menu.addSeparator()
        tray_menu.addMenu(self.build_quick_presets_menu())
        
        tray_menu.addSeparator()
        
        # 设置动作
        settings_action = QAction(self.tr('settings'), self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        # 显示/隐藏动作
        toggle_action = QAction(self.tr('show_hide'), self)
        toggle_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(toggle_action)

        fullscreen_text = self.tr('exit_fullscreen') if self.is_fullscreen else self.tr('enter_fullscreen')
        fullscreen_action = QAction(fullscreen_text, self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        tray_menu.addAction(fullscreen_action)
        
        tray_menu.addSeparator()
        
        # 锁定/解锁动作
        lock_text = self.tr('unlock_window') if self.is_locked else self.tr('lock_window')
        lock_action = QAction(lock_text, self)
        lock_action.triggered.connect(self.toggle_lock)
        tray_menu.addAction(lock_action)
        
        tray_menu.addSeparator()
        
        # 退出动作
        quit_action = QAction(self.tr('quit'), self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
    def init_timer(self):
        """初始化定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(TimerConstants.TIMER_UPDATE_INTERVAL)  # 每秒更新一次
        
        # 闪烁定时器
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.flash_window)
        
    def init_shortcuts(self):
        """初始化快捷键（根据设置绑定）"""
        self._shortcut_objs = []
        self._bind_shortcuts()

    def _clear_shortcuts(self):
        objs = getattr(self, '_shortcut_objs', [])
        for obj in objs:
            try:
                obj.setParent(None)
            except Exception:
                pass
        self._shortcut_objs = []

    def _bind_shortcuts(self):
        self._clear_shortcuts()
        sc = self.settings.get('shortcuts', {})
        mapping = [
            (sc.get('pause_resume', DEFAULT_SHORTCUTS['pause_resume']), self.toggle_pause),
            (sc.get('reset', DEFAULT_SHORTCUTS['reset']), self.reset_timer),
            (sc.get('show_hide', DEFAULT_SHORTCUTS['show_hide']), self.toggle_visibility),
            (sc.get('open_settings', DEFAULT_SHORTCUTS['open_settings']), self.show_settings),
            (sc.get('lock_unlock', DEFAULT_SHORTCUTS['lock_unlock']), self.toggle_lock),
            (sc.get('toggle_fullscreen', DEFAULT_SHORTCUTS['toggle_fullscreen']), self.toggle_fullscreen),
        ]
        for seq_str, handler in mapping:
            try:
                if seq_str:
                    obj = QShortcut(QKeySequence(seq_str), self, handler)
                    self._shortcut_objs.append(obj)
            except Exception as _e:
                print(f"[shortcuts] 绑定失败: {seq_str}: {_e}")

    def reload_shortcuts(self):
        """根据当前 settings 重新绑定快捷键（用于设置更改后）"""
        # 合并默认，防止缺失
        merged = dict(DEFAULT_SHORTCUTS)
        try:
            merged.update(self.settings.get('shortcuts', {}))
        except Exception:
            pass
        self.settings['shortcuts'] = merged
        # 重绑
        self._bind_shortcuts()
        
    def update_time(self):
        """更新时间显示"""
        # 使用 language-independent 模式键
        mode_key = self.settings.get('timer_mode_key')
        if not mode_key:
            mode_key = self.derive_mode_key(self.settings.get('timer_mode', ''))
            self.settings['timer_mode_key'] = mode_key
        
        # 时钟模式
        # 调试首帧输出当前模式
        if not hasattr(self, '_dbg_printed'):
            print(f"[DEBUG] update_time: mode_key={mode_key}")
            self._dbg_printed = True
        if mode_key == 'clock':
            from PyQt5.QtCore import QDateTime
            current_time = QDateTime.currentDateTime()
            
            # 根据设置构建时间格式
            if self.settings.get("clock_show_date", False):
                # 显示日期
                if self.settings.get("clock_format_24h", True):
                    # 24小时制带日期
                    if self.settings.get("clock_show_seconds", True):
                        time_str = current_time.toString("yyyy-MM-dd HH:mm:ss")
                    else:
                        time_str = current_time.toString("yyyy-MM-dd HH:mm")
                else:
                    # 12小时制带日期：指示符应贴近时间，不要出现在日期前
                    date_part = current_time.toString("yyyy-MM-dd")
                    time_part = current_time.toString("hh:mm:ss") if self.settings.get("clock_show_seconds", True) else current_time.toString("hh:mm")
                    if self.settings.get("clock_show_am_pm", True):
                        ampm_style = self.settings.get("clock_am_pm_style", "zh")
                        # 使用 hour() 判断，更可靠
                        hour = current_time.time().hour()
                        is_pm = hour >= 12
                        indicator = ('PM' if is_pm else 'AM') if ampm_style == 'en' else ('下午' if is_pm else '上午')
                        pos = self.settings.get("clock_am_pm_position", "before")
                        time_with_indicator = f"{indicator} {time_part}" if pos == 'before' else f"{time_part} {indicator}"
                    else:
                        time_with_indicator = time_part
                    time_str = f"{date_part} {time_with_indicator}"
            else:
                # 不显示日期
                if self.settings.get("clock_format_24h", True):
                    # 24小时制
                    if self.settings.get("clock_show_seconds", True):
                        time_str = current_time.toString("HH:mm:ss")
                    else:
                        time_str = current_time.toString("HH:mm")
                else:
                    # 12小时制
                    if self.settings.get("clock_show_seconds", True):
                        base = current_time.toString("hh:mm:ss")
                    else:
                        base = current_time.toString("hh:mm")
                    # 是否显示 AM/PM 指示
                    if self.settings.get("clock_show_am_pm", True):
                        ampm_style = self.settings.get("clock_am_pm_style", "zh")
                        # 使用 hour() 判断，更可靠
                        hour = current_time.time().hour()
                        is_pm = hour >= 12
                        indicator = ('PM' if is_pm else 'AM') if ampm_style == 'en' else ('下午' if is_pm else '上午')
                        pos = self.settings.get("clock_am_pm_position", "before")
                        time_str = f"{indicator} {base}" if pos == 'before' else f"{base} {indicator}"
                    else:
                        time_str = base
            
            self.time_label.setText(time_str)
            
        # 计时器模式
        else:
            if self.is_running:
                if mode_key == 'countdown':
                    self.elapsed_seconds -= 1
                    if self.elapsed_seconds <= 0:
                        self.elapsed_seconds = 0
                        self.is_running = False
                        self.on_countdown_finished()
                else:
                    self.elapsed_seconds += 1
                
            hours = abs(self.elapsed_seconds) // 3600
            minutes = (abs(self.elapsed_seconds) % 3600) // 60
            seconds = abs(self.elapsed_seconds) % 60
            
            time_str = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
            self.time_label.setText(time_str)
        
        # 只在文本内容改变时才调整窗口大小
        current_text = self.time_label.text()
        if current_text != self.last_displayed_text and not self.is_fullscreen:
            self.last_displayed_text = current_text
            self.time_label.adjustSize()
            self.resize(self.time_label.size())
        
    def on_countdown_finished(self):
        """倒计时结束处理"""
        action = self.settings["countdown_action"]
        
        # 播放铃声
        if self.settings.get("enable_sound", True):
            sound_file = self.settings.get("sound_file", "")
            if sound_file:
                # 如果是相对路径，转换为绝对路径
                if not os.path.isabs(sound_file):
                    if getattr(sys, 'frozen', False):
                        base_path = os.path.dirname(sys.executable)
                    else:
                        base_path = os.path.dirname(__file__)
                    sound_file = os.path.join(base_path, sound_file)
                
                if os.path.exists(sound_file):
                    self.play_sound(sound_file)
                else:
                    # 如果文件不存在，播放系统提示音
                    if self.tr('beep') in action or '提示音' in action:
                        QApplication.beep()
            else:
                # 如果没有自定义铃声，播放系统提示音
                if self.tr('beep') in action or '提示音' in action:
                    QApplication.beep()
        
        # 闪烁提醒
        if self.tr('flash') in action or '闪烁' in action:
            # 开始闪烁
            self.is_flashing = True
            self.flash_count = 0
            self.flash_timer.start(TimerConstants.FLASH_INTERVAL)
        
        # 弹窗提示
        if self.settings.get("enable_popup", True):
            # 创建自定义弹窗
            msg = QMessageBox(self)
            msg.setWindowTitle(self.tr('countdown_finished'))
            msg.setText(self.tr('countdown_finished_msg'))
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            
            # 确保窗口可见
            if not self.isVisible():
                self.show()
            
            # 显示弹窗
            msg.exec_()
        else:
            # 如果不使用弹窗，显示托盘通知
            self.tray_icon.showMessage(
                self.tr('countdown_finished'),
                self.tr('countdown_finished_msg'),
                QSystemTrayIcon.Information,
                TimerConstants.NOTIFICATION_DURATION_SHORT * 1000
            )
            
            # 确保窗口可见
            if not self.isVisible():
                self.show()
        
        # Windows原生通知
        if toaster:
            try:
                toaster.show_toast(
                    "DesktopTimer",  # 通知标题
                    self.tr('countdown_finished') + "\n" + self.tr('countdown_finished_msg'),
                    duration=TimerConstants.NOTIFICATION_DURATION_LONG,
                    threaded=True
                )
            except Exception as e:
                print(f"Windows通知失败: {e}")
        
        try:
            self.update_tray_icon()
        except Exception:
            pass
    
    def flash_window(self):
        """闪烁窗口"""
        if self.is_flashing:
            current_color = self.time_label.styleSheet()
            if 'color: red' in current_color:
                self.apply_settings()
            else:
                # 临时改为红色
                bg_rgb = self.hex_to_rgb(self.settings["bg_color"])
                bg_opacity = self.settings["bg_opacity"]
                corner_radius = self.settings.get("corner_radius", 15) if self.settings.get("rounded_corners", True) else 0
                self.time_label.setStyleSheet(f"""
                    QLabel {{
                        color: red;
                        background-color: rgba({bg_rgb[0]}, {bg_rgb[1]}, {bg_rgb[2]}, {bg_opacity});
                        border-radius: {corner_radius}px;
                        padding: 20px 40px;
                    }}
                """)
            # 停止闪烁(只闪3次)
            self.flash_count += 1
            if self.flash_count >= TimerConstants.FLASH_COUNT_MAX:  # 3次闪烁 = 6次状态切换
                self.is_flashing = False
                self.flash_count = 0
                self.update_tray_icon()  # 闪烁结束后更新托盘图标
        else:
            self.flash_timer.stop()
            self.apply_settings()
            
    def toggle_pause(self):
        """切换暂停/继续"""
        self.is_running = not self.is_running
        if self.is_running:
            self.pause_action.setText(self.tr('pause'))
            self.tray_icon.showMessage(
                self.tr('app_name'),
                self.tr('timer_continued'),
                QSystemTrayIcon.Information,
                TimerConstants.TRAY_MESSAGE_DURATION
            )
        else:
            self.pause_action.setText(self.tr('continue'))
            self.tray_icon.showMessage(
                self.tr('app_name'),
                self.tr('timer_paused'),
                QSystemTrayIcon.Information,
                TimerConstants.TRAY_MESSAGE_DURATION
            )
        
        try:
            self.update_tray_icon()
        except Exception:
            pass
    
    def reset_timer(self):
        """重置计时：倒计时回到初始设置，正计时归零"""
        mode_key = self.settings.get('timer_mode_key')
        if not mode_key:
            mode_key = self.derive_mode_key(self.settings.get('timer_mode', ''))
            self.settings['timer_mode_key'] = mode_key
        if mode_key == 'countdown':
            hours = self.settings.get("countdown_hours", 0)
            minutes = self.settings.get("countdown_minutes", 0)
            seconds = self.settings.get("countdown_seconds", 0)
            self.elapsed_seconds = hours * 3600 + minutes * 60 + seconds
        else:
            self.elapsed_seconds = 0
        self.is_running = False
        self.update_time()
        self.tray_icon.showMessage(
            self.tr('app_name'),
            self.tr('timer_reset'),
            QSystemTrayIcon.Information,
            TimerConstants.TRAY_MESSAGE_DURATION
        )
        
        try:
            self.update_tray_icon()
        except Exception:
            pass
    
    def quick_countdown(self, hours, minutes, seconds):
        """快速设置倒计时"""
        self.settings["timer_mode"] = self.tr('countdown_mode')
        self.settings["timer_mode_key"] = 'countdown'
        self.settings["countdown_hours"] = hours
        self.settings["countdown_minutes"] = minutes
        self.settings["countdown_seconds"] = seconds
        self.save_settings()
        self.reset_timer()
        self.tray_icon.showMessage(
            self.tr('countdown_set'),
            f'{hours} {self.tr("hours")} {minutes} {self.tr("minutes")} {seconds} {self.tr("seconds")}',
            QSystemTrayIcon.Information,
            1000
        )
        
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 重新创建托盘菜单以更新语言
            self.create_tray_menu()
            
    def toggle_visibility(self):
        """切换窗口显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            if self.is_fullscreen:
                self.showFullScreen()
            else:
                self.show()
            self.activateWindow()

    def toggle_fullscreen(self):
        """�л�ȫ��/�˳�ȫ��"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        """����ȫ��ģʽ"""
        if self.is_fullscreen:
            return
        self.is_fullscreen = True
        try:
            self._stored_geometry = self.geometry()
        except Exception:
            self._stored_geometry = None
        self._stored_window_flags = self.windowFlags()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.apply_settings(preserve_elapsed=True)
        self.create_tray_menu()
        try:
            self.update_tray_icon()
        except Exception:
            pass

    def exit_fullscreen(self):
        """�˳�ȫ��ģʽ"""
        if not self.is_fullscreen:
            return
        self.is_fullscreen = False
        restore_flags = self._stored_window_flags or (Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setWindowFlags(restore_flags)
        self.showNormal()
        if self._stored_geometry:
            self.setGeometry(self._stored_geometry)
        else:
            self.center_on_screen()
        self.apply_settings(preserve_elapsed=True)
        self.create_tray_menu()
        try:
            self.update_tray_icon()
        except Exception:
            pass
            
    def tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()
    
    def toggle_lock(self):
        """切换窗口锁定状态"""
        self.is_locked = not self.is_locked
        
        if self.is_locked:
            # 锁定：只设置鼠标事件穿透，保留键盘事件以便快捷键仍然有效
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.tray_icon.showMessage(
                self.tr('app_name'),
                self.tr('window_locked'),
                QSystemTrayIcon.Information,
                1000
            )
            # Windows原生通知 - 锁定
            if toaster:
                try:
                    toaster.show_toast(
                        "DesktopTimer",
                        self.tr('window_locked'),
                        duration=TimerConstants.NOTIFICATION_DURATION_SHORT,
                        threaded=True
                    )
                except Exception as e:
                    print(f"Windows通知失败: {e}")
        else:
            # 解锁：恢复窗口交互
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            
            # Windows原生通知 - 解锁
            if toaster:
                try:
                    toaster.show_toast(
                        "DesktopTimer",
                        self.tr('window_unlocked'),
                        duration=TimerConstants.NOTIFICATION_DURATION_SHORT,
                        threaded=True
                    )
                except Exception as e:
                    print(f"Windows通知失败: {e}")
            else:
                # 如果没有 Windows 通知，使用托盘通知
                self.tray_icon.showMessage(
                    self.tr('app_name'),
                    self.tr('window_unlocked'),
                    QSystemTrayIcon.Information,
                    2000
                )
        
        # 更新托盘菜单以反映锁定状态
        self.create_tray_menu()
            
    def quit_app(self):
        """退出应用 - 清理所有资源"""
        try:
            # 停止所有定时器
            if hasattr(self, 'timer') and self.timer:
                self.timer.stop()
                self.timer.deleteLater()
            
            if hasattr(self, 'flash_timer') and self.flash_timer:
                self.flash_timer.stop()
                self.flash_timer.deleteLater()
            
            # 停止并清理媒体播放器
            if hasattr(self, 'media_player') and self.media_player:
                if self.media_player.state() == QMediaPlayer.PlayingState:
                    self.media_player.stop()
                self.media_player.deleteLater()
            
            # 保存设置（立即保存，不延迟）
            self.save_settings(immediate=True)
            
            # 隐藏托盘图标
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
        except Exception as e:
            print(f"[错误] 清理资源失败: {e}")
        finally:
            QApplication.quit()
        
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.LeftButton and not self.is_locked and not self.is_fullscreen:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于拖动窗口"""
        if self.dragging and not self.is_locked and not self.is_fullscreen:
            self.move(event.globalPos() - self.offset)
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 停止拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        menu = QMenu(self)
        
        # 暂停/继续
        pause_action = QAction(self.tr('pause') if self.is_running else self.tr('continue'), self)
        pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(pause_action)
        
        # 重置
        reset_action = QAction(self.tr('reset'), self)
        reset_action.triggered.connect(self.reset_timer)
        menu.addAction(reset_action)
        
        menu.addSeparator()
        menu.addMenu(self.build_quick_presets_menu())
        menu.addSeparator()
        
        # 锁定/解锁窗口
        lock_text = self.tr('unlock_window') if self.is_locked else self.tr('lock_window')
        lock_action = QAction(lock_text, self)
        lock_action.triggered.connect(self.toggle_lock)
        menu.addAction(lock_action)
        
        menu.addSeparator()
        
        # 设置
        settings_action = QAction(self.tr('settings'), self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # 显示/隐藏
        hide_action = QAction(self.tr('show_hide'), self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)

        fullscreen_text = self.tr('exit_fullscreen') if self.is_fullscreen else self.tr('enter_fullscreen')
        fullscreen_action = QAction(fullscreen_text, self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        menu.addAction(fullscreen_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction(self.tr('quit'), self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())
        
    def switch_to_count_up(self):
        """切换到正计时"""
        self.settings["timer_mode"] = self.tr('count_up_mode')
        self.settings["timer_mode_key"] = 'countup'
        self.save_settings()
        self.reset_timer()

    def switch_to_clock_mode(self):
        """�л���ʱ��ģʽ"""
        self.settings["timer_mode"] = self.tr('clock_mode')
        self.settings["timer_mode_key"] = "clock"
        self.save_settings()
        self.reset_timer()
            
    def closeEvent(self, event):
        """关闭事件 - 最小化到托盘而不是退出"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            self.tr('app_name'),
            self.tr('minimized_to_tray'),
            QSystemTrayIcon.Information,
            TimerConstants.TRAY_MESSAGE_DURATION
        )
        
    def update_tray_icon(self):
        """根据当前状态更新托盘图标（Qt标准图标）"""
        try:
            tray = getattr(self, 'tray_icon', None)
            if tray is None:
                return
            style = self.style()
            # 优先：在倒计时完成的闪烁阶段，显示信息图标
            if getattr(self, 'is_flashing', False):
                icon = style.standardIcon(QStyle.SP_MessageBoxInformation)
            else:
                if getattr(self, 'is_running', False):
                    icon = style.standardIcon(QStyle.SP_MediaPlay)
                else:
                    # 未运行，区分是否已归零
                    if getattr(self, 'elapsed_seconds', 0) == 0:
                        icon = style.standardIcon(QStyle.SP_MediaStop)
                    else:
                        icon = style.standardIcon(QStyle.SP_MediaPause)
            tray.setIcon(icon)
        except Exception as e:
            print(f"更新托盘图标失败: {e}")

    def showEvent(self, event):
        """窗口显示时更新托盘图标"""
        super().showEvent(event)
        self.update_tray_icon()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序
    
    # 设置Qt的中文翻译
    translator = QTranslator()
    # 尝试加载Qt自带的中文翻译
    if translator.load("qt_zh_CN", QApplication.applicationDirPath()):
        app.installTranslator(translator)
    elif translator.load("qtbase_zh_CN"):
        app.installTranslator(translator)
    
    # 设置应用程序区域为中文
    QLocale.setDefault(QLocale(QLocale.Chinese, QLocale.China))
    
    window = TimerWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
