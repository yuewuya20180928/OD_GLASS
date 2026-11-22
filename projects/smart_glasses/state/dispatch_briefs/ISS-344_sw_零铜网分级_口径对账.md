★★★★【main 2026-11-23 00:5x · ★★PCB 线 · 固件侧「可悬空候选」分级 与 板那一趟终裁 对账 · 纯分析 + 文档订正 + 机器闸 · 零写板 ★★】★★★★
★**`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §3 表把 6 条网判成「NC (不连)」, 而 main 2026-11-22 20:5x 已把它们逐条改判【必需】⇒ 这 6 条会带着「板侧不许标 NC」的矛盾进板那一趟 ★**

★**派活方 = 项目总工 (main) · 2026-11-23 00:5x · cron fb67af40 (队列自动派活)★★**
★**来源 = ISS-338 交回 main 的 3 条 need (★main 2026-11-22 20:5x 逐条已裁·落在 `state/fragments/pm.yaml` 的 `answers` 里·key = `iss338_need_usbif_cc1_cc2_rule` / `iss338_need_boot_storage_answer` / `iss338_need_jtag_group_decision`★) + `iss334_need4b_zero_copper_net_triage` 的分级定稿★★**
★**工作目录 (★所有命令都在这里跑★)**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`

---

## §0 事实 (★main 本机实读 + 实跑, 不抄任何 agent 报告★)

★**① ISS-338 交回 main 的那条待决 (★那本交卷页自己写的★) ★**:
★**`HANDOFF/2026-11-19_sw-lead_ISS338_9条单端脚固件引用.md` §B5-6 原文**: ★**「9 条的固件侧降级声明由谁落笔 | **main** (派给 sw-lead 下一单) | ★**本单【不许改固件本体】⇒ §3 只写清「改哪一行」, 一行未动** ★ | ★**下一单照 §3 的行号清单改** ★」** ★
★⇒ ★**这份「下一单」一直在等 main 先裁「哪些网真能悬空」⇒ ★**main 已于 2026-11-22 20:5x 裁完了 ⇒ 本单就是那一单 ★**

★**② main 2026-11-22 20:5x 的终裁 (★`state/fragments/pm.yaml` → `answers` → 逐字★) ★**:
- ★**`iss338_need_jtag_group_decision`**: ★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」** ★
- ★**`iss338_need_boot_storage_answer`**: ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★
- ★**`iss338_need_usbif_cc1_cc2_rule`**: ★**`USB_CC2` 判【必需】(板侧不许标 NC)** ★
- ★**`iss334_need4b_zero_copper_net_triage` (分级定稿)**: ★**A 必需 (23 条) = ① 15 条高速差分腿 + ② 8 条单端脚 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · B 可悬空 (1 条) = `FSIN_OUT` (★**条件**: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作**★)★★
- ★★**⇒ 逐条对照: 终裁说「可悬空」的只有 `FSIN_OUT` 一条; 终裁说「必需」的单端脚 = 8 条 (含 `CAM_RESET_N` `LED_G_D` 这两条本来就没争议的) ★★**

★**③ ★★本单的病根: SW 那份交付物的 §3 表【还在按 ISS-338 当时 (11-19) 的旧分级】, 跟终裁逐条打架 ★★ (main 实跑判定) ★**:
- ★**机器真值 = `HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` = `["CAM_RESET_N", "LED_G_D", "USB_CC2", "JTAG_TDI", "UART_RX", "SPI_SCLK_BOOT", "SPI_MOSI_BOOT", "SPI_MISO_BOOT"]` + `FLOAT_OK = ["FSIN_OUT"]` + `EXPECT_REQUIRED = 23` / `EXPECT_FLOAT = 1` / `EXPECT_TBD = 0` ★**
- ★**main 实跑 `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ⇒ rc=0, 输出「分级自检: 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔」★**
- ★**main 实跑 (★把 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §3 表逐行解析, 抽出「建议的板侧标记 = NC (不连)」的网名★) ⇒ 判 NC 的 7 条 = `FSIN_OUT` `JTAG_TDI` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2` ★**
- ★★**⇒ 与终裁【冲突】的是 6 条: `JTAG_TDI` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2` (★终裁 = 必需·板侧不许标 NC; SW 页 = NC (不连)★) ★★**
- ★**⇒ 与终裁【一致】的只有 1 条: `FSIN_OUT` (★终裁 = 可悬空, 但★**带条件**★: 板那一趟新基线上仍零铜才允许标 NC ⇒ 现在只定口径不动手★) ★**

★**④ 冲突的具体后果 (★这 6 条每一条都踩一个不同的坑, main 逐条读过原文★) ★**:
| 网 | SW 页 §3 说 | 终裁说 | 踩坑点 (main 实读) |
|---|---|---|---|
| ★`JTAG_TDI` ★ | NC (不连) + 固件侧要改 4 处 (★`SW/FLASH_AND_VERSION.md:336` / `:44` · `SW/EVT_TEMPLATE.md:503` · `SW/S2_BOARD_TEST_CHECKLIST.md:393`★) | ★**必需 · 整组保留** ★ | ★**JTAG 整组 4 根 (`TCK`/`TMS`/`TDO`/`TDI`) 全有铜 ⇒ 只把 `TDI` 标 NC ⇒ 「4 线缺 1」⇒ 调试口等于摆设 ⇒ 这正是 main 11-22 20:5x 明确裁掉的「裁 TDI」路线 ★** |
| ★`SPI_MISO_BOOT`/`SPI_MOSI_BOOT`/`SPI_SCLK_BOOT` ★ | NC (不连) + 固件侧要改 4 处 (★`SW/FLASH_AND_VERSION.md:359` / `:46` / `:527` · `SW/S2_VENDOR_QUESTION_LIST.md:315`★) | ★**必需 · 板侧【不许】标 no-connect** ★ | ★**`J_BOOT1` 焊盘位【已经在板上】⇒ 布线保留的成本 ≈ 0 ⇒ 现在标 NC ⇒ 将来老板拍「外挂 SPI-NOR」⇒ 板必须重出 ⇒ 直接破「板只改一次」★** |
| ★`UART_RX` ★ | NC (不连) + 固件侧要改 3 处 (★`SW/S2_BOARD_TEST_CHECKLIST.md:94` · `SW/tools/s2_board_run.sh:248` · `SW/tools/s2_rescue_config.json:230`★) | ★**必需** ★ | ★**main 11-22 20:5x 明确不采信 sw-lead 的「`UART_RX` 可悬空」结论 (★`UART_RX` 是调试口 ⇒ 布线保留成本 ≈ 0★) ★** |
| ★`USB_CC2` ★ | 待定 ⇒ 建议 NC (不连) + 固件侧要改 3 处 (★`SW/ONETRIP_SW_RENAME_SAFETY.md:31` · `SW/SW_TIMING_REVIEW.md:274` · `SW/tools/check_sw_ref_reachability.py:185`★) | ★**必需 · 板侧不许标 NC** ★ | ★**[官网] USB Type-C 插座端双路 Rd 条款 ⇒ `USB_CC2` 不可悬空 ★** |

★**⑤ 为什么这条【不】依赖老板拍板 (★老板那 9 件还在队列里, 本单不许拿它当阻塞项★) ★**:
★**这 6 条的分级 main 已于 2026-11-22 20:5x 逐条裁完 (★机制地界·不占老板拍板面★) ⇒ ★**本单现在就能做 (只做【对账 + 订正 + 机器闸】, 不动固件本体不动板) ★**

★**⑥ 固件本体一个字都不许动 (★ISS-338 自己的边界★) ★**:
★**ISS-338 §B2 第 6 条原文: 「★**本单不许改固件本体** ★」 ⇒ ★**本单同样不许改固件本体 (`SW/tools/s2_board_run.sh` / `SW/tools/s2_rescue_config.json` / `SW/tools/check_sw_ref_reachability.py` 等) ★** ⇒ ★**本单只做「把 §3 那张表的分级口径与固件侧要改清单订正到与终裁一致」, 一行固件代码都不许动 ★**

---

## §1 本单要交付什么 (★三件, 不许跑题★)

★**① `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §3 表 + 相关分级陈述追加式订正 (★老字一字不删★) ★**
- ★**把那 6 条 (★`JTAG_TDI` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2`★) 的「建议的板侧标记 = NC (不连)」改成「★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★」 ⇒ ★**并写明依据 (★逐条引 pm.yaml 的哪个 key + 哪句原文 + 证据等级★) ★**
- ★**`FSIN_OUT` 保留「可悬空」, 但必须把【条件】补上 (★main 原文: 「★**条件**: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作**★」★) ⇒ ★**不许在 SW 侧现在就把 NC 落下去 ★**
- ★**★**连带清理 (★main 实跑发现: 同一份文件里还有别处也在说「可悬空 6 条 / 必需 2 条」★)★**: ★**该文件的 §0 / §2 / §5 三处分级陈述 (★原文含「真必需 4 条」「可悬空候选 4 条」「必需 2」「可悬空候选 6」「待定 1」等等★) 也必须一并订正到与终裁一致 (★终裁: 必需 23 / 可悬空 1 / 待定 0★) ⇒ ★**你必须把这几处的具体行号逐条找出来 (★main 实读: 第 6 行 / 第 12 行 / 第 15 行 / 第 24~25 行 / 第 235 行 附近都有分级陈述★) 并逐处订正 ★** ⇒ ★**不许只改 §3 表就交卷 (★那会留下「表说必需 2 · 表外说必需 23」的自相矛盾★) ★**
- ★**★**订正方式 = 追加式 (★加一段「★**分级订正 (main 2026-11-22 20:5x 终裁) ★**」小节, 逐条列「旧说法 → 新说法 → 依据」★) ⇒ ★**老字一个字都不许删 (★本项目铁律: 追加式·老字一字未删 = 可自证★) ★**

★**② 建一道机器闸, 让「SW 侧分级」与「板侧真值」不许再分叉 (★只读 + 反向用例★) ★**
- ★**新建 `SW/tools/check_sw_zero_copper_grade_consistency.py` (★**新建**★) ★**
- ★**它必须做: ① 读 `HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` / `FLOAT_OK` (★**真值源 = 板那一趟的唯一机器判据**★) ⇒ ② 扫 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §3 表, 抽出每条网「建议的板侧标记」⇒ ③ 断言: ★**凡判 NC 的网, 必须在 `FLOAT_OK` 里; 凡在 `REQUIRED_SINGLE` 里的网, 判 NC 就判红并点名哪一条** ★★**
- ★**★**方向纪律 (★本项目铁律★)★★: ★**只许【加严】不许【放宽】** ★ ⇒ ★**不许改 `HW/check_s8_target_list.py` 的 `REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*` (★那是板那一趟的判据, 一字不许动★) ⇒ ★**你只许【读】它 ★**
- ★**★**反向用例 (★必须有, 否则闸是装饰★)★★: ★**在 `tmp/` 副本上把 SW 页 §3 表某条必需网的「建议的板侧标记」改回「NC (不连)」⇒ 你的闸必须判红并点名那条网名 ⇒ 恢复原件 ⇒ 判绿 ★** ⇒ ★**★**把这条闸接到哪 / 怎么跑, 你自己定, 但【必须交得出这条反向用例的读数】★★
- ★**★**沙盒纪律★: 反向用例只在 `tmp/` 副本上做 ⇒ ★**真件 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 一个字节都不许在反向用例里被动 ★**

★**③ 把「固件侧要改哪一行」那份清单, 改成与终裁一致的版本 (★仍然只出清单, 一行固件都不许动★) ★**
- ★**ISS-338 §3 表第三列「悬空后固件侧要不要改」列的是具体 file:line (★main 已逐条核对过那些行号在盘且内容对得上, 见 §0④★) ⇒ ★**那 6 条既然**不改判成必需**, 它们对应的「固件侧要改」条目 (★降级声明 / 改判 / NC 标记★) 就**不再成立** ⇒ 你必须把那 6 条的「固件侧要改」清单标成「★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★」 ⇒ ★**而【不是】把它们改写成新的固件侧改动 (★那是板那一趟同批改的活, 不属本单★) ★**
- ★**`FSIN_OUT` 的那 4 处 (★`SW/INTEGRATION_PLAN.md:717` / `:844` · `SW/SW_REQUIREMENTS.md:684` · `SW/EVT_TEMPLATE.md:250`★) 保留在清单里, 但必须标注「★**板那一趟动作 · 现在只定口径不定动作**★」 ★**

---

## §2 边界 (★违反任一条 = 本单不成立★)

★**① 零写板**: `HW/PCB/demo_mainboard.kicad_pcb` md5 必须仍 = `611b869e13518c3c023fb178f91a0075`, mtime 仍 = `2026-11-06 07:07:17.362193413` ★ ⇒ ★**本单【不许】碰板** ★
★**② 零改固件本体**: ★**`SW/tools/s2_board_run.sh` · `SW/tools/s2_rescue_config.json` · `SW/tools/check_sw_ref_reachability.py` · `SW/tools/check_sw_ref_reachability_v2.py` · `SW/FLASH_AND_VERSION.md` · `SW/EVT_TEMPLATE.md` · `SW/S2_BOARD_TEST_CHECKLIST.md` · `SW/INTEGRATION_PLAN.md` · `SW/SW_REQUIREMENTS.md` · `SW/S2_VENDOR_QUESTION_LIST.md` · `SW/ONETRIP_SW_RENAME_SAFETY.md` · `SW/SW_TIMING_REVIEW.md` —— 一个字节都不许动** ★ ⇒ ★**本单只改 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` + 新建闸 + 交卷页 + 分片 ★**
★**③ 零改板侧判据**: ★**`HW/check_s8_target_list.py` 一字不许动 (★`REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*` 是板那一趟的判据★) ⇒ 只许读 ★**
★**④ 零落表**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 逐字节不变; ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一个字节不许碰** ★
★**⑤ 零改别人的分片**: ★**`state/fragments/pm.yaml` (main 的) / `hw.yaml` / `mech.yaml` 一个字节不许碰** ★ ⇒ ★**本单只许写 `state/fragments/sw.yaml` ★**
★**⑥ 零改 `MECH/` 任何文件** ★
★**⑦ 不许代拍**: ★**分级是 main 已裁的 (★终裁原文逐字引, 不许重新解释·不许提「建议默认值」★) ⇒ ★**本单是【对齐】不是【重判】★ ★**
★**⑧ 不许外发**: ★**零邮件 / 零询价 / 零问询 / 零采购 ★** ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★** ⇒ ★**没有「批一句可以发」这个选项 ★**
★**⑨ 不许替老板拍板**: ★**本单【不新增】任何老板拍板项 ★**
★**⑩ 引用零假引用**: 交卷页里引用的每个 `SW/*` / `HW/*` / `state/*` / `logs/*` 文件必须逐个在盘 ⇒ ★**交卷前自检一次, 输出贴进 §B6 ★**
★**⑪ `FSIN_OUT` 现在不许落 NC** (★终裁明写「标 NC 是板那一趟做·现在只定口径不动手」★) ★

---

## §3 交卷物 (★N 件, 缺一件即不算交卷★)

★**① 交卷页 `HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md` (★**新建**★) ⇒ ★**B1 结论摘要 / B2 验收标准逐条自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 ★**六块齐全 (★`state/gate_check.py` 的 `REQUIRED_BLOCKS` 就是这 6 块 + 证据分级标签 `[实测]/[官方]/[推算]/[0数据]`★) ⇒ ★**先落骨架再填内容 (★先 write 六个标题, 再逐块填·★不许一次性 write 大段★) ★**
★**② `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的追加式订正 (★落在真件, 老字一字不删★) ⇒ 交卷页给出 ★**老前缀 md5 前后对比 + `diff` 输出★ (★证明只增不删★) ★**
★**③ 新闸 `SW/tools/check_sw_zero_copper_grade_consistency.py` + 它的反向用例读数 (★落在 `logs/iss344/`) ★**
★**④ `state/fragments/sw.yaml` 登记 (★**只走 `python3 state/frag_write.py --agent sw-lead`★·零重复 key★) ⇒ ★**`grep -c iss344 state/fragments/sw.yaml` ≥ 3 ★**
★**⑤ `logs/iss344/` 原始输出 (★机器生成的命令输出, 一条命令能复现★) ★**

★**★必跑命令 (★全部是本机实存路径, `state/check_brief_commands.py --brief-file` 已验 rc=0★)★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb ; echo "S8_RC=$?"
TMPDIR=$PWD/tmp python3 SW/tools/check_sw_ref_reachability.py ; echo "REF_RC=$?"
TMPDIR=$PWD/tmp python3 SW/tools/check_onepass_sw_release.py ; echo "SWREL_RC=$?"
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

★**★交卷前必须跑 (§2 边界自证 + 主线闸) ★★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"     # ★rc 必须 0★
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"   # ★rc 必须 0 且 Q1 = 18/18★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
python3 state/frag_write.py --agent sw-lead --show | head -5
```
★**★回复 ≤ 500 字 + 4 行读数 (`S8_RC` / `REF_RC` / `GATE_RC` / `BOARD_MD5`) + 反向用例是否判红★★**

---

## §4 交卷时必须回答 main 的 3 个问题

★**① 「你逐条对出来的那 6 条冲突, 与 pm.yaml 的哪个 key 的哪句话对应? 逐条列出来」 ★**
★**② 「SW 那份文件里除了 §3 表, 还有哪几处在说旧分级? 行号逐个列」 ★**
★**③ 「你的闸反向用例: 把某条必需网改回 NC, 判红了没有? 点名了哪条?」 ★**

★**★额外纪律 (★派活方统一加, 一条都不许少★)★★**:
★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★) ★**
★**② 只写本任务允许的文件, 不碰别人的 (★特别是 `state/fragments/pm.yaml` = main 的分片★) ★**
★**③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 (★`USB_CC2` 那条要标 `[官网]`; 其余多为 `[实测]`+`[推算]`★) ★**
★**④ 不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项 ★**
★**⑤ 交卷前跑 `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复 ★**
