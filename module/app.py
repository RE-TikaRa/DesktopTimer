import json
import logging
import os
import sys

from PyQt6.QtCore import QLocale, QTranslator
from PyQt6.QtWidgets import QApplication

from .paths import get_base_path
from .timer_window import TimerWindow


def _configure_logging():
    level = logging.DEBUG if os.environ.get("DESKTOPTIMER_DEBUG") == "1" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

def _load_language_setting() -> str:
    try:
        base_path = get_base_path()
        settings_path = os.path.join(base_path, "settings", "timer_settings.json")
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get('language', 'zh_CN')
    except Exception:
        return 'zh_CN'


def main():
    _configure_logging()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序

    lang_code = _load_language_setting()
    translator = QTranslator()
    if lang_code == "zh_CN":
        if translator.load("qt_zh_CN", QApplication.applicationDirPath()):
            app.installTranslator(translator)
        elif translator.load("qtbase_zh_CN"):
            app.installTranslator(translator)
        QLocale.setDefault(QLocale(QLocale.Language.Chinese, QLocale.Country.China))
    else:
        QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

    window = TimerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
