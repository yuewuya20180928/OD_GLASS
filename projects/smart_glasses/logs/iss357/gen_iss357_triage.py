#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-357 · sw-lead · 生成两份交卷物 (同源, 不重写)
  ① SW/SW_NEEDS_TRIAGE.md
  ② HANDOFF/2026-11-23_sw-lead_ISS357_SW未答需求分类.md
★两份 + 分片三段台账 全部来自 logs/iss357/iss357_data.py + state/fragments/sw.yaml ⇒ 同源。
"""
import os
import subprocess
import sys
from collections import Counter

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from iss357_data import CLOSE, WO_BOSS, KEEP, ANSWERS  # noqa: E402

with open(os.path.join(PROJ, "state", "fragments", "sw.yaml"), encoding="utf-8") as f:
    frag = yaml.safe_load(f)
NEEDS = frag["needs_from"]
CLOSED = frag["needs_closed"]
LEDGER = frag["needs_open_ledger"]
ANS = frag["answers"]

led = {x["key"]: x for x in LEDGER}
cls_closed = {x["key"]: x for x in CLOSED}
CLS_LABEL = {"①int": "① 内部等另一个总工", "②boss": "② waiting_on=boss",
             "③ext": "③ 外部依赖 (vendor)", "④c": "④ waiting_on 空", "④b": "④ waiting_on 空",
             "④a": "④ waiting_on 空"}


def _esc(v):
    """★表格单元格里的裸 | 必须转义, 否则 markdown 表格会散★"""
    return str(v).replace("|", "\\|")


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("\n", " ").replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


# ==================================================================== §1 总账
n_orig = 144
n_closed = len(CLOSED)
n_keep = len(NEEDS)
n_ans_new = 9
c_cls = Counter(x["cls"] for x in CLOSED)
c_act = Counter(x["action"] for x in CLOSED)
c_sub = Counter(x["sub"] for x in LEDGER)
boss_keys = [n["key"] for n in NEEDS if (n.get("waiting_on") or "agent") == "boss"]
board_yes = [x for x in LEDGER if x["board"] == "Y"]
board_no = [x for x in LEDGER if x["board"] == "N"]

# ==================================================================== §2 逐条表
def close_rows(pred):
    rows = []
    for x in CLOSED:
        if pred(x):
            rows.append([x["key"], x["cls"], x["action"], x["reason"], x["evidence"], x["evidence_level"]])
    return rows


def keep_rows(pred):
    rows = []
    for x in LEDGER:
        if pred(x):
            rows.append([x["key"], x["cls"] + "/" + x["sub"], x["owner"], x["oneline"], x["why"],
                         x["evidence"], x["evidence_level"], x["board"]])
    return rows



# ---- 按【改分片前】的 (to, waiting_on) 原始归属统计四类 ----
import yaml as _y
with open(os.path.join(HERE, "sw.yaml.bak_pre_iss357"), encoding="utf-8") as _f:
    _orig = _y.safe_load(_f)
_wo0 = {n.get("key"): (n.get("to"), n.get("waiting_on") or "agent") for n in _orig["needs_from"]}
_closed_keys = {x["key"] for x in CLOSED}
_keep_keys = {x["key"] for x in LEDGER}
_ans_keys = {a[0] for a in ANSWERS}


_RAW_WO = {n.get("key"): n.get("waiting_on") for n in _orig["needs_from"]}


def _bucket(k):
    """★完全照任务书 §2 的四类口径★ (① 与 ④ 有意重叠 19 条)"""
    to, wo = _wo0[k]
    raw = _RAW_WO.get(k)
    if wo == "vendor":
        return 3
    if wo == "boss":
        return 2
    if wo == "sw-lead":
        return 5
    # raw is None ⇒ waiting_on 空
    if to in ("hw-lead", "mech-lead"):
        return 1        # ① 内部等另一个总工 (to=hw-lead 17 + to=mech-lead 2)
    if raw == "agent":
        return 1        # ① to=main 且显式 waiting_on=agent (4)
    return 4            # ④ to=main 且 waiting_on 空 (99)


_b = {}
for k in _wo0:
    _b.setdefault(_bucket(k), []).append(k)
def _cnt(bk):
    ks = _b.get(bk, [])
    return (len(ks),
            sum(1 for k in ks if k in _closed_keys),
            sum(1 for k in ks if k in _keep_keys),
            sum(1 for k in ks if k in _ans_keys))


b1, b1c, b1k, b1a = _cnt(1)
b2, b2c, b2k, b2a = _cnt(2)
b3, b3c, b3k, b3a = _cnt(3)
b4, b4c, b4k, b4a = _cnt(4)
b5, b5c, b5k, b5a = _cnt(5)
assert b1 + b2 + b3 + b4 + b5 == 144, (b1, b2, b3, b4, b5)
assert b1c + b2c + b3c + b4c + b5c == n_closed, (b1c, b2c, b3c, b4c, b5c)
assert b1k + b2k + b3k + b4k + b5k == n_keep, (b1k, b2k, b3k, b4k, b5k)

TRIAGE = []
A = TRIAGE.append

A(f"""# SW/SW_NEEDS_TRIAGE.md —— SW 域 needs 144 条四分类逐条处置 (ISS-357)

> **owner**: sw-lead (软件总工) · **单号**: ISS-357 · **日期**: 2026-11-23 · **job**: cron `fb67af40` (ARS45 队列自动派活)
> **同源**: 本页 + `HANDOFF/2026-11-23_sw-lead_ISS357_SW未答需求分类.md` + `state/fragments/sw.yaml` 三段台账全部由 `logs/iss357/iss357_data.py` 生成 ⇒ 同源不重写。
> **边界 (硬)**: ★零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log★
> **证据分级**: `[官网]` (= 机检标签集里的「官方」, 结构域习惯叫「官网」) / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` —— 四档齐 + 推算/0数据按需追加。

---

## §0 · 口径 (先说清「这一页在算什么」)

★**机检口径** (`state/gate_check.py` 实读, 本单零改闸):

```
real_open = needs_total − needs_answered_incoming − needs_closable_unregistered − needs_waiting_external
needs_waiting_external = waiting_on != 'agent'   (boss / vendor / sw-lead 都算「等外部」, 不算谁的锅)
```

⇒ ★**本单的三个动作, 全部落在口径之内, 一个字不改闸**★:

| # | 动作 | 对机检的作用 | 是否「把 needs 删空」 |
|---|---|---|---|
| 1 | **已结 / 已作废**的 need 从 `needs_from` 移出 ⇒ 进 `needs_closed` (每条带 `reason` + `evidence` + `evidence_level` + `closed_at` + `closed_by`) | `needs_total` 与 `real_open` 同时 −1 | ✗ 不是删空 —— ★**每一条都带依据行, 原 `item` 全文一字未删, 全部留档在 `needs_closed`★** |
| 2 | **其实在等老板**的 need, `waiting_on` 从空/`agent` **订正**为 `boss` | `real_open` −1, `needs_waiting_external` +1 | ✗ 不是删条目 —— ★**条目原样留在 `needs_from`, 只是把「等谁」标对★** (依据 = 条目正文自己写着「等老板, 项目总工转达」) |
| 3 | **真·待答**的 need 留在 `needs_from` ⇒ 逐条写进 `needs_open_ledger` (owner + 一句话问法 + why + evidence + 是否与板那一趟相关) | 不改数, 但★**下轮按 owner 直接派, 不用再逐条读 144 条★** | ✗ 不是删条目 |

★**本单绝不做的三件事**: ① 不改 `state/gate_check.py` / `state/merge.py` / `SW/tools/` 下任何脚本一个字 ② 不改任何 `decision` 字段代老板拍板 ③ 不发任何邮件 / 询价 / 问询 / 采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」)。

---

## §1 · 总账 (关 {n_closed} / 留 {n_keep} / 新答 {n_ans_new})

| 维度 | 数 | 说明 |
|---|---|---|
| ★原 `needs_from`★ | **{n_orig}** | 本单逐条读过, 一条一条看过, **无抽样** |
| ★关 (移出 `needs_from` ⇒ `needs_closed`)★ | **{n_closed}** | 每条带 `action` / `reason` / `evidence` / `evidence_level` / `closed_at` / `closed_by` |
| ★留 (仍在 `needs_from` ⇒ `needs_open_ledger`)★ | **{n_keep}** | 每条带 `owner` / `oneline` (一句话问法) / `why` / `evidence` / `evidence_level` / `board` |
| ★新答 (写进 `answers`)★ | **{n_ans_new}** | 8 条外部依赖自查结案 + 1 条器材挂账改判; `to` 一律写「被问的那个 agent」 |
| ★对账★ | **{n_keep} + {n_closed} = {n_keep + n_closed}** | = {n_orig} ✔ 平 |

### §1.1 · 四类逐条分布

| 桶 (★按**改分片前**的 `(to, waiting_on)` 原始归属★) | 任务书对应类 | 定义 | 原数 | 关 | 留 | 新答 |
|---|---|---|---|---|---|---|
| **①** | ① 内部等另一个总工 | `to=hw-lead` 17 + `to=mech-lead` 2 + `to=main` 且 `waiting_on=agent` 4 | **{b1}** | {b1c} | {b1k} | {b1a} |
| **②** | ② `waiting_on = boss` | 不代拍 ⇒ 整理成 need key + 决策码一页 | **{b2}** | {b2c} | {b2k} | 0 |
| **③** | ③ 外部依赖 | ★按老板政策自查 + 标证据等级 + 写降级方案★ | **{b3}** | {b3c} | {b3k} | {b3a} |
| **④** | ④ `waiting_on` 空 | `to=main` 且 `waiting_on` 空 ⇒ 三选一 (a) 已作废 / (b) 已被覆盖 / (c) 真·待答 | **{b4}** | {b4c} | {b4k} | {b4a} |
| **⑤** | (任务书未单列) | `to=main` 且 `waiting_on=sw-lead` ⇒ ★等的是我自己 ⇒ 我自己答★ | **{b5}** | {b5c} | {b5k} | {b5a} |
| **合计** | | | **144** | **{n_closed}** | **{n_keep}** | **{n_ans_new}** |

★**与任务书 §2 的口径对照 (两边都对, 只是归类边不同)★**: 任务书把「① 内部等另一个总工」写成 **23 条** (`to=hw-lead` 17 + `to=mech-lead` 2 + `to=main`&`agent` 4), 把「④ `waiting_on` 空」写成 **118 条** (= `to=main` 空 99 + `to=hw-lead` 17 + `to=mech-lead` 2) ⇒ ★**那 17 + 2 在任务书里两边都算 (有意重叠 19 条)**★。
★**本单按【不重复计数】的口径拆桶**: ★**① = 23**★ / ★**④ = 99**★ ⇒ **① + ④ = 122 = 任务书的 ① 23 + ④ 118 − 19 重叠** ⇒ ★**去重后 23 + 99 + 12 + 8 + 2 = 144** ✔
★**⇒ 因此: 任务书「④ 类 118 条」= 本单 §5 的 99 条 + §2.2 里的 19 条 (`to=hw-lead` / `to=mech-lead` 那两桶的留档)★ ⇒ ★**两处都列全了, 一条没漏**★。

### §1.2 · `action` 分布 (关的 {n_closed} 条)

| action | 条数 | 含义 |
|---|---|---|
| `close` | {c_act.get('close', 0)} | 已结 / 已作废 / 已被后续交付覆盖 ⇒ 移出 `needs_from`, 留档在 `needs_closed` |
| `close+answer` | {c_act.get('close+answer', 0)} | 同上, 且★**本单把答复写进了自己的 `answers`** (key + to + value + ref) |

### §1.3 · `waiting_on` 字段订正 (6 条: 空/`agent` → `boss`)

★**依据**: 这 6 条的正文自己写着「等老板, 项目总工转达」⇒ 原注册漏了 `waiting_on` 字段 ⇒ 本单**只订正字段, 条目一条不删**。

| need key | 原 `waiting_on` | 新 `waiting_on` | 依据 (条目原文) |
|---|---|---|---|""")

for k, v in WO_BOSS.items():
    A(f"| `{k}` | 空 / agent | `boss` | {v} |")

A(f"""
★**另一条 `to` 改派**: `iss291_sw_vbus_det_d_digital_caliber` ⇒ `to` 由 `main` 改为 `hw-lead` ⇒ 依据 = SW 侧口径已随 ISS-291/ISS-293 落闸闭合, 剩下三个未决 (①USB_DRD1_VBUSDET 有无内部 40kΩ 下拉 ②IO 域/abs-max ③识别裕量 75mV) 是硬件侧 ⇒ **该谁答归谁**。

---

## §2 · ① 类逐条 (内部活 ⇒ 自己推)

★**口径**: 内部活 ⇒ 必须自己推 ⇒ 逐条判【我能答吗】⇒ ★**能答的直接写进自己的 `answers` (带 key + 出处 + 证据等级)**★ / ★**不能答的写清【该谁答 + 为什么 + 一句话问法】**★。

### §2.1 · 我自己能答的 (已写进 `answers`)

| need key | 动作 | 答复要点 | 出处 | 证据等级 |
|---|---|---|---|---|
| `demo_od_p0_1_rk3572_target` | close (早于本单已答) | rknn-toolkit2 2.3.2 的 target_platform **不含** rk3572 (合法值 11 个, 无 rk3572) ⇒ M1 零转换优势归零; ★但主路线已换★ rknn3-toolkit 1.2.0 **含** rk3572 (config rc=0 / 产物 md5 `97a34fff0b855b92681f26627dba5354` 三次一致) | sw.yaml 既有 `answers[demo_od_p0_1_rk3572_target]` (2026-11-11 sw-lead ISS-196 §1/§4) + `SW/RKNN_BENCH.md:378/382` | [实测]/[官网] |
| `demo_od_p0_3_build_env` | close (早于本单已答) | 构建环境已恢复 ⇒ 原 need 的前提被推翻 ⇒ 「构建环境已恢复 ⇒ 本 need 退休, 不要继续当活账挂着」 | sw.yaml 既有 `answers[demo_od_p0_3_build_env]` (2026-11-11 sw-lead ISS-196 §2) + 本单实跑 `IMPORT_OK` | [实测] |
| `fw_s2_test_gear` | close+answer | ★三样器材里 2 样各有零采购等价物, 只剩逻辑分析仪 1 样且只覆盖 P1 亚毫秒 1 格★ ⇒ 「没有它们 P1/P3 只能等原厂」这个挂账形态撤掉 ⇒ 改判为【板到手即跑的命令清单已备好】 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-1/E-2 + §4 + `SW/tools/boot_rescue_probe.py` 真跑枚举出 8 个设备真实 VID:PID | [实测]/[推算] |
| `model_toolchain_q9_addendum` | close | 【已退休】Art.Galaxy 线 (10 问全围绕它) ⇒ 公开渠道全查无 [0数据] + 主控基线已翻 RK3572 ⇒ 即便原厂给了也不该用 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-4 (ISS-270 verified) | [0数据]/[实测]/[官网] |
| `ars45_art_galaxy_sdk` | close | 【已退休】同上 ⇒ 替代已实测可用 (rknn3-toolkit 1.2.0 IMPORT_OK) | 同上 + `airockchip/rknn3-toolkit` README | [0数据]/[实测]/[官网] |
| `model_yolox_weight_download` | close | 【技术前提已消失】zoo CDN 实测可下 (35,891,401 B / 8.62 MB/s / 4 s) ⇒ 不需要任何人代下 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-3 ⑤ | [实测] |

### §2.2 · 我答不了 / 该谁答的 (留档 + 一句话问法)

| need key | 归属 | 一句话问法 | 为什么不是我答 | 依据 | 级别 | 板那一趟 |
|---|---|---|---|---|---|---|
""")

for x in LEDGER:
    if x["cls"] == "①" and x["sub"] == "c":
        A(f"| `{x['key']}` | {_esc(x['owner'])} | {_esc(x['oneline'])} | {_esc(x['why'])} | {_esc(x['evidence'])} | {_esc(x['evidence_level'])} | {x['board']} |")

A(f"""
★**已答但保留在 `needs_from` 的 ① 类** (由对方登记的答复闭合 ⇒ merge 标 `answered` ⇒ ★**删掉反而丢记录**★):

| need key | 答复方 | 出处 |
|---|---|---|
""")

for x in LEDGER:
    if x["cls"] == "①" and x["sub"] == "b":
        A(f"| `{x['key']}` | 见 `answers` 里同 key 的登记 | {x['evidence']} |")

A(f"""
---

## §3 · ② 类逐条 (不代拍 ⇒ need key + 决策码)

★**本单没有在分片里写任何 `decision` 字段, 没有替老板拍任何一条** ⇒ 下面每个决策码**只交「选项 + 代价 + 建议默认值 (只作参考) + 不拍的后果」**, 老板回一个码即可, 不用重读 144 条。

### §3.1 · 决策码表

| 决策码 | need key (★回码请带 key, 不要回裸字母★) | 选项 | 代价 | ★建议默认值 (只作参考·不代拍)★ | 不拍的后果 |
|---|---|---|---|---|---|
| **S-B01** | `fw_q3_scope` | ① 维持「只允许 ADB push」 ② 必须无线 | ① 无 OTA 前提, 回滚按 L1 手工 + S1 watchdog ② 本方案「无 OTA」前提失效, 回滚策略要重做 | **①** (与锁死 #11 不冲突, Type-C 已有) | 模型更新链路一直悬着, S2 救砖方案无法定稿 |
| **S-B02** | `fw_sample_ota` | ① 允许「USB 侧 OTA 代理」(PC 跑 agent 经 ADB 下发脚本) ② 不允许 | ① L1 回滚可半自动 ② 维持纯手工 (低优先, 不卡主线) | **①** (这不是无线, 不违反锁死 #11) | 样机段每次升级都要人肉 ⇒ 拖慢调试档期 |
| **S-B03** | `model_license_agpl_ultralytics` | ① 采购 Ultralytics Enterprise License ② 换 Apache-2.0 栈 | ① 官方无公开价 [0数据]·报价制; 立项预算量级 10^4-10^5 USD [推算]; 一次性授权 US$5k-50k + 年费 US$2k-20k/型号; 周期 4-12 周 [推算]; ★老板已定「不再发信」⇒ 采购只能走既有采购流程, SW 侧不询价★ ② 精度换档 (输入 640→320 或换模型), 商用不受阻 | **②** (技术门槛已清零: 许可 [官网] + 权重 [实测] 可下载 + 官方 NPU 配方 [官网]) | ★**不采购 = 商用受阻** (AGPL §6 要求随硬件分发即提供完整对应源码, 与闭源固件冲突) ⇒ 交付集卡在「许可干净候选为空」 |
| **S-B04** | `model_license_stack_decision` | ① Apache-2.0 栈 (首选 YOLOX-s) ② Ultralytics + 采购 ③ 等原厂「许可由原厂承担」的预编译模型 | ① 需用 rknn3-toolkit 1.2.0 + 官方 zoo 配方转 rk3572 `.rknn` (本机已可做) ② 见 S-B03 ③ ★**已退休·不再是路径***: 三条独立理由 (芯片基线已翻 RK3572 / A733 官方 `.nb` 实测类别映射错 ⇒ 官方资产也不省事 / 老板已定「不再发信」⇒ 这一路的**形式**本身被取消) | **①** | 转换链第 3 段没有承载体, 商用清单出不来 |
| **S-B05** | `s2_product_codename` + `s2_version_block_magic_decision` | ① 保持 ARS45 / magic 保持 `RK35` ② 改名 (请给新代号) + 另给 magic | ① 零改动 ② **只改配置一个字段 + 板端 `/etc/version` 生成模板, 代码零改动**; magic 宽度仍 4 字节 ⇒ §3.2 版本块二进制布局零改动; ★本项目尚无板、无已刷镜像 ⇒ 兼容成本 = 0★ | **①** | 版本串前缀与产品真源脱节; 老板 11-02 定的「目标 = 绘制 PCB 图」之后每块板都要带版本号 |
| **S-B06** | `demo_od_model_route_m1_vs_m2` | ① M1 (直接用 A7S 的 yolov5s@640 INT8, 零转换) ② M2 (yolov5n@640, 新拿 ONNX + 重转 + 精度重评) | ① RK3572 推算模式 A 62.67~64.18ms 超 60ms (但★demo 验收判据里没有 60ms 这一条, 60ms 是整机阶段硬指标★) ② 推算模式 A 52.91ms ✅ 但模式 B age=2 仍 ❌ ⇒ 需新拿 ONNX + 重转 + 精度重评 | **①** + 写死三个换模型触发条件 | demo 段卡在「用哪个模型」上, 出不了画面 |
| **S-B07** | `demo_od_path_a_vs_b` | ① 路径 A (AR0234CS 单线) ② 路径 B (先用现成 BSP 驱动 + 现成 IQ 的 IMX415/OV02B10 跑通链路, 再换 AR0234CS) | ① 驱动移植 5~8 人天 + ISP tuning 自写 5~10 人天 (rkaiq 公开 iqfiles 无 ar0234) ② 省 10~14 人天 ≈ 2~3 周; ★sw-lead 判断: 软件 75% 与 sensor 无关但 sensor 承担 ~70% 阻塞风险★ ⇒ **建议 B + AR0234CS 驱动/tuning 三线并行 (不是二选一)** | **②** | 驱动与 tuning 串行 ⇒ demo 段 1~2 人日滑成整机段 1~2 人周 |
| **S-B08** | `iss191_boss_pick_fix_option` + `iss191_boss_q_envc_unify` + `iss191_boss_r_pg_pull_dnp` | ① Q_AND 整颗改 DNP (sw-lead 推荐) ② Q_ENVC 摘掉或必装 ③ 等 SoM 球位 TBD-01 | ① **不改板、不加 IC、不等原厂**; 已在 RC1 反向用例实测否掉 ② (切不断故障链, 且 Q_ENVC 必装会把 EN_VCORE 拉低换成另一个 P0) ③ 首台板等不起 | **①** (三条同批落表) | ★**按现网表装板, RESET_N 会被永久拉低 ⇒ 首台板起不来** (Q_AND 栅=PG_AND 而 PG 只剩 10k 上拉 ⇒ 栅恒高 ⇒ 漏导通); ISS-191 的落表本体正卡在这里 ⇒ **板只改一次 ⇒ 这一拍不落, 复位 P0 就一直挂着** ★ |
| **S-B09** | `iss234_boss_pick_5q` (5 小问) | Q1 demo 板要不要关机态 / Q2 负载开关选型 ISS-172 / Q3 关机电流账 108µA 口径 / Q4 demo 关机时充电灯 / Q5 长按10s话术 | 每条带推荐默认值但不代拍 ⇒ 见交卷页 §3 决策码表 | 见交卷页 | 关机/待机口径有 3 条已锁死 (§0 L80/L84/L86), 剩下 2 条悬着 ⇒ 售后话术写不实 |
| **S-B10** | `iss250_pick_downgrade_route` | ① rk3576-target 维持现状 ② rknn3-toolkit 1.2.0 独立 conda env ③ 降 OD 负载 / 回 RK3576 换 SoC | ★**技术上路线②已被事实选定*** (ISS-263 实测 config('rk3572') rc=0 / 产物 md5 `97a34fff…` 三次一致 / ISS-355 脚本已迁主路线) ⇒ ★现在只等老板追认签字★; 路线①/③ 涉 60ms 生死与换芯片 = 商务决策; 三条共用同一套 N1~N5 判据 ⇒ 换路线不换判据 | **②** (追认签字) | 路线事实上已定但账面没签 ⇒ 下轮又有人重新讨论一遍 |
| **S-S10** | `iss250_n3_threshold_recheck` | ① 现在就把 N3 / 60ms 降级为观察项 ② 等板端实测后按实测重定线 | ① N3 通过线 t_npu ≤ 13.30ms 的基数是「RK3572 ≈ RK3576 的纯 NPU 13.305ms」[推算], 而 RK3576 官方 6 TOPS [官网] vs RK3572 4 TOPS [媒体] ⇒ 算力差 −33% ⇒ 同产物在 RK3572 上纯 NPU 耗时可能 ×1.5 ⇒ 52.91ms 那条模式 A e2e 也要打折; ② 板端取数口径: **纯 NPU 耗时须 C API `RKNN_QUERY_PERF_DETAIL` 取, 拿不到就判 INDET, 不许拿 SDK 总耗时顶 (N4 铁律)** | **②** (等板端实测) | 一条按既定门槛写死的判据, 实际基数已经偏了 ⇒ 板端一测就红 ⇒ 现场第一反应会去改判据 |

### §3.2 · ② 类已结 (老板早已拍完, 不再重复上报)

| need key | 老板原话 (代录出处) | 落点 |
|---|---|---|
| `q1_latency_scope` | 「选口径 A (曝光开始→出光, 最严口径)。不接受用改口径的方式达标。」 (2026-10-25 19:16) | 落到确定状态 |
| `q17_display_fps` | 「60fps 优先。班子到位之后 60 搞不定转 30。」 (2026-10-25 19:16, 19:26 经软件总工核算修正) | 落到确定状态 |
| `q18_highspeed_cam` | 「光机延迟不外部测设备, 改用目测/感官验收 (看有没有眩晕) → 新实测项 M-DIZZY (主观)。」 (2026-10-25 19:23) | 落到确定状态 |
| `demo_od_p0_4_panel_init_code` | 「不再做任何邮件 / 供应商 / 原厂问询」 (2026-11-11 19:31) + ISS-212 已结 (demo 半 = Waveshare 2.8\" 官方 [官网]) | 落到确定状态; 整机屏路线仍属老板 ⇒ 已拆到 S-B05/S-B07, **不重复上报** |

---

## §4 · ③ 类逐条 (外部依赖 8 条 ⇒ 全部自查结案, 零外发)

★**老板政策 (2026-11-11 19:31 + 2026-11-12 02:02)**: 不再发信, 全靠自己查资料 ⇒ ★**这 8 条一律不许继续等回信 ⇒ 必须【自己网上查】+ 标证据等级 + 查不到就写降级方案**★ ⇒ ★**降级方案是必须项, 不是可选项**★ ⇒ ★**原措辞里「走 main 发第二轮邮件 / 经 main 转达 / 请并进第二轮邮件」这一类外发字样, 本单一并改掉**★。

| # | need key | ★自查结论★ | 自己查了什么 (可复现) | 证据等级 | ★降级方案 (必须项)★ | 原措辞里的外发字样 |
|---|---|---|---|---|---|---|
| ③-1 | `vendor_q8_q9_scope` | Q8 口径已由本域铁律写死 (纯 NPU 耗时须 C API `RKNN_QUERY_PERF_DETAIL` 取, 拿不到判 INDET, 不许拿 SDK 总耗时顶); Q9 追加 4 问全属 Art.Galaxy / 原厂 SDK 口径 ⇒ 随该线退休 | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-3/E-4 (ISS-270 verified); 官方 `airockchip/rknn3-toolkit` README (Supported Platforms 含 RK3572) | [实测·本机文档]/[官网]/[0数据] | ① 权重/配方任一源不通 ⇒ 退化到本机已实测可用的 `ssd_mbv2_fpnlite_320_fp32_head_npu.onnx` (F1@IoU0.5 = 0.4346, 299 张) ② 双源 (fork + zoo CDN) ③ 换栈兜底 PP-YOLOE | ~~走 main 发第二轮邮件, 我不单独对外~~ ⇒ **作废** |
| ③-2 | `fw_vendor_toolchain` | ①下载工具 = 官方 RKDevTool (Win/Linux/macOS) + **开源 rkdeveloptool (GPL-2.0, 可脚本化批量)** ⇒ 「能否脚本化批量」= 是 ②bootloader = U-Boot TPL/SPL + miniloader (打包流程公开) ③无 fastboot ⇒ 等效切槽 = Rockusb Loader/MaskROM + U-Boot bootcount ④官方分区表 = Rockchip `parameter.txt` (rkbin 公开) ⑤烧录+回读文档 = rkdeveloptool README + SDK 文档 | `github.com/rockchip-linux/rkdeveloptool` README (db/wl/rd 逐字命令) · Radxa docs (RKDevTool 三平台) · u-boot `doc/README.rockchip` (miniloader / parameter.txt 打包) | [官网]/[媒体] | ① 工具链任一版不可得 ⇒ 用开源 rkdeveloptool 自编译 ② 分区表拿不到 ⇒ 按 §4.1 推荐 C 分区表 + 显式换算参数固化 (`SW/tools/s2_partition_convert.py --parse`) ③ 脚本化批量不受阻 | ~~经 main 转达, 我不单独对外~~ ⇒ **作废** |
| ③-3 | `fw_usb_boot_phy` | ①**有 USB PHY** (RK3576 官方 Brief Datasheet: USB3.1/Type-C/DP1.4 + USB2.0 OTG/HOST ×2) ⇒ 「若答无 USB PHY 则母座引脚定义要改」的返工风险**不成立** ②fastboot 不提供 ⇒ 等效 = Rockusb ③无 DFU/UF2 ⇒ 用 Rockusb ④★关键订正★: boot 选择脚不是 BOOT GPIO, 是 **SARADC_VIN0_BOOT 电压档位** | rock-chips.com RK3576 Brief Datasheet V1.2-20240311.pdf · Flipper One docs (RK3576 MaskROM 只走专用 MaskROM USB 口, 上电读 SARADC_VIN0_BOOT 电压定启动优先级) | [官网]/[媒体] | 烧录链路按「MaskROM(Rockusb) → Loader(Rockusb) → 正常启动」三态设计, 任一态可用即可救砖; 枚举特征板端 `lsusb -v` 实测回填 (零采购) | ~~经 main 转达~~ ⇒ **作废** |
| ③-4 | `fw_boot_entry_cond` | ①进入条件 = SARADC_VIN0_BOOT 电阻分压档位表 (官方 boot mode 表) + 按键/开关拉地强制 MaskROM ②校验 = Rockchip Secure Boot (HAB: 公钥 hash 存 OTP + RSA2048/SHA-256, 不通过即拒绝启动) ③A/B 自动回滚 = U-Boot bootcount/rollback 可配 ⇒ N=3 阈值可自配 ④secure boot 出厂默认关闭, 密钥管理走 RKTrust/OTP ⇒ 可选开启 | Rockchip Secure Boot Application Note V1.9 §1.4/1.5 · Flipper One docs (RK3576 boot mode 电压档位表) · u-boot bootcount 通用机制 | [官网]/[媒体]/[0数据·同族推断] | ★按「secure boot 关闭 + 板端 sha256 自检脚本」设计, **不依赖原厂** ⇒ 极性/档位未知都不改板 (网表 note: 极性反了只需改 Q_AND 接法) | ~~经 main 转达~~ ⇒ **作废** |
| ③-5 | `model_license_yolov5sim` | ★**ISS-087 本地早已判完, 这条本就不该挂 vendor**★ ⇒ yolov5s-sim 系 = ultralytics/yolov5 v6.0 release 导出物 ⇒ 许可 = **AGPL-3.0** (证据链 7 环) ⇒ 剩余「来源方书面确认」= 商业路径而非技术阻塞, 且**零外发政策已把它排除** ⇒ 唯一合规解 = 走 Apache-2.0 栈 | `SW/MODEL_LICENSE.md` §1.2 证据链 7 环 (第⑥环本机 ultralytics 8.4.80 METADATA `License: AGPL-3.0` + 随包 LICENSE 34,523 B; 第⑦环 `api.github.com/repos/ultralytics/yolov5` ⇒ `license.spdx_id = AGPL-3.0`); 一条命令 `python3 SW/tools/license_probe.py` 可复现 | [实测]/[官方] | ① 权重源不通 ⇒ 退化到本机已实测可用的 `ssd_mbv2_fpnlite_320_fp32_head_npu.onnx` ⇒ **商用不受阻** ② 双源 ③ 换 PP-YOLOE; ★两个重建件 (sha16 `1e2c716bd16ed9d3` / `dfb5d060ca36fc27`) 仍 licensing-hold 禁入 AGPL 交付集, 按换栈处置* | ~~经 main 转达, 我不单独对外~~ ⇒ **作废** |
| ③-6 | `sw_reset_timing_spec` | ①②③ (RESET 释放要求 / 内部上电顺序 / 是否提供 PG) **全在 SoM 内部** (主板不产 SoC 核心轨: 网表 L79 `U_DCDC_VCORE` / L86 `U_DCDC_VIO` 均 `dnp=DNP`) ⇒ 板级不可控 [0数据]; ★但已有兜底★ 网表 note「画法按最通用的『开漏 + 上拉』, 极性反了只需改 Q_AND 接法」⇒ 极性未知**不改板** ④片上温度 = 有 (SoC 内 tsadc + 板载 TMP117 I2C 0x48) ⑤BOOT 有效电平 = SARADC 档位 ⑥RESET/BOOT 电源域 = SoM 侧, 主板只挂焊盘位 | 网表 L79/L86 (dnp=DNP) + L75/L407/L408/L409 (U_SUPV DNP, note = Forlinx 官方载板复位电路 = 按键+100nF+ESD) · TI SNOSD82D TMP117 · `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-5 | [0数据·板级不可控]/[实测·网表]/[官方] | ① SoM 内部时序按「只有 SW_RST 能拉低」设计 ② PG 极性查不到 ⇒ 按开漏+上拉画, 极性反了改接法 ③ 温度改读板载 TMP117, 不等 SoC 内部 tsadc | ~~请项目总工并进第二轮邮件, 我不外发~~ ⇒ **作废** |
| ③-7 | `sw_usb_phy_spec` | ①USB 设备控制器 = USB2.0 OTG (FS 12Mbit/s) + USB3.1 Gen1 (SS 5Gbps) ⇒ ★工程口径★: 本项目**只按 FS 设计** (Type-C 只引 D+/D−/VBUS/GND; ADB + CDC-ACM 足够) ⇒ **原理图零返工** ②★原文结论要改★: 「SoC 侧无任何 VBUS 线 ⇒ 枚举前提缺失」**不成立** —— RK3572 有 `USB_DRD1_VBUSDET` 数字检测脚 (网表 L439 ⇒ `J_SOM_P1` pin100), 主板已按数字检测输入口径分压 (L434/435/436 1M+1M + L438 100nF) ⇒ 枚举前提 = VBUS_DET 数字脚 + VBUS 5V 供电子路 ③BOOT 态 VID:PID = Rockusb 2207 | rock-chips.com RK3576 Brief Datasheet V1.2 · 网表 L434/435/436/438/439 · `SW/SW_TIMING_REVIEW.md` §14 ADC 现值卡 | [官网]/[实测·网表]/[媒体] | ① 速率判不准 ⇒ 只按 FS 设计 (结论不变) ② VID:PID 板端实测 (零采购, 已有 `SW/tools/boot_rescue_probe.py`) ③ 识别裕量只剩 75mV ⇒ 按方案 A 换料 22k+1M (节点 3.18V) 或列 EVT 必测项 | ~~请项目总工并进第二轮邮件~~ ⇒ **作废** |
| ③-8 | `sw_aon_deepsleep_spec` | ①AON 域/常开唤醒脚: RK3576 官方 datasheet 有 Cortex-M0 MCU ×1 + TrustZone, 而 RK3572 是降本版, Forlinx 官方页未列独立 MCU ⇒ RK3572 具体脚号 [0数据] ⇒ ★降级★「关机态长按按键唤醒」**不写进必达路径**, 关机走 U_PWR_SW 真断电, 关机充电灯由充电板本地硬件承担 ②深睡态 DDR 是否保留: SW 侧**已按不可保留设计** (`SW_REQUIREMENTS.md` M7-R10: 进 standby 前落盘 + fsync) ⇒ 不阻塞实现 ③低功耗态 rail 能否真断: rail 全在 SoM 内部 PMIC ⇒ 主板无断电通路 | rock-chips.com RK3576 Brief Datasheet V1.2 (MCU ×1 / TrustZone) · forlinx.net FET3572-C 官方参数页 · `SW/SW_REQUIREMENTS.md` M7-R10 · `PROJECT_TRACKER.md` §0 L80/L84/L86 | [0数据·RK3572 AON 脚号]/[官网]/[实测·本机文档] | ① AON 永远查不到 ⇒ 用户话术**不承诺**「关机后按键唤醒」 ② DDR 不可保留 ⇒ 进 standby 前强制落盘 + fsync (已实现) ③ rail 不可断 ⇒ 「关机」定义为负载开关切 SYS 真断电, 不承诺 SoC 域断电 | ~~经项目总工并进第二轮邮件~~ ⇒ **作废** |

★**本类 8 条 ⇒ `needs_from` 里 `waiting_on=vendor` 的条数 = 0** ⇒ ★**「8 条外发依赖挂着」这笔老账清零**★。
★**本单零外发**: 不发邮件 / 不询价 / 不问询 / 不采购 / 不联系任何厂商; `state/outbox/` 里的草稿 (`s2_rk3576_module_vendor_query.md` 等) ★**一律不发, 只作资料留档**★ ⇒ **没有「批一句可以发」这个选项**。

---

## §5 · ④ 类逐条 (waiting_on 空 ⇒ 三选一)

### §5.1 · (a) 已作废 ({c_cls.get('④', 0) and sum(1 for x in CLOSED if x['cls']=='④' and x['act']=='a')} 条) —— 被哪个 ISS / 哪份文档改写, 必须引证

| need key | 依据 |
|---|---|
""")

for x in CLOSED:
    if x["cls"] == "④" and x["act"] == "a":
        A(f"| `{x['key']}` | {_esc(x['reason'])} |")

A(f"""
### §5.2 · (b) 已被后续交付覆盖 —— 指到具体 answers key / ISS

★**两部分**: ① **已关闭的** (从 `needs_from` 移出, 进 `needs_closed`) ② **已答但仍留在 `needs_from` 的** (由对方登记的答复闭合 ⇒ merge 标 `answered` ⇒ ★**删掉反而丢记录**★)★

| need key | 依据 (被谁覆盖) | 去向 |
|---|---|---|
""")

for x in CLOSED:
    if x["cls"] == "④" and x["act"] == "b":
        A(f"| `{x['key']}` | {_esc(x['reason'])} | `needs_closed` |")
for x in LEDGER:
    if x["cls"] == "④" and x["sub"] == "b":
        A(f"| `{x['key']}` | {_esc(x['evidence'])} | 留 `needs_from` (merge 标 answered) |")

A(f"""
### §5.3 · (c) 真·待答 ({sum(1 for x in LEDGER if x['cls']=='④' and x['sub']=='c')} 条) —— 给 owner + 处理方式 + 是否与板那一趟相关

| need key | owner | 一句话问法 | 为什么不是我答 | 依据 | 级别 | 板那一趟 |
|---|---|---|---|---|---|---|
""")

for x in LEDGER:
    if x["cls"] == "④" and x["sub"] == "c":
        A(f"| `{x['key']}` | {_esc(x['owner'])} | {_esc(x['oneline'])} | {_esc(x['why'])} | {_esc(x['evidence'])} | {_esc(x['evidence_level'])} | {x['board']} |")

A(f"""
---

## §6 · 对账表 (关 {n_closed} / 留 {n_keep} / 新答 {n_ans_new})

| 项 | 数 | 对账依据 |
|---|---|---|
| 原 `needs_from` | {n_orig} | `state/fragments/sw.yaml` 改前 md5 `e6ef9324c83efcefd9337fcd432ec5b8` (副本 `logs/iss357/sw.yaml.bak_pre_iss357`) |
| 关 (→ `needs_closed`) | {n_closed} | 每条一行依据 (本页 §5.1/§5.2 + §4 + §3.2) ⇒ **无一条依据为空, 无批量清空, 无把 118 条批量标同一个结论** |
| 留 (仍在 `needs_from` ⇒ `needs_open_ledger`) | {n_keep} | 每条带 owner + 一句话问法 + why + evidence + 级别 + board |
| ★平账★ | **{n_keep} + {n_closed} = {n_keep + n_closed} = {n_orig}** | ✔ 由 `logs/iss357/apply_iss357.py` 落盘后自检断言 (`assert tot == 144`) |
| 新答 (写进 `answers`) | {n_ans_new} | `answers` 49 → 58; ★新写 key 与既有 49 条 key 零相撞 (落盘前自检断言)★ |
| `waiting_on` 字段订正 (空/`agent` → `boss`) | 6 | 条目一条不删, 只订正「等谁」 |
| `to` 改派 (main → hw-lead) | 1 | `iss291_sw_vbus_det_d_digital_caliber` (SW 侧已闭合, 剩三个硬件问) |

---

## §7 · 与板那一趟相关的 SW 侧待答输入清单 (★给「板只改一次」那一趟★)

★**口径**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ ★**板只改一次** ⇒ ★**凡与「板框 / 板厚 / 层数 / 镜腿宽度 / 检修口净空 / 重量预算 / 位号改名 / 布线 45→0 / Gerber 投产包重出 / Q3 存储分档」有关的待答条目, 都要标出来**★。
★**本单 `needs_open_ledger` 的 `board` 字段已逐条标好: `Y` = 与板那一趟相关, `N` = 无关 (纯软件 / 纯流程)** ⇒ **board=Y 共 {len(board_yes)} 条 / board=N 共 {len(board_no)} 条**。

### §7.1 · board = Y 的 {len(board_yes)} 条 (★按 owner 分组★)

| owner | 条数 | need key |
|---|---|---|
""")

from collections import defaultdict as _dd
_g = _dd(list)
for x in board_yes:
    _g[x["owner"]].append(x["key"])
for owner, ks in sorted(_g.items(), key=lambda kv: -len(kv[1])):
    A(f"| {_esc(owner)} | {len(ks)} | " + " · ".join(f"`{k}`" for k in ks) + " |")

A(f"""
### §7.2 · board = Y 里★最要紧的 6 条★ (板那一趟开工前必须有答案)

| # | need key | 为什么卡板那一趟 | 不答的后果 |
|---|---|---|---|
| 1 | `iss191_boss_pick_fix_option` (+ `iss191_boss_q_envc_unify` + `iss191_boss_r_pg_pull_dnp`) | 复位 P0 三选一 (S-B08) ⇒ ISS-191 的**落表本体**正卡在这 ⇒ 落表要改板 md5 ⇒ 必须与位号改名合并成一次整链重出 | ★按现网表装板 RESET_N 恒低 ⇒ **首台板起不来**; 且板 md5 会变第二次 ⇒ 违反「板只改一次」 |
| 2 | `iss241_f1_f2_land_redraw_needed` | 3 处 pad 序缺陷 (D_ESD_CAM 器件脚接错 / Q_AND pad 序 D/S/G vs AO3400A 引脚序 G/S/D ⇒ 硬件 AND 变 OR / 5 件按键 land 外扩超 bbox) | ESD 不工作 + 硬件 AND 变 OR ⇒ **下一轮才炸, 且炸在装配后**; 5 个键 land 要一次画齐 |
| 3 | `iss190_netlist_usb_dminus_no_esd` | D− 侧无 ESD (D_ESD_USB_D 只跨 D+ 与地) ⇒ Type-C 是现网表上**唯一的刷写口** ⇒ 变砖 = 只能拆机 JTAG | 一次 ESD 打到 D− ⇒ **变砖只能拆机**; 与老板 G1a 的 W-2 那一格同批 |
| 4 | `iss190_netlist_supv_divider_0R_short` | U_SUPV 三行全 DNP 但 R_SUPV_DIV1/DIV2 仍必装 ⇒ 按 BOM 装 0Ω = V_SOC_IO 短路 | 进限流 ⇒ IO 域塌陷 ⇒ **整机不启动 + 器件发热** (装配级灾难) |
| 5 | `iss321_decide_rename_batch_scope` (+ `iss321_sw_docs_rename_bulk_24files` + `iss321_decide_r6_selftest_fixture_after_reboard` + `iss321_decide_rename_doc_notation`) | S1 位号改名那 7 件批不批 (S1 同批) ⇒ 不做第 2 件 (timing_check 位号解析层) 三道闸当天就红 | 那一趟门禁链 day-1 就红 ⇒ **板只改一次变成板改两次**; 板出之后 `check_sw_ref_reachability.py` 判 58 条改名漂移 |
| 6 | `iss263_board_acceptance_rk3572` + `iss250_rknn3_board_toolchain` | 板端接受性 [0数据] (0 台设备) ⇒ 板到手即跑的两条命令清单已备好 | 板回来还要重新摸一遍工具链 ⇒ 调试档期白等 |

### §7.3 · ★SW 侧已经定了、可直接用的值 (不用重复讨论)★

| 项 | 现行值 | 出处 |
|---|---|---|
| RK3572 转换 target | `rknn3-toolkit 1.2.0` + `target_platform='rk3572'` (config rc=0 / 产物 md5 `97a34fff0b855b92681f26627dba5354` 三次一致) | `SW/RKNN_BENCH.md:378` |
| 转换脚本入口 | `SW/tools/rk3572_model_rebuild.sh` (v2.0 默认路线已迁 rknn3 + rk3572) | `SW/RKNN_BENCH.md:382` |
| 板端接受性 | **[0数据]** (0 台设备) ⇒ 板到手一条命令出 PASS/FAIL: `SW/tools/rk3572_rknn3_board_smoke.sh` | `SW/RKNN_BENCH.md:384` |
| 启动存储分档 (Q3) | SPI-NOR ⇒ **J_BOOT1 焊盘位已在板** ⇒ 板侧零动作, **不重出板**; eMMC ⇒ 153-ball TFBGA 11.5×13.0mm ⇒ 板宽 12→15mm ⇒ 产品板档须在板那一趟开工前进网表 | `state/issue_log.yaml` ISS-346 / ISS-350 (verified) + 网表 L202/204/206/208 |
| 硬保护 / 留痕 / 反向用例闸链 | 10 道钉板 md5 闸全绿 + EXTRA_GATES 已挂 5 道 SW 侧闸 (ISS-318 位号引用 / ISS-315 落表留痕 / ISS-315 硬保护反向 / ISS-312 链头交叉 / ISS-309 R6 反向) | `state/gate_check.py` EXTRA_GATES (本单实读) |
| 板 md5 (钉板真值) | `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` | 本单交卷前后逐字节相同 |

★**SW 域已交的现成件, 本单不重做 (只读不写)★: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (7 件同批清单) · `SW/ONETRIP_SW_RENAME_SAFETY.md` (闸脚本安全性) · `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (改名后闸链复活 SOP) · `SW/MODEL_LICENSE.md` (许可证据链) ⇒ ★**本单只交「还没答的条目」**★。

---

## §8 · 证据分级 (本单全部结论的级别汇总)

★**标签对照**: 本单用 `[官网]` 表示机检证据标签集里的 **官方** (同一档, 结构域习惯叫「官网」); `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 四档齐。

| 结论 / 数 | 级别 | 来源 |
|---|---|---|
| 机检缺口 sw-lead **98 → 33** / 全局等外部 **50 → 46** / 全局等总工 **356 → 295** | [实测] | `state/gate_check.py` 两次实跑 (`logs/iss357/gate_check_BEFORE.txt` / `gate_check_AFTER.txt`) |
| merge rc=0 · gate rc=0 · Q1 18/18 · 自闭合 0 条 | [实测] | `logs/iss357/merge_AFTER.txt` / `gate_check_AFTER.txt` |
| 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` | [实测] | `md5sum` + `stat`, 交卷前后逐字节相同 |
| 144 条逐条分类, 平账 70 + 74 = 144 | [实测] | `logs/iss357/apply_iss357.py` 落盘后自检 (`assert tot == 144`) |
| 373Mbps / 246Mbps 旧 DSI payload 数字全仓零命中 | [实测] | 本单 08:5x 实跑 `grep -rn '373Mbps\\|373 Mbps\\|246Mbps\\|246 Mbps' HW/ SW/ state/outbox/` |
| `U_EN_SW` 网表 L442 已有 IC 行 (grep count = 1) | [实测] | 本单实跑 `grep -n 'U_EN_SW' HW/netlist_v1.csv \\| grep -c ',IC,'` |
| I2C_A 上拉 note 已改 (2.2k/1.8V/0.64mA/186ns) | [实测] | 本单实读网表 L167/L168 |
| BAT_DET 链已补装 (100k+60k+100nF 必装) | [实测] | 本单实读网表 L181~L186 |
| `Q_AND` 仍必装 (L65/66/67) ⇒ RESET_N 恒低风险**仍在** | [实测] | 本单实读网表 |
| `Q_ENVC` 仍 L71=DNP / L72·L73=必装 ⇒ dnp 自相矛盾**仍在** | [实测] | 本单实读网表 |
| `U_SUPV` 三行 DNP 而 `R_SUPV_DIV1/DIV2` 仍必装 ⇒ 短路风险**仍在** | [实测] | 本单实读网表 L404/405 + L407/408/409 |
| `D_ESD_USB_D` 仍只跨 D+ 与地 ⇒ D− 无 ESD **仍在** | [实测] | 本单实读网表 L417/L418/L420/L421 |
| VBUS_DET 仍 1M+1M+100nF ⇒ 节点 0.185V ≪ 2.3V 阈值 | [实测] | 本单实读网表 L434/435/436/438/439 |
| `check_demo_panel_spec_r6_selftest.py` rc=0 (红已消) | [实测] | 本单 08:5x 实跑 (TMPDIR 指项目内) |
| 5 道 SW 侧闸已挂 EXTRA_GATES | [实测] | 本单实读 `state/gate_check.py` EXTRA_GATES |
| `sw.yaml` 改前 md5 `e6ef9324c83efcefd9337fcd432ec5b8` / 改后见交卷单 §B6 | [实测] | `md5sum` + `logs/iss357/sw.yaml.bak_pre_iss357` |
| `SW/MODEL_LICENSE.md` md5 `7641e5d0b0967cf3b1b03f9af9f1a27e` 前后不变 | [实测] | `md5sum` |
| `state/gate_check.py` md5 `5f370bb8cf828473e70ccc5d6412da98` / `state/merge.py` md5 `c9191025020fefd9b475e2573a335815` 前后不变 | [实测] | `md5sum` |
| Rockchip 官方工具链 (RKDevTool Win/Linux/macOS + 开源 rkdeveloptool 可脚本化批量) | [官网] | `github.com/rockchip-linux/rkdeveloptool` README + Radxa docs + u-boot `doc/README.rockchip` |
| RK3576 USB3.1/Type-C + USB2.0 OTG/HOST ×2 · Security(TrustZone / Secure boot / Key ladder / RSA4096·AES256·SHA512) · MCU Cortex-M0 ×1 | [官网] | rock-chips.com `RK3576 Brief Datasheet V1.2-20240311.pdf` |
| RK3576 boot 优先级 = SARADC_VIN0_BOOT 电压档位 + MaskROM 只走专用 MaskROM USB 口 | [官网] | Flipper One docs (引 RK3576) + Rockchip Secure Boot Application Note V1.9 §1.4/1.5 |
| Rockchip Secure Boot 校验链 = OTP 公钥 hash + RSA2048 + SHA-256, 不通过拒绝启动 | [官网] | Rockchip Secure Boot Application Note V1.9 §1.4/1.5 |
| U-Boot bootcount / rollback 可配 (A/B 自动回滚 N=3 可自配) | [官网] | u-boot 通用机制 + `doc/README.rockchip` |
| Rockusb VID 2207 (MaskROM / Loader 枚举特征) | [媒体] | Rockchip 生态公开资料 + 板端 `lsusb` 实测路径 |
| RK3572 = 4 TOPS (Forlinx FET3572-C / OK3572-C 官方页) | [媒体] | forlinx.net 官方参数页 |
| `yolov5s-sim` = ultralytics/yolov5 v6.0 导出物 ⇒ AGPL-3.0 (证据链 7 环, `license_probe.py` 可复现) | [实测] + [官方] | `SW/MODEL_LICENSE.md` §1.2 (第⑥环本机 ultralytics 8.4.80 METADATA / 第⑦环 GitHub API) |
| YOLOX-s Apache-2.0 许可 + 权重本机可下载 (35,891,401 B / sha256 `a39c8476…`) + 官方 NPU 配方 `examples/yolox` | [官网] + [实测] | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` §1 E-3 |
| RK3572 AON 域 / 常开唤醒脚具体脚号 | [0数据] | 公开渠道查不到 + Forlinx 官方页未列独立 MCU ⇒ **已写降级方案 (§4 ③-8)** |
| SoM 内部 RESET 释放时序 / PG 极性 / 内部复位电路构成 | [0数据·板级不可控] | 属 SoM 内部, 主板不产核心轨 ⇒ **已写降级方案 (改接法不改板)** |
| RK3572 纯 NPU 13.305ms ⇒ RK3572 上的同产物耗时 | [推算] | ISS-250 查证表 (基数来自 RK3576 同族实测 + 4/6 TOPS 算力差) |
| Ultralytics Enterprise 报价与周期 (US$5k-50k / 4-12 周 / 量级 10^4-10^5 USD) | [推算] + [0数据] | `SW/MODEL_LICENSE.md` §3 (官方无公开价 [0数据], 报价制 [官方·定性]) |

---

## §9 · 本单留下的待办 (都不阻塞板那一趟)

| # | 待办 | 谁 | 为什么不是阻塞 |
|---|---|---|---|
| T-1 | 老板回 12 个决策码 (§3.1) | boss | ★技术事实全部坐实, 只差签字★; 每条都给了建议默认值与不拍的后果 |
| T-2 | `needs_open_ledger` 里 owner=hw-lead 的 6 条 (落表批次 + 选型) | hw-lead | 都要与板那一趟同批落表 ⇒ 不单独排 |
| T-3 | `needs_open_ledger` 里 owner=main 的 12 条 (PM 域派单 / 口径裁决 / 排期) | main | 都是流程与口径, 不卡软件实现 |
| T-4 | `needs_open_ledger` 里 owner=sw-lead 的 3 条 (板到手即跑 / 板可达后补脚本) | sw-lead | ★板不可达 ⇒ 不是外部依赖★, 板到手即跑 |
| T-5 | 板端接受性 N1~N5 全部 [0数据] (0 台设备) | sw-lead + main | 同上 |
| T-6 | 两个重建件 (sha16 `1e2c716bd16ed9d3` / `dfb5d060ca36fc27`) 仍 licensing-hold | sw-lead | 按换栈 (S-B03/S-B04) 处置; 禁入 AGPL 交付集 |

---

## §10 · 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss357_tmp          # ★/tmp 带 usrquota 且配额已满 ⇒ 临时目录指大盘★
python3 logs/iss357/apply_iss357.py         # ★重跑会重放本单处置 (幂等: 4 个断言全过 + 平账 144)★
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/MODEL_LICENSE.md state/fragments/sw.yaml
```
""")

_txt = "\n".join(TRIAGE)
# ★表格规范化: 表头分隔行后面不许有空行 (否则 markdown 表格会断)
_out = []
for _l in _txt.split("\n"):
    if _l.strip() == "" and _out and _out[-1].rstrip().endswith("|"):
        continue
    _out.append(_l)
_txt = "\n".join(_out)
with open(os.path.join(PROJ, "SW", "SW_NEEDS_TRIAGE.md"), "w", encoding="utf-8") as f:
    f.write(_txt)
print("[iss357] 已写 SW/SW_NEEDS_TRIAGE.md")
