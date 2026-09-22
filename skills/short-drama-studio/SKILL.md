---
name: short-drama-studio
description: 用一套统一规则完成 AI 短剧的拆集拆镜、逐镜情绪设计、30 秒视频分镜提示词与电影感静帧故事板。用于分镜拆分、镜头设计、Seedance 视频提示词、剧集时长与边界规划、逐镜情绪与连续性检查、21:9 电影感单帧／三联／九镜等短剧视觉生产任务。
metadata:
  version: 3
  short-description: 短剧拆镜与提示词一体化生产
---

# 短剧分镜工作室

面向真人实拍质感的 AI 短剧：从原剧本出发，做拆集拆镜、逐镜情绪设计、30 秒视频提示词，必要时产出电影感静帧故事板。

## 最高优先级

1. 用户当前任务的明确要求。
2. **剧本原文。** 原文对人物、身份、关系、场景、动作、台词有明确描写处一律照原文执行。资产设定、参考图、既有草稿、旧版提示词与原文冲突时，一律以原文为准。
3. 用户提供的资产图、服装图、场景图、道具图与上一段尾帧。
4. 项目《分镜规范》。项目已把本 skill 的通用规则本地化为具体值时，以项目规范为执行依据。
5. 本 skill 的默认规则，见 [references/production-rules.md](references/production-rules.md)。

## 六条不可违背的生产纪律

- **对白与旁白一律取自原文本，不删减、不改写、不合并、不省略。** 本地化项目按目标语言输出朗读文本，画面指令保持中文。旁白与对白分轨：旁白或内心 VO 播放期间，画面内所有人物闭口、无口型、无说话嘴形。
- **每个生成单元结尾必须有作为时间轴实际镜头的技术尾帧**，写明人物位置、姿态、朝向、距离、道具与光源状态，可被下一单元首帧直接继承。
- **女性角色锁骨以下在全部镜头完整遮挡**，包括沐浴、换装、亲密、动作场景；由服装、床品、道具、前景遮挡或安全构图承担。
- **每集走完四步门禁才动手。** 先做方案分析讨论，再在对话界面弹出方案选项交互卡让用户点选或自行输入要求，确认之后才拆分镜、出提示词。只在正文里列 A／B 选项不算过闸；当前模式发不出交互卡时，停下说明并请用户切换模式。
- **连续场先建状态账本。** 区分实际在场人物与本段主动人物，锁定固定空间、关系轴、人物禁区、道具持有和动作进程；没有明确离场的人不得因本段无台词而消失。复杂连续任务读 [references/continuity-ledger.md](references/continuity-ledger.md)。
- **时空与声源必须分层。** 真实现场、显示载体、档案影像、纯音频、VO 与后期文字分别标记；档案人物和道具不得串入现实现场，文本交付不得冒充成片验证。

## 选择模式

| 用户要什么 | 模式 | 读 |
|---|---|---|
| 分析剧本、拆集、定分镜边界、算时长、定交接 | A 拆集拆镜 | [references/splitting.md](references/splitting.md) |
| 出某一集或某一段的镜头提示词 | B 视频提示词 | [references/video-prompt.md](references/video-prompt.md) ＋ [references/craft.md](references/craft.md) |
| 电影感单帧／三联／九宫格静帧故事板 | C 静帧故事板 | [references/cinematic-stills.md](references/cinematic-stills.md) |

模式 B 依赖 A 的边界结论。用户直接要提示词却没给边界时，先按 A 的方法快速定边界，再写提示词。

## 五种任务分支

- **新增段落**：产出完整的 30 秒时间轴，包含技术尾帧。
- **完整修订**：原结构无法成立时，重出整合后的完整提示词。
- **局部返修**：冻结已认可的结构、节奏和其他人物状态，只修改用户指出的位置、机位、声源或尾帧变量。
- **仅追加插入**：只返回请求的插入内容与其时长，不提前泄露被保留的剧情悬念。
- **接续**：从用户指定的上一段尾帧状态起步；未指定时，从紧邻的技术尾帧状态起步。

## 默认技术基线

- 视频提示词：Seedance 2.5 Pro，原生 9:16 竖屏，单条生成单元不超过 30 秒。
- 单条 30 秒内的镜头不超过 3 秒；30 秒段落不少于 10 个镜头（含技术尾帧）。
- 每集 60—90 秒，按内容时长分配 2—3 个生成单元。
- 静帧故事板：2.39:1，每镜独立生成后再拼版，绝不要求模型在一张画布里画九宫格。

## 流程

### 单集四步（门禁）

1. **方案分析讨论**：先出方案、不出镜头清单。九项必含项见 [references/production-rules.md](references/production-rules.md) 第二节。
2. **弹出方案选项交互卡**：把可比方案摆成可点选项，由用户点选或自行输入要求；本集需要用户决定的事项必须在这一步全部闭掉。
3. **分镜拆解**：按确认后的方案定边界、定情绪、分配镜头与秒数；边界行号锁定后未经确认不得移动。
4. **提示词生成**：逐段产出可整段复制的提示词，并跑时长三重校验。

第 1、2 步没完成，不得进入第 3、4 步。每集在项目台账里留一行方案确认记录。

### 每段的制作步骤

1. 读原文，取到准确的段落范围与行号，并锁定本次制作起点、终点和不得提前生成的外部边界。DOCX 用 `scripts/extract_docx.py` 导出带段落号与样式的 UTF-8 文本。
2. 做时长预算：中文约 4.5 字/秒、英文约 2.7 词/秒（情绪对白 2.4—2.6），叠加句间停顿与尾帧，算出每段能装多少字。详见 [references/splitting.md](references/splitting.md)。
3. 定边界：优先落在场景转换点与事件完成处，不切在同一句对白或同一连续动作中间；按连续场次建立依赖链，不把相邻集自动视为独立任务。
4. 建账本：记录实际在场人物、固定锚点、关系轴、道具生命周期和上一尾帧；含屏幕、录像、录音或 VO 时标记 `REAL/DISPLAY/ARCHIVE/AUDIO/VO/POST` 层。
5. 定情绪：先确定这一段的情绪基调，再逐镜写清每位出镜人物的情绪、具体视线目标与微表演。禁止把暧昧戏演成悬疑、把看戏演成恐惧。
6. 写镜头：一镜一个信息任务，九项字段齐全，单一单元内不越轴；相邻镜头景别不同，同一动作不跨镜重复，长台词切到对方反应镜。
7. 按 [references/video-prompt.md](references/video-prompt.md) 的自检清单与 production-rules 第四节回看清单过一遍，并按证据注明提示词、生成、检查和用户确认分别处于哪一状态。

## 输出约定

- 提示词默认直接在对话里给出可整段复制的纯文本，不额外写入文件；用户明确要求落盘时才写文件。
- 每个生成单元必须自包含：场景、时间天气、人物状态、起始位置、朝向、距离、光源、镜头清单、尾帧锁定全部重述，不依赖模型记住上一段。
- 提示词里只写资产名称（场景、人物、服装、道具）；人物外观、服装样式与场景布局一律写「以随附资产图为准」，不重复描述，避免模型自行编造空间与外观。
- 已有定稿资产图时，剧本决定剧情事实、资产图决定视觉外观、紧邻尾帧决定当前状态；缺少定稿资产时列出缺失项，不自行想象成定稿。
- 精确短信、法律文件、聊天记录和界面文字使用 `POST` 后期叠加；视频模型只负责可信载体、版式区域和人物反应。
- 不给人物加眼睛发光、瞳孔异色、泛红、发烫、光晕、粒子一类特效。

## 按需读取

默认先读精简版；只有需要更细的模板或更全的方法库时才读完整版，不要一次全部加载。

**精简版（默认）**

- 单集四步门禁、P0／P1／P2 三级规则、回看清单：[references/production-rules.md](references/production-rules.md)
- 时长预算、边界与交接：[references/splitting.md](references/splitting.md)
- 连续状态账本、时空声源分层、道具生命周期与局部返修：[references/continuity-ledger.md](references/continuity-ledger.md)
- 视频提示词字段与自查：[references/video-prompt.md](references/video-prompt.md)
- 表演、情绪、轴线、运镜、转场、物理：[references/craft.md](references/craft.md)
- 静帧／三联／九镜：[references/cinematic-stills.md](references/cinematic-stills.md)

**完整版（按需）**

- 生成前十问、角色／服装／场景／道具锁定模板、特殊场景合规要求（沐浴、换装、亲密、水中）：[references/output-format.md](references/output-format.md)
- 完整通用制作规则库：同房间换区域、多人反应、Seedance 能力适配、无声叙事、段与段衔接等：[references/craft-full-spec.md](references/craft-full-spec.md)
- 9:16 竖屏的完整故事板规范（垂直压力类型、竖版提示词基底与负面约束）：[references/cinematic-stills-9x16.md](references/cinematic-stills-9x16.md)
- 2.39:1 横版的完整故事板规范：[references/cinematic-stills-21x9.md](references/cinematic-stills-21x9.md)
- 执行九镜时必须读：[references/nine-shot-story-protocol-v3.md](references/nine-shot-story-protocol-v3.md)
- 画面油腻、过度精致、镜头节奏平庸：[references/cinema-dna-v4-anti-ai.md](references/cinema-dna-v4-anti-ai.md)
- 单帧、三联、焦段、光学与题材方法库：按章节读 [references/cinema-dna-full-spec.md](references/cinema-dna-full-spec.md)，不整份加载
