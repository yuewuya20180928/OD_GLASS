★**ISS-259 · MECH 侧 H-1 重锚 (第 6 跳 · 网表/脚表 md5 过期 ⇒ `check_demo_struct_truth.py` G5b + C21 双红)** ★ (main · 2026-11-16 21:5x)

★★**为什么派这一件**: ★**ISS-257 (hw-lead) 合法落表 ⇒ 网表 md5 `16ac89f7…` → `e06c1dd6…` · 脚表 md5 `ef436a37…` → `287e7861…` ⇒ MECH 侧锚点过期 ⇒ `MECH/check_demo_struct_truth.py` **rc=2 (21/23, FAIL G5b + C21)** · `--selftest` **rc=2 (报「基线就不绿 ⇒ 自测不成立」)** ★
★★**根因 = 上游合法落表 (ISS-257), 不是真源被换** ★★ ⇒ ★**只需把锚点重锚到新 md5, 判据逻辑一个字节不许动** ★★

★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-259 · ★**零外发** ★
★**本单 = 主线内 (原理图/网表侧·结构侧锚点) · 不是 PCB 布线/布局类** ★

---

## ① 要改的 (★只许改【网表 + 脚表那两条锚点】★)

| 文件 | 改什么 |
|---|---|
| `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS` 块 | `source_ledger.entries[]` 里 **`HW/netlist_v1.csv`** 那一条: `by: ISS-257` · `prev_md5: 16ac89f77c25a3f61834cc7ebcd78a7f` · `md5: e06c1dd633566aa44732762c2ff99d1c` · `landed_at: "2026-11-16 21:22"` |
| 同上 | **`HW/netlist_v1_pins.csv`** 那一条: `by: ISS-257` · `prev_md5: ef436a37412ac9b6eac3c9f41f1edca4` · `md5: 287e7861a0d1007748d92d9fbecdd490` · `landed_at: "2026-11-16 21:22"` |
| 同上 §1 `source_ledger.landing_records` | 追加 `HANDOFF/2026-11-16_hw-lead_ISS257_*.md` (★H-1 第 ③ 步★) |
| 同上 §3.1 已修复 (留痕) | 追加 **R-06** 行 (★追加式: R-01~R-05 历史行一个字不改★) |
| 同上 §1 顶部注记块 / Q-11 那种「重锚第 N 跳」说明 | ★**追加**一行「第 6 跳 (ISS-257)」说明, ★**不许改历史那几行的字** ★ |

★**依据 (main 21:4x 本机实跑)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` **§18.4 (L1069/L1070)** = ★**单号 `ISS-257` + 文件名 + 新 md5 + 旧 md5 四项同行齐全** ★ ⇒ ★**C21 判据 ①②③ 全能查到** ★
★**`landed_at` 以台账 §18.4 那一行的时刻为准 (21:22) —— 别自己编时间** ★

★**脚表那条的旧 md5**: 台账 §18.4 记的是三段式 (旧 `ef436a37…` → 中间 `87a7d2d9…` → 新 `287e7861…`) ⇒ ★**锚点 `prev_md5` 写【旧 `ef436a37…`】· `md5` 写【新 `287e7861…`】** ★

★**板 `611b869e…` + `.kicad_pro` `3e504d2b…` + BOM `94642d07…` 一个字节都不许动** ★
★**`MECH/check_demo_struct_truth.py` (★门禁脚本★) 一个字节都不许改** ★ ⇒ ★**只改 `MECH/HW_CROSS_REVIEW_TRIAGE.md` 里那 2 条锚点 + landing_records + 追加留痕** ★

## ② 要交的 (★三件★)

1. ★**改后实测 (原样贴输出)★**
   - `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 · 23/23 · FAIL 0** ★
   - `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ ★**rc=0 · 14/14 反向用例一条没删** ★
2. ★**反向用例 (★贴两次输出★)★**: ★**把 §1 那两条锚点的 `md5` 改回旧值 ⇒ 必须变红 (rc≠0 且点名 G5b/C21) ⇒ 再改回来 ⇒ rc=0** ★ ⇒ ★**这是「它真在被读」的证据** ★
3. ★**留痕**: 改前 md5 → 改后 md5 + 逐行改前改后 + ★**受保护 md5 前后对照 (★自己跑出来的★)** ★
   ★**交卷单 `HANDOFF/2026-11-16_mech-lead_ISS259_H1重锚第6跳.md` (★B1~B6 齐全★) + 分片 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写★)** ★

## ★③ 本单必须回答的一个问题 (★main 21:5x 实测发现的真问题★) ★

★**`MECH/check_demo_struct_truth.py` 的 G5b 说「8 个受保护文件 md5 逐字节未变 (板/`.kicad_pro` + 4 个 check 脚本 + 网表/脚表)」** ★
★**⇒ 那 4 个 check 脚本的 md5 也必须在锚点里登记 ⇒ ★**改锚点时, ★**别把那 4 个 check 脚本的 md5 误改成新的** (★它们本轮没变★) ⇒ ★**跑前跑后 `md5sum` 逐字节比对 + 原样贴出来** ★
★**如果实跑发现 G5b 还在读【别处】的旧 md5** ⇒ ★**不许自己改判据阈值去凑绿** ★ ⇒ ★**原样报 main** ★

## 边界

★零落表 (网表/脚表/BOM/板/`.kicad_pro` 一个字节不许动) · ★零外发 · ★零实物 · ★**不碰 `HW/` 与 `SW/`** ★ · ★**不碰布线/布局/板框** ★ · ★**不改判据阈值 (`G5b`/`C21` 判据逻辑 0 改动)** ★ · ★**不许替老板拍板 (★板长/板厚/腔体/集热面那些不归你★)** ★ · ★**不自签 issue_log** ★
★**硬保护**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**跑前跑后逐字节不变** ★
★**零外发政策** (★老板 2026-11-12 02:02★): 本单**不需要**查任何外部资料 ⇒ ★**一次网都不要上** ★
