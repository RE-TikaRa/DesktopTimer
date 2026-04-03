# DesktopTimer 技术文档

适用版本：`2026.04.03`  
适用平台：Windows 10 / 11（源码环境要求 Python `3.13`）

## 1. 项目概述

DesktopTimer 是一个基于 `PyQt6` 的桌面计时器应用，当前支持以下三种运行模式：

- 正计时（Count Up）
- 倒计时（Countdown）
- 时钟（Clock）

应用以“常驻桌面 + 系统托盘控制”为核心交互模型，围绕以下能力展开：

- 主窗口实时显示时间
- 托盘菜单与右键菜单控制常用动作
- 设置页统一管理外观、模式、提醒、预设和快捷键
- JSON 配置持久化
- 中英文双语切换
- 外部资源目录（`img/`、`lang/`、`sounds/`）支持源码运行与打包运行两种场景

---

## 2. 技术栈

| 类别 | 选型 | 说明 |
| --- | --- | --- |
| 语言 | Python 3.13 | 项目运行语言 |
| GUI 框架 | PyQt6 | 主窗口、对话框、计时器、托盘等 |
| Fluent UI | PyQt6-Fluent-Widgets | 设置页、菜单与 Fluent 风格组件 |
| 音频播放 | QMediaPlayer + QAudioOutput | 播放提醒音 |
| Windows 通知 | win10toast | 原生 Toast 提示（可选） |
| 打包工具 | PyInstaller | 生成 `DesktopTimer.exe` |
| 安装包工具 | Inno Setup | 生成安装程序 |
| 依赖管理 | uv | 安装依赖、运行项目 |
| 代码检查 | Ruff | 静态检查与格式化 |

---

## 3. 目录结构

```text
DesktopTimer/
├── main.py
├── module/
│   ├── __init__.py
│   ├── app.py
│   ├── constants.py
│   ├── localization.py
│   ├── paths.py
│   ├── settings_dialog.py
│   └── timer_window.py
├── img/
├── lang/
├── settings/
│   └── timer_settings.json
├── sounds/
├── setup/
│   └── setup.iss
├── tools/
│   ├── Run.bat
│   ├── pyinstaller.bat
│   ├── ensure_multi_size_ico.py
│   └── update_version.py
├── DesktopTimer.spec
├── pyproject.toml
├── requirements.txt
├── README.md
└── uv.lock
```

目录职责说明：

- `main.py`：程序入口，仅负责转发到 `module.main`
- `module/`：核心业务与 UI 逻辑
- `img/`：图标与品牌资源
- `lang/`：业务层语言包（`zh_CN.json`、`en_US.json`）
- `settings/`：运行时配置文件
- `sounds/`：默认提醒音资源
- `tools/`：运行、打包、版本更新脚本
- `setup/`：Inno Setup 安装脚本

---

## 4. 运行时架构概览

运行链路可概括为：

```text
main.py
  -> module.app.main()
     -> QApplication
     -> Qt 翻译器初始化
     -> TimerWindow 创建
     -> SettingsDialog / 托盘 / 定时器 / 音频 / 快捷键
     -> 事件循环
```

从职责上可以分成四层：

1. **启动层**
   - 初始化日志
   - 读取语言设置
   - 创建 `QApplication`

2. **界面层**
   - `TimerWindow`：主窗口、托盘、计时、通知
   - `SettingsDialog`：设置页、预设管理、快捷键编辑

3. **资源与配置层**
   - `paths.py`：统一资源根目录解析
   - `localization.py`：加载业务语言包
   - `settings/timer_settings.json`：持久化用户设置

4. **发布层**
   - `DesktopTimer.spec`：PyInstaller 构建入口
   - `setup/setup.iss`：安装包定义

---

## 5. 启动流程

### 5.1 入口

`main.py` 只做一件事：

```python
from module import main as run_app
```

真正的启动逻辑位于 `module/app.py`。

### 5.2 `module/app.py`

启动过程如下：

1. `_configure_logging()`
   - 读取环境变量 `DESKTOPTIMER_DEBUG`
   - 为整个应用配置 `logging`

2. `_load_language_setting()`
   - 从 `settings/timer_settings.json` 读取 `language`
   - 若失败则默认回退到 `zh_CN`

3. `main()`
   - 创建 `QApplication`
   - 设置 `app.setQuitOnLastWindowClosed(False)`，保证关闭主窗口后应用仍可常驻托盘
   - 根据语言设置加载 Qt 自带翻译器
   - 创建并显示 `TimerWindow`
   - 进入 Qt 事件循环

---

## 6. 模块设计

### 6.1 `module/paths.py`

提供 `get_base_path()`，统一处理资源目录：

- **源码运行**：返回项目根目录
- **PyInstaller 打包运行**：返回 `exe` 所在目录

这个函数是整个项目资源定位的基础，`img/`、`lang/`、`sounds/`、`settings/` 的读取都依赖它。

### 6.2 `module/constants.py`

负责提供：

- 默认快捷键 `DEFAULT_SHORTCUTS`
- 内置倒计时预设 `DEFAULT_COUNTDOWN_PRESETS`
- 应用版本 `APP_VERSION`
- 项目地址 `PROJECT_URL`
- 定时器相关常量 `TimerConstants`

`TimerConstants` 目前主要定义：

- 主计时器刷新间隔：`1000ms`
- 闪烁间隔：`500ms`
- 闪烁总次数
- 托盘消息持续时间
- Windows 通知展示时长

### 6.3 `module/localization.py`

包含两部分：

1. 模块级加载：
   - 启动时预加载 `zh_CN` / `en_US` JSON 语言包
2. `L18n` 类：
   - 按语言码加载字典
   - 通过 `tr(key)` 返回业务翻译文本

项目采用的是 **Qt 原生翻译 + 自定义 JSON 翻译** 双通道方案：

- Qt 原生控件文本：由 `QTranslator` 负责
- 业务文案、菜单、设置项文本：由 `L18n` / `LANGUAGES` 负责

### 6.4 `module/timer_window.py`

这是项目的核心运行类，负责：

- 主窗口创建与显示
- 计时逻辑
- 系统托盘菜单
- 右键菜单
- 音频播放
- 倒计时完成提醒
- 设置加载、保存与兼容修复
- 快捷键绑定
- 窗口锁定、拖动、全屏、点击穿透

### 6.5 `module/settings_dialog.py`

负责 Fluent 风格设置页与预设编辑逻辑，内部包含：

- `SettingsDialog`
- `PresetEditorDialog`

其中 `SettingsDialog` 进一步拆成五个选项卡：

- 外观
- 计时模式
- 预设
- 通用
- 关于

---

## 7. `TimerWindow` 核心设计

### 7.1 关键状态

`TimerWindow` 内部维护的关键状态包括：

| 字段 | 作用 |
| --- | --- |
| `settings` | 当前内存中的完整配置 |
| `elapsed_seconds` | 当前计时值；倒计时时表示剩余秒数 |
| `is_running` | 计时器是否处于运行状态 |
| `is_flashing` | 是否正在执行闪烁提醒 |
| `is_locked` | 主窗口是否被锁定 |
| `is_fullscreen` | 当前是否处于全屏模式 |
| `audio_output` / `media_player` | 音频播放对象 |
| `timer` | 主刷新定时器，每秒触发一次 |
| `flash_timer` | 闪烁提醒定时器 |

### 7.2 主窗口形态

主窗口是一个极简的无边框浮窗：

- 置顶显示
- 透明背景
- 使用单个 `QLabel` 显示时间
- 支持鼠标拖动
- 支持圆角、背景透明度、字体样式调整

窗口关闭时不会退出程序，而是隐藏到系统托盘。

### 7.3 模式模型

项目已经将显示文本与逻辑状态解耦，统一通过以下键值表示模式：

- `countup`
- `countdown`
- `clock`

对应字段：

- `timer_mode`：面向 UI 的可读文本
- `timer_mode_key`：逻辑判断使用的语言无关键值

这能避免中英文切换后依赖字符串比较带来的问题。

### 7.4 设置加载与兼容修复

`load_settings()` 会先准备默认配置，再尝试读取 `settings/timer_settings.json`。

除了普通加载外，还包含兼容逻辑：

- 补全缺失字段
- 合并默认快捷键
- 从旧版文本模式推断 `timer_mode_key`
- 从旧版文本动作推断 `countdown_action_key`
- 将位于 `sounds/` 目录内的绝对路径转成相对路径
- 规范化倒计时预设结构
- 自动修正非法配置值

### 7.5 配置保存

保存分为两种方式：

- 延迟保存：普通交互时通过 `QTimer` 做 1 秒防抖
- 立即保存：用户主动确认设置、退出应用、兼容修复时立即落盘

最终由 `_do_save_settings()` 写入 `settings/timer_settings.json`。

### 7.6 计时刷新循环

主定时器由 `init_timer()` 创建，每秒执行一次 `update_time()`。

三种模式的行为如下：

#### 时钟模式

- 每秒读取当前系统时间
- 支持 12/24 小时制
- 支持显示秒
- 支持显示日期
- 支持 AM/PM 的中英文样式与前后位置控制

#### 倒计时模式

- 运行时每秒减 1
- 到达 0 后停止
- 触发 `on_countdown_finished()`

#### 正计时模式

- 运行时每秒加 1
- 使用 `HH:MM:SS` 显示

### 7.7 倒计时完成提醒

提醒行为由 `countdown_action_key` 控制：

- `beep`
- `flash`
- `beep_flash`

完成后可能触发以下动作：

1. 播放音频文件
2. 系统 Beep 兜底提醒
3. 主窗口红色闪烁
4. `QMessageBox` 弹窗
5. 托盘提示
6. Windows Toast 原生通知

音频播放依赖 `QMediaPlayer + QAudioOutput`，Windows 通知依赖 `win10toast`，并通过后台线程调用避免阻塞主 UI。

### 7.8 托盘与右键菜单

托盘菜单与主窗口右键菜单基本保持一致，主要包含：

- 暂停 / 继续
- 重置
- 模式切换
- 倒计时预设菜单
- 一次性自定义倒计时
- 打开设置
- 显示 / 隐藏窗口
- 进入 / 退出全屏
- 锁定 / 解锁窗口
- 退出应用

其中“模式切换”子菜单是当前项目的重要入口，支持：

- 切换到正计时
- 选择倒计时预设
- 使用临时自定义倒计时
- 切换到时钟模式

### 7.9 快捷键系统

主窗口在初始化时会根据配置创建 `QShortcut` 对象，支持：

- 暂停 / 继续
- 重置
- 显示 / 隐藏
- 打开设置
- 锁定 / 解锁
- 全屏切换

设置页保存后会调用 `reload_shortcuts()` 重新绑定。

### 7.10 窗口锁定与全屏

锁定能力包含两层：

- 禁止拖动
- 启用点击穿透

点击穿透通过以下方式实现：

- `WA_TransparentForMouseEvents`
- `WindowTransparentForInput`（Qt 提供时启用）

全屏切换会保存并恢复原窗口几何信息与窗口标志位，避免退出全屏后状态丢失。

### 7.11 生命周期

- `closeEvent()`：关闭主窗口时隐藏到托盘
- `quit_app()`：真正退出时停止定时器、停止音频、保存设置并隐藏托盘图标

---

## 8. `SettingsDialog` 核心设计

### 8.1 总体结构

设置页使用 `PyQt6-Fluent-Widgets` 构建，通过 `Pivot + QStackedWidget` 组织多标签页。

界面结构如下：

1. 外观
2. 计时模式
3. 预设
4. 通用
5. 关于

### 8.2 外观页

负责以下配置：

- 字体与字号
- 文字颜色
- 背景颜色
- 背景透明度
- 圆角开关与圆角半径
- 主显示字号滑块
- Fluent 主题模式
- 夜读模式

### 8.3 模式页

负责三类模式相关配置：

- 当前运行模式
- 倒计时时间
- 倒计时结束动作
- 时钟格式（12/24 小时）
- 是否显示秒
- 是否显示日期
- AM/PM 样式和显示位置

### 8.4 预设页

这是当前项目功能最复杂的设置页之一，支持：

- 搜索预设
- 预设列表展示
- 新增 / 编辑 / 删除
- 多选批量删除
- 全选 / 清空选择
- 手动排序
- 按名称排序
- 按时长排序
- 将选中预设直接应用到当前倒计时

预设编辑由 `PresetEditorDialog` 完成，支持：

- 时 / 分 / 秒编辑
- 当前语言名称编辑
- 第二语言名称编辑
- 自动名称与手动名称兼容
- 多语言标签保留

### 8.5 通用页

负责以下配置：

- 应用语言
- 是否自动开始计时
- 启动时恢复上次模式 / 固定模式
- 固定模式选择
- 提醒音开关
- 提示弹窗开关
- Windows Toast 开关
- 音量调节
- 铃声文件选择
- 打开铃声目录
- 测试铃声
- 随机铃声
- 快捷键编辑

### 8.6 关于页

展示：

- 应用名称与版本
- 技术栈
- 项目链接
- Logo / 品牌信息

### 8.7 预览与保存策略

设置页有两类变化：

1. **预览型变化**
   - 语言
   - 主题

   这些变化会先即时作用到主窗口和托盘，用于预览，但未确认前不持久化。

2. **确认型变化**
   - 点击“确定”后统一写回 `parent_window.settings`
   - 调用主窗口 `apply_settings()`
   - 立即保存配置
   - 重新绑定快捷键

### 8.8 快捷键冲突检测

在确认保存前，设置页会检查所有自定义快捷键是否重复。

若存在冲突：

- 阻止保存
- 弹窗提示冲突项

---

## 9. 配置系统

### 9.1 配置文件

运行时配置存储在：

```text
settings/timer_settings.json
```

### 9.2 配置项分组

当前配置大致可以分为以下几组：

| 分组 | 关键字段 |
| --- | --- |
| 外观 | `font_family`、`font_size`、`text_color`、`bg_color`、`bg_opacity` |
| 窗口风格 | `rounded_corners`、`corner_radius`、`night_mode` |
| 计时模式 | `timer_mode`、`timer_mode_key` |
| 倒计时 | `countdown_hours`、`countdown_minutes`、`countdown_seconds` |
| 提醒 | `countdown_action`、`countdown_action_key`、`enable_sound`、`enable_popup` |
| 音频 | `sound_file`、`sound_volume` |
| 主题与语言 | `theme_mode`、`language` |
| 时钟模式 | `clock_format_24h`、`clock_show_seconds`、`clock_show_date`、`clock_show_am_pm` |
| 启动行为 | `startup_mode_behavior`、`startup_fixed_mode_key`、`auto_start_timer` |
| 快捷键 | `shortcuts` |
| 预设 | `countdown_presets`、`preset_sort_mode` |

### 9.3 预设数据结构

倒计时预设的单项结构如下：

```json
{
  "id": "preset_xxxxxxxx",
  "mode": "countdown",
  "hours": 0,
  "minutes": 25,
  "seconds": 0,
  "label": "番茄钟",
  "labels": {
    "zh_CN": "番茄钟",
    "en_US": "Pomodoro"
  },
  "name_key": "pomodoro"
}
```

字段说明：

- `id`：预设唯一标识
- `mode`：当前固定为 `countdown`
- `label`：主显示名称
- `labels`：多语言名称映射
- `name_key`：内置预设的翻译键

### 9.4 相对路径策略

`sound_file` 支持绝对路径与相对路径，但项目优先使用相对路径，尤其是：

```text
sounds/Alarm01.wav
```

这样在打包后只要资源目录与 `exe` 同级即可继续使用。

---

## 10. 国际化设计

项目国际化分为两层：

### 10.1 Qt 控件国际化

由 `module/app.py` 中的 `QTranslator` 完成，用于 Qt 自带控件文本。

### 10.2 业务文案国际化

由 `lang/zh_CN.json` 与 `lang/en_US.json` 提供，业务代码通过 `tr(key)` 获取文本。

### 10.3 设计特点

- 使用 `timer_mode_key` / `countdown_action_key` 规避多语言文本判断
- 预设名称支持双语标签
- 设置页可即时预览语言变化

---

## 11. 资源管理

项目依赖以下资源目录：

- `img/`
  - 应用图标
  - 关于页 Logo

- `lang/`
  - 中文与英文语言包

- `sounds/`
  - 默认提示音 `Alarm01.wav` ~ `Alarm10.wav`

运行时会执行以下资源相关逻辑：

- 统一通过 `get_base_path()` 解析资源目录
- 若 `sounds/` 不存在则自动创建
- 若当前提示音不存在，则自动尝试选择一个可用音频

---

## 12. 构建与发布流程

### 12.1 本地运行

```bash
uv sync
uv run python main.py
```

### 12.2 代码检查

```bash
uv run ruff check .
uv run ruff format .
```

### 12.3 生成可执行文件

```bash
uv sync --dev
uv run python -m PyInstaller DesktopTimer.spec --noconfirm
```

PyInstaller 只打包主程序，资源目录仍作为外部文件存在，需要和 `DesktopTimer.exe` 放在同级目录。

### 12.4 一键打包脚本

`tools/pyinstaller.bat` 会执行：

1. 清理旧的 `build/`、`dist/`、`DesktopTimer.zip`
2. `uv sync --dev`
3. 调用 PyInstaller 构建
4. 复制 `img/`、`lang/`、`sounds/` 到 `dist/`
5. 生成 `DesktopTimer.zip`

### 12.5 安装包

`setup/setup.iss` 基于 `dist/` 目录内容生成安装程序，当前使用相对路径引用：

- `..\dist\DesktopTimer.exe`
- `..\dist\*`
- `..\img\timer_icon.ico`
- `..\LICENSE`

### 12.6 版本更新脚本

`tools/update_version.py` 会同步更新以下文件中的版本号：

- `module/constants.py`
- `pyproject.toml`
- `setup/setup.iss`
- `AGENTS.md`
- `README.md`
- `uv.lock`

---

## 13. 开发与维护建议

### 13.1 当前架构特点

项目整体结构清晰，但核心复杂度集中在两个大文件：

- `module/timer_window.py`
- `module/settings_dialog.py`

这种结构的优点是逻辑集中、迭代快；缺点是：

- 单文件体积较大
- 功能耦合偏高
- 回归修改时定位成本逐渐上升

### 13.2 适合继续拆分的方向

后续若继续演进，可以优先拆出以下子模块：

- 托盘菜单构建
- 倒计时预设管理
- 提醒与通知逻辑
- 主题与样式应用
- 设置项序列化 / 反序列化

### 13.3 新功能扩展时的注意点

1. **新增模式**
   - 同时更新 `timer_mode_key`
   - 更新设置页模式选择
   - 更新托盘菜单与右键菜单
   - 更新 `update_time()` 分支逻辑

2. **新增提醒方式**
   - 扩展 `countdown_action_key`
   - 更新设置页动作下拉框
   - 更新 `on_countdown_finished()` 调度逻辑

3. **新增语言**
   - 新增 `lang/<code>.json`
   - 更新语言切换 UI
   - 检查预设多语言标签展示逻辑

4. **新增预设字段**
   - 同步更新预设编辑器、序列化、规范化与兼容修复逻辑

---

## 14. 手动验证建议

项目当前没有自动化测试套件，建议至少做一次手动冒烟验证：

1. `uv run python main.py`
2. 检查三种模式切换
3. 检查倒计时结束提醒（声音 / 弹窗 / 闪烁 / Toast）
4. 检查托盘菜单与右键菜单
5. 检查设置页保存与重启后的配置恢复
6. 检查语言切换、快捷键修改、预设编辑
7. 检查打包后资源目录是否完整

---

## 15. 总结

DesktopTimer 当前属于一个典型的“单进程、本地配置、桌面常驻型” PyQt 工具应用，技术方案选择偏务实：

- 用 PyQt6 完成桌面 GUI 与系统集成
- 用 QFluentWidgets 提升设置页体验
- 用 JSON 保持配置简单透明
- 用外部资源目录兼顾源码运行与单文件发布

从工程角度看，它的关键设计点主要是：

- 模式逻辑与显示文本解耦
- 配置兼容与自动修正
- 托盘交互与主窗口交互保持一致
- 打包运行与开发运行共享一套资源定位逻辑

这套结构非常适合继续在 Windows 桌面工具方向上迭代。（笑）
