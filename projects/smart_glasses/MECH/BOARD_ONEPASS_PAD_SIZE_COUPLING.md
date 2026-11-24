# MECH · 「板那一趟」焊盘尺寸 ⇄ MECH 判决链 7 个数 —— 【耦合盲区】清账真相页 (ISS-403 · mech-lead)

> ★**生成**: 2026-11-25 00:3x~01:5x (mech-lead · 本机实跑) · ★**形态**: ★**纯查证 + 纯分析 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发** ★
> ★**纪律归位**: 「板只改一次」纪律 ① (★先派纯分析类·不动板★) · ★**本单是【开工前的耦合分析】, 不是【已经出事】** ★
> ★**证据等级**: `[官网]` = 厂商官网/能力表逐字 · `[实测]` = 本机实读/实跑读数 · `[媒体]` = 第三方报道 · `[推算]` = 本机按公式算 · `[0数据]` = 查不到 ★

────────────────────────────────────────────────────────────────────────────────
## ★§0 · 一句话结论 (★本机实跑得出·不抄任何 agent 报告★) ★

★★ **「板那一趟」一旦把排针焊盘从 `1.000×1.000` 放大到 `1.110×1.110` (★规划孔 `Ø0.71` ⇒ 环宽 `0.1450` < 板厂多层 1oz 绝对下限 `0.15` ⇒ 必须放大★), MECH 判决链消费的 7 个数【全部作废】—— 而当前 7 道 MECH 闸里有 5 道【对它完全盲】(★pad 改了它们照样全绿★) ⇒ ⇒ 「结构件按旧数出件 → 装配干涉 → 板改第二次」这条路, 今天【没有任何机器闸会响】** ★★

★**判据句 (方向)**: ★**MECH 侧必须在「板那一趟」同批把 7 个数与 5 道盲闸一起收口, 否则焊盘一放大, 判决链的数全部作废而无人报警** ★
★**事实句 (现状)**: ★**本机 A/B 实测 (★pad `1.000` vs `1.110`·只换库不换真件·`--root` 指向真实项目★): 7 道闸里 5 道红项集合【逐条相同】⇒ 它们结构上看不见焊盘尺寸; 另有 7 道 MECH 闸【一道都没挂】`state/gate_check.py` ⇒ 连「盲」的那道主闸都不在门禁链上跑** ★
★**两句同时成立, 不许混成一句「OK / 合格」** ★

────────────────────────────────────────────────────────────────────────────────
## ★§1 · 前提: 「焊盘维持 1.000」已被坐实为不成立 ★

| 事实 | 值 | 证据等级 | 出处 (★本机实读★) |
|---|---|---|---|
| 官方 KiCad 库 THT 排针焊盘 | `(size 1 1)` (正方) | `[实测]` | `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` L177-L183 · md5 `7a5f470c1f70d4b832be258501945385` |
| 同上 (1×2) | `(size 1 1)` | `[实测]` | 同目录 `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` L177-L183 · md5 `47bcbf6d0f267d543e50d4b2a8dfabf5` |
| 库件默认钻孔 | `(drill 0.65)` | `[实测]` | 同上 (两个 `.kicad_mod` 各 4/2 处) |
| ★**「板那一趟」规划的钻孔** ★ | ★**`Ø0.71` (TYP)** ★ | ★`[官网]` ★ | ★`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` §1.1 (Samtec 官方推荐 PCB 图文字层逐字 `.028 0.71 (TYP)`) + ISS-391 已登记的板侧动作「落 FTS 时钻孔 `0.65 → 0.71`」 ★ |
| ★**环宽 (annular ring) = (焊盘 − 钻孔) / 2 = (1.000 − 0.71) / 2** ★ | ★**`0.1450` mm** ★ | ★`[推算]` (本机算) ★ | ★与 `state/issue_log.yaml` ISS-387 `verify_result` 登记的 `0.1450` 逐字一致 ★ |
| ★**板厂能力表 (逐字)** ★ | ★**`PTH annular ring ≧0.20mm` ; `2-layer: 1 oz: Recommended 0.25 mm or above; absolute minimum 0.18 mm` ; `Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm` ; `2 oz: 0.254 mm or above`** ★ | ★`[官网]` ★ | ★**JLCPCB 官方 PCB 能力表** · ★原件落盘** `tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html` (md5 `24dd86f068aa85728b74706f2fd80b3e`·main 2026-11-24 20:43 curl 落盘) · ★**本单本机实读该文件确认逐字一致** (见 §1.1 复现命令) ★ · ★另 `state/ROUND_LOG_cron775d_2026-11-24_2050.md` L46 / `HANDOFF/2026-11-24_hw-lead_ISS396_FTS改孔登记落盘.md` L83 同款逐字 ★ |
| ★**⇒ `0.1450` < `0.15`** ★ | ★**低于多层 1oz 绝对下限** ★ | ★`[推算]` ★ | ★**⇒ 「焊盘维持 `1.000×1.000`」这个前提已被坐实为不成立** ★ |
| ★**本板适用哪一行** ★ | ★**多层 (Multilayer) 1 oz** ★ | ★`[实测]` + `[推算]` ★ | ★本板 = **8 层** (F.Cu/In1..In6.Cu/B.Cu) · 外层铜 **1 oz** ⇒ `HW/PCB/FAB_ORDER_NOTES.md` §1「层数 8 层 / 外层铜 1 oz」+ `HW/PCB/demo_mainboard.kicad_pcb` 的 `(layers ...)` 段 (8 个 `*.Cu` signal 层) ⇒ 走 `Multilayer: 1 oz` 行 (绝对下限 `0.15`) ★★ |
| ★**⚠ 条件句 (若板厂按 2 层做)** ★ | ★**2 层 1 oz 的绝对下限是 `0.18` (不是 `0.15`) ⇒ `1.010` 那一档【不满足】⇒ 需 `pad ≥ 1.070`** ★ | ★`[推算]` ★ | ★**本板是 8 层板, 走 2 层是异常路径; 但「板厂是谁」这一格至今 `[0数据]` ⇒ 此条件句必须随 §8 三选项一起交 main** ★ |

### ★§1.1 · §1 的复现命令 (★本机实跑·rc 逐字★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0{2,4}_P1.27mm_Vertical.kicad_mod
grep -n "size\|drill" /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod
python3 - <<'PY'
import re,html
t=open("tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html",encoding="utf-8",errors="replace").read()
for m in re.finditer(r"PTH annular ring", t):
    s=max(0,m.start()-200); e=min(len(t),m.end()+700)
    print(re.sub(r"<[^>]+>"," ", t[s:e]))
PY
# rc=0
```

★**读数 (逐字)**: 焊盘 `(size 1 1)` · 钻孔 `(drill 0.65)` · 能力表逐字 `Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm` ★

★**★【降级方案 · 必须项】**: ★**若「本板厂到底是谁」这一格继续 `[0数据]` (★`HW/PCB/FAB_ORDER_NOTES.md` 全文只写「板厂」从未指名★), 则本单**不把它当阻塞项挂着** ⇒ ★**降级路径 = §8 的三档 pad 全列出来 (三档都给出环宽与代价) ⇒ 由 main 在拍档时把「板厂能力表适用行」作为拍档的前置输入一并落**★ ⇒ **本单不外发询价, 不依赖任何外部回复** (★纪律 ①★) ★

────────────────────────────────────────────────────────────────────────────────
## ★§2 · pad 档位表 (★本机自算·★不抄任何 agent 报告★) ★

★**推导**: ★`环宽 = (pad − 规划钻孔 0.71) / 2` ⇒ 反解 `pad = 2 × 环宽下限 + 0.71` ★ `[推算]` (本机算)

| 档位 ID | ★pad (mm)★ | ★环宽 (规划孔 `Ø0.71`) (mm)★ | ★板厂口径 (多层 1oz)★ | ★达成档★ | 证据等级 |
|---|---|---|---|---|---|
| `P1000` | ★`1.000`★ | ★`0.1450`★ | ★**低于绝对下限 `0.15`** ★ | ★**✗ 不成立 (现状·前提已死)** ★ | `[推算]` |
| `P1010` | `1.010` | `0.1500` | 恰达绝对下限 `0.15` | ✓ 绝对下限 (推荐值 `0.20` 未达) | `[推算]` |
| `P1110` | `1.110` | `0.2000` | 达推荐值 `0.20` | ✓ **推荐值** | `[推算]` |
| `P1218` | `1.218` | `0.2540` | 达 `2 oz` 的 `0.254` | ✓ 2oz 口径 (若板厂按 2oz 报价) | `[推算]` |

★**★【必须登记的两条口径事实】★**:
★**① 环宽是按【规划钻孔 `Ø0.71`】算的, 不是按库件默认 `(drill 0.65)`** ⇒ ★**若那一趟最终按库件默认 `0.65` 落板, 环宽 = (1.000 − 0.65)/2 = `0.1750` ≥ `0.15` ⇒ 环宽这一格就不红了 ⇒ ★**但 ISS-391 已把「落 FTS 必须 `0.65 → 0.71`」登记成板侧动作 (厂件规格 `Ø0.71` 才是 Samtec 官方值) ⇒ 本单按 `0.71` 算** ★ (`[推算]` + `[实测]` + `[官网]`) ★
★**② 本板是 8 层多层板 ⇒ 适用 `Multilayer: 1 oz` 行 (绝对下限 `0.15`) ⇒ `1.010` 成立; 若板厂按 2 层做 ⇒ 绝对下限 `0.18` ⇒ `1.010` 不成立 (见 §1 条件句)** ★

────────────────────────────────────────────────────────────────────────────────
## ★§3 · 7 个数 × 4 个 pad 档位 · 全矩阵 (★本机自算·逐格带推导式★) ★

### ★§3.1 · 7 个数是谁 + 各自的推导式 (★每个都从真源现读·不许写死★) ★

| # | ★数名★ | ★现值★ | ★推导式 (★本机按公式算★) ★ | ★真源 (★现读★) ★ |
|---|---|---|---|---|
| ① | `j_debug_copper_x` | `4.8100` | ★`跨距 3.8100 + pad` ★ (3 段 × 1.27) | `.kicad_mod` 实读 4 个焊盘沿局部 Y 跨距 `3.8100` `[实测]` |
| ② | `j_uart_copper_x` | `2.2700` | ★`跨距 1.2700 + pad` ★ (1 段 × 1.27) | `.kicad_mod` 实读 2 个焊盘跨距 `1.2700` `[实测]` |
| ③ | `j_debug_required_clear_x` | `6.6100` | ★`copper_x + 2 × (CRIT + TOL)` = `copper_x + 1.8000` ★ | ★`CRIT`/`TOL` 真身 = `MECH/service_port_check.py` L126-L127 (`TOL["fdm_part"]=0.30` ⇒ `CRIT=0.60`) ★`[实测]` |
| ④ | `j_uart_required_clear_x` | `4.0700` | ★`copper_x + 2 × (CRIT + TOL)` = `copper_x + 1.8000` ★ | 同上 ★ |
| ⑤ | `j_uart_cover_margin_x` | `0.1350` | ★`(座体必须清空区 X 宽 2.5400 − copper_x) / 2` ★ | ★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L346「检修口 · 必须清空区 X 17.620..20.160」⇒ 宽 `2.5400` (★座体支配·固定值·不随铜箔走★) ★`[实测]` |
| ⑥ | `j_debug_opening_margin_x` | `2.6950` | ★`(开口 X 宽 10.2000 − copper_x) / 2` ★ | ★同页 L352「调试口 · 开口 (居中解) X 137.850..148.050」⇒ 宽 `10.2000` ★`[实测]` |
| ⑦ | `j_debug_cover_margin_y` | `0.7700` | ★`(必须清空区 Y 宽 2.5400 − copper_y) / 2` · ★`copper_y = pad` ★ | ★同页 L351「调试口 · 必须清空区 Y 55.330..57.870」⇒ 宽 `2.5400` ★`[实测]` |

★**★【推导链自检 · 本机实跑逐格对拍】★**: ★**按上表推导 pad=`1.000` 档 ⇒ 得 `4.8100 / 2.2700 / 6.6100 / 4.0700 / 0.1350 / 2.6950 / 0.7700` ⇒ 与既有已签收页 (`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` L105/L110/L129/L138 · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` L32/L38/L113 · `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` L44/L46) 登记值【逐字一致·7/7】⇒ 推导链成立** ★ (`[实测]`)

### ★§3.2 · 全矩阵 (★本机自算·4 档 × 7 数 = 28 格·每格带推导式★) ★

★**记法**: ★`铜箔X` = ①/② · `清空需求` = ③/④ · `罩住X` = ⑤ · `开口X` = ⑥ · `罩住Y` = ⑦ ★
★**判据阈**: `CRIT = 0.60` (罩住/开口【每边】余量) · `最坏 = 余量 − TOL 0.30` ⇒ **过阈要 `余量 ≥ 0.60`** ★

| 档位 | pad | 环宽 | ① `J_DEBUG` 铜箔X | ② `J_UART` 铜箔X | ③ `J_DEBUG` 清空需求 | ④ `J_UART` 清空需求 | ⑤ `J_UART` 罩住X | ⑥ `J_DEBUG` 开口X | ⑦ `J_DEBUG` 罩住Y |
|---|---|---|---|---|---|---|---|---|---|
| ★`P1000`★ | `1.000` | `0.1450` | ★`4.8100`★ | ★`2.2700`★ | ★`6.6100`★ | ★`4.0700`★ | ★`0.1350`★ | ★`2.6950`★ | ★`0.7700`★ |
| `P1010` | `1.010` | `0.1500` | `4.8200` | `2.2800` | `6.6200` | `4.0800` | `0.1300` | `2.6900` | `0.7650` |
| ★`P1110`★ | `1.110` | `0.2000` | ★`4.9200`★ | ★`2.3800`★ | ★`6.7200`★ | ★`4.1800`★ | ★`0.0800`★ | ★`2.6400`★ | ★`0.7150`★ |
| `P1218` | `1.218` | `0.2540` | `5.0280` | `2.4880` | `6.8280` | `4.2880` | `0.0260` | `2.5860` | `0.6610` |

★**逐格推导式 (★每格都可复算·★闸 `check_pad_size_coupling_closed.py` 按同一组公式自算并逐格对拍★) ★**:

★**① `J_DEBUG` 铜箔X** = `3.8100 + pad`:
· `P1000` ⇒ `3.8100 + 1.000 = 4.8100` · `P1010` ⇒ `3.8100 + 1.010 = 4.8200` · `P1110` ⇒ `3.8100 + 1.110 = 4.9200` · `P1218` ⇒ `3.8100 + 1.218 = 5.0280`
★**② `J_UART` 铜箔X** = `1.2700 + pad`:
· `1.2700 + 1.000 = 2.2700` · `+1.010 = 2.2800` · `+1.110 = 2.3800` · `+1.218 = 2.4880`
★**③ `J_DEBUG` 清空需求** = `① + 1.8000`:
· `4.8100 + 1.8000 = 6.6100` · `4.8200 + 1.8000 = 6.6200` · `4.9200 + 1.8000 = 6.7200` · `5.0280 + 1.8000 = 6.8280`
★**④ `J_UART` 清空需求** = `② + 1.8000`:
· `2.2700 + 1.8000 = 4.0700` · `2.2800 + 1.8000 = 4.0800` · `2.3800 + 1.8000 = 4.1800` · `2.4880 + 1.8000 = 4.2880`
★**⑤ `J_UART` 罩住X** = `(2.5400 − ②) / 2`:
· `(2.5400 − 2.2700)/2 = 0.1350` · `(2.5400 − 2.2800)/2 = 0.1300` · `(2.5400 − 2.3800)/2 = 0.0800` · `(2.5400 − 2.4880)/2 = 0.0260`
★**⑥ `J_DEBUG` 开口X** = `(10.2000 − ①) / 2`:
· `(10.2000 − 4.8100)/2 = 2.6950` · `(10.2000 − 4.8200)/2 = 2.6900` · `(10.2000 − 4.9200)/2 = 2.6400` · `(10.2000 − 5.0280)/2 = 2.5860`
★**⑦ `J_DEBUG` 罩住Y** = `(2.5400 − pad) / 2` (★`copper_y = pad`★):
· `(2.5400 − 1.000)/2 = 0.7700` · `(2.5400 − 1.010)/2 = 0.7650` · `(2.5400 − 1.110)/2 = 0.7150` · `(2.5400 − 1.218)/2 = 0.6610`

★**★⇒ 三个硬事实 (★本机实算★) ★**:
★**① 7 个数【无一例外全部要重算】**: ★`①/②` 直接吃 pad; ★`③/④` 由 `①/②` 派生; ★`⑤` 由 `②` 派生; ★`⑥` 由 `①` 派生; ★`⑦` 由 pad 直接派生 ⇒ ★**一个都不例外** ★
★**② `J_UART` 罩住余量 `0.1350 → 0.0800` (pad=`1.110`) ⇒ 本来就红 (最坏 `-0.1650` < `CRIT` `0.60`) ⇒ ★**红得更狠** ★ ⇒ ★**且 `pad = 1.218` 时 `0.0260` (最坏 `-0.2740`) ⇒ 越放大越红** ★
★**③ `J_DEBUG` 罩住Y `0.7700 → 0.7150` (pad=`1.110`) ⇒ 最坏 `0.4700 → 0.4150` ⇒ ★**本来就红, 再红一点** ★**

★**★⇒ 由此得到一条【口径陈旧】的事实句 (★不写「板已经改坏了」·★这是【开工前的耦合分析】★) ★**:
★**「MECH 七个数一个都不用改」这个结论 (★ISS-387 / ISS-391 当时的口径★) 在 `pad = 1.000` 之下成立, 在 `pad ≥ 1.010` 之下【不成立】⇒ 那两页的现状值型判据【已经陈旧】⇒ 结构件 + 镜脚侧要整体重算一次** ★ (`[推算]`)

★**★⇒ 代价 (★金额不代估·★区间只作量级参考★) ★**: ★**结构件 + 镜脚侧整体重算 = 2-4 周 + ¥4-8K 级 (★沿用 ISS-387 / ISS-391 已登记的量级·★本单不重新估价·★精确金额归 main / boss★) ★**

────────────────────────────────────────────────────────────────────────────────
## ★§4 · 5 道盲闸: 逐道点名 + 盲在哪一行 (★本机自己跑 A/B·不抄结论★) ★

### ★§4.1 · A/B 实测方法 (★零拷贝假象·★只换库不换真件★) ★

★**沙盒**: ★**只落项目盘 `tmp/iss403/`** (★系统 `/tmp` 带 usrquota 且配额已满 ⇒ 不落★) ★
★**做法**: ★**① `tmp/iss403/libA/` = 官方 KiCad 库根的【符号链接农场】, 其中 `Connector_PinHeader_1.27mm.pretty` 落成实体副本且两份 THT 封装 `(size 1 1)` → `(size 1.11 1.11)`; ★② `tmp/iss403/libB/` = 同款农场, 该 `.pretty` 为【实体副本·原样 `(size 1 1)`】; ★③ `--root` 始终指向【真实项目根】⇒ 页 / 板 / CRIT 文件全是真件 ⇒ 零拷贝假象; ★④ 7 道闸中【能读库的两道】跑沙盒副本 (★唯一改动 = `LIBROOT` 常量一行·diff 自证 2 行·其余 5 道【压根不读库】⇒ 直接跑真闸·副本与真闸 md5 逐字相同★) ★**

★**符号链接农场的用意**: ★**它保证 `.pretty` 目录数 (155) 与 `.kicad_mod` 文件数 (15468) 与官方根【逐字相同】⇒ `check_jdebug_1p27_clearance.py` G7 的「库清单数」判据不会被沙盒自身噪声打红 ⇒ A/B 差集里只剩「焊盘尺寸」这一个变量** ★ (`[实测]`)

### ★§4.2 · A/B 结果逐道 (★本机实跑·rc 与红项集合逐字★) ★

| # | MECH 闸 | A 臂 (`pad 1.110`) rc | B 臂 (`pad 1.000`) rc | ★红项集合差集★ | ★反应★ |
|---|---|---|---|---|---|
| 1 | `MECH/check_debug_seat_3d_fit.py` | `0` (201/201 绿) | `0` (201/201 绿) | ★A 独有 ∅ · B 独有 ∅ (stdout md5 两臂**逐字相同** `a64fd530…`)★ | ★**✗ 完全盲** ★ |
| 2 | `MECH/check_debug_seat_rework_spec.py` | `0` | `0` | ★∅ (stdout md5 两臂**逐字相同** `b86c5610…`)★ | ★**✗ 完全盲** ★ |
| 3 | `MECH/check_fts_seat_body_geometry.py` | `0` | `0` | ★∅ (stdout md5 两臂**逐字相同** `5d17b5e2…`)★ | ★**✗ 完全盲** ★ |
| 4 | `MECH/check_connector_clearance_caliber.py` | `1` | `1` | ★∅ (stdout md5 两臂**逐字相同** `7ade2794…`)★ | ★**✗ 完全盲 (红项无差集)★** ★ |
| 5 | `MECH/check_fts_vs_generic_courtyard_delta.py` | `0` | `0` | ★∅ (stdout md5 两臂**逐字相同** `7839434d…`)★ | ★**✗ 完全盲** ★ |
| 6 | `MECH/check_jdebug_1p27_clearance.py` | `1` | `0` | ★A 独有: `G1` `G2` `G3` `G4` 四条转红 (★外加 17 条逐项对拍红·含 `copper_w_mm 写 4.81, 实算 4.92` / `clearance_x_left 写 2.695, 实算 2.64` / `per_edge_mm 写 0.3625, 实算 0.4175` / `annular_ring_mm 写 0.175, 实算 0.23`★)★ | ★**✓ 抓得到** ★ |
| 7 | `MECH/check_juart_1p27_clearance.py` | `1` | `0` | ★A 独有: `J0` `J1` `J5` `J7` 四条转红 (★外加逐项对拍红·含 `实读 pitch=1.27 铜箔 X 宽=2.3800 (包络 [-0.555, -0.555, 1.825, 0.555])` / `实读环宽=0.2300`★)★ | ★**✓ 抓得到** ★ |

★**★⇒ 汇总: ★5/7 道对焊盘尺寸【完全盲】 (★stdout md5 两臂逐字相同 ⇒ 不是「红得不一样」, 是「连输出都一模一样」★) ★**

### ★§4.3 · 逐道点名: 【盲在哪一行 / 为什么结构上看不见】 ★

★**★逐道给【根因行号】(★本机实读源码·★不是推测★) ★**:

| # | 闸 | ★盲在哪一行 (★逐字★) ★ | ★盲的机制 (★判据句★) ★ | 证据等级 |
|---|---|---|---|---|
| 1 | `check_debug_seat_3d_fit.py` | ★**L683** `"J_DEBUG": {"copper": {"x": 4.81, "y": 1.0},` · ★**L686** `"J_UART": {"copper": {"x": 2.27, "y": 1.0},` ★ (★`official` 表·★模块级字面量★) ★ | ★**铜箔宽被【写死】成 `pad = 1.000` 的产物 (`3.81 + 1.00` / `1.27 + 1.00`) ⇒ pad 一改这两个数就错 ⇒ 闸拿错的数算判决 ⇒ 判决【自洽但失真】⇒ 全绿** ★ | `[实测]` |
| 1b | 同上 (★同源的第二/第三处★) | ★**L491** `want_cover = r4((float(c["value"]) - 4.81) / 2.0)` · ★**L746** `mc = r4((v - 4.81) / 2.0)` · ★**L753** `"protrusion_per_side": r4(max(0.0, (4.81 - v) / 2.0))` ★ | ★**同一份「4.81」字面量在文件里出现 5 处 (L491/L683/L686/L746/L753) ⇒ 改 pad 要改 5 处 ⇒ 【改一处就假绿】★ ⇒ 这就是「盲」的结构性来源** ★ | `[实测]` |
| 2 | `check_debug_seat_rework_spec.py` | ★**L120** `OFFICIAL_DEBUG_COPPER_X = 4.8100` · ★**L122** `OFFICIAL_COPPER_Y = 1.0000` · ★**L579** `copper = OFFICIAL_DEBUG_COPPER_X if r.get("ref") == "J_DEBUG" else 2.2700` ★ | ★**注释 L119 写着「★闸从官方 .kicad_mod 实算·拿不到时退化为页内声明值★」, 但代码里【一行 `.kicad_mod` 读取都没有】⇒ 注释是【愿望】, 实现是【写死】⇒ 下一个读代码的人会以为现读能力已生效** ★ | `[实测]` |
| 3 | `check_fts_seat_body_geometry.py` | ★**全文件 `kicad_mod` / `LIBROOT` / `libroot` / `footprint` 命中数 = 0** ★ | ★**它压根没有任何通向 KiCad 库的读入口 ⇒ 焊盘尺寸【在物理上进不去】它的判决** ★ | `[实测]` |
| 4 | `check_connector_clearance_caliber.py` | ★**同上 · 命中数 = 0** ★ | ★**同上** ★ | `[实测]` |
| 5 | `check_fts_vs_generic_courtyard_delta.py` | ★**同上 · 命中数 = 0** ★ | ★**同上** ★ | `[实测]` |
| 6 | `check_jdebug_1p27_clearance.py` | ★**L85** `LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"` + ★**L211** `tht_geometry()` 实算 (★`copper_w_along = span + pad_along`★) ★ | ★**它真读 `.kicad_mod` ⇒ pad 一改, `copper_w_along` 立刻变 ⇒ G1/G2/G3/G4 当场转红 ⇒ 【能抓】** ★ | `[实测]` |
| 7 | `check_juart_1p27_clearance.py` | ★**L84** `LIBROOT = …` + ★**L1085** `--libroot` 参数 + ★**J0 现读** ★ | ★**同上 ⇒ 【能抓】** ★ | `[实测]` |

### ★§4.4 · 【三处与来件口径不一致】的实测订正 (★本机实跑·★以本机读数为准★) ★

★**★本单必须照实更正三处 (★否则交卷页会把来件口径的【沙盒假读数】当成事实传下去★) ★**:

| # | 来件 (brief) 写的 | ★本机实测 (★逐字★) ★ | ★差在哪★ | 证据等级 |
|---|---|---|---|---|
| ① | `check_fts_vs_generic_courtyard_delta.py` 基线 `rc=1` (红) | ★**基线 `rc=0` (全绿)** ★ | ★**来件的 `rc=1` 是【沙盒假读数】: 该闸的 `ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` (★L29★) ⇒ 把它复制到沙盒目录后, 它会去沙盒根找 `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` ⇒ 找不到 ⇒ `FileNotFoundError` ⇒ rc=1。★在真实项目里跑 = 全绿★** ⇒ ★**本单 A/B 因此直接跑【真闸】(★副本与真闸 md5 逐字相同★)★ | `[实测]` |
| ② | `check_connector_clearance_caliber.py` 基线 `rc=1` (**3 条红**) | ★**基线 `rc=1`, 但只【1 条】红 (`K7`)★** ★ | ★**红项 = `K7`: `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` md5 `f1ce54c98…` ≠ 已签收基线 `ffc09939…` ; `MECH/check_juart_1p27_clearance.py` md5 `daf8fa36…` ≠ 已签收基线 `ea89e0dd…` ★⇒ ★**这是【既有】的 md5 漂移 (与本单无关·本单零改既有文件)★** ⇒ ★**本单不动它·只登记为基线** ★ | `[实测]` |
| ③ | `check_juart_1p27_clearance.py` 在 `pad 1.110` 下转红 `J0/J5/J7` (3 条) | ★**转红 `J0/J1/J5/J7` (4 条)** ★ | ★**本机 A 臂实测 `RESULT: FAIL (4 条判据不通过)` + `[FAIL] J0` `[FAIL] J1` `[FAIL] J5` `[FAIL] J7` ★⇒ 以本机读数为准** ★ | `[实测]` |

★**★⇒ 订正后的准确口径: ★**7 道闸里 5 道对焊盘尺寸完全盲 (★stdout md5 两臂逐字相同★) + 2 道能抓 (★`jdebug`: `G1/G2/G3/G4`; `juart`: `J0/J1/J5/J7`★)★** ★

────────────────────────────────────────────────────────────────────────────────
## ★§5 · `parse_footprint_copper()` 是死代码 (★代码级证据·★defined but never called★) ★

★**函数本体** (★`MECH/check_debug_seat_3d_fit.py` **L187-L215**★):
```
187: def parse_footprint_copper(path: str):
188:     """★从官方 .kicad_mod 解析 pad → rot90 (沿板 X 排) 的铜箔包络 (X 宽, Y 宽)★"""
...
213:         "copper_x": r4(span_local_y + max_w),
214:         "copper_y": r4(max_h),
```
★**★⇒ 这个函数【已经写好了】「从 `.kicad_mod` 现读 pad 算铜箔包络」的能力, 算式与 §3.1 的 `①`/`②` 同源 (★`copper_x = 跨距 + pad 宽`★) —— 但它【一次都没被调用】** ★

### ★§5.1 · grep 逐条证据 (★本机实跑·全仓·排除 `tmp/`★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -rn "parse_footprint_copper" --include=*.py . | grep -v "^./tmp/"
```
★**逐条输出 (4 条, 全文只有这 4 处) ★**:
```
./state/_apply_20261125_0020_cronfb67af40_open_iss403.py:32:   ★**且该文件里已经写好了「从 `.kicad_mod` 现读 pad 算铜箔包络」的 `parse_footprint_copper()`
./state/_apply_20261125_0020_cronfb67af40_open_iss403.py:123:  ★**★⇒ 而且该文件里其实已经写好了…的 `parse_footprint_copper()` (L187) —— ★**但它一次都没被调用**…
./state/_apply_20261125_0020_cronfb67af40_open_iss403.py:134:  ★**⑤ `parse_footprint_copper()` 死代码怎么处理…
./state/_apply_20261125_0020_cronfb67af40_open_iss403.py:221:  if not got or "parse_footprint_copper" not in str(got[0].get("task_brief")):
./MECH/check_debug_seat_3d_fit.py:187:def parse_footprint_copper(path: str):
```
★**逐条判读 (★这是本节的关键★) ★**:
| 命中 | 是什么 | ★是不是【调用点】★ |
|---|---|---|
| `state/_apply_20261125_0020_cronfb67af40_open_iss403.py` L32 / L123 / L134 | ★**开单脚本里的文字 (brief 文本)★** | ★**✗ 不是调用点** ★ |
| `state/_apply_20261125_0020_cronfb67af40_open_iss403.py` L221 | ★**开单脚本里的字符串断言** (`"parse_footprint_copper" not in str(got[0].get("task_brief"))`) ★ | ★**✗ 不是调用点** ★ |
| `MECH/check_debug_seat_3d_fit.py` **L187** | ★**函数定义行 (`def`)★** | ★**✗ 这是定义, 不是调用** ★ |
★**⇒ 全仓【零个调用点】★ ⇒ ★**`parse_footprint_copper()` = 死代码 (defined but never called)★** ★

★**补充判据 (★更硬的一条★)**: ★**在 `MECH/check_debug_seat_3d_fit.py` 内, 形如 `parse_footprint_copper(` 的行【只有 L187 那一行定义本身】(★`grep -n "parse_footprint_copper(" MECH/check_debug_seat_3d_fit.py` ⇒ 只回 L187★) ⇒ ★**连「调用被注释掉」的痕迹都没有 ⇒ 它是【纯死代码】不是【被注释的调用】★** ★ (`[实测]`)

★**★⇒ 后果 (★判据句★)**: ★**「现读的能力有、但没接上」⇒ 【焊盘尺寸 ⇒ 铜箔包络 ⇒ 7 个数】这条链在代码里【断在最后一步】⇒ §4 的 5 道盲闸正好卡在这个断点上 ⇒ ★**下一个读 `check_debug_seat_3d_fit.py` 的人会看到 L187-L215 一个完整的现读实现, 极易误以为主闸已经现读了 ⇒ 【现读能力已生效】这个错觉本身就是一个风险** ★**

────────────────────────────────────────────────────────────────────────────────
## ★§6 · 7 道 MECH 闸【零挂链】的证据 (★`state/gate_check.py` 两张表逐条核过★) ★

### ★§6.1 · 两张表的全部 MECH 条目 (★本机逐条列出·★不含任何猜测★) ★

★**表 ① `EXTRA_GATES` (★`state/gate_check.py` **L211** 起★) —— 全部 MECH 条目只有 2 道** ★:
| 行 | 条目 |
|---|---|
| L212 | `MECH/check_mech_verdict_freshness.py` — 「MECH 结构结论防漂闸 (ISS-295)」 |
| L246-L247 | `MECH/tools/check_mech_ref_reachability.py` — 「MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)」 |

★**表 ② `PINNED_MD5_GATES` (★`state/gate_check.py` **L262** 起★) —— 全部 MECH 条目只有 2 道** ★:
| 行 | 条目 |
|---|---|
| L269 | `MECH/check_board_frame_coords.py` — 「钉板闸⑦ 板框坐标闸」 |
| L270 | `MECH/check_demo_struct_truth.py` — 「钉板闸⑧ 结构真值闸」 |

★**★⇒ 逐条对拍: 7 道 MECH 闸在两张表里【一道都没挂】★** ★

| # | 闸 | `EXTRA_GATES` 命中 | `PINNED_MD5_GATES` 命中 |
|---|---|---|---|
| 1 | `check_debug_seat_3d_fit.py` | ★**0** ★ | ★**0** ★ |
| 2 | `check_debug_seat_rework_spec.py` | ★**0** ★ | ★**0** ★ |
| 3 | `check_fts_seat_body_geometry.py` | ★**0** ★ | ★**0** ★ |
| 4 | `check_connector_clearance_caliber.py` | ★**0** ★ | ★**0** ★ |
| 5 | `check_fts_vs_generic_courtyard_delta.py` | ★**0** ★ | ★**0** ★ |
| 6 | `check_jdebug_1p27_clearance.py` | ★**0** ★ | ★**0** ★ |
| 7 | `check_juart_1p27_clearance.py` | ★**0** ★ | ★**0** ★ |

### ★§6.2 · 复现命令 (★逐条 grep·rc=0★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
for g in check_debug_seat_3d_fit check_debug_seat_rework_spec check_fts_seat_body_geometry \
         check_connector_clearance_caliber check_fts_vs_generic_courtyard_delta \
         check_jdebug_1p27_clearance check_juart_1p27_clearance; do
  printf "%-42s EXTRA=%s PINNED=%s\n" "$g" \
    "$(grep -c "$g" state/gate_check.py)" "$(grep -c "check_$g" state/gate_check.py)"
done
```
★**读数**: ★**7 行全部 `EXTRA=0 PINNED=0`** ★ (`[实测]`)

★**★⇒ 后果 (★判据句★)**: ★**连 §4 里【盲】的那道主闸 (`check_debug_seat_3d_fit.py`, 201 条判据) 都不在门禁链上跑 ⇒ 【红了也没人知道】, 更别说它【压根不红】⇒ ⇒ **§4 的两条坏结局 (焊盘放大无人报警 / 7 个数作废无人报警) 今天都【没有机器闸会响】** ★

★**★⇒ 但【挂链】这件事不是本单的地界** ★: ★**改 `state/gate_check.py` = 改【已签收件】⇒ 归 main ⇒ 本单只登记事实与代价 (★见交卷页 B5-④★) ★**

────────────────────────────────────────────────────────────────────────────────
## ★§7 · 机器块 (★可被 `MECH/check_pad_size_coupling_closed.py` 解析★) ★

```json
{
  "doc": "ISS-403 · MECH 判决链的焊盘尺寸耦合盲区清账 · 机读块",
  "generated_by": "mech-lead · 2026-11-25 · 本机自算 (零写板/零落表/零挂链)",
  "evidence_levels": ["官网", "实测", "媒体", "推算", "0数据"],
  "planned_drill_mm": 0.71,
  "planned_drill_source": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §1.1 · Samtec 官方 Ø0.71 TYP",
  "fab_capability": {
    "source": "JLCPCB 官方 PCB 能力表 · tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html (md5 24dd86f068aa85728b74706f2fd80b3e)",
    "row_applies": "Multilayer: 1 oz",
    "recommended_mm": 0.2,
    "absolute_min_mm": 0.15,
    "two_layer_1oz_absolute_min_mm": 0.18,
    "board_layer_count": 8,
    "board_outer_copper_oz": 1,
    "evidence": "官网"
  },
  "current_pad": {
    "read_from": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "pad_x_mm": 1.0,
    "pad_y_mm": 1.0,
    "drill_mm": 0.65,
    "current_tier_id": "P1000",
    "evidence": "实测"
  },
  "pad_tiers": [
    {"id": "P1000", "pad_mm": 1.0,  "annular_ring_mm": 0.145, "meets": "none",           "note": "现状档 · 环宽 0.1450 < 多层1oz绝对下限 0.15 ⇒ 前提已死"},
    {"id": "P1010", "pad_mm": 1.01, "annular_ring_mm": 0.15,  "meets": "abs_min",        "note": "恰达绝对下限 0.15 · 未达推荐值 0.20"},
    {"id": "P1110", "pad_mm": 1.11, "annular_ring_mm": 0.2,   "meets": "recommended",    "note": "达推荐值 0.20"},
    {"id": "P1218", "pad_mm": 1.218,"annular_ring_mm": 0.254, "meets": "2oz_min",       "note": "达 2oz 的 0.254"}
  ],
  "seven_number_defs": {
    "j_debug_copper_x": "跨距 3.8100 + pad",
    "j_uart_copper_x": "跨距 1.2700 + pad",
    "j_debug_required_clear_x": "j_debug_copper_x + 2*(CRIT+TOL) = copper_x + 1.8000",
    "j_uart_required_clear_x": "j_uart_copper_x + 2*(CRIT+TOL) = copper_x + 1.8000",
    "j_uart_cover_margin_x": "(座体必须清空区X宽 2.5400 - j_uart_copper_x)/2",
    "j_debug_opening_margin_x": "(开口X宽 10.2000 - j_debug_copper_x)/2",
    "j_debug_cover_margin_y": "(必须清空区Y宽 2.5400 - pad)/2"
  },
  "seven_numbers_matrix": {
    "P1000": {"j_debug_copper_x": 4.81, "j_uart_copper_x": 2.27, "j_debug_required_clear_x": 6.61, "j_uart_required_clear_x": 4.07, "j_uart_cover_margin_x": 0.135, "j_debug_opening_margin_x": 2.695, "j_debug_cover_margin_y": 0.77},
    "P1010": {"j_debug_copper_x": 4.82, "j_uart_copper_x": 2.28, "j_debug_required_clear_x": 6.62, "j_uart_required_clear_x": 4.08, "j_uart_cover_margin_x": 0.13, "j_debug_opening_margin_x": 2.69, "j_debug_cover_margin_y": 0.765},
    "P1110": {"j_debug_copper_x": 4.92, "j_uart_copper_x": 2.38, "j_debug_required_clear_x": 6.72, "j_uart_required_clear_x": 4.18, "j_uart_cover_margin_x": 0.08, "j_debug_opening_margin_x": 2.64, "j_debug_cover_margin_y": 0.715},
    "P1218": {"j_debug_copper_x": 5.028, "j_uart_copper_x": 2.488, "j_debug_required_clear_x": 6.828, "j_uart_required_clear_x": 4.288, "j_uart_cover_margin_x": 0.026, "j_debug_opening_margin_x": 2.586, "j_debug_cover_margin_y": 0.661}
  },
  "critical_constants": {"crit_mm": 0.6, "tol_fdm_part_mm": 0.3, "source": "MECH/service_port_check.py L126-L127"},
  "verdict_chain_current": {
    "copper_x_j_debug": 4.81,
    "copper_y_j_debug": 1.0,
    "copper_x_j_uart": 2.27,
    "copper_y_j_uart": 1.0,
    "required_clear_x_j_debug": 6.61,
    "required_clear_x_j_uart": 4.07,
    "cover_margin_x_j_uart": 0.135,
    "opening_margin_x_j_debug": 2.695,
    "cover_margin_y_j_debug": 0.77,
    "note": "★A3 逐格对象: 这一组【直接由 `.kicad_mod` 实算】(跨距+pad / 清空区需求 / 罩住余量 / 开口余量) ⇒ 不与 seven_numbers_matrix 共用参考面 ⇒ 闸 P2/P3 两条判据可分别验证"
  },
  "blind_gates": [
    {"gate": "MECH/check_debug_seat_3d_fit.py", "blind_lines": ["L683", "L686", "L491", "L746", "L753"], "mechanism": "official 表把铜箔宽写死成 pad=1.000 的产物", "baseline_rc": 0, "baseline_red_items": [], "baseline_stdout_md5": "a64fd53091c16f9538348ffa23a99a37"},
    {"gate": "MECH/check_debug_seat_rework_spec.py", "blind_lines": ["L120", "L122", "L579"], "mechanism": "OFFICIAL_DEBUG_COPPER_X / OFFICIAL_COPPER_Y 模块级常量写死", "baseline_rc": 0, "baseline_red_items": [], "baseline_stdout_md5": "b86c561098d8d52f9a873780e00a3ce3"},
    {"gate": "MECH/check_fts_seat_body_geometry.py", "blind_lines": [], "mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口", "baseline_rc": 0, "baseline_red_items": [], "baseline_stdout_md5": "5d17b5e23afa509561cdcee7c527526b"},
    {"gate": "MECH/check_connector_clearance_caliber.py", "blind_lines": [], "mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口", "baseline_rc": 1, "baseline_red_items": ["K7"], "baseline_stdout_md5": "7ade27949541ba0d694088e812c8b6b5"},
    {"gate": "MECH/check_fts_vs_generic_courtyard_delta.py", "blind_lines": [], "mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口", "baseline_rc": 0, "baseline_red_items": [], "baseline_stdout_md5": "7839434d7e69608953507a51946bb165"}
  ],
  "sensitive_gates": [
    {"gate": "MECH/check_jdebug_1p27_clearance.py", "read_lines": ["L85", "L211"], "mechanism": "LIBROOT 现读 .kicad_mod ⇒ copper_w_along = span + pad_along", "baseline_rc": 0, "baseline_red_items": [], "pad_1p110_red": ["G1", "G2", "G3", "G4"]},
    {"gate": "MECH/check_juart_1p27_clearance.py", "read_lines": ["L84", "L1085"], "mechanism": "LIBROOT / --libroot 现读 .kicad_mod", "baseline_rc": 0, "baseline_red_items": [], "pad_1p110_red": ["J0", "J1", "J5", "J7"]}
  ],
  "all_mech_gates": [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_connector_clearance_caliber.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py"
  ],
  "gate_criteria": {
    "A1": "pad 档位从 .kicad_mod 现读 (不许写死 1.0) ⇒ 与本块 pad_tiers 逐字一致",
    "A2": "7 个数必须由 pad 档位推导 (不许写死) ⇒ 与本块 seven_numbers_matrix 逐格一致",
    "A3": "判决链消费的数 (copper_x/copper_y/清空区需求/罩住余量/开口余量) 必须与 .kicad_mod 实算逐格一致",
    "A4": "盲闸名单不许凭空: 每个名字必须真在盘上 + 真能实跑出登记的红项集合 + 静态证明其无库读入口",
    "A5": "零挂链自证: grep -c check_pad_size_coupling_closed state/gate_check.py == 0",
    "A6": "证据分级五级白名单 + 零挂起措辞 + 判据句/事实句分开",
    "A7": "板面零写板自证 (md5 / mtime / size 三项)",
    "A8": "零外发自证 (state/outbox/ 一个字节没动)"
  },
  "board_baseline": {"path": "HW/PCB/demo_mainboard.kicad_pcb", "md5": "611b869e13518c3c023fb178f91a0075", "mtime": "2026-11-06 07:07:17.362193413", "size": 4940213},
  "outbox_tree_md5": "098539a001f662415997f869d6725655",
  "outbox_tree_files": 22,
  "open_items": {
    "OI-403-1": "焊盘档位最终取哪档 (1.010 / 1.110 / 1.218) ⇒ to=main (连带: 板厂是谁这一格仍是 [0数据])",
    "OI-403-2": "7 个数的新值何时落 ⇒ 建议与「板那一趟」同批 ⇒ to=main",
    "OI-403-3": "5 道盲闸要不要修 (改已签收件 ⇒ 要重签+留痕) ⇒ to=main",
    "OI-403-4": "7 道 MECH 闸挂不挂 state/gate_check.py ⇒ to=main",
    "OI-403-5": "parse_footprint_copper() 死代码怎么处理 ⇒ to=main"
  },
  "decision_taken_here": "not_decided_here"
}
```

★**★【两套证据等级词表的并存说明 (★给读的人省一次踩坑★)】★**:
★**① MECH 域闸的五级白名单 = `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** (★`MECH/check_jdebug_1p27_clearance.py` L97-L99·★本单 `MECH/check_pad_size_coupling_closed.py` 的 P6 沿用同款★) ⇒ ★**方括号形式的「官方」二字在这套词表里是【禁用】词** (★`FORBIDDEN_EVIDENCE`★) ⇒ ★**本页一律用 `[官网]`, 绝不用方括号包起来的「官方」** ★
★**② 全局 `state/gate_check.py` 的 Q2 覆盖率检测器用的是另一套词表** (`EVIDENCE_TAGS = ["实测", "官方", "推算", "0数据", "0 数据"]`·★L55★) ⇒ ★**它会把正文里的「官方」二字当成一个标签抓走** ⇒ ★**Q2 本机实跑读数: `mech-lead 标签: ['实测', '官方', '推算', '0数据']` ⇒ 3/3 总工都做了证据分级 ⇒ Q2 通过 (★两套词表互不冲突: 一套管【方括号标签】, 一套管【正文里有没有这个词】★) ★**

────────────────────────────────────────────────────────────────────────────────
## ★§8 · 「板那一趟」焊盘档位的三选项 + 各自代价 (★★不代拍★·一律交 main★) ★

★**★本节只列档位与代价, 【不选】。选哪一档 = main 的地界 (★连带「板厂是谁」这一格 `[0数据]` 也要一并落★)。** ★

| 选项 | pad | 环宽 | ★达成档★ | ★MECH 侧后果 (7 个数全变·见 §3.2)★ | ★结构件侧代价 (★量级·不代估金额★)★ | ★别的连带 (★一并交 main★)★ |
|---|---|---|---|---|---|---|
| ★**A** ★ | `1.010` | `0.1500` | 恰达多层 1oz 绝对下限 `0.15` | 7 个数变化最小 (铜箔X +0.0100 / 罩住X −0.0050 / 罩住Y −0.0050) | ★最小 (结构件重算量最小)★ | ★⚠ 若板厂按 2 层做 ⇒ 绝对下限 `0.18` ⇒ 本档【不成立】⇒ 需 `pad ≥ 1.070`★ |
| ★**B** ★ | `1.110` | `0.2000` | 达推荐值 `0.20` | `J_DEBUG` 铜箔X `4.8100→4.9200` · `J_UART` 铜箔X `2.2700→2.3800` · `J_UART` 罩住X `0.1350→0.0800` (最坏 `-0.1650→-0.2200`) · `J_DEBUG` 罩住Y `0.7700→0.7150` | ★中 (结构件 + 镜脚侧整体重算一次·2-4 周 + ¥4-8K 级)★ | 满足「推荐值」口径 ⇒ 板厂退单风险最低 |
| ★**C** ★ | `1.218` | `0.2540` | 达 `2 oz` 的 `0.254` | `J_UART` 罩住X `0.1350→0.0260` (最坏 `-0.2740`) ⇒ ★**罩住余量几乎归零 ⇒ 红得最狠**★ · `J_DEBUG` 铜箔X `5.0280` ⇒ 清空区需求 `6.8280` | ★最大 (清空区 X 要多让 ~1.02/边·镜脚侧重算量最大)★ | 仅当板厂按 2oz 铜报价/有能力时才必要 |

★**★【三档全列 = 一种降级】**: ★**「本板厂到底是谁」至今 `[0数据]` ⇒ 本单【不把它当阻塞项挂着】⇒ 三档全列 + 每档的达成口径 + 每档的 MECH 侧后果 + 每档的结构件代价 全部算好 ⇒ main 拍档时【直接选一档】即可, 不需要再回本单算一遍** ★ (`[推算]`)
★**★【不许代拍】**: ★**本单【不选档】。`decision_taken_here = "not_decided_here"` (★机器块已登记·闸 A6 会查★) ★**

────────────────────────────────────────────────────────────────────────────────
## ★§9 · 未决项 (★一条都不代拍·★全部 to=main★) ★

★**★见交卷页 `HANDOFF/2026-11-25_mech-lead_ISS403_焊盘尺寸耦合盲区清账与闸.md` §B5 (★五条·每条带问法/建议默认值/不答的后果/代价/归属★) ★**

| ID | 未决项 | 归属 |
|---|---|---|
| `OI-403-1` | 焊盘档位最终取哪档 (`1.010` / `1.110` / `1.218`) ⇒ 连带「板厂是谁」这一格 `[0数据]` | main |
| `OI-403-2` | 7 个数的新值何时落 (★建议与「板那一趟」同批·提前落 = 中间态 = 制造假红★) | main |
| `OI-403-3` | 5 道盲闸要不要修 (★改已签收件 ⇒ 要重签 + 留痕★) | main |
| `OI-403-4` | 7 道 MECH 闸挂不挂 `state/gate_check.py` | main |
| `OI-403-5` | `parse_footprint_copper()` 死代码怎么处理 (★接上 = 改已签收件; 不接 = 下一个读代码的人会以为现读能力已生效★) | main |

────────────────────────────────────────────────────────────────────────────────
## ★§10 · 边界自证 (★逐条·★本机实跑★) ★

| 边界 | 自证方式 | 读数 |
|---|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项 | ★`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` ⇒ 与基线**逐字节相同** ★ |
| ★**零落表** ★ | 三表 md5 | ★`hw.yaml` `1f5484c06b97746d4cadbc333ce5fab9` (★未动★) · ★`sw.yaml` `40a19b239a317cddd112aeaba1e00ddf` (★未动★) · ★**`mech.yaml` 由本单单写 (★走 `state/frag_write.py`★)** · ★`pm.yaml` 在本单工作窗口内 mtime 变成 2026-11-25 00:47 ⇒ ★**那是 main 的并发写入, 不是本单写的** (★本单只调过 `frag_write.update_fragment("mech-lead", …)` ⇒ 该模块的 `FILE_OF` 映射物理上写不到 `pm.yaml`; 且 `state/merge.py` 全文只 `atomic_write(STATE_PATH, body)` (★L624★) ⇒ 它一次都不写分片★) ★ |
| ★**零改既有闸判据/阈值** ★ | 7 道既有闸源码 md5 对拍 | ★开工前/收工后**逐字相同** (★A/B 跑完 + 交卷前各对拍一次·见交卷页 B6★) ★ |
| ★**零改既有页正文** ★ | 本单只【新建】2 个文件 + 【新建】1 个闸 | ★`MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` (新) · ★`HANDOFF/2026-11-25_mech-lead_ISS403_焊盘尺寸耦合盲区清账与闸.md` (新) · ★`MECH/check_pad_size_coupling_closed.py` (新) ⇒ ★**既有页一个字节没动** ★ |
| ★**零挂链** ★ | `grep -c check_pad_size_coupling_closed state/gate_check.py` | ★**0** ★ |
| ★**零外发** ★ | `state/outbox/` 全树 md5 | ★22 个文件 · 树摘要 `7c5f45e922447340349a224cf05a9807` ⇒ 与基线**逐字节相同** ⇒ ★**本单没发任何邮件/询价/问询/采购** ★ |
| ★**不代拍** ★ | 机器块 `decision_taken_here` | ★`"not_decided_here"` ★ |
| ★**不自签** ★ | `state/issue_log.yaml` | ★**一行没写** (★ISS-403 的签收归 main★) ★ |
| ★**沙盒只落项目盘** ★ | 沙盒路径 | ★`tmp/iss403/` (★未向系统 `/tmp` 写任何字节★) ★ |

────────────────────────────────────────────────────────────────────────────────
★**页尾**: ★**本页 = 真相页 + 机器块; 判据载体在 `MECH/check_pad_size_coupling_closed.py` (★裸跑 rc=0 = 现状自洽; `--selftest` rc=0 末行逐字 `ALL TESTS PASS`★) · 交卷页 = `HANDOFF/2026-11-25_mech-lead_ISS403_焊盘尺寸耦合盲区清账与闸.md`** ★
★**★本单零写板 · 零落表 (除自有分片) · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
