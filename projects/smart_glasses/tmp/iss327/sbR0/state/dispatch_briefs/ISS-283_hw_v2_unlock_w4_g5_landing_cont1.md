★**ISS-283 · hw-lead 续做任务书 (cont1) —— ★★【V-2 落表解锁 + W-4 写法A 落表 + G-5 亮度档落表】★★ ★ (main · 2026-11-17 12:1x · cron `fb67af40` 队列自动派活 · ★**续做重派第 1 次**) ★**

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 12:1x · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-283 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 落表链侧 · 三件落表 + 三道收口** ★ ⇒ ★**零写板 · 零改判据阈值 · 不替老板拍板** ★
> ★**单号状态**: ★**仍是 `fixing`** (★续做重派不是新单★) · ★**派活日志已追加一条续做条目** ★

---

## ★★§0 · ★★这一趟是从哪儿断的 (★main 本 job 自己查盘 + 读 transcript, 不抄任何兄弟 job 的报告★) ★★

★**上一趟会话**: `agent:hw-lead:subagent:eeecf73f` (★11:42:49 → 12:07:26 · status=**timeout** · abortedLastRun=**true**★) ⇒ ★**被网关掐断, 不是自己交卷★**

★**transcript 最后 3 条 (原样)**:
- ★12:04:46 ★`Successfully replaced 1 block(s) in .../HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md`★ ⇒ ★**交卷单骨架刚建完就断了**★
- ★12:04:39 ★`started syntax OK`★ ⇒ ★**落表器最后一次改完代码 + 语法过**★
- ★12:07:24 ★`Command still running (session tender-reef, pid 740455)`★ ⇒ ★**最后一条 exec 没等到结果★** (★main 本 job 已实测: **pid 740455 现在已不存在** ⇒ 没有僵尸进程在改盘★)

★**⇒ 盘上现状 (main 本 job 12:0x 实测) ★**:

| 件 | 现状 | 判定 |
|---|---|---|
| ★**B1 守卫改动** ★ | ★`HW/check_land_row_anchors.py` 已改: ★`LANDING_AUTH` 授权通道 (★L280 `AUTH_BLOCK_RE` + L292 口径 + L1032 台账写入器★) · ★反向用例 T10~T16 已在 (★L1197~L1342★) · ★fail-closed 三条一条没动★ | ★**✅ 已落盘 · 不要重做**★ |
| ★**落表器侧授权块写入** ★ | ★`state/land_v_values.py` L1570~L1590 已写 `### ★★16.3 · 身份变更授权台账` (★含 `<!-- LANDING_AUTH:BEGIN/END -->` 块 + 旧身份/新身份 JSON 数组★) · L2454 已调 `HW/check_land_row_anchors.py --reanchor` ★ | ★**✅ 已落盘 · 不要重做**★ |
| ★**⑩-a 落表器自测** ★ | ★`logs/iss283/selftest_lv4.log` (★12:04★) 末行 = ★`✅ rc=0: ★落表器自测全过 (14 条) · 真盘零写入`★ ⇒ rc=0 ★ | ★**✅ 已修好 (V-3/V-4 已落过判定 + 用例 12 改判红)· 不要重做**★ |
| ★**三件落表 (A3 / B2 / B3)** ★ | ★**一条都还没落** ★ ⇒ ★**网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` 三件 md5 与 09:58 落表后完全一致★ ★ ⇒ ★**台账里也还没有 `LANDING_AUTH` 块★** | ★**❌ 未做 ⇒ 本单主要工作★** |
| ★**交卷单** ★ | ★`HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md` = ★**3188 B 骨架**★ (★B1 有进度 / B2·B3·⑩·⑪·③·收尾·自检 全「⏳ 进行中 / 待做」★) | ★**❌ 骨架级 ⇒ 要填满★** |
| ★**分片** ★ | ★`grep -c "iss283\|ISS-283" state/fragments/hw.yaml` = ★**0**★ ⇒ ★**零写**★ | ★**❌ 未写★** |
| ★**板** ★ | ★`611b869e…` · mtime 仍 ★`2026-11-06 07:07:17`★ ⇒ ★**零写板**★ | ★**✅ 保持★** |

★**⇒ 结论: 这是【半落地僵尸】—— ★工具侧两件已修好 (B1 + ⑩-a), 但【三件落表一件没落 + 交卷单是骨架 + 分片零写】★ ⇒ ★**从盘上继续, 不要从零重做 (★尤其不要重写 `HW/check_land_row_anchors.py` 的授权通道, 也不要重写 `state/land_v_values.py` 的 16.3 段★)★**

---

## ★★§1 · ★★还没做的 (★按这个顺序, B1 是 B2 的前置·别跳顺序★) ★★

### ★① · A3 落表 (★V-2 = 1★) ⇒ ★**B1 解锁后的第一刀**★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/land_v_values.py --decision V-2=1 --apply --boss-decision "2026-11-17 A3 = 1"
```
★**期望 rc=0** ⇒ ★落完 `D_ESD_USB_D` pad1 的网名 = `NET_USB_D_P_TYPEC` · ★**台账 §16.3 授权块自动写出** · ★**行号锚点守卫必须判绿 (PASS=310 · DRIFT=0 · RED=0) 且 registry 身份指纹被同步** ★
★**落完必须立刻复跑 (★rc 必须是【落表之后】跑的, 不许拿落表前的 rc 交卷★)**:
```bash
python3 HW/check_land_row_anchors.py            # 期望 rc=0 (PASS=310)
python3 HW/check_land_row_anchors.py --selftest # 期望 rc=0 (★条数只许增不许减★)
python3 HW/check_netlist_selfconsistency.py     # 期望 rc=0
```

### ★② · B2 落表 (★W-4 写法A = `Q_PG` pad1 ↔ pad3 网互换★)
★**老板已拍**: ★写法 A = ★**S=BAT_SW / D=ON / G=PG**★ ⇒ ★**pad1 = PWR_GOOD (G) · pad2 = BAT_SW (S) · pad3 = PWR_ON (D)**★ ⇒ ★**落表动作 = pad1 ↔ pad3 的网互换 + 三行 note 改写成写法A + 脚表/网表/BOM/原理图同步 + 台账痕迹** ★
★**★连带必须写进板那一趟的 S 步清单 (不许漏)**: ★板上 `Q_PG` land 是按旧接法画的 ⇒ ★**「板只改一次」那一趟必须重画 `Q_PG` 的 3 根线 (或改选 D-S-G 序器件 · 那也是换封装 · 同样是板那一趟)★ ★

### ★③ · B3 落表 (★G-5 亮度档 = 改 R 到 20 mA 档★)
★**老板已拍**: ★选项 ② = 改 R 到 20mA 档 ⇒ ★**`R_LED_R` = 68Ω ±1% (红) · `R_LED_G` = 55Ω ±1% (绿)**★ (★**68/55Ω 是准数, 150Ω 只有 ~5mA · 达不到老板批的 20mA 档★) ★
★**连带 (如实登记, 不许瞒)**: ★每颗功耗 2.2mW → 66mW (两颗 ≈ 0.13W 进电池账) · ★亮度 ×14 ⇒ ★**IEC 62471 分级要重算 ⇒ 登记 need 给 main (你只登记, 不代拍)★** · ★**这两个阻值进 BOM ⇒ 板那一趟重出 BOM + 投产包 (footprint 不变 ⇒ 不构成额外板改)★ ★

### ★④ · ⑩-b 落表后两道过期闸收口
```bash
python3 HW/check_onepass_preflight_coverage.py            # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest # 期望 rc=0 (反向一条不许少)
python3 HW/check_onepass_commit_order.py                  # D0 基线过期 ⇒ 期望 rc=0
python3 HW/check_onepass_commit_order.py --selftest       # 期望 rc=0
```
★**P5 两个现状探针的期望值跟盘面改** (★`B17_DNP_43` = `零标记 40 颗` · `B03_ULDO_S28_PAD3` = `18 条缺陷`★) · ★**P6 三个基线走「落表台账为准」口径, 不是把基线数字改成新值** ★

### ★⑤ · ⑪ HW 侧 C6 机制化收口 (`HW/check_board_frame_caliber.py`)
★**现状**: ★`HW/check_board_frame_caliber.py` ⇒ ★**rc=1 (C6 FAIL)**★ (★网表基线 `e06c1dd…` → 现值 `2f17650c…` / 脚表 `287e7861…` → `6ea65fec…`★) ⇒ ★**★归你 (HW 侧)★★**
★**★正确修法 (和 ISS-273 / ISS-275 同构)★**:
1. ★**C6 对【网表 / 脚表 / BOM】三件的判定改为「落表台账为准」**: ★盘上 md5 == `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该文件最新登记的 md5 ⇒ 绿★ ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 四项不齐 ⇒ 红** ★
2. ★**★★只把基线数字改成新值 = 下次落表又红一遍 ⇒ 判据的【取值来源】必须变, 不是【取值】变★** ⇒ ★**★不许用 `--update-baseline` 消红 (★那正是「换取值」不是「换来源」★)★★
3. ★**板 / `.kicad_pro` 两件的基线照旧写死 (★它们不归落表链管★) ⇒ 那两条一条不许动** ★
4. ★**反向用例 ≥4 条**: ① 台账有登记且一致 ⇒ 绿 ② 台账查不到 ⇒ 红 ③ 台账有登记但盘上 ≠ ⇒ 红 ④ 台账四项不齐 ⇒ 红 ★
5. ★**★另外一条机制建议 (「一次修好机制」逻辑)★**: ★**落表器的【落表后自检清单】要加上【全闸扫描】(★一次性跑完所有闸 + 把红的列出来 + 查有没有人认领★) ⇒ 否则每次落表都要 main 手工扫一遍, 而手工扫 = 一定会漏 (★今天就漏了两道·其中一道是 ISS-286 / MECH 侧, 另一道就是你这道 C6★)★ ★

### ★⑥ · ③ 板侧清单追加 §③ 三条 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`)
| # | 补什么 | 为什么 |
|---|---|---|
| ① | ★**V-2 的网改名**: `D_ESD_USB_D` pad1 网名 `USB_D_P_SRC` → `NET_USB_D_P_TYPEC` ⇒ ★**板上的 footprint 焊盘网名必须同趟改**★ | 漏改 ⇒ 网表与板对不上 |
| ② | ★**Q_PG land 重画** (pad1↔pad3 互换) ⇒ 板那一趟的 S 步清单里要有它 | B2 的直接后果 |
| ③ | ★**D− 侧 ESD 三件仍挂着** (R4×2 + R9): ① `D_ESD_USB_D` 只有 2 焊盘 ② D− 网上无任何 ESD 位号 ③ `D_ESD_USB_D`→`J_USB_C` 板面距离 **47.99mm** > 3.0mm 判据 ⇒ ★**这三条是 G1a-4 最后 4 条未落表项 (板侧) · 板那一趟清掉它们, G1a-4 才转绿**★ | G1a-4 现在红的就是这 4 条 |

★**验收**: ★`python3 HW/check_onepass_preflight_coverage.py` ⇒ ★**rc=0** ★ · `--selftest` ⇒ ★**rc=0 (反向一条不许少)** ★

### ★⑦ · 收尾 (★全部本机实跑, 贴现场 rc★)
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/land_v_values.py --selftest                      # 期望 rc=0 (★条数只许增不许减★)
python3 HW/check_land_row_anchors.py                            # 期望 rc=0 (PASS=310)
python3 HW/check_land_row_anchors.py --selftest                 # 期望 rc=0
python3 HW/check_netlist_selfconsistency.py                     # 期望 rc=0 (现状守卫)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # 期望 rc=1 (★还剩板侧那几条★)
python3 HW/check_onepass_preflight_coverage.py                  # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest       # 期望 rc=0
python3 HW/check_onepass_commit_order.py                        # 期望 rc=0
python3 HW/check_onepass_commit_order.py --selftest             # 期望 rc=0
python3 HW/check_board_frame_caliber.py                         # 期望 rc=0
python3 HW/check_board_frame_caliber.py --selftest              # 期望 rc=0
python3 state/merge.py && python3 state/gate_check.py           # 期望 rc=0 / rc=0 (Q1 18/18)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv \
       HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… 必须逐字节不变★★
```
★**★★红线**: ★**验收 rc 必须【在三件落表【之后】】再跑一遍** ⇒ ★**不许拿【落表之前】跑的 rc 当交卷证据 (★md5 会变 ⇒ 拿旧 rc 交卷 = 交假证据★)★ ★

### ★⑧ · 交卷单 + 分片 (★交卷单骨架已在 ⇒ 直接填, 不要另起一份★)
1. ★**交卷单** `HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md` (★B1~B6 六块齐全 + 三件落表各一段原样 rc + 反向用例 rc + 边界自证★)
2. ★**台账痕迹** `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★§16.3 授权块 + 新旧 md5 + 老板凭据★)
3. ★**分片** `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead` 原子写★ ⇒ ★**写完 `grep` 校验 `iss283` 在不在 (★现在 grep = 0, 一条都没写★)★) ★
4. ★**零自签 `state/issue_log.yaml`** (★签字是 main 的活★) · ★**零外发** ★

---

## ★★§2 · ★★边界 (★违反就是不合格★) ★★

★零写板 (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 一个字节不许动★) · ★零改既有判据阈值 · ★**不许弱化行号锚点守卫的 fail-closed 三条 (链头不唯一 / 链断 / 链头无单号 ⇒ 仍红)★** · ★**不许用 `--update-baseline` 之类「只改基线数字」的手法消红** ★ · ★不碰 `MECH/` / `SW/` 的分片与文件 (★**SW 侧那条红归 ISS-285 (sw-lead) ⇒ 不许你去改 `SW/`**★) · ★**`MECH/check_board_frame_coords.py` 那条 C4 归 ISS-286 (mech-lead, 在飞) ⇒ 不许你去改 `MECH/`** ★ · ★零外发 · ★**不替老板拍板 (★ESD 型号轴 + D− 侧仍待拍, 你不许顺手选型★)** ★ · ★**不自签 issue_log** ★ · ★不许把整份大文件读进来 (★只 grep 你要改的那几行★) ★

★**★SW 侧那条红不是你的活 (★重申, 上一趟已经说过一次★)★**: ★`SW/tools/timing_check.py` ⇒ rc=1 (68/71 · 3 条红) ⇒ ★**归 ISS-285 (sw-lead)· 已在飞** ⇒ ★**你只交叉引用** ★

---

## ★★§3 · ★★纪律 (★这项目的老教训★) ★★

★**交卷单第一件事就是 `write` 建骨架 (★**已在 ⇒ 直接填**)★** · ★**长任务一律 `nohup ... > logs/iss283/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因·★上一趟就是 12:07 被掐的★)★** · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★ · ★**★注意: `/tmp` 可能已满 (★别的单的沙盒占着★) ⇒ `--selftest` 跑不动就把 `TMPDIR` 指到项目盘 (★sw-lead 上一趟踩过这个坑: `Disk quota exceeded★)★

---

## ★★§4 · ★★原任务书全文 (★**第一件事 cat 全文, 别只读这份 cont1★)★★ ★

★**完整任务书 (★含 §①~§⑦ + ★⑩ 追加块★)**: ★**`state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing.md`** (★171 行 · 14346 B★) ⇒ ★**cat 一遍★**
★**★⑪ 追加块 (★main 2026-11-17 11:2x 实跑·落表后第三道【没人管的红】★)★**: ★**见下面 §5 全文 (★原样抄录, 一字未改★)★**

---

## ★★§5 · ★★⑪ 追加块全文 (★原样抄录自 `state/issue_log.yaml` 的 ISS-283 `task_brief`·一字未改★) ★★

★★**⑪ 再追加 (★2026-11-17 11:2x main 实跑·落表后第三道【没人管的红】被 main 抓出来★★)**

★**A1+A2 落表后, 全闸扫描抓出 3 道红, 其中 2 道当时【没有任何 issue 拥有】⇒ 已分别派单, 这道归你★**

| 闸 | 现象 | 归属 |
|---|---|---|
| ★**`HW/check_onepass_preflight_coverage.py`** ★ | ★**现已绿** (★基线已被重锚到落表后的真值★) | —— 已收 |
| ★**`HW/check_board_frame_caliber.py`** ★ | ★**rc=1 (C6 FAIL)**: ★**网表 md5 基线 `e06c1dd…` → 现值 `2f17650c…` / 脚表 `287e7861…` → `6ea65fec…` ⇒ 判红** ★ | ★**★归你 (HW 侧)★★** |
| ★**`MECH/check_board_frame_coords.py`** ★ | ★**rc=2 (C4)**: ★**网表 / 脚表 / BOM 三件基线全过期 ⇒ 判红** ★ | ★**已开 ISS-286 (mech-lead)★★** |
| ★**`state/land_v_values.py --selftest`** ★ | ★**rc=2 (崩)**: 用例 12 硬套 V-3/V-4 的旧值补丁而旧值已不存在 ⇒ `RuntimeError: 旧值出现 0 次` | ★**★归你 (⑩ 节已写)★★** |

★**★HW 侧那道 (C6) 的正确修法 (★和 ISS-273 / ISS-275 同构, 别只改基线数字★)**:
1. ★**C6 对【网表 / 脚表 / BOM】三件的判定改为「落表台账为准」**: ★**盘上 md5 == `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该文件最新登记的 md5 ⇒ 绿** ★ ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 四项不齐 ⇒ 红** ★
2. ★**★只把基线数字改成新值 = 下次落表又红一遍 ⇒ 判据的【取值来源】必须变, 不是【取值】变★** ★
3. ★**板 / `.kicad_pro` 两件的基线照旧写死 (★它们不归落表链管★) ⇒ 那两条一条不许动** ★
4. ★**反向用例 ≥4 条**: ① 台账有登记且一致 ⇒ 绿 ② 台账查不到 ⇒ 红 ③ 台账有登记但盘上 ≠ ⇒ 红 ④ 台账四项不齐 ⇒ 红 ★
5. ★**★另外一条机制建议 (★ISS-273 的同款「一次修好机制」逻辑★)**: ★**落表器的【落表后自检清单】要加上【全闸扫描】(★一次性跑完所有闸 + 把红的列出来 + 查有没有人认领★) ⇒ 否则每次落表都要 main 手工扫一遍, 而手工扫 = 一定会漏 (★今天就漏了两道★)** ★

★**★铁律复述 (★main 今天新学到的★)**: ★**落表成功 ≠ 全链绿 ⇒ 落表完必须扫一遍【所有以真源 md5 / 现状值为基线的闸与自测】** ★ ⇒ ★**今天的实例: 落表前全绿, 落表后 3 道红, 其中 2 道【落表前谁都没料到】(HW 板框口径 / MECH 坐标归一) ⇒ 若不是 main 手工全扫, 这两道会一直红到下一轮才被人撞见** ★
