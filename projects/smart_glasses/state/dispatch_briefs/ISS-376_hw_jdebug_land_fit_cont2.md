# ISS-376 · hw-lead · 「板那一趟」`J_DEBUG` 换官方 1×4 THT land 的**落位可行性**穷举（现位放不进 ⇒ 挪哪 / 挪多大）· ★★cont2 续做 (★上一趟 01:13~01:17 被掐·**扫描脚本已落·JSON 落盘炸了·页/闸/交卷页/分片零**★)★★ · 纯分析 + 沙盒预演 + 新建闸 · 零写板

★★**这是 cont2 续做派活 (★不是从零重开★)** ⇒ ★**上一趟 (2026-11-24 01:13:40 派) 的子会话 `agent:hw-lead:subagent:ea28af80` (sessionId 1d527598) 于 01:17:12 被掐死 (★status=timeout + abortedLastRun=true + runtimeMs=410,495 ≈ 6.8 分钟·promptError="This operation was aborted"·**externalAbort=false** ⇒ 非外部 abort·非上下文溢出★)** ⇒ ★**⇒ 本单 = 【只补剩下的】, 不是从零★**

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-376_hw_jdebug_land_fit.md` ★

---

## ★★一 已在盘的 (★不要重做·直接用★) ★★

★**① ★★落位扫描脚本已落 (★这一趟最贵的重活已经做完了·★你【不要重写】, 只修它的 bug★)★★**: ★`tmp/iss376_sbx/tools/scan_land_fit.py` (★538 行 @ 2026-11-24 01:15★) ★

★**② ★★它跑出来了, 但【落盘炸了】★★**: ★**`logs/iss376/scan_stdout.txt` (★1,535 B @ 01:17★) 里有完整 traceback + `logs/iss376/scan_land_fit.json` (★1,154 B @ 01:17★) 是【半截的】** ★
★**★main 本机实读的炸点 (★行号是脚本里的真行号★)★★**:
```
File "tmp/iss376_sbx/tools/scan_land_fit.py", line 531, in main
    json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
TypeError: Object of type set is not JSON serializable
```
★**⇒ 根因 = `out` 里有【set】对象, `json.dump` 不认 ⇒ ★**修法 = 落盘前把 set 转成 sorted list (★`sorted(...)` 或 `list(...)`★)** ★
★**★⇒ ★★这一条就是你这趟的第一个动作 (★见 §四 ①★)★★**

★**③ ★★`logs/iss376/scan_land_fit.json` 的【前半截是真的、可直接读】★★**: ★**main 本机实读 (★它写到这里就炸了·但前半截已落盘·★**已落的内容逐字如下★)★**:
```json
{ "meta": { "board": ".../HW/PCB/demo_mainboard.kicad_pcb", "pcbnew": "10.0.8" },
  "mod": { "file": ".../Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
            "pads": [ {"name":"1","ptype":"thru_hole","shape":"rect","x":0.0,"y":0.0,"w":1.0,"h":1.0,"drill":0.65},
                      {"name":"2","ptype":"thru_hole","shape":"circle","x":0.0,"y":1.27,...},
                      {"name":"3",...,"x":0.0,"y":2.54,...},
                      {"name":"4",...,"x":0.0,"y":3.81,...} ],
            "crtyd": {"x1":-1.55,"y1":-1.14,"x2":1.55,"y2":4.95},
            "fab":   {"x1":-1.16,"y1":-0.81,"x2":1.05,"y2":4.445},
            "local_span_y": 3.81, "local_span_x": 0.0, "copper_x_span": 1.0, "pad_drill": ...
```
★**⇒ ★★官方 land 的几何已经测准了 (★pad1=rect / 其余 circle / 沿局部 Y 排 / 跨度 3.81 / 铜箔 X 跨度 1.0 / 钻孔 0.65 / crtyd 3.10×6.09 / fab 2.21×5.255★)⇒ ★★你不用重测它, 修完 bug 重跑一遍脚本就会重新落全量★**

★**④ ★★你的全部工作量 = 三件★★**: ★**① 修脚本那个 `set` 的 bug 并重跑, 让 `logs/iss376/scan_land_fit.json` 【完整落盘】 ② 新建真相页 `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` ③ 新建闸 `HW/check_jdebug_land_fit.py` (★L0~L8 + `--selftest` ≥8 条反向用例★) ④ 新建交卷页 `HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md` (★B1~B6 六段齐全★) ⑤ 分片 `state/fragments/hw.yaml` 登记 (★只走 `state/frag_write.py`★) ★**

---

## ★★二 ★★你必须自己算出来的数 (★main 已给判据与坐标, 但数必须你自己跑出来★) ★★

★**① 现位冲突表 (★§1 要的逐 pad 表★)**: ★**`J_DEBUG` 现位 origin `(144.3000, 58.0000)` orient `0.0` · 4 pad 全 SMD `0.2750×0.9000` 全 RECT · pad X `142.2000/142.7000/143.2000/143.7000` (pitch `0.5000`) · 铜箔 X `142.0625..143.8375` (宽 `1.7750`) × Y `56.1500..57.0500`** ★
★**② 官方 land 三朝向的 pad 绝对坐标** (★rot `0` / `90` / `270`·★**不许手算旋转矩阵·★用 `FOOTPRINT.SetOrientationDegrees` 在真 board 上算★**) ★
★**③ ★★落位可行域 (★本单正题·★要交【区间】不是【一个点】★)★★**: ★**逐个候选落位上, 对四个 THT 孔与板面【所有 via 孔 + 所有已有 THT 孔】算孔净距 (★要求 ≥ `min_hole_to_hole` = `0.25`★) + 铜箔包络 (X 宽 `4.8100` = 3×1.27+1.00) 与既有过孔铜箔/走线的净距 + fab 外框 (rot90 `5.08×2.10` / rot0 `2.10×5.08`) 与板框的关系 ⇒ ★**⇒ 交出「哪一段区间放得下」+「最优落点 (带余量)」** ★**
★**④ ★★挪完还剩什么 (★§3 的代价账·★逐件必须带坐标★)★★**: ★**板面既有对象 (★main 00:4x 实读过 via 坐标·★全部 via 直径 `0.6000` / 钻孔 `0.3000`★)★:
- `XTAL_OUT` @ `(142.2000, 53.2000)` 与 `(146.9500, 57.9500)`
- `JTAG_TDO` @ `(143.7000, 57.9500)` 与 `(142.4500, 54.7000)`
- `JTAG_TCK` @ `(138.7000, 54.7000)`
- `JTAG_TMS` @ `(145.2000, 54.9500)` 与 `(147.2000, 54.4500)`
- `XTAL_IN` @ `(141.2000, 58.9500)`
⇒ ★**两个硬冲突 (★ISS-373 沙盒 S2b 实测·★你必须能重现这两个数·★对不上就停下查你的脚本★)★**: ★**PTH pad1 `(144.3000, 58.0000)` vs via `JTAG_TDO` `(143.7000, 57.9500)` 孔净距 `0.1271` (★要求 ≥ `0.25`★) · PTH pad3 `(146.8400, 58.0000)` vs via `XTAL_OUT` `(146.9500, 57.9500)` 孔净距 `0.0000`** ⇒ ★**⇒ DRC `hole_to_hole` 由 `0` → `4`** ★
★**⑤ 板 DRC 判据 (★读 `.kicad_pro` 真值·★不许写死进闸★)**: ★`min_hole_to_hole`=`0.25` · `min_hole_clearance`=`0.25` · `min_through_hole_diameter`=`0.3` · `min_via_diameter`=`0.5` · `min_via_annular_width`=`0.1` · `min_track_width`=`0.2` ★
★**⑥ 那 4 条 JTAG 走线脱网 (★ISS-373 实测★)**: ★**落盘后 KiCad 连通性重建把 63 段 `JTAG_TDO` 走线改归 `JTAG_TCK` (★S1: `JTAG_TCK` 34 段 / `JTAG_TDO` 63 段 ⇒ S2b: `JTAG_TCK` 97 段 / `JTAG_TDO` 0 段★) ⇒ ★**⇒ 那 4 条 JTAG 走线的端点脱网 ⇒ 必须重接** (★⇒ 这一条要进 §3 的代价账★) ★

---

## ★★三 边界 (★一条不许越★) ★★

★**零写板** (★真板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★`HW/netlist_v1.csv` md5 `6aee500e60ba0732f83a9cf557ba90ab` · `HW/netlist_v1_pins.csv` md5 `9174309df1ec9411ac8e8d9e80ee386a` · `HW/BOM_v1.csv` md5 `5b9993992405904a60ac96a020b375d8` 一律只读★) ★
★**零改既有闸** (★`HW/check_onepass_s10_swap_set_truth.py` (★ISS-373 已签收件★) · `HW/check_fp_libid_truth.py` (★ISS-369 已签收件★) · `HW/check_onepass_preflight_coverage.py` · `HW/check_pcb_nets.py` · `MECH/check_jdebug_1p27_clearance.py` (★ISS-371 已签收件★) · `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ⇒ ★**★你只许改【你自己这一单的闸】`HW/check_jdebug_land_fit.py` + 【你自己这一单的沙盒脚本】`tmp/iss376_sbx/tools/scan_land_fit.py`★** ★
★**零改既有页面正文** (★`HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` (★ISS-373 已签收件★) · `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` (★ISS-369 已签收件★) · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收件★) —— ★**本单只新写一页 + 一条闸, 既有页面一个字都不许动**★ ⇒ ★**要订正既有页面的部分 ⇒ 写成「追加式订正块」放进【你自己那一页】的 §4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/hw.yaml`** (★**只走 `python3 state/frag_write.py --agent hw-lead`** ★· 写前写后各记一次 md5 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」· 不许静默覆盖★) ★
★**沙盒只落 `tmp/iss376_sbx/` + `logs/iss376/`** ★
★**不代老板拍板** · **不代 main 拍** (★「那一趟换不换 land (90 件 vs 91 件)」是 main 的裁决权 ⇒ 你只给落位侧的代价账与可行域★) ★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ **全靠自己查·查不到写降级方案·不许写「等原厂回信」**★) ★
★**不自签 `state/issue_log.yaml`** (★台账由 main 签收★) ★
★**零推 GitHub** (★由独立的 5 小时同步 job 负责★) ★

---

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 HW/check_jdebug_land_fit.py                    # 新闸 ⇒ rc=0
python3 HW/check_jdebug_land_fit.py --selftest          # 新闸自测 ⇒ rc=0 (末行 ALL TESTS PASS)
python3 HW/check_onepass_s10_swap_set_truth.py         # ★ISS-373 那条闸必须仍然 rc=0 (零漂移自证)★
python3 HW/check_fp_libid_truth.py                      # ★ISS-369 那条闸必须仍然 rc=0 (零漂移自证★)
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                            # rc=0 (★Q1 必须 18/18★)
python3 state/check_brief_commands.py                  # rc=0
grep -c check_jdebug_land_fit state/gate_check.py      # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                 # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb        # 必须 2026-11-06 07:07:17.362193413 4940213
```
★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「cont1 被掐 + 本趟从已落扫描脚本续做 + 修了 json 落盘的一个真 bug」** ★
★**收工后回卷 (★按老规矩★)**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」★)★ ★

---

## ★★五 ★★你这一趟有一条约 16 分钟的硬墙 (★实测: 上一趟就因为【父 run 收尾连带】被掐在 6.8 分钟★) ⇒ ★★顺序必须严格照这个来, 每一步都先落盘★★ ★★

1. ★**① 修 `scan_land_fit.py` 的 `set` 落盘 bug (★§一 ② 给了行号与根因·★是【落盘那一步】炸的, 不是扫描本身炸的★) ⇒ 重跑它 ⇒ `logs/iss376/scan_land_fit.json` 完整落盘** ★
2. ★**② 从完整 JSON 里读出可行域 + 最优落点 + 代价清单 (★§二 的 ①~⑥ 全部要有数★)** ★
3. ★**③ 新建真相页 `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` (★§0~§6★) 并落盘** ★
4. ★**④ 新建闸 `HW/check_jdebug_land_fit.py` (★L0~L8 + `--selftest` ≥8 条反向用例·★其中 ≥2 条针对「只试一个落点就宣布可行/不可行」★) 并落盘** ★
5. ★**⑤ 新建交卷页 (★B1~B6★) + 分片登记 (★`state/frag_write.py`★) 并落盘** ★
6. ★**⑥ 最后跑一遍 §四 那 11 条命令, 把输出贴进交卷页 B6** ★

★**★★第一个工具调用 = 修那个 `set` 的 bug 并重跑脚本 (★不是读文档·不是读你已有的页★) ★★** ★**★★并且: ★★你算出来的数如果跟 main 给的对不上, 【以你本机复算的为准】, 但必须在交卷页里写清差在哪、为什么差★★ ★**
