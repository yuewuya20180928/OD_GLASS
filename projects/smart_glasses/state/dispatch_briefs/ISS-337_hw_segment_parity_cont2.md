【ISS-337 · hw-lead · ★★cont2 · 「段数追平」根因定位 —— ★只补 4 处缺口 + 把已做完的 3 件写进交卷页★★】

★**这是 ISS-337 的第二次续做单 (★不是从零重做★)** ★**派活方 = 项目总工 (main)** ★
★**上游**: ISS-337 cont0 交卷页 `HANDOFF/2026-11-19_hw-lead_ISS337_段数追平根因定位.md` (21,043 B @01:03) + 主交付物 `HW/PCB/ONETRIP_S8_SEGMENT_PARITY_ROOTCAUSE.md` (20,026 B @01:00) + `logs/iss337/` 17 件★

★★★【★★为什么派 cont2 (★派活方 2026-11-22 20:5x 本机实读·不抄任何 agent 报告★)★★★】★★

★**① cont1 (★2026-11-19 02:3x 由兄弟 job fb67af40 派出★) 的子会话在 02:42 被【Token Plan 用量上限】掐死** (★错误码 2056·★**不是技术失败**★) ⇒ ★**它只干到一半** ★
★**② 派活方 2026-11-22 20:5x 本机实读盘面 ⇒ cont1 的 6 处缺口: 【已做完 3 处】/【还差 4 处】** ★
★**③ ★**距上一次产出已隔 3 天 18 小时 (2026-11-19 02:42 → 2026-11-22 20:5x·★全仓零文件改动★) ⇒ 本单是【断线后第一条活】★**

★★★【★★★① cont1 【已经做完】的 3 件 (★派活方 2026-11-22 20:5x 本机逐件实读·★你不许重做·★直接引用★)★★★】★★★

| ★做完的★ | ★盘面证据 (★mtime 逐字★)★ | ★读数★ |
|---|---|---|
| ★**cont1 缺口 ③ (selftest 用例 5 写反) 已修** ★ | `tmp/iss337/seg_parity_selfcheck.py` (16,245 B @**02:36**) + `logs/iss337/19_seg_parity_selftest_fixed.txt` (@**02:40**) | ★末行 = `ALL TESTS PASS` ⇒ ★**新口径成立: 官方板与现役臂【同带】, 老口径【会把官方板自己拦掉】**★ |
| ★**cont1 缺口 ⑤ (归一化段数定义没钉死) 已钉死** ★ | `logs/iss337/18_norm_impl_diff.txt` (@**02:42**) + `tmp/iss337/norm_impl_diff.py` (@02:35) | ★V1/V2/V3/V4 四套实现对照: 官方 **2649/2650/2464/2461** · 现役 **2582/2583/2537/2534** ⇒ ★**口径 = V1 (层,网,宽 + 度数=2) ⇒ 官方 2649 vs 现役 2582** ★ |
| ★**main 的 2 条独立复算发现 已复算完** ★ | `logs/iss337/17_main_findings_recheck.txt` (@02:35) + `tmp/iss337/verify_main_findings.py` (@02:35) | ★发现①: 官方板 136 焊盘网 / 90 有铜 / **24 零铜**; 现役链终 v76mg1 = **7** · v76mz = 12 · best_unc23 = 7 ⇒ ★**两边都零铜只剩 3 条**: `CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N` ★ / ★发现②: 官方板 vs best_unc23 两板都有铜 86 条 ⇒ ★**铜长相符只有 21/86**★ (最大差 8 条: `LIGHT_3V3` Δ−63.0mm / `DSI_D0_D0_N` Δ−58.3mm / `ID_DETECT_0` Δ−51.4mm / `I2C_A_SDA` Δ−41.6mm / `BAT_DET` Δ−31.0mm / `LED_G` Δ−30.0mm / `I2C_B_SCL` Δ−27.8mm / `NET_USB_D_N_TYPEC` Δ−26.8mm) ★ |

★★★【★★★② 还差 【4 处】 (★这就是你这一趟要干的全部·★不许开新研究·★不许写新的大段分析★)★★★】★★★

| ★缺口★ | ★干什么 (★逐字可执行★)★ | ★验收信号★ |
|---|---|---|
| ★**G1 · 交卷页缺 B4「接口取值声明」块** ★ | ★**追加式**: 在 `HANDOFF/2026-11-19_hw-lead_ISS337_段数追平根因定位.md` 里 ★**新增一节 `## B4 · 接口取值声明 (interface_claims)`** ★ (★★你原来那节「B4 · 分片」★**一个字不许删**★ ⇒ ★**改完后页里同时有两节 B4·这没关系·闸只认标题关键词★★) ⇒ ★**内容 = 你实际登记进 `state/fragments/hw.yaml` 的 interface_claims 逐条 (★key + value + 谁可以照抄★) ⇒ ★**零 interface_claims 就写「本单零 interface_claims」+ 理由** ★ | ★**`python3 state/gate_check.py` ⇒ 【Q1 交付齐备率】里 hw-lead 那行 = `6/6 缺: 无`** ★ |
| ★**G2 · 分片根本没写** ★ | ★**只走 `python3 state/frag_write.py --agent hw-lead --add-claim ... --add-artifact ... --add-need ...` 原子写** ★ (★★**不许 `open(p,"w")` 手写 YAML**★) ⇒ ★**至少登记**: ① 归一化口径 (V1) + 三个区间 ② 「不追段数·改立同口径基线」这条口径 ③ 本单 4 个产物路径 (artifact) ④ main 的两条发现的复算结论 (claim) ⇒ ★**交卷时贴 `grep -c iss337 state/fragments/hw.yaml` 的读数 (★要求 ≥ 5★)** ★ | ★**`grep -c iss337 state/fragments/hw.yaml` ≥ 5** ★ |
| ★**G3 · band 口径三处不一致 (★文档 vs 脚本 vs 老口径★)** ★ | ★**脚本真值 (★已由 cont1 修好·★不许再改★)**: `tmp/iss337/seg_parity_selfcheck.py` L59-61 ⇒ ★**归一化段数 ∈ [2300, 3200] · 铜长 ∈ [4600, 5900] mm · 过孔 ∈ [380, 520]** ★ ⇒ ★**交卷页 §B1/§B2 与主交付物 §(口径段) 里现存的「归一化 [2400,2900] · 铜长 [5400,5900] · 过孔 [380,450]」必须改成上面这组脚本真值** ★ ⇒ ★**并写明为什么改**: ★**老过孔口径 [380,450] 是按官方板 433 拍的 ⇒ 现役臂 471/486/505 全被误拦 ⇒ 官方板自己反而过了 ⇒ 区间不能由单块板锚定·必须由「官方 + 现役 + v76mz + best_unc23」四块一起锚** ★ ⇒ ★**脚本一个字都不许改** (★只改文档里的引用值★) ★ | ★**交卷页 + 主交付物里搜 `380` / `450` / `520` / `[2400` ⇒ 区间值与脚本逐字一致; ★`python3 tmp/iss337/seg_parity_selfcheck.py --selftest` 末行 = `ALL TESTS PASS` (★rc=0★)** ★ |
| ★**G4 · 交卷页自称一份不存在的证据 (★件数 + 空指针★)** ★ | ★**§B3 件数 = 13 (★不是 16★·★以盘面为准★)** ⇒ ★**§5 那两行沙盒臂读数列 (段数/过孔/铜长/归一化/unc/DRC) 全部写 `[0数据]` + 原因** ⇒ ★**原因只许写本机原文**: `tmp/iss337/sbx/run_sbx.out` 逐字 = `[A] ★EXIT=124 2026-11-19 01:59:34` (★timeout 3600★) + `[B] ★EXIT=143 2026-11-19 02:29:59` (★被 kill★) ⇒ ★**全页零空指针零假引用零「见 §B3-13」这种指空** ★ ⇒ ★**不许写「等原厂回信」「等外部回复」「待外部确认」(★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·全靠自己查★)⇒ 这一条没有任何外部依赖·本机日志就是全部证据** ★ | ★**交卷页全文 grep `见 §B3-1` / `__[A-Z_]+__` / `🔄\|待填\|PLACEHOLDER\|施工中` ⇒ 全 0** ★ |

★★★【★★★③ 同时把 cont1 已经做完的 3 件 【写进交卷页正文】(★不许只躺在 logs 里·★交卷页是唯一门面★)★★★】★★★

★**★W1 · 把「归一化口径 = V1 (层,网,宽 + 度数=2)」写进交卷页与主交付物 (★附 V1/V2/V3/V4 四套实现的对照读数, ★出处 = `logs/iss337/18_norm_impl_diff.txt`★) ⇒ ★**并写明「归一化段数只差 2.5% ⇒ 老口径会把官方板自己拦掉 ⇒ 老口径已作废」** ★
★**★W2 · 把 main 的发现①写进交卷页**: ★**官方板 24 条零铜网里, 21 条在现役链终板 (v76mg1) 上【已经有铜】·两边都零铜只剩 3 条 (`CSI_D0_D0_N_SRC`/`CSI_D0_D2_N`/`CSI_D0_D3_N`)** ⇒ ★**⇒ 「布线 45→0」的分母必须在【板那一趟的新基线】上重读, 不许拿官方板那 24 条当靶** ★
★**★W3 · 把 main 的发现②写进交卷页**: ★**「段数对齐」≠「同一块铜」** (★逐网铜长相符只有 21/86★) ⇒ ★**⇒ 判据必须改成【逐网铜量名单 + 零铜网名单】双向, 不许拿归一化段数当唯一尺子** ★ ⇒ ★**这一条同时是 ISS-334 need-4b 定稿的输入** ★

★★★【★★★④ 交卷前必跑 (★原样贴进交卷页 B6★)★★★】★★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 tmp/iss337/seg_parity_selfcheck.py --selftest   # ⇒ 末行 ALL TESTS PASS, rc=0
TMPDIR=$PWD/tmp python3 state/merge.py       ; echo "MERGE_RC=$?"
TMPDIR=$PWD/tmp python3 state/gate_check.py   ; echo "GATE_RC=$?"   # ⇒ Q1 里 hw-lead 6/6 缺: 无
TMPDIR=$PWD/tmp python3 state/issue_check.py  ; echo "ISSUE_RC=$?"
grep -c iss337 state/fragments/hw.yaml        # ⇒ ≥ 5
md5sum HW/PCB/demo_mainboard.kicad_pcb        # ⇒ 611b869e13518c3c023fb178f91a0075 (逐字节不许变)
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # ⇒ 2026-11-06 07:07:17.362193413 +0800
```

★★★【★★★★【★边界 (★一条都不许破★)★★★★】★★★】

★**零写板** (★板 md5 + mtime 交卷前后各贴一次★) · ★**零落表** (网表 / 脚表 / BOM 三个 md5 不许变) · ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_official.py` / `state/chain_gate.py` 一个字节不许改★) · ★**零改生成器代码** (★`state/gen_pcb_routing.py` / `state/gen_pcb_netlist_board.py` / `state/gen_kicad_project.py` 一个字节不许改★) · ★**零改别人文档** (★只许改本单自己的交卷页 + 主交付物 + `state/fragments/hw.yaml`★) · ★**只写自己的分片** (★`state/fragments/hw.yaml`·★`hw.yaml` 里别人的 key 一条都不许删改★) · ★**不自签 issue_log** (★`state/issue_log.yaml` 是 main 的地界★) · ★**零外发** (★不发邮件 / 不联系供应商 / 不下采购单★) · ★**不替老板拍板** (★板框 / 屏版本 / 跌落等级那些老板级的你一条都不许代拍★) · ★**沙盒只写 `tmp/iss337/` + `logs/iss337/`** (★★**不许重跑两条沙盒臂**★ ⇒ 上一趟 EXIT=124/143 的账已在 §5 写清·重跑只是烧时间★)

★★★【★★★★【★交卷格式 (★你 cont0 的格式, 照抄★)★★★★】★★★

★**交卷页**: 在 `HANDOFF/2026-11-19_hw-lead_ISS337_段数追平根因定位.md` 上 ★**追加式补齐** (★★**不要新建第二份交卷页**★ ⇒ ★**gate_check 按文件名倒序取「最新一份」评分, 新建一份会让评分基准切换·没必要★) ⇒ ★**B0~B6 六块齐全 (B4 标题必须是「B4 · 接口取值声明 (interface_claims)」)★**
★**主交付物**: `HW/PCB/ONETRIP_S8_SEGMENT_PARITY_ROOTCAUSE.md` (★口径段改成脚本真值 + 补 W1/W2/W3 三段★)
★**证据**: `logs/iss337/` 追加本趟新产物 (★编号接在 19 后面·★**先落盘再写页·别最后一起写★**)
★**分片**: `state/fragments/hw.yaml` (★只走 `frag_write.py`★)
★**最后一条消息**: ★**只回这 4 行** ★
```
SELFTEST_RC=0
GATE_RC=0
FRAG_ISS337_HITS=<数字>
BOARD_MD5=611b869e13518c3c023fb178f91a0075
```
★**再附 ≤8 行摘要** (★讲清 G1~G4 四处补得怎么样 + W1~W3 三段写进哪一页 + 交卷页字节数·★不许写「已完成」这种空话·要有读数★)
