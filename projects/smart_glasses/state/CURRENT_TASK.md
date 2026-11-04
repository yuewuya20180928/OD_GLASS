# CURRENT_TASK —— 当前在做什么 (board_progress.py 会读前 4 行)
2. ★[在跑] **两轮并行**: v21 = 6层/160×100 + 预算×6 (PID 109262, 官方板, timeout 10800s) ＋ v22-8L = **8层** + 预算×3 (PID 109509, **隔离输出** /tmp/board_8l_v3.kicad_pcb, 不碰官方板) ⇒ ★**两个方向并行对比**: 预算 vs 层数
1. 最高优先级: 自研 demo 主板 → 可下单 (ISS-181 / ISS-182) —— ★当前关 G1, 缺口 1 项 = PCB 未布线 (官方板 = v20 的 22386 段/504 过孔, **但没有铜皮** ⇒ v21 才是第一块带平面的板)
2. ★★**瓶颈判断修正 (05:20)**: ★**"加层"方向之前被我误杀** —— 180×120 实验只否掉了"更大面积"(仍是 6 层), **没否掉"加层"** ⇒ 代码里我自己写的注释: "400 个 0.4mm pitch BTB 焊盘 ⇒ 3 个信号层的 escape 面积不够 ⇒ unconnected 卡在 ~90" ⇒ ★**现在实测 97 ≈ 那个平台** ⇒ ★**瓶颈 = escape 面积(层数), 不是 A\* 预算** ⇒ 8 层必须真跑一次
2. ★[已落盘] v20 实测 (05:00:44): 走线 22386 段 / 过孔 504 / unconnected 97 / DRC 17 / ★**用时 2799s (46.6 分钟)** / 原子替换 ✓ / 自动备份 ✓ / parity 缺失14→**2** 多余12→**0**
3. ★[已修] 平面铜皮: v20 日志 "⚠️ 平面重填失败: 'NoneType'..." ⇒ tmp 文件名缺 .kicad_pcb ⇒ LoadBoard 返回 None ⇒ ★**整板铜皮没填** (只有 2 处 filled_polygon) ⇒ 没有 GND 回流面 ⇒ v20 的 97/17 **不是最终成绩** ⇒ 已修: tmp 名改 xxx.tmp.kicad_pcb
4. ★[已修] 排版丢器件: 撞禁放区 (USB-C 座区) 时 `continue` ⇒ ★**器件被静默丢掉** ⇒ C_BULK_SENSOR_AVDD 封装压根没画 ⇒ 这就是 parity"缺失2"的来源 ⇒ 已修: 换行后重试 (60 次保护) + 被丢器件全部打印
5. ★[已修] parity 根因: _is_pad_name 认 USB-IF 合并写法 ("A6+B6" / "A4+A9+B4+B9") ⇒ 缺失 14→2 / 多余 12→0
6. ★[已修] 原子替换路径 bug (平面重填 LoadBoard(PCB) → LoadBoard(_tmp_pcb)) + 每次成功自动备份 /tmp/board_last_good.kicad_pcb ⇒ 11-05 03:49 那轮就是因此丢了 v15 的 92/17
7. ★[已修] 放行触发器: ① 探测 /proc 里真正在跑的那一轮 ② 落盘标记 "已原子替换正式板" + 官方板 >0 段走线 ③ ★**板侧判据** (板 mtime > 留证 mtime 且有走线且没量过 ⇒ 补测) ④ 修 `grep -c || echo 0` 造成的整数错 (空板闸本来静默失效)
8. ★[已修] 衔接脚本 chain_next_round.sh: 三道闸 (走线>0 / 落盘标记 / parity 全过) + ★**A 闸: 起下一轮前先自验刚落盘的板** + timeout = 1200×倍数
9. ★[已装] 板面现状: 832 焊盘, 有网 480 / 无网 352 (无网的全是 SoM 4×100pin BTB 未分配脚 + USB-C 的 A8/B8/壳体 ⇒ ★**设计如此**, 不是 bug)
10. 待办: SoM BTB 密集区剩 97 个脚布不动 (预算耗尽 54 / 真堵死 43) ⇒ ★v21 用 mult×6 攻预算
11. 待办: 差分对 N 侧缺铜 3 对 (USB_D_N_SRC / CSI_D0_D0_N_SRC / CSI_D0_D0_N) + Δ 超限 4 对 (USB_TYPEC 7.18 / CSI_D0_CK 11.78 / DSI_D0_D0 24.83 / DSI_D0_D3 53.09mm, 门限 0.13) ⇒ 要改对侧走廊耦合
12. 收尾: unconnected=0 + DRC=0 + Gerber 重出 ⇒ 投板放行清单 (G1 过) ⇒ 用 state/verify_and_release.sh 一键自验+放行
13. 纪律: 同一块板不能我和子 agent 同时写; 回执数字必须能在留证文件里对上; 播报只用机器读数; 当前步骤要写进本文件(否则播报落后一轮); ★并行实验一律 PCB_OUT 隔离 + 不得写 .layout_done.json; ★**官方板除生成器外还有 fix_dangling_*/check_pcb_drc/GitHub 同步 cron 会写 ⇒ 落盘后要立刻数段数, 异常用 /tmp/board_last_good.kicad_pcb 回滚**
