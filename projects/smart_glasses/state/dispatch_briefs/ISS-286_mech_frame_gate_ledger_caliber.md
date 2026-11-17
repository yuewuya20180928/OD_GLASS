★**ISS-286 · mech-lead 任务书 —— ★★【MECH 侧坐标归一闸 `check_board_frame_coords.py` C4 落表后基线过期 ⇒ 改成「落表台账为准」口径】★★** ★ (main · 2026-11-17 11:3x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 11:3x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-286 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 门禁机制收口 · 零写板 · 零落表**★

---

## ① 病灶 (★main 11:2x 本机实跑, 原样★)

★**A1+A2 落表 (2026-11-17 09:58:16 · rc=0) 之后, 你自己的坐标归一闸变红了**:

```
$ python3 MECH/check_board_frame_coords.py ; echo rc=$?
   ✅ HW/PCB/demo_mainboard.kicad_pcb 基线 611b869e13518c3c023fb178f91a0075 ⇒ 现值 611b869e13518c3c023fb178f91a0075
   ✅ HW/PCB/demo_mainboard.kicad_pro 基线 3e504d2be83152e337949723e909be1b ⇒ 现值 3e504d2be83152e337949723e909be1b
   ❌ HW/netlist_v1.csv 基线 e06c1dd633566aa44732762c2ff99d1c ⇒ 现值 2f17650cfbef48d5efd71821505c3343
   ❌ HW/netlist_v1_pins.csv 基线 287e7861a0d1007748d92d9fbecdd490 ⇒ 现值 6ea65fecdf95902e47330083d140d455
   ❌ HW/BOM_v1.csv 基线 94642d07a69e8d60dd2af57f69b93607 ⇒ 现值 ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd
   ❌ C4 受保护件被改: (上面三件逐件再报一次)
【结论】❌ 有检查项判红        rc=2
```

★**★病根 (★和 ISS-273 是同一个病★)**: ★**C4 把【网表/脚表/BOM 的 md5】写死成基线 ⇒ 上游一次【合法落表】就把这三件换掉 ⇒ 闸红 ⇒ 而真源【没被偷换】** ★
⇒ ★**这不是「真源被改了」, 是【判决源选错了】** ★

★**★先例 (★已跑通, 照抄口径, 别自创★)**: ★**ISS-273 (MECH 侧, 07-17 09:0x 已 verified)** ⇒ ★**把 C21/G5b 的判决源从【域侧锚点副本】换成【落表台账最新记录】⇒ 合法落表不再红, 而「悄悄换真源」仍然红** ★ ⇒ ★**ISS-275 = SW 侧同构 (已 verified)** ★

---

## ② 要交的 (★每件都能独立验收★)

1. ★**改成「台账为准」口径**: ★**C4 对【网表 / 脚表 / BOM】三件的判定改为: 盘上 md5 == 落表台账 (`HW/SCHEMATIC_LANDING_V1_LANDED.md`) 里该文件最新登记的 md5** ⇒ ★**合法落表 ⇒ 自动前移 ⇒ 绿** ★ ⇒ ★**而【盘上 md5 在台账里查不到任何登记】⇒ 红** ★ ⇒ ★**台账被偷改 / 链头不唯一 / 链断 ⇒ 红 (fail-closed 三条一条不许动)** ★
2. ★**★不许只是把基线数字改成新值★** ⇒ ★**只改数字 = 下一次落表又红一遍 (★这正是 ISS-273 之前的病★)** ★ ⇒ ★**判据的【取值来源】必须变, 不是【取值】变** ★
3. ★**板 / `.kicad_pro` 两件的基线照旧写死** (★它们是【真·不许变】的件, 落表链不管它们★) ⇒ ★**C4 的这两条一条不许动** ★
4. ★**反向用例 (★至少 4 条, 每条贴原样 rc★)**:
   | # | 构造 | 期望 |
   |---|---|---|
   | ① | ★**台账里有该文件的最新登记, 盘上 == 台账 ⇒ 放行** ★ | **绿** (★合法落表不再红★) |
   | ② | ★**台账里查不到该文件的任何登记, 盘上是别的值** ★ | **红** (★悄悄换真源★) |
   | ③ | ★**台账里有登记, 但盘上 ≠ 台账登记值** ★ | **红** |
   | ④ | ★**台账被手改 (登记值与盘上凑成一致, 但单号/文件名/前后 md5 四项不齐)** ★ | **红** (★四项不齐不许放行★) |
5. ★**交卷单 + 分片**: ★**`HANDOFF/2026-11-17_mech-lead_ISS286_坐标归一闸台账化.md` (B1~B6)** ★ + ★**`python3 state/frag_write.py --agent mech-lead`** ★

## ③ 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_board_frame_coords.py            # 期望 rc=0 (C1~C4 全过)
python3 MECH/check_board_frame_coords.py --selftest   # 期望 rc=0 (★原有 6 条一条不许少 + 新增 4 条★)
python3 MECH/check_demo_struct_truth.py               # 期望 rc=0 (23/23) ⇒ ★**不许把你的老闸弄红★**
python3 state/merge.py && python3 state/gate_check.py # 期望 rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变★★
```

## ④ 边界

★零写板 · ★零落表 (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `MECH/check_demo_struct_truth.py` 与其它既有判据脚本的语义** ★ · ★**不许放宽 fail-closed 三条** ★ · ★不碰 `HW/` / `SW/` 的文件与分片 (★只交叉引用 ISS-273 的口径★) · ★零外发 · ★**不替老板拍板** ★ · ★**不自签 issue_log** ★

## ⑤ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架** ★ · ★**长任务 `nohup` 后台 + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少写盘一次** ★ · ★**分片写完 `grep` 校验自己的 key 在不在 (★`frag_write.py` 无锁★)** ★
