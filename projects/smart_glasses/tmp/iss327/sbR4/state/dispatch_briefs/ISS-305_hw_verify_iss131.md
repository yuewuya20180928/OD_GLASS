# ISS-305 · hw-lead 任务书 · ★独立复验 ISS-131「RK3572 口径自查版」交付物★

★**派出方 = 项目总工 (main) · cron 775d9893「ARS45 继续执行后继计划」· 2026-11-18 01:4x** ★
★**verify_by = hw-lead（★铁律: 干活的人不许自签 ⇒ 本单是「别人验」★）** ★

---

## 0 · 一句话

★**ISS-131 已由 main 自办完成（★零写板 · 零落表 · 零外发★）⇒ 本单 = 独立复验它的交付物，不是重做一遍。**

★**你这一趟【不产新结论】★ ⇒ ★**只做「复现 + 挑错 + 签字」**★ ⇒ ★**不许改任何工程文件**★

---

## 1 · 待复验的交付物（★3 件★）

| # | 物 | 路径 | 期望 |
|---|---|---|---|
| ① | 交付页 | `HW/RK3572_INQUIRY_CALIBER_V2.md` | 6,007 B · ★**真判据 `grep -cE "🔄 待填"` = 0** ★ |
| ② | 交叉核对脚本 | `state/_iss131_crosscheck_rk3572_caliber.py` | ★**rc=0** ★ |
| ③ | 官方 datasheet（项目内留存） | `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (143,755 B) · PDF 2,414,580 B | ★只读源·不许改★ |

★**ISS-131 单号在 `state/issue_log.yaml`（owner=main · status=open · due 2026-11-19）★**

---

## 2 · 你要跑的（★5 条·原样 rc 落 `logs/iss305/`★）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
mkdir -p logs/iss305

# ① 交付页占位符扫描 (★真判据★)
grep -cE "🔄 待填" HW/RK3572_INQUIRY_CALIBER_V2.md        # ★期望 0★

# ② 交叉核对脚本 (★核心★)
python3 state/_iss131_crosscheck_rk3572_caliber.py ; echo "rc=$?"   # ★期望 rc=0★

# ③ ★★零写板双证 (★跑前跑后各一次·md5 + mtime★)★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat  -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv

# ④ 抽验 3 条官方逐字 (★自己到 txt 里 grep·别抄交付页★)
grep -n "Support 2 MIPI CSI-2 interfaces"          HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt
grep -n "One channel ISP,12M pixels"                HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt
grep -n "Maximum input:4096x3072"                  HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt
grep -n "MIPI_DPHY_CSI0_RX_D2P/MIPI_DPHY_CSI1_RX_D0P" HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt

# ⑤ 全闸回归 (★不许改判据去消红·只记录★)
python3 state/gate_check.py ; echo "rc=$?"
python3 state/merge.py ; echo "rc=$?"
python3 state/issue_check.py ; echo "rc=$?"
```

---

## 3 · 你要挑的错（★这才是复验的价值★）

★**请逐条独立判「对 / 不对」，★不许照抄交付页的结论★**：

| # | 待挑的错 | 怎么判 |
|---|---|---|
| A | ★**球位号 11/11** —— 网表 J_SOM_P2/P4 的 CSI/MCLK 落位 ↔ `FET3572C_PIN_TABLE.csv` ↔ 官方 datasheet | ★自己抽查 ≥ 3 条（★含 1 条「同球双名」的 A22/B22/A23/B23·看窗口判据对不对★）★ |
| B | ★**「CSI 2 接口 vs VICAP 4 组」我方的读法**（★2 个 4-lane D-PHY 可拆 2×2 ⇒ 4 个 2-lane 口★） | ★去 datasheet 找有没有反证★ |
| C | ★**「One channel ISP ⇒ 同时只能 1 路传感器」**（★[官方+推算] 的合成结论★） | ★这是 ★**本单里唯一带推算成分的硬约束** ⇒ ★**请重点挑**: 它是不是 over-claim？★ |
| D | ★**「4096×3072 = 12.58M ⇒ 12M 是单帧分辨率上限不是 MP/s」** | ★自算一遍★ |
| E | ★**MP/s = [0数据] 的判据**（★datasheet 全文检索不到 ISP 的 MP/s 上限★） | ★自己 grep 一遍（★MP/s / MPPS / megapixel/s / throughput★）⇒ ★**若你找到了 ⇒ 交付页这条就是错的 ⇒ 报错**★ |
| F | ★**交付页有没有把 [实测] 混进去** | ★全篇应无 [实测]★（★本机无板★）⇒ ★有就报错★ |

---

## 4 · ★★不许做的事（★本单只有「读 + 记 + 签」★★

1. ★**不许改任何工程文件**（★网表 / 脚表 / BOM / 原理图 / 板 / 落表台账 / 作业包页 一律不许动★）
2. ★**不许改 `state/_iss131_crosscheck_rk3572_caliber.py` 的判据**（★它是本单要复验的对象·★你要是觉得它有 bug ⇒ **在交卷单里报错**, 别自己改掉再报绿★★）
3. ★**不许改任何闸的判据去消红**（★★本单不是修闸单★）
4. ★**不许写 `state/fragments/hw.yaml` 以外的任何分片**（★pm.yaml / mech.yaml / sw.yaml 一个字节不许碰★）
5. ★**零外发**（★不发邮件 · 不联系任何厂商 · 不下单★）
6. ★**不许自签 `state/issue_log.yaml`**（★签字是 main 的活★）
7. ★**不许替老板拍板**（★尤其不许替老板拍「ISP MP/s 到底多少」—— 那是 [0数据] ⇒ 降级方案已在交付页里★）

---

## 5 · 交卷物（★4 件·缺一不合格★）

| # | 物 | 判据 |
|---|---|---|
| ① | 交卷单 `HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md` | ★**B0~B6 七块齐全** ★ · ★**真判据 `grep -cE "🔄 待填"` = 0** ★（★注: `state/check_report_placeholders.py` 抓不到这种形态 ⇒ 真判据是那条 grep★）★ |
| ② | `logs/iss305/` | ★5 组命令的**原样 rc + 原样输出**★ |
| ③ | 分片 | ★走 `state/frag_write.py --agent hw-lead` 原子写★ · ★**`grep -c iss305 state/fragments/hw.yaml` ≥ 5** ★ |
| ④ | 判决 | ★**A~F 六条逐条「对 / 不对 + 依据」** ★ · ★**不许只写「全部通过」**★ |

★**交卷单里必须写全三样（★MEMORY 铁律②★）★**：① **交付时读数** ② **现在读数** ③ **归属单**（★若某道闸红 ⇒ 归到谁身上·不许自己消化★）

---

## 6 · ★为什么派给你（★背景·3 行★）

★**ISS-131 = 「问询口径改 RK3572（ISP 16M→12M / CSI 3×→2×）+ 球位号问询对象改 RK3572 模组厂」** ⇒ ★老板 2026-11-12 02:02 口径「不再发信，全靠自己查资料」⇒ ★**main 已用项目内官方 datasheet 自查完** ⇒ ★**你的活 = 独立复验这份自查有没有 over-claim**★ ⇒ ★**本单不动板·不动网表·不发信 ⇒ 符合「板只改一次」铁律**★

★**★这一趟特别要盯的坑★**：★**交付页里有一句是 [官方+推算] 的合成结论（「One channel ISP ⇒ 同时只能 1 路传感器」）★ ⇒ ★**它将来会变成 demo 选型的硬判据 ⇒ ⇒ 如果它 over-claim ⇒ 以后选型会拿一条错判据去筛供应商 ⇒ ⇒ ★所以这条必须有人真的挑一遍★**
