# AGENTS 指南

## 项目速览
- **DesktopTimer 2.0.0**：PyQt6 桌面计时器（设置页基于 PyQt6-Fluent-Widgets），入口 `main.py → module.app.main() → TimerWindow`。
- 支持 Windows 10/11 & Python 3.13，提供正计时/倒计时/时钟模式、托盘常驻、快捷键、自定义外观与多语言（`lang/zh_CN.json`、`lang/en_US.json`）。
- 运行态配置写入 `settings/timer_settings.json`，加载时会与 `DEFAULT_SHORTCUTS`、`DEFAULT_COUNTDOWN_PRESETS` 等默认值合并并做合法性校验。
- 许可证：DesktopTimer Non-Commercial License 1.0（DNCL-1.0），商用需作者授权。

## 目录速查
```
DesktopTimer/
├── main.py                 # 程序入口
├── module/
│   ├── app.py              # QApplication + Translator + TimerWindow
│   ├── timer_window.py     # 主窗口/计时逻辑/托盘/提醒/快捷键
│   ├── settings_dialog.py  # 设置面板（外观/模式/预设/通用/关于）
│   ├── constants.py        # APP_VERSION、默认快捷键/预设、计时常量
│   ├── localization.py     # 语言加载 & L18n.tr()
│   └── paths.py            # sys.frozen 判定 + 资源基路径
├── lang/                   # 多语言 JSON
├── img/                    # 图标资源
├── sounds/                 # 默认铃声
├── settings/               # 用户配置（timer_settings.json）
├── DesktopTimer.spec       # PyInstaller 脚本
├── pyproject.toml          # UV 项目配置
├── uv.lock                 # UV 锁文件
├── tools/                  # 构建/打包脚本
└── README.md / requirements.txt
```

## 核心逻辑要点
- **TimerWindow**
  - `get_resource_path()` 统一定位资源，兼容开发与 PyInstaller onefile。
  - 设置生命周期：`load_settings()` → `_normalize_countdown_presets()` / `_validate_and_fix_settings()` → `apply_settings()`，延迟写入由 `save_settings()` + `_do_save_settings()` 控制。
  - 托盘：`build_quick_presets_menu()` 提供正/倒/时钟切换、倒计时预设列表、一次性自定义倒计时（`prompt_custom_countdown()`）。
  - 倒计时预设：`countdown_presets` 支持 `labels` 字典，按语言显示，缺省时回退到 `name_key` 或时长描述。
  - 主题：支持浅色/深色/跟随系统与主题色，菜单与托盘样式跟随主题。
  - 提醒能力：`QMediaPlayer` + `QAudioOutput` 播放音效、系统 Beep、窗口闪烁、托盘气泡、可选 `win10toast` 通知（设置页可调音量与开关）。
  - 快捷键：`DEFAULT_SHORTCUTS` + 用户自定义，`reload_shortcuts()` 用于设置变更后重绑。

- **SettingsDialog**
  - 五个 Tab（外观/模式/预设/通用/关于），通过父窗口 settings 获取/写回数据。
  - 预设 Tab 支持搜索、增删改查、拖动排序、多选删除、排序方式记忆、恢复默认；预设编辑器支持多语言名称。
  - 保存时调用 `_serialize_presets()` 写回 `countdown_presets`，随后触发 `TimerWindow.apply_settings()` 与 `reload_shortcuts()`。

- **localization.py**
  - 导入即加载 `lang/*.json`，`L18n.tr(key)` 不存在时返回 key。

- **paths.py**
  - `get_base_path()` 在打包场景返回 exe 目录，开发时返回仓库根，确保资源相对路径可移植。

## 常用命令
- 安装依赖：`uv sync`
- 运行调试：`uv run python main.py`
- 打包：先 `uv sync --dev`，再 `uv run python -m PyInstaller DesktopTimer.spec --noconfirm`；记得将 `img/ lang/ sounds/ settings/` 复制到 `dist/`
- 一键打包：`tools\pyinstaller.bat`（清理 → 同步 → 构建 → 复制资源 → 压缩）
- DEBUG 日志：运行前设置 `DESKTOPTIMER_DEBUG=1` 可输出更详细日志

## 给 AI 代理的建议
1. **改动前先读配置**：涉及设置/预设逻辑时同步更新 `settings/timer_settings.json`、`DEFAULT_COUNTDOWN_PRESETS`、语言文本，并保持旧字段兼容。
2. **保持最小改动**：沿用现有编码/排版风格，避免无关重构；如需重写，应删除旧实现防止重复路径。
3. **多语言同步**：任何新 UI 文案必须同时更新 `lang/zh_CN.json` 与 `lang/en_US.json`，并确认 `SettingsDialog.tr()` 能读取。
4. **资源路径**：通过 `get_resource_path()` 访问文件，禁止硬编码绝对路径以保证打包可用。
5. **版本一致性**：如修改 `APP_VERSION`，需同步 README、安装脚本等对版本有显示的文件。
6. **验证流程**：本地运行 `uv run python main.py` 检查托盘菜单（模式切换 / 自定义倒计时）、快捷键与设置保存；若触及打包流程需重新执行 PyInstaller。
7. **文档同步**：新功能或行为调整要更新 README 与本 AGENTS 文档，以免信息漂移。

## TODO / Backlog
- 预设导入/导出 JSON，以及更友好的批量语言编辑 UI
- 预设列表排序/搜索功能，方便管理大批量条目
- 设置对话框在关闭前提醒“语言改动需点击应用/确定”或自动保存策略
- 设置项中加入调试日志开关（不依赖环境变量）
- 替换 win10toast 或移除其 `pkg_resources` 依赖，确保未来 Python/Setuptools 版本兼容

## 维护提醒
- 优先中文描述，commit/PR 均请遵守 DNCL-1.0。
- 当前环境：Windows 11 Pro 24H2，Python 3.13.3，具备完整网络与 GPU 能力，但项目主要依赖 PyQt6。
- 打包方式：onefile + 外置资源目录（`DesktopTimer.spec` 未内置数据文件）。
- 禁止擅自还原用户已有改动；操作前可 `git status` 快速确认工作区状态。
