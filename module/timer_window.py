import json
import logging
import os
import random
import uuid

from PyQt6.QtCore import QPoint, Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QFont, QIcon, QKeySequence, QIntValidator, QShortcut
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLineEdit,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
)
from qfluentwidgets import FluentStyleSheet, Theme, setTheme, setThemeColor

try:
    from win10toast import ToastNotifier

    toaster = ToastNotifier()
except ImportError:
    toaster = None

from .constants import DEFAULT_COUNTDOWN_PRESETS, DEFAULT_SHORTCUTS, TimerConstants
from .localization import L18n
from .paths import get_base_path
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)


def _clamp_int(value, min_value, max_value):
    """简单的整型裁剪助手"""
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        ivalue = min_value
    return max(min_value, min(max_value, ivalue))


class CustomCountdownDialog(QDialog):
    """自定义倒计时对话框（独立输入时/分/秒）"""

    def __init__(self, parent, translator):
        super().__init__(parent)
        self._tr = translator
        self.setWindowTitle(self._tr('custom_countdown_title'))
        self.setModal(True)
        self.setMinimumWidth(320)
        layout = QVBoxLayout()

        hint_label = QLabel(self._tr('custom_countdown_hint'))
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        self.hours_edit = self._build_input_row(layout, self._tr('hours'), default='0')
        self.minutes_edit = self._build_input_row(layout, self._tr('minutes'), default='25')
        self.seconds_edit = self._build_input_row(layout, self._tr('seconds'), default='0')

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _build_input_row(self, parent_layout, label_text, default='0'):
        row = QHBoxLayout()
        label = QLabel(f"{label_text}:")
        edit = QLineEdit()
        edit.setText(default)
        edit.setValidator(QIntValidator(0, 99, self))
        edit.setMaximumWidth(100)
        row.addWidget(label)
        row.addWidget(edit)
        row.addStretch()
        parent_layout.addLayout(row)
        return edit

    def get_values(self):
        try:
            hours = int(self.hours_edit.text() or 0)
            minutes = int(self.minutes_edit.text() or 0)
            seconds = int(self.seconds_edit.text() or 0)
        except ValueError:
            return None
        return hours, minutes, seconds

    def accept(self):
        values = self.get_values()
        if not values:
            QMessageBox.warning(self, self._tr('custom_countdown_title'), self._tr('custom_countdown_invalid'))
            return
        h, m, s = values
        if h == 0 and m == 0 and s == 0:
            QMessageBox.warning(self, self._tr('custom_countdown_title'), self._tr('custom_countdown_invalid'))
            return
        super().accept()


class TimerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 计算基础路径（一次性，避免重复）
        self.base_path = get_base_path()
        
        self.l18n = L18n(lang_code=self.get_language())
        self._current_language = self.l18n.lang_code
        self.load_settings()
        self._last_theme_state = None
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
            logger.debug("enforce startup mode failed: %s", _e)
        self.elapsed_seconds = 0
        self.is_running = self.settings.get("auto_start_timer", False)
        self.is_flashing = False
        self.is_locked = False  # 窗口锁定状态
        self.is_fullscreen = False  # ȫ��״̬
        self._stored_geometry = None
        self._stored_window_flags = None
        self.last_displayed_text = ""  # 缓存上一次显示的文本，用于优化窗口大小调整
        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(0.8)
        self.media_player = QMediaPlayer(self)
        self.media_player.setAudioOutput(self.audio_output)
        
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

    @staticmethod
    def derive_action_key(action_text):
        if not isinstance(action_text, str):
            return 'beep'
        if action_text in ('beep', 'flash', 'beep_flash'):
            return action_text
        text_lower = action_text.lower()
        has_beep = (
            'beep' in text_lower
            or 'sound' in text_lower
            or '提示音' in action_text
            or '铃声' in action_text
        )
        has_flash = 'flash' in text_lower or '闪烁' in action_text
        if has_beep and has_flash:
            return 'beep_flash'
        if has_flash:
            return 'flash'
        return 'beep'
        
    def get_language(self):
        """从设置获取语言代码"""
        try:
            settings_path = self.get_resource_path("settings", "timer_settings.json")
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings.get('language', 'zh_CN')
        except Exception:
            return 'zh_CN'
        
    def tr(self, sourceText: str, disambiguation: str | None = None, n: int = -1) -> str:  # type: ignore[override]
        _ = disambiguation
        _ = n
        return self.l18n.tr(sourceText)
    
    def _ensure_language(self):
        desired_lang = self.settings.get('language', 'zh_CN')
        if desired_lang != getattr(self.l18n, 'lang_code', None):
            try:
                self.l18n.load(desired_lang)
                self._current_language = desired_lang
            except Exception as exc:
                logger.warning("Failed to switch language to %s: %s", desired_lang, exc)
        
    def load_settings(self):
        """加载设置"""
        settings_dir = self.get_resource_path("settings")
        self.settings_file = os.path.join(settings_dir, "timer_settings.json")
        # 调试：打印设置文件路径
        logger.debug("settings file: %s", self.settings_file)
        
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
            "countdown_action": "beep",
            "countdown_action_key": "beep",  # 可选: 'beep' | 'flash' | 'beep_flash'
            # 音效文件设置
            "sound_file": "sounds/Alarm01.wav",  # 默认音效
            "sound_volume": 80,
            "enable_windows_toast": True,
            "theme_mode": "auto",
            "theme_color": "#0078D4",
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
            # 倒计时预设
            "countdown_presets": [dict(preset) for preset in DEFAULT_COUNTDOWN_PRESETS],
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.debug(
                    "loaded timer_mode_key=%s timer_mode=%s",
                    self.settings.get('timer_mode_key'),
                    self.settings.get('timer_mode'),
                )
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
                # 兼容旧版本：倒计时动作键
                action_key = self.settings.get("countdown_action_key")
                if action_key not in ('beep', 'flash', 'beep_flash'):
                    self.settings["countdown_action_key"] = self.derive_action_key(
                        self.settings.get("countdown_action", "")
                    )
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
                                logger.info("Converted absolute sound path to relative: %s", rel_path)
                        except (ValueError, OSError):
                            # 转换失败，保持原样
                            pass
            except Exception:
                logger.exception("failed to load settings, fallback to defaults")
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

        presets_normalized, presets_changed = self._normalize_countdown_presets(
            self.settings.get('countdown_presets')
        )
        self.settings['countdown_presets'] = presets_normalized
        if presets_changed:
            try:
                self.save_settings(immediate=True)
            except Exception:
                pass
        
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

        theme_mode = self.settings.get("theme_mode", "auto")
        if theme_mode not in ("auto", "light", "dark"):
            self.settings["theme_mode"] = "auto"
            fixed = True

        theme_color = self.settings.get("theme_color", "#0078D4")
        if not isinstance(theme_color, str) or not theme_color.startswith('#') or len(theme_color) != 7:
            self.settings["theme_color"] = "#0078D4"
            fixed = True
                
        # 验证语言设置
        language = self.settings.get("language")
        if language not in ('zh_CN', 'en_US'):
            self.settings["language"] = 'zh_CN'
            fixed = True

        # 验证倒计时动作键
        action_key = self.settings.get("countdown_action_key")
        if action_key not in ('beep', 'flash', 'beep_flash'):
            self.settings["countdown_action_key"] = self.derive_action_key(
                self.settings.get("countdown_action", "")
            )
            fixed = True

        # 验证音量
        volume = self.settings.get("sound_volume", 80)
        if not isinstance(volume, int) or not 0 <= volume <= 100:
            self.settings["sound_volume"] = 80
            fixed = True

        # 验证 Windows 通知开关
        if not isinstance(self.settings.get("enable_windows_toast", True), bool):
            self.settings["enable_windows_toast"] = True
            fixed = True
            
        # 验证启动模式行为
        startup_behavior = self.settings.get("startup_mode_behavior")
        if startup_behavior not in ('restore', 'fixed'):
            self.settings["startup_mode_behavior"] = 'restore'
            fixed = True

        # 如果修正了任何设置,立即保存
        if fixed:
            logger.info("Detected invalid settings values, auto corrected.")
            self.save_settings(immediate=True)

    def _default_countdown_presets(self):
        return [dict(preset) for preset in DEFAULT_COUNTDOWN_PRESETS]

    def _normalize_countdown_presets(self, presets):
        """确保倒计时预设结构合法"""
        source = presets if isinstance(presets, list) else []
        normalized = []
        changed = False

        if not source:
            source = self._default_countdown_presets()
            changed = True

        seen_ids = set()
        current_lang = self.settings.get('language', 'zh_CN')
        for entry in source:
            if not isinstance(entry, dict):
                changed = True
                continue

            preset_id = entry.get('id')
            if not isinstance(preset_id, str) or not preset_id.strip():
                preset_id = f"preset_{uuid.uuid4().hex[:8]}"
                changed = True
            if preset_id in seen_ids:
                preset_id = f"{preset_id}_{uuid.uuid4().hex[:4]}"
                changed = True
            seen_ids.add(preset_id)

            hours = _clamp_int(entry.get('hours', 0), 0, 99)
            minutes = _clamp_int(entry.get('minutes', 0), 0, 59)
            seconds = _clamp_int(entry.get('seconds', 0), 0, 59)

            labels = self._clean_labels(entry.get('labels'))

            name_key = entry.get('name_key')
            if isinstance(name_key, str):
                name_key = name_key.strip()
            else:
                name_key = None

            single_label = entry.get('label')
            if isinstance(single_label, str) and single_label.strip():
                stripped = single_label.strip()
                labels.setdefault(current_lang, stripped)

            label_value = labels.get(current_lang)
            if not label_value and labels:
                # fallback to any existing label
                label_value = next(iter(labels.values()))

            normalized.append({
                'id': preset_id,
                'mode': 'countdown',
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                **({'label': label_value} if label_value else {}),
                **({'labels': labels} if labels else {}),
                **({'name_key': name_key} if name_key else {}),
            })

        if not normalized:
            normalized = self._default_countdown_presets()
            changed = True

        return normalized, changed

    def ensure_presets_normalized(self):
        normalized, changed = self._normalize_countdown_presets(
            self.settings.get('countdown_presets')
        )
        if changed:
            self.settings['countdown_presets'] = normalized
        return changed

    def _format_preset_duration(self, preset):
        hours = _clamp_int(preset.get('hours', 0), 0, 99)
        minutes = _clamp_int(preset.get('minutes', 0), 0, 59)
        seconds = _clamp_int(preset.get('seconds', 0), 0, 59)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _format_duration_text(self, preset):
        hours = _clamp_int(preset.get('hours', 0), 0, 99)
        minutes = _clamp_int(preset.get('minutes', 0), 0, 59)
        seconds = _clamp_int(preset.get('seconds', 0), 0, 59)
        lang_code = self.settings.get('language', 'zh_CN')
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

    def _get_label_for_language(self, preset, lang_code):
        labels = self._clean_labels(preset.get('labels'))
        if labels:
            if lang_code in labels and labels[lang_code]:
                return labels[lang_code]
            lang_short = lang_code.split('_')[0]
            for key, value in labels.items():
                if key.split('_')[0] == lang_short and value:
                    return value
            # fallback to任一语言
            first = next(iter(labels.values()), None)
            if first:
                return first
        label = preset.get('label')
        if isinstance(label, str) and label.strip():
            return label.strip()
        return None

    @staticmethod
    def _clean_labels(raw_labels):
        labels = {}
        if isinstance(raw_labels, dict):
            for lang_code, text in raw_labels.items():
                if not isinstance(lang_code, str):
                    continue
                if isinstance(text, str):
                    stripped = text.strip()
                    if stripped:
                        labels[lang_code] = stripped
        return labels

    def _resolve_preset_label(self, preset):
        lang_code = self.settings.get('language', 'zh_CN')
        label = self._get_label_for_language(preset, lang_code)
        if label:
            return label
        name_key = preset.get('name_key')
        if name_key:
            translated = self.tr(name_key)
            if translated and translated != name_key:
                return translated
        return self._format_duration_text(preset)

    def prompt_custom_countdown(self):
        """一次性自定义倒计时"""
        dialog = CustomCountdownDialog(self, self.tr)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parsed = dialog.get_values()
        if not parsed:
            QMessageBox.warning(self, self.tr('custom_countdown_title'), self.tr('custom_countdown_invalid'))
            return
        hours, minutes, seconds = parsed
        hours = _clamp_int(hours, 0, 99)
        minutes = _clamp_int(minutes, 0, 59)
        seconds = _clamp_int(seconds, 0, 59)
        if hours == 0 and minutes == 0 and seconds == 0:
            QMessageBox.warning(self, self.tr('custom_countdown_title'), self.tr('custom_countdown_invalid'))
            return
        self.quick_countdown(hours, minutes, seconds)
    
    def save_settings(self, immediate=False):
        """
        延迟保存设置（防抖动）
        
        Args:
            immediate: 是否立即保存，跳过延迟机制
        """
        if immediate:
            # 立即保存
            self._pending_save = True
            self._save_timer.stop()
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

        self.ensure_presets_normalized()

        try:
            # 确保 settings 目录存在
            settings_dir = os.path.dirname(self.settings_file)
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            self._pending_save = False
            logger.debug("Settings saved.")
        except Exception as e:
            logger.error("Failed to save settings: %s", e)
    
    def ensure_sounds_folder(self):
        """确保sounds文件夹存在，并随机选择铃声"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        base_path = self.base_path
        
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
                logger.debug("Random sound selected: %s", os.path.basename(selected_sound))
    
    def get_sound_files(self):
        """获取sounds文件夹中的所有音频文件"""
        # 获取 exe 所在目录（打包后）或脚本所在目录（开发时）
        base_path = self.base_path
        
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
            logger.error("Failed to read sounds folder: %s", e)
        
        return sound_files
            
    def play_sound(self, sound_file):
        """播放铃声（停止旧音效后播放新音效）"""
        try:
            # 停止当前播放的音效
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.stop()

            if os.path.exists(sound_file):
                url = QUrl.fromLocalFile(sound_file)
                self.media_player.setSource(url)
                self.media_player.play()
            else:
                logger.warning("Sound file not found: %s", sound_file)
                QApplication.beep()
        except Exception as e:
            logger.error("Failed to play sound: %s", e)
            QApplication.beep()
    
    def init_ui(self):
        """初始化主窗口"""
        # 设置窗口属性
        self.setWindowTitle(self.tr('app_name'))
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |  # 窗口置顶
            Qt.WindowType.FramelessWindowHint |    # 无边框
            Qt.WindowType.Tool                      # 工具窗口
        )
        self._stored_window_flags = self.windowFlags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        
        # 创建时间显示标签
        self.time_label = QLabel('00:00:00', self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.geometry()
        
        # 计算居中位置
        x = (geometry.width() - self.width()) // 2
        y = (geometry.height() - self.height()) // 2
        
        # 移动窗口到居中位置
        self.move(max(0, x), max(0, y))
        
    def apply_settings(self, preserve_elapsed=False):
        """应用设置"""
        self._ensure_language()

        theme_mode = self.settings.get("theme_mode", "auto")
        if theme_mode == "light":
            theme = Theme.LIGHT
        elif theme_mode == "dark":
            theme = Theme.DARK
        else:
            theme = Theme.AUTO
        theme_color = self.settings.get("theme_color", "#0078D4")
        setThemeColor(theme_color, save=False, lazy=True)
        setTheme(theme, save=False, lazy=True)
        theme_state = (theme_mode, theme_color)
        if theme_state != getattr(self, "_last_theme_state", None):
            self._last_theme_state = theme_state
            if getattr(self, "tray_icon", None) is not None:
                self.create_tray_menu()
        # 应用字体
        font = QFont(
            self.settings.get("font_family", "Consolas"),
            self.settings.get("font_size", 96),
            QFont.Weight.Bold,
        )
        self.time_label.setFont(font)

        volume = self.settings.get("sound_volume", 80)
        if not isinstance(volume, int):
            try:
                volume = int(volume)
            except (TypeError, ValueError):
                volume = 80
        volume = max(0, min(100, volume))
        self.audio_output.setVolume(volume / 100)
        
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
        logger.debug("apply_settings with mode_key=%s", mode_key)
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
        self.setWindowTitle(self.tr('app_name'))
        
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
        
        style = self.style()
        if style is None:
            return
        self.tray_icon.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # 创建托盘菜单
        self.create_tray_menu()
        
        self.tray_icon.show()
        
        # 双击托盘图标显示/隐藏窗口
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
    def build_quick_presets_menu(self):
        """������ͼ��/�Ҽ��˵��еĿ��ٹ���˵�"""
        preset_menu = QMenu(self.tr('mode_switch_menu'), self)
        self._apply_menu_style(preset_menu)

        countup_action = QAction(self.tr('count_up_mode'), self)
        countup_action.triggered.connect(self.switch_to_count_up)
        preset_menu.addAction(countup_action)

        preset_menu.addSeparator()

        countdown_menu = QMenu(self.tr('countdown_mode'), self)
        self._apply_menu_style(countdown_menu)
        countdown_presets = self.settings.get('countdown_presets', [])
        if countdown_presets:
            for preset in countdown_presets:
                duration = self._format_preset_duration(preset)
                label = self._resolve_preset_label(preset)
                action = QAction(label, self)
                action.setToolTip(duration)
                hours = _clamp_int(preset.get('hours', 0), 0, 99)
                minutes = _clamp_int(preset.get('minutes', 0), 0, 59)
                seconds = _clamp_int(preset.get('seconds', 0), 0, 59)
                action.triggered.connect(lambda _, h=hours, m=minutes, s=seconds:
                                         self.quick_countdown(h, m, s))
                countdown_menu.addAction(action)
        else:
            placeholder = QAction(self.tr('no_presets_available'), self)
            placeholder.setEnabled(False)
            countdown_menu.addAction(placeholder)
        countdown_menu.addSeparator()
        custom_action = QAction(self.tr('custom_countdown_once'), self)
        custom_action.triggered.connect(self.prompt_custom_countdown)
        countdown_menu.addAction(custom_action)
        preset_menu.addMenu(countdown_menu)

        preset_menu.addSeparator()

        clock_action = QAction(self.tr('clock_mode'), self)
        clock_action.triggered.connect(self.switch_to_clock_mode)
        preset_menu.addAction(clock_action)

        return preset_menu
        
    def create_tray_menu(self):
        """创建托盘菜单"""
        tray_menu = QMenu()
        self._apply_menu_style(tray_menu)
        
        # 开始/暂停动作
        pause_text = self.tr('pause') if self.is_running else self.tr('continue')
        self.pause_action = QAction(pause_text, self)
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
                logger.warning("Failed to bind shortcut %s: %s", seq_str, _e)

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
            logger.debug("update_time: mode_key=%s", mode_key)
            self._dbg_printed = True
        if mode_key == 'clock':
            from PyQt6.QtCore import QDateTime
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
        action_key = self.settings.get("countdown_action_key")
        if action_key not in ('beep', 'flash', 'beep_flash'):
            action_key = self.derive_action_key(self.settings.get("countdown_action", ""))
            self.settings["countdown_action_key"] = action_key
        
        # 播放铃声
        if self.settings.get("enable_sound", True) and action_key in ("beep", "beep_flash"):
            sound_file = self.settings.get("sound_file", "")
            if sound_file:
                # 如果是相对路径，转换为绝对路径
                if not os.path.isabs(sound_file):
                    base_path = self.base_path
                    sound_file = os.path.join(base_path, sound_file)
                
                if os.path.exists(sound_file):
                    self.play_sound(sound_file)
                else:
                    # 如果文件不存在，播放系统提示音
                    QApplication.beep()
            else:
                # 如果没有自定义铃声，播放系统提示音
                QApplication.beep()
        
        # 闪烁提醒
        if action_key in ("flash", "beep_flash"):
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
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            
            # 确保窗口可见
            if not self.isVisible():
                self.show()
            
            # 显示弹窗
            msg.exec()
        else:
            # 如果不使用弹窗，显示托盘通知
            self.tray_icon.showMessage(
                self.tr('countdown_finished'),
                self.tr('countdown_finished_msg'),
                QSystemTrayIcon.MessageIcon.Information,
                TimerConstants.NOTIFICATION_DURATION_SHORT * 1000
            )
            
            # 确保窗口可见
            if not self.isVisible():
                self.show()
        
        # Windows原生通知
        if self.settings.get("enable_windows_toast", True) and toaster:
            try:
                toaster.show_toast(
                    "DesktopTimer",  # 通知标题
                    self.tr('countdown_finished') + "\n" + self.tr('countdown_finished_msg'),
                    duration=TimerConstants.NOTIFICATION_DURATION_LONG,
                    threaded=True
                )
            except Exception as e:
                logger.warning("Windows toast failed: %s", e)
        
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
                QSystemTrayIcon.MessageIcon.Information,
                TimerConstants.TRAY_MESSAGE_DURATION
            )
        else:
            self.pause_action.setText(self.tr('continue'))
            self.tray_icon.showMessage(
                self.tr('app_name'),
                self.tr('timer_paused'),
                QSystemTrayIcon.MessageIcon.Information,
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
            QSystemTrayIcon.MessageIcon.Information,
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
            QSystemTrayIcon.MessageIcon.Information,
            1000
        )
        
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
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
        restore_flags = self._stored_window_flags or (
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        )
        self.setWindowFlags(restore_flags)
        self.showNormal()
        if self._stored_geometry is not None:
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
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_visibility()
    
    def toggle_lock(self):
        """切换窗口锁定状态"""
        self.is_locked = not self.is_locked
        
        if self.is_locked:
            # 锁定：只设置鼠标事件穿透，保留键盘事件以便快捷键仍然有效
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.tray_icon.showMessage(
                self.tr('app_name'),
                self.tr('window_locked'),
                QSystemTrayIcon.MessageIcon.Information,
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
                    logger.warning("Windows toast failed: %s", e)
        else:
            # 解锁：恢复窗口交互
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            
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
                    logger.warning("Windows toast failed: %s", e)
            else:
                # 如果没有 Windows 通知，使用托盘通知
                self.tray_icon.showMessage(
                    self.tr('app_name'),
                    self.tr('window_unlocked'),
                    QSystemTrayIcon.MessageIcon.Information,
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
                if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                    self.media_player.stop()
                self.media_player.deleteLater()
            if hasattr(self, 'audio_output') and self.audio_output:
                self.audio_output.deleteLater()
            
            # 保存设置（立即保存，不延迟）
            self.save_settings(immediate=True)
            
            # 隐藏托盘图标
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
        except Exception as e:
            logger.error("Failed to clean up resources: %s", e)
        finally:
            QApplication.quit()
        
    def mousePressEvent(self, a0):
        """鼠标按下事件 - 用于拖动窗口"""
        if a0 is None:
            return
        event = a0
        if event.button() == Qt.MouseButton.LeftButton and not self.is_locked and not self.is_fullscreen:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.pos()
            
    def mouseMoveEvent(self, a0):
        """鼠标移动事件 - 用于拖动窗口"""
        if a0 is None:
            return
        event = a0
        if self.dragging and not self.is_locked and not self.is_fullscreen:
            self.move(event.globalPosition().toPoint() - self.offset)
            
    def mouseReleaseEvent(self, a0):
        """鼠标释放事件 - 停止拖动"""
        if a0 is None:
            return
        event = a0
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        if event is None:
            return
        menu = QMenu(self)
        self._apply_menu_style(menu)
        
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
        
        menu.exec(event.globalPos())

    def _apply_menu_style(self, menu: QMenu) -> None:
        FluentStyleSheet.MENU.apply(menu)
        menu.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
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
            
    def closeEvent(self, a0):
        """关闭事件 - 最小化到托盘而不是退出"""
        if a0 is None:
            return
        event = a0
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            self.tr('app_name'),
            self.tr('minimized_to_tray'),
            QSystemTrayIcon.MessageIcon.Information,
            TimerConstants.TRAY_MESSAGE_DURATION
        )
        
    def update_tray_icon(self):
        """根据当前状态更新托盘图标（Qt标准图标）"""
        try:
            tray = getattr(self, 'tray_icon', None)
            if tray is None:
                return
            style = self.style()
            if style is None:
                return
            # 优先：在倒计时完成的闪烁阶段，显示信息图标
            if getattr(self, 'is_flashing', False):
                icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
            else:
                if getattr(self, 'is_running', False):
                    icon = style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
                else:
                    # 未运行，区分是否已归零
                    if getattr(self, 'elapsed_seconds', 0) == 0:
                        icon = style.standardIcon(QStyle.StandardPixmap.SP_MediaStop)
                    else:
                        icon = style.standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            tray.setIcon(icon)
        except Exception as e:
            logger.warning("Failed to update tray icon: %s", e)

    def showEvent(self, a0):
        """窗口显示时更新托盘图标"""
        event = a0
        super().showEvent(event)
        self.update_tray_icon()
