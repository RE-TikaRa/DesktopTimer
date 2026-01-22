import logging
import os
import random
import uuid
from typing import TYPE_CHECKING, cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFontDatabase, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QKeySequenceEdit,
    QListWidgetItem,
)
from qfluentwidgets import (
    BodyLabel as QLabel,
    CheckBox as QCheckBox,
    ColorDialog,
    ComboBox as QComboBox,
    CardWidget,
    Dialog,
    FluentIcon,
    IconWidget,
    LineEdit as QLineEdit,
    ListWidget as QListWidget,
    MessageBox,
    Pivot,
    PushSettingCard,
    PrimaryPushButton,
    PushButton as QPushButton,
    ScrollArea as QScrollArea,
    Slider as QSlider,
    SpinBox as QSpinBox,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
)

from .constants import (
    APP_VERSION,
    DEFAULT_COUNTDOWN_PRESETS,
    DEFAULT_SHORTCUTS,
    PROJECT_URL,
)
from .localization import LANGUAGES
from .paths import get_base_path

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .timer_window import TimerWindow


class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = cast("TimerWindow", parent)
        self._current_lang_code = self.parent_window.settings.get("language", "zh_CN")
        self._initial_lang_code = self._current_lang_code
        self._other_lang_code = self._find_other_language(self._current_lang_code)
        self._preset_data = self._load_preset_snapshot()
        self._applied_once = False
        self.setWindowTitle(self.tr('settings_title'))
        
        # 设置窗口图标
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        base_path = self._base_path()
        icon_path = os.path.join(base_path, "img", "timer_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 隐藏帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.setMinimumSize(800, 600)  # 允许用户缩小窗口
        self.resize(850, 800)  # 设置默认大小
        self.init_ui()
        
    def tr(self, sourceText: str, disambiguation: str | None = None, n: int = -1) -> str:  # type: ignore[override]
        """翻译助手"""
        _ = disambiguation
        _ = n
        lang = self.parent_window.settings.get("language", "zh_CN")
        return LANGUAGES.get(lang, LANGUAGES['zh_CN']).get(sourceText, sourceText)

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

    def _confirm(self, title: str, content: str) -> bool:
        dialog = Dialog(title, content, self)
        return bool(dialog.exec())

    def _notify(self, title: str, content: str) -> None:
        MessageBox(title, content, self).exec()

    def _pick_color(self, title: str, initial_hex: str) -> QColor | None:
        initial = QColor(initial_hex)
        color_holder = {"color": initial}
        dialog = ColorDialog(initial, title, self, enableAlpha=False)
        dialog.colorChanged.connect(lambda c: color_holder.__setitem__("color", c))
        if dialog.exec():
            return color_holder["color"]
        return None

    def _create_card(self, title: str) -> tuple[CardWidget, QVBoxLayout]:
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)
        return card, layout

    def _apply_switch_status(self, card, desc: str | None = None) -> None:
        def _update(checked: bool) -> None:
            status = self.tr('status_on') if checked else self.tr('status_off')
            if desc:
                card.setContent(f"{desc} · {status}")
            else:
                card.setContent(status)
        _update(card.isChecked())
        card.checkedChanged.connect(lambda checked: _update(checked))

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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 创建导航与内容容器
        self.pivot = Pivot(self)
        self.stacked_widget = QStackedWidget(self)
        
        # 外观设置选项卡
        appearance_tab = self.create_appearance_tab()
        self._add_tab(appearance_tab, "appearance", self.tr('appearance'))
        
        # 计时模式选项卡
        mode_tab = self.create_mode_tab()
        self._add_tab(mode_tab, "timer_mode", self.tr('timer_mode'))
        
        # 预设选项卡
        preset_tab = self.create_preset_tab()
        self._add_tab(preset_tab, "presets", self.tr('presets'))
        
        # 通用设置选项卡
        general_tab = self.create_general_tab()
        self._add_tab(general_tab, "general", self.tr('general'))
        
        # 关于选项卡
        about_tab = self.create_about_tab()
        self._add_tab(about_tab, "about", self.tr('about'))

        self.stacked_widget.setCurrentWidget(appearance_tab)
        self.pivot.setCurrentItem("appearance")
        self.stacked_widget.currentChanged.connect(self._sync_pivot)

        layout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.stacked_widget, 1)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        apply_btn = QPushButton(self.tr('apply'))
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.clicked.connect(self.apply_settings)
        
        ok_btn = PrimaryPushButton(self.tr('ok'))
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept_settings)
        
        cancel_btn = QPushButton(self.tr('cancel'))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _add_tab(self, widget: QWidget, route_key: str, title: str) -> None:
        widget.setObjectName(route_key)
        self.stacked_widget.addWidget(widget)
        self.pivot.addItem(
            routeKey=route_key,
            text=title,
            onClick=lambda: self.stacked_widget.setCurrentWidget(widget),
        )

    def _sync_pivot(self, index: int) -> None:
        widget = self.stacked_widget.widget(index)
        if widget is not None:
            self.pivot.setCurrentItem(widget.objectName())
    
    def create_about_tab(self):
        """创建关于选项卡"""
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)

        header_card = CardWidget()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(12)

        base_path = self._base_path()
        logo_path = os.path.join(base_path, "img", "ALP_STUDIO-logo-full.svg")
        if os.path.exists(logo_path):
            logo_widget = IconWidget(QIcon(logo_path))
            logo_widget.setFixedSize(340, 200)
            logo_container = QWidget()
            logo_layout = QHBoxLayout(logo_container)
            logo_layout.addStretch()
            logo_layout.addWidget(logo_widget)
            logo_layout.addStretch()
            logo_layout.setContentsMargins(0, 0, 0, 6)
            header_layout.addWidget(logo_container)
        else:
            logo_label = QLabel("🕒")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_font = logo_label.font()
            logo_font.setPointSize(40)
            logo_label.setFont(logo_font)
            header_layout.addWidget(logo_label)

        app_name = QLabel("DesktopTimer")
        app_font = app_name.font()
        app_font.setPointSize(22)
        app_font.setBold(True)
        app_name.setFont(app_font)
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(app_name)

        subtitle = QLabel(self.tr('app_subtitle'))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(11)
        subtitle.setFont(subtitle_font)
        header_layout.addWidget(subtitle)

        layout.addWidget(header_card)

        info_group = SettingCardGroup(self.tr('about_basic_info'), widget)
        info_items = [
            (self.tr('about_version'), f"{APP_VERSION}", None),
            (self.tr('about_author'), "TikaRa", None),
            (self.tr('about_email'), "163mail@re-TikaRa.fun", "mailto:163mail@re-TikaRa.fun"),
            (self.tr('about_website'), "re-tikara.fun", "https://re-tikara.fun"),
            (self.tr('about_homepage'), self.tr('about_homepage_value'), PROJECT_URL),
            (self.tr('about_bilibili'), "夜雨安歌_TikaRa", "https://space.bilibili.com/374412219"),
            (self.tr('about_license'), self.tr('about_license_value'), None),
        ]

        for label_text, value_text, link_url in info_items:
            card = SettingCard(
                FluentIcon.INFO,
                label_text,
                None,
                parent=self,
            )
            if link_url:
                value_label = QLabel(f'<a href="{link_url}">{value_text}</a>')
                value_label.setOpenExternalLinks(True)
            else:
                value_label = QLabel(value_text)
            card.hBoxLayout.addWidget(
                value_label,
                0,
                Qt.AlignmentFlag.AlignRight,
            )
            card.hBoxLayout.addSpacing(16)
            info_group.addSettingCard(card)

        layout.addWidget(info_group)

        desc_card = CardWidget()
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(24, 16, 24, 16)
        desc_layout.setSpacing(8)
        desc_label = QLabel(self.tr('about_description'))
        desc_label.setWordWrap(True)
        thanks_label = QLabel(self.tr('about_thanks'))
        thanks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(thanks_label)
        layout.addWidget(desc_card)

        layout.addStretch()

        widget.setLayout(layout)
        scroll.setWidget(widget)

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
        layout.setSpacing(16)
        
        font_group = SettingCardGroup(self.tr('font_settings'), widget)
        font_summary = (
            f"{self.parent_window.settings.get('font_family', 'Consolas')} · "
            f"{self.parent_window.settings.get('font_size', 96)}px"
        )
        self.font_card = PushSettingCard(
            self.tr('choose_font'),
            FluentIcon.FONT,
            self.tr('font'),
            font_summary,
            parent=self,
        )
        self.font_card.clicked.connect(self.choose_font)
        font_group.addSettingCard(self.font_card)
        layout.addWidget(font_group)

        color_group = SettingCardGroup(self.tr('color_settings'), widget)
        text_color = self.parent_window.settings.get("text_color", "#E0E0E0")
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(80, 30)
        self.update_color_button(self.text_color_btn, text_color)
        self.text_color_btn.clicked.connect(self.choose_text_color)
        self.text_color_card = SettingCard(
            FluentIcon.FONT,
            self.tr('text_color'),
            text_color,
            parent=self,
        )
        self.text_color_card.hBoxLayout.addWidget(
            self.text_color_btn,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.text_color_card.hBoxLayout.addSpacing(16)
        color_group.addSettingCard(self.text_color_card)

        bg_color = self.parent_window.settings.get("bg_color", "#1E1E1E")
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(80, 30)
        self.update_color_button(self.bg_color_btn, bg_color)
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        self.bg_color_card = SettingCard(
            FluentIcon.PALETTE,
            self.tr('bg_color'),
            bg_color,
            parent=self,
        )
        self.bg_color_card.hBoxLayout.addWidget(
            self.bg_color_btn,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.bg_color_card.hBoxLayout.addSpacing(16)
        color_group.addSettingCard(self.bg_color_card)
        layout.addWidget(color_group)

        opacity_group = SettingCardGroup(self.tr('opacity_settings'), widget)
        opacity_value = self.parent_window.settings.get("bg_opacity", 200)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(opacity_value)
        self.opacity_value_label = QLabel(str(opacity_value))
        self.opacity_card = SettingCard(
            FluentIcon.TRANSPARENT,
            self.tr('bg_opacity'),
            str(opacity_value),
            parent=self,
        )
        self.opacity_card.hBoxLayout.addWidget(
            self.opacity_value_label,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.opacity_card.hBoxLayout.addSpacing(6)
        self.opacity_card.hBoxLayout.addWidget(
            self.opacity_slider,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.opacity_card.hBoxLayout.addSpacing(16)
        def _update_opacity(v: int) -> None:
            self.opacity_value_label.setText(str(v))
            self.opacity_card.setContent(str(v))
        self.opacity_slider.valueChanged.connect(_update_opacity)
        opacity_group.addSettingCard(self.opacity_card)
        layout.addWidget(opacity_group)

        style_group = SettingCardGroup(self.tr('window_style'), widget)
        self.rounded_card = SwitchSettingCard(
            FluentIcon.LAYOUT,
            self.tr('rounded_corners'),
            None,
            parent=self,
        )
        self.rounded_card.setChecked(self.parent_window.settings.get("rounded_corners", True))
        self._apply_switch_status(self.rounded_card)
        style_group.addSettingCard(self.rounded_card)

        radius_value = self.parent_window.settings.get("corner_radius", 15)
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 50)
        self.radius_spin.setValue(radius_value)
        self.radius_spin.setSuffix(' px')
        self.radius_card = SettingCard(
            FluentIcon.BRUSH,
            self.tr('corner_radius'),
            f"{radius_value}px",
            parent=self,
        )
        self.radius_card.hBoxLayout.addWidget(
            self.radius_spin,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.radius_card.hBoxLayout.addSpacing(16)
        self.radius_spin.valueChanged.connect(
            lambda v: self.radius_card.setContent(f"{v}px")
        )
        style_group.addSettingCard(self.radius_card)

        current_size = self.parent_window.settings.get("font_size", 96)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(48, 220)
        self.size_slider.setSingleStep(2)
        self.size_slider.setValue(current_size)
        self.size_value_label = QLabel(f"{current_size}px")
        self.size_card = SettingCard(
            FluentIcon.FONT_SIZE,
            self.tr('window_size'),
            f"{current_size}px",
            parent=self,
        )
        self.size_card.hBoxLayout.addWidget(
            self.size_value_label,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.size_card.hBoxLayout.addSpacing(6)
        self.size_card.hBoxLayout.addWidget(
            self.size_slider,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.size_card.hBoxLayout.addSpacing(16)
        def _update_size(v: int) -> None:
            self.size_value_label.setText(f"{v}px")
            self.size_card.setContent(f"{v}px")
        self.size_slider.valueChanged.connect(_update_size)
        style_group.addSettingCard(self.size_card)
        layout.addWidget(style_group)

        theme_group = SettingCardGroup(self.tr('theme_settings'), widget)
        self.theme_mode_combo = QComboBox()
        theme_items = [
            ('auto', self.tr('theme_auto')),
            ('light', self.tr('theme_light')),
            ('dark', self.tr('theme_dark')),
        ]
        for key, label in theme_items:
            self.theme_mode_combo.addItem(label, key)
        current_theme = self.parent_window.settings.get("theme_mode", "auto")
        for i in range(self.theme_mode_combo.count()):
            if self.theme_mode_combo.itemData(i) == current_theme:
                self.theme_mode_combo.setCurrentIndex(i)
                break
        self.theme_mode_card = SettingCard(
            FluentIcon.PALETTE,
            self.tr('theme_mode'),
            None,
            parent=self,
        )
        self.theme_mode_card.hBoxLayout.addWidget(
            self.theme_mode_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.theme_mode_card.hBoxLayout.addSpacing(16)
        theme_group.addSettingCard(self.theme_mode_card)

        theme_color = self.parent_window.settings.get("theme_color", "#0078D4")
        self.theme_color_btn = QPushButton()
        self.theme_color_btn.setFixedSize(80, 30)
        self.update_color_button(self.theme_color_btn, theme_color)
        self.theme_color_btn.clicked.connect(self.choose_theme_color)
        self.theme_color_card = SettingCard(
            FluentIcon.PALETTE,
            self.tr('theme_color'),
            theme_color,
            parent=self,
        )
        preset_container = QWidget()
        preset_layout = QHBoxLayout(preset_container)
        preset_layout.setContentsMargins(0, 0, 0, 0)
        preset_layout.setSpacing(6)
        preset_colors = [
            "#0078D4",
            "#00B294",
            "#E81123",
            "#FFB900",
            "#8E8CD8",
            "#2D7D9A",
        ]
        for color in preset_colors:
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            btn.setStyleSheet(
                f"background-color: {color}; border: 1px solid #666; border-radius: 4px;"
            )
            btn.clicked.connect(lambda _, c=color: self._set_theme_color(c))
            preset_layout.addWidget(btn)
        self.theme_color_card.hBoxLayout.addWidget(
            preset_container,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.theme_color_card.hBoxLayout.addSpacing(6)
        self.theme_color_card.hBoxLayout.addWidget(
            self.theme_color_btn,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.theme_color_card.hBoxLayout.addSpacing(16)
        theme_group.addSettingCard(self.theme_color_card)
        layout.addWidget(theme_group)

        night_group = SettingCardGroup(self.tr('night_mode'), widget)
        self.night_mode_card = SwitchSettingCard(
            FluentIcon.BRIGHTNESS,
            self.tr('night_mode'),
            None,
            parent=self,
        )
        self.night_mode_card.setChecked(self.parent_window.settings.get("night_mode", False))
        self._apply_switch_status(self.night_mode_card, self.tr('night_mode_desc'))
        night_group.addSettingCard(self.night_mode_card)
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
        
        mode_group = SettingCardGroup(self.tr('timer_mode'), widget)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            self.tr('count_up_mode'),
            self.tr('countdown_mode'),
            self.tr('clock_mode'),
        ])
        key = self.parent_window.settings.get('timer_mode_key')
        if not key:
            key = TimerWindow.derive_mode_key(self.parent_window.settings.get('timer_mode', ''))
            self.parent_window.settings['timer_mode_key'] = key
        index = {'countup': 0, 'countdown': 1, 'clock': 2}.get(key, 1)
        self.mode_combo.setCurrentIndex(index)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_card = SettingCard(
            FluentIcon.STOP_WATCH,
            self.tr('mode'),
            None,
            parent=self,
        )
        mode_card.hBoxLayout.addWidget(
            self.mode_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        mode_card.hBoxLayout.addSpacing(16)
        mode_group.addSettingCard(mode_card)
        layout.addWidget(mode_group)
        
        self.countdown_widget = QWidget()
        countdown_layout = QVBoxLayout()
        countdown_group = SettingCardGroup(self.tr('countdown_mode'), self.countdown_widget)
        
        time_container = QWidget()
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(8)
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
        time_card = SettingCard(
            FluentIcon.STOP_WATCH,
            self.tr('countdown_time'),
            None,
            parent=self,
        )
        time_card.hBoxLayout.addWidget(
            time_container,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        time_card.hBoxLayout.addSpacing(16)
        countdown_group.addSettingCard(time_card)
        
        self.countdown_action = QComboBox()
        action_items = [
            ('beep', self.tr('beep')),
            ('flash', self.tr('flash')),
            ('beep_flash', self.tr('beep_flash')),
        ]
        for key, label in action_items:
            self.countdown_action.addItem(label, key)
        current_key = self.parent_window.settings.get("countdown_action_key")
        if current_key not in ('beep', 'flash', 'beep_flash'):
            current_key = self.parent_window.derive_action_key(
                self.parent_window.settings.get("countdown_action", "")
            )
        for i in range(self.countdown_action.count()):
            if self.countdown_action.itemData(i) == current_key:
                self.countdown_action.setCurrentIndex(i)
                break
        action_card = SettingCard(
            FluentIcon.SPEAKERS,
            self.tr('countdown_action'),
            None,
            parent=self,
        )
        action_card.hBoxLayout.addWidget(
            self.countdown_action,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        action_card.hBoxLayout.addSpacing(16)
        countdown_group.addSettingCard(action_card)
        countdown_layout.addWidget(countdown_group)
        self.countdown_widget.setLayout(countdown_layout)
        layout.addWidget(self.countdown_widget)
        
        self.clock_widget = QWidget()
        clock_layout = QVBoxLayout()
        clock_group = SettingCardGroup(self.tr('clock_mode'), self.clock_widget)
        
        self.clock_format_combo = QComboBox()
        self.clock_format_combo.addItems([
            self.tr('clock_24h_format'),
            self.tr('clock_12h_format') if 'clock_12h_format' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) else ('12小时制' if self.tr('quit') == '退出' else '12-Hour Format'),
        ])
        self.clock_format_combo.setCurrentIndex(0 if self.parent_window.settings.get("clock_format_24h", True) else 1)
        format_card = SettingCard(
            FluentIcon.DATE_TIME,
            self.tr('time_format'),
            None,
            parent=self,
        )
        format_card.hBoxLayout.addWidget(
            self.clock_format_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        format_card.hBoxLayout.addSpacing(16)
        clock_group.addSettingCard(format_card)
        
        self.clock_seconds_card = SwitchSettingCard(
            FluentIcon.STOP_WATCH,
            self.tr('clock_show_seconds'),
            None,
            parent=self,
        )
        self.clock_seconds_card.setChecked(self.parent_window.settings.get("clock_show_seconds", True))
        self._apply_switch_status(self.clock_seconds_card)
        clock_group.addSettingCard(self.clock_seconds_card)
        
        self.clock_date_card = SwitchSettingCard(
            FluentIcon.CALENDAR,
            self.tr('clock_show_date'),
            None,
            parent=self,
        )
        self.clock_date_card.setChecked(self.parent_window.settings.get("clock_show_date", True))
        self._apply_switch_status(self.clock_date_card)
        clock_group.addSettingCard(self.clock_date_card)

        self.clock_am_pm_card = SwitchSettingCard(
            FluentIcon.LANGUAGE,
            self.tr('clock_show_am_pm'),
            None,
            parent=self,
        )
        self.clock_am_pm_card.setChecked(self.parent_window.settings.get("clock_show_am_pm", True))
        self._apply_switch_status(self.clock_am_pm_card)
        clock_group.addSettingCard(self.clock_am_pm_card)

        self.am_pm_style_combo = QComboBox()
        self.am_pm_style_combo.addItems([
            self.tr('am_pm_style_en') or 'AM/PM',
            self.tr('am_pm_style_zh') or '上午/下午',
        ])
        current_style = self.parent_window.settings.get("clock_am_pm_style", "zh")
        self.am_pm_style_combo.setCurrentIndex(0 if current_style == 'en' else 1)
        style_card = SettingCard(
            FluentIcon.LANGUAGE,
            self.tr('clock_am_pm_style'),
            None,
            parent=self,
        )
        style_card.hBoxLayout.addWidget(
            self.am_pm_style_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        style_card.hBoxLayout.addSpacing(16)
        clock_group.addSettingCard(style_card)

        self.am_pm_pos_combo = QComboBox()
        self.am_pm_pos_combo.addItems([
            self.tr('am_pm_pos_before') or 'Before time',
            self.tr('am_pm_pos_after') or 'After time',
        ])
        current_pos = self.parent_window.settings.get("clock_am_pm_position", "before")
        self.am_pm_pos_combo.setCurrentIndex(0 if current_pos == 'before' else 1)
        pos_card = SettingCard(
            FluentIcon.ALIGNMENT,
            self.tr('clock_am_pm_position'),
            None,
            parent=self,
        )
        pos_card.hBoxLayout.addWidget(
            self.am_pm_pos_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        pos_card.hBoxLayout.addSpacing(16)
        clock_group.addSettingCard(pos_card)

        def _update_ampm_enabled():
            is_24h = (self.clock_format_combo.currentIndex() == 0)
            self.clock_am_pm_card.setEnabled(not is_24h)
            enable_detail = (not is_24h) and self.clock_am_pm_card.isChecked()
            self.am_pm_style_combo.setEnabled(enable_detail)
            self.am_pm_pos_combo.setEnabled(enable_detail)
        self.clock_format_combo.currentIndexChanged.connect(lambda _: _update_ampm_enabled())
        self.clock_am_pm_card.checkedChanged.connect(lambda _: _update_ampm_enabled())
        _update_ampm_enabled()
        
        clock_layout.addWidget(clock_group)
        self.clock_widget.setLayout(clock_layout)
        layout.addWidget(self.clock_widget)
        
        # 根据当前模式显示/隐藏倒计时设置
        self.on_mode_changed(self.mode_combo.currentText())
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_preset_tab(self):
        """创建预设选项卡"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)

        preset_group, preset_layout = self._create_card(self.tr('presets'))

        preset_label = QLabel(self.tr('preset_manage_hint'))
        preset_label.setWordWrap(True)
        preset_layout.addWidget(preset_label)

        self.preset_list = QListWidget()
        self.preset_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.preset_list.setMinimumHeight(260)
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

        layout.addWidget(preset_group)
        layout.addStretch()
        widget.setLayout(layout)

        self._refresh_preset_list()
        self._update_preset_button_states()
        scroll.setWidget(widget)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(scroll)
        wrapper.setLayout(wrapper_layout)
        return wrapper

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
            item.setData(Qt.ItemDataRole.UserRole, preset.get('id'))
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        if not self._confirm(
            self.tr('preset_delete_confirm_title'),
            self.tr('preset_delete_confirm_msg'),
        ):
            return
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
        if not self._confirm(
            self.tr('preset_reset'),
            self.tr('preset_reset_confirm_msg'),
        ):
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
        self._notify(
            self.tr('preset_applied'),
            self.tr('preset_applied_msg').format(
                preset.get('hours', 0),
                preset.get('minutes', 0),
                preset.get('seconds', 0),
            ),
        )
        
    def create_general_tab(self):
        """创建通用设置选项卡"""
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        lang_group = SettingCardGroup(self.tr('language'), widget)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['简体中文', 'English'])
        current_lang = '简体中文' if self.parent_window.settings.get("language", "zh_CN") == "zh_CN" else 'English'
        self.lang_combo.setCurrentText(current_lang)
        self.lang_combo.currentIndexChanged.connect(self._preview_language_change)
        lang_card = SettingCard(
            FluentIcon.LANGUAGE,
            self.tr('language'),
            None,
            parent=self,
        )
        lang_card.hBoxLayout.addWidget(
            self.lang_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        lang_card.hBoxLayout.addSpacing(16)
        lang_group.addSettingCard(lang_card)
        layout.addWidget(lang_group)
        
        startup_group = SettingCardGroup(self.tr('auto_start'), widget)
        self.auto_start_card = SwitchSettingCard(
            FluentIcon.PLAY,
            self.tr('auto_start_timer'),
            None,
            parent=self,
        )
        self.auto_start_card.setChecked(self.parent_window.settings.get("auto_start_timer", True))
        self._apply_switch_status(self.auto_start_card)
        startup_group.addSettingCard(self.auto_start_card)
        
        self.startup_behavior_combo = QComboBox()
        self.startup_behavior_combo.addItems([
            LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}).get('startup_mode_restore_last', '恢复上次模式' if self.tr('quit') == '退出' else 'Restore last mode'),
            LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}).get('startup_mode_fixed', '固定为指定模式' if self.tr('quit') == '退出' else 'Always use fixed mode'),
        ])
        self.startup_behavior_combo.setCurrentIndex(0 if self.parent_window.settings.get('startup_mode_behavior', 'restore') == 'restore' else 1)
        behavior_card = SettingCard(
            FluentIcon.UPDATE,
            self.tr('startup_mode_behavior'),
            None,
            parent=self,
        )
        behavior_card.hBoxLayout.addWidget(
            self.startup_behavior_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        behavior_card.hBoxLayout.addSpacing(16)
        startup_group.addSettingCard(behavior_card)
        
        self.startup_fixed_combo = QComboBox()
        self.startup_fixed_combo.addItems([
            self.tr('count_up_mode'),
            self.tr('countdown_mode'),
            self.tr('clock_mode'),
        ])
        fixed_map = {'countup': 0, 'countdown': 1, 'clock': 2}
        self.startup_fixed_combo.setCurrentIndex(fixed_map.get(self.parent_window.settings.get('startup_fixed_mode_key', 'countdown'), 1))
        self.startup_fixed_card = SettingCard(
            FluentIcon.PIN,
            self.tr('startup_fixed_mode'),
            None,
            parent=self,
        )
        self.startup_fixed_card.hBoxLayout.addWidget(
            self.startup_fixed_combo,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.startup_fixed_card.hBoxLayout.addSpacing(16)
        startup_group.addSettingCard(self.startup_fixed_card)
        
        def _update_fixed_enabled():
            enabled = self.startup_behavior_combo.currentIndex() == 1
            self.startup_fixed_card.setEnabled(enabled)
        self.startup_behavior_combo.currentIndexChanged.connect(lambda _: _update_fixed_enabled())
        _update_fixed_enabled()
        
        layout.addWidget(startup_group)
        
        sound_group = SettingCardGroup(self.tr('sound_settings'), widget)
        self.enable_sound_card = SwitchSettingCard(
            FluentIcon.SPEAKERS,
            self.tr('enable_sound'),
            None,
            parent=self,
        )
        self.enable_sound_card.setChecked(self.parent_window.settings.get("enable_sound", True))
        self._apply_switch_status(self.enable_sound_card)
        sound_group.addSettingCard(self.enable_sound_card)
        
        self.enable_popup_card = SwitchSettingCard(
            FluentIcon.MESSAGE,
            self.tr('enable_popup'),
            None,
            parent=self,
        )
        self.enable_popup_card.setChecked(self.parent_window.settings.get("enable_popup", True))
        self._apply_switch_status(self.enable_popup_card)
        sound_group.addSettingCard(self.enable_popup_card)

        self.enable_toast_card = SwitchSettingCard(
            FluentIcon.INFO,
            self.tr('enable_windows_toast'),
            None,
            parent=self,
        )
        self.enable_toast_card.setChecked(self.parent_window.settings.get("enable_windows_toast", True))
        self._apply_switch_status(self.enable_toast_card)
        sound_group.addSettingCard(self.enable_toast_card)

        current_volume = self.parent_window.settings.get("sound_volume", 80)
        if not isinstance(current_volume, int):
            try:
                current_volume = int(current_volume)
            except (TypeError, ValueError):
                current_volume = 80
        current_volume = max(0, min(100, current_volume))
        self.sound_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.sound_volume_slider.setRange(0, 100)
        self.sound_volume_slider.setValue(current_volume)
        self.sound_volume_value_label = QLabel(f"{current_volume}%")
        self.sound_volume_card = SettingCard(
            FluentIcon.VOLUME,
            self.tr('sound_volume'),
            f"{current_volume}%",
            parent=self,
        )
        self.sound_volume_card.hBoxLayout.addWidget(
            self.sound_volume_value_label,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.sound_volume_card.hBoxLayout.addSpacing(6)
        self.sound_volume_card.hBoxLayout.addWidget(
            self.sound_volume_slider,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        self.sound_volume_card.hBoxLayout.addSpacing(16)
        self.sound_volume_slider.valueChanged.connect(
            lambda v: (self.sound_volume_value_label.setText(f"{v}%"), self.sound_volume_card.setContent(f"{v}%"))
        )
        sound_group.addSettingCard(self.sound_volume_card)

        def _sync_volume_enabled():
            enabled = self.enable_sound_card.isChecked()
            self.sound_volume_slider.setEnabled(enabled)
            self.sound_volume_value_label.setEnabled(enabled)
        self.enable_sound_card.checkedChanged.connect(lambda _: _sync_volume_enabled())
        _sync_volume_enabled()
        
        current_sound = self.parent_window.settings.get("sound_file", "")
        display_name = os.path.basename(current_sound) if current_sound and os.path.exists(current_sound) else self.tr('no_sound_file')
        self.sound_file_card = PushSettingCard(
            self.tr('choose_sound'),
            FluentIcon.MUSIC_FOLDER,
            self.tr('sound_file'),
            display_name,
            parent=self,
        )
        self.sound_file_card.clicked.connect(self.choose_sound_file)
        sound_group.addSettingCard(self.sound_file_card)
        
        action_container = QWidget()
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(6)
        folder_btn = QPushButton(self.tr('open_folder'))
        folder_btn.clicked.connect(self.open_sound_folder)
        test_btn = QPushButton(self.tr('test_sound'))
        test_btn.clicked.connect(self.test_sound)
        random_btn = QPushButton('随机' if self.tr('quit') == '退出' else 'Random')
        random_btn.clicked.connect(self.random_sound)
        action_layout.addWidget(folder_btn)
        action_layout.addWidget(test_btn)
        action_layout.addWidget(random_btn)
        action_card = SettingCard(
            FluentIcon.MUSIC,
            self.tr('sound_folder'),
            None,
            parent=self,
        )
        action_card.hBoxLayout.addWidget(
            action_container,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        action_card.hBoxLayout.addSpacing(16)
        sound_group.addSettingCard(action_card)
        layout.addWidget(sound_group)
        
        shortcut_group = SettingCardGroup(self.tr('shortcuts'), widget)
        current_shortcuts = dict(DEFAULT_SHORTCUTS)
        current_shortcuts.update(self.parent_window.settings.get('shortcuts', {}))
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
            editor = QKeySequenceEdit()
            try:
                editor.setKeySequence(QKeySequence(current_shortcuts.get(skey, DEFAULT_SHORTCUTS[skey])))
            except Exception:
                editor.setKeySequence(QKeySequence(DEFAULT_SHORTCUTS[skey]))
            card = SettingCard(
                FluentIcon.COMMAND_PROMPT,
                label_text,
                None,
                parent=self,
            )
            card.hBoxLayout.addWidget(
                editor,
                0,
                Qt.AlignmentFlag.AlignRight,
            )
            card.hBoxLayout.addSpacing(16)
            shortcut_group.addSettingCard(card)
            self.shortcut_edits[skey] = editor

        hint_text = self.tr('shortcut_edit_hint') if 'shortcut_edit_hint' in LANGUAGES.get(self.parent_window.settings.get('language', 'zh_CN'), {}) else '提示：点击后按下组合键（如 Ctrl+Space）。'
        hint_card = SettingCard(
            FluentIcon.INFO,
            self.tr('shortcuts'),
            hint_text,
            parent=self,
        )
        shortcut_group.addSettingCard(hint_card)
        layout.addWidget(shortcut_group)

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
        
    def on_mode_changed(self, mode):
        """模式改变时的处理"""
        is_countdown = self.tr('countdown_mode') in mode or '倒计时' in mode
        is_clock = self.tr('clock_mode') in mode or '时钟' in mode
        
        self.countdown_widget.setVisible(is_countdown)
        self.clock_widget.setVisible(is_clock)
        
    def choose_font(self):
        """选择字体"""
        current_family = self.parent_window.settings.get("font_family", "Consolas")
        current_size = self.parent_window.settings.get("font_size", 96)

        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("choose_font"))

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        family_combo = QComboBox()
        families = QFontDatabase.families()
        family_combo.addItems(families)
        if current_family in families:
            family_combo.setCurrentText(current_family)

        size_spin = QSpinBox()
        size_spin.setRange(6, 200)
        size_spin.setValue(current_size)

        form.addRow(QLabel(self.tr("font")), family_combo)
        form.addRow(QLabel(self.tr("font_size")), size_spin)
        layout.addLayout(form)

        button_layout = QHBoxLayout()
        ok_btn = PrimaryPushButton(self.tr("ok"))
        cancel_btn = QPushButton(self.tr("cancel"))
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.parent_window.settings["font_family"] = family_combo.currentText()
            self.parent_window.settings["font_size"] = size_spin.value()
            if hasattr(self, "font_card"):
                self.font_card.setContent(
                    f"{family_combo.currentText()} · {size_spin.value()}px"
                )
            
    def choose_text_color(self):
        """选择文字颜色"""
        color = self._pick_color(
            self.tr("text_color"),
            self.parent_window.settings.get("text_color", "#E0E0E0"),
        )
        if color is not None and color.isValid():
            self.parent_window.settings["text_color"] = color.name()
            self.update_color_button(self.text_color_btn, color.name())
            if hasattr(self, 'text_color_card'):
                self.text_color_card.setContent(color.name())
            
    def choose_bg_color(self):
        """选择背景颜色"""
        color = self._pick_color(
            self.tr("bg_color"),
            self.parent_window.settings.get("bg_color", "#1E1E1E"),
        )
        if color is not None and color.isValid():
            self.parent_window.settings["bg_color"] = color.name()
            self.update_color_button(self.bg_color_btn, color.name())
            if hasattr(self, 'bg_color_card'):
                self.bg_color_card.setContent(color.name())

    def _set_theme_color(self, hex_color: str) -> None:
        self.parent_window.settings["theme_color"] = hex_color
        if hasattr(self, 'theme_color_btn'):
            self.update_color_button(self.theme_color_btn, hex_color)
        if hasattr(self, 'theme_color_card'):
            self.theme_color_card.setContent(hex_color)
            
    def choose_theme_color(self):
        """选择主题色"""
        color = self._pick_color(
            self.tr("theme_color"),
            self.parent_window.settings.get("theme_color", "#0078D4"),
        )
        if color is not None and color.isValid():
            self._set_theme_color(color.name())
            
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
            
            if hasattr(self, "sound_file_card"):
                self.sound_file_card.setContent(os.path.basename(file_path))
            
    def open_sound_folder(self):
        """打开铃声文件夹"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        base_path = self._base_path()
        
        sound_dir = os.path.join(base_path, 'sounds')
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            self._notify(
                self.tr('sound_folder_created'),
                self.tr('sound_folder_created_msg'),
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
            self._notify(
                "错误",
                f"无法打开文件夹: {sound_dir}\n请手动打开该路径。",
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
            if hasattr(self, "sound_file_card"):
                self.sound_file_card.setContent(os.path.basename(selected_sound))
            # 播放选中的铃声
            self.parent_window.play_sound(selected_sound)
        else:
            self._notify(
                self.tr('no_sound_files_found'),
                self.tr('no_sound_files_msg'),
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
            self._notify(msg_text, msg_detail)
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
        self.parent_window.settings["night_mode"] = self.night_mode_card.isChecked()
        self.parent_window.settings["timer_mode"] = self.mode_combo.currentText()
        # 保存语言无关的键
        self.parent_window.settings["timer_mode_key"] = {0: 'countup', 1: 'countdown', 2: 'clock'}.get(self.mode_combo.currentIndex(), 'countdown')
        self.parent_window.settings["countdown_hours"] = self.hours_spin.value()
        self.parent_window.settings["countdown_minutes"] = self.minutes_spin.value()
        self.parent_window.settings["countdown_seconds"] = self.seconds_spin.value()
        action_key = self.countdown_action.currentData()
        if action_key not in ('beep', 'flash', 'beep_flash'):
            action_key = 'beep'
        self.parent_window.settings["countdown_action_key"] = action_key
        self.parent_window.settings["countdown_action"] = self.countdown_action.currentText()
        # 时间格式：索引0为24小时制，1为12小时制
        self.parent_window.settings["clock_format_24h"] = (self.clock_format_combo.currentIndex() == 0)
        self.parent_window.settings["clock_show_seconds"] = self.clock_seconds_card.isChecked()
        self.parent_window.settings["clock_show_date"] = self.clock_date_card.isChecked()
        self.parent_window.settings["clock_show_am_pm"] = self.clock_am_pm_card.isChecked()
        self.parent_window.settings["clock_am_pm_style"] = 'en' if self.am_pm_style_combo.currentIndex() == 0 else 'zh'
        self.parent_window.settings["clock_am_pm_position"] = 'before' if self.am_pm_pos_combo.currentIndex() == 0 else 'after'
        self.parent_window.settings["language"] = "zh_CN" if self.lang_combo.currentText() == "简体中文" else "en_US"
        self.parent_window.settings["auto_start_timer"] = self.auto_start_card.isChecked()
        self.parent_window.settings["rounded_corners"] = self.rounded_card.isChecked()
        self.parent_window.settings["corner_radius"] = self.radius_spin.value()
        self.parent_window.settings["enable_sound"] = self.enable_sound_card.isChecked()
        self.parent_window.settings["enable_popup"] = self.enable_popup_card.isChecked()
        self.parent_window.settings["sound_volume"] = self.sound_volume_slider.value()
        self.parent_window.settings["enable_windows_toast"] = self.enable_toast_card.isChecked()
        theme_mode = self.theme_mode_combo.currentData()
        if theme_mode not in ("auto", "light", "dark"):
            theme_mode = "auto"
        self.parent_window.settings["theme_mode"] = theme_mode
        self.parent_window.settings["theme_color"] = self.parent_window.settings.get(
            "theme_color", "#0078D4"
        )
        
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
        self._applied_once = True
        
    def accept_settings(self):
        """确定设置（带快捷键冲突检测）"""
        # 先验证快捷键
        if not self._validate_shortcuts():
            return  # 有冲突，不保存
        self.apply_settings()
        self.accept()

    def reject(self):
        if not getattr(self, "_applied_once", False):
            self.parent_window.settings["language"] = self._initial_lang_code
            self.parent_window.apply_settings(preserve_elapsed=True)
            self.parent_window.create_tray_menu()
            try:
                self.parent_window.reload_shortcuts()
            except Exception:
                pass
        super().reject()


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

        button_layout = QHBoxLayout()
        ok_btn = PrimaryPushButton(self._tr('ok'))
        cancel_btn = QPushButton(self._tr('cancel'))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def accept(self):
        name = self.primary_edit.text().strip()
        total_seconds = (
            self.hours_spin.value() * 3600
            + self.minutes_spin.value() * 60
            + self.seconds_spin.value()
        )
        if total_seconds <= 0:
            MessageBox(self._tr('preset_error_title'), self._tr('preset_error_duration'), self).exec()
            return
        raw_labels = self._initial.get('labels')
        existing_labels: dict = raw_labels if isinstance(raw_labels, dict) else {}
        existing_primary = existing_labels.get(self._current_lang)
        has_existing_primary = isinstance(existing_primary, str) and existing_primary.strip()
        if not name and not self._allow_auto_name and not has_existing_primary and not self.secondary_toggle.isChecked():
            MessageBox(self._tr('preset_error_title'), self._tr('preset_error_name'), self).exec()
            return
        labels = {}
        if name:
            labels[self._current_lang] = name
        if self.secondary_toggle.isChecked():
            alt_name = self.secondary_edit.text().strip()
            if not alt_name:
                MessageBox(self._tr('preset_error_title'), self._tr('preset_error_name'), self).exec()
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
            MessageBox(self._tr('preset_error_title'), self._tr('preset_error_name'), self).exec()
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
