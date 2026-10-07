# Critical review against the English source

Reviewed all 18 sections against the source and project glossary.

1. Section 04: “maneuver priority” became “通行方向优先级”, which narrows the meaning and can be confused with lane direction. Use “行驶动作优先级”.
2. Section 01: “构想札记” is unnatural in this academic presentation; use “研究构想”. Prefer “基于屏障的车队控制” for the title.
3. Section 07: the embedded English “sum over ...” is not suitable final Chinese. Typeset the full double sum in LaTeX, preserving indices and weights.
4. Section 14: “保留其表示” is literal and vague. Say “持续将其纳入冲突检查，直至车尾驶离”. Preserve that this is an additional implementation requirement.
5. Section 17: “存储容量有限的路段” is a computing calque. Use “可容纳车辆数有限的连接路段”.
6. Section 18: “鲁棒性与成本” obscures that cost is computation time. Use “鲁棒性与计算开销”. Preserve energy-model conditionality and avoid interpreting estimated arrival time as collision TTC.

Arithmetic checked independently: T_A=3, T_B=5, h=.5, phi=-2, u_B=-1; the exact constant-acceleration update gives d_B^+=49.005, v_B^+=9.9, T_B^+=4.95, h^+=.55. No omitted scenario or KPI. No unsupported experiment result or safety theorem was introduced.

Slide adaptation must condense this prose while retaining the formula caveats and proposal status. All diagram prose is authored through the same bilingual macros; lane IDs and mathematical symbols stay unchanged.
