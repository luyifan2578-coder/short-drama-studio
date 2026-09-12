# 电影感静帧故事板（单帧／三联／九镜）

用于把人物、空间、产品、建筑、历史、神话、科幻、体育或一句简单故事，转译为真人实景电影感的 2.39:1 单帧、三联或九镜故事板。只在用户明确提出片名、海报、封面、视觉体系时才追加海报阶段。

## 1. 模式选择

| 用户意图 | 模式 | 交付 |
|---|---|---|
| 一张、单帧、封面底图 | Single Frame | 1 张独立 2.39:1 |
| 三联、三个镜头、默认电影测试 | Triptych | 3 张独立 2.39:1，再纵向拼接 |
| 9 张讲故事、九镜、九宫格 | Nine-Shot Story | 9 张独立 2.39:1，再拼 3×3 |

未指定数量时默认 Triptych；需要规则、发现、选择、后果与余韵时用 Nine-Shot。

## 2. 后端与拼版

- 遵守用户指定的图像后端；用户指定官方内置图像生成时不得静默切换。
- **每镜独立生成**，禁止要求模型在一张画布里画三联、九宫格或分镜表。
- 生成后用脚本拼版；保留每张独立源图，便于只替换失败镜头。
- 九镜默认分三批（1–3／4–6／7–9），每批返回后立即记录「镜号 → 提示词 → 文件路径」。

## 3. 五个最高优先级判断

1. **先定义不可立即解决的状态**：用一句可拍摄的事实描述冲突，不用情绪词替代剧情。
2. **每镜只有一个主要动作**，外加一个次要线索、一个主要构图决定、一个主光源、2—3 个具体场景信息。
3. **构图由关系压力产生**：谁在看谁、谁知道得更多、谁被空间限制、观众站在哪一侧、什么东西比人物更有权力。
4. **每镜写清视线流量**：视线从 A 进入，被 B 遮挡，落到 C，由 D 带走。
5. **色彩是物理叙事**：两个主色域、一个过渡色域、一个小面积强调色，每种颜色都要有现实来源。

## 4. Continuity Bible

写镜头前先锁定，每个镜头提示词都重复核心锚点：

    时间与时代：
    地点与空间骨架：
    主角：年龄段、身份、发型、体态、服装主色、唯一识别物
    配角：年龄段、身份、服装主色、与主角关系
    关键道具：形状、材质、颜色、使用状态
    固定环境：墙体、门窗、地面、设备、天气
    综合色：主色 / 辅色 / 强调色
    成像基底：35mm / 16mm / 早期数字 / 纪录式手持等
    光源法则：
    禁止漂移：不得改变的人物、服装、道具和空间事实

每个角色保留 4—6 个稳定锚点即可，细节越多漂移越严重。

## 5. 镜头账本

    | # | 剧情功能 | 主要动作 | 观众位置 | 景别/焦段 | 构图压力 | 关键线索 | 与前镜变化 |

每个相邻镜头至少变化四项：景别、机位高度、摄影机与主体距离、人物与环境比例、观看立场、构图机制、信息载体、焦点层、光线方向、人物状态。

九镜的完整节拍、变化矩阵与模板见 [nine-shot-story-protocol-v3.md](nine-shot-story-protocol-v3.md)，执行九镜时必读。

## 6. 提示词编译

默认英文，按以下顺序：

1. 独立单帧与画幅：`standalone live-action film still, 2.39:1 horizontal, no collage, no grid`
2. Continuity Bible 中与本镜相关的稳定锚点
3. 本镜唯一主要动作与未完成状态
4. 摄影机实体位置、焦段、景别、观看关系
5. 前景、中景、背景的决定性信息
6. 可解释的主光源
7. 综合色与强调色的物理来源
8. 成像介质与有限光学缺陷
9. 精简负面约束

基底按需取用，不要全部堆叠：

> standalone live-action feature-film still, practical location, real actors, physically plausible set and props, restrained production design, soft highlight roll-off, medium-low microcontrast, subtle uneven grain, local optical softness, natural skin texture

负面约束：

> no collage, no grid, no captions, no watermark, no CGI concept art, no game key art, no glossy AI rendering, no HDR, no plastic skin, no excessive particles, no teal-orange grading, no artificial rim light, no commercial beauty lighting, no television-drama blocking

避免空泛词：masterpiece、epic、beautiful、dramatic、volumetric、highly detailed、rich detail。

## 7. 拼版

    & scripts/compose-nine-shot-storyboard.ps1
      -Sources @('shot01.png', ... ,'shot09.png')
      -OutputDir '<输出目录>'
      -Prefix '<故事名>'

脚本验证 9 个可读源文件、保留独立源图、保持纵横比、输出三张纵向三联图与一张 3×3 九宫格、使用 8—12 px 黑色呼吸间隔、不添加文字与水印。

## 8. 参考图与原创隔离

参考图只允许抽取一个主维度：构图方法、配色方法、或题材方向。其余维度必须原创。若同时借用两个以上维度，或一眼能认出某部具体影片的静帧轮廓，必须重写。提示词不依赖导演名或电影名。

## 9. 部分失败恢复

某镜失败、被误拦截或漂移时：盘点已成功镜头 → 保留该镜的剧情功能与连续性锚点 → 删掉可能触发误判但非核心的措辞 → 只补跑失败镜 → 写回原镜号再拼版。不要因为一镜失败而改变整组角色、时代、色彩或结局。

## 10. 质量验收

| 项目 | 分值 |
|---|---:|
| 剧情因果与不可打乱性 | 25 |
| 连续性圣经执行 | 20 |
| 构图、视线与观看立场 | 20 |
| 色彩和光源物理可信 | 15 |
| 真人实景与反 AI 质感 | 15 |
| 文件与拼版完整性 | 5 |

低于 82 分不交付。一票否决：模型在一张画布里直接生成九宫格；缺少独立源图；九镜只是同一构图换角度；明显 CG、游戏宣传图或商业广告；人物、关键道具或空间在关键因果镜头中无理由变形。

画面仍显油腻、过度精致、过脏或镜头节奏平庸时，读 [cinema-dna-v4-anti-ai.md](cinema-dna-v4-anti-ai.md)。需要更完整的单帧、三联、焦段、光学与题材方法库时，按章节读 [cinema-dna-full-spec.md](cinema-dna-full-spec.md)。
