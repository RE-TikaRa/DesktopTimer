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
                             QListWidget, QStyle, QScrollArea)
from PyQt5.QtGui import QIcon

# 自定义可点击标签类
class ClickableLabel(QLabel):
    def __init__(self, text, url, parent=None):
        super().__init__(text, parent)
        self.url = url
        self.parent_dialog = parent
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.parent_dialog:
            self.parent_dialog.open_link(self.url)
from PyQt5.QtCore import QTimer, Qt, QPoint, QUrl, QTranslator, QLocale
from PyQt5.QtGui import QFont, QIcon, QColor, QKeySequence, QDesktopServices, QPixmap
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
        _p = _os_i18n.path.join(_os_i18n.path.dirname(__file__), 'lang', f'{_code}.json')
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


class L18n:
    def __init__(self, lang_code='zh_CN'):
        self.lang_code = lang_code
        self.translations = {}
        self.load(lang_code)
        
    def load(self, lang_code):
        lang_path = os.path.join(os.path.dirname(__file__), 'lang', f'{lang_code}.json')
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
        icon_path = os.path.join(os.path.dirname(__file__), "img", "timer_icon.ico")
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
        font_label = QLabel(f'{self.tr("current_font")}: {self.parent_window.settings["font_family"]}, {self.tr("font_size")}: {self.parent_window.settings["font_size"]}')
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
        self.update_color_button(self.text_color_btn, self.parent_window.settings["text_color"])
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
        self.update_color_button(self.bg_color_btn, self.parent_window.settings["bg_color"])
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
        self.opacity_slider.setValue(self.parent_window.settings["bg_opacity"])
        self.opacity_value_label = QLabel(f'{self.parent_window.settings["bg_opacity"]}')
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
        size_layout = QHBoxLayout()
        size_label = QLabel(self.tr('window_size') + ':')
        self.size_combo = QComboBox()
        self.size_combo.addItems([
            self.tr('size_small'),    # 小
            self.tr('size_medium'),   # 中
            self.tr('size_large'),    # 大
            self.tr('size_extra_large') # 超大
        ])
        # 根据当前字体大小设置默认选项
        current_size = self.parent_window.settings.get("font_size", 72)
        if current_size <= 60:
            self.size_combo.setCurrentIndex(0)  # 小
        elif current_size <= 80:
            self.size_combo.setCurrentIndex(1)  # 中
        elif current_size <= 100:
            self.size_combo.setCurrentIndex(2)  # 大
        else:
            self.size_combo.setCurrentIndex(3)  # 超大
            
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        size_layout.addStretch()
        style_layout.addLayout(size_layout)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # 夜读模式
        night_group = QGroupBox(self.tr('night_mode'))
        night_layout = QVBoxLayout()
        
        self.night_mode_check = QCheckBox(self.tr('night_mode_desc'))
        self.night_mode_check.setChecked(self.parent_window.settings["night_mode"])
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
        self.mode_combo.addItems([self.tr('count_up_mode'), self.tr('countdown_mode')])
        current_mode = self.parent_window.settings["timer_mode"]
        self.mode_combo.setCurrentText(current_mode)
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
        self.hours_spin.setValue(self.parent_window.settings["countdown_hours"])
        
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setSuffix(' ' + self.tr('minutes'))
        self.minutes_spin.setValue(self.parent_window.settings["countdown_minutes"])
        
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setSuffix(' ' + self.tr('seconds'))
        self.seconds_spin.setValue(self.parent_window.settings["countdown_seconds"])
        
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
        current_action = self.parent_window.settings["countdown_action"]
        for i in range(self.countdown_action.count()):
            if self.countdown_action.itemText(i) in current_action or current_action in self.countdown_action.itemText(i):
                self.countdown_action.setCurrentIndex(i)
                break
        action_layout.addWidget(self.countdown_action)
        action_layout.addStretch()
        countdown_layout.addLayout(action_layout)
        
        self.countdown_widget.setLayout(countdown_layout)
        mode_layout.addWidget(self.countdown_widget)
        
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
                btn.clicked.connect(lambda checked, h=hours, m=minutes, s=seconds: 
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
        random_btn = QPushButton('🎲 随机' if self.tr('quit') == '退出' else '🎲 Random')
        random_btn.clicked.connect(self.random_sound)
        folder_layout.addWidget(folder_btn)
        folder_layout.addWidget(test_btn)
        folder_layout.addWidget(random_btn)
        folder_layout.addStretch()
        sound_layout.addLayout(folder_layout)
        
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        # 快捷键设置
        shortcut_group = QGroupBox(self.tr('shortcuts'))
        shortcut_layout = QVBoxLayout()
        
        shortcuts_info = [
            (self.tr('shortcut_pause'), 'Ctrl+Space'),
            (self.tr('shortcut_reset'), 'Ctrl+R'),
            (self.tr('shortcut_hide'), 'Ctrl+H'),
            (self.tr('shortcut_settings'), 'Ctrl+,'),
        ]
        
        for label, key in shortcuts_info:
            info_layout = QHBoxLayout()
            info_layout.addWidget(QLabel(label + ':'))
            key_label = QLabel(key)
            key_label.setStyleSheet('QLabel { background-color: #f0f0f0; padding: 5px; border-radius: 3px; font-family: Consolas; }')
            info_layout.addWidget(key_label)
            info_layout.addStretch()
            shortcut_layout.addLayout(info_layout)
        
        shortcut_group.setLayout(shortcut_layout)
        layout.addWidget(shortcut_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
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
        logo_path = os.path.join(os.path.dirname(__file__), "img", "ALP_STUDIO-logo-full.svg")
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
            ("版本号", "1.0.0", None),
            ("作者", "TikaRa", None),
            ("邮箱", "163mail@re-TikaRa.fun", "mailto:163mail@re-TikaRa.fun"),
            ("个人网站", "re-tikara.fun", "https://re-tikara.fun"),
            ("代码仓库", "https://github.com/RE-TikaRa/DesktopTimer", "https://github.com/RE-TikaRa/DesktopTimer"),
            ("B站主页", "夜雨安歌_TikaRa", "https://space.bilibili.com/374412219")
        ]
        
        for label_text, value_text, link_url in info_items:
            item_layout = QHBoxLayout()
            
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #34495e;
                    min-width: 80px;
                    background: transparent;
                }
            """)
            
            # 如果有链接，使用可点击标签
            if link_url:
                value = ClickableLabel(value_text, link_url, self)
                value.setStyleSheet("""
                    QLabel {
                        color: #3498db;
                        background: transparent;
                    }
                    QLabel:hover {
                        color: #2980b9;
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
        
    def open_link(self, url):
        """打开链接"""
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开链接: {str(e)}")
        
    def on_mode_changed(self, mode):
        """模式改变时的处理"""
        self.countdown_widget.setVisible(self.tr('countdown_mode') in mode or '倒计时' in mode)
        
    def choose_font(self):
        """选择字体"""
        current_font = QFont(self.parent_window.settings["font_family"], 
                           self.parent_window.settings["font_size"])
        
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
        color = QColorDialog.getColor(QColor(self.parent_window.settings["text_color"]), self)
        if color.isValid():
            self.parent_window.settings["text_color"] = color.name()
            self.update_color_button(self.text_color_btn, color.name())
            
    def choose_bg_color(self):
        """选择背景颜色"""
        color = QColorDialog.getColor(QColor(self.parent_window.settings["bg_color"]), self)
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
        sound_dir = os.path.join(os.getcwd(), 'sounds')
        if not os.path.exists(sound_dir):
            sound_dir = os.getcwd()
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('choose_sound'),
            sound_dir,
            "Sound Files (*.wav *.mp3 *.ogg);;All Files (*.*)"
        )
        
        if file_path:
            self.parent_window.settings["sound_file"] = file_path
            self.sound_file_label.setText(os.path.basename(file_path))
            
    def open_sound_folder(self):
        """打开铃声文件夹"""
        sound_dir = os.path.join(os.getcwd(), 'sounds')
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
        if sound_file and os.path.exists(sound_file):
            self.parent_window.play_sound(sound_file)
        else:
            QApplication.beep()
    
    def random_sound(self):
        """随机选择铃声"""
        sound_files = self.parent_window.get_sound_files()
        if sound_files:
            selected_sound = random.choice(sound_files)
            self.parent_window.settings["sound_file"] = selected_sound
            self.sound_file_label.setText(os.path.basename(selected_sound))
            # 播放选中的铃声
            self.parent_window.play_sound(selected_sound)
        else:
            QMessageBox.warning(
                self,
                self.tr('no_sound_files_found'),
                self.tr('no_sound_files_msg')
            )
        
    def apply_settings(self):
        """应用设置"""
        self.parent_window.settings["bg_opacity"] = self.opacity_slider.value()
        self.parent_window.settings["night_mode"] = self.night_mode_check.isChecked()
        self.parent_window.settings["timer_mode"] = self.mode_combo.currentText()
        self.parent_window.settings["countdown_hours"] = self.hours_spin.value()
        self.parent_window.settings["countdown_minutes"] = self.minutes_spin.value()
        self.parent_window.settings["countdown_seconds"] = self.seconds_spin.value()
        self.parent_window.settings["countdown_action"] = self.countdown_action.currentText()
        self.parent_window.settings["language"] = "zh_CN" if self.lang_combo.currentText() == "简体中文" else "en_US"
        self.parent_window.settings["auto_start_timer"] = self.auto_start_check.isChecked()
        self.parent_window.settings["rounded_corners"] = self.rounded_check.isChecked()
        self.parent_window.settings["corner_radius"] = self.radius_spin.value()
        self.parent_window.settings["enable_sound"] = self.enable_sound_check.isChecked()
        self.parent_window.settings["enable_popup"] = self.enable_popup_check.isChecked()
        
        # 应用窗口大小设置
        size_text = self.size_combo.currentText()
        if self.tr('size_small') in size_text or '小' in size_text:
            self.parent_window.settings["font_size"] = 60
        elif self.tr('size_medium') in size_text or '中' in size_text:
            self.parent_window.settings["font_size"] = 72
        elif self.tr('size_large') in size_text or '大' in size_text:
            self.parent_window.settings["font_size"] = 96
        elif self.tr('size_extra_large') in size_text or '超大' in size_text:
            self.parent_window.settings["font_size"] = 120
        
        self.parent_window.apply_settings()
        self.parent_window.save_settings()
        
    def accept_settings(self):
        """确定设置"""
        self.apply_settings()
        self.accept()


class TimerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.l18n = L18n(lang_code=self.get_language())
        self.load_settings()
        self.elapsed_seconds = 0
        self.is_running = self.settings.get("auto_start_timer", False)
        self.is_flashing = False
        self.media_player = QMediaPlayer()
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "img", "timer_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.init_ui()
        self.init_tray()
        self.init_timer()
        self.init_shortcuts()
        self.apply_settings()
        self.ensure_sounds_folder()
        
    def get_language(self):
        # 从设置获取语言代码
        try:
            settings_path = os.path.join(os.path.dirname(__file__), "settings", "timer_settings.json")
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings.get('language', 'zh_CN')
        except Exception:
            return 'zh_CN'
        
    def tr(self, key):
        return self.l18n.tr(key)
        
    def load_settings(self):
        """加载设置"""
        self.settings_file = os.path.join(os.path.dirname(__file__), "settings", "timer_settings.json")
        default_settings = {
            "font_family": "Consolas",
            "font_size": 96,  # 增加字体大小，窗口会更大
            "text_color": "#E0E0E0",
            "bg_color": "#1E1E1E",
            "bg_opacity": 200,
            "night_mode": False,
            "timer_mode": "正计时",
            "countdown_hours": 0,
            "countdown_minutes": 25,
            "countdown_seconds": 0,
            "countdown_action": "提示音+闪烁",
            "language": "zh_CN",
            "auto_start_timer": False,
            "rounded_corners": True,
            "corner_radius": 15,
            "enable_sound": True,
            "enable_popup": True,
            "sound_file": ""
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                # 确保所有键都存在
                for key, value in default_settings.items():
                    if key not in self.settings:
                        self.settings[key] = value
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
            
    def save_settings(self):
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def ensure_sounds_folder(self):
        """确保sounds文件夹存在，并随机选择铃声"""
        sounds_dir = os.path.join(os.getcwd(), 'sounds')
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
        
        # 如果用户没有指定铃声文件，随机选择一个
        if not self.settings.get("sound_file", "") or not os.path.exists(self.settings.get("sound_file", "")):
            sound_files = self.get_sound_files()
            if sound_files:
                # 随机选择一个铃声文件
                selected_sound = random.choice(sound_files)
                self.settings["sound_file"] = selected_sound
                self.save_settings()
                print(f"随机选择铃声: {os.path.basename(selected_sound)}")
    
    def get_sound_files(self):
        """获取sounds文件夹中的所有音频文件"""
        sounds_dir = os.path.join(os.getcwd(), 'sounds')
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
        """播放铃声"""
        try:
            if os.path.exists(sound_file):
                url = QUrl.fromLocalFile(sound_file)
                content = QMediaContent(url)
                self.media_player.setMedia(content)
                self.media_player.setVolume(80)  # 设置音量为80%
                self.media_player.play()
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
        
    def apply_settings(self):
        """应用设置"""
        # 应用字体
        font = QFont(self.settings["font_family"], self.settings["font_size"], QFont.Bold)
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
        
        # 转换RGB
        bg_rgb = self.hex_to_rgb(bg_color)
        
        # 圆角半径
        corner_radius = self.settings.get("corner_radius", 15) if self.settings.get("rounded_corners", True) else 0
        
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: rgba({bg_rgb[0]}, {bg_rgb[1]}, {bg_rgb[2]}, {bg_opacity});
                border-radius: {corner_radius}px;
                padding: 30px 60px;  /* 增加内边距，让窗口更宽敞 */
            }}
        """)
        
        # 重置计时器根据模式
        mode = self.settings["timer_mode"]
        if self.tr('countdown_mode') in mode or '倒计时' in mode:
            total_seconds = (self.settings["countdown_hours"] * 3600 + 
                           self.settings["countdown_minutes"] * 60 + 
                           self.settings["countdown_seconds"])
            self.elapsed_seconds = total_seconds
        else:
            self.elapsed_seconds = 0
            
        self.update_time()
        
        # 重新计算窗口大小并居中
        self.time_label.adjustSize()
        self.resize(self.time_label.size())
        self.center_on_screen()
        
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
        
        # 快捷预设菜单
        preset_menu = QMenu(self.tr('quick_presets'), self)
        
        presets = [
            (self.tr('pomodoro'), 0, 25, 0),
            (self.tr('short_break'), 0, 5, 0),
            (self.tr('long_break'), 0, 15, 0),
            ('30 ' + self.tr('minutes'), 0, 30, 0),
            ('1 ' + self.tr('hours'), 1, 0, 0),
        ]
        
        for name, h, m, s in presets:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, hours=h, mins=m, secs=s: 
                                    self.quick_countdown(hours, mins, secs))
            preset_menu.addAction(action)
            
        tray_menu.addMenu(preset_menu)
        
        tray_menu.addSeparator()
        
        # 设置动作
        settings_action = QAction(self.tr('settings'), self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        # 显示/隐藏动作
        toggle_action = QAction(self.tr('show_hide'), self)
        toggle_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(toggle_action)
        
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
        self.timer.start(1000)  # 每秒更新一次
        
        # 闪烁定时器
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.flash_window)
        
    def init_shortcuts(self):
        """初始化快捷键"""
        # Ctrl+Space: 暂停/继续
        QShortcut(QKeySequence('Ctrl+Space'), self, self.toggle_pause)
        
        # Ctrl+R: 重置
        QShortcut(QKeySequence('Ctrl+R'), self, self.reset_timer)
        
        # Ctrl+H: 显示/隐藏
        QShortcut(QKeySequence('Ctrl+H'), self, self.toggle_visibility)
        
        # Ctrl+,: 设置
        QShortcut(QKeySequence('Ctrl+,'), self, self.show_settings)
        
    def update_time(self):
        """更新时间显示"""
        if self.is_running:
            mode = self.settings["timer_mode"]
            if self.tr('countdown_mode') in mode or '倒计时' in mode:
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
        
        # 调整窗口大小以适应文本
        self.time_label.adjustSize()
        self.resize(self.time_label.size())
        
    def on_countdown_finished(self):
        """倒计时结束处理"""
        action = self.settings["countdown_action"]
        
        # 播放铃声
        if self.settings.get("enable_sound", True):
            sound_file = self.settings.get("sound_file", "")
            if sound_file and os.path.exists(sound_file):
                self.play_sound(sound_file)
            else:
                # 如果没有自定义铃声，播放系统提示音
                if self.tr('beep') in action or '提示音' in action:
                    QApplication.beep()
        
        # 闪烁提醒
        if self.tr('flash') in action or '闪烁' in action:
            # 开始闪烁
            self.is_flashing = True
            self.flash_count = 0
            self.flash_timer.start(500)
        
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
                3000
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
                    duration=5,
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
            # 停止闪烁（只闪3次）
            self.flash_count += 1
            if self.flash_count >= 6:  # 3次闪烁 = 6次状态切换
                self.is_flashing = False
                self.flash_count = 0
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
                1000
            )
        else:
            self.pause_action.setText(self.tr('continue'))
            self.tray_icon.showMessage(
                self.tr('app_name'),
                self.tr('timer_paused'),
                QSystemTrayIcon.Information,
                1000
            )
        
        try:
            self.update_tray_icon()
        except Exception:
            pass
    
    def reset_timer(self):
        """重置计时：倒计时回到初始设置，正计时归零"""
        mode = self.settings.get("timer_mode", "倒计时")
        if self.tr('countdown_mode') in mode or '倒计时' in mode:
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
            1000
        )
        
        try:
            self.update_tray_icon()
        except Exception:
            pass
    
    def quick_countdown(self, hours, minutes, seconds):
        """快速设置倒计时"""
        self.settings["timer_mode"] = self.tr('countdown_mode')
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
            self.show()
            self.activateWindow()
            
    def tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()
            
    def quit_app(self):
        """退出应用"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于拖动窗口"""
        if self.dragging:
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
        
        # 快捷预设
        preset_menu = QMenu(self.tr('quick_presets'), self)
        
        presets = [
            (self.tr('pomodoro'), 0, 25, 0),
            (self.tr('short_break'), 0, 5, 0),
            (self.tr('long_break'), 0, 15, 0),
            ('30 ' + self.tr('minutes'), 0, 30, 0),
            ('1 ' + self.tr('hours'), 1, 0, 0),
            (self.tr('switch_count_up'), -1, -1, -1),
        ]
        
        for name, h, m, s in presets:
            action = QAction(name, self)
            if h == -1:
                action.triggered.connect(self.switch_to_count_up)
            else:
                action.triggered.connect(lambda checked, hours=h, mins=m, secs=s: 
                                        self.quick_countdown(hours, mins, secs))
            preset_menu.addAction(action)
            
        menu.addMenu(preset_menu)
        menu.addSeparator()
        
        # 设置
        settings_action = QAction(self.tr('settings'), self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # 显示/隐藏
        hide_action = QAction(self.tr('show_hide'), self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction(self.tr('quit'), self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())
        
    def switch_to_count_up(self):
        """切换到正计时"""
        self.settings["timer_mode"] = self.tr('count_up_mode')
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
            1000
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
        """首次显示时启动托盘图标刷新定时器"""
        super().showEvent(event)
        if not hasattr(self, '_icon_updater_started') or not self._icon_updater_started:
            self._icon_updater_started = True
            try:
                self.icon_update_timer = QTimer(self)
                self.icon_update_timer.timeout.connect(self.update_tray_icon)
                self.icon_update_timer.start(1000)  # 每秒更新一次
                self.update_tray_icon()
            except Exception as e:
                print(f"启动托盘图标刷新失败: {e}")


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
