import logging
import os
import sys

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication

from .timer_window import TimerWindow


def _configure_logging():
    level = logging.DEBUG if os.environ.get("DESKTOPTIMER_DEBUG") == "1" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main():
    _configure_logging()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序

    translator = QTranslator()
    if translator.load("qt_zh_CN", QApplication.applicationDirPath()):
        app.installTranslator(translator)
    elif translator.load("qtbase_zh_CN"):
        app.installTranslator(translator)

    QLocale.setDefault(QLocale(QLocale.Chinese, QLocale.China))

    window = TimerWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
