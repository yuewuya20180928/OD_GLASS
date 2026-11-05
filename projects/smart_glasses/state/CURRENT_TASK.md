# CURRENT_TASK —— 当前在做什么 (board_progress.py 会读前 4 行)
2. ★[在跑] **v27 三臂 (09:52 起)** (E=8层160×100 / F=10层160×100 / G=8层180×120, **各自 PCB_OUT 隔离 ⇒ 官方板不动**) ⇒ ★**共同新增: F7 排版 (PCB_PIN_CONN_CAM=1) + 差分对 N 侧出脚修复 (PCB_PAIR_ESCAPE_EXEMPT=1) + 浮点容差 1nm + 过孔查重** ⇒ ★**早期读数: 三臂差分对"N 未通"= 0 (v26 是 18/22) ⇒ USB_D_N_SRC / CSI_D0_CK_N_SRC 都 ok=True/True Δ=0.000** ⇒ ETA ~11:00
2b. ★★[09:55 真凶] **浮点容差**: `_stub_vs_routed` 判 0.4mm pitch 相邻出脚直道净距时 `need=0.4`, 实测算出 **0.3999999999999986** ⇒ 每一对相邻脚被判死 ⇒ **SoM BTB 全出不来 ⇒ 22 对里 17~18 对 N 侧 0 段铜** (unconnected 82/83 的头号来源) ⇒ 三处比较加 **1nm 容差** ⇒ 探针实测 6/6 个 _SRC 对 N 侧全部有铜 Δ=0.000 ring=2
2c. ★[09:52 官方板已换] v25 → **臂 A** (19070 段/407 孔) ⇒ ★**焊盘短路 (R_SER_USB_D_N.2↔Q_PG.1) 消失** ⇒ 剩 DRC 2 = **同点重复过孔** (落板自检已抓到: 板上 407 vs 内存 405) ⇒ 已加 `_via_exists` 查重 (v27 起生效)
2d. ★[09:56 chain_gate] ①网表✅ ②原理图✅ ③PCB 准入✅/准出❌(DRC2/unconn83) ④BOM✅ ⑤**投产资料包✅✅ (51 文件/19MB, 09:55 重出)** ⇒ ★**只剩 ③ 板子本身**
2e. ★[09:26 已交付] 叠层/阻抗: `state/add_stackup.py` (8层/总厚1.600mm/外铜0.035/内铜0.018/prepreg PR2116+core FR4/ENIG) ⇒ ★**KiCad 10.0.8 回读通过 (走线/过孔数不变)** + 规格书 `HW/PCB/STACKUP_IMPEDANCE.md` ⇒ ★**踩坑: 往 .kicad_pcb 塞裸文本标记行 ⇒ KiCad 静默解析失败返回 None**
2f. ★[09:54 已修] `state/verify_and_release.sh` 三处 `echo "rc=$?"` 把 `$?` 吃掉 ⇒ DRC/chain_gate/stage_gate 挂了也不 FAIL ⇒ ★**自验永远退 0** (这正是上次"带短路板被推上 GitHub"的温床) ⇒ 已改成先存 `_rc=$?` 再打印
2g. ★[09:55 注意] `issue_check rc=1` (逾期未闭环 6 条, 多数归 boss/其他 lead) ⇒ ★**即使板子全绿, 这一条也会挡住放行章** ⇒ 需老板定口径
1. 最高优先级: 自研 demo 主板 → 可下单 (ISS-181/182) —— ★G1 缺口 = PCB 未布线。★⚠️ **官方板 (v25) 带短路 (R_SER_USB_D_N.2 ↔ Q_PG.1 焊盘搭接) ⇒ 绝对不许投板, 只作过程产物** ⇒ 已在生成器加短路闸门+排版避让修掉, 新排版实测无搭接。★**v25 已落盘 (08:14:50)**: 17664 段 / 413 过孔 / **unconnected 82** / **DRC 2** / parity rc=0 / ★**落板自检通过 (板上17664==内存17664 ⇒ cleanup 回归没发生)**
3. ★★v25 的教训 (三条根因都已修, 待 v26 验证): ① **过孔判据过严** (halo[2] 半径 0.95mm ⇒ 密集区放不下任何过孔 ⇒ 长线不能换层 ⇒ 52 个"真被堵死"里的一部分) ⇒ 已加 `_via_exact_ok` ② **F5 排版把差分对远端连接器搬走** (CONN_CAM → (93.3,17.6) ⇒ 22 对 8→5) ⇒ 已钉回 ③ **halo 放松 (skip_pad_cells) 可能让 P 侧走进 N 焊盘邻域** ⇒ 已做开关 `PCB_SKIP_PAD_CELLS=0` ⇒ **臂 B 专门测**
4. ★★落板验收三看: ① `[CLEAN]` 零长/悬空/孤立过孔数 ② **落板自检"板上 N 段 == 内存 M 段"** ③ `[SUM]` 段数 vs 板上实测 (v25 三看全过 ✔)
5. ★★[已修 08:17] `落盘时刻印失败: name 'json' is not defined` (我改代码丢了 import) ⇒ ★**收工闸"段数 vs 落盘印"判据会失效** ⇒ 已修 + 手工补印 (at=1793837690 tracks=17664 vias=413)
6. ★[已修 08:20] **GND 下拉 20 个失败没救回** ⇒ 根因 = `_via_free_all` 用 halo[2] (0.95mm) ⇒ 已改 `_via_exact_ok` ⇒ 冒烟: `inpad_busy`/`narrow` 消失 ✔ ⇒ ★**顺带松开长线换层**
7. ★[已修 08:10] **差分对端点连接器钉回** (`_PAIR_ENDPOINT_CONN = CONN_CAM/CONN_LIGHT` 不参与伙伴件搬移) ⇒ 实测 CONN_CAM 回到 x=78.90..93.90 (与旧板 x 区间一致) · parity 全过 · 零掉件
8. ★[已修 08:00] meander v3 (min_len 0.3 + 自适应凸起高度 3.0/2.0/1.2) + 配平后重算 Δ 写回
9. ★[已修 07:40] **层数通吃 6/8/10**: ROUTE_LAYERS/CU_LAYERS/平面层/RLAY_NBRS/LNAME 全按层数生成 (10 层 ⇒ 5 信号层) ⇒ ★**若最终定 10 层必须补真叠层+阻抗规格** (投板交付项)
10. ★[已修 07:20] cleanup 真删 (`_drop_committed` + `board.Remove`) + 身份记账 (`id(元组)`) + 落板自检 ⇒ ★**v25 实测无回归**
11. ★[已修 07:15] parity 闸门 (`check_pcb_nets rc=0`) · ★[已修 06:40] NPTH 全层障碍 + USB-C 丝印→F.Fab + In3.Cu 平面
12. ★备选路 (工业级): **KiCad 10 自带 ExportSpecctraDSN/ImportSpecctraSES** ⇒ **DSN 已导出 51914 字节** ⇒ ★**[09:27 实测] freerouting 1.6.0 (JRE17 可跑) 启动即 `java.awt.HeadlessException` ⇒ 1.6/1.9 都需要 X ⇒ Xvfb 装不上 (apt 权限) ⇒ ★**唯一无头路径 = freerouting 2.1.0 + JRE 21** ⇒ ★**[09:28] JRE21 正在下 (github 实测 114KB/s, 9.4/45MB); ★**注意: `~/tools/jdk-21.0.5+11-jre` **是残缺的** (缺 libjli.so ⇒ java 起不来) ⇒ 别再以为已装好** ⇒ 脚本 `state/freeroute_run.sh`
13. 纪律: 一个板一个写者; 实验臂一律 PCB_OUT 隔离; 数字只认机器读数; ★**官方板只由赢家轮落盘** ⇒ v26 三臂比"布不动的脚"个数后再选
