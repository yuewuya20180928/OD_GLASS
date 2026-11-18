★**ISS-258 · SW 侧 H-1 重锚 (第 6 跳 · 网表/脚表 md5 过期 ⇒ `check_demo_panel_spec.py` + `timing_check.py` 红)** ★ (main · 2026-11-16 21:5x)

★★**为什么派这一件**: ★**ISS-257 (hw-lead) 合法落表 ⇒ 网表 md5 `16ac89f7…` → `e06c1dd6…` · 脚表 md5 `ef436a37…` → `287e7861…` ⇒ SW 侧锚点过期 ⇒ `SW/tools/check_demo_panel_spec.py` **rc=1 (R6 红 2 条)** · `SW/tools/timing_check.py` **rc=1 (SELFTEST 69/71)** · `check_demo_panel_spec.py --selftest` **rc=1 (15/16, 报「基线就不绿」)** ★
★★**根因 = 上游合法落表 (ISS-257), 不是真源被换** ★★ ⇒ ★**只需把锚点重锚到新 md5, 判据逻辑一个字节不许动** ★★

★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-258 · ★**零外发** ★
★**本单 = 主线内 (原理图/网表侧·门禁口径) · 不是 PCB 布线/布局类** ★

---

## ① 要改的 (★只许改【网表 + 脚表那两条锚点】★)

| 文件 | 改什么 |
|---|---|
| `SW/SW_MD5_BASELINE_LEDGER.md` §1 `SW_MD5_ANCHORS` 块 | `source_ledger.entries[]` 里 **`HW/netlist_v1.csv`** 那一条: `by: ISS-257` · `prev_md5: 16ac89f77c25a3f61834cc7ebcd78a7f` · `md5: e06c1dd633566aa44732762c2ff99d1c` · `landed_at: "2026-11-16 21:22"` |
| 同上 | **`HW/netlist_v1_pins.csv`** 那一条: `by: ISS-257` · `prev_md5: ef436a37412ac9b6eac3c9f41f1edca4` · `md5: 287e7861a0d1007748d92d9fbecdd490` · `landed_at: "2026-11-16 21:22"` |
| 同上 §1 `source_ledger.landing_records` | 追加 `HANDOFF/2026-11-16_hw-lead_ISS257_*.md` (★H-1 第 ③ 步: 新的落表台账位置必须登记★) |
| 同上 §3 留痕账 | 追加 **R-09** 行 (★追加式: 历史行一个字不改, 与 R-08 的口径一致★) |

★**依据 (main 21:4x 本机实跑)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` **§18.4 (L1069/L1070)** = ★**单号 `ISS-257` + 文件名 + 新 md5 + 旧 md5 四项同行齐全** ★ ⇒ ★**R6 判据 ②③④⑤ 都能查到** ★
★**`landed_at` 以台账 §18.4 那一行的时刻为准 (21:22) —— 别自己编时间** ★

★**脚表那条的旧 md5 要注意**: 台账 §18.4 记的是三段式 (旧 `ef436a37…` → 中间 `87a7d2d9…` → 新 `287e7861…`) ⇒ ★**锚点 `prev_md5` 写【旧 `ef436a37…`】**(★与 R-08 行脚表那条的 prev 口径一致★) ★**`md5` 写【新 `287e7861…`】** ★

★**板 `611b869e…` + `.kicad_pro` `3e504d2b…` + BOM `94642d07…` 一个字节都不许动** ★ (★BOM 不在 R6 的受管真源里, 只登记不许改★)

## ② 要交的 (★三件★)

1. ★**改后实测 (原样贴输出)★**
   - `python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=0 · R1~R7 全过** ★
   - `python3 SW/tools/timing_check.py` ⇒ ★**rc=0 · SELFTEST 71/71** ★
   - `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ ★**rc=0 · 16/16** ★
2. ★**反向用例 (★贴两次输出★)★**: ★**把 §1 那两条锚点的 `md5` 改回旧值 ⇒ 必须变红 (rc≠0 且点名 R6) ⇒ 再改回来 ⇒ rc=0** ★ ⇒ ★**这是「它真在被读」的证据, 不许只贴绿灯** ★
3. ★**留痕**: 改前 md5 → 改后 md5 + 逐行改前改后 + ★**受保护 md5 前后对照 (★自己跑出来的, ★别抄别人的★)** ★
   ★**交卷单 `HANDOFF/2026-11-16_sw-lead_ISS258_H1重锚第6跳.md` (★B1~B6 六块齐全★) + 分片 `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写★)** ★

★**自测命令**: `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ ★**rc=0 且一条不许少 (★反向用例不许删★)** ★

## ★③ 本单必须回答的一个问题 (★main 21:5x 实测发现的真问题★) ★

★**`timing_check.py` 现在掉的是哪 2 条?** ★**SW 的 R6 只锚【网表 + 脚表】两条, 而 `timing_check.py` 的 2 条掉的是同源 md5 锚点断言 ⇒ 改完 §1 那两条, `timing_check.py` 应当一起回绿** ★
★**但如果实跑发现 `timing_check.py` 还在读【别处】的旧 md5** (★★SW/SW_MD5_BASELINE_LEDGER.md 之外的地方, ★比如 SW 目录别的台账★) ⇒ ★**不许自己改判据阈值去凑绿** ★ ⇒ ★**把「还在读哪里的旧 md5」原样报给 main, 由 main 决定是再登记一条锚点还是别的修法** ★

## 边界

★零落表 (网表/脚表/BOM/板/`.kicad_pro` 一个字节不许动) · ★零外发 · ★零实物 · ★**不碰 `HW/` 与 `MECH/`** ★ · ★**不碰布线/布局/板框** ★ · ★**不改判据阈值** ★ · ★**不许替老板拍板** ★ · ★**不自签 issue_log** ★ · ★**别把整份台账重写 (★只改 §1 两条 entries + landing_records + 追加 R-09★)** ★
★**硬保护**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**跑前跑后逐字节不变** ★
★**零外发政策** (★老板 2026-11-12 02:02★): 本单**不需要**查任何外部资料 ⇒ ★**一次网都不要上** ★
