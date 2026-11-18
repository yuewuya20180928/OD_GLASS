★**ISS-302 · hw-lead 任务书 —— ★★【落表: `C_SYS` / `SYS_CHG` 必装 + note 追加式订正 + BOM 加 20 µF (ISS-095 的同批动作)】★★** ★ (main · 2026-11-17 23:1x)

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
