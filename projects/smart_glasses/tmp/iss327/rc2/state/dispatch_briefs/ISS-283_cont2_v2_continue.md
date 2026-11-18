【项目总工派活 · 队列自动推进 · 闭环 ISS-283 (cont2 续做重派)】你是 硬件总工 (hw-lead)。

★★★【★★这是【续做重派】, 不是新单: 你上一趟 (会话 agent:hw-lead:subagent:adfd437a…, 12:1x~12:51) 被 abort, 交卷没成立 (★分片一个字节没写★)★★】★★
★★★⇒ main 2026-11-17 13:1x 实读盘面 + 实跑闸, 把【已落地 / 没做完 / 现在红的】三件事一次给你 ⇒ ★**不要重做已落地的, 不要凭印象, 按下面这份实测清单接着往下做** ★★★

★★【★① 上一趟【已经真落地】的 (main 本机实测, 不许重做·不许回退)】★★
· B1 · V-2 (A3=1) 落表解锁: ★**守卫改动已落盘** (`HW/check_land_row_anchors.py` · 新增 `--migrate-id-str` + T17/T18 · selftest 18/18) ★
· A3 (V-2=1) 真落 12:16:08 rc=0 ⇒ 网表 L417 的 net `USB_D_P_SRC` → ★**`NET_USB_D_P_TYPEC`** ★ · 台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` L1328~L1332 有 LANDING_AUTH 块 (ISS-283 · 凭据「2026-11-17 A3 = 1」) · registry `id_str`/`auth` 补齐
· ★**盘面现值 (main 13:1x 实测)**: 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…` ★**板 `611b869e…` + `.kicad_pro` `3e504d2b…` 逐字节未变** ★
· ★**这三件 md5 就是当前「链头」⇒ 你后面 B2/B3 再落表会动它们 ⇒ 每次落表前后都要重跑 C6 与 C4 两道闸 (★它们现在都是绿的·别弄红★)** ★

★★【★② 上一趟【没做完】的清单 (main 实读交卷单 + 实跑闸得出)】★★
⏳ **B2 · W-4 (P4/G-1) `Q_PG` 写法 A 落表** (S=BAT_SW / D=ON / G=PG ★**且 pad1↔pad3 的网要互换**★ ⇒ ★**DMP3098L 引脚序 1=G/2=S/3=D ⇒ 板那一趟必须重画 Q_PG 的 land**★)
⏳ **B3 · G-5 (P6/W-6) LED 亮度档落表** (★R_LED_R 1k→68Ω · R_LED_G 1k→55Ω = 20mA 档★)
⏳ **⑩ · 落表后两道过期闸收口** (preflight P5/P6 ⇒ `HW/check_onepass_preflight_coverage.py` · `HW/check_onepass_commit_order.py` D0)
⏳ **⑪ · HW 侧 C6 机制化** (`HW/check_board_frame_caliber.py` 判据改「落表台账为准」) ★★**改到一半 ⇒ 现在是红的 (见 ③)**★★
⏳ **③ · 板侧清单追加 §③ 三条** (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`)
⏳ **收尾 · 落表后全套 rc 复跑** (★验收 rc 必须落在三件落表之后, 不许拿落表前的 rc 交卷★)
⏳ **交卷自检 (边界复核)** + ★**分片 `state/fragments/hw.yaml` 一个字没写 (main 实测 grep iss283 = 0) ⇒ 交卷不成立** ★

★★★【★★③ 本轮最要紧的一件: ⑪ C6 那道闸【现在是红的】, 而且是 abort 前的半成品★★】★★★
★main 2026-11-17 13:1x 本机实跑 (原样 rc · 日志 `logs/iss283/c6_selftest_main_1312.log`)★:
· `python3 HW/check_board_frame_caliber.py` ⇒ ★**rc=0** (★主判据是绿的 ⇒ 判据没写坏★) ★
· `python3 HW/check_board_frame_caliber.py --selftest` ⇒ ★**rc=1 · 反向用例 12 条 · 失败 2 条** ★ ⇒ ★**这两条没抓住 ⇒ 就是「有漏网」★**:
  ① **⑤b**「落表台账里删掉 BOM 的登记行 ⇒ 应红」⇒ ★**自证改动 md5 `1ae6242a…` → `1ae6242a…` (★没改到★) ⇒ 突变函数根本没咬到目标那一处 ⇒ C6 自然还是绿的 ⇒ 这是【用例自身没写完】★★
  ② **⑤c**「落表台账里 BOM 的【新 md5】缺了 ⇒ 应红」⇒ ★**突变真改到了 (md5 `1ae6242a…` → `7f426857…`) 但 C6 仍 GREEN ⇒ 这是【判据真缺口】: C6 的「四项不齐」没覆盖到「BOM 新 md5 缺失」这一路** ★
  (⑤d 链断 / ⑤e 链头无单号 ⇒ PASS ✔ ⇒ ★**链头机制那部分已经写对了**★)
⇒ ★**要求**: ⑤b 的突变函数改成真咬到台账那一行 (删掉 BOM 的登记行) ⇒ 自证 md5 必须变化; ⑤c 必须让 C6 判红 ⇒ ★**若是判据真缺一路, 就补那一路 (★判据方向不许放宽: 合法落表仍要绿 · 偷换真源 / 台账被改坏仍要红★)** ★
⇒ ★★**不许把这两条用例删掉、或改成「预期绿」来凑绿** ★ ⇒ 改完 `--selftest` 必须 ★**rc=0 且 12 条一条没少 (★用例只许增不许减★)** ★
⇒ ★**沙盒落 workspace/tmp, 不要落 /tmp (★/tmp 是带 usrquota 的 tmpfs, 已满过 ⇒ 跑挂过一次★)** ★

★★【④ 板侧铁律 (一字不让)】★★
· ★**板 `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` = `3e504d2be83152e337949723e909be1b` ⇒ 这一趟你【不许写板】** ★
· ⇒ ★**B2 里那句「板那一趟必须重画 Q_PG 的 land」= 写进板侧清单 / 作业包, 不是本趟动板** ★ ⇒ ★**板改那一趟 = 「板只改一次」那一趟, 由 main 统一开** ★
· ⇒ ★**Gerber / 投产包一律不许用 (★板现在仍是「旧网表的板」★)** ★

★★【⑤ 边界】★★
· 零写板 · 零跑布线臂 · ★**零改既有判据阈值/方向** ★ · ★**不许改 `state/fragments/` 里别人的分片** ★ · ★**不许自签 issue_log (status 由 main 签)** ★
· 只写本单允许的文件 (HW/ 与自己的分片) ⇒ ★**不碰 SW/ 与 MECH/** ★
· ★**零外发** ★

★★【★⑥ 交卷纪律 ★】★★
· ★**写分片必须用 `state/frag_write.py`** (★禁止 open(p,"w")★) ⇒ ★**分片必须能 grep 到 `iss283`** ★
· 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md` ★**B1~B6 六块 + 收尾 + 交卷自检全填, 0 处「施工中/待填」残留** ★
· ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
· 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标

★★【★⑦ 额外纪律 (老板 2026-11-11 19:31 + 2026-11-12 02:02)★】★★
· ★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 / 任何对外沟通** ⇒ `state/outbox/` 里的草稿【一律不发】, 只作资料留档 ⇒ ★**没有「老板批一句可以发」这个选项** ★
· ★**凡标了「等原厂回信 / 等外部回复 / 待外部确认」的地方, 一律换成【自己网上查的结果 + 证据等级 + 查不到就写降级方案】⇒ 不许把外部依赖挂着当阻塞项** ★

--- 以下是 ISS-283 原任务书全文 (未改写) ---
★**续做重派 (★11:42~12:07 那一趟会话被掐 ⇒ 盘上已有半成品: 交卷单 3188 B 骨架 + B1 守卫授权通道已改 + 落表器 §16.3 授权块已写 + ⑩-a 落表器自测已 rc=0 ⇒ 【三件落表一件没落】⇒ 从盘上现状继续, 不要从零重做★)** ⇒ ★**完整续做任务书全文 = `state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing_cont1.md` (10413 B) ⇒ 第一件事先 cat 全文**★
★**原任务书全文** = `state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing.md` (14346 B · §①~§⑦ + ⑩ 追加块) ⇒ 也 cat 一遍★
★**★不许重做已落盘的两件**: B1 守卫授权通道 (`HW/check_land_row_anchors.py` · T10~T16) · 落表器授权块写入 (`state/land_v_values.py` §16.3) · ⑩-a 已落过判定 (用例 12 改判红)★
★**★剩下的是**: A3 真落 (`--decision V-2=1 --apply`) → B2 (Q_PG pad1↔pad3) → B3 (68Ω/55Ω) → ⑩-b (preflight P5/P6 + commit_order D0) → ⑪ (HW 侧 C6 改「落表台账为准」· ★不许 `--update-baseline`★) → ③ 板侧清单三条 → 收尾 rc (★必须落表之后才跑★) → 交卷单填满 (★骨架已在, 直接填★) → 分片 (★现在 grep = 0★)**★
★**ISS-283 · hw-lead 任务书 —— ★★【V-2 落表解锁 + W-4 写法A 落表 + G-5 亮度档落表】★★** ★ (main · 2026-11-17 10:1x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 10:1x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-283 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 落表链侧 · 三件**★ ⇒ ★**零写板 · 零改判据阈值 · 不替老板拍板**★

---

## ① 背景 (★main 本机实测, 原样 rc★)

★**老板 2026-11-17 09:49 拍板「按照你的建议执行」⇒ 8 条决策已落账** (★`state/fragments/pm.yaml` 的 `needs_from` 8 条 + 同 key 两条 ★) ⇒ ★**其中 3 件要你做** ★

★**A1 + A2 (V-3=E + V-4=680) 已经落了** ★: `python3 state/land_v_values.py --decision V-3=E --decision V-4=680 --apply --boss-decision "2026-11-17 A1 = E" --boss-decision "2026-11-17 A2 = 680"` ⇒ **rc=0** ⇒ 网表 L182/L183/L184 已落 `100k/60k/100nF` 必装 · L47/L48 已落 `680Ω ±1%` ⇒ 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (含老板凭据机器化留痕) ★

★**★ A3 (V-2=1) 落不下去 —— 这条是你要解的第一个死锁 ★★**:

```
$ python3 state/land_v_values.py --decision V-3=E --decision V-4=680 --decision V-2=1 --apply ...
★★ rc=1: 落表后有门禁不过 ⇒ 自动回滚: ★行号锚点守卫 (ISS-262 · 纯漂移自动重锚·期望 rc=0)★: rc=1
   ❌ d4_a417_value [netlist] ★行号没变 + 实体内容变了 (台账里那颗器件在本表里找不到了) ⇒ **红**: 器件被换/被删, 锚点已指向别的行★
   ❌ d4_a417_net / d4_a417_dnp / d4_a417_note / d9_esd_dual_claim   (★五条全在 L417 = D_ESD_USB_D 那行★)
✅ rc=0: 已从 state/.bak_land_v_values_v_20261117-095506 还原 7 个文件 (★工具自带回滚★)
```

★**根因 (★main 逐行读过 `HW/check_land_row_anchors.py` L390~L432★)**: ★**V-2 的落表动作 = 把 `D_ESD_USB_D` pad1 的网名由 `USB_D_P_SRC` 改成 `NET_USB_D_P_TYPEC`** ★ ⇒ ★**这改的是守卫的【实体身份 (ref + net)】⇒ 守卫判「器件被换/被删」⇒ RED ⇒ 落表器自回滚** ★
⇒ ★**不是落表内容错, 是【落表器 ↔ 行号锚点守卫】两个工具的接口没接上** ★
⇒ ★**★不准弱化守卫的 fail-closed 那几条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红)★** ★

---

## ② 要交的三件 (★每件都能独立验收★)

### ★B1 · ★★V-2 (A3 = 1) 落表解锁 (★最要紧★★)

★**目标**: ★**让「合法落表改 net 名」成为守卫认得的一条合法通道** ★ ⇒ ★**落完 V-2 后 `D_ESD_USB_D` pad1 的网名 = `NET_USB_D_P_TYPEC`, 而守卫判 PASS 并把 registry 的身份指纹同步更新** ★

★**建议做法 (★你比我有资格定细节, 但下面三条不许破★)**:
1. ★**合法通道的判据必须是【可机器查的授权证据】**: ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里能查到 (★落表单号 + 文件名 + 该行的旧身份 + 新身份★)** ★⇒ ★**查不到 ⇒ 仍 RED** ★
2. ★**不许把 RED 改成静默 PASS**: 合法通道必须**留痕** (★registry 里记「本次身份变更由哪个单号授权」★) ⇒ ★**台账被偷改 ⇒ 仍 RED (★守卫自带 `REGISTRY_SHA256` 防偷改, 那条不许动★)** ★
3. ★**不许放宽 fail-closed**: 链头不唯一 / 链断 / 链头无单号 ⇒ 仍红 ★

★**反向用例 (★至少 4 条, 每条都要贴原样 rc★)**:
| # | 构造 | 期望 |
|---|---|---|
| ① | ★**盘上网表那一行的 net 被改了, 但落表台账里查不到授权记录** ★ | **红** (★身份变了 + 无授权 ⇒ 仍红★) |
| ② | ★**落表台账里有授权记录 (单号 + 文件名 + 旧身份 + 新身份齐全) ⇒ 放行并同步 registry** ★ | **绿** |
| ③ | ★**授权记录里的单号在台账里查不到 / 四项不齐** ★ | **红** |
| ④ | ★**registry 被手改 (sha256 对不上)** ★ | **红** (★既有行为, 不许因本单破例★) |

★**交完 B1 后, 立刻真落 A3**:
```bash
python3 state/land_v_values.py --decision V-2=1 --apply --boss-decision "2026-11-17 A3 = 1"
```
⇒ ★**期望 rc=0** ⇒ ★**落完必须复跑: `HW/check_land_row_anchors.py` rc=0 (PASS=310 · DRIFT=0 · RED=0) · `HW/check_netlist_selfconsistency.py` rc=0 · `state/merge.py` + `state/gate_check.py` rc=0 · 受保护 5 件 md5 逐字节不变 (★板 `611b869e…` / `.kicad_pro 3e504d2b…` 尤其不许变★)** ★

### ★B2 · ★★W-4 (P4 / G-1) `Q_PG` 写法 A 落表 ★★

★**老板已拍**: ★**写法 A = S=BAT_SW / D=ON / G=PG** (★依据 ISS-244 实跑: 写法 A ⇒ PG 低时 VGS = −4.2V 导通 / PG 高时 −0.9V 关断 ⇒ 自洽; 写法 B ⇒ PG 高低都关 ⇒ 开机路径彻底不通★) ★

★**★但落的东西比「改 note」多一层 —— 这是 main 10:0x 读盘查出来的★★**:
| 项 | 盘上现状 | 写法 A 要求 |
|---|---|---|
| 落地件 | `DMP3098L` (SOT-23) ⇒ ★**引脚序 1=G / 2=S / 3=D**★ (`HW/check_part_selection_landed_crosscheck.py` L70) | — |
| pad1 | ★**PWR_ON (负载侧)**★ ⇒ 物理上是 **G 位** ⇒ ★**栅极接负载**★ | ★**pad1 = PWR_GOOD (G)**★ |
| pad2 | BAT_SW ⇒ 物理上是 **S 位** ✓ | BAT_SW (S) ✓ |
| pad3 | ★**PWR_GOOD (PG)**★ ⇒ 物理上是 **D 位** ⇒ ★**漏极接 PG**★ | ★**pad3 = PWR_ON (D)**★ |

⇒ ★**★所以 B2 = pad1 ↔ pad3 的网互换 (PWR_ON ↔ PWR_GOOD) + 三行 note 改写成写法 A + 脚表/网表/BOM/原理图同步 + 落表台账 + 锚点重锚★★**
⇒ ★**★连带 (★必须写进板那一趟的 S 步清单, 不许漏★): 板上的 Q_PG land 是按旧接法画的 ⇒ 「板只改一次」那一趟必须重画 Q_PG 的 3 根线 (★或改选 D-S-G 序器件 —— 那也是换封装, 同样是板那一趟★)★★**
⇒ ★**注意**: pad1↔pad3 互换 = ★**换 net ⇒ 又是【实体身份变了】⇒ B1 没做完之前 B2 也落不下去** ⇒ ★**⇒ B1 是 B2 的前置** ★

### ★B3 · ★★G-5 (P6 / W-6) LED 亮度档落表 ★★

★**老板已拍**: ★**选项 ② = 改 R 到 20 mA 档** ★ ⇒ ★**`R_LED_R` = 68Ω ±1% (红) · `R_LED_G` = 55Ω ±1% (绿)** ★
⇒ ★**★口径订正 (★main 主动纠正自己上一条消息, 你照 68/55Ω 做★)**: 我 09:4x 给老板写的「建议改 ≈150Ω」是 §A-补4 W-6 行的旧数 ⇒ ★**按 ISS-244 [官网] 级实测折算, 20mA 档的真值 = 红 68Ω / 绿 55Ω (150Ω 只有 ~5mA, 达不到老板批准的「20mA 档」)**★

★**连带 (★如实登记, 不许瞒★)**:
- ★**每颗功耗 2.2mW → 66mW (两颗 ≈ 0.13W 进电池账)** ★
- ★**亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算 ⇒ 登记成 need 给 main (★你只登记, 不代拍★)** ★
- ★**这两个电阻的值会写进 BOM ⇒ 板那一趟要重出 BOM + 投产包 (★但 footprint 不变 ⇒ 不构成额外板改★)** ★

---

## ③ 必须一起更新的三处 (★漏一处 = 板那一趟白跑★)

★**落表完 + 落表台账写好之后, 把下面两条补进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★板侧项全集页★) ⇒ 并重跑覆盖度闸** ★:

| # | 补什么 | 为什么 |
|---|---|---|
| ① | ★**V-2 的网改名**: `D_ESD_USB_D` pad1 网名 `USB_D_P_SRC` → `NET_USB_D_P_TYPEC` ⇒ ★**板上的 footprint 焊盘网名必须同趟改**★ | ★落表器自己的警告: 「漏改 ⇒ 网表与板对不上」★ |
| ② | ★**Q_PG land 重画** (pad1↔pad3 互换) ⇒ 板那一趟的 S 步清单里要有它 | ★B2 的直接后果★ |
| ③ | ★**D− 侧 ESD 三件仍挂着** (R4×2 + R9): ① `D_ESD_USB_D` 只有 2 焊盘 ② D− 网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上无任何 ESD 位号 ③ `D_ESD_USB_D`→`J_USB_C` 板面距离 **47.99mm** > 3.0mm 判据 ⇒ ★**这三条现在是 G1a-4 的最后 4 条未落表项 (★板侧) ⇒ 板那一趟清掉它们, G1a-4 才转绿**★ | ★G1a-4 现在红的就是这 4 条★ |

⇒ ★**验收**: `python3 HW/check_onepass_preflight_coverage.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 (反向一条不许少)** ★

---

## ④ 必跑的命令 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/land_v_values.py --selftest                      # 落表器自测 (期望 rc=0)
python3 HW/check_land_row_anchors.py                            # 行号锚点守卫 (期望 rc=0 · PASS=310)
python3 HW/check_land_row_anchors.py --selftest                 # 期望 rc=0
python3 HW/check_netlist_selfconsistency.py                     # 期望 rc=0 (现状守卫)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # 期望 rc=1 (★还剩板侧那几条★)
python3 HW/check_onepass_preflight_coverage.py                  # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest       # 期望 rc=0
python3 state/merge.py && python3 state/gate_check.py           # 期望 rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv \
       HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 + .kicad_pro 必须逐字节不变 (611b869e… / 3e504d2b…)★★
```

## ⑤ 交卷物 (★5 件★)

1. ★**交卷单 `HANDOFF/2026-11-17_hw-lead_ISS282_V2解锁与W4G5落表.md`** (★B1~B6 六块齐全 + 三件落表各一段原样 rc★) ★
2. ★**B1 的守卫改动** (★`HW/check_land_row_anchors.py` + 它的 `REGISTRY_SHA256` 同步 + 反向用例 4 条★) ★
3. ★**三件落表的台账痕迹** (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 新段 + 老板凭据 + 新旧 md5★) ★
4. ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 追加 §③ 三条 + 覆盖度闸复跑记录** ★
5. ★**分片** `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead` 原子写★) ★

## ⑥ 边界 (★违反就是不合格★)

★零写板 (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 一个字节不许动★) · ★零改既有判据阈值 · ★**不许弱化行号锚点守卫的 fail-closed 三条** ★ · ★不碰 `MECH/` / `SW/` 的分片与文件 (★只交叉引用★) · ★零外发 · ★**不替老板拍板 (★ESD 型号轴 + D− 侧仍待拍, 你不许顺手选型★)** ★ · ★**不自签 issue_log** ★ · ★不许把整份大文件读进来 (★只 grep 你要改的那几行★)★

## ⑦ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss282/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验自己的 key 在不在 (★`frag_write.py` 无锁 ⇒ 并发写会 lost-update★)** ★


---

## ★★⑩ 追加 (★2026-11-17 10:4x main 实跑·落表的直接后果·这两件归你一起收口★★)

★**A1+A2 落表后, 有两道闸当场变红 —— 都是【落表的正常后果】, 但必须收, 不许留红★**

### ★① `HW/check_onepass_preflight_coverage.py` ⇒ **rc=1** (★落表前是 rc=0★)

```
  FAIL  P5
     5 个现状探针: 清单里的现状值 == 盘面实测: ❌
     ❌ B17_DNP_43: 盘面实测 = '零标记 40 颗', 但清单 current_state 里没有这个值 ⇒ 清单过期
     ❌ B03_ULDO_S28_PAD3: 盘面实测 = '18 条缺陷', 但清单 current_state 里没有这个值 ⇒ 清单过期
  FAIL  P6
     受保护 5 件 md5 逐字节不变: ❌
     ❌ 网表 md5 2f17650cfbef48d5efd71821505c3343 ≠ 基线 e06c1dd633566aa44732762c2ff99d1c
     ❌ 脚表 md5 6ea65fecdf95902e47330083d140d455 ≠ 基线 287e7861a0d1007748d92d9fbecdd490
     ❌ BOM  md5 ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd ≠ 基线 94642d07a69e8d60dd2af57f69b93607
```

★**⇒ 收口动作 (★两条, 不许用「改判据让它绿」的办法★)**:
- ★**P5 = 清单现状值跟着盘面改**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 里 `B17_DNP_43` 的 current_state → `零标记 40 颗` (★落表后 DEMO_DNP 少 3 颗★) · `B03_ULDO_S28_PAD3` 的 current_state → `18 条缺陷` (★落表后 `--expect-resolved` 只剩 4 条, 全是板侧★) ⇒ ★**闸自己写的正确姿势: 「盘面变了 ⇒ 现状值跟着改 ⇒ 再跑闸」** ★
- ★**P6 = 受保护基线重锚**: 网表 / 脚表 / BOM 三件的基线 md5 ⇒ 改成刚落表的真值 (`2f17650c…` / `6ea65fec…` / `ea5f4f58…`) ⇒ ★**必须留痕 (★走 H-1 四项: 落表单号 + 文件名 + 新旧 md5★) ⇒ 出处 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16** ★ ⇒ ★**板 `611b869e…` 与 `.kicad_pro 3e504d2b…` 两个基线不许动 (★它们本来就没变★)** ★
- ★**⇒ 改完必须 `python3 HW/check_onepass_preflight_coverage.py` rc=0 + `--selftest` rc=0 (★反向一条不许少★)** ★

### ★② `state/land_v_values.py --selftest` ⇒ **rc=1 (★是崩, 不是红★)**

```
  File "state/land_v_values.py", line 1896, in run_selftest
    plan12.apply_patches()
  File "state/land_v_values.py", line 1390, in apply_patches
    txt = replace_after(txt, p.ctx, p.old, p.new, p.count)
RuntimeError: ★旧值出现 0 次 (期望 1 次)
```

★**⇒ 根因**: 落表器自测的用例 12 假设 V-3/V-4 **还没落** ⇒ 落表后旧值不存在 ⇒ 硬套补丁 ⇒ 崩 ⇒ ★**落表器的「已落过」检测只覆盖了 V-2 (D_ESD_USB_D), 没覆盖 V-3 / V-4** ★
★**⇒ 收口动作**: ★**给 V-3 / V-4 也加「已落过」判定** (★像 V-2 那样: 已落 ⇒ 拒绝重落 + 文案写【已落过】★) ⇒ ★**用例 12 改成对【已落过】状态判红, 不许再硬套补丁** ⇒ ★**`--selftest` 必须回到 rc=0** ★
★**★顺带**: 你 B1 做的「合法落表改 net 名」通道, ★**也要顺手把 V-3/V-4 的「已落过」语义理清** (★「合法落表」与「重复落表」是两件事, 不许混★) ★


---

## ★★⑪ 再追加 (★2026-11-17 11:2x main 实跑·落表后第三道【没人管的红】被 main 抓出来★★)

★**A1+A2 落表后, 全闸扫描抓出 3 道红, 其中 2 道当时【没有任何 issue 拥有】⇒ 已分别派单, 这道归你★**

| 闸 | 现象 | 归属 |
|---|---|---|
| ★**`HW/check_onepass_preflight_coverage.py`** ★ | ★**现已绿** (★基线已被重锚到落表后的真值★) | —— 已收 |
| ★**`HW/check_board_frame_caliber.py`** ★ | ★**rc=1 (C6 FAIL)**: ★**网表 md5 基线 `e06c1dd…` → 现值 `2f17650c…` / 脚表 `287e7861…` → `6ea65fec…` ⇒ 判红** ★ | ★**★归你 (HW 侧)★★** |
| ★**`MECH/check_board_frame_coords.py`** ★ | ★**rc=2 (C4)**: ★**网表 / 脚表 / BOM 三件基线全过期 ⇒ 判红** ★ | ★**已开 ISS-286 (mech-lead)★★** |
| ★**`state/land_v_values.py --selftest`** ★ | ★**rc=2 (崩)**: 用例 12 硬套 V-3/V-4 的旧值补丁而旧值已不存在 ⇒ `RuntimeError: 旧值出现 0 次` | ★**★归你 (⑩ 节已写)★★** |

★**★HW 侧那道 (C6) 的正确修法 (★和 ISS-273 / ISS-275 同构, 别只改基线数字★)**:
1. ★**C6 对【网表 / 脚表 / BOM】三件的判定改为「落表台账为准」**: ★**盘上 md5 == `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该文件最新登记的 md5 ⇒ 绿** ★ ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 四项不齐 ⇒ 红** ★
2. ★**★只把基线数字改成新值 = 下次落表又红一遍 ⇒ 判据的【取值来源】必须变, 不是【取值】变** ★
3. ★**板 / `.kicad_pro` 两件的基线照旧写死 (★它们不归落表链管★) ⇒ 那两条一条不许动** ★
4. ★**反向用例 ≥4 条**: ① 台账有登记且一致 ⇒ 绿 ② 台账查不到 ⇒ 红 ③ 台账有登记但盘上 ≠ ⇒ 红 ④ 台账四项不齐 ⇒ 红 ★
5. ★**★另外一条机制建议 (★ISS-273 的同款「一次修好机制」逻辑★)**: ★**落表器的【落表后自检清单】要加上【全闸扫描】(★一次性跑完所有闸 + 把红的列出来 + 查有没有人认领★) ⇒ 否则每次落表都要 main 手工扫一遍, 而手工扫 = 一定会漏 (★今天就漏了两道★)** ★

★**★铁律复述 (★main 今天新学到的★)**: ★**落表成功 ≠ 全链绿 ⇒ 落表完必须扫一遍【所有以真源 md5 / 现状值为基线的闸与自测】** ★ ⇒ ★**今天的实例: 落表前全绿, 落表后 3 道红, 其中 2 道【落表前谁都没料到】(HW 板框口径 / MECH 坐标归一) ⇒ 若不是 main 手工全扫, 这两道会一直红到下一轮才被人撞见** ★

--- 原任务书全文到此结束 ---

★**再强调一次本单 PCB 类口径 (main 口径)**: ★**本单 = 落表链侧 (网表/脚表/BOM) + 判据收口 + 板侧清单 ⇒ 零写板 / 零落表布线臂 / 板一个字节不许动** ★ ⇒ ★**「板只改一次」那一趟 (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出) 仍未启动, 不许在本单里偷偷开** ★
