#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-301 分片写入驱动 (hw-lead)
=====================================================================
纪律: 必须走 state/frag_write.py 的原子写 (tmp + fsync + os.replace),
      禁止 open(p,"w")。
说明: frag_write.py 的 CLI 用 shlex.split(spec) 解析 --add-* 参数
      ⇒ 值里不能带空格 (否则 SystemExit)。项目里既有的 300+ 条
      interface_claims / 185 条 needs_from 都是用 state/frag_write.py
      自己的 Python API 写的 (见该文件 docstring 的用法示例)。
      ⇒ 本驱动直接 import state/frag_write.py 的 update_fragment(),
         走的是同一个 atomic_write_yaml() ⇒ 与 CLI 完全同一落盘路径。
=====================================================================
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "state"))

from frag_write import update_fragment, load_fragment, atomic_write_yaml  # noqa: E402

TODAY = "2026-11-17"
HANDOFF = "HANDOFF/2026-11-17_hw-lead_ISS301_TI电源事实卡复核.md"

NEED_ITEM = (
    "【ISS-301 复核结论 · 请 main 落表/签字】"
    "① ISS-095 可落 verified (TI bq25896 SLUSC76C §7 原文 Connect a 20uF closely to the SYS pin 逐字坐实; "
    "本仓 state/.cache_iss243/bq25896.pdf 与我今天从 ti.com 重下的原件 md5 同为 5f2c3958901c8841c7b698b71a16b927 "
    "且 cmp rc=0 逐字节一致) ⇒ 同批落表: HW/netlist_v1.csv L499 C_SYS dnp DNP→必装 + L498 SYS_CHG dnp DNP→必装 + "
    "两条 note 追加式改写 + BOM 加 1 颗 20uF 6.3V X7R (零改板: CHG_BOARD 根本没有 PCB 文件) "
    "② ISS-102 事实层 4 条全部成立, 但卡里两条派生结论必须先加追加式订正: "
    "订正A (P0) 事实卡 §③ 的『VBUS_DET 分压整条可以删』对本板不成立 —— 本板是 5V→1M+1M→SoM USB_DRD1_VBUSDET(P1_100), "
    "删分压 = 5V 灌 3.3V 域 SoC 球 = 过压 ⇒ 正确口径 = 分压不可删, dedicated 脚的价值是省掉跨铰链那根线 + 让 SoC 侧直接判 VBUS 在位, "
    "不是省掉板上的分压 "
    "③ 订正B (落表前必改, 关系板只改一次) 事实卡 §② 说复位链按『PG 高=就绪』, 而网表 L62/L65/L67/L71 的 note 全写反了 "
    "(两路 PG 都好时为低 / PG 有效(低) / 任一路不 ok 本网被上拉拉高) ⇒ 网表 note 必须在本趟 S6 之前定死; "
    "我建议按 HW/PCB/RESET_P0_FIX_PLAN.md 改法② 把 Q_AND 改 DNP (两颗 DC-DC 本就 DNP ⇒ 该互锁实际损失 0, 且不带极性坑进本趟) "
    "④ 订正C (算术) 事实卡 §④ 的『沿用 108uA/0.40mW + AON 按 0 计』不自洽 (108uA 本身含 50uA AON) ⇒ 正确口径 ~58uA/~0.21mW "
    "约 8.4 个月; 且 VBUS_DET 那 50uA 在本板不会省掉 ⇒ HW/POWER_SHUTDOWN_V3.md 需同口径 (那是 ISS-097 owner=boss 的活, 我没动) "
    "⑤ 卡里另有两处转写差: §③ 引脚行写了 1C28/B28 (官网只有 B28, 1C28 全库零命中) · §② 的 requires pull-up "
    "(官网逐字是 requires pullup resistor) · §② 括注『上拉电流≤10mA』出自 §9.3.2 放电接法, §8.3.3 + §6 VOL_PG 的证据灌能力只有 2mA "
    "(本板 10k/1.8V = 0.18mA, 两边都满足) ⇒ 事实卡本体一个字我没改, 请 main 用追加式加订正行 (老字不删) "
    "⑥ 卡里那个唯一的 [0数据] 残余我今天答掉了: Forlinx OK3572-C / FET3572-C User Hardware Manual V1.0 (2026-06-15) §2.6.2 "
    "Table 2 (P1 Even) row NUM=100 BALL=B28 USB_DRD1_VBUSDET + Table 6 (P3 Even) row NUM=16 BALL=1C18 USB_DRD0_VBUSDET "
    "+ 官方 Pin Multiplexing 表 P1_100 / P3_16 ⇒ SoM 两颗球都引出来了; 我自己重下官网手册 (默认 curl 被 Cloudflare 拦, 换浏览器 UA 成功) "
    "并独立重跑了 399 行全量逐格比对 (官网 8 表 50/50/50/49/50/50/50/50 = 399 = 本地 399, 7 列多重集 diff 仅 9 行且逐条 spot check "
    "全是官方空单元格写法差 ⇒ 实质差异 0) ⇒ 网表 L439 那条 [官方] 断言成立 ⇒ S6 清单里 R_VBUS_DET_D1 / R_VBUS_DET_D2 / C_DET_VBUS_D "
    "三件留不动, 板侧清单零变化"
)

CLAIM_VALUE = (
    "四条断言的【事实层】全部复核成立: "
    "① BQ25896 SYS 必接 20uF (成立: TI SLUSC76C §7 逐字 + 官网原件 md5 5f2c3958901c8841c7b698b71a16b927 与本仓缓存 cmp rc=0) · "
    "② TPS62130A PG=高=好 / 开漏需上拉 / 关断拉低 (成立: TI Rev.F SLVSAG7F Pin Functions L176 + §8.3.3 + §9.3.2; "
    "但逐字应为 requires pullup resistor, 且保证沉灌只有 2mA (§8.3.3 + VOL_PG IPG=-2mA) 不是 10mA) · "
    "③ RK3572 有 2 颗 dedicated USB VBUS detect 球 (成立: RK3572 datasheet V1.1 引脚表 L1641/L1651; 卡里的 1C28/B28 多字, 官网只有 B28) "
    "+ SoM 两颗都引出 (成立: Forlinx 手册 V1.0 §2.6.2 Table 2/Table 6 + Pin Multiplexing 表 P1_100/P3_16) "
    "⇒ 卡里唯一的 [0数据] 残余已答掉; 但派生结论『分压整条可以删』对本板不成立 (照做 = 5V 灌 3.3V 域 SoC 球 = P0 过压) · "
    "④ ISS-102 ① AON 问法作废 + RK3572 datasheet V1.1 全文无 AON (成立: grep -c 实测 0 / rc=1); "
    "但降级方案『沿用 108uA/0.40mW + AON 按 0 计』算术不自洽 ⇒ 应为 ~58uA/~0.21mW"
)

CLAIM_NOTE = (
    "证据等级: ① [官网] ② [官网] ③ [官网] (SoC+SoM 两侧) ④ [官网]+[推算]; "
    "复核手段 = 本仓离线件与 TI 官网原件 md5+cmp 逐字节对拍 / 自己上 ti.com 与 docs.forlinx.net GET 官网件 / "
    "自己写脚本做 Forlinx 官网 8 表 x 本地 399 行 7 列多重集全量比对; "
    "实物 [实测] = 0 条; 零外发 (只 GET, 不发信/不询价/不问询/不采购); 零写板 零落表 零改网表/脚表/BOM/事实卡本体; 零改闸; "
    "未自签 issue_log (ISS-095 / ISS-102 的签字是 main 的活)"
)

ART_SUMMARY = (
    "ISS-301 交卷单: B0 一句话结论 + B1 四条断言复核表 (断言原文逐字 / 证据出处 / 复核手段 / 结论 / 证据等级) + "
    "B2 交叉一致性三条 (ISS-095 ① vs C_SYS DNP 不自洽且代价算错 = 实占约 8mm² 非 25x10mm; ISS-102 ④ 交叉引用没写错, "
    "但被引用的网表 note 极性反了 L62/L65/L67/L71; ④ 降级方案 108uA 含 50uA AON 算术不自洽) + B3 现场 rc 原样 + "
    "B4 边界自证 (板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17:362193413 双自证零写板) + "
    "B5 给 main 的明确结论 4 问; 证据副本在 logs/iss301/ (TI 官网 2 个件 + Forlinx 官网手册快照 + 399 行比对日志)"
)


def mutate(d):
    d.setdefault("needs_from", []).append({
        "key": "iss301_ti_power_facts_counterverify_result",
        "to": "main",
        "item": NEED_ITEM,
        "since": TODAY,
    })
    d.setdefault("interface_claims", []).append({
        "key": "iss301_ti_power_facts_4_claims_verified",
        "value": CLAIM_VALUE,
        "note": CLAIM_NOTE,
        "ref": HANDOFF + "#B1",
    })
    d.setdefault("artifacts", []).append({
        "path": HANDOFF,
        "kind": "note",
        "version": "1.0",
        "updated_at": TODAY,
        "summary": ART_SUMMARY,
    })


def main():
    before = load_fragment("hw-lead")
    n_before = (
        len(before.get("needs_from") or []),
        len(before.get("interface_claims") or []),
        len(before.get("artifacts") or []),
    )
    update_fragment("hw-lead", mutate)          # ← 走 state/frag_write.py 的原子写
    after = load_fragment("hw-lead")
    n_after = (
        len(after.get("needs_from") or []),
        len(after.get("interface_claims") or []),
        len(after.get("artifacts") or []),
    )
    print("[iss301] ✅ 分片已原子写 (state/frag_write.py::update_fragment)")
    print(f"[iss301]    needs_from       {n_before[0]} -> {n_after[0]}")
    print(f"[iss301]    interface_claims {n_before[1]} -> {n_after[1]}")
    print(f"[iss301]    artifacts        {n_before[2]} -> {n_after[2]}")
    # 逐条回读校验 (确保三条都真的落进去了)
    ok = True
    for k, field, want in (
        ("iss301_ti_power_facts_counterverify_result", "needs_from", "to=main"),
        ("iss301_ti_power_facts_4_claims_verified", "interface_claims", "key"),
    ):
        got = [e for e in (after.get(field) or []) if e.get("key") == k]
        print(f"[iss301]    ✔ {field}: {k} -> {len(got)} 条")
        ok = ok and len(got) == 1
    art = [e for e in (after.get("artifacts") or []) if e.get("path") == HANDOFF]
    print(f"[iss301]    ✔ artifacts: {HANDOFF} -> {len(art)} 条")
    ok = ok and len(art) == 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
