> ★★【已作废 · 不要再派】★★ ★**2026-11-17 05:2x main 标注**★
> 本单 (ISS-253 H-1 重锚 第 4 跳 R-05) ★**已于 2026-11-16 20:0x 落表交付**★, 之后又被 ★**ISS-259 (第 6 跳 R-06, by ISS-257)**★ 覆盖 ⇒ ★**现在盘上的锚点现值 = 网表 `e06c1dd633566aa44732762c2ff99d1c` / 脚表 `287e7861a0d1007748d92d9fbecdd490`**★
> ⇒ ★**照本单字面落地 = 把网表谎报成 ISS-249 旧版本 = 打红 + 做假绿** ★ ⇒ ★**本单已作废, 不要再派 mech-lead 重锚** ★
> ★**另**: 本单写的「文件 = `MECH/check_demo_struct_truth.py`」★**不成立** ★ ⇒ ★**锚点在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS` 块**, 脚本只是**读**它 ⇒ ★**以后派 H-1 单请直接写锚点文件** ★
> ★**替代任务书**: `state/dispatch_briefs/ISS-259_mech_h1_reanchor_jump6.md` (第 6 跳, 已 verified) · 机制收口单 = `state/dispatch_briefs/ISS-273_mech_h1_anchor_single_source.md` (★判决源改成台账最新记录, 合法落表不再红★)

★**ISS-253 · MECH 侧 H-1 重锚 (网表 md5 过期 ⇒ `check_demo_struct_truth.py` 红)** ★ (main · 2026-11-16 20:0x)

★★**为什么派这一件**: ★**ISS-249 合法落表 (F1) ⇒ 网表 md5 `611c3ba3…` → `16ac89f7…` ⇒ MECH 侧的锚点过期 ⇒ `MECH/check_demo_struct_truth.py` **rc=2 (21/23, FAIL G5b + C21)** ★
★★**根因 = 上游合法落表, 不是真源被换** ★★ ⇒ ★**只需把锚点重锚到新 md5, 判据逻辑一个字节不许动** ★★

★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-253 · ★**零外发** ★

---

## ① 要改的 (★只许改【网表那一条锚点】★)

| 项 | 值 |
|---|---|
| 文件 | `MECH/check_demo_struct_truth.py` (★**判据逻辑 0 改动**★) |
| 锚点新值 | `md5 = 16ac89f77c25a3f61834cc7ebcd78a7f` |
| 锚点旧值 (★必须留痕★) | `prev_md5 = 611c3ba3db3dc7de7213063375b96d01` |
| by | `ISS-249` |
| landed_at | ★**以 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17 为准 (★别自己编时间★)** ★ |

★**脚表 / BOM / 板 / `.kicad_pro` 四件逐字节不变 ⇒ 锚点只改网表那一条, 一个字节都不许动** ★

## ② 要交的 (★三件★)

1. ★**改后实测**: `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0 · 23/23 · FAIL 0** ⇒ ★**原样贴输出** ★
2. ★**反向用例**: ★**把锚点改回旧 md5 ⇒ 必须变红 (rc≠0 且点名 G5b/C21)⇒ 再改回来 ⇒ rc=0** ★ ⇒ ★**贴两次输出** ★ (★这是「它真在被读」的证据★)
3. ★**留痕**: 改前 md5 → 改后 md5 + 逐行改前改后 + ★**受保护 md5 前后对照 (★自己跑出来的, ★别抄别人的★)** ★
   ★**交卷单 `HANDOFF/2026-11-16_mech-lead_ISS253_H1重锚网表md5.md` (★B1~B6 六块齐全★) + 分片 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py` 原子写★)** ★

★**自测命令**: `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ ★**rc=0 且一条不许少 (★反向用例不许删★)** ★

## 边界

★零落表 (网表/脚表/BOM 一个字节不许动) · ★零外发 · ★零实物 · ★**不碰 `HW/` 与 `SW/`** ★ · ★**不碰布线/布局/板框** ★ · ★**不改判据阈值** ★ · ★**不许替老板拍板 (★板长/板厚/腔体那些不归你★)** ★ · ★**不自签 issue_log** ★ · ★**别把整份脚本重写 (★只改锚点常量★)** ★
