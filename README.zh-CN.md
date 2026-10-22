# AI生意经 · 面向实体创业者与企业家的 AI 经营工作流

<!-- REPOSITORY_RETIRED_20261021 -->
> **已归档／Archived — 停止维护。** 本仓为历史公开试用版，仅供历史回查；当前个人 Agent 与 Skills 统一由 `AI-Agent-Skills-Private` 私有主仓维护，需现有私仓访问权限。本公开仓不再作为现役 Agent／Skill 版本源。
> This public trial is no longer maintained. Existing source, license, examples and commit history are retained for reference.


**让 AI 进入实体创业者和企业家的真实经营工作。**

围绕门店、制造、实体服务等经营场景，从客户关心的问题出发，把产品、服务、方法与经营经验讲明白，完成朋友圈表达和方案展示。

首批公开选题、文案、朋友圈写作与HTML四项能力，从长期自用工作流中整理，由 Codex 参与整理与维护。当前公开范围聚焦经营内容表达，获客、成交与经营成效仍需真实使用验证。

| 工作 | 对应的经营任务 |
| --- | --- |
| [选题](skills/topic-selection/SKILL.md) | 从客户问题、行业场景与已有材料中，找到值得讲的题 |
| [文案](skills/article-writing/SKILL.md) | 把产品、服务、方法和经营经验写清楚，也能定向改稿 |
| [朋友圈](skills/moments-writing/SKILL.md) | 将真实经营观察、产品说明或常见问题写成一条自然表达 |
| [HTML](skills/html-story/SKILL.md) | 把方案、介绍和经营判断做成可阅读、可演示的独立网页 |

## 直接开始

让能读文件的 AI 助手完整读取命中的 `SKILL.md`，提供你有权使用的材料。例如：

> 读取 skills/topic-selection/SKILL.md，用 skills/examples/source.md 为小餐馆经营者选一个值得写的题。保留虚构示例身份，不把示例写成经营成绩。

需要成稿再进入文案或朋友圈，需要网页再进入 HTML。每项可以独立使用；只改一段不重跑整条链。安装时复制整个 Skill 文件夹，按客户端官方说明操作；本仓库不会修改全局设置。

[完整示例](skills/examples/README.md)提供原料、选题、文章、朋友圈和可打开的 HTML。示例全部虚构，不含真实客户、私人经营资料或账号信息。

## 运行条件与状态

Skills 需要可读取文件的 AI 助手，模型服务可能收费。没有附带私人资料库、连接器、账号、定时任务或发布权限。HTML 图示脚本可在 Python 3.10+ 下运行，无第三方依赖；生成结果是待嵌入页面的片段。

选题、文章与朋友圈是本轮模型执行示例，仍需使用者判断质量。HTML 阅读示例已做390×844与1440×900截图回看；演示/双模式、独立客户端安装和真实业务验收待验证。脚本运行或文件检查不代替这些验收。

这四项是有明确范围的公开改编，原私有工作流保持独立。来源与改编说明见 [ORIGINS](skills/ORIGINS.md)。其他能力不在首批发布范围。

主要维护者：[savannahx0uybzri53ntk7c-tech](https://github.com/savannahx0uybzri53ntk7c-tech)。采用 [MIT许可](LICENSE)，贡献与问题反馈见 [CONTRIBUTING](CONTRIBUTING.md)。

项目处于早期，不宣称已有外部用户规模、商业结果或 OpenAI 支持。
