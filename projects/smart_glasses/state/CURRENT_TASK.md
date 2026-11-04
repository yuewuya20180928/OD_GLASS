# CURRENT_TASK —— 当前在做什么 (board_progress.py 会读前 4 行)
2. ★[在跑] **v25 = 8层 + 预算×6 + 全部修复** (PID 121357, 07:14:45 起, 写官方板, timeout 14400s, 日志 /tmp/gen_v25.log 实时) ⇒ ★**这是第一块带齐所有修复的板**: 新排版F5+TP贴伙伴 · NPTH全层障碍 · USB-C丝印→F.Fab · In3.Cu平面 · 中途落盘先commit · cleanup真删 · 身份记账 · 落板自检 · meander v3
1. 最高优先级: 自研 demo 主板 → 可下单 (ISS-181/182) —— ★G1 缺口 = PCB 未布线 (官方板 = 8层板: 21980 段/530 过孔/unconnected 87/DRC 11; parity 已全过 check_pcb_nets rc=0)
3. ★★[待 v25 落盘后] 落板验收三看: ① `[CLEAN]` 零长/悬空/孤立过孔数 ② **新增的"落板自检: 板上 N 段 == 内存 M 段"** ③ `[SUM]` 段数 vs 板上实测段数 (差 ≈577 ⇒ 回归)
4. ★★[已修 07:20] "中途落盘先 commit"的回归 (我自己引入, 同事抓到): cleanup 只改内存列表删不掉已画进板的 ~565 零长段 ⇒ **已加 `_drop_committed()` 真删**; `_done_tracks` 按下标记账会被 cleanup 重排打乱 ⇒ **改按 id(元组) 身份记账**
5. ★★[已修 07:25] 差分配平 `add_meander_v3`: v2 用"剩余差值反算凸起高度" ⇒ **差越大 a 越大 ⇒ 超 a≤3 上限 ⇒ 一个凸起都加不上** ⇒ v3 **固定 a=3.0 反算每凸起 +5.12mm** ⇒ Δ32.4 = 7 个凸起; 候选直段门槛 1.2→0.8mm
6. ★[已修 07:15] parity 闸门: ★**检查器与生成器口径不一致** —— ① USB-IF 合并写法只改了生成器 ② J_USB_C 的 A8/B8 按 USB-IF 规范本就是 NC ⇒ ★**check_pcb_nets rc=0** (C1/C2/C3 全 ✅)
7. ★[已修 06:40] NPTH 孔 = 所有层障碍 + 0.25mm 孔净距 (⇒ 14 条 hole_clearance 全消) · USB-C 位号→F.Fab (⇒ 11 条 silk_over_copper)
8. ★[已修 06:40] 6层/8层都补回 **In3.Cu GND 平面** (原先只有 B.Cu+In1.Cu ⇒ In2/In4 底下没回流面)
9. ★[已修 07:00] 排版第二版: ★**>100mm 长线 15→5 条** (平均 68.2→51.9mm) ⇒ 三区分带装箱 (左下角/右上/其余) + 测试点贴伙伴件
10. ★[已修 06:55] 发布前闸 (只拦板不拦文档) + 落盘时刻闸 (量/推都必须过) + 三道闸串成证据链
11. ★[已纠正 07:00] RAIL_SOM_DCIN **不是**封装级问题: 实测已布出 15 段(全 F.Cu), 7 焊盘 6 个有铜, 只剩 pad 91↔93 ⇒ 路由器漏了一条腿 ⇒ **不卡下单**
12. 待办: v25 落盘 ⇒ ① 重跑差分对全审计 (15 对单边零铜 + Δ 超限) ② unconnected 87→0 ③ DRC 11→0 ⇒ 齐了才跑 verify_and_release.sh 出放行清单
13. 纪律: 同一块板只能一个写者; 数字只认机器读数; 实验臂一律 PCB_OUT 隔离; 官方板除生成器外还有 fix_dangling_*/check_pcb_drc/GitHub 同步 cron 会写 ⇒ 落盘后立刻数段数, 异常用 state/.lastgood/ 或 /tmp/board_last_good.kicad_pcb 回滚
