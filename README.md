# 《炼狱弐》PSP 日版简体中文汉化工程

这是 PSP《炼狱弐 The Stairway to H.E.A.V.E.N.》日版到简体中文汉化补丁的工作仓库。仓库保存的是逆向记录、文本/字体/图片处理脚本、测试和项目文档；不包含游戏 ISO、提取后的版权资源、重打包 ISO 或补丁发布包。

发布与实机/模拟器展示：

- S1 发布帖：[汉化] [PSP]炼狱 贰 The Stairway to H.E.A.V.E.N._小方&oid汉化版：https://stage1st.com/2b/thread-2281317-1-1.html
- B 站资源分享：【汉化资源分享】PSP 炼狱2 通往天国得阶梯 汉化版发布中！相当另类得一款游戏：https://www.bilibili.com/video/BV1hqGq6dE6f/?vd_source=1b420207a50e87a574d9bfc22a6c18a8
- B 站实况/展示：2026年PSP汉化游戏《炼狱 贰 通往天国的阶梯》：https://www.bilibili.com/video/BV19SGo6EECq/?vd_source=1b420207a50e87a574d9bfc22a6c18a8

## 当前状态

本仓库基本冻结。当前可发布基线是 v44：

```text
local/rebuilt/combined_chs_v44_reviewed_token_extracted/
local/rebuilt/combined_chs_v44_reviewed_token.iso
local/work/combined_chs_v44_reviewed_token/
local/work/chs_coverage_v44_reviewed_token/
```

这些路径在本地是 ignored 产物，不应提交。它们记录了最后一次完整构建、字形分配、覆盖率报告和 PPSSPP-ready extracted folder。

v44 覆盖内容：

- DATA001、DATA002、DATA003 当前已解析文本表。
- DATA003/1089 剧情文本，按日文原文优先重新校对。
- DATA001/0015 装备文本，reviewer 文本和 runtime fit 文本分层处理。
- DATA001/0017 帮助/说明书文本。
- DATA002/0065 名字输入和 UI 文本。
- EBOOT 中的新存档 PARAM.SFO 模板字符串，包括标题、详情、游玩时间标签和 OSK 提示。
- PSP shell 的 `PIC0.PNG` 预览图，以及 `PIC1.PNG` 左上角小 credit 图。

已知没有纳入发布基线的实验：

- 游戏内标题 logo/背景材质 credit patch。可以显示，但观感不如 shell 图干净，所以 v44 发布基线保持游戏内标题纹理原样。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `docs/` | 当前逆向、格式、策略和本地 artifact 文档。 |
| `tools/` | 提取、导入、字体、图片、EBOOT、ISO 构建等脚本。 |
| `tests/` | 工具层单元测试，不需要游戏数据。 |
| `samples/` | 可提交的 glyph seed 和小型参考文件。 |
| `translation_reviewed/` | reviewer 修改后的文本 JSON；这是嵌套 git 仓库。 |
| `local/` | ignored 本地工作区：游戏提取、生成表格、字体页、重构建目录、ISO 等。 |

重要原则：

- 不提交 ISO、BIN、PRX、MIG/TDL 提取图、重构建 ISO、PPSSPP dump 等版权/生成文件。
- 本地生成物放在 `local/`，并在 `docs/local-artifacts.md` 里记录保留理由。
- `translation_reviewed/` 是独立 git 仓库，提交时要和主仓库分开。

## 文档地图

后续如果有人想继续做 PSP 逆向或移植到另一个游戏，建议先看这些文档：

| 文档 | 用途 |
| --- | --- |
| `docs/chs-plan.md` | 最后阶段状态、构建路径、覆盖率、已知限制。 |
| `docs/chs-strategy.md` | 汉化策略、翻译分层、字库策略、发布基线说明。 |
| `docs/chs-layout-rules.md` | 换行、排版、按键提示、帮助页、名字输入等规则。 |
| `docs/formats.md` | MCD3、TDL、MIG、offset-table、EBOOT/PARAM.SFO、PIC0/PIC1 等格式笔记。 |
| `docs/runtime-observations.md` | PPSSPP 运行时确认过的现象。 |
| `docs/tooling.md` | 当前维护脚本索引和常用命令。 |
| `docs/local-artifacts.md` | `local/` 下哪些东西该保留、哪些可以删。 |
| `docs/chs-glossary.json` | 剧情名词和人名统一表。 |

## 关键逆向结论

### 文本容器

主要文本来自 MCD3 entry 中的 offset-table 风格记录。当前构建涉及：

```text
DATA001/0003  启动/UI
DATA001/0008  教程/提示
DATA001/0012  旧剧情/角色文本
DATA001/0015  装备名和装备描述
DATA001/0016  UI
DATA001/0017  帮助/说明书
DATA002/0065  名字输入和部分 UI
DATA003/1089  主要剧情脚本
```

`tools/extract_text.py`、`tools/extract_offset_table_runs.py`、`tools/decode_offset_table_text.py` 和 `tools/build_chs_offset_table.py` 是理解这条链路的入口。

### 字体与 glyph

游戏字体在 DATA001/0002 的 TDL/MIG 字体页里。最终构建使用 bitplane 模式：同一个物理 cell 的 low/high layer 可以承载两个逻辑字形。

当前 v44 字形统计：

```text
assigned glyphs: 1523
physical cells used: 845
logical capacity: 1782
usable CHS headroom: 106
```

原则是只把 CJK 汉字放入生成字体；Latin、数字、标点、符号和原游戏已有字形尽量复用原码位。

相关脚本：

```text
tools/build_chs_tutorial.py
tools/render_mig_font_cell.py
tools/stage_font_probe.py
tools/build_chs_combined_data001.py
tools/make_chs_glyph_contact_sheet.py
tools/report_chs_coverage.py
```

最后一版覆盖字形 contact sheet：

```text
local/work/combined_chs_v44_reviewed_token/glyph_contact_sheet/glyph_contact_sheet.png
local/work/combined_chs_v44_reviewed_token/glyph_contact_sheet/glyph_contact_index.csv
```

### reviewer pack

reviewer 文本入口是 `translation_reviewed/`。最后使用的是瘦身 JSON：

```json
{
  "id": "DATA003/1089#0202:0",
  "category": "story_script",
  "chs": "…#GRAM#…是你吗？",
  "jp": "　…#GRAM#…貴方なのですか？"
}
```

`jp` 是 code-aware 视图，不是单纯 OCR 文本。最后规则：

- `0x0020` 显示为半角空格。
- `0x0100` 显示为全角空格。
- `0x000A` 显示为换行。
- DATA003 中运行时主角名 token 显示为 `#GRAM#`。
- DATA001/0012 中另一类主角名 token 保持 `@GRAM@`。
- `DATA002/0065#0085:0` 是符号/低码位特殊行，review 视图保留 raw code sequence。

相关脚本：

```text
tools/export_code_aware_review_pack.py
tools/promote_reviewed_translation_package.py
tools/make_equipment_jp_first_layers.py
tools/apply_story_glossary.py
```

### EBOOT 和存档信息

PSP 系统存档列表显示的标题和详情来自每个 savedata 的 `PARAM.SFO`：

```text
SAVEDATA_TITLE
SAVEDATA_DETAIL
TITLE
```

已有存档可以用 `tools/patch_savedata_sfo.py` 单独修。新存档写入模板在解密后的 EBOOT ELF 中，v44 已 patch：

- 游戏标题。
- 新存档标题/详情模板。
- 通关次数、死亡次数、击破数等计数字段。
- 游玩时间标签。
- 名字输入 OSK 提示。

相关脚本：

```text
tools/patch_eboot_runtime_strings.py
tools/patch_savedata_sfo.py
```

### 图片

PSP shell 图：

- `PIC0.PNG` 是 PSP 菜单预览/说明图，最终已换成中文图。
- `PIC1.PNG` 是 PSP shell 背景，最终使用左上角小 credit 版本。

游戏内标题背景/标题 logo 也调查过，但没有进入发布基线。相关实验都留在 `local/work/title_credit_probe/`，格式笔记见 `docs/formats.md`。

相关脚本：

```text
tools/patch_psp_pic0.py
tools/patch_title_credit.py
tools/runtime_texture_inventory.py
```

## 常用命令

运行测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

promote reviewer 文本：

```powershell
.\.venv\Scripts\python.exe tools\promote_reviewed_translation_package.py
.\.venv\Scripts\python.exe tools\make_equipment_jp_first_layers.py
.\.venv\Scripts\python.exe tools\apply_story_glossary.py
```

导出 code-aware reviewer pack：

```powershell
.\.venv\Scripts\python.exe tools\export_code_aware_review_pack.py
```

构建 extracted folder：

```powershell
.\.venv\Scripts\python.exe tools\build_chs_combined_data001.py `
  --target DATA001/0003 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0003_full_current_target_sheet.json `
  --target DATA001/0008 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0008_full_current_target_sheet.json `
  --target DATA001/0012 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0012_full_current_target_sheet.json `
  --target DATA001/0015 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0015_full_current_target_sheet.json `
  --target DATA001/0016 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0016_full_current_target_sheet.json `
  --target DATA001/0017 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA001_0017_full_current_target_sheet.json `
  --target DATA002/0065 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA002_0065_full_current_target_sheet.json `
  --target DATA003/1089 local/work/translation_refine_v1/merged_target_sheets_v41_reviewed_all/DATA003_1089_jp_first_target_sheet.json `
  --work-root local/work/combined_chs_v44_reviewed_token `
  --output-root local/rebuilt/combined_chs_v44_reviewed_token_extracted `
  --font local/fonts/full-semibold-18.fnt `
  --font-size 13 `
  --render-mode palette3 `
  --threshold 64 `
  --gray-threshold 176 `
  --assignment-model bitplane `
  --no-title-credit `
  --overwrite
```

构建 ISO：

```powershell
.\.venv\Scripts\python.exe tools\build_psp_iso.py `
  local\rebuilt\combined_chs_v44_reviewed_token_extracted `
  local\rebuilt\combined_chs_v44_reviewed_token.iso `
  --overwrite
```

覆盖率报告：

```powershell
.\.venv\Scripts\python.exe tools\report_chs_coverage.py `
  --build-root local\work\combined_chs_v44_reviewed_token `
  --stage local\work\combined_chs_v44_reviewed_token\stage_combined_chs.json `
  --output local\work\chs_coverage_v44_reviewed_token
```

生成覆盖字形 contact sheet：

```powershell
.\.venv\Scripts\python.exe tools\make_chs_glyph_contact_sheet.py `
  --build-root local\work\combined_chs_v44_reviewed_token `
  --output-dir local\work\combined_chs_v44_reviewed_token\glyph_contact_sheet
```

## 给后来者的建议

1. 先读 `docs/tooling.md`、`docs/formats.md` 和 `docs/runtime-observations.md`，不要直接从脚本名猜用途。
2. `build_chs_combined_data001.py` 名字是历史遗留，实际可以构建 DATA001/002/003。
3. 任何新游戏都不要直接套本项目码位；只能复用方法。尤其是空格、按键、运行时 token、字库页布局都要重新确认。
4. PPSSPP texture dump 很有用，但游戏内图层和 PSP shell 图是两套东西，别混。
5. reviewer 文本、runtime fit 文本、最终构建文本要分层。装备描述是这个项目里最能说明分层价值的例子。
6. 如果 git 被多个 Codex/编辑器卡住，先确认没有 git 进程，再处理 `.git/index.lock`。`translation_reviewed/` 有自己的 `.git`。

## 法律与版权

本仓库只保存研究和汉化工程文件。请使用自己合法取得的游戏镜像进行研究和打补丁。不要向本仓库提交或分发游戏本体、提取资源、重构建 ISO 或其他版权内容。
