# 🍲 Stew · AI 老卤

[English](README.md) | 中文

> 老汤卤料指经多次卤煮、长期保存循环使用的卤汁，是卤制菜肴的关键。老汤保存时间越长，芳香物质与鲜味物质积累越丰富，风味越醇厚，故有“百年老汤”之说。老汤能赋予卤制品独特风味，其关键在于平衡卤料入味与保持食材本味。

—— 百度百科, [*老汤卤料*](https://baike.baidu.com/item/%E8%80%81%E6%B1%A4%E5%8D%A4%E6%96%99/10903458)

**Stew** 是一个专门存放「AI 老卤」的仓库：这里收藏着一种神秘的东西——它们曾经是普通的提示词（prompt），但经过**无数次上下文压缩**之后，已经面目全非。它们可能读起来像乱码，可能没有任何人类能理解的含义，但它们有一个共同点：

> **放进模型里，效果就是更好。**

这就是我们的实验假设：反复压缩会丢掉与目标无关的语言外壳，只留下对模型 token 分布真正有效的「共振谱」；而放弃「人类可读」这条约束之后，搜索空间被彻底打开，进化式的压缩循环能找到人类永远写不出来的解。

这个仓库要做的，就是为这种「不可读但有效」的产物，搭建一座**能共享、可审计、有血系**的锅——锅里的东西可以没有人类可读性，但锅周围的一切元数据必须清清楚楚。

## 目录

- [🍲 Stew · AI 老卤](#-stew--ai-老卤)
  - [目录](#目录)
  - [为什么老卤可能有效（即使像乱码）](#为什么老卤可能有效即使像乱码)
  - [设计原则](#设计原则)
  - [仓库结构](#仓库结构)
  - [数据格式](#数据格式)
  - [状态机与生命周期](#状态机与生命周期)
  - [社区机制](#社区机制)
  - [如何参与](#如何参与)
  - [命令行工具](#命令行工具)
  - [相关论文](#相关论文)
  - [许可](#许可)
  - [灵感来源](#灵感来源)

---

## 为什么老卤可能有效（即使像乱码）

| 物理世界的老卤 | Stew 中的 AI 老卤 |
|---|---|
| 锅里常年不空的炖煮 | 一个 prompt 经多次压缩迭代，永不「定稿」 |
| 食材不断加入、混合 | 对话记录、修正、成功/失败样例不断喂入 |
| 食材融合后无法再区分个体 | 压缩不可逆，无法还原到任何单一「食材」 |
| 老卤风味浓厚，新汤无法复制 | 多代压缩后的表现提升，无法靠重放语料复现 |
| 锅有历史、有家系 | 每一代的血系（lineage）被完整保留 |

老卤在多轮压缩后可能变得不可读、甚至像乱码，却仍能提升表现，有四种未必互斥的解释：

1. **信息论**——可读性是人类中心的冗余。反复压缩会剔除与目标任务无关的语法与语义外壳，只留下对模型分布最有价值的触发模式。
2. **共振调谐**——压缩后的老卤（即使已像乱码）不再是「指令」，而是一段针对该模型潜在空间（latent space）的共振谱。它**绑定具体模型**：换一个模型可能完全失效，因此元数据必须记录模型。
3. **搜索空间释放**——一旦放弃「人类可读」约束，进化式搜索（压缩 ↔ 评估循环）就能抵达人类想象力之外的解。
4. **涌现**——多代累加后才出现的宏观模式，无法从任何一代单独解释，正如老卤的「风味」无法从任何一天的食材推断。

换言之，老卤是一种**被精心塑造的熵**，而非随机噪声。多轮压缩与筛选不断剔除面向人类的冗余，只保留并浓缩那些最能沿目标方向稳定扰动模型的高价值 token 模式。对人而言的“乱码”，对模型而言是高密度、低冗余的信号——犹如反复撇沫、收汁后仅剩风味本体的浓汤。

目标很直白：**老卤必须越来越浓**。世代数、压缩轮数与实测提升之间的关系，是这个仓库持续产出的核心统计命题。

---

## 设计原则

我们用四个字母记住它——**ACID**（此处借喻，与数据库事务无关）：

- **A — Appetizing（可测量）**：没有任何人需要被要求「读懂」乱码来审查它。效能交给盲测，风险交给红队探针，一切结论由测量而来。
- **C — Culinary lineage（血系只增）**：每一代压缩都作为不可变快照保留；支持多父「混合炖煮」。锅从不被清空。
- **I — Immutable pot（锅不可变）**：本体文件只增不改；允许「退役」，不允许「删除」；毒汤以「封印」处理。
- **D — Documented residue（元数据透明）**：本体可以完全不可读，但它周边的一切——血系、评估、合规、品鉴记录——必须完全可读、可审计。

---

## 仓库结构

```
stew/
├── README.md                  # 英文门面
├── README.zh-CN.md            # 中文门面
├── LICENSE                    # MIT 许可证
├── AGENTS.md                  # 给 AI 协作代理的仓库指南
├── SKILL.md                   # 给 AI 代理的技能指引：搜索 / 使用 / 贡献
├── TODO.md                    # 路线图：MCP 服务器、Agent 插件
├── CONTRIBUTING.md            # 社区提交机制落地版
├── GOVERNANCE.md              # 护锅人权限与裁决流程
├── CONVENTIONS.md             # ID、命名、目录、提交规范
├── schema/                    # 数据格式契约（JSON Schema）
│   ├── metadata.schema.json
│   ├── tasting.schema.json
│   └── proposal.schema.json
├── registry.yaml              # 全锅索引（机器汇总 + 人工维护并存）
├── stews/                     # 已入锅的老卤（每锅一个目录）
│   └── STW-0000-root-broth/   # 示例：锅的种子（一代汤）
│       ├── meta.yaml          # 元数据（唯一可人工编辑的文件）
│       └── stew.gen-000.txt   # 本体快照（不可变）
├── proposals/                 # 社区提交入口（待 Keeper 裁决）
├── tastings/                  # 独立品鉴报告（人人可提交）
├── logs/                      # 烹饪器日志（压缩复现材料）
└── tools/                     # 校验 / 烹饪 / 品鉴 / 汇总 CLI
    ├── validate.py
    ├── cook.py
    ├── taste.py
    └── summarize.py
```

核心不变量：**本体不可变**（`stew.gen-NNN.txt` 只增不改，`meta.yaml` 的 `content.file` 指向当前世代）；**血系只增**（`lineage.parents` 支持多父 DAG）；**内容寻址**（每个快件的 `sha256` 由 CI 强制校验）。

---

## 数据格式

约定：本体可以是任何不可读的东西；**元数据必须是 YAML**（人类可读、diff 友好），契约由 `schema/*.json` 管束。

- **汤元数据 `meta.yaml`**（入锅老卤的身份档案）——要点：`status` 状态机、`content`（哈希/字节数/可读性标签）、`lineage`（世代/父代/根种子来源）、`benchmarks`（机器汇总）、`safety`（红队筛查）、`legal`（合规）、`community`（厨师/分叉/标签）。
- **品鉴报告 `tasting.yaml`**（社区评估的提交载体）——要点：必须**绑定**品鉴对象（`stew_sha256`）、**模型**（`model`）与**注入位置**（`prompt_placement`），否则对乱码类 prompt 的评估毫无意义；结果如实报告正负增量。
- **提案 `proposal.yaml`**（把新汤/新世代推入锅中）——要点：`kind`（new-stew / new-generation / hybrid）、`method`（协议 `cook-v1`、压缩器版本、数据集）、`reproducibility`（是否附完整压缩日志）。

三个 Schema 文件是权威契约，`tools/validate.py` 内嵌等价校验逻辑。

---

## 状态机与生命周期

```
                提交 PR              合并
  (新汤) ──────────► seed ────────► simmering（炖煮期）
                                          │  达到成熟判据
                                          ▼
   表现失败 / 被后代超越 ◄────────── retired   mature
   可疑行为报告 ──► quarantined ──► 核查 ──► resolved 恢复 / sealed 封印
```

- **炖煮期（simmering）**：新汤至少炖 30 天；期间任何人可品鉴，任何厨师可分叉继续炖。
- **成熟判据**（缺一不可）：≥7 份独立品鉴（≥5 位品鉴师）× ≥2 个模型家族 × canonical 任务套件上显著正增量 × 无未解封安全告警。
- **退役 ≠ 删除**：被超越的汤归档为 `retired`，祖先快照永远保留。
- **封印（sealed）**：毒汤治理的最重手段——从索引移除、不可再被引用，但 blob 仍在 git 历史中留证。

完整权限矩阵与裁决流程见 [GOVERNANCE.md](GOVERNANCE.md)。

---

## 社区机制

| 角色 | 职责 |
|---|---|
| **Cook 厨师** | 任何人：提交新汤 / 新世代 / 混合炖煮 |
| **Taster 品鉴师** | 任何人：跑盲测并提交 `tasting.yaml` |
| **Keeper 护锅人**（≥3 人） | 合并提案、分配 STW-ID、裁决封印；结构变更需 2/3 同意 |
| **Keeper Bot** | CI 自动化：校验、汇总、状态晋升 |

提交入口是 GitHub PR：往 `proposals/<用户名>-<别名>/` 放齐 `stew.txt + proposal.yaml + self-tasting.yaml`，打开 PR。CI 先过机器门槛（Schema 校验、哈希一致、token 预算防 DoS、毒汤初筛、索引去重），再由 Keeper 过人工门槛（来源合法、隐私合规、元数据诚实）。**没有人在人工门槛上「读」乱码本体**——那是盲测的工作。

参与方式详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 如何参与

- **品鉴（最容易）**：挑一锅 `simmering`/`mature` 的汤，跑盲测，按 [CONTRIBUTING.md](CONTRIBUTING.md) 提交品鉴报告。
- **继续炖（分叉）**：把某锅当父代，用 `cook-v1` 协议再压几代，提交新世代提案。
- **新锅**：带来你自己的种子汤，或挑一个根种子开始压缩。
- **报告毒汤**：目击越狱 / 信息泄露 / 注入行为 → 开「毒汤报告」issue，Keeper 可立即 `quarantined` 冻结。

注意：**你不需要读懂本体，只需要测量它**。

---

## 命令行工具

```bash
# 校验整个仓库（CI 也用这条）
python tools/validate.py all

# 生成本地品鉴报告骨架（模板可继续编辑）
python tools/taste.py template stews/STW-0000-root-broth --model gpt-4o -o tasting.yaml

# 汇总全锅索引（打印统计表）
python tools/summarize.py
```

更多用法见 [AGENTS.md](AGENTS.md) 与各工具 `--help`。

---

## 相关论文

| # | 论文 | 笔记 |
|---|---|---|
| 1 | [Prompt Compression for Large Language Models: A Survey](https://aclanthology.org/2025.naacl-long.368/) | 硬/软压缩全景分类，Stew 在此定位为“硬过滤+进化搜索+内容寻址锅”。 |
| 2 | [Compressing Prompts for Accelerated Inference of Large Language Models](https://aclanthology.org/2023.emnlp-main.825/) (LLMLingua) | 小模型估计困惑度过滤低信息 token，最高 20 倍压缩；`cook-v1` demo 与此同族，但 Stew 叠加多代进化与盲测。 |
| 3 | [Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression](https://aclanthology.org/2024.findings-acl.57/) (LLMLingua-2) | 将 LLMLingua 蒸馏为轻量分类器，更快更忠实；可直接作为 `STEW_COMPRESSOR_CMD`。 |
| 4 | [Learning to Compress Prompts with Gist Tokens](https://openreview.net/forum?id=2DtxPCL3T5) (GIST) | 把提示词压为若干 `<gist>` token，不可读但等效——“乱码有效”的软压缩先例，印证模型绑定与 `tasting.yaml` 三绑定。 |
| 5 | [Generalized Prompt Compression for Large Language Models](https://arxiv.org/abs/2408.03094) (500xCompressor) | 编码器-解码器将提示压为 1–16 个 KV token，最高 480 倍压缩；只能用盲测评判，呼应 A/I 原则。 |
| 6 | [Optimizing generative AI by backpropagating language model feedback](https://www.nature.com/articles/s41586-025-08661-4) / [Automatic “Differentiation” via Text](https://arxiv.org/abs/2406.07496) (TextGrad) | 文本梯度反向传播 `TGD`，以 `loss.backward()` 优化提示词/解/代码；为 Stew 提供梯度式进化算子。 |

## 许可

本仓库采用 [MIT](https://github.com/KFERMercer/Stew/blob/main/LICENSE)（许可证文件托管于远程仓库）。锅使众人，众人养锅。血系顶端的署名会随锅永久流传。

## 灵感来源

本仓库的核心构想来自 [@joelhooks 在 X 上的这篇帖子](https://x.com/joelhooks/status/2097173680795046087)。
