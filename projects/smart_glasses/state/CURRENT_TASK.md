# CURRENT_TASK —— 当前在做什么 (board_progress.py 会读前 4 行)
2. ★[在跑] A/B 同预算对照 (8层×3 PID 114052 写官方板 / 6层×3 PID 114067 隔离) ⇒ ★**chain_v25.sh 已武装**: 出 EXIT= 即自动比『布不动的脚』⇒ 起 v25 (赢的层数 + 预算×6 + 新排版 + NPTH + In3.Cu 平面 + USB-C 丝印修正)
1. 最高优先级: 自研 demo 主板 → 可下单 (ISS-181/182) —— ★G1 缺口 = PCB 未布线 (官方板仍是 v21: 22642 段/521 过孔/带铜皮/parity 全过, unconnected 101 / DRC 25)
3. ★★**8 层不是"证伪", 是被异常吞了** (06:15 定案): 8L 那轮**布完只剩 78 个脚** (v20=97 / v21=101) ⇒ ★**比 6 层好** ⇒ 但 `gen_pcb_routing.py:1953` `CU_LAYERS[li]` 越界 (写死 6 项, 8 层时 li=6) ⇒ IndexError ⇒ except 把整轮结果吞掉并落了个 0 走线骨架 ⇒ **已修** (CU_LAYERS 按层数生成 + 8 层平面层 (1,7))
4. ★[已修] 布线异常 ⇒ **不再落盘骨架** (以前 except 后继续写盘 ⇒ 一轮好成绩作废 + 官方板变空板) ⇒ 现在 sys.exit(2) 保留上一块好板
5. ★[已修] `tools/diff_pair_audit.py` 硬编码 PCB 路径 (无视 argv) ⇒ **对比工具拿官方板的数套别的板** ⇒ 已改成 `sys.argv[1]`
6. ★[已修] 触发器加**落盘时刻闸**: 落盘时写 `HW/PCB/.layout_landed.json` {at, tracks} ⇒ 自验要求 |板mtime-at|<=10s 且 段数一致 ⇒ **中途存盘覆盖过的板不许量** (05:57 自己污染自己证据的根因)
7. ★[已修] `gen_pcb_routing.py:2208` 中途落盘无视 PCB_OUT (并行实验污染官方板) ⇒ 已改成同一口径
8. ★[已修] 排版丢器件 (撞 USB-C 禁放区时 continue ⇒ 器件静默消失) ⇒ 改成换行后重试 ⇒ C_BULK_SENSOR_AVDD 回到板上 ⇒ ★**v21 parity 全过**
9. ★[已修] 平面铜皮没填 (tmp 文件名缺 .kicad_pcb ⇒ LoadBoard 返回 None) ⇒ v21 是第一块带 GND 回流面的板
10. ★[已修] 自动备份固定名会被实验板覆盖 ⇒ 实验板用独立文件名
11. 待办: 差分对 **14 对单边零铜** (N 侧整条没布出来) + **7 对 Δ 超限** ⇒ ★**先攻"能不能布出来"(层数/escape), 再攻配平** —— 零铜的配平没意义
12. 待办: 8 层的**叠层方案**要按 STACKUP.md 定稿 (现在 L1信号/L2 GND/L3信号/L4空/L5信号/L6空/L7信号/L8 GND) ⇒ 下单前必须过电气评审
13. 收尾: unconnected=0 + DRC=0 + Gerber 重出 ⇒ G1 过 ⇒ `state/verify_and_release.sh` 出放行清单 ⇒ 才盖章
14. 纪律: 同一块板只能一个写者; 数字只认机器读数; 实验一律 PCB_OUT 隔离; 官方板除生成器外还有 fix_dangling_*/check_pcb_drc/GitHub 同步 cron 会写 ⇒ 落盘后立刻数段数, 异常用 /tmp/board_last_good.kicad_pcb 回滚
