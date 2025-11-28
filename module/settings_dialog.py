import logging
import os
import random
import uuid
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QKeySequence
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QKeySequenceEdit,
    QFontDialog,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
)

from .constants import (
    APP_VERSION,
    DEFAULT_COUNTDOWN_PRESETS,
    DEFAULT_SHORTCUTS,
    PROJECT_URL,
)

logger = logging.getLogger(__name__)
from .localization import LANGUAGES
from .paths import get_base_path

if TYPE_CHECKING:
    from .timer_window import TimerWindow


class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # type: TimerWindow
        self._current_lang_code = self.parent_window.settings.get("language", "zh_CN")
        self._other_lang_code = self._find_other_language(self._current_lang_code)
        self._preset_data = self._load_preset_snapshot()
        self.setWindowTitle(self.tr('settings_title'))
        
        # 设置窗口图标
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        base_path = self._base_path()
        icon_path = os.path.join(base_path, "img", "timer_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 隐藏帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.setMinimumSize(700, 800)  # 进一步增加尺寸确保内容显示完整
        self.resize(700, 800)  # 设置初始大小
        self.init_ui()
        
    def tr(self, key):
        """翻译助手"""
        lang = self.parent_window.settings.get("language", "zh_CN")
        return LANGUAGES.get(lang, LANGUAGES['zh_CN']).get(key, key)

    def _base_path(self) -> str:
        if self.parent_window and getattr(self.parent_window, 'base_path', None):
            return self.parent_window.base_path
        return get_base_path()

    def _find_other_language(self, current_code: str) -> str:
        for code in LANGUAGES.keys():
            if code != current_code:
                return code
        return current_code

    def _load_preset_snapshot(self):
        presets = self.parent_window.settings.get('countdown_presets')
        snapshot = []
        if isinstance(presets, list):
            for preset in presets:
                if isinstance(preset, dict):
                    entry = dict(preset)
                    if isinstance(preset.get('labels'), dict):
                        entry['labels'] = dict(preset['labels'])
                    snapshot.append(entry)
        if not snapshot:
            snapshot = []
            for preset in DEFAULT_COUNTDOWN_PRESETS:
                entry = dict(preset)
                snapshot.append(entry)
        for entry in snapshot:
            entry.setdefault('mode', 'countdown')
            preset_id = entry.get('id')
            if not isinstance(preset_id, str) or not preset_id.strip():
                entry['id'] = f"preset_{uuid.uuid4().hex[:8]}"
        return snapshot

    def _clean_labels(self, labels):
        cleaned = {}
        if isinstance(labels, dict):
            for lang_code, text in labels.items():
                if not isinstance(lang_code, str):
                    continue
                if isinstance(text, str):
                    stripped = text.strip()
                    if stripped:
                        cleaned[lang_code] = stripped
        return cleaned

    def _apply_label_result(self, entry, data):
        labels = self._clean_labels(data.get('labels'))
        if labels:
            entry['labels'] = labels
            primary_label = labels.get(self._current_lang_code)
            if not primary_label and labels:
                primary_label = next(iter(labels.values()))
            if primary_label:
                entry['label'] = primary_label
        else:
            entry.pop('labels', None)
            label = data.get('label')
            if label:
                entry['label'] = label
            else:
                entry.pop('label', None)

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
        base_path = self._base_path()
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

        preset_label = QLabel(self.tr('preset_manage_hint'))
        preset_label.setWordWrap(True)
        preset_layout.addWidget(preset_label)

        self.preset_list = QListWidget()
        self.preset_list.setSelectionMode(QListWidget.SingleSelection)
        self.preset_list.itemSelectionChanged.connect(self._update_preset_button_states)
        self.preset_list.itemDoubleClicked.connect(lambda _: self.edit_selected_preset())
        preset_layout.addWidget(self.preset_list)

        action_row = QHBoxLayout()
        self.preset_add_btn = QPushButton(self.tr('preset_add'))
        self.preset_add_btn.clicked.connect(self.add_preset)
        self.preset_edit_btn = QPushButton(self.tr('preset_edit'))
        self.preset_edit_btn.clicked.connect(self.edit_selected_preset)
        self.preset_delete_btn = QPushButton(self.tr('preset_delete'))
        self.preset_delete_btn.clicked.connect(self.remove_selected_preset)
        self.preset_reset_btn = QPushButton(self.tr('preset_reset'))
        self.preset_reset_btn.clicked.connect(self.reset_presets)
        action_row.addWidget(self.preset_add_btn)
        action_row.addWidget(self.preset_edit_btn)
        action_row.addWidget(self.preset_delete_btn)
        action_row.addStretch()
        action_row.addWidget(self.preset_reset_btn)
        preset_layout.addLayout(action_row)

        reorder_row = QHBoxLayout()
        self.preset_up_btn = QPushButton(self.tr('preset_move_up'))
        self.preset_up_btn.clicked.connect(lambda: self.move_selected_preset(-1))
        self.preset_down_btn = QPushButton(self.tr('preset_move_down'))
        self.preset_down_btn.clicked.connect(lambda: self.move_selected_preset(1))
        reorder_row.addWidget(self.preset_up_btn)
        reorder_row.addWidget(self.preset_down_btn)
        reorder_row.addStretch()
        preset_layout.addLayout(reorder_row)

        apply_row = QHBoxLayout()
        self.preset_apply_btn = QPushButton(self.tr('preset_apply_to_timer'))
        self.preset_apply_btn.clicked.connect(self.apply_selected_preset_to_timer)
        apply_row.addWidget(self.preset_apply_btn)
        apply_row.addStretch()
        preset_layout.addLayout(apply_row)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        layout.addStretch()
        widget.setLayout(layout)

        self._refresh_preset_list()
        self._update_preset_button_states()
        return widget

    def _preview_language_change(self, _index):
        new_lang = "zh_CN" if self.lang_combo.currentText() == "简体中文" else "en_US"
        current = self.parent_window.settings.get("language", "zh_CN")
        if new_lang == current:
            return
        self.parent_window.settings["language"] = new_lang
        self.parent_window.apply_settings(preserve_elapsed=True)
        self.parent_window.create_tray_menu()
        try:
            self.parent_window.reload_shortcuts()
        except Exception:
            pass
        # 仅预览，不保存
        self.parent_window.settings["language"] = current

    def _format_preset_duration(self, preset):
        hours = max(0, min(99, int(preset.get('hours', 0))))
        minutes = max(0, min(59, int(preset.get('minutes', 0))))
        seconds = max(0, min(59, int(preset.get('seconds', 0))))
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _format_duration_text(self, preset):
        hours = max(0, min(99, int(preset.get('hours', 0))))
        minutes = max(0, min(59, int(preset.get('minutes', 0))))
        seconds = max(0, min(59, int(preset.get('seconds', 0))))
        lang_code = self.parent_window.settings.get('language', 'zh_CN')
        is_zh = lang_code.startswith('zh')

        def _fmt(value, unit_key):
            if value <= 0:
                return None
            unit_text = self.tr(unit_key)
            return f"{value}{unit_text}" if is_zh else f"{value} {unit_text}"

        parts = [
            _fmt(hours, 'hours'),
            _fmt(minutes, 'minutes'),
            _fmt(seconds, 'seconds'),
        ]
        parts = [p for p in parts if p]
        if not parts:
            unit = self.tr('seconds')
            return f"0{unit}" if is_zh else f"0 {unit}"
        return ''.join(parts) if is_zh else ' '.join(parts)

    def _resolve_preset_label(self, preset):
        label = preset.get('label')
        if isinstance(label, str) and label.strip():
            return label.strip()
        name_key = preset.get('name_key')
        if name_key:
            translated = self.tr(name_key)
            if translated and translated != name_key:
                return translated
        return self._format_duration_text(preset)

    def _preset_summary(self, preset):
        return f"{self._resolve_preset_label(preset)} · {self._format_preset_duration(preset)}"

    def _refresh_preset_list(self):
        if not hasattr(self, 'preset_list'):
            return
        self.preset_list.clear()
        for preset in self._preset_data:
            item = QListWidgetItem(self._preset_summary(preset))
            item.setData(Qt.UserRole, preset.get('id'))
            self.preset_list.addItem(item)

    def _get_selected_preset_index(self):
        if not hasattr(self, 'preset_list'):
            return -1
        row = self.preset_list.currentRow()
        if 0 <= row < len(self._preset_data):
            return row
        return -1

    def _update_preset_button_states(self):
        has_selection = self._get_selected_preset_index() != -1
        for btn in [
            getattr(self, 'preset_edit_btn', None),
            getattr(self, 'preset_delete_btn', None),
            getattr(self, 'preset_up_btn', None),
            getattr(self, 'preset_down_btn', None),
            getattr(self, 'preset_apply_btn', None),
        ]:
            if btn:
                btn.setEnabled(has_selection)

    def add_preset(self):
        dialog = PresetEditorDialog(
            parent=self,
            translator=self.tr,
            allow_auto_name=False,
            current_lang=self._current_lang_code,
            other_lang=self._other_lang_code,
            existing_labels={},
        )
        dialog.setWindowTitle(self.tr('preset_add'))
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_result()
            new_entry = {
                'id': f"preset_{uuid.uuid4().hex[:8]}",
                'mode': 'countdown',
                'hours': data['hours'],
                'minutes': data['minutes'],
                'seconds': data['seconds'],
            }
            self._apply_label_result(new_entry, data)
            self._preset_data.append(new_entry)
            self._refresh_preset_list()
            self.preset_list.setCurrentRow(len(self._preset_data) - 1)
            self._update_preset_button_states()

    def edit_selected_preset(self):
        index = self._get_selected_preset_index()
        if index == -1:
            return
        preset = self._preset_data[index]
        allow_auto = bool(preset.get('name_key'))
        existing_labels = self._clean_labels(preset.get('labels'))
        legacy_label = preset.get('label')
        if isinstance(legacy_label, str) and legacy_label.strip():
            existing_labels.setdefault(self._current_lang_code, legacy_label.strip())
        dialog = PresetEditorDialog(
            parent=self,
            translator=self.tr,
            allow_auto_name=allow_auto,
            initial=preset,
            resolved_label=self._resolve_preset_label(preset),
            current_lang=self._current_lang_code,
            other_lang=self._other_lang_code,
            existing_labels=existing_labels,
        )
        dialog.setWindowTitle(self.tr('preset_edit'))
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_result()
            preset['hours'] = data['hours']
            preset['minutes'] = data['minutes']
            preset['seconds'] = data['seconds']
            self._apply_label_result(preset, data)
            if not allow_auto:
                preset.pop('name_key', None)
            self._preset_data[index] = preset
            self._refresh_preset_list()
            self.preset_list.setCurrentRow(index)

    def remove_selected_preset(self):
        index = self._get_selected_preset_index()
        if index == -1:
            return
        reply = QMessageBox.question(
            self,
            self.tr('preset_delete_confirm_title'),
            self.tr('preset_delete_confirm_msg'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._preset_data.pop(index)
            self._refresh_preset_list()
            self._update_preset_button_states()

    def move_selected_preset(self, offset):
        index = self._get_selected_preset_index()
        if index == -1:
            return
        new_index = index + offset
        if not 0 <= new_index < len(self._preset_data):
            return
        self._preset_data[index], self._preset_data[new_index] = (
            self._preset_data[new_index],
            self._preset_data[index],
        )
        self._refresh_preset_list()
        self.preset_list.setCurrentRow(new_index)

    def reset_presets(self):
        reply = QMessageBox.question(
            self,
            self.tr('preset_reset'),
            self.tr('preset_reset_confirm_msg'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._preset_data = [dict(preset) for preset in DEFAULT_COUNTDOWN_PRESETS]
        self._refresh_preset_list()
        self._update_preset_button_states()

    def apply_selected_preset_to_timer(self):
        index = self._get_selected_preset_index()
        if index == -1:
            return
        preset = self._preset_data[index]
        self.mode_combo.setCurrentIndex(1)  # 倒计时
        self.hours_spin.setValue(int(preset.get('hours', 0)))
        self.minutes_spin.setValue(int(preset.get('minutes', 0)))
        self.seconds_spin.setValue(int(preset.get('seconds', 0)))
        QMessageBox.information(
            self,
            self.tr('preset_applied'),
            self.tr('preset_applied_msg').format(
                preset.get('hours', 0),
                preset.get('minutes', 0),
                preset.get('seconds', 0),
            ),
        )
        
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
        self.lang_combo.currentIndexChanged.connect(self._preview_language_change)
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
        
    def choose_sound_file(self):
        """选择铃声文件"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        base_path = self._base_path()
        
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
        base_path = self._base_path()
        
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
            logger.warning("Failed to open sound folder: %s", e)
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
                base_path = self._base_path()
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
            base_path = self._base_path()
            try:
                rel_path = os.path.relpath(selected_sound, base_path)
            except ValueError:
                rel_path = selected_sound
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
        
    def _serialize_presets(self):
        serialized = []
        for preset in self._preset_data:
            entry = {
                'id': preset.get('id') or f"preset_{uuid.uuid4().hex[:8]}",
                'mode': 'countdown',
                'hours': max(0, min(99, int(preset.get('hours', 0)))),
                'minutes': max(0, min(59, int(preset.get('minutes', 0)))),
                'seconds': max(0, min(59, int(preset.get('seconds', 0)))),
            }
            label = preset.get('label')
            if isinstance(label, str) and label.strip():
                entry['label'] = label.strip()
            name_key = preset.get('name_key')
            if isinstance(name_key, str) and name_key.strip():
                entry['name_key'] = name_key.strip()
            labels = self._clean_labels(preset.get('labels'))
            if labels:
                entry['labels'] = labels
                primary_label = labels.get(self._current_lang_code)
                if primary_label:
                    entry['label'] = primary_label
            serialized.append(entry)
        if not serialized:
            serialized = [dict(preset) for preset in DEFAULT_COUNTDOWN_PRESETS]
        return serialized

    def apply_settings(self):
        """应用设置"""
        self.parent_window.settings["countdown_presets"] = self._serialize_presets()
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


class PresetEditorDialog(QDialog):
    def __init__(
        self,
        parent,
        translator,
        allow_auto_name=False,
        initial=None,
        resolved_label=None,
        current_lang='zh_CN',
        other_lang='en_US',
        existing_labels=None,
    ):
        super().__init__(parent)
        self._tr = translator
        self._allow_auto_name = allow_auto_name
        self._initial = initial or {}
        self._resolved_label = resolved_label
        self._result = None
        self._current_lang = current_lang
        self._other_lang = other_lang
        raw_labels = existing_labels if isinstance(existing_labels, dict) else self._initial.get('labels')
        self._existing_labels = self._clean_labels_dict(raw_labels)
        self._legacy_label = self._extract_legacy_label()

        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout()

        form = QFormLayout()
        primary_label_text = self._tr('preset_primary_label').format(self._language_name(self._current_lang))
        self.primary_edit = QLineEdit()
        default_label = self._get_existing_label(self._current_lang) or self._initial.get('label') or self._resolved_label or ''
        if default_label:
            self.primary_edit.setText(default_label)
        placeholder = self._tr('preset_name_placeholder_auto') if self._allow_auto_name else ''
        if placeholder:
            self.primary_edit.setPlaceholderText(placeholder)
        tooltip_text = self._tr('preset_same_label_tip')
        self.primary_edit.setToolTip(tooltip_text)
        form.addRow(primary_label_text, self.primary_edit)

        self.secondary_toggle = QCheckBox(
            self._tr('preset_secondary_toggle').format(self._language_name(self._other_lang))
        )
        self.secondary_toggle.toggled.connect(self._update_secondary_state)
        form.addRow(self.secondary_toggle)

        secondary_label_text = self._tr('preset_secondary_label').format(self._language_name(self._other_lang))
        self.secondary_edit = QLineEdit()
        self.secondary_edit.setEnabled(False)
        other_default = self._get_existing_label(self._other_lang)
        if other_default:
            self.secondary_edit.setText(other_default)
            self.secondary_toggle.setChecked(True)
        self.secondary_edit.setToolTip(self._tr('preset_same_label_tip'))
        form.addRow(secondary_label_text, self.secondary_edit)

        same_label_hint = QLabel(self._tr('preset_same_label_tip'))
        same_label_hint.setStyleSheet('color:#777;')
        same_label_hint.setWordWrap(True)
        form.addRow(same_label_hint)

        dual_hint = QLabel(self.tr('preset_multi_lang_hint'))
        dual_hint.setWordWrap(True)
        dual_hint.setStyleSheet('color:#777;')
        dual_hint.setToolTip(tooltip_text)
        form.addRow(dual_hint)

        duration_label = QLabel(self._tr('preset_duration'))
        duration_row = QHBoxLayout()
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 99)
        self.hours_spin.setValue(int(self._initial.get('hours', 0)))
        self.hours_spin.setSuffix(' ' + self._tr('hours'))

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(int(self._initial.get('minutes', 0)))
        self.minutes_spin.setSuffix(' ' + self._tr('minutes'))

        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setValue(int(self._initial.get('seconds', 0)))
        self.seconds_spin.setSuffix(' ' + self._tr('seconds'))

        duration_row.addWidget(self.hours_spin)
        duration_row.addWidget(self.minutes_spin)
        duration_row.addWidget(self.seconds_spin)
        form.addRow(duration_label, duration_row)
        layout.addLayout(form)

        if self._allow_auto_name:
            hint = QLabel(self._tr('preset_auto_name_hint'))
            hint.setStyleSheet('color:#666;')
            layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def accept(self):
        name = self.primary_edit.text().strip()
        total_seconds = (
            self.hours_spin.value() * 3600
            + self.minutes_spin.value() * 60
            + self.seconds_spin.value()
        )
        if total_seconds <= 0:
            QMessageBox.warning(self, self._tr('preset_error_title'), self._tr('preset_error_duration'))
            return
        existing_labels = self._initial.get('labels') if isinstance(self._initial.get('labels'), dict) else {}
        existing_primary = existing_labels.get(self._current_lang)
        has_existing_primary = isinstance(existing_primary, str) and existing_primary.strip()
        if not name and not self._allow_auto_name and not has_existing_primary and not self.secondary_toggle.isChecked():
            QMessageBox.warning(self, self._tr('preset_error_title'), self._tr('preset_error_name'))
            return
        labels = {}
        if name:
            labels[self._current_lang] = name
        if self.secondary_toggle.isChecked():
            alt_name = self.secondary_edit.text().strip()
            if not alt_name:
                QMessageBox.warning(self, self._tr('preset_error_title'), self._tr('preset_error_name'))
                return
            labels[self._other_lang] = alt_name
        else:
            labels.pop(self._other_lang, None)
        # 保留其他语言的既有标签（如果用户未显式移除）
        if isinstance(existing_labels, dict):
            for lang_code, text in existing_labels.items():
                if not isinstance(lang_code, str):
                    continue
                if lang_code == self._current_lang:
                    if not name and isinstance(text, str) and text.strip():
                        labels[self._current_lang] = text.strip()
                    continue
                if lang_code == self._other_lang and not self.secondary_toggle.isChecked():
                    continue
                if isinstance(text, str) and text.strip():
                    labels.setdefault(lang_code, text.strip())

        if not labels and self._allow_auto_name:
            label_value = None
        else:
            label_value = labels.get(self._current_lang)
            if not label_value and labels:
                label_value = next(iter(labels.values()))
        if not labels and not self._allow_auto_name:
            # 没有任何语言的名称
            QMessageBox.warning(self, self._tr('preset_error_title'), self._tr('preset_error_name'))
            return
        self._result = {
            'hours': self.hours_spin.value(),
            'minutes': self.minutes_spin.value(),
            'seconds': self.seconds_spin.value(),
            'label': label_value,
            'labels': labels if labels else None,
        }
        super().accept()

    def get_result(self):
        if self._result:
            return self._result
        labels = dict(self._existing_labels)
        fallback = self.primary_edit.text().strip()
        if fallback:
            labels[self._current_lang] = fallback
        return {
            'hours': self.hours_spin.value(),
            'minutes': self.minutes_spin.value(),
            'seconds': self.seconds_spin.value(),
            'label': fallback or self._legacy_label,
            'labels': labels or None,
        }

    def _language_name(self, lang_code):
        key = f"language_name_{lang_code}"
        text = self._tr(key)
        return text if text != key else lang_code

    @staticmethod
    def _clean_labels_dict(raw):
        cleaned = {}
        if isinstance(raw, dict):
            for lang_code, text in raw.items():
                if not isinstance(lang_code, str):
                    continue
                if isinstance(text, str):
                    stripped = text.strip()
                    if stripped:
                        cleaned[lang_code] = stripped
        return cleaned

    def _extract_legacy_label(self):
        legacy = self._initial.get('label')
        if isinstance(legacy, str) and legacy.strip():
            return legacy.strip()
        if isinstance(self._resolved_label, str) and self._resolved_label.strip():
            return self._resolved_label.strip()
        return None

    def _get_existing_label(self, lang_code):
        labels = self._existing_labels or self._initial.get('labels')
        if isinstance(labels, dict):
            value = labels.get(lang_code)
            if isinstance(value, str) and value.strip():
                return value.strip()
            lang_short = lang_code.split('_')[0]
            for key, text in labels.items():
                if not isinstance(key, str):
                    continue
                if key.split('_')[0] == lang_short and isinstance(text, str) and text.strip():
                    return text.strip()
        return self._legacy_label

    def _update_secondary_state(self, checked):
        self.secondary_edit.setEnabled(checked)
