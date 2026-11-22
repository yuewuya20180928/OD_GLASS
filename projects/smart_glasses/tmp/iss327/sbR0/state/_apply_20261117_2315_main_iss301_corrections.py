#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 23:1x · job 775d9893「ARS45 继续执行后继计划」
★(1) 独立复验 ISS-301 ⇒ 落 verified (★它抓出 main 自产 TI 电源事实卡的一条 P0 级错误推导★)★
★(2) 按 ISS-301 的订正 A/B/C 给 `HW/TI_POWER_FACTS.md` + `HW/POWER_SHUTDOWN_V3.md` 加【追加式】订正节 (★老字一字不删★)★
★(3) 开 ISS-302 (hw-lead): 落表 C_SYS/SYS_CHG 必装 + note 追加式 + BOM 加 20µF (★ISS-095 落 verified 的同批动作★)★
★(4) ISS-102 fixed → verified (★owner=main · verify_by=hw-lead = ISS-301 的复核·★C3 满足★)★
★(5) ISS-095 fixed → verified (★同批挂 ISS-302 那 4 条落表动作·★交卷单原文「落 verified 时必须同批挂」★)★
★**纪律: 多行标量走【收集整个标量跨度 → 单行 json 写回 → 全量 safe_load 复核 + 其余 issue 逐字相同比对】★★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
PM = os.path.join(HERE, "fragments", "pm.yaml")
FACTS = os.path.join(PROJ, "HW", "TI_POWER_FACTS.md")
SHUT = os.path.join(PROJ, "HW", "POWER_SHUTDOWN_V3.md")
BRIEF_PATH_302 = os.path.join(HERE, "dispatch_briefs", "ISS-302_hw_c_sys_landing.md")
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


FACTS_ADD = """

---

## ★★订正 · ★★ISS-301 (hw-lead) 复核 ⇒ main 自产本卡的三条派生结论有错 (2026-11-17 23:1x · 追加式 · ★上面每一行老字一字未删★)★★

> ★**★这是 main 自己的卡, 由 hw-lead 独立复核抓出来的 ⇒ ★**「验证分离」救回一次 P0** ★ ⇒ ★**下面三条订正逐条点名上面哪一句过期, 引用本卡时以订正节为准** ★

### ★订正 A (★P0 级·必改★) · 本卡 §③ 末句「⇒ VBUS_DET 分压整条可以删 (★省 50 µA + 2 颗电阻★)」★

★**↑ 这一句对本板不成立, 照做 = 5 V 灌 3.3 V 域 SoC 球 = P0 过压** ★
⇒ ★**本板实况**: ★**`5 V → 1M + 1M 分压 → SoM 的 `USB_DRD1_VBUSDET` (P1_100)** ★ ⇒ ★**分压【不可删】** ★
⇒ ★**正确的口径**: ★**dedicated 脚的价值 = 省掉【跨铰链那根线】+ 省掉【分压链的静态功耗假设】, 但本板的分压本身必须保留** ★
⇒ ★**板侧影响**: ★**`R_VBUS_DET_D1` / `R_VBUS_DET_D2` / `C_DET_VBUS_D` 三件【留, 不动】⇒ 「板只改一次」不受影响** ★ (★依据: SoM `P1_100` = B28 = `USB_DRD1_VBUSDET` 已在 Forlinx 官网手册 §2.6.2 Table 2 逐字坐实, hw-lead 独立重跑 399 行全量逐格比对★)

### ★订正 B (★落表前必改·关系「板只改一次」★) · 本卡 §② 末句「⇒ 复位链画法可按『PG 高 = 就绪』写」★

★**↑ 官网支持这句话, 但本项目网表 L62 / L65 / L67 / L71 的 note 写的全是反的** (★「两路 PG 都好时为低」/「PG 有效 (低)」/「任一路不 ok · 本网被上拉拉高」★)
⇒ ★**这四条 note 必须在 S6 那一趟之前定死** ⇒ ★**建议口径 = 按 `RESET_P0_FIX_*` 那条既定方案写 (★ISS-191 已裁过的复位链方案★), 且两条 PG 的【器件名 + 脚名 + 极性】必须同时写清 (★BQ25896 的 /PG 低有效 vs TPS62130A 的 PG 高有效, 两个器件两个脚, 不许混★)** ★

### ★订正 C (★算术·同批改★) · 本卡 §④ 末句「⇒ 降级方案: 关机续航继续用 ISS-097 §0 第 6 条的 ~108 µA / 0.40 mW, 其中 AON 项按 0」★

★**↑ 算术不自洽**: ★**108 µA 本身含 50 µA 的 AON 项 ⇒ 「AON 按 0」⇒ 应为 ~58 µA / ~0.21 mW (≈8.4 个月)** ★
⇒ ★**且订正 A 已定: 分压那 50 µA 在本板不会省掉 ⇒ 「省掉 50 µA」这条路不存在** ★
⇒ ★**⇒ 关机静态电流口径改为: AON 按 0 (RK3572 无 datasheet 级 AON 域 · 〔0数据〕· 实测全文检索无 "AON" 字样) + VBUS_DET 分压 50 µA + BQ25896 ~2 µA + BQ2970 ~1 µA + 负载开关 IQ ≤5 µA ⇒ ~58 µA / ~0.21 mW** ★ ⇒ ★**`HW/POWER_SHUTDOWN_V3.md` 已同批加追加式订正** ★

### ★★这条订正的出处与证据等级 ★★
- ★**交卷单**: `HANDOFF/2026-11-17_hw-lead_ISS301_TI电源事实卡复核.md` §B5-② (★4 问逐条回答 + 三条订正·★50,179 B★) ★
- ★**证据**: ① TI 官网原件 (`bq25896.pdf` md5 `5f2c3958901c8841c7b698b71a16b927` · ★与仓内离线件 `cmp` rc=0 逐字节一致★) ② TPS62130A RevF 官网 txt (★`High = VOUT ready` / `pulls the PG pin Low` / `VOL_PG` 逐字命中★) ③ Forlinx 官网手册 `OK3572C` §2.6.2 Table 2 (★`VBUSDET` 两颗都引出: `P1_100` / `P3_16`★) ⇒ ★**证据等级 [官网] + [实测]** ★
- ★**★本卡的【事实层】四条断言全部成立 (① 成立 / ② 成立 / ③ 成立但派生结论错 / ④ 成立但降级方案算术不自洽) ⇒ 事实层可落 verified, 派生结论按上面三条订正执行** ★
"""

SHUT_ADD = """

---

## ★★订正 · ★★ISS-301 (hw-lead) 复核 ⇒ 关机静态电流的算术与口径 (2026-11-17 23:1x · 追加式 · ★上面每一行老字一字未删★)★★

★**★上面第 6 条与第 140 行的「~108 µA / 0.40 mW」= 「AON ~50µA + BQ25896 ~2µA + BQ2970 ~1µA + 开关 IQ ≤5µA + VBUS_DET 分压 50µA」★ ⇒ ★**算术不自洽: 108 µA 本身含那 50 µA 的 AON 项** ★
⇒ ★**正确口径 (★RK3572 无 datasheet 级 AON 域 · 〔0数据〕· 实测全文检索无 "AON" 字样 ⇒ AON 项按 0★)**: ★**AON 0 + BQ25896 ~2µA + BQ2970 ~1µA + 负载开关 IQ ≤5µA + VBUS_DET 分压 50µA ⇒ ~58 µA / ~0.21 mW (≈8.4 个月)** ★
⇒ ★**★同时: ISS-301 订正 A 已定「VBUS_DET 分压【不可删】」(★本板是 `5 V → 1M+1M 分压 → SoM 的 USB_DRD1_VBUSDET (P1_100)` ⇒ 删了 = 5 V 灌 3.3 V 域 SoC 球 = P0 过压★) ⇒ 「省掉 50 µA」这条路不存在** ★
⇒ ★**★另 (★ISS-301 订正 B★)**: 网表 L62 / L65 / L67 / L71 的四条 PG note 与 TPS62130A 的「PG 高 = 就绪」完全相反 ⇒ ★**这四条 note 必须在 S6 那一趟之前定死 (★ISS-302 的落表批次同批处理或明确排进 S6 前置★)** ★
⇒ ★**★本页的「关机」拓扑 (真断电 / 负载开关) 本身不变 ⇒ 老板锁死的「关机(断电) <0.05W」仍成立 (0.21 mW < 0.05 W)★ ⇒ ★**只有【静态电流的数与月数】按上面订正** ★**
"""

BRIEF_TEXT_302 = """★**ISS-302 · hw-lead 任务书 —— ★★【落表: `C_SYS` / `SYS_CHG` 必装 + note 追加式订正 + BOM 加 20 µF (ISS-095 的同批动作)】★★** ★ (main · 2026-11-17 23:1x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 23:1x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-302 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 落表链侧 · ★★零写板 (★CHG_BOARD 没有 PCB 文件★) · 零改既有判据阈值★★** ★

---

## ① 为什么要这一单 (★依据 = ISS-301 交卷单 §B5-①, ★main 2026-11-17 23:1x 实读网表确认现状★)

★**TI 官网逐字 (bq25896 datasheet SLUSC76C §7)**: ★**"Connect a 20uF closely to the SYS pin."** ★ ⇒ ★**`SYS_CHG` / `C_SYS` 必须必装 + 必须挂 20 µF 到地 (★紧靠 SYS 脚, 充电板本地, **不跨铰链引系统轨**★)** ★
⇒ ★**现状 (★main 本机实跑 `grep` 盘上真源★)**: ★**网表 L498 `SYS_CHG` = DNP · L499 `C_SYS` = DNP** ★ ⇒ ★**且两条 note 里还留着已过期的裁决** (★「VSYS 脚不接 (NC)」/「装 20µF 只占 25×10mm 板面」/「DNP 时不占板面」★) ⇒ ★**BOM 里 CHG_BOARD 也没有那颗 20 µF** ★

## ② 要落的四条 (★交卷单原文列的四条, 一条不许少★)

| # | 落点 | 改法 |
|---|---|---|
| 1 | ★**`HW/netlist_v1.csv` L499** `C_SYS` | ★**`dnp`: `DNP` → `必装`** ★ |
| 2 | ★**`HW/netlist_v1.csv` L498** `SYS_CHG` | ★**`dnp`: `DNP` → `必装`** ★ |
| 3 | ★**L498 / L499 的 note** | ★**追加式改写 (★老字一字不许删★)**: ★**删掉已过期的「VSYS 脚不接 (NC)」裁决, 换成「★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★」** ★; ★**把「装 20µF 只占 25×10mm 板面」改成「≈8 mm² (0805/1206)」** ★; ★**把「DNP 时不占板面」删掉** ★ |
| 4 | ★**`HW/BOM_v1.csv`** | ★**CHG_BOARD 加 1 颗 20 µF 6.3 V X7R/X5R** ★ |

★**★走落表链 (★不许手改产物★)**: ★**改真源 (网表生成器 / 规格页) → 重生成 (gen_netlist → gen_kicad_net → gen_netlist_pins → gen_bom → gen_schematic_pages → gen_kicad_sch) → 落表台账 + 锚点 (★走【落表台账为准】新口径, ★不许手改基线 md5★) → 闸复跑** ★
★**★「零板改第二次」依据**: ★**CHG_BOARD 根本没有 PCB 文件, `C_SYS` 封装还没落 ⇒ 装不装都在同一次布局里落** ★

## ③ 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_netlist_selfconsistency.py ; echo "rc=$?"
python3 HW/check_netlist_selfconsistency.py --expect-resolved ; echo "rc=$?"
python3 HW/check_land_row_anchors.py ; echo "rc=$?"
python3 HW/check_onepass_preflight_coverage.py ; echo "rc=$?"
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变 (零写板)★★
```

## ④ 交卷物 (★3 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_hw-lead_ISS302_CSYS落表.md` (★B1~B6★) ★
2. ★**落表台账痕迹 (★单号 + 文件名 + 新旧 md5★) + 锚点重锚记录** ★
3. ★**分片** `state/fragments/hw.yaml` (★走 `state/frag_write.py --agent hw-lead` 原子写 + grep 校验★) ★

## ⑤ 边界

★**零写板** · ★**不许手改产物 (网表/脚表/BOM/原理图 一律重生成)** ★ · ★**不许手改基线 md5 (★走落表台账为准的新口径★)** ★ · ★不许动 MECH/SW 的文件与分片 · ★零外发 · ★**不替老板拍板** ★ · ★**不自签 issue_log** ★

## ⑥ 纪律

★**交卷单第一件事就是 `write` 建骨架** ★ · ★**长任务 `nohup` 后台 + 短轮询** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**分片写完 `grep` 校验自己的 key 在不在** ★
"""


def main() -> int:
    # ---------- (2) 两份文档的追加式订正 ----------
    for path, add, tag in ((FACTS, FACTS_ADD, "订正 · ★★ISS-301"), (SHUT, SHUT_ADD, "订正 · ★★ISS-301")):
        t = open(path, encoding="utf-8").read()
        if tag in t:
            print("⚠ %s 已订正 ⇒ 不重复追加" % os.path.basename(path))
            continue
        shutil.copy2(path, path + ".bak_20261117_2315_main_iss301_corrections")
        open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)
        print("✔ %s 已加追加式订正" % os.path.basename(path))

    # ---------- (3) 任务书 ----------
    open(BRIEF_PATH_302, "w", encoding="utf-8").write(BRIEF_TEXT_302)
    print("✔ 任务书已写: state/dispatch_briefs/ISS-302_hw_c_sys_landing.md")

    # ---------- (5) pm.yaml: P0 教训 + 落表 need ----------
    shutil.copy2(PM, PM + ".bak_20261117_2320_main_iss301")
    d = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    nf = d.setdefault("needs_from", [])
    have = {n.get("key") for n in nf}
    E = {
        "key": "iss301_main_card_p0_catch_20261117",
        "to": "main",
        "item": ("★★【★验证分离救回一次 P0★】★★ ★**main 自产的 `HW/TI_POWER_FACTS.md` 被 hw-lead 的 ISS-301 独立复核抓出三条派生结论错误**: "
                 "① ★**P0 级**: §③「⇒ VBUS_DET 分压整条可以删 (省 50µA + 2 颗电阻)」★ ⇒ ★**对本板不成立** (★本板是 5V → 1M+1M 分压 → SoM 的 USB_DRD1_VBUSDET (P1_100) ⇒ 删了 = 5V 灌 3.3V 域 SoC 球 = 过压★) "
                 "② ★**落表前必改**: §②「⇒ 复位链画法可按『PG 高 = 就绪』写」⇒ ★**官网支持, 但本项目网表 L62/L65/L67/L71 的 note 写的全是反的** ⇒ 这四条 note 必须在 S6 那一趟之前定死 "
                 "③ ★**算术不自洽**: §④「AON 按 0 ⇒ 沿用 ~108µA / 0.40mW」⇒ ★**108µA 本身含 50µA 的 AON** ⇒ 正确 ~58µA / ~0.21mW (≈8.4 个月), 且分压那 50µA 不会省掉** ⇒ "
                 "★**⇒ 两份文档已加追加式订正 (老字一字未删): `HW/TI_POWER_FACTS.md` §订正 A/B/C + `HW/POWER_SHUTDOWN_V3.md` 关机静态电流口径订正★** ⇒ ★**ISS-102 落 verified; ISS-095 的 4 条落表动作 = ISS-302 (已派)** ★"),
        "since": TODAY,
        "decision": ("★**main 2026-11-17 23:1x 裁决: 三条订正全部采纳 (A/B/C) ⇒ 事实层四条断言成立 ⇒ ISS-102 落 verified (★owner=main · verify_by=hw-lead = ISS-301 的复核★) ⇒ "
                     "ISS-095 的 4 条落表动作 (C_SYS/SYS_CHG 必装 + note 追加式 + BOM 加 20µF) 同批挂 ISS-302 (hw-lead) ⇒ ★**CHG_BOARD 无 PCB 文件 ⇒ 不构成「板改第二次」** ★ ⇒ "
                     "★**★教训: 事实层 (官网逐字) 与派生结论 (据此可以做什么) 必须分开复核 ⇒ 派生结论最危险, 最容易带出 P0 级误判** ★"),
        "decided_at": "2026-11-17 23:20",
        "decided_by": "main (项目总工 · ★依据 hw-lead ISS-301 的独立复核★)",
    }
    if E["key"] not in have:
        nf.append(E)
    d["updated_at"] = "2026-11-17 23:20"
    d["updated_by"] = "main"
    open(PM, "w", encoding="utf-8").write(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))

    # ---------- issue_log: 签 ISS-301 / ISS-102 / ISS-095 + 开 ISS-302 ----------
    raw = open(LOG, encoding="utf-8").read()
    before = yaml.safe_load(raw) or {}
    bmap = {it["id"]: it for it in before.get("issues", [])}
    if "ISS-302" in bmap:
        print("❌ ISS-302 已存在")
        return 2
    lines = raw.split("\n")

    def block_range(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    def replace_scalar(iid, key, newval):
        s, e = block_range(iid)
        if s is None:
            print("❌ 找不到", iid)
            return False
        blk = lines[s:e]
        ki = None
        for j, ln in enumerate(blk):
            if ln.strip().startswith(key + ":"):
                ki = j
                break
        if ki is None:
            return False
        k = ki + 1
        while k < len(blk):
            ln = blk[k]
            if ln.startswith("- id: "):
                break
            ind = len(ln) - len(ln.lstrip(" "))
            if ind <= 2 and ":" in ln:
                break
            k += 1
        blk[ki:k] = ["  %s: %s" % (key, q(newval))]
        lines[s:e] = blk
        return True

    def append_key(iid, key, newval):
        s, e = block_range(iid)
        blk = lines[s:e]
        keys = {ln.split(":", 1)[0].strip() for ln in blk if ln.startswith("  ") and ":" in ln and not ln.startswith("    ")}
        if key in keys:
            return False
        while blk and blk[-1].strip() == "":
            blk.pop()
        blk.append("  %s: %s" % (key, q(newval)))
        lines[s:e] = blk
        return True

    VN_301 = ("★**main 2026-11-17 23:1x 独立复验 (★自己实跑, 不采信 agent 自述★)**: "
              "★**① 交卷单在盘**: `HANDOFF/2026-11-17_hw-lead_ISS301_TI电源事实卡复核.md` = **50,179 B** (★mtime 2026-11-17 23:06★) · "
              "★**② 官网证据副本**: `logs/iss301/` (★TI bq25896 SLUSC76C 官方 PDF · TPS62130A RevF txt · Forlinx OK3572C 官网手册快照 + 399 行逐格比对日志★) ★ "
              "★**③ 闸读数 (★现场 rc 原样★)**: `HW/check_netlist_selfconsistency.py --expect-resolved` **rc=1** (★既有 4 条板侧未落表★) · `state/gate_check.py` **rc=0** · `state/issue_check.py` **rc=0** ★ "
              "★**④ 盘面事实核对 (★main 自己 grep 盘上真源★)**: ★**网表 L498 `SYS_CHG` = DNP · L499 `C_SYS` = DNP (⇒ 那 4 条落表动作确实还没落)★** · ★**BOM 里 CHG_BOARD 无 20µF** ★ · "
              "★**⑤ 边界**: 板 md5 `611b869e…` (mtime 2026-11-06 07:07:17) / 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…` ⇒ **零写板 · 零改真源** ★ "
              "★**★★本单的价值 (★main 记一笔★)**: 它抓的是 ★**main 自己写的卡**★ ⇒ ★**订正 A 是 P0 级** (★「VBUS_DET 分压整条可以删」⇒ 本板 5V→1M+1M 分压→SoM 的 USB_DRD1_VBUSDET ⇒ 删了 = 5V 灌 3.3V 域 SoC 球 = 过压★) ⇒ "
              "★**⇒ 「事实层 (官网逐字) 与派生结论 (据此可以做什么) 必须分开复核」: 派生结论最危险, 最容易带出 P0 级误判** ★ ⇒ ★**main 已把三条订正 (A/B/C) 以追加式写进 `HW/TI_POWER_FACTS.md` + `HW/POWER_SHUTDOWN_V3.md` (老字一字未删)** ★ ⇒ 落 verified ★")

    replace_scalar("ISS-301", "status", "verified")
    replace_scalar("ISS-301", "fix_ref", "HANDOFF/2026-11-17_hw-lead_ISS301_TI电源事实卡复核.md (50,179 B · B0~B6) · HW/TI_POWER_FACTS.md (★main 追加式订正 §订正 A/B/C★) · HW/POWER_SHUTDOWN_V3.md (★main 追加式订正: 关机静态电流口径★) · logs/iss301/ (TI 官网 2 件 + Forlinx 手册快照 + 399 行比对)")
    replace_scalar("ISS-301", "verify_result", "pass")
    replace_scalar("ISS-301", "verify_date", TODAY)
    append_key("ISS-301", "verify_note", VN_301)

    VN_102 = ("★**main 2026-11-17 23:1x 落 verified (★owner=main · verify_by=hw-lead ⇒ ★**hw-lead 的 ISS-301 交卷单 = 本条的独立复核** ★ ⇒ C3 满足★)**: "
              "★**① 四个问题的事实层全部有答案** (★ISS-301 逐条复核成立★): ① AON 问法作废 + RK3572 datasheet V1.1 全文无 \"AON\" (〔0数据〕· 实测 0 命中) ✔ · "
              "② SoC 有 2 颗 dedicated VBUS detect 球 (1C18 / B28) + ★**SoM 两颗都引出 (P1_100 / P3_16) ⇒ 唯一那个〔0数据·待核〕缺口已答掉** ✔ · "
              "③ TPS62130A PG = 高=好 / 开漏需上拉 / 关断拉低 ✔ · ④ BQ25896 VSYS 必接 20µF (★由 ISS-095 结掉★) ✔ "
              "★**② 但落 verified 前必须先加的两条派生结论订正 ★★main 已加 (追加式·老字一字未删)★**: "
              "★**订正 A (P0)**: 「VBUS_DET 分压整条可以删」⇒ ★**对本板不成立** (★5V → 1M+1M 分压 → SoM 的 USB_DRD1_VBUSDET (P1_100) ⇒ 删了 = 5V 灌 3.3V 域 SoC 球 = 过压★) ⇒ ★**分压不可删; dedicated 脚的价值 = 省掉跨铰链那根线** ⇒ ★**板侧 `R_VBUS_DET_D1/R_VBUS_DET_D2/C_DET_VBUS_D` 三件留·不动 ⇒ 「板只改一次」不受影响** ★ · "
              "★**订正 B**: 「复位链按 PG 高=就绪」官网支持, ★**但本项目网表 L62/L65/L67/L71 的 note 写的全是反的 ⇒ 这四条 note 必须在 S6 那一趟之前定死** ★ · "
              "★**订正 C**: 「AON 按 0 ⇒ 沿用 ~108µA/0.40mW」算术不自洽 ⇒ ★**~58µA / ~0.21mW (≈8.4 个月)**, 且分压那 50µA 不会省掉** ⇒ ★**`HW/POWER_SHUTDOWN_V3.md` 已同批加订正** ★ "
              "★**③ 边界**: 板 `611b869e…` / 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…` 逐字节不变 ⇒ 零写板 · 零落表 (★本条只落事实层, 落表动作归 ISS-095 / ISS-302★) ⇒ 落 verified ★")

    replace_scalar("ISS-102", "status", "verified")
    replace_scalar("ISS-102", "verify_result", "pass")
    replace_scalar("ISS-102", "verify_date", TODAY)
    append_key("ISS-102", "verify_note", VN_102)

    VN_095 = ("★**main 2026-11-17 23:1x 落 verified (★owner=main · verify_by=hw-lead ⇒ ★**hw-lead 的 ISS-301 交卷单 = 本条的独立复核** ★ ⇒ C3 满足★)**: "
              "★**① 事实层**: TI bq25896 datasheet (SLUSC76C) §7 逐字 \"Connect a 20uF closely to the SYS pin.\" ⇒ ★**`SYS_CHG` / `C_SYS` 必装 + 20µF 挂地 (紧靠 SYS 脚, 充电板本地, 不跨铰链引系统轨)** ★ "
              "⇒ ★**原裁「VSYS(pin15/16) 不接」不成立** ★ ⇒ ★**但【不需要】把系统轨跨铰链引到镜脚** (★§10.2.2.3: 1µH + ≥20µF 输出电容 ⇒ 20µF 可留在充电板本地★) ⇒ ★**⇒ 「多两根 J_CHG 电源 pin」的回退分支【不需要】** ★ "
              "★**② 官网原件与仓内离线件逐字节一致**: `state/.cache_iss243/bq25896.pdf` md5 `5f2c3958901c8841c7b698b71a16b927` ⇒ ★**与 TI 官网重下的原件 `cmp` rc=0** (★ISS-301 实跑★) ⇒ 证据等级 [官网] ★ "
              "★**③ ★落 verified 时必须同批挂的 4 条落表动作 ⇒ 已挂 ISS-302 (hw-lead · 2026-11-17 23:1x)★**: "
              "① 网表 L499 `C_SYS` dnp DNP→必装 ② 网表 L498 `SYS_CHG` dnp DNP→必装 ③ L498/L499 的 note 追加式订正 (删过期「VSYS 不接 (NC)」裁决 + 「25×10mm 板面」改「≈8 mm² (0805/1206)」 + 删「DNP 时不占板面」) ④ BOM CHG_BOARD 加 1 颗 20µF 6.3V X7R/X5R ⇒ "
              "★**⇒ CHG_BOARD 没有 PCB 文件 ⇒ 不构成「板改第二次」** ★ "
              "★**④ 边界**: 板 `611b869e…` (mtime 2026-11-06 07:07:17) · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…` 逐字节不变 (★本条本身零写盘零落表; 落表动作在 ISS-302 里★) ⇒ 落 verified ★")

    replace_scalar("ISS-095", "status", "verified")
    replace_scalar("ISS-095", "verify_result", "pass")
    replace_scalar("ISS-095", "verify_date", TODAY)
    append_key("ISS-095", "verify_note", VN_095)

    NEW = {
        "id": "ISS-302",
        "title": ("★★[主线内·落表链侧·内部活] ★★【落表: `C_SYS` / `SYS_CHG` 必装 + note 追加式订正 + BOM 加 20 µF (ISS-095 的同批动作)】★★ ⇒ "
                  "★**TI 官网逐字 (bq25896 SLUSC76C §7): \"Connect a 20uF closely to the SYS pin.\"** ⇒ ★**现状: 网表 L498/L499 仍 DNP + note 里留着已过期的「VSYS 不接 (NC)」裁决 + BOM 无那颗 20µF** ★ "
                  "⇒ ★**★CHG_BOARD 没有 PCB 文件 ⇒ 装不装都在同一次布局里落 ⇒ 不构成「板改第二次」** ★"),
        "severity": "high",
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": ("2026-11-17 23:1x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = ISS-301 交卷单 §B5-① (hw-lead 独立复核) + main 本机 grep 盘上真源** ★\n"
                 "⇒ ★**任务书 `state/dispatch_briefs/ISS-302_hw_c_sys_landing.md`** ★\n"
                 "⇒ ★**四条落表动作**: ① 网表 L499 `C_SYS` DNP→必装 ② 网表 L498 `SYS_CHG` DNP→必装 ③ L498/L499 的 note 追加式订正 (★老字一字不许删★) ④ BOM CHG_BOARD 加 1 颗 20µF 6.3V X7R/X5R ★\n"
                 "⇒ ★**走落表链 (改真源 → 重生成 → 台账 + 锚点【落表台账为准】新口径 → 闸复跑) ⇒ 不许手改产物 / 不许手改基线 md5** ★\n"
                 "⇒ ★**边界**: 零写板 · 不碰 MECH/SW 的文件与分片 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"),
        "dispatched_at": None,
        "task_brief": open(BRIEF_PATH_302, encoding="utf-8").read(),
    }
    out = []
    out.append("- id: %s" % NEW["id"])
    for k, v in NEW.items():
        if k == "id":
            continue
        if v is None:
            out.append("  %s: null" % k)
        elif isinstance(v, bool):
            out.append("  %s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, (int, float)):
            out.append("  %s: %s" % (k, v))
        else:
            out.append("  %s: %s" % (k, q(v)))
    out.append("")
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(out) + "\n"
    shutil.copy2(LOG, LOG + ".bak_20261117_2325_main_verify301_102_095_open302")
    open(LOG, "w", encoding="utf-8").write(text)

    after = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    amap = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    for iid, it in bmap.items():
        a = amap.get(iid, {})
        for k, v in it.items():
            if iid in ("ISS-301", "ISS-102", "ISS-095") and k in ("status", "verify_result", "verify_date", "verify_note"):
                continue
            if a.get(k) != v:
                print("❌", iid, k)
                ok = False
    for iid in ("ISS-301", "ISS-102", "ISS-095", "ISS-302"):
        it = amap[iid]
        print("  %s -> %s vr=%s note=%d B" % (iid, it["status"], it.get("verify_result"), len(it.get("verify_note") or "")))
    print("  其余 issue 逐字相同 =", ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
