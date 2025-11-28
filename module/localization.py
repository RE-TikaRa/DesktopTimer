import json
import os
from typing import Dict

from .paths import get_base_path


def _load_lang_json(code: str) -> Dict[str, str]:
    try:
        base_path = get_base_path()
        lang_path = os.path.join(base_path, 'lang', f'{code}.json')
        with open(lang_path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as exc:  # pragma: no cover - debug helper
        print(f'[i18n] 读取语言文件失败 {code}: {exc}')
        return {}


LANGUAGES = {
    'zh_CN': _load_lang_json('zh_CN'),
    'en_US': _load_lang_json('en_US'),
}


class L18n:
    def __init__(self, lang_code: str = 'zh_CN'):
        self.lang_code = lang_code
        self.translations: Dict[str, str] = {}
        self.load(lang_code)

    def load(self, lang_code: str) -> None:
        base_path = get_base_path()
        lang_path = os.path.join(base_path, 'lang', f'{lang_code}.json')
        try:
            with open(lang_path, 'r', encoding='utf-8') as fh:
                self.translations = json.load(fh)
        except Exception as exc:
            print(f"语言包加载失败: {exc}")
            self.translations = {}

    def tr(self, key: str) -> str:
        return self.translations.get(key, key)
