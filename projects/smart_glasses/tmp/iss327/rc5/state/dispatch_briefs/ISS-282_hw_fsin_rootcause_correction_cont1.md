★**ISS-282 · hw-lead 任务书 (★续做第 1 次★) —— 「板只改一次」的【`FSIN_OUT` 根因订正 + 布线前置闸】★★**

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 11:0x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划) · ★**续做重派** ★
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-282 (★status 仍是 fixing ⇒ 本趟是【续做同一单】, 不是新单★) ★
> ★**原任务书**: `state/dispatch_briefs/ISS-282_hw_fsin_rootcause_correction.md` (★**全文照旧有效, 一字不许删**★) ★
> ★**本单性质**: ★**内部活 · PCB 线 · 纯规格 + 作业包追加式订正 + 机器闸类** ★ ⇒ ★**零写板 · 零落表 · 零跑布线臂 · 零跑生成器 · 零改网表/脚表/BOM · 零改既有判据阈值** ★ ⇒ ★**不是老板级拍板** ★ ⇒ ★**不用问老板** ★

---

## ★① 上一趟死在哪儿 (★main 本机实查, 不猜★)

★**会话**: `agent:hw-lead:subagent:169ee40f-64eb-4cda-b473-eb9059efdfc5` · ★**10:04~10:22** · ★**status=done 但 `abortedLastRun=true`** (★网关重载把它掐了★) · ★**transcript 最后一句**: 「Diagnosed: my landing-ledger window matched an older section (line 108/204) instead of §16.2 (line 1270), and the anchor's pad refs need splitting. Let me fix both.」 ★ ⇒ ★**它自己已经发现了两个病灶, 但还没改完就被掐了** ★

★**盘上现状 (★main 实测 mtime/size★)**:

| # | 交付物 | 状态 |
|---|---|---|
| 1 | `HW/PCB/FSIN_OUT_ROOTCAUSE.md` | ★**在盘 20128 B (10:16)**★ |
| 2 | `HW/check_fsin_rootcause.py` | ★**在盘 39479 B (10:19)** ★ ⇒ ★**但主模式 rc=1 (3 项红) ⇒ 闸还没修好** ★ |
| 3 | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §6.2 | ★**追加行在 L388 (老 S8 行 L387 逐字仍在)** ★ ⇒ ★**老字零删除, 已合规** ★ |
| 4 | `HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md` | ★**只有骨架 2617 B · B1~B6 全是「待填」** ★ ⇒ ★**这一件等于零** ★ |
| 5 | `state/fragments/hw.yaml` | ★**没有 iss282 (mtime 09:22, 还是 ISS-281 那版)** ★ |

---

## ★② ★★main 本机实跑的 3 条红 + 根因 (★你照这个改, 别从零重查★)★★

★**main 实跑 (★原样 rc★)**:

```
$ python3 HW/check_fsin_rootcause.py            ⇒ rc=1  (D1 ✅ / D2 ❌ / D3 ❌ / D4 ✅ / D5 ❌)
$ python3 HW/check_fsin_rootcause.py --selftest ⇒ rc=1  (反向 8/10, ⑩ 正向对照也不绿)
```

### ★2.1 · D2 / D3 红 ⇒ 根因 = 【`find_pad` 的参数口径不对】★

★**闸里怎么调的** (★`HW/check_fsin_rootcause.py` L520~L521★):
```python
pa = find_pad(board, anchor.get("pad_a", "R_SER_FSIN.1"), "1")
pb = find_pad(board, anchor.get("pad_b", "TP_FSIN.1"), "1")
```
★**但 `find_pad(board, ref, num)` 的语义是 (★L358★)**:
```python
def find_pad(board, ref, num):
    for p in board.pads:
        if p[0] == ref and p[1] == num:   # ★p[0]=位号, p[1]=脚号★ ⇒ ref 不许带 ".1"★
```
★**⇒ 页面锚点块里存的是 `pad_a=R_SER_FSIN.1` / `pad_b=TP_FSIN.1` (★带脚号后缀★) ⇒ 拿去当 `ref` ⇒ 永远匹配不上 ⇒ 报「读不到那两个焊盘」★**

★**main 本机用【闸自己的解析器】实测 (★不改盘★)**:
```
Board("HW/PCB/demo_mainboard.kicad_pcb") ⇒ pads 834 / segs 18092 / vias 433
find_pad(b, "R_SER_FSIN", "1")     ⇒ ('R_SER_FSIN','1','FSIN_OUT', 93.3, 46.6, ...)   ✅
find_pad(b, "R_SER_FSIN.1", "1")   ⇒ None                                             ❌
find_pad(b, "TP_FSIN", "1")        ⇒ ('TP_FSIN','1','FSIN_OUT', 93.5, 49.6, ...)     ✅
```
★**⇒ 修法二选一 (★你定细节, 但下面两条不许破★)**:
1. ★**要么** 页面锚点块改成 `pad_a=R_SER_FSIN` + `pad_a_num=1` (★把脚号单独存★)
2. ★**要么** 调用点先 `ref.split(".")` 拆成 (ref, num) 再传给 `find_pad` (★**不许**放宽 `find_pad` 本身去"猜"★)
★**★不许弱化判据**: ★**拆完之后 D2/D3 必须实算出 main 09:2x 那两个数 (★`R_SER_FSIN.1` 距最近异网焊盘边缘 **1.1500mm** · `TP_FSIN.1` 距最近异网焊盘边缘 **1.3528mm**★) ⇒ ★**写死常量 = 不合格** ⇒ ★**闸必须自己从板面重算** ★

### ★2.2 · D5 红 ⇒ 根因 = 【取错了落表台账的那一段】★ (★就是你自己 transcript 里说的那个坑★)

★**闸里怎么取的** (★`landing_after_md5()` L452~L468★):
```python
idx = landing_txt.find("前后对照")     # ★★取【第一个】匹配★★
window = landing_txt[idx:]
cut = window.find("\n###")
```
★**⇒ 真盘上 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里 "前后对照" 至少出现两次** ⇒ ★**它命中了 L204~L207 那张【旧表】(基线 `c78f9912…` / 产物 `13f59a43dbd3…`) ⇒ ⇒ 允许集变成 {基线 `e06c1dd6…`, 落表后 `c78f9912…`} ⇒ ⇒ 现在的真值当然不在里面 ⇒ 假红★**

★**main 本机实测的落表台账真值 (★§16.2 · L1268~L1274★)**:
| 文件 | 前 | 后 | 变了? |
|---|---|---|---|
| `HW/netlist_v1.csv` | `e06c1dd633566aa44732762c2ff99d1c` | `2f17650cfbef48d5efd71821505c3343` | ★**是**★ |
| `HW/netlist_v1_pins.csv` | `287e7861a0d1007748d92d9fbecdd490` | `6ea65fecdf95902e47330083d140d455` | ★**是**★ |
| `HW/BOM_v1.csv` | `94642d07a69e8d60dd2af57f69b93607` | `ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd` | ★**是**★ |
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | 否 |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | 否 |

★**⇒ 修法**: ★**取该文件的【最新一条落表记录】** (★`rfind` 最后一处「前后对照」表 ★或★按台账里的落表单号/时间取最新★) ⇒ ★**不许把允许集写死成常量** (★下一轮落表 md5 又会变 ⇒ 写死 = 又一次假红★) ★
★**★不许放宽 D5 的 fail-closed**: ★**不在台账里登记过的 md5 ⇒ 仍必须红** ★

### ★2.3 · `--selftest` 8/10 ⇒ 因为沙盒里也是同 3 红 ★

★**沙盒是把真盘(板 + 落表台账)复制进去的 ⇒ D2/D3/D5 在沙盒里同样红 ⇒ ⑩「正向对照: 沙盒原样不动 ⇒ rc=0 (证明闸不是恒红)」自然也不绿★**
★**⇒ 修完 2.1 + 2.2 ⇒ 主模式应 rc=0 且 selftest 应 10/10 ⇒ ★**自测必须端到端跑真板, 不许只测纯函数** ★**

---

## ★③ 要交的四件 (★每件都能独立验收★)

1. ★**交卷单填满**: `HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md` (★**骨架已在盘 ⇒ 直接填, 不用重建★**) ★**B1~B6 六块不许留「待填」** ★ ⇒ ★**B3 贴原样 rc (主模式 + `--selftest` + 邻闸)★**
2. ★**闸修绿**: `HW/check_fsin_rootcause.py` ⇒ ★**主模式 rc=0 (D1~D5 全绿) + `--selftest` rc=0 (★条数只许增不许减★, 目标 10/10)** ★
3. ★**作业包追加行**: ★**L388 那行已经合规 ⇒ 一个字节都不许动 (★老 S8 行 L387 也一样★)** ★ ⇒ ★**本趟【不许】再追加第二行订正** ★
4. ★**分片**: `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead` 原子写★) ★**claim + artifact + status★ ⇒ ★**写完 `grep` 校验 `iss282` 在不在★**

★**必跑 (★全部本机实跑, 贴现场 rc★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fsin_rootcause.py; echo "rc=$?"
python3 HW/check_fsin_rootcause.py --selftest; echo "rc=$?"
python3 HW/check_onepass_commit_order.py; echo "rc=$?"          # ISS-280 的闸 (相邻, 别弄红它)
python3 HW/check_onepass_preflight_coverage.py --selftest; echo "rc=$?"
python3 state/merge.py && python3 state/gate_check.py; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… 必须逐字节不变★★
```
★**已知相邻红 (★不是你弄坏的, 但要在交卷单里写明★)**: ★**`HW/check_onepass_preflight_coverage.py` 主模式 rc=1 (P6 三个基线 md5 过期 ⇒ 09:58 授权落表后的正常后果) ★ · `SW/tools/timing_check.py` rc=1 (68/71) ★ ⇒ ★**这两道闸的收口在 ISS-283 (hw-lead) 与新开的 ISS-285 (sw-lead) 上, 不是本单范围** ★

---

## ★④ 边界 (★违反就是不合格★)

★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 一个字节不许动★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**零跑布线臂 / 零跑生成器** (★不许跑 `state/gen_pcb_routing.py` / `state/gen_pcb_netlist_board.py` / `state/gen_production_pack.sh`★) · ★**零改既有判据阈值** · ★**不许弱化 D5 的 fail-closed** · ★**不碰 `MECH/` / `SW/` 的文件与分片** (★只交叉引用★) · ★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★⑤ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` (★骨架已在 ⇒ 你是【填】不是【建】★)** ★ · ★**长任务一律 `nohup ... > logs/iss282/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★ · ★**★被掐了不要从零重做: 盘上已有 3 件交付物 ⇒ 从「改闸 3 条红」接着做★**
