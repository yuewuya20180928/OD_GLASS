# HW/TI_POWER_FACTS.md —— TI 电源器件 + RK3572 电源域 【官网自查】事实卡 (ISS-095 / ISS-102)

> **作者**: 项目总工 (main / moli) · **日期**: 2026-11-16 06:4x~07:0x
> **为什么做**: ★**老板 2026-11-12 02:02 新口径「不再发信, 全靠自己查资料」⇒ 这两条原本在等【原厂回信】的 issue, 改成【自己查官网】★**
> **本卡性质**: ★**全部 [官网] 一手材料 (TI 官方 datasheet PDF + 项目内已解析的 RK3572 官方 datasheet 引脚表) ⇒ 逐条给出原文引用 + 出处** ★
> **边界**: 本卡**不改网表 / 不改板 / 不改任何判据脚本** · 只给结论与引用 · ★**不许据此直接落表 (落表要走 ISSUE 的落表流程)** ★

---

## ① BQ25896 的 SYS/VSYS 脚 —— **必须接 20 µF, 不能悬空** [官网]

> **出处**: TI **bq25896** datasheet, SLUSC76C (2015-07 初版 / 2018-05 改版), ★**§7 Pin Configuration and Functions, SYS 行 (pin 15,16)** ★
> **原文逐字**: "The internal BATFET is connected between BAT and SYS. When the battery falls below the minimum system voltage, switch-mode converter keeps SYS above the minimum system voltage. ★**Connect a 20uF closely to the SYS pin.**★"

| 项 | 结论 | 出处 / 数值 |
|---|---|---|
| SYS/VSYS 性质 | ★**有源调节输出** (不是干接点/不是可选脚) ⇒ 电池低于 SYS_MIN 时由 buck 继续抬到 SYS_MIN 以上 ★ | §7 pin functions |
| 电容要求 | ★**"Connect a 20uF closely to the SYS pin"** ⇒ ★**必须按规格挂 20 µF** ★ | §7 原文 |
| 电压窗口 | VSYS(MIN) = **3.50 V** (min, 默认 SYS_MIN=3.5V) · VSYS(MAX) = **4.40 V** | §6 Electrical Characteristics (VSYS(MIN)/VSYS(MAX) 行) |
| 环路稳定性 | ★**1 µH + ≥20 µF 输出电容** 才有好环路稳定性 (X7R/X5R, ≥6 V 耐压) ★ | §10.2.2.3 System Output Capacitor |
| 典型应用 | PMID 8.2 µF · SYS **10 µF** · BAT **10 µF** (BATFET 两侧各一颗紧靠) | §10.2 Typical Application 图 |

### ⇒ 对 ISS-095 的结论 (★**main 的裁「VSYS 不接」不成立** ★)
1. ★**「VSYS(pin15/16) 不接」按 TI 数据手册口径【不成立】** ⇒ SYS 是调节输出, 悬空 ⇒ 无输出电容 ⇒ §10.2.2.3 的环路稳定性条件不满足 ⇒ **必须接** ★
2. ★**但【不需要】把系统轨跨铰链引到镜脚** ⇒ ★**20 µF 可以留在充电板本地** (电容紧靠 SYS 脚, 不需要连到负载) ⇒ ⇒ ⇒ ★**ISS-095 原来担心的「多两根电源 pin (镜脚侧 SYS 要经 J_CHG 引到充电板)」这个回退分支【不需要】** ★
3. ★**口径改写建议 (供落表时用)**: 「充电板 SYS 脚**不接跨铰链系统轨**, 但**必须按 TI 规格挂 20 µF 到地** (紧靠 SYS 脚) ⇒ 充电板无系统侧负载时, 由 buck 把 SYS 维持在 ≥3.5 V (SYS_MIN)」 ★

---

## ② TPS62130A 的 PG 极性 —— **高 = 好, 开漏需上拉** [官网]

> **出处**: TI **tps62130a** datasheet (SLVS…TPS6213x), ★**§8.3.3 Power Good (PG) + Pin Functions 表 + §8.4** ★
> **原文逐字 (Pin Functions)**: "Output power good (★**High = VOUT ready, Low = VOUT below nominal regulation**★); ★**open drain (requires pull-up)**★"
> **原文逐字 (§8.3.3)**: "The TPS6213x has a built-in power good (PG) function to indicate whether the output voltage has reached its appropriate level or not. …"
> **原文逐字 (§9, 应用说明)**: "★**The TPS62130A pulls the PG pin Low when the device is shut down by EN, UVLO, or thermal shutdown.**★"

| 项 | 结论 |
|---|---|
| 极性 | ★**高电平 = 输出已就绪 (power good); 低电平 = 输出低于额定调节 / 器件被关断** ★ ⇒ **「ok=高」** |
| 驱动形式 | ★**开漏 (open drain) ⇒ 必须外接上拉** ★ (上拉电流 ≤10 mA) |
| 关断时 | EN 拉低 / UVLO / 过热关断 ⇒ ★**PG 被拉低** ★ (⇒ 用 PG 做复位/时序链时, 关机=PG 低) |

### ⇒ 对 ISS-102 ③ 的结论
★**TPS62130A 的 PG = 开漏, 高=好, 关机/UVLO/过热时拉低** ⇒ ★**复位链画法可按「PG 高 = 就绪」写** ⇒ ★**ISS-097 §0 第 3 条里用的其实是【BQ25896 的 /PG】(充电板电源良好), 与 TPS62130A 的 PG 是两个不同器件的不同脚, ★不许混用极性口径** ★

---

## ③ RK3572 有 dedicated USB VBUS detect 脚 —— **有, 2 个** [官网]

> **出处**: 项目内已解析的 ★**RK3572 官方 datasheet V1.1 引脚表** (`HW/RK3572_PIN_TABLE/rk3572_pins.csv`, 550 球, 由 `parse_rk3572_datasheet.py` 从官方 PDF 解析) ★ ⇒ ★**原始出处 = Rockchip RK3572 Datasheet V1.1 引脚表** ★

| 球位 | 名称 | func |
|---|---|---|
| ★**1C18** ★ | ★**USB_DRD0_VBUSDET** ★ | USB |
| ★**B28** ★ | ★**USB_DRD1_VBUSDET** ★ | USB |

> ★**datasheet 原始行 (逐字, 引脚表 L1641 / L1651)**: "USB_DRD0_VBUSDET  1C18  -" · "USB_DRD1_VBUSDET  1C28/B28" ⇒ ★**两个 USB DRD 各有一个 VBUS detect 输入** ★

### ⇒ 对 ISS-102 ② 的结论
★**SoC 侧有 dedicated VBUS detect 脚 ⇒ VBUS_DET 分压整条可以删** (★省 50 µA + 2 颗电阻, 是 ISS-097 §0 第 6 条里「关机静态电流最大单项」的直接解法★) ★
★**★但仍差一步 (★别当成已闭环★)**: ★**SoM (Forlinx RK3572 模组) 有没有把这两个球引出来, 本卡无法判定** ⇒ ★**〔0数据·待核〕: 查 Forlinx RK3572 模组手册的引脚表** ⇒ ★**若 SoM 已引出 ⇒ 直接用; 若没引出 ⇒ 仍要分压, 且【SoM 侧的分压比 SoC 侧的更省事 (因为 SoM 已经有 VBUS 感测电路)】** ★

---

## ④ ISS-102 ① (ARS45 的 AON/唤醒脚与静态电流) —— ★**该问法已作废** ★

- ★**ARS45 / AR9481 / 酷芯微 已于老板 2026-10-29 19:20 拍板作废** ⇒ ★**「ARS45 的 AON 域」不存在了** ⇒ ★**该子问题【作废】, 不是「还没查到」** ★
- ★**替代口径 (RK3572 侧)**: ★**RK3572 datasheet V1.1 全文检索无 "AON" 字样** ⇒ ★**〔0数据〕: RK3572 没有 datasheet 级的 AON 域定义** ⇒ ★**降级方案: 关机续航继续用 ISS-097 §0 第 6 条的 ~108 µA / 0.40 mW [推算] 口径, 其中 AON 项按 0 计 (待 RK3572 SoM 模组厂手册确认是否另有 always-on 域)** ★

---

## ⑤ BQ25896 的 /PG (与 ② 的 TPS62130A PG 是两个脚, 别混)

- bq25896 典型应用图里 **/PG** 为开漏输出 (STAT 旁的 /PG, 10 kΩ 上拉) ⇒ ★**BQ25896 的 /PG 是「低有效」型电源良好指示 (充电板侧), 而 TPS62130A 的 PG 是「高有效」型 (输出就绪)** ★
- ⇒ ★**ISS-097 §0 第 3 条「充电板 PG (开漏, LOW=输入源良好) ⇒ 经 P-MOS 拉高负载开关 ON 脚」这条画法, 与 ② 的 TPS62130A PG 极性【不冲突】(两个器件两个脚, 极性各自独立)** ⇒ ★**但写文档时必须写清是哪家的 PG** ★

---

## 附 · 本卡的复现命令 (★可复核★)

```bash
cd /tmp
curl -sSL -o bq25896.pdf https://www.ti.com/lit/ds/symlink/bq25896.pdf
pdftotext -layout bq25896.pdf bq25896.txt
grep -n -A3 "Connect a 20uF closely to the SYS pin" bq25896.txt     # §7 SYS pin
grep -n "VSYS(MIN)\|VSYS(MAX)" bq25896.txt                           # §6 电压窗口
grep -n -A6 "10.2.2.3 System Output Capacitor" bq25896.txt          # §10.2.2.3 环路稳定性

curl -sSL -o tps62130a.pdf https://www.ti.com/lit/ds/symlink/tps62130a.pdf
pdftotext -layout tps62130a.pdf tps62130a.txt
grep -n "High = VOUT ready" tps62130a.txt                            # PG 极性
grep -n "pulls the PG pin Low when the device is shut down" tps62130a.txt

cd <项目根>
grep -n "VBUSDET" HW/RK3572_PIN_TABLE/rk3572_pins.csv                # 1C18 / B28
grep -n -i "AON" HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt      # 无命中 ⇒ 无 AON 域
```


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
