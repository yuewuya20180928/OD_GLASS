# ISS-368 · mech-lead · 「板那一趟」E-9 · `D_LED_G` 换封装后 LED 落位带同趟重算 + 机器闸

★★**题**: ★**把「板那一趟」换官方 land 时【必须同一次重算】的那组 LED 落位带/块数, 做成【逐件可执行的重算作业包 + 一条机器闸 + 沙盒重扫预演】** ★★
★★**类别**: ★**纯分析 + 作业包 + 新建闸 + 沙盒重扫 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发** ★★

---

## ★★〇 · main 的本机实读 (★2026-11-23 17:4x~17:5x · 全部数字本机可复跑 · 不抄任何 agent 报告★) ★★

★**① ★★本单为什么必须存在 (★main 本机实读·★这是全篇最硬的一条★)★★**:

★**ISS-365 (你上一单) 已经把病灶挖出来了: 换官方 land ⇒ `D_LED_G` 的铜箔相对原点偏移变 ⇒ 那组【LED 落位带 + 可落位块数】全变 ⇒ 而这组数现在【不在任何闸的射程里】⇒ 那一趟改板时没人会拦住它 ⇒ 改完才发现 ⇒ 要么板 md5 变第二次 (★违「板只改一次」★) 要么照着过期的数画 ⇒ 装不上** ★

★**main 本机实跑 (★读 `logs/iss365/led_space_drift.json` 的 BEFORE/AFTER 两段·★不是抄 agent 报告★)**:

| 项 | BEFORE (★现占位 land★) | AFTER (★换官方 0805★) | Δ |
|---|---|---|---|
| ★**可落位块数** ★ | ★**1992** ★ | ★**2183** ★ | ★**+191** ★ |
| ★**整高自由带 (X 向)** ★ | ★**1.550..3.450 (宽 1.900)** ★ + ★**72.540..73.660 (宽 1.120)** ★ | ★**2.225..3.250 (宽 1.025)** ★ + ★**73.215..74.385 (宽 1.170)** ★ | ★**带 A 宽 −0.875** ★ · ★**带 B 宽 +0.050** ★ |
| ★**clearance sweep** ★ | ★**1992 / 2016 / 2031 / 2075** (★clr 0.00/0.10/0.20/0.50★) ★ | ★**2183 / 2241 / 2253 / 2197** ★ | ★**★不再单调 (clr 0.50 的 2197 < clr 0.20 的 2253) ⇒ 必须重扫·不能插值★** ★ |

★**★两个致命的推论 (★main 本机实算★)★★**:
- ★**① 带 A 收窄了 0.875 mm** ★ ⇒ ★**`D_LED_G` 的落位窗口从「宽 1.900」变成「宽 1.025」⇒ 而官方 0805 的 fab 外框比现占位【大 0.70×0.40 mm】⇒ ⇒ 【落位窗口变窄 + 器件变大】是同一件事 ⇒ 那一趟必须重排, 不能照抄现在的数★** ★
- ★**② sweep 不再单调** ★ ⇒ ★**任何「按 clr 线性插值取块数」的写法在换 land 后【会算错】⇒ ⇒ 必须真重扫 (★`MECH/check_board_frame_coords.py` 的 `led_space` 口径★) ⇒ ⇒ ★**这组数必须【同一次重算】, 不许「差不多沿用」★** ★

★**② ★★那组数现在写在【哪里】(★main 本机 grep 定位·★这是本单的作业面★)★★**:

| 位置 | 现状 (★main 本机实读★) | 本单怎么处理 |
|---|---|---|
| ★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块** ★ | ★**`full_height_bands` (L301 附近) + `clearance_sweep` (L327~L330) 还是 BEFORE 的旧值** ★ (★1992/2016/2031/2075 + 两条带 1.550..3.450 / 72.540..73.660★) ★ | ★**零改既有页面** ★ ⇒ ★**只出【重算作业包】+ 机器闸·把「那一趟该改成什么值」写成可执行指令★** ★ |
| ★**`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`** ★ | ★**L32 / L243 / L289 / L447 / L535 五处** 都写着 ★**「整高自由带 X 1.550..3.450 (宽 1.900) + X 72.540..73.660 (宽 1.120)」+「最近落位带 X 6.940..8.250 × Y 63.700..67.900」** ★ | ★**同上·零改·只出建议 + 机器判据★** ★ |
| ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2** ★ | ★**你上一单已按 main 16:55 的整改要求改写过了** (★旧 md5 `41fe11f28af1c165ea9c02bad7577c44` → 新 `8a38ac9319e2e47fc080d3651995cf5b`·★对照件 `logs/iss365/29b_struct_crosscheck_md5_change.txt`★) ⇒ ★**这一处【已经做完·不许你再改一遍】** ★ | ★**不许动** ★ |

★**③ ★★ISS-365 交回的「仍归 main 派活」原文 (★main 本机读交卷页·★这是本单的授权依据★)★★**:

> ★**「剩下两处 (`MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块的 `led.full_height_bands` + `led.clearance_sweep` + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格) 仍归 main 派活, 在那一趟换 land 时同一次重算 (E-9)」** ★

★**⇒ 本单 = 那一趟的 E-9 重算作业包 + 机器闸 (★**纯准备·零写板·零落表**★) ⇒ ★★做完本单, 那一趟的 E-9 就变成「照着抄」而不是「到时候再算」★★** ★

★**④ MECH 侧现有三道闸的现状 (★main 本机实跑★)**:
- `MECH/check_onepass_struct_crosscheck.py` (★N1~N6★) · `MECH/check_onepass_mech_sync.py` (★M1~M5★) · `MECH/check_board_frame_coords.py` ★★**三者现在全绿 (★它们读的是当前板 ⇒ 换 land 后会自动重判 ⇒ 本单要做的正是【提前把这个重判算出来】★)★★** ★
★**★关键前提 (★main 本机实读源码·★别踩坑★)★**: ★**`MECH/check_onepass_struct_crosscheck.py` 【没有】 `--root`** (★它靠 `PROJ = HERE/..`★) ⇒ ★**⇒ 沙盒做法: 把 `MECH/` 整个目录 + `HW/PCB/demo_mainboard.kicad_pcb`(副本) + 它要读的表, 复制到 `tmp/iss368_sbx/` ⇒ 跑 `tmp/iss368_sbx/MECH/check_onepass_struct_crosscheck.py` ⇒ 它自动把 PROJ 指向沙盒根 ⇒ ★**真闸一个字节不许改 (只改沙盒副本)】★** ★

★**⑤ 你上一单已经建好的资产 (★你直接用·不许重做★)**:
- `MECH/check_onepass_s10_fp_swap_impact.py` (★M0~M7 · `--selftest` 8/8 · ★**你的新闸要和它同款口径★**★) ★
- `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` (★85,675 B · 你的新页照它的结构写★) ★
- `logs/iss365/led_space_drift.json` (★BEFORE/AFTER 两段·★1,001,851 B·★**大文件·只许 jq/脚本抽读·不许整份读进对话★**★) ★
- `logs/iss365/compute_iss365.json` (★266,340 B★) ★
- ★**★main 本机提醒 (★别踩你上一单的坑★)★**: ★**上一单你因为在页里写库名/封装名全大写+位号前缀, 触发了 `MECH/check_mech_ref_reachability.py` 的 C15 (代码常量名 ⇒ 不是位号) 而把 `gate_check.py` 拖红 (★Q1 15/18★) ⇒ 你的新页/新闸**不许出现「全大写 + 位号前缀」形态的库名**(★写法: 「前缀 + 余下」两段写, ★或用反引号包原名 + 括号里写库★) ⇒ ★**这一条是硬要求·你的闸 rc=0 但 `gate_check.py` 红了照样是失败★** ★

---

## ★★一 · 本单交付物 (★3 件 · 不许扩项★) ★★

### ★★① 第 1 件 · 一页: ★**新建** `MECH/BOARD_ONEPASS_S10_LED_RECALC_WORKPACKET.md` ★★

★**必须包含 (★逐条·不许少★)**:
- ★**§0 口径与读数** ★: 上面 ①②③④ 五条 (★每个数字都要能被 §五 的某条命令复现·**不许抄 main 的转述**·要写「main 17:4x 实跑」并附你**自己复跑**的读数★) ★
- ★**§1 ★★重算作业包: 那一趟该怎么改 (★本单的真命门·★照着就能干★)★★** ★:
  - ★**§1.1 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块的两处** ★: ★**逐处写「现在的值 (BEFORE·逐字) → 该改成什么 (AFTER·逐字) → 依据哪条命令」** ★ (★`full_height_bands` 两条带 · `clearance_sweep` 四档★) ⇒ ★**机器块是 JSON ⇒ 你必须给出【可直接粘贴的 JSON 片段】★ (★不许只写「照 §0 的数改」★) ★
  - ★**§1.2 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的五处** ★: ★**逐处写「行号 + 现在的原话 (逐字) → 该改成什么 → 依据」** ★ (★main 实读定位: L32 / L243 / L289 / L447 / L535★) ⇒ ★**每处都要给【改后的整句】·不许写「同上」★ ★
  - ★**§1.3 ★★「最近落位带」那一组 (X 6.940..8.250 × Y 63.700..67.900) 的处置** ★: ★**main 实读的 AFTER 读数里【整高自由带】变了, 但「最近落位带」那组数 main 没读出来 ⇒ ★**你必须自己实算** (★`logs/iss365/led_space_drift.json` 的 `nearest_band` / `nearest_to_r_led_g` 两项就有★) ⇒ ★**给出 BEFORE / AFTER 两列 + 判「变了还是没变」** ★
  - ★**§1.4 ★★sweep 不再单调 ⇒ 那组数怎么取** ★: ★**你必须给出【真重扫】的做法与逐档读数 (★不是插值★)·并写清「为什么不能插值」(★用 §0 的 2197 < 2253 这条实测证据★)★ ★
- ★**§2 ★★落位可行性的连带影响 (★净距/零侵占那条链不许断★)★★** ★: ★**重算后, `D_LED_G` 在新带里【还放得下吗】? ★** ⇒ ★**给出新带里的可放行窗口 (封装原点) + 与现占位的 Δ + 若放不下 ⇒ 给降级方案 (★三选一: 实测样件 / 选官网参数可满足的替代件 / 改设计路径绕开★)·**不许写「应该放得下」★** ★
  - ★**★你上一单已经证明「S6 那 10 个 `R_SEL_*` 落位前后都不碰 LED 带」(★零侵占·前半句仍成立★) ⇒ ★**你必须复核【重算后的新带】是否仍然零侵占** ⇒ ★**如果新带吃掉了 S6 的落位 ⇒ 那就是【真漂移】·必须写进 §5 卡点★ ★
- ★**§3 三条反向自证** ★: ① 喂【BEFORE 的 land】⇒ 读数必须回到 1992/2016/2031/2075 (★证明你的脚本跟输入走·不是写死★) ② 喂【AFTER 的 land】⇒ 读数必须是 2183/2241/2253/2197 ③ 喂【一个假的中间 land】(★你自己造·★只落沙盒★) ⇒ 读数必须【不等于】上面两个 (★证明闸不是哑弹★)
- ★**§4 降级方案 (★逐条必填·一件不空·三选一★)** ★
- ★**§5 未决项与卡点** ★: ★哪些真要老板拍 (★★只登记·**不许代拍**★·★典型: `D_LED_G` 结构光孔有/无 (★U-365-1·★孔径取决于最终 OPN 镜头 Ø ⇒ `[0数据]`★)★) · ★哪些要 main 裁 (★写清「要谁回答什么」★)★

### ★★② 第 2 件 · 一条机器闸: ★**新建** `MECH/check_onepass_s10_led_recalc.py` ★★

★**判据 (★内容级·**不挂 md5**·沿用 `MECH/check_onepass_s10_fp_swap_impact.py` 的做法·★文档改一个字就重判★)**:
- ★**R0** 基准块存在且是合法 JSON (★同款 BEGIN/END 块★) ★
- ★**R1** ★**AFTER 的四个数由脚本自己算出来** ★: ★**在沙盒上把 `D_LED_G` 的 land 换成官方 0805 ⇒ 真跑 `MECH/check_board_frame_coords.py` 的 `led_space` 口径 ⇒ 算出 `n_placeable` 四档 + 两条整高自由带** ★ ⇒ 页里写的 ≠ 脚本实算 ⇒ 红 ★
- ★**R2** ★**两条整高自由带的 X 区间与页里逐字一致** ★ (★x0/x1 都要比·★不许只比宽度★) ⇒ 对不上即红 (★★这一条是本闸的核心: 它抓的是「只记了宽度·没记位置」★★) ★
- ★**R3** ★**BEFORE / AFTER 两列齐全 + 逐档 Δ 齐全** ★ ⇒ ★**缺一即红 + 点名** ★
- ★**R4** ★**sweep 单调性判据** ★: ★**判「AFTER 的 sweep 【不要求单调】但页里必须【显式写出】AFTER 不单调这件事 + 写明因此不许插值】** ★ ⇒ ★**页里若还写「按 clr 插值」或「块数不变」⇒ 红** ★ (★★这一条钉的是 ISS-365 §3.2 那句被作废的后半句★) ★
- ★**R5** ★**§1.2 的五处 (L32/L243/L289/L447/L535) 逐处齐全** ★ ⇒ ★**少一处即红 + 点名行号** ★
- ★**R6** ★**§1.1 的 JSON 片段可解析 + 片段里的数 == R1 实算的数** ★ ⇒ 对不上即红 ★
- ★**R7** 证据等级全在五级白名单 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★ ⇒ 写 `[官方]` = 红★) ★
- ★**R8** 正文无挂起措辞 (★禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」★) ★
- ★**R9** ★**板 md5 == `611b869e13518c3c023fb178f91a0075` + mtime == `2026-11-06 07:07:17.362193413`** ★ ⇒ ★**★这一条钉住「你没有偷偷改板」—— 沙盒副本必须落在 `tmp/iss368_sbx/`★ ★**

★**`--selftest` 反向用例 ≥7 条, 每条自证「红的是目标那一条, 其余仍绿」**: ★**① 把 §0 的 2183 改成 1992 ⇒ R1 红且 R0/R2~R9 仍绿 · ② 把 §1.2 删掉 L243 那一处 ⇒ R5 红 · ③ 把 §1.1 的 JSON 片段里带 A 的 x1 改错 ⇒ R6 红 · ④ 把 §1.2 某处的整高自由带写成只有宽度没写区间 ⇒ R2 红 · ⑤ 把页里「按 clr 插值」那句话留着 ⇒ R4 红 · ⑥ 清空某行降级方案 ⇒ 红 + 点名 · ⑦ 正文塞「等原厂回信」⇒ R8 红 · ⑧ 把某条证据等级写成 `[官方]` ⇒ R7 红** ★

★**★沙盒一律落项目盘 `tmp/iss368_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)★**

### ★★③ 第 3 件 · 交卷页 + 分片 + 留证 ★★
- ★**交卷页** `HANDOFF/2026-11-23_mech-lead_ISS368_E9_LED落位带同趟重算.md` (★B1~B6 六段齐全 + 20 条验收逐条判定 + 落盘文件清单 + 沙盒留证路径★) ★
- ★**分片** `state/fragments/mech.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ ★**写前后各记一次 md5 基线·期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖** ★
- ★**留证** `logs/iss368/` (★基线 md5 / BEFORE·AFTER 逐档读数 / 五处原话逐字 / JSON 片段 / 沙盒前后闸输出 / selftest 全量输出 / 闸复跑输出★) ★

---

## ★★二 · 边界 (★逐条·不许越★) ★★

★**零写板** ★ (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B ⇒ **开工前 + 交卷后各打一次双证**★) ★
★**零落表** ★ (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `state/issue_log.yaml` 一字不改★) ★
★**零改既有闸** ★ (★`MECH/check_onepass_struct_crosscheck.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_mech_ref_reachability.py` · `MECH/check_onepass_s10_fp_swap_impact.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一个字节不许改★) ★
★**★你的【重算作业包】只是【那一趟该怎么改】的清单·不是现在就改·★** ★ (★§1.1/§1.2 给的是「该改成什么」+「可直接粘贴的片段」·**不许现在就写进那两份既有页**·★那一趟还没到★) ★
★**零改既有页面正文** ★ (★`MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★你上一单已改过的那一行·★**本单不许再动**★) · `MECH/BOARD_GEOM_30MM.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_FRAME_CALIBER.md` 老字一字不许删·不许改·只在交卷页里写建议★) ★
★**零挂链** ★ (★新闸交脚本但不挂进 `state/gate_check.py` —— 挂链是 main 的机制地界·ISS-330/333/362 同款★) ★
★**零外发 / 零采购 / 零联系供应商** ★ (★不发邮件·不询价·不问询·不下采购单★) ★
★**不替老板拍板** ★ (★★`D_LED_G` 结构光孔有/无 (★U-365-1★) 只登记缺口 + 给依据 + 给代价·**不许代选**★★) ★
★**不写别人的分片** ★ (★只写 `state/fragments/mech.yaml`★) ★
★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★
★**证据分级必标** ★ (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★ (★ISS-360 cont0 就是死在这上面★) ★
★**★上下文纪律 (★ISS-363 就是死在这上面★)★**: ★**分段做 + 骨架先落盘 + 大文件不许整份读进对话** ★ (`logs/iss365/led_space_drift.json` 1,001,851 B · `logs/iss365/compute_iss365.json` 266,340 B · `MECH/BOARD_ONEPASS_MECH_SYNC.md` 98,536 B · ★**只 jq / 脚本抽读你���的那几项·不许整份 cat 进上下文★**) ★

---

## ★★三 · 必跑命令 (★全部真实存在·★main 2026-11-23 17:4x~17:5x 本机实测过★) ★★

```bash
# ★★读数 (★main 已实跑过·你要自己复现★) ★★
python3 -c "import json;d=json.load(open('logs/iss365/led_space_drift.json'));print({k:(d[k]['led_space']['n_placeable'],[b for b in d[k]['led_space']['full_height_bands']]) for k in ('BEFORE','AFTER')})"
python3 MECH/check_board_frame_coords.py         # ★当前板读数 (BEFORE 口径)
python3 MECH/check_onepass_struct_crosscheck.py  # ★N1~N6
python3 MECH/check_onepass_mech_sync.py          # ★M1~M5
python3 MECH/check_onepass_s10_fp_swap_impact.py # ★你上一单的闸 · 复跑不许改★
python3 MECH/check_mech_ref_reachability.py      # ★★你的页/闸不许把它拖红 (★上一单的坑★)★

# ★★本单新建 (★你交的两个脚本★) ★★
python3 MECH/check_onepass_s10_led_recalc.py
python3 MECH/check_onepass_s10_led_recalc.py --selftest

# ★★收尾 (★一个字节没改·只许跑不许改★) ★★
python3 state/merge.py                          # rc 必须 0
python3 state/gate_check.py                     # rc 必须 0 · Q1 必须 18/18
python3 state/check_brief_commands.py
md5sum HW/PCB/demo_mainboard.kicad_pcb
```

★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**: ① 页存在且非空 ② BEFORE / AFTER 四档数与脚本实算一致 ③ 两条整高自由带的 X 区间 (x0 与 x1) 逐字一致 ④ §1.1 给出可直接粘贴的 JSON 片段且可解析 ⑤ §1.1 片段里的数 == 实算 ⑥ §1.2 五处 (L32/L243/L289/L447/L535) 逐处在页 + 逐处给改后整句 ⑦ 「最近落位带」给出 BEFORE/AFTER 两列 + 变了没变的判定 ⑧ §1.4 给出真重扫做法与逐档读数 + 写明不许插值 ⑨ §2 给出新落位窗口 + Δ + 放不下时的降级方案 ⑩ §2 复核「S6 那 10 个 `R_SEL_*` 对新带仍零侵占」 ⑪ §3 三条反向自证全部自证成功 ⑫ 证据等级全在五级白名单 ⑬ 降级方案逐件非空 ⑭ 正文零挂起措辞 ⑮ 自建闸裸跑 rc=0 ⑯ `--selftest` ≥7/7 全 PASS 且每条自证「只红目标那条」 ⑰ 沙盒在项目盘 `tmp/iss368_sbx/` (★不写 /tmp★) ⑱ **板 md5/mtime 逐字节未变** ⑲ `merge.py` rc=0 + `gate_check.py` rc=0 且 Q1 18/18 (★★且 `check_mech_ref_reachability.py` 仍绿★) ⑳ 分片只走 `frag_write.py` + 交卷页 B1~B6 齐全 + `logs/iss368/` 留证在盘
