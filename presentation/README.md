# Research idea discussion

## 决策屏障框架：中英文图解演示

- `decision_barrier_zh.pdf`、`decision_barrier_en.pdf`：中文和英文各 **18 页**，16:9 静态图解，适合约 15–20 分钟汇报。
- `decision_barrier_zh.tex`、`decision_barrier_en.tex`：两种语言的编译入口。
- `decision_barrier_common.tex`：共用逐页内容、公式及图示；`\bi{English}{中文}` 控制语言。
- `decision_barrier_style.tex`：共用字体、版式、颜色和 TikZ 道路/车辆/冲突图组件。
- `translation_glossary_en_zh.md`：中英文术语表；`translation/` 保存英文文案及分析、初译、审校、修订、润色记录。

新稿依照论文 Idea Note（2026-07-08）讲解原始方法，与下面的既有 QP 研究提案是两套独立材料。所有算例参数均为示意，实验均为未来计划。

内容顺序：第 1–10 页为两层结构、到达时间、激活判断、加权修正、一步计算及边界；第 11–14 页为 Case A/B；第 15–17 页为五阶段实验；第 18 页为单页 baseline/KPI 对照。

### 编译新稿

需要 XeLaTeX、latexmk、Beamer、ctex/Fandol、TeX Gyre Heros、TikZ 与 PGFPlots（TeX Live/MacTeX）。在项目根目录执行：

```sh
sh presentation/build_decision_barrier.sh
```

也可进入 `presentation/` 后单独编译：

```sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error decision_barrier_zh.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error decision_barrier_en.tex
```

两份入口必须与共用文件放在同一目录。全部图示和公式均由 LaTeX 绘制，没有外部图片依赖。构建脚本将中间文件放入临时目录，仅把最终 PDF 复制回来。

### 内容约定与来源

- 路径方向用 NS/SN/EW/WE 表示，示意采用分离直行车道。Case A 有两条唯一交叉冲突边，Case B 有四条。
- 区分对称裕度与有序裕度。原始 `-1/h` 在零点奇异，负裕度侧符号反转，激活阈值处跳变；本稿明确标注这些边界。
- 若制动修正为负加速度，“最强单项制动”取 `min`。这澄清了原文 `max` 与其文字解释之间的符号问题，原论文未被改写。
- 演示中输入 `u` 的算例单位为 m/s²，权重含 m/s 增益；一步恒加速度更新得到 `h: 0.50 s → 0.55 s`，不是仿真实验或安全证明。
- 原文的队首候选规则与“占用车辆保留至车尾清空”的后续实现要求分开表述。能耗需要指定模型，预计到达时间不等于碰撞 TTC。
- 翻译使用 [baoyu-translate v1.117.3](https://github.com/JimLiu/baoyu-skills/blob/1567581c26ec29f4216c6e6835415bf30343b0e3/skills/baoyu-translate/SKILL.md)，固定提交 `1567581c26ec29f4216c6e6835415bf30343b0e3`，MIT 许可。采用 refined 流程，项目偏好见 `../.baoyu-skills/baoyu-translate/EXTEND.md`。
- 比较方法与 KPI 来自论文实验章节；最后一页附 SUMO 信号控制、TripInfo 与 Ames 等 CBF-QP 文献的可点击来源。

## 既有英文研究提案

- `idea_discussion.pdf`：英文汇报，12 页主体＋4 页备份，主体约 15 分钟。
- `idea_discussion.tex`：可编辑 Beamer 源码，16:9，无外部图片或参考文献文件依赖。
- `speaker_notes_zh.md`：中文总结、逐页讲稿、时间分配与问答准备。
- `research_plan_zh.md`：方法边界、里程碑、实验与指标、来源记录。

## 编译

安装包含 Beamer、fontspec、TeX Gyre Heros 的 TeX Live 或 MacTeX。进入本目录：

```sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error idea_discussion.tex
```

也可以运行两次：

```sh
xelatex -interaction=nonstopmode -halt-on-error idea_discussion.tex
xelatex -interaction=nonstopmode -halt-on-error idea_discussion.tex
```

本提案允许 V2X/路侧协调，第一版采用联合 QP。没有已完成实验；没有对新方法的无条件安全或效率承诺。原始 figure-eight 理论及 BaIP 报告待核实。中文 Markdown 含 LaTeX 公式，可在支持数学渲染的 Markdown 阅读器中查看。
