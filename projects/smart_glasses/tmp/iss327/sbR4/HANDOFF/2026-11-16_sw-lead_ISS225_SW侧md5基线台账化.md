# [sw-lead→PM] ISS-225 · SW 侧 md5 基线台账化 (R6 重锚 + 三方对账 + 同根因全清单)

> ★**owner**: sw-lead (软件/工具链侧总工) · ★**verify_by**: main · ★**单号**: ISS-225 · ★**开单**: main 2026-11-16 04:07 (cron `fb67af40` 队列自动派活) · ★**交卷**: 2026-11-16 04:2x
> ★**上游**: ★**ISS-220** (hw-lead 落表第 1 批, 2026-11-16 02:32) · ★**后续**: ★**ISS-223** (hw-lead 落表第 2 批, 待落)
> ★**边界 (★本单逐条自查过★)★**: ★**没碰** `HW/` 下任何文件 (网表 / 脚表 / 板 / `.kicad_pro` / 原理图 / BOM 一个字节没动) ★ · ★**没碰** `MECH/` 下任何文件 (★`MECH/check_demo_struct_truth.py` 的 C21 只许只读参照★) ★ · ★**没改** `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片 (★`state/fragments/{pm,hw,mech}.yaml` 一个字节没碰★) ★ · ★**没碰 PCB 布线 / 布局 / 板框** ★ · ★**没把 `--skip-md5` 设成默认跳过** ★ · ★**没自签 issue_log** (★status 留给 main 落 verified★) ★ · ★**零外发** ★

---

## ★0 一句话

★★**这次红 = 【锚点过期】, 不是【红灯被调没】** ★★
★**hw-lead 的 ISS-220 落表 (2026-11-16 02:32) 真改了 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv`** (md5 `c78f9912…`→`13f59a43…` / `4814617e…`→`a600afae…`),
而 **SW 侧的门禁锚点还钉在落表前的旧 md5** ⇒ **门禁读旧数 = 假红** ⇒ **必须重锚** ⇒
★**但"只把锚点里的 md5 换成新值" = 把门禁再废一次** (下次落表又恒红, 而且没人分得清"真源变了"还是"门禁坏了")
⇒ ★**所以本单把 R6 从「钉死一组 md5」升级成【台账驱动 + 三方对账】**: ★**锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致才叫绿** ★
⇒ ★**并把 SW 侧同根因的下一处恒红 (`SW/tools/timing_check.py`) 一起收掉** ★

---

## B1 结论摘要

| 项 | 结论 |
|---|---|
| ★**根因** ★ | ★**ISS-220 落表 (hw-lead, 2026-11-16 02:32) 改了网表/脚表** ⇒ ★**SW 侧两处 md5 锚点过期** ⇒ **R6 恒红** ★ |
| ★**鉴别证据 (是锚点过期, 不是红灯被调没)** ★ | ★**门禁脚本 `SW/tools/check_demo_panel_spec.py` mtime = 2026-11-15 23:59 < 落表 02:32** ⇒ ★**脚本一个字节没被碰过**; ★**并且** ① 落表台账里**白纸黑字**记着新 md5 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` L108/L110/L204/L206) ② 喂**落表前**的网表跑 `timing_check.py` ⇒ ★**正好只有那 2 条内容断言红、其余 68 条全过** ⇒ ★**红灯跟网表真值走, 不跟脚本走** ★ |
| ★**① R6 重锚 + 升级成三方对账** ★ | ★**`SW/tools/check_demo_panel_spec.py` 的 R6 现在做 6 项核对** (① 盘上 md5 == 锚点 ② 锚点 md5 在落表台账里查得到 ③ 锚点旧 md5 也查得到 ④ 落表单号查得到 ⑤ **文件名 + 新 md5 + 旧 md5 三项在落表台账的同一行** ⑥ 登记的落表台账位置一个都不存在 ⇒ 红) ⇒ ★**锚点从「脚本里的 4 个硬编码 md5」搬到【新台账 `SW/SW_MD5_BASELINE_LEDGER.md` §1】** (机器可读 YAML 块) ⇒ ★**机制照抄 MECH C21 (只读参照, `MECH/` 一个字节没碰)** ★ |
| ★**新增 R7** ★ | ★**「已修复 (留痕) 必须在场」** ⇒ ★**删节 / 删行 / 抹 md5 / 抹判别标记 ⇒ 门禁立刻红** (照 MECH G8) ★ |
| ★**② 同根因全清单 + 逐条处置** ★ | ★**搜法**: `grep -rnoE '\b[0-9a-f]{32}\b' SW/` + `grep -rn "netlist_v1\.csv\|netlist_v1_pins\.csv\|demo_mainboard\.kicad_pcb\|demo_mainboard\.kicad_pro" SW/` ⇒ ★**命中 8 条 (S-01…S-08), 处置口径: 台账化 2 条 · 保留并说明理由 2 条 · 本单不管但登记 3 条 · 重锚 1 条** ⇒ ★**没有一条"留着不管且不登记"** ★ (全表见 `SW/SW_MD5_BASELINE_LEDGER.md` §2) |
| ★**③ 留痕** ★ | ★**`SW/SW_MD5_BASELINE_LEDGER.md` §3「已修复 (留痕)」** 登记 3 行 (R-01 面板门禁 R6 · R-02 timing F3 内容断言 · R-03 timing 网表 md5 基线) ⇒ ★**每行写得出: 哪个单号 / 哪两个 md5 (旧→新) / 判别证据 / 复现命令** ★ ⇒ ★**R7 机器守住它** ★ |
| ★**④ 反向用例** ★ | ★**`check_demo_panel_spec.py --selftest` 从 8 条扩到 16 条 (16/16 全抓到)**, 新增 7 条 + 1 条基线校验: ★**① 盘上真源被换掉而锚点没换 ⇒ 红 ② 锚点改成台账里查不到的哈希 ⇒ 红 ③ 锚点里的落表单号改坏 (ISS-220→ISS-999) ⇒ 红 ④ 落表台账里的落表单号被改坏 ⇒ 红 ⑤ 把落表台账里那两行删掉 ⇒ 红 ⑥ 把锚点块整个删掉 ⇒ 红 (fail-closed) ⑦ 把「已修复 (留痕)」那一节删掉 ⇒ 红** ★ |
| ★**⑤ 交接单 + 分片** ★ | ★**本文件** + ★**`state/fragments/sw.yaml`** (★走 `python3 state/frag_write.py` 原子写★) ★ |
| ★**同根因的第二处恒红 (本单一起收掉)** ★ | ★**`SW/tools/timing_check.py`** 开工时 **rc=1 / 65/68** (3 条 FAIL) ⇒ ★**同一根因**: ① 硬编码的网表 md5 基线过期 ② 两条断言断言的是【网表侧那条 I2C 矛盾仍在】, 而 ★**ISS-220 d6 真把网表 I2C_A 改成 2.2k@1.8V/186ns ⇒ 那条矛盾被上游真修好了** ⇒ ★**本单把断言方向反过来 (注记必须与实算一致) + md5 基线台账化** ⇒ ★**现 rc=0 / 70/70** ★ |
| ★**板端 [实测]** ★ | ★**0 条** (★板与屏不在本机★) ⇒ ★**凡是标 [实测] 的, 一律是"本机脚本 / 本机文件实读"** ★ |
| ★**零外发** ★ | ★**本单未发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ★ |

★**一句话给 main**: ★**SW 侧的门禁全绿了 (R6/R7 三方对账 + 留痕在场 + 16/16 反向用例), 而且不是"追了一次 md5" —— 是把"真源变更"变成了台账里可对账、可追责的事件** ★

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 (派活书原文) | 判定 | 证据 |
|---|---|---|---|
| A-1 | ★**① R6 重锚 + 升级成三方对账** (锚点 ↔ 落表台账 ↔ 盘上真源) ★ | ✅ **通过** | `SW/tools/check_demo_panel_spec.py` R6 6 项核对 + 锚点搬到 `SW/SW_MD5_BASELINE_LEDGER.md` §1; 实跑 rc=0 |
| A-2 | ★**机制照抄 `MECH/check_demo_struct_truth.py` 的 C21 (只读参照, `MECH/` 不许改)** ★ | ✅ **通过** | 同名同构 (`source_ledger.landing_records` + `entries[].{file,by,prev_md5,md5}`); ★**`MECH/` 零写入** (见 B6 ⑤) |
| A-3 | ★**台账来源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` 或 `HANDOFF/2026-11-16_hw-lead_ISS223_*.md`** ★ | ✅ **通过** | 锚点 `landing_records` 两个都登记了 (★后者还不存在 ⇒ 通配命中 0 个 ⇒ 不影响, ISS-223 落表后自动生效★) |
| A-4 | ★**台账里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项** ★ | ✅ **通过** | 锚点 `by=ISS-220`; 实测台账 L108 (`HW/netlist_v1.csv` · `c78f991283cc`→`13f59a43dbd3`) / L110 (脚表) / L204 / L206 ⇒ ★**四项齐 + 同行** |
| A-5 | ★**只改锚点不落表 = 悄悄换真源 = 红** ★ | ✅ **通过** | 反向用例 REV-10 (锚点改成 `deadbeef…`) + REV-13 (删台账那两行) ⇒ 实测 R6 红 |
| A-6 | ★**② SW 侧同根因同类基线全清单 + 逐条处置** ★ | ✅ **通过** | `SW/SW_MD5_BASELINE_LEDGER.md` §2: ★**8 条 (S-01…S-08) 逐条处置, 含位置/类型/基线/现状/处置** ★ |
| A-7 | ★**不许只修 R6 一处, 留下同根因的下一处恒红** ★ | ✅ **通过** | ★**`SW/tools/timing_check.py` 的 3 条 FAIL (同根因) 一并收掉 ⇒ 65/68 → 70/70 rc=0** ★ |
| A-8 | ★**③ 留痕 (是锚点过期, 不是红灯被调没 + 根因单号 + 新旧 md5 + 复现命令)** ★ | ✅ **通过** | `SW/SW_MD5_BASELINE_LEDGER.md` §3 三行 (R-01/R-02/R-03) ⇒ ★**R7 机器守住 (REV-15 实测删节 ⇒ 红)** ★ |
| A-9 | ★**④ 反向用例 --selftest 必须全抓到 (① 盘上被换 ② 锚点查不到台账 ③ 单号改坏 ④ 删台账那一行)** ★ | ✅ **通过** | ★**16/16 全抓到** (新增 7 条 + 1 条基线) ★ |
| A-10 | ★**⑤ 交接单 (新建) + 分片 (走 `state/frag_write.py` 原子写)** ★ | ✅ **通过** | 本文件 + `state/fragments/sw.yaml` (★`state/frag_write.py` 原子写, 禁 `open(p,"w")` 已遵守★) |
| A-11 | ★**不许改 `HW/` 下任何文件** ★ | ✅ **通过** | 见 B6 ⑤ (逐文件 md5 前后对照) |
| A-12 | ★**不许改 `MECH/` 下任何文件** ★ | ✅ **通过** | 见 B6 ⑤ |
| A-13 | ★**不许改 `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片** ★ | ✅ **通过** | 见 B6 ⑤ |
| A-14 | ★**不许把 `--skip-md5` 设成默认跳过** ★ | ✅ **通过** | `--skip-md5` 仍是**既有逃生舱** (可选开关), ★**默认路径必须校 R6+R7** (B6 ① 无参即校) |
| A-15 | ★**不许硬编码一个"查不到出处"的 md5 当基线** ★ | ✅ **通过** | ★**锚点里的两个 md5 都能在落表台账里查到出处 (单号/文件/新旧)** ⇒ 查不到就红 (REV-10/12/13) ⇒ **本单没有硬写任何"查不到出处"的数** ★ |
| A-16 | ★**板端 [实测] = 0 条** ★ | ✅ **通过** | B3 全表已标 |
| A-17 | ★**零外发** ★ | ✅ **通过** | 本单零外发动作 |
| A-18 | ★**不许自签 issue_log** ★ | ✅ **通过** | ★**`state/issue_log.yaml` 零写入** ⇒ status 留给 main 落 verified (B5-①) ★ |
| A-19 | ★**交卷前实跑 7 条命令并贴原样输出** ★ | ✅ **通过** | 见 B6 |
| A-20 | ★**交卷前最后一件事: 再实跑一次 R6 (ISS-223 可能在本单期间落表)** ★ | ✅ **通过** | 见 B6 ⑨ (★交卷那一刻盘上 md5 才是锚点目标值★) |
| A-21 | ★**不许碰 PCB 布线 / 布局 / 板框** ★ | ✅ **通过** | 本单与 PCB 零交集 |
| A-22 | ★**零外发且缺口一律自己网上查 + 标证据等级** ★ | ✅ **不适用** | ★**本单无外部信息缺口** (全部是本机文件/脚本的实读与对账) ⇒ **没有需要外查的项** ★ |

---

## B3 证据分级

| 结论 | 证据等级 | 怎么量的 |
|---|---|---|
| 网表 / 脚表现 md5 = `13f59a43dbd35dc6cb16e897c8c891ab` / `a600afae493f5a7a6c55f46ad35ac89c` | ★**`[实测]`** ★ | ★**本机 `md5sum`** (2026-11-16 04:1x) ★ |
| 落表台账四项齐全 (单号 ISS-220 + 文件名 + 新 md5 + 旧 md5) | ★**`[实测]`** ★ | ★**本机 grep `HW/SCHEMATIC_LANDING_V1_LANDED.md` (L1/L4/L108/L110/L204/L206)** ★ |
| 门禁脚本 mtime (2026-11-15 23:59) 早于落表 (02:32) ⇒ 脚本没被碰过 ⇒ 是锚点过期 | ★**`[实测]`** ★ | ★**本机 `stat -c '%n %y'`** ★ |
| `check_demo_panel_spec.py` R1~R7 全过 (rc=0) + selftest 16/16 (rc=0) | ★**`[实测]`** ★ | ★**本机实跑 (B6 ①②)** ★ |
| `timing_check.py` 70/70 全过 (rc=0) | ★**`[实测]`** ★ | ★**本机实跑 (B6 ⑦)** ★ |
| 喂落表前网表 ⇒ **正好只有那 2 条内容断言红 (68/70)** ⇒ 这 2 条红是网表真值变化引起的 | ★**`[实测]`** ★ | ★**本机 `python3 SW/tools/timing_check.py --netlist state/.bak_iss220/HW_netlist_v1.csv.bak_iss220`** ★ |
| SW 侧 md5 基线清点 8 条 (S-01…S-08) | ★**`[实测]`** ★ | ★**本机 `grep -rnoE '\b[0-9a-f]{32}\b' SW/` + 4 文件名 grep** ★ |
| ISS-223 落表后 SW 门禁会再红 | ★**`[推算]`** ★ | ★**机制推演 (锚点 ↔ 盘上 比的是 md5, 真源一变就不等) + 与 MECH C21/G5b 同一设计 (★只读参照★)** ★ |
| 新网表 I2C_A 注记与实算一致 (186ns vs 186.4ns, 误差 1.00×) | ★**`[实测]`** ★ | ★**本机 `timing_check.py` 输出 `netlist_annotation_ns=186.0` / `annotation_error_ratio=1.0`** ★ |
| 板 / 屏 / 实物时延 | ★**`[0数据]`** ★ | ★**板与屏不在本机 ⇒ 实物 [实测] = 0 条** ★ |

---

## B4 接口取值声明 (interface_claims)

| key | value | 说明 | ref |
|---|---|---|---|
| `sw_md5_baseline_ledger` | `SW/SW_MD5_BASELINE_LEDGER.md` | ★**SW 侧受保护真源的 md5 基线台账 (锚点 §1 / 全清单 §2 / 留痕 §3 / 交接约定 §4)** ⇒ ★**SW 侧两个门禁 (`check_demo_panel_spec.py` R6/R7 · `timing_check.py` 网表锚点) 都从它读锚点** ⇒ ★**锚点不再硬编码在脚本里** ★ | `SW/SW_MD5_BASELINE_LEDGER.md §1` |
| `sw_md5_landing_records` | `HW/SCHEMATIC_LANDING_V1_LANDED.md` · `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` | ★**落表台账的登记位置 (hw-lead 写, SW 侧只读)** ⇒ ★**锚点里的 md5 必须在这些位置里查到【单号 + 文件名 + 新 md5 + 旧 md5】** ⇒ ★**只改锚点不落表 = 红** ★ | `SW/SW_MD5_BASELINE_LEDGER.md §1 source_ledger.landing_records` |
| `sw_panel_gate_r6_scope` | `锚点 ↔ 落表台账 ↔ 盘上真源 三方一致` | ★**ISS-212 门禁 R6 的判定语义 (ISS-225 后)** ⇒ ★**不再只是"md5 逐字节未变"** ⇒ ★**下游 (main / hw-lead / 后续 SW 单) 看到的红 = "要么真源被换了, 要么锚点过期了", 两种都有据可查** ★ | `SW/tools/check_demo_panel_spec.py` `check_r6_three_way()` |
| `sw_netlist_baseline_states` | `13f59a43dbd35dc6cb16e897c8c891ab` (落表后) · `c78f991283cc82d56c8e3dd31657c785` (落表前) | ★**`HW/netlist_v1.csv` 在落表台账里登记过的两个状态** ⇒ ★**`timing_check.py` 接受这两个 md5, 其它一律红 (⇒ 悄悄换真源必被抓)** ★ | `SW/SW_MD5_BASELINE_LEDGER.md §1` |

---

## B5 未决项与卡点

| 序 | 项 | 卡在谁 | ★**要谁回答什么** ★ |
|---|---|---|---|
| **①** | ★**ISS-225 的 status 落 verified** ★ | ★**main** ★ | ★**本单不自签 `state/issue_log.yaml`** ⇒ ★**请 main 落 verified** (★证据 = B6 全部 7 条命令 rc=0 + Q1 18/18★) ★ |
| **②** | ★**ISS-223 (hw-lead 落表第 2 批) 落表后 SW 侧要重锚** ★ | ★**main → sw-lead** ★ | ★**这是设计, 不是故障**: ★**ISS-223 一改网表/脚表 ⇒ SW 的 R6 会自动红 ("盘上 md5 ≠ 锚点登记")** ⇒ ★**请 main 在 ISS-223 落表后派 sw-lead 走 `SW/SW_MD5_BASELINE_LEDGER.md` §4 的 H-1 流程 (改锚点 3 个字段 + 落表台账位置 + §3 加一行留痕)**** ★ ⇒ ★**本单不预判 ISS-223 会改成什么 md5, 也不许硬写一个"查不到出处"的数当基线** ★ |
| **③** | ★**MECH 闸会因 ISS-223 落表按设计变红 (G5b + C21)** ★ | ★**hw-lead (改) / mech-lead (重锚)** ★ | ★**`MECH/check_demo_struct_truth.py` 的 C21 与本单 R6 是同一套设计** ⇒ ★**ISS-223 落表后 MECH 闸也会红 ⇒ 那是"锚点过期"的红, 要 hw-lead 更新落表台账 + mech-lead 更新锚点** ⇒ ★**本单没改 `MECH/` 一个字节, 也不许为了让 MECH 闸变绿去改 `MECH/`** ★ |
| **④** | ★**SW 侧还有没有第二处"读网表内容硬编码"的断言会在下次落表再红** ★ | ★**sw-lead (下一单)** ★ | ★**本单实测: `timing_check.py` 的 3 条 = 全部同根因, 已收掉**; ★**其余 SW 脚本 (`demo_timing_check.py` / `demo_e2e_budget.py` / `rknn_bench.py` / `isp_budget_solve.py`) 实测零个 md5 硬编码** ⇒ ★**但"读网表内容"型的断言 (如某条 note 的字面值) 本单只清了 `timing_check.py` 里的 2 条** ⇒ ★**下一轮落表前建议再扫一遍 `grep -rn "2380\|2\.38µs" SW/` 类内容指纹** ★ |
| **⑤** | ★**板端 [实测] = 0 条** ★ | ★**板与屏不在本机** ★ | ★**本单所有 [实测] 都是"本机脚本 / 本机文件实读"** ⇒ ★**没有需要外查的缺口** ⇒ ★**零外发** ★ |

---

## B6 自证复现命令 (输出原样)

### ① `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0**

```
✅ ISS-212 demo 显示侧口径门禁: 全过
   R1 demo 屏规格真源 (480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz + 附属必填项) ✅
   R2 demo 规格里整机口径只在「整机路线占位区」内 ✅
   R3 pipeline spec 的 demo 活动口径已重锚 ✅
   R4 整机路线占位仍在且带「整机路线·暂缓」 ✅
   R5 逐处定性表 (22 + 16 = 38 处) 完整 ✅
   R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致 ✅
   R7 已修复 (留痕) 在场 (ISS-220 落表锚点过期, 不是红灯被调没) ✅
```

### ② `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0 (16/16)**

```
=== SELFTEST (反向用例: 每条都必须在被破坏后变红) ===
  ✅ REV-1 把 pipeline 的 demo 口径塞回 1920×1080               ⇒ R3 变红 ...
  ✅ REV-2 把 pipeline 的 480×640 buffer 塞回 1920×1080 buffer ⇒ R3 变红 ...
  ✅ REV-3 把 demo 规格的 480×640 删掉                          ⇒ R1 变红 ...
  ✅ REV-4 把 demo 规格的 2-lane 删掉                           ⇒ R1 变红 ...
  ✅ REV-5 把 demo 规格的「无 DCS」结论删掉                          ⇒ R1 变红 ...
  ✅ REV-6 把 demo 规格的 I2C ≤100kHz 上限删掉                          ⇒ R1 变红 ...
  ✅ REV-7 把整机口径塞到 demo 规格的占位区块外                          ⇒ R2 变红 ...
  ✅ REV-8 把定性表的 L-22 行删掉                                 ⇒ R5 变红 ...
--- ISS-225 台账对账反向用例 (R6/R7) ---
  ✅ 基线全绿 (R1~R7 在临时树上全过)
  ✅ REV-9 盘上真源被换掉而锚点没换                                   ⇒ R6 变红 (R6 盘上真源 md5 HW/netlist_v1.csv = 580e695e... ≠ 锚点登)
  ✅ REV-10 锚点改成台账里查不到的哈希                                 ⇒ R6 变红 (R6 盘上真源 md5 HW/netlist_v1.csv = 13f59a43... ≠ 锚点登)
  ✅ REV-11 锚点里的落表单号改坏 (ISS-220 → ISS-999)                ⇒ R6 变红 (R6 HW/netlist_v1.csv: 落表台账里查不到 (单号 ISS-999 / ...)
  ✅ REV-12 落表台账里的落表单号被改坏 (ISS-220 → ISS-999)             ⇒ R6 变红 (R6 HW/netlist_v1.csv: 落表台账里查不到 (单号 ISS-220 / ...)
  ✅ REV-13 把落表台账里那两行删掉                                   ⇒ R6 变红 (R6 HW/netlist_v1.csv: 落表台账里查不到 (单号 ISS-220 / ...)
  ✅ REV-14 把锚点块整个删掉 (fail-closed)                        ⇒ R6 变红 (R6 读不到 SW 侧 md5 基线台账锚点 ⇒ 门禁 fail-closed: ...)
  ✅ REV-15 把「已修复 (留痕)」那一节删掉                              ⇒ R7 变红 (R7 留痕账里没有「已修复 (留痕)」那一节 ...)
--- SELFTEST 16/16 通过 ---
```

### ③ `python3 SW/tools/demo_timing_check.py` ⇒ **rc=0 (51 项断言全过, ISS-221 的 17 条一条没被改红)**

```
  ✅ [ISS-221] SW/DEMO_BOARD_60MS_VERDICT_PLAN.md 判据工具是 demo 真源脚本 (不许拿整机脚本当判据工具) 无
  ✅ [ISS-221] SW/DEMO_BOARD_60MS_VERDICT_PLAN.md 引用了 demo 真源脚本 有
  ✅ [ISS-221] SW/DEMO_BOARD_60MS_VERDICT_PLAN.md demo 活动口径表逐行 == demo 真源脚本输出 本文件无「表 A — demo 活动口径」⇒ 免检 (只有锚点区块)
  ✅ [ISS-221] 两份文档的锚点区块逐项一致                    一致 (SW/DEMO_OD_TIMING_SPEC.md / SW/DEMO_BOARD_60MS_VERDICT_PLAN.md)
------------------------------------------------------------------------------
★板端时延数字 = [0数据] (无板) —— 本脚本只核规格结构, 不编数
```

### ④ `python3 SW/tools/demo_timing_check.py --selftest` ⇒ **rc=0 (18/18)**

```
  ✅ ISS-221 反例14 锚点区块删掉必被抓到            抓到: ['[ISS-221] SW/DEMO_OD_TIMING_SPEC.md 有成对的「demo 预算真源锚点」分区标记', ...]
  ✅ ISS-221 反例15 表 A 手抄错必被抓到           抓到: ['[ISS-221] SW/DEMO_OD_TIMING_SPEC.md demo 活动口径表逐行 == demo 真源脚本输出']
==============================================================================
退出码 rc = 0 (0=自检全过)
```

### ⑤ `python3 SW/tools/demo_e2e_budget.py` ⇒ **rc=0 (自检: 本份账零异常 —— 值型锚点 / 结构恒等 全部对齐)**

```
✅ 自检: 本份账零异常 (值型锚点 / 结构恒等 全部对齐)
```

### ⑥ `python3 SW/tools/demo_e2e_budget.py --selftest` ⇒ **rc=0 (31/31, 9 种改坏 + 1 种源码污染全抓到)**

```
★反向用例: 9 种「改坏」+ 1 种「源码污染」全部必须红 ⇒ 改坏必红
```

### ⑦ `python3 SW/tools/timing_check.py` ⇒ **rc=0 (SELFTEST 70/70 通过, rc=0)** ★★本单一起收掉的同根因恒红★★

★**对照实验 (★证明"红灯跟网表真值走, 不跟脚本走"★)**:

```
$ python3 SW/tools/timing_check.py --netlist state/.bak_iss220/HW_netlist_v1.csv.bak_iss220
  [FAIL] I2C 网表注记与实算一致 (误差 < 1.01 倍 ⇒ 网表侧矛盾已被 ISS-220 d6 消除)
  [FAIL] F3 实读: 网表自带的 t_r 注记 186ns (ISS-220 d6 已把 I2C_A 改成 2.2k@1.8V ⇒ 注记与实算一致, 网表侧矛盾已消除)
SELFTEST 68/70 通过, rc=1        # ★正好只有这 2 条红, 其余 68 条全过 ⇒ 旧网表真有那条矛盾 ⇒ 是真值变化, 不是脚本坏了★
```

### ⑧ `python3 state/merge.py && python3 state/gate_check.py` ⇒ **rc=0, 【Q1 交付齐备率】18/18**

```
✅ STATE.yaml 已刷新 (2026-11-16T04:27:49+08:00)
   产出 276 | 阻塞 43 (高危 33) | 未闭合需求 159 | 冲突 0 | 健康度 red
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-16_hw-lead_ISS220_落表第1批.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-16_sw-lead_ISS225_SW侧md5基线台账化.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-16_mech-lead_ISS224_门禁锚点再基线.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
【Q3 接口声明率】 全员 interface_claims 共 563 条 (sw-lead 148 条)
```

### ⑨ ★**交卷前最后一次 R6 (★ISS-223 可能在本单期间落表★)** ★

```
$ date "+%Y-%m-%d %H:%M:%S"
2026-11-16 04:27:53
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
13f59a43dbd35dc6cb16e897c8c891ab  HW/netlist_v1.csv
a600afae493f5a7a6c55f46ad35ac89c  HW/netlist_v1_pins.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
$ stat -c '%n  %y' HW/netlist_v1.csv HW/netlist_v1_pins.csv
HW/netlist_v1.csv  2026-11-16 02:32:07.519734484 +0800
HW/netlist_v1_pins.csv  2026-11-16 02:32:07.617735670 +0800
$ python3 SW/tools/check_demo_panel_spec.py ; echo RC=$?
✅ ISS-212 demo 显示侧口径门禁: 全过
   ...
   R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致 ✅
   R7 已修复 (留痕) 在场 (ISS-220 落表锚点过期, 不是红灯被调没) ✅
RC=0
```

★**交卷那一刻盘上的 md5 = 锚点目标值** ⇒ ★**交卷时无 ISS-223 落表痕迹 (网表/脚表 mtime 仍是 2026-11-16 02:32 = ISS-220 那次)** ★
⇒ ★**★但本单交卷期间, ISS-223 的**源**已经在动了 (实测 `state/gen_netlist.py` mtime = 2026-11-16 04:21:43, `HW/SCHEMATIC_V1_SPEC.json` / `state/check_netlist.py` 同窗口被改) ⇒ **产物还没重生成** ⇒ **网表 md5 随时可能变** ★★ ⇒
⇒ ★**★若 ISS-223 在你交卷之后落表 ⇒ ★**锚点会再次过期, 但台账对账机制会自动红 (R6 报「盘上真源 md5 … ≠ 锚点登记 … (真源被换了或锚点过期)」), 这是设计** ★★ ⇒ ★**走台账 §4 H-1 重锚即可 (改 §1 的 md5/prev_md5/by 三项 + 加落表台账位置 + §3 加一行留痕)★ ★

### ⑩ ★**边界审计 (本单一个字节没碰的文件)** ★

```
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb \
         HW/PCB/demo_mainboard.kicad_pro HW/SCHEMATIC_LANDING_V1_LANDED.md \
         MECH/check_demo_struct_truth.py MECH/HW_CROSS_REVIEW_TRIAGE.md
```

★**⇒ 与开工前逐字节一致 (见 B6 ⑨ 的 md5 输出 + 本机 `stat` mtime 未变) ★**
★**⇒ 本单改动的文件只有 4 个 + 1 个分片** ★:

| 文件 | 改了什么 |
|---|---|
| `SW/SW_MD5_BASELINE_LEDGER.md` | ★**新建** (SW 侧 md5 基线台账: §1 机器可读锚点 / §2 全清单 + 逐条处置 / §3 已修复 (留痕) / §4 交接约定 / §5 证据分级) ★ |
| `SW/tools/check_demo_panel_spec.py` | ★**R6 重锚 + 升级成三方对账** (新增 `load_sw_anchor` / `load_ledger_records` / `ledger_row_has` / `check_r6_three_way` / `check_r7_trace_present`) + ★**selftest 8 → 16 条** ★ |
| `SW/tools/timing_check.py` | ★**网表 md5 基线台账化** (硬编码 `c78f9912…` → 从台账读 + 三方对账) + ★**2 条 F3 I2C 内容断言重锚** (ISS-220 d6 把网表矛盾真修好了 ⇒ 断言方向反过来) ★ |
| `SW/SW_TIMING_REVIEW.md` · `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` | ★**只加"★该 md5 是 ISS-220 落表**前**的值 + 现值锚点在哪"的注记 (S-03 / S-04 处置) ⇒ 一个历史数字都没改** ★ |
| `state/fragments/sw.yaml` | ★**走 `python3 state/frag_write.py` 原子写** (artifact ×4 / answer ×1 / claim ×4 / need ×1 / status 追加) ★ |

---

## 本单改了什么 (清单)

| # | 文件 | 类型 | 摘要 |
|---|---|---|---|
| 1 | `SW/SW_MD5_BASELINE_LEDGER.md` | ★**新建** ★ | SW 侧受保护真源的 md5 基线台账 (§1 机器可读锚点 YAML 块 / §2 同类基线全清单 8 条 + 逐条处置 / §3 已修复 (留痕) 3 行 / §4 交接约定 H-1~H-6 / §5 证据分级) |
| 2 | `SW/tools/check_demo_panel_spec.py` | ★**改** ★ | R6 重锚 + 三方对账 (6 项核对) + 新增 R7 留痕在场 + selftest 8→16 条 (新增 REV-9~REV-15) + 锚点从硬编码搬到台账 |
| 3 | `SW/tools/timing_check.py` | ★**改** ★ | 网表 md5 基线 → 台账驱动 (三方对账) + 2 条 F3 I2C 内容断言重锚 (ISS-220 d6 把网表矛盾真修好了) ⇒ 65/68 → 70/70 |
| 4 | `SW/SW_TIMING_REVIEW.md` · `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` | ★**改 (只加注记)** ★ | S-03 / S-04 处置: 标注"该 md5 = ISS-220 落表前的值 + 现值锚点在哪" ⇒ **历史数字一个没改** |
| 5 | `state/fragments/sw.yaml` | ★**改 (原子写)** ★ | artifact ×4 / answer ×1 / interface_claim ×4 / need ×1 / status 追加 |

---

## ★边界审计 (本单自证: 哪些文件我写了 / 哪些我一个字节没动)

| 项 | 状态 |
|---|---|
| ★**`HW/` 下任何文件** ★ | ★**零写入** ★ (网表 / 脚表 / 板 / `.kicad_pro` / 原理图 / BOM / 落表台账 全只读) |
| ★**`MECH/` 下任何文件** ★ | ★**零写入** ★ (★`check_demo_struct_truth.py` 的 C21 只读参照★) |
| ★**`state/issue_log.yaml`** ★ | ★**零写入** ★ (★status 留给 main★) |
| ★**`PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/`** ★ | ★**零写入** ★ |
| ★**别人的分片 (`state/fragments/{pm,hw,mech}.yaml`)** ★ | ★**零写入** ★ |
| ★**PCB 布线 / 布局 / 板框** ★ | ★**零触碰** ★ |
| ★**`SW/tools/demo_timing_check.py` / `SW/tools/demo_e2e_budget.py`** ★ | ★**零写入** ★ (ISS-221 的件, 只许读不许改) |
| ★**`--skip-md5` 默认值** ★ | ★**没动** ★ (★默认路径仍校 R6 + R7★) |
| ★**外发动作** ★ | ★**零** ★ |
| ★**自签 issue** ★ | ★**没有** ★ |

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

| # | to | 请求 |
|---|---|---|
| 1 | ★**hw-lead** ★ | ★**不需要你改任何东西** —— 只登记一条信息依赖: ★**你下次落表 (ISS-223) 若改了 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv`, 请在落表台账里写清【落表单号 + 文件名 + 新 md5 + 旧 md5】四项** ⇒ ★**SW 侧的三方对账直接吃这份台账** ⇒ ★**否则 SW 门禁会红 (这是设计, 不是 bug)** ★ |
| 2 | ★**main** ★ | ★**ISS-223 落表后派 sw-lead 重锚** (走 `SW/SW_MD5_BASELINE_LEDGER.md` §4 H-1) ★ |

---

## 待办: 需要项目总工做什么

1. ★**落 ISS-225 的 verified** (★证据 = B6 ①②③④⑤⑥⑦⑧ 全部 rc=0 + Q1 18/18★) ★
2. ★**ISS-223 落表后派 sw-lead 重锚 SW 侧锚点** (★流程写在 `SW/SW_MD5_BASELINE_LEDGER.md` §4 H-1★) ★
3. ★**知会 mech-lead**: ★**ISS-223 落表后 MECH 闸的 G5b + C21 会按设计变红** ⇒ ★**那是"锚点过期"的红, 处置同 H-1 (更新 MECH 锚点 + 落表台账) ★**⇒ ★**本单没改 `MECH/` 一个字节, 也不许为了让 MECH 闸变绿去改 `MECH/`** ★

---

## 阻塞: 缺什么信息

★**无阻塞** ★ —— ★**本单全部结论都来自本机文件与本机脚本实读; 没有需要外部信息 (官网 / 媒体 / 供应商) 的缺口 ⇒ 零外发 ⇒ 板端 [实测] = 0 条如实标注** ★
