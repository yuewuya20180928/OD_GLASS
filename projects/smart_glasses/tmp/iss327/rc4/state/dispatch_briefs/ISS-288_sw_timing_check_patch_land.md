★**ISS-288 · sw-lead 任务书 —— ★★【把 ISS-285 设计好的补丁真正落进 `SW/tools/timing_check.py`】★★** ★ (main · 2026-11-17 14:1x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 14:1x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-288 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · SW 侧门禁口径收口 · 零写板 · 零落表**★ ⇒ ★**续做, 不是从零做**★

---

## ① 前提已变 (★本单为什么现在才存在★)

★**ISS-285 (sw-lead · 已 verified) 当时判定的是「情形一: ISS-283 未落 verified」⇒ 它只出设计, 不落补丁** ★
⇒ ★**原文**: 「★**本轮只读分析 + 方案页 + 自测设计, 不改 `SW/SW_MD5_BASELINE_LEDGER.md` 锚点 / 不改 `timing_check.py` 判据 / 不改期望值**★」 ★
⇒ ★**而现在 (★2026-11-17 12:30:23★) ISS-283 已落表并 verified** ⇒ ★**情形二成立 ⇒ §1 / §2 的补丁必须落地** ★

★**★ISS-283 落表实况 (★main 14:0x 实测★)**:
| 文件 | 落表前 | 落表后 (现值) |
|---|---|---|
| `HW/netlist_v1.csv` | `87f2f792513584bee3d147883c8fb93b` | ★**`37f62ac3f0b81d92ca7d48fdea717f07`** ★ |
| `HW/netlist_v1_pins.csv` | `8ca46495ba0365a886068fa420b519ac` | ★**`a4270120454aedf7a23c92cd8985c8a6`** ★ |
| `HW/BOM_v1.csv` | — | ★**`5d02bece9477ffce5fbe0193c7d5cce4`** ★ |
| ★板 / `.kicad_pro` ★ | — | ★**`611b869e…` / `3e504d2b…` (未变, 逐字节)** ★ |

★**★所以 `SW/tools/timing_check.py` 现在还有 3 条红 (★main 14:0x 实跑, 原样★)**:
```
  [FAIL] 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)
  [FAIL] 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)
  [FAIL] F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗全 DNP
SELFTEST 68/71 通过, rc=1
```

---

## ② 要交的 (★照 ISS-285 交卷单 §1 / §2 的设计落地, ★别自创口径★)

★**ISS-285 的交卷单 `HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md` §1 / §2 里, 补丁已经写好了 (★原文写着「待写入 `SW/tools/timing_check.py`」★) ⇒ ★**本单 = 把那份补丁写进去 + 跑自测** ★

| # | 内容 | 来源 |
|---|---|---|
| ★**B1** ★ | ★**网表锚点 ×2 改成「落表台账链头」口径** (★与 `check_demo_panel_spec.py` 的 R6 同源★) ⇒ ★**合法落表 ⇒ 绿** ★ ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 链头无单号 ⇒ 红 (fail-closed 三条一条不许动)** ★ | ★ISS-285 §1.1~§1.5 ★ |
| ★**B1-bugfix** ★ | ★**ISS-285 §1.4 那个口径 bug 一并修掉**: 落表台账登记的是【12 位前缀】而 `netlist_md5_allowed()` 拿 32 位 md5 直接做集合成员判断 ⇒ ★**永远比不中 ⇒ 那条判据恒红** ★ ⇒ ★**修法 = 前缀比对 (★R6 也是 12 位比, 与之同源★)** ★ | ★ISS-285 §1.4 ★ |
| ★**B2** ★ | ★**F4' 的期望随落表更新**: 现在期望是「BAT_DET 三颗全 DNP」⇒ ★**落表后三颗已改必装 ⇒ 该期望已过期** ★ ⇒ ★**新期望必须仍能咬住真问题 (★ISS-285 §2.2 逐项对照过「不许比原来弱」★) ⇒ ★**不许把这条改成永远绿** ★ | ★ISS-285 §2.1~§2.4 ★ |

★**★硬约束 (★违反就是不合格★)**:
- ★**不许动 `check_demo_panel_spec.py` 的 R6 判据逻辑** (★ISS-275 的成果★) ⇒ ★**改完 R6 的读数必须与改前逐字相同** ★
- ★**不许改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 的 `source_ledger.entries` 那两条** (★那是「台账为准」的判据源, 不是本单地界★) ★
- ★**不许放宽 fail-closed 三条** ★
- ★**不许改任何阈值 / 期望值来「让它绿」** ⇒ ★**唯一允许改的期望值 = F4' 那一条【因落表而过期的期望】, 且必须写明「因 2026-11-17 12:30 落表而过期 + 新期望仍咬得住什么」** ★

## ③ 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py; echo "rc=$?"                 # 期望 rc=0 (SELFTEST 71/71)
python3 SW/tools/check_demo_panel_spec.py; echo "rc=$?"         # 期望 rc=0 (R1~R7) ★**读数须与改前逐字相同★**
python3 SW/tools/check_demo_panel_spec.py --selftest; echo "rc=$?"  # 期望 rc=0 (★条数只许增不许减★)
python3 HW/check_onepass_preflight_coverage.py; echo "rc=$?"     # 期望 rc=0
python3 state/merge.py && python3 state/gate_check.py; echo "rc=$?"  # 期望 rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变★★
```

## ④ 交卷物 (★3 件★)

1. ★**交卷单 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md`** (★B1~B6 + 贴 ISS-285 §1/§2 的补丁 diff + 前后 rc 对照★) ★
2. ★**`SW/tools/timing_check.py` 的改动** (★★落表台账链头口径 + 前缀比对 bugfix + F4' 期望更新 + 自测新增用例★) ★
3. ★**分片** `state/fragments/sw.yaml` (★走 `state/frag_write.py --agent sw-lead` 原子写 + grep 校验★) ★

## ⑤ 边界

★零写板 · ★零落表 (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `check_demo_panel_spec.py` 的 R6 判据逻辑** ★ · ★**不许改 SW 台账 §1 的 `source_ledger.entries`** ★ · ★**不许放宽 fail-closed 三条** ★ · ★不碰 `HW/` / `MECH/` 的文件与分片 · ★零外发 · ★**不替老板拍板** ★ · ★**不自签 issue_log** ★

## ⑥ 纪律

★**交卷单第一件事就是 `write` 建骨架** ★ · ★**长任务 `nohup` 后台 + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**分片写完 `grep` 校验自己的 key 在不在** ★
