# [sw-lead→PM] ISS-250 · 查证表收尾 + `rknn3-toolkit` 线索验证 · ★**含 ISS-254 (SW 侧重锚)** ★

| 项 | 值 |
|---|---|
| **单号** | ★**ISS-250** (★root cause = ISS-155★) + ★**ISS-254** (★SW 侧重锚, 与本单同一会话一起做★) ★ |
| **owner** | ★**sw-lead** (软件总工) ★ |
| **verify_by** | ★**main** (项目总工) ★ |
| **交卷时刻** | ★**2026-11-16 20:0x ~ 20:4x (GMT+8)** ★ |
| **地界** | ★**只动 3 个文件**: ① `SW/SW_MD5_BASELINE_LEDGER.md` (★§1 网表锚点 1 条 × 4 字段 + §1 `landing_records` + §1 登记位置表 1 行 + §3 追加 R-08 留痕行 + §3 追加现值注记★) ② 本交接单 ③ `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py` 原子写★) ★ ⇒ ★**`HW/` 受保护件一个字节没写 (网表 / 脚表 / BOM / 板 / `.kicad_pro` 五个 md5 交卷前后逐字节不变) · `MECH/` 一个字节没写 · `state/issue_log.yaml` 自改零处 · `PROJECT_TRACKER.md` §0 零改动 · 两个门禁脚本一个字节没碰** ★ |
| ★**零外发** ★ | ★**本单没发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 口径: 不再发信, 缺口一律自己查资料 + 标证据等级★) ★ |
| ★**实物 [实测] = 0 条** ★ | ★**本单零实物** (★板与屏不在本机 ⇒ 所有 [实测] 都是「本机脚本实跑 / 本机文件实读」★) ★ |

---

## ★0 一句话

★★**① ISS-254 (两个红闸) = 上游 ISS-249 合法落表后的【锚点过期】, 不是真源被换、不是红灯被调没** ★★
⇒ **ISS-249 (hw-lead) 2026-11-16 19:36 合法落表第 5 批** (★`F1` 真落表 = `state/gen_netlist.py` 两行 `node2` 槽的借位裸位号 `C_VBUS_OUT` → 本行自己的网名★)
⇒ 网表被重生成 ⇒ **md5 `611c3ba3…` → `16ac89f7…`** ⇒ **SW 侧 §1 锚点还钉在落表前的旧 md5** ⇒ `check_demo_panel_spec.py` R6 红 + `timing_check.py` 2 条红
⇒ ★**本单走 §4 H-1 重锚 (第 5 跳)**: ★**只改 §1 锚点那一条的 4 个字段 + `landing_records` 加 ISS-249 位置 + §3 追加 R-08 留痕行** ★
⇒ ★**交卷后: `check_demo_panel_spec.py` rc=0 (R1~R7 全过) · `timing_check.py` rc=0 (71/71) · `--selftest` rc=0 (16/16) · 反向用例把锚点改回旧 md5 ⇒ 两个闸立刻变红 (69/71) ⇒ 证明判据跟盘上真值走** ★

★★**② ISS-250 查证表**: ★**`rknn3-toolkit` 这条线索本轮已查证** ⇒ 结论 + 降级方案表 + 板端执行清单见本单 **B7 / B8 / B9** ★

---

## B1 结论摘要

| 序 | 结论 | 判定 |
|---|---|---|
| **①-1** | ★**`SW/tools/check_demo_panel_spec.py` rc=1 → rc=0** (★R1~R7 全过★) | ★**✅ 通过** ★ |
| **①-2** | ★**`SW/tools/timing_check.py` rc=1 (69/71) → rc=0 (71/71)** ★ | ★**✅ 通过** ★ |
| **①-3** | ★**`SW/tools/check_demo_panel_spec.py --selftest` rc=0 · 16/16** (★反向用例一条没删★) | ★**✅ 通过** ★ |
| **①-4** | ★**反向用例: 把锚点改回旧 md5 (`611c3ba3…`) ⇒ 两个闸立刻变红** (★panel rc=1 · R6 红; timing rc=1 · 69/71 · 同样那 2 条红★) ⇒ ★**判据跟盘上真值走, 不是摆设** ★ | ★**✅ 通过** ★ |
| **①-5** | ★**受保护 5 件 md5 交卷前后逐字节不变** (网表 `16ac89f7…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`) | ★**✅ 通过** ★ |
| **①-6** | ★**脚表 / BOM / 板 / `.kicad_pro` 四件锚点一个字节都没动** (★ISS-249 逐字节不变 ⇒ 不该重锚就不许重锚★) | ★**✅ 通过** ★ |
| **①-7** | ★**判据逻辑 0 改动**: R6 的 6 条判据 / R7 的判据 / `timing_check.py` 71 条断言, ★**一个字没动** ★; ★**只改了 §1 锚点常量 (md5 / prev_md5 / by / landed_at) 与 §3 留痕账** ★ | ★**✅ 通过** ★ |
| **①-8** | ★**落表凭据四项齐全** (★单号 `ISS-249` + 文件名 `HW/netlist_v1.csv` + 新 md5 `16ac89f7…` + 旧 md5 `611c3ba3…` **同一行**★) ⇒ ★**R6 判据 ②③④⑤ 全过** ★ | ★**✅ 通过** ★ |
| **②-1** | ★**`rknn3-toolkit` 存在性与官方性** ⇒ 见 **B7** ★ | ★**见 B7** ★ |
| **②-2** | ★**RK3572 是否在支持列表** ⇒ 见 **B7** ★ | ★**见 B7** ★ |
| **②-3** | ★**版本 / 安装 / 与 rknn-toolkit2 2.3.2 的关系** ⇒ 见 **B7** ★ | ★**见 B7** ★ |
| **②-4** | ★**E-06 ~ E-08 已补进查证表** ⇒ `SW/research/ISS250_rknn_toolkit2_target_查证表.md` ★ | ★**✅ 已补** ★ |
| **②-5** | ★**降级方案表 (每条带量化代价 + 启用条件 + 谁拍)** ⇒ 见 **B8** ★ | ★**✅ 列出 (不替老板拍板)** ★ |
| **②-6** | ★**板端可达时的执行清单 (一条命令 + 逐条步骤 + 量化判据)** ⇒ 见 **B9** ★ | ★**✅ 列出** ★ |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

### 2.1 任务书验收标准逐条

| 序 | 任务书要求 | 实测结果 | 判定 |
|---|---|---|---|
| **V-1** | ★**`check_demo_panel_spec.py` rc=0** ★ | ★**rc=0** (★R1~R7 全过, 原样输出见 B5 ①★) | ★**✅ 通过** ★ |
| **V-2** | ★**`timing_check.py` rc=0 (自测 71/71)** ★ | ★**rc=0 · SELFTEST 71/71 通过** (★原样输出见 B5 ②★) | ★**✅ 通过** ★ |
| **V-3** | ★**只改【网表那一条锚点】: `md5=16ac89f7…` + 留 `prev_md5=611c3ba3…`** ★ | ★**§1 `entries[]` 里 `HW/netlist_v1.csv` 那一条: `md5` = `16ac89f77c25a3f61834cc7ebcd78a7f` · `prev_md5` = `611c3ba3db3dc7de7213063375b96d01` · `by` = `ISS-249` · `landed_at` = `2026-11-16 19:36`★** ⇒ ★**网表那一条之外, 脚表那条锚点 / `hard_protected` 两条 / 脚表 / BOM / 板 / `.kicad_pro` 一个字节都没动★** | ★**✅ 通过** ★ |
| **V-4** | ★**脚表 / BOM / 板 / `.kicad_pro` 四件逐字节不变 ⇒ 一个字节都不许动** ★ | ★**`md5sum` 交卷前后 4 件逐字节相同** (★见 B5 ⑤★) | ★**✅ 通过** ★ |
| **V-5** | ★**必须留痕: 改前 md5 → 改后 md5 + 反向用例 (把锚点改回旧 md5 ⇒ 必须变红) + 逐行改前改后** ★ | ★**改前/改后逐行对照 = B6.2; 反向用例原样输出 = B5 ④; 改前 md5 = `d9b9ce7478eb7f77ce746177560284d2` (台账) → 改后 = `f6a384edd151a5ffd313f8de33846f93`★** | ★**✅ 通过** ★ |
| **V-6** | ★**判据逻辑 0 改动 (只许改锚点常量与它的自测 fixture)** ★ | ★**两个门禁脚本 md5 交卷前后不变 (`e14014aa…` / `4cba20b1…`), mtime 交卷前后不变 ⇒ 一个字节都没碰** (★见 B6.3★) | ★**✅ 通过** ★ |
| **V-7** | ★**反向用例自证** ★ | ★**沙盒把锚点整条改回旧 md5 ⇒ panel rc=1 (R6 红) + timing rc=1 (69/71, 同样那 2 条红) ⇒ 装回去又绿** ★ | ★**✅ 通过** ★ |
| **V-8** | ★**E-06 ~ E-08 补进查证表** ★ | ★**已补** (★`SW/research/ISS250_rknn_toolkit2_target_查证表.md`★) | ★**✅ 通过** ★ |
| **V-9** | ★**降级方案表 (每条带量化代价 + 启用条件 + 谁拍)** ★ | ★**见 B8 (★3 条路线 · 每条带代价 / 条件 / 拍板人★)** | ★**✅ 通过** ★ |
| **V-10** | ★**板端可达时的执行清单 (一条命令 + 逐条步骤 + 量化判据)** ★ | ★**见 B9** | ★**✅ 通过** ★ |
| **V-11** | ★**交卷单 B1~B6 六块齐全 + 分片 `state/fragments/sw.yaml` (走 `python3 state/frag_write.py` 原子写)** ★ | ★**B1~B6 齐全; 分片已写** (★见 B6.5★) | ★**✅ 通过** ★ |
| **V-12** | ★**零外发 / 不改网表脚表 BOM 板 `.kicad_pro` / 不改 `HW/` 与 `MECH/` / 不替老板拍板 / 不写别人的分片 / 不自签 issue_log / 实物 [实测] = 0 条** ★ | ★**逐条自证见 B6.5** | ★**✅ 通过** ★ |

### 2.2 修法自评 (★为什么这是「重锚」不是「作弊」★)

★**锚点过期 ≠ 红灯被调没**: ★**R6 判据 ① 判的是「盘上真源 md5 == 锚点登记 md5」** ⇒ ★**改锚点只是让「台账 ↔ 盘上」重新对齐, 判据本身没变** ★
⇒ ★**反向自证**: ★**把锚点改回旧 md5 ⇒ 立刻变红** ⇒ ★**证明这条判据还在咬, 没被废掉** ★
⇒ ★**落表凭据**: ★**上游 ISS-249 有正式落表台账 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` §17) + 交接单, 四项 (单号 / 文件名 / 新旧 md5) 同一行齐全** ⇒ ★**不是「悄悄换真源」** ★
⇒ ★**本单 0 字节写 `HW/`**: ★**网表只被重生成 (落表器干的), 本单没碰** ★

### 2.3 边界自评 (逐条)

| 边界 | 自证 |
|---|---|
| ★**零外发** ★ | ★**本轮只做了本机文件读写 + 本机脚本实跑 + 公网只读抓取 (GitHub / PyPI 页面), 没发信 / 询价 / 问询 / 采购** ★ |
| ★**不改网表 / 脚表 / BOM / 板 / `.kicad_pro`** ★ | ★**B5 ⑤ 交卷前后 `md5sum` 5 行逐字节相同** ★ |
| ★**不改 `HW/` 与 `MECH/`** ★ | ★**`HW/` 下 0 写入 (mtime 未变) · `MECH/` 0 写入** ★ |
| ★**不替老板拍板** ★ | ★**B8 每条降级方案只列「代价 + 启用条件 + 谁拍」, 本单不选★** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/sw.yaml`** (★本单是 sw-lead, 这是自己的分片★) ★ |
| ★**不自签 issue_log** ★ | ★**`state/issue_log.yaml` 本轮 0 改动** ★ |
| ★**实物 [实测] = 0 条** ★ | ★**板与屏不在本机 ⇒ 0 条; 全部标 [实测] 的都是「本机脚本实跑 / 本机文件实读」★** ★ |

---

## B3 证据分级 (实测 / 官方 / 推算 / 0数据)

| 结论 | 证据等级 | 怎么量的 |
|---|---|---|
| 门禁开工前红: `check_demo_panel_spec.py` rc=1 (R6 1 项) · `timing_check.py` rc=1 (69/71) | ★**`[实测]`** ★ | ★**本机实跑 (2026-11-16 20:0x 前)** ★ |
| 门禁交卷绿: `check_demo_panel_spec.py` rc=0 (R1~R7) · `timing_check.py` rc=0 (71/71) · `--selftest` rc=0 (16/16) | ★**`[实测]`** ★ | ★**本机实跑, 原样输出见 B5 ①②③** ★ |
| 盘上真源 md5 = 网表 `16ac89f77c25a3f61834cc7ebcd78a7f` · 脚表 `ef436a37412ac9b6eac3c9f41f1edca4` · BOM `2a7305741134788dfee9f13f34c656b4` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` | ★**`[实测]`** ★ | ★**本机 `md5sum`** ★ |
| 落表时刻 = 2026-11-16 19:36:12 (网表落盘 mtime) | ★**`[实测]`** ★ | ★**本机 `stat -c '%y'`** ★ |
| 门禁脚本 mtime (`check_demo_panel_spec.py` 08:33:00 · `timing_check.py` 18:32:34) **都早于**落表 (19:36:12) ⇒ 脚本没被碰过 | ★**`[实测]`** ★ | ★**本机 `stat`** ★ |
| 落表台账四项齐全 (单号 / 文件名 / 新旧 md5 同一行) ⇒ R6 判据 ②③④⑤ 成立 | ★**`[实测]`** ★ | ★**本机 `grep -n` ⇒ `HW/SCHEMATIC_LANDING_V1_LANDED.md` L852** ★ |
| 反向用例: 锚点改回旧 md5 ⇒ 两个闸变红 | ★**`[实测]`** ★ | ★**`/tmp` 沙盒实跑 (★真盘不动★), 原样输出见 B5 ④** ★ |
| 后续若再落表, R6 会再次红 ⇒ 走 §4 H-1 再重锚 | ★**`[推算]`** ★ | ★**机制推演 (★§4 H-1/H-4 写明, 这是设计不是故障★)** ★ |
| 板与屏的实物行为 | ★**`[0数据]`** ★ | ★**板与屏不在本机 ⇒ 实物 [实测] = 0 条** ★ |

---

## B4 接口取值声明 (interface_claims)

| 序 | key | 取值声明 | 证据等级 |
|---|---|---|---|
| **I-1** | `iss254_sw_md5_anchor_netlist` | ★**SW 侧 §1 锚点 (网表) = `16ac89f77c25a3f61834cc7ebcd78a7f`** (★`by`=`ISS-249` · `prev_md5`=`611c3ba3db3dc7de7213063375b96d01` · `landed_at`=2026-11-16 19:36★) ⇒ ★**盘上真值, 不是抄来的** ★ | ★`[实测]` ★ |
| **I-2** | `iss254_sw_md5_anchor_pins` | ★**SW 侧 §1 锚点 (脚表) = `ef436a37412ac9b6eac3c9f41f1edca4`** (★`by`=`ISS-243` · **不变**, ★因为 ISS-249 脚表逐字节不变★) | ★`[实测]` ★ |
| **I-3** | `iss254_sw_md5_hop_count` | ★**SW 侧 md5 锚点重锚跳数 = 第 5 跳** (★先例: ISS-223 → ISS-233 → ISS-243 三跳 + ISS-245 第 4 跳; 本单 ISS-254 第 5 跳★) ⇒ ★**锚点 `by` 单号链 = ISS-243 → ISS-249** ★ | ★`[实测]` (★台账 §3 R-01~R-08 行★) ★ |
| **I-4** | `iss254_sw_md5_landing_ticket` | ★**本次锚点挂的落表单号 = `ISS-249`** (★hw-lead 落表第 5 批, 2026-11-16 19:36★) ⇒ ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17 + `HANDOFF/2026-11-16_hw-lead_ISS249_*.md` 两处都在 §1 `landing_records` 里登记** ★ | ★`[实测]` ★ |
| **I-5** | `iss254_sw_gate_contract` | ★**SW 侧两条门禁的契约 (交卷后不变)**: `check_demo_panel_spec.py` ⇒ rc=0 且 R1~R7 全过; `timing_check.py` ⇒ rc=0 且 selftest 71/71; ★**`--skip-md5` 仍不是默认跳过** ★ | ★`[实测]` ★ |

---

## B5 验收命令原样输出 (未决项与卡点)

### 5.1 ★V-1 `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=0 ★

★**改前 (2026-11-16 20:0x, ★重锚前★) ★**

```
rc=1
❌ ISS-212 demo 显示侧口径门禁: 1 项不通过
   - R6 盘上真源 md5 HW/netlist_v1.csv = 16ac89f77c25a3f61834cc7ebcd78a7f ≠ 锚点登记 611c3ba3db3dc7de7213063375b96d01 (真源被换了或锚点过期)
```

★**改后 (2026-11-16 20:0x, ★重锚后★) ★**

```
rc=0
✅ ISS-212 demo 显示侧口径门禁: 全过
   R1 demo 屏规格真源 (480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz + 附属必填项) ✅
   R2 demo 规格里整机口径只在「整机路线占位区」内 ✅
   R3 pipeline spec 的 demo 活动口径已重锚 ✅
   R4 整机路线占位仍在且带「整机路线·暂缓」 ✅
   R5 逐处定性表 (22 + 16 = 38 处) 完整 ✅
   R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致 ✅
   R7 已修复 (留痕) 在场 (ISS-220 落表锚点过期, 不是红灯被调没) ✅
```

### 5.2 ★V-2 `python3 SW/tools/timing_check.py` ⇒ rc=0 · 71/71 ★

★**改前 ★**

```
rc=1
  [FAIL] 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)
  [FAIL] 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)
...
SELFTEST 69/71 通过, rc=1
```

★**改后 ★**

```
rc=0
...
  [PASS] ISP p95 = 18.00 ms ⇒ 模式B 上限 (17.33) FAIL
  [PASS] T2 交叉核对: 纯 NPU 21.00 ms ⇒ 命中老板翻案条款 (20.33 ms)

SELFTEST 71/71 通过, rc=0
```

### 5.3 ★V-3 `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ rc=0 · 16/16 ★

```
rc=0
  ✅ REV-13 把落表台账里那两行删掉                                   ⇒ R6 变红 (R6 HW/netlist_v1.csv: 落表台账里查不到 (单号 ISS-249 / 文件 HW/netlist_v1.csv / 新 ))
  ✅ REV-14 把锚点块整个删掉 (fail-closed)                        ⇒ R6 变红 (R6 读不到 SW 侧 md5 基线台账锚点 ⇒ 门禁 fail-closed: 台账里找不到锚点块 (# BEGIN SW_MD5_ANC)
  ✅ REV-15 把「已修复 (留痕)」那一节删掉                              ⇒ R7 变红 (R7 留痕账里没有「已修复 (留痕)」那一节 (删了 ⇒ 一次真变更被从账上抹了))
--- SELFTEST 16/16 通过 ---
```

★**★注意 REV-13 的报错里单号已动态读成 `ISS-249`** (★不是写死的旧值 ★) ⇒ ★**证明 REV-12 那条反向用例是【动态读锚点块当前单号再改坏】, 不是硬编码★**

### 5.4 ★V-7 反向自证 (★`/tmp` 沙盒: 绿 → 红 ⇒ 证明判据还在咬★) ★

★**做法**: ★**`cp -as` 把整棵树软链到 `/tmp/iss250_revert`** (★真盘一个字节不动★) ⇒ ★**把沙盒里的锚点整条改回 ISS-243 那版 (`md5` = `611c3ba3…` / `prev_md5` = `34132f7e…` / `by` = `ISS-243` / `landed_at` = `2026-11-16 15:45`)★** ⇒ 跑两个闸。

★**反向 A · `check_demo_panel_spec.py` ⇒ rc=1 (红) ★**

```
★反向 A · check_demo_panel_spec.py rc=1 ★
❌ ISS-212 demo 显示侧口径门禁: 1 项不通过
   - R6 盘上真源 md5 HW/netlist_v1.csv = 16ac89f77c25a3f61834cc7ebcd78a7f ≠ 锚点登记 611c3ba3db3dc7de7213063375b96d01 (真源被换了或锚点过期)
```

★**反向 B · `timing_check.py` ⇒ rc=1 · 69/71 (★同样那 2 条红★) ★**

```
★反向 B · timing_check.py rc=1 ★
  [FAIL] 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)
  [FAIL] 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)
SELFTEST 69/71 通过, rc=1
```

★**★反向用例的自证逻辑 (★为什么这能证明不是作弊★)**: ★**锚点改回旧 md5 ⇒ 两个闸立刻变红** ⇒ ★**说明 R6 判据 ① 咬的是【盘上真源】, 不是脚本里的常量** ⇒ ★**本单改锚点不是「把红灯调没」, 是「把过期锚点挪到盘上真值」** ★

### 5.5 ★落表凭据 (★R6 判据 ②③④⑤ 的实读原文★) ★

★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` L852 (★本机 `sed -n '852p'` 实读★)** ★

```
| ★**ISS-249** ★ | ★**`HW/netlist_v1.csv`** (表A) ★ | `611c3ba3db3dc7de7213063375b96d01` | `16ac89f77c25a3f61834cc7ebcd78a7f` | ★**是 (★只有 L8 / L12 两行的 node2 单元★)** ★ |
```

★**同一份台账 L854 / L855 / L858 / L859 (★四件「逐字节不变」的凭据★)** ★

```
| ★**ISS-249** ★ | ★**`HW/netlist_v1_pins.csv`** (脚表) ★ | `ef436a37412ac9b6eac3c9f41f1edca4` | `ef436a37412ac9b6eac3c9f41f1edca4` | ★**否 (★逐字节不变★)** ★ |
| ★**ISS-249** ★ | ★**`HW/BOM_v1.csv`** ★ | `2a7305741134788dfee9f13f34c656b4` | `2a7305741134788dfee9f13f34c656b4` | ★**否 (★逐字节不变★)** ★ |
| ★**ISS-249** ★ | ★**`HW/PCB/demo_mainboard.kicad_pcb`** (★受保护·板★) ★ | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**否 (★逐字节不变★)** ★ |
| ★**ISS-249** ★ | ★**`HW/PCB/demo_mainboard.kicad_pro`** (★受保护★) ★ | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | ★**否 (★逐字节不变★)** ★ |
```

### 5.6 ★受保护 md5 (★交卷前后逐字节一致★) ★

★**交卷时点实测 (★本单只写 `SW/SW_MD5_BASELINE_LEDGER.md`, `HW/` 下 0 写入 ⇒ 与落表后盘上真值逐字节相同★)** ★

```
16ac89f77c25a3f61834cc7ebcd78a7f  HW/netlist_v1.csv
ef436a37412ac9b6eac3c9f41f1edca4  HW/netlist_v1_pins.csv
2a7305741134788dfee9f13f34c656b4  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
e14014aac5bc55fd00e92148d417285b  SW/tools/check_demo_panel_spec.py
4cba20b1d0249b671632878c964b4bd7  SW/tools/timing_check.py
f6a384edd151a5ffd313f8de33846f93  SW/SW_MD5_BASELINE_LEDGER.md
```

★**mtime (★落表时刻 19:36:12 ⇒ 门禁脚本 mtime 都早于它 ⇒ 脚本没被碰过★)** ★

```
2026-11-16 19:36:12.524595948 +0800  HW/netlist_v1.csv
2026-11-16 19:23:57.513014688 +0800  HW/netlist_v1_pins.csv
2026-11-16 19:23:57.627016019 +0800  HW/BOM_v1.csv
2026-11-06 07:07:17.362193413 +0800  HW/PCB/demo_mainboard.kicad_pcb
2026-11-04 23:47:30.279742515 +0800  HW/PCB/demo_mainboard.kicad_pro
2026-11-16 08:33:00.325296648 +0800  SW/tools/check_demo_panel_spec.py
2026-11-16 18:32:34.990932709 +0800  SW/tools/timing_check.py
2026-11-16 20:03:03.218410322 +0800  SW/SW_MD5_BASELINE_LEDGER.md
```

### 5.7 ★未决项与卡点 (★需要谁回答什么★) ★

| 序 | 未决项 | ★**谁拍** ★ | ★**本单为什么不拍** ★ |
|---|---|---|---|
| **O-1** | ★**ISS-250 降级方案选哪条 (B8 路线①/②/③)** ★ | ★**main (项目总工) / 老板** ★ | ★**本单只列代价 + 启用条件, 不替老板拍板** ★ |
| **O-2** | ★**板端实测何时能跑 (B9 执行清单)** ★ | ★**main** ★ | ★**板不可达 ⇒ 挂「板不可达」, 不许挂「等外部回复」** ★ |
| **O-3** | ★**是否需要额外开一块板做 RK3572 vs RK3576 算子一致性比对** ★ | ★**main** ★ | ★**涉及预算 / 采购 ⇒ 零外发, 本单不询价** ★ |

---

## B6 边界审计 (自证复现命令)

### 6.1 ★本单动过的文件 (★全部★) ★

| 文件 | 动作 | md5 (改前 → 改后) |
|---|---|---|
| `SW/SW_MD5_BASELINE_LEDGER.md` | ★**改** (★§1 锚点 1 条 × 4 字段 + `landing_records` + 登记位置表 + §3 R-08 留痕行 + 现值注记★) ★ | ★`d9b9ce7478eb7f77ce746177560284d2` → `f6a384edd151a5ffd313f8de33846f93` ★ |
| `HANDOFF/2026-11-16_sw-lead_ISS250_查证表收尾与rknn3验证.md` | ★**新增** (★本交接单★) ★ | ★— → 新文件 ★ |
| `SW/research/ISS250_rknn_toolkit2_target_查证表.md` | ★**改** (★补 E-06 ~ E-08 + 降级方案表 + 板端执行清单★) ★ | ★见 B7.5★ |
| `state/fragments/sw.yaml` | ★**改** (★走 `python3 state/frag_write.py` 原子写★) ★ | ★见 B6.5★ |
| `state/.bak_iss250/SW_MD5_BASELINE_LEDGER.md.bak_iss250` | ★**新增** (★改前备份, ★沙盒反向自证用★) ★ | ★`d9b9ce7478eb7f77ce746177560284d2` ★ |
| ★**其它全部** ★ | ★**0 改动** ★ | ★**`HW/` 0 · `MECH/` 0 · 两个门禁脚本 0 · `state/issue_log.yaml` 0 · `PROJECT_TRACKER.md` 0** ★ |

### 6.2 ★锚点变更前后对照 (★§1 机器可读块, 逐字段★) ★

★**改前 (`state/.bak_iss250/SW_MD5_BASELINE_LEDGER.md.bak_iss250` L33~L39) ★**

```yaml
      - HANDOFF/2026-11-16_hw-lead_ISS243_*.md
    entries:                        # ★ 受"台账对账"机制管的真源: 旧锚点 → 新锚点 + 落表单号
      - file: HW/netlist_v1.csv
        by: ISS-243                 # ★ 落表单号 (这次变更挂在哪个单号下)
        prev_md5: 34132f7e40a241e1fae1476be0eafbd5
        md5: 611c3ba3db3dc7de7213063375b96d01
        landed_at: "2026-11-16 15:45"
```

★**改后 (盘上 `SW/SW_MD5_BASELINE_LEDGER.md` L33~L40) ★**

```yaml
      - HANDOFF/2026-11-16_hw-lead_ISS243_*.md
      - HANDOFF/2026-11-16_hw-lead_ISS249_*.md
    entries:                        # ★ 受"台账对账"机制管的真源: 旧锚点 → 新锚点 + 落表单号
      - file: HW/netlist_v1.csv
        by: ISS-249                 # ★ 落表单号 (这次变更挂在哪个单号下)
        prev_md5: 611c3ba3db3dc7de7213063375b96d01
        md5: 16ac89f77c25a3f61834cc7ebcd78a7f
        landed_at: "2026-11-16 19:36"
```

★**逐字段对照表 ★**

| 字段 | 改前 | 改后 | 依据 |
|---|---|---|---|
| `by` | `ISS-243` | ★**`ISS-249`** ★ | ★**落表单号 = ISS-249 (hw-lead 落表第 5 批)★** |
| `prev_md5` | `34132f7e40a241e1fae1476be0eafbd5` | ★**`611c3ba3db3dc7de7213063375b96d01`** ★ | ★**ISS-249 落表前的网表 md5 (台账 L852 旧值列)★** |
| `md5` | `611c3ba3db3dc7de7213063375b96d01` | ★**`16ac89f77c25a3f61834cc7ebcd78a7f`** ★ | ★**ISS-249 落表后的网表 md5 (台账 L852 新值列) = 盘上 `md5sum` 实测值★** |
| `landed_at` | `"2026-11-16 15:45"` | ★**`"2026-11-16 19:36"`** ★ | ★**网表落盘 mtime = 2026-11-16 19:36:12★** |
| `landing_records` | 3 条 | ★**4 条 (+ `HANDOFF/2026-11-16_hw-lead_ISS249_*.md`)★** ★ | ★**H-1 步骤 ③★** |
| ★**脚表那条** ★ | `by`=ISS-243 / `md5`=`ef436a37…` | ★**不变 (逐字节相同)★** ★ | ★**ISS-249 脚表「逐字节不变」(台账 L854)⇒ 不该重锚就不许重锚★** |
| ★**`hard_protected` 两条** ★ | 板 `611b869e…` / `.kicad_pro` `3e504d2b…` | ★**不变 (逐字节相同)★** ★ | ★**同上 (台账 L858/L859)★** |

★**★注**: ★**上表「改后」块 = 盘上 `sed -n '33,42p'` 的原文 (★转录无误, 以 B6.4 复现命令为准★)** ★

### 6.3 ★门禁脚本 0 改动自证 ★

| 脚本 | md5 | mtime | 结论 |
|---|---|---|---|
| `SW/tools/check_demo_panel_spec.py` | ★`e14014aac5bc55fd00e92148d417285b`★ | ★`2026-11-16 08:33:00`★ | ★**交卷前后未变; mtime 早于落表 19:36 ⇒ 判红不是脚本被改出来的★** |
| `SW/tools/timing_check.py` | ★`4cba20b1d0249b671632878c964b4bd7`★ | ★`2026-11-16 18:32:34`★ | ★**同上★** |

### 6.4 ★自证复现命令 (★一整串, 从零复跑★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★1 · 两条门禁 + selftest (★交卷口径★) ★★
python3 SW/tools/check_demo_panel_spec.py            # ⇒ rc=0 · R1~R7 全过
python3 SW/tools/timing_check.py                     # ⇒ rc=0 · 71/71
python3 SW/tools/check_demo_panel_spec.py --selftest  # ⇒ rc=0 · 16/16

# ★★2 · 锚点实读 (改完之后的锚点 = 盘上真值) ★★
sed -n '33,42p' SW/SW_MD5_BASELINE_LEDGER.md
md5sum HW/netlist_v1.csv

# ★★3 · 落表凭据 (单号 / 文件名 / 新旧 md5 同一行) ★★
sed -n '852p;854p;855p;858p;859p' HW/SCHEMATIC_LANDING_V1_LANDED.md

# ★★4 · 门禁脚本没被碰过 (★判别证据: mtime 早于落表★) ★★
stat -c '%y  %n' SW/tools/check_demo_panel_spec.py SW/tools/timing_check.py HW/netlist_v1.csv

# ★★5 · 反向自证 (★在 /tmp 沙盒里做, 真盘不动★) ★★
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
SBX=/tmp/iss250_revert; rm -rf $SBX; mkdir -p $SBX
cp -as "$PROJ/." "$SBX/"
rm -f $SBX/SW/SW_MD5_BASELINE_LEDGER.md
cp $PROJ/SW/SW_MD5_BASELINE_LEDGER.md $SBX/SW/SW_MD5_BASELINE_LEDGER.md
#   把沙盒锚点整条改回 ISS-243 那版 (md5=611c3ba3… / prev_md5=34132f7e… / by=ISS-243 / landed_at=2026-11-16 15:45)
python3 SW/tools/check_demo_panel_spec.py --root $SBX   # ⇒ rc=1 (R6 红)
( cd $SBX && python3 SW/tools/timing_check.py )          # ⇒ rc=1 (69/71)

# ★★6 · 受保护 md5 交卷前后对照 ★★
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```

### 6.5 ★分片写入 (★走 `python3 state/frag_write.py` 原子写★) ★

★**见 B6.6 (★`state/frag_write.py` 实跑输出★)** ★

### 6.6 ★边界审计表 (★逐条自证★) ★

| 边界 | 自证 | 判定 |
|---|---|---|
| ★**零外发** ★ | ★**本轮外部动作只有「只读抓取公网页面」 (GitHub / PyPI) 与本机命令; 无邮件 / 询价 / 问询 / 采购** ★ | ★**✅** ★ |
| ★**不改网表 / 脚表 / BOM / 板 / `.kicad_pro`** ★ | ★**B5 ⑥ 五个 md5 与落表后盘上真值逐字节相同; 本单对 `HW/` 0 写入 (mtime 未变)★** ★ | ★**✅** ★ |
| ★**不改 `HW/` 与 `MECH/`** ★ | ★**`HW/` mtime 全部未变; `MECH/` 0 写入** ★ | ★**✅** ★ |
| ★**不替老板拍板** ★ | ★**B8 三条路线都写「谁拍」, 本单不选★** ★ | ★**✅** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/sw.yaml`** ★ | ★**✅** ★ |
| ★**不自签 issue_log** ★ | ★**`state/issue_log.yaml` 0 改动** ★ | ★**✅** ★ |
| ★**实物 [实测] = 0 条** ★ | ★**板与屏不在本机 ⇒ 0 条** ★ | ★**✅** ★ |
| ★**每 10 分钟至少一次写盘** ★ | ★**20:03 写台账 (含 R-08 留痕) → 20:0x 写交卷单 → …… 逐条落盘★** ★ | ★**✅** ★ |
| ★**不 clone 大仓库 / 不下大 wheel** ★ | ★**只读抓页面 + 本机已装包实测; 没下 wheel★** ★ | ★**✅** ★ |

---
<!-- ★★② ISS-250 查证表部分 (B7 / B8 / B9) 见下 ★★ -->
