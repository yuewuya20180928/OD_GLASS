★**ISS-286 · mech-lead 续做任务书 (cont1) —— ★★【MECH 侧坐标归一闸 C4 判决源台账化】★★** ★ (main · 2026-11-17 12:3x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 12:3x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-286 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 门禁机制收口 · 零写板 · 零落表 · 零改既有语义**★

---

## ★⓪ 第一件事 (★必做, 顺序不许换★)

★**1. cat 全文 (★本文件) ⇒ 2. cat 原任务书 `state/dispatch_briefs/ISS-286_mech_frame_gate_ledger_caliber.md` (5233 B · §①~§⑤) ⇒ 3. ★**从盘上现状继续, 不要从零重做**★**

★**★上一趟 (11:41~12:13) 是半落地僵尸: 交卷单骨架刚建完就被掐 ⇒ 盘上几乎什么都没落★**

| 项 | 盘上实况 (★main 12:3x 本机实测★) |
|---|---|
| ★**`MECH/check_board_frame_coords.py`** ★ | ★**md5 `92f4eebb7f70c129f20e964cdf7485a0` · mtime `Nov 17 06:57` ⇒ 【一字未动】⇒ 你的改动【零落地】★** |
| ★**`MECH/patches/`** ★ | ★**目录不存在 ⇒ 补丁套用器零落地**★ |
| ★**交卷单** `HANDOFF/2026-11-17_mech-lead_ISS286_坐标归一闸台账化.md` ★ | ★**867 B 骨架** (★B1~B6 六段全是「（施工中）」★) ⇒ ★**直接在这份骨架上填, 另起一份不算**★ |
| ★**`state/fragments/mech.yaml`** ★ | ★**`grep -c "iss286"` = 0 ⇒ 分片零写**★ |
| ★**上一趟会话** ★ | `agent:mech-lead:subagent:a6a8ca76` (11:41→12:13 · status=done · abortedLastRun=true) ⇒ transcript 末条 = 12:07:25 一段被 abort 的 thinking ⇒ ★**它停在「设计阶段」, 连代码都没开始写**★ |

★**⇒ 你真正要做的 = 把上一趟设计出来的东西写出来 + 跑出证据 + 填满交卷单 + 写分片。设计部分别再重新推一遍, 直接用下面 §⓶ 里 main 已经替你验好的先例实现★**

---

## ★⓶ ★★【决定性新证据 · main 12:3x 实测】★★ ★★【硬写基线的病, 40 分钟内发作了两次】★★

★**你不在的这 40 分钟里, `ISS-283` (hw-lead) 又落了两次表 ⇒ 网表 / 脚表 / BOM 三件的 md5 又动了两次★**

| 时刻 | 网表 md5 | 脚表 md5 | BOM md5 |
|---|---|---|---|
| ★**09:58:16** (A1+A2 落表 · 原任务书里的现值) ★ | `2f17650c…` | `6ea65fec…` | `ea5f4f58…` |
| ★**12:1x** (ISS-283 A3=V-2=1 落表) ★ | `87f2f792…` | `8ca46495…` | `ea5f4f58…` |
| ★**12:2x** (ISS-283 A4=Q_PG pad1↔pad3 + A5=20mA 落表) ★ | ★**`37f62ac3…`** ★ | ★**`a4270120…`** ★ | ★**`5d02bece…`** ★ |

★**⇒ C4 现在硬写的那三个基线 (`e06c1dd6…` / `287e7861…` / `94642d07…`) 已经【过期两轮】⇒ ★**这不是「下次第落表又红一遍」, 是【已经红了三遍】★** ★

★**★★【★main 已经替你把先例验通了 ⇒ 你直接照抄, 不要自己创★】★★**

★**main 12:3x 本机实跑**: ★**把 `MECH/check_demo_struct_truth.py` 的 ISS-273 台账解析器 (`ledger_state` / `ledger_records`) 指向【当前盘上真台账】跑了一遍★** ⇒

```
HW/netlist_v1.csv        head= 37f62ac3f0b8  producer=['ISS-283']  why=(none)  disk= 37f62ac3f0b8  ✅MATCH
HW/netlist_v1_pins.csv   head= a4270120454a  producer=['ISS-283']  why=(none)  disk= a4270120454a  ✅MATCH
HW/BOM_v1.csv            head= 5d02bece9477  producer=['ISS-283']  why=(none)  disk= 5d02bece9477  ✅MATCH
```

★**⇒ 【台账为准】口径在【此刻】就是绿的 ⇒ ★**你要做的是把这条口径搬进 `check_board_frame_coords.py` 的 C4, 不是去追新的基线数字★** ★
★**⇒ ★**台账解析器不用你写、不用你扩★** (★`LANDING_AUTH` 那些行里没有 md5 ⇒ 解析器自动跳过 ⇒ 不会造出假记录★)★

---

## ★① 病灶 (★与原任务书 §① 同, 但现值已更新到 12:2x★)

★**`MECH/check_board_frame_coords.py` 的 C4 把【网表 / 脚表 / BOM】三件的 md5 写死成基线** ⇒ 上游一次【合法落表】就把这三件换掉 ⇒ 闸红 ⇒ 而真源【没被偷换】 ★

★**★病根 = 【判决源选错了】, 不是【真源被改了】★** ⇒ ★**修法必须落在「取值来源」上, 不许只改「取值」★**

---

## ★② 先例 (★已跑通, 照抄口径, 别自创★)

★**ISS-273 (MECH 侧 · 2026-11-17 09:0x 已 verified)** ⇒ ★**把 C21/G5b 的判决源从【域侧锚点副本】换成【落表台账最新记录 (链头)】⇒ 合法落表不再红, 而「悄悄换真源」仍然红** ★ ⇒ ★**ISS-275 = SW 侧同构 (已 verified)** ★

★**★先例代码位置 (★main 12:3x 实读·行号可能随改动漂移, 以函数名为准★)★★**:
- ★**`MECH/check_demo_struct_truth.py`** ★
  - `LEDGER_CANON` (★判决源台账路径 = `HW/SCHEMATIC_LANDING_V1_LANDED.md`·★只读★)★
  - `LEDGER_MD_RE` (★32 位 / 12 位 md5 token★)
  - `ledger_records(text, rel)` (★抽该文件的【改前→改后】记录行·★行序无关★)★
  - `ledger_state(rel, text)` (★算【链头 / 链 / 产出单号 / why】·★取不准 ⇒ head=None ⇒ 判红★)★
  - `ledger_canonical_text(root, anchors, overrides)` (★取台账文本 + 支持内存 override ⇒ 反向用例不用真改 HW/★)★
  - `run_checks(...)` 的 `ledger_texts` / `md5_override` 两个可选参数 (★★只为让反向用例能在内存里造台账★★)★
- ★**ISS-273 交卷单**: `HANDOFF/2026-11-17_mech-lead_ISS273_锚点台账化.md` (★其中 §「链头 / fail-closed 三条 / 反向用例 R1~R6」的写法照抄★)★

★**★你这次要动的位置 (★main 12:3x 实读★)★**:
- `MECH/check_board_frame_coords.py` ★**L73~75** ⇒ `PROTECTED` 字典里那三行硬写基线 (★板 / `.kicad_pro` 两行**保留不动**★)★
- ★**L435~456** ⇒ `C4 · 受保护 5 件 md5` 段 (`md5_of` / `check_c4`)★
- ★**L735+** ⇒ `selftest()` (★现有 5 条反向用例: ① 改窗口角 ② 抽表头帧标签 ③ 挪进 SoM 区 ④a/④b 旧矩形 ⑤ 改受保护件 ⇒ ★**这 5 条一条不许少★**★)★
- ★**L841~853** ⇒ 用例 ⑤ (★它现在靠「改 `.kicad_pro` 让 C4 红」⇒ ★**`.kicad_pro` 的基线照旧写死 ⇒ 这条用例照样成立, 不许动★**)★

---

## ★③ 要交的 (★每件都能独立验收★)

1. ★**改成「台账为准」口径**: ★**C4 对【网表 / 脚表 / BOM】三件的判定改为: 盘上 md5 == 落表台账 (`HW/SCHEMATIC_LANDING_V1_LANDED.md`) 里该文件最新登记的 md5 (链头)** ⇒ ★**合法落表 ⇒ 自动前移 ⇒ 绿** ★ ⇒ ★**而【盘上 md5 在台账里查不到任何登记】⇒ 红** ★ ⇒ ★**台账被偷改 / 链头不唯一 / 链断 / 链头无单号 ⇒ 红 (fail-closed 一条不许动)** ★
2. ★**★不许只是把基线数字改成新值★** ⇒ ★**只改数字 = 下一次落表又红一遍 (★这 40 分钟内已经红了三遍·实测证据在 §⓶★)** ★ ⇒ ★**判据的【取值来源】必须变, 不是【取值】变★** ★
3. ★**板 / `.kicad_pro` 两件的基线照旧写死** (★它们是【真·不许变】的件, 落表链不管它们★) ⇒ ★**C4 的这两条一条不许动** ★
4. ★**反向用例 (★至少 4 条新增, 每条贴原样 rc★)**:
   | # | 构造 | 期望 |
   |---|---|---|
   | ① | ★**台账里有该文件的最新登记, 盘上 == 台账 ⇒ 放行** ★ | **绿** (★合法落表不再红★) |
   | ② | ★**台账里查不到该文件的任何登记, 盘上是别的值** ★ | **红** (★悄悄换真源★) |
   | ③ | ★**台账里有登记, 但盘上 ≠ 台账登记值** ★ | **红** |
   | ④ | ★**台账被手改 (登记值与盘上凑成一致, 但单号/文件名/前后 md5 四项不齐)** ★ | **红** (★四项不齐不许放行★) |
   | ★⑤ (★可选加分) ★ | ★**链头不唯一 (台账里造两条指向同一文件) ⇒ 红 (fail-closed 不许动)** ★ | **红** |
5. ★**交卷单 + 分片**: ★**`HANDOFF/2026-11-17_mech-lead_ISS286_坐标归一闸台账化.md` (★867 B 骨架已在·直接填·B1~B6 六块·★不许留「（施工中）」★)** ★ + ★**`python3 state/frag_write.py --agent mech-lead`** ★ + ★**`grep -c "iss286" state/fragments/mech.yaml` ≥ 1** ★

---

## ★④ 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_board_frame_coords.py            # 期望 rc=0 (C1~C4 全过)
python3 MECH/check_board_frame_coords.py --selftest   # 期望 rc=0 (★原有 5 条一条不许少 + 新增 ≥4 条★)
python3 MECH/check_demo_struct_truth.py               # 期望 rc=0 (23/23) ⇒ ★**不许把你的老闸弄红★**
python3 state/merge.py && python3 state/gate_check.py # 期望 rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/SCHEMATIC_LANDING_V1_LANDED.md
# ★★板 611b869e… / .kicad_pro 3e504d2b… / 台账 1ae6242a… 一个字节不许变★★
```

★**★注意 `/tmp` 可能已满 (别的单的沙盒占着) ⇒ `--selftest` 跑不起来就把 `TMPDIR` 指到项目盘 (★`TMPDIR=$PWD/tmp`★)** ★

---

## ★⑤ 边界 (★违反就是不合格★)

★零写板 · ★零落表 (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `MECH/check_demo_struct_truth.py` 与其它既有判据脚本的语义** ★ (★只准【读】它的实现当先例, 不准改它★) · ★**不许放宽 fail-closed** ★ · ★**不许改 `MECH/check_board_frame_coords.py` 里 C1/C2/C3 三段的语义** ★ · ★**不许动 C4 里板 / `.kicad_pro` 那两行基线** ★ · ★不碰 `HW/` / `SW/` 的文件与分片 (★只交叉引用 ISS-273 的口径★) · ★零外发 · ★**不替老板拍板** ★ · ★**不自签 issue_log** ★ · ★**不许动 `state/issue_log.yaml`** ★

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架** (★骨架已在, 直接填★) · ★**长任务 `nohup` 后台 + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少写盘一次** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验自己的 key 在不在 (★`frag_write.py` 无锁★)** ★
★**★本单最容易踩的坑 (★上一趟就死在这★)★**: ★**别在一条长 exec 里写代码 ⇒ 一次 exec 干一件事, 每件事 ≤ ~120 秒 ⇒ 写完立刻落盘★** ★
