# Codex Skills

个人 Codex 技能仓库。

## 包含的技能

### short-drama-studio

用一套统一规则完成 AI 短剧的拆集拆镜、逐镜情绪设计、30 秒视频分镜提示词与电影感静帧故事板。

- **模式 A｜拆集拆镜**：时长预算（中文 4.5 字/秒、英文 2.8 词/秒）、边界规则、场景一致性、尾帧交接。
- **模式 B｜视频提示词**：Seedance 2.5 Pro、9:16 竖屏、单条不超过 30 秒、单镜不超过 3 秒、多机位不越轴、导演级运镜与动机化转场。
- **模式 C｜静帧故事板**：21:9 或 9:16 的电影感单帧／三联／九镜，含连续性圣经、镜头账本与质量验收。

核心纪律：原文是唯一最高标准；对白与旁白不删减不改写；旁白与现场对白分轨、旁白期间全员闭口；每条生成单元结尾有可交接的技术尾帧；女性角色锁骨以下全程遮挡。

## 安装

把仓库里的 `skills/<技能名>` 目录复制到本机的技能目录：

| 系统 | 路径 |
|---|---|
| Windows | `C:\Users\<用户名>\.codex\skills\` |
| macOS / Linux | `~/.codex/skills/` |
| 设置过 `CODEX_HOME` | `$CODEX_HOME/skills/` |

要求：目标文件夹名与技能名一致，其根目录必须有 `SKILL.md`。复制完成后新开一个对话即可用 `$<技能名>` 调用。

也可以用 skill-installer 从本仓库安装：

```
从 <owner>/codex-skills 仓库安装 skills/short-drama-studio
```

## 目录结构

```
skills/short-drama-studio/
|-- SKILL.md                  入口：优先级、生产纪律、模式路由、技术基线、流程
|-- agents/openai.yaml        UI 元数据
|-- references/               规则与方法库，按需读取
|-- scripts/                  DOCX 导出与九宫格拼版
`-- assets/examples/          示例图
```

## 依赖

- `scripts/extract_docx.py`：仅用 Python 标准库。
- `scripts/compose-nine-shot-storyboard.ps1`：需要 PowerShell（macOS 用 PowerShell 7，或改为手动拼版）。

没有其他外部依赖。
