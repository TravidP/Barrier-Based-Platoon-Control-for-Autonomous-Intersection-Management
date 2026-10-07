# 双八字双路口研究设计

`main.pdf`：完整英文版在前，完整中文版在后。

`main.tex`：主文件。正文为 `report_body.tex`，两种语言共用公式与图形几何；修改文字时编辑对应的 `\bi{English}{中文}`。

## 编译

需要 XeLaTeX、BibTeX、latexmk（TeX Live / MacTeX）。在本目录执行：

```sh
latexmk -xelatex -interaction=nonstopmode main.tex
```

`references.bib` 由 BibTeX 管理；中文采用 TeX Live 自带 Fandol 字体。

## 几何与配置

```sh
python3 geometry_check.py
```

该命令仅检查道路数学几何并生成 `geometry_summary.json`，无需第三方 Python 包。`proposed_config.json` 是设计登记表，不是可直接运行的 CARLA 配置。零值缺失项以 `null` 或说明保留，等待仿真实施前校准。

完整计划在上级目录的 `double_figure_eight_plan.md`。`translation/` 保存翻译分析、初稿与审校记录；`qa/` 保存版面检查结果。原报告没有被修改，本文件包不包含新增仿真实验结果或安全证明。
