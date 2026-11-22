
---

## §7 ★★分级订正 (main 2026-11-22 20:5x 终裁) · ISS-344 追加式订正块★★

> ★**本节性质**: ★**追加式订正 (★老字一个字都没删·§7-4 有 diff 自证★)** ★
> ★**上游**: ★**main 2026-11-22 20:5x 的终裁 (★机制地界·不占老板拍板面★)** ★ ⇒ ★**本节是【对齐】, 不是【重判】** ★
> ★**机器真值 (★唯一尺子·只读★)**: ★**`HW/check_s8_target_list.py`** 的 `REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*` ★

### §7-0 ★★依据 (★逐字引 main 的终裁·`state/fragments/pm.yaml` → `answers`★)★★

- ★**`iss334_need4b_zero_copper_net_triage`** (★need-4b 分级【定稿】★): ★**「A 必需 (23 条) = ① 15 条高速差分腿 + ② 8 条单端脚 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · B 可悬空 (1 条) = `FSIN_OUT` (★条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作**★) · C 待定 (0 条)」** ★ → ★**[实测]** (★本机实跑 `HW/check_s8_target_list.py` ⇒ 「必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔」★)
- ★**`iss338_need_jtag_group_decision`**: ★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」** ★ → ★**[实测]** (★`R_JTAG_TDI` 在盘 · `J_DEBUG` 1×4 排针 · `TP_JTAG` · ★`JTAG_TCK`/`JTAG_TMS`/`JTAG_TDO` 都有铜 ⇒ 只裁 TDI = 调试口摆设★)
- ★**`iss338_need_boot_storage_answer`**: ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ → ★**[实测]** (★`J_BOOT1` 焊盘位已在板 ⇒ ★**布线保留的成本 ≈ 0 ⇒ 事后不用重出板**★)
- ★**`iss338_need_usbif_cc1_cc2_rule`**: ★**「裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的「板侧默认 NC + 保留 R_CC2_D」建议【不采纳】」** ★ → ★**[官网]** (★USB Type-C Cable and Connector Specification 原文: 「★**The USB Type-C receptacle presents Rd on both of its CC pins because a CC pull-down must be present for the receptacle to indicate that it wants to consume VBUS current.**」⇒ ★**USB 2.0-only 插座 = 双路 Rd ⇒ CC1/CC2 都要有 Rd ⇒ CC2 不可悬空**★) · ★**[媒体]** (★TI《A Primer on USB Type-C and Power Delivery Applications》: 一条 CC 线可能变 VCONN ⇒ 另一条仍须 Rd 做方向检测★) · ★**[媒体]** (★网上「单 Rd 省一颗电阻」只适用于 Source/DRP 侧 (★规范原文: 「Only one of the CC1 or CC2 pins shall be in the SRC.Rd state」·★那是【源端】条款★)·★公开来源之所以互相矛盾就是这两条被混着引用了★)
- ★**main 给 SW 侧的判据边界 (★逐字·在 `iss338_need_jtag_group_decision` 里★)**: ★**「『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】」** ★ → ★**[推算]** (★JTAG 与 UART 是【硬件接口】, 由调试器 / 探针驱动, 不由应用固件引用 ⇒ ★**SW 零引用对它不构成「可悬空」的证据**★)

★**⇒ 终裁口径 (★唯一有效★)**: ★**必需 23 · 可悬空 1 · 待定 0** ★ ⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 · 可悬空 1 · 待定 0** ★

### §7-1 ★★逐条订正表 (★旧说法 → 新说法 → 依据·★老字都在上面, 这里给有效口径★)★★

| ★net★ | ★旧说法 (ISS-338 · 2026-11-19)★ | ★新说法 (main 2026-11-22 20:5x 终裁)★ | ★依据 (pm.yaml key + 原文片段)★ | ★证据等级★ | ★固件侧「要改哪一行」清单★ |
|---|---|---|---|---|---|
| ★`CAM_RESET_N`★ | ★**必需** ★ | ★**必需** ★ (★**与终裁一致·无变化**★) | `iss334_need4b_zero_copper_net_triage` ★**「`CAM_RESET_N` (dts `reset-gpios gpio1 RK_PB3` ⇒ 相机不出图则 MIPI-CSI 链死)」** ★ | ★**[实测]** + ★**[官方]** ★ | ★**无需改** (★**从未判过 NC★**) ★ |
| ★`LED_G_D`★ | ★**必需** ★ | ★**必需** ★ (★**与终裁一致·无变化**★) | `iss334_need4b_zero_copper_net_triage` ★**「`LED_G_D` (同族 `LED_B_D`=105 段 / `LED_R_D`=169 段都有铜·只它 0 段 ⇒ 该布没布)」** ★ | ★**[实测]** ★ | ★**无需改** (★**从未判过 NC★**) ★ |
| ★`JTAG_TDI`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_jtag_group_decision` ★**「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (`SW/FLASH_AND_VERSION.md:336` / `:44` · `SW/EVT_TEMPLATE.md:503` · `SW/S2_BOARD_TEST_CHECKLIST.md:393`) ★**不再成立** ★ |
| ★`SPI_MISO_BOOT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_boot_storage_answer` ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (`SW/FLASH_AND_VERSION.md:359` / `:46` / `:527` · `SW/S2_VENDOR_QUESTION_LIST.md:315`) ★**不再成立** ★ |
| ★`SPI_MOSI_BOOT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_boot_storage_answer` ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (★**同 `SPI_MISO_BOOT`**★) ★**不再成立** ★ |
| ★`SPI_SCLK_BOOT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_boot_storage_answer` ★**「3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect」** ★ | ★**[实测]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 4 处 (★**同 `SPI_MISO_BOOT`**★) ★**不再成立** ★ |
| ★`UART_RX`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_jtag_group_decision` ★**「『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】⇒ 所以你那 9 条里 `JTAG_TDI` / `UART_RX` 的『可悬空』结论, main 不采信」** ★ | ★**[推算]** ★ | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 3 处 (`SW/S2_BOARD_TEST_CHECKLIST.md:94` · `SW/tools/s2_board_run.sh:248` · `SW/tools/s2_rescue_config.json:230`) ★**不再成立** ★ |
| ★`USB_CC2`★ | ★**待定** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ | `iss338_need_usbif_cc1_cc2_rule` ★**「裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的『板侧默认 NC + 保留 R_CC2_D』建议【不采纳』」** ★ | ★**[官网]** (★USB Type-C 规范原文·插座端双路 Rd★) | ★**作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)** ★ ⇒ 原 3 处 (`SW/ONETRIP_SW_RENAME_SAFETY.md:31` · `SW/SW_TIMING_REVIEW.md:274` · `SW/tools/check_sw_ref_reachability.py:185`) ★**不再成立** ★ |
| ★`FSIN_OUT`★ | ★**可悬空候选** ★ ⇒ ★**建议的板侧标记 = NC (不连)** ★ | ★**可悬空 (条件式) · 板那一趟动作 · 现在只定口径不定动作** ★ | `iss334_need4b_zero_copper_net_triage` ★**「B 可悬空 (1 条) = `FSIN_OUT` (★条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; ★**标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作**★)」** ★ | ★**[实测]** ★ | ★**保留在册 (4 处: `SW/INTEGRATION_PLAN.md:717` / `:844` · `SW/SW_REQUIREMENTS.md:684` · `SW/EVT_TEMPLATE.md:250`), 但标注「★板那一趟动作 · 现在只定口径不定动作★」** ★ |

★**★本页 9 条单端脚的有效口径 (★只此一份·与机器真值同源★)**: ★**必需 8 · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★

### §7-2 ★★固件侧「要改哪一行」清单 (★与终裁一致的版本·★仍然只出清单·一行固件都不许动★)★★

★**① 6 条必需网的「固件侧要改」条目 ⇒ 全部【作废】(★**不是改写成新的固件侧改动**★ · ★**那是板那一趟同批改的活·不属本单**★)** ★
- ★`JTAG_TDI` ⇒ ★**作废** ★ (原 4 处: `SW/FLASH_AND_VERSION.md:336` / `:44` · `SW/EVT_TEMPLATE.md:503` · `SW/S2_BOARD_TEST_CHECKLIST.md:393`)
- ★`SPI_MISO_BOOT` / `SPI_MOSI_BOOT` / `SPI_SCLK_BOOT` ⇒ ★**作废** ★ (原 4 处: `SW/FLASH_AND_VERSION.md:359` / `:46` / `:527` · `SW/S2_VENDOR_QUESTION_LIST.md:315`)
- ★`UART_RX` ⇒ ★**作废** ★ (原 3 处: `SW/S2_BOARD_TEST_CHECKLIST.md:94` · `SW/tools/s2_board_run.sh:248` · `SW/tools/s2_rescue_config.json:230`)
- ★`USB_CC2` ⇒ ★**作废** ★ (原 3 处: `SW/ONETRIP_SW_RENAME_SAFETY.md:31` · `SW/SW_TIMING_REVIEW.md:274` · `SW/tools/check_sw_ref_reachability.py:185`)
- ★★**依据**: pm.yaml → `iss338_need_jtag_group_decision` (★`JTAG_TDI` / `UART_RX★) · `iss338_need_boot_storage_answer` (★`SPI_*_BOOT★) · `iss338_need_usbif_cc1_cc2_rule` (★`USB_CC2★) · 证据等级 = ★**[实测]** / ★**[官网]** ★

★**② `FSIN_OUT` 的 4 处 ⇒ 保留在清单里, 但标注「★板那一趟动作 · 现在只定口径不定动作★」** ★
- `SW/INTEGRATION_PLAN.md:717` (IR-03) · `SW/INTEGRATION_PLAN.md:844` (B-5) · `SW/SW_REQUIREMENTS.md:684` (M-2 示波器法) · `SW/EVT_TEMPLATE.md:250` (E2E-05)
- ★★**本单现在【不动】这 4 处** ★ ⇒ ★**标 NC 是板那一趟的板侧动作** ★

★**③ `CAM_RESET_N` / `LED_G_D` ⇒ 无需改 (★**从未判过 NC**★)** ★

### §7-3 ★★机器闸 (★SW 侧分级与板侧真值不许再分叉★)★★

★**闸脚本**: ★**`SW/tools/check_sw_zero_copper_grade_consistency.py`** (★ISS-344 新建★) ★
★**真值源**: ★**`HW/check_s8_target_list.py`** 的 `REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*` (★**只读·AST 静态解析·不执行它的代码·一个字都不许动**★) ★

★**判据 (★逐条可单测★)** ★★
- ★**C0** ★**跨节一致**: §3/§3-1 表的「建议的板侧标记」必须与 §7 订正表的「新说法」判出同一档 ★
- ★**C1** ★**凡判 NC 的网, 必须在 `FLOAT_OK` 里** ⇒ 否则判红并点名 ★
- ★**C2** ★**凡在 `REQUIRED_SINGLE` 里的网, 判 NC 就判红并点名** ★
- ★**C3** ★**`REQUIRED_SINGLE` 的每一条都必须在 SW 页里被判成【必需】** ★
- ★**C4** ★**`FLOAT_OK` 的网不得被 SW 页判成【必需】** ★
- ★**C5** ★**`REQUIRED_SINGLE` 的网, 其「固件侧要改哪一行」清单必须标「作废」** ★
- ★**C6** ★**待定档必须为空** (终裁: 待定 0 条) ★
- ★**C7** ★**板侧名单之外的网, 不许被 SW 页判成 NC 或必需** ★
- ★**C8** ★**标记类别认不出来** ⇒ 判红 (不许糊过去) ★
- ★**C9** ★**§2 表「分级」列与 §3 标记同档** (加分项) ★

★**怎么跑 (★一条命令能复现★)** ★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_sw_zero_copper_grade_consistency.py ; echo "GATE344_RC=$?"
# ★反向用例 (★只在 tmp/ 副本上做·真件一个字节都不许被动★): ★
python3 SW/tools/check_sw_zero_copper_grade_consistency.py --doc tmp/iss344/rev/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md ; echo "REV_RC=$?"
```

### §7-4 ★★只增不删自证 (★老字一字未删 = 可自证★)★★

★**★为什么不能用 `diff | grep -c '^<'` 当证据 (★本项目老坑·这里说清楚★)**: ★**§3/§2 表里有 14 行是【行内插入】(在单元格中间插字) ⇒ 行级 diff 会把这 14 行同时打成 `<` 和 `>` ⇒ 行级 diff 看不出「只增不删」** ★ ⇒ ★**必须按【字符级子序列】证明** ★

★**自证命令 (★一条能复现★)** ★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 logs/iss344/check_only_additions.py \
     tmp/iss344/orig_ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md \
     SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md ; echo "ONLYADD_RC=$?"
# ★三条判据全过才算过: ① 逐行 (老行逐字原样仍在, 或老行是某新行的字符子序列)
#   ② 全文 (老文件全文是新文件全文的字符子序列 ⇒ 全局一个字符都没被删)
#   ③ 行数只增不减 ★
# ★人工可读的完整 diff 落在 `logs/iss344/05_diff_only_additions.txt`
#   (★那 14 个 `<` 行 = 14 个被【行内插入】的表格行·不是删除★) ★
```

★**订正执行器**: ★**`logs/iss344/apply_iss344_corrections.py`** (★**只做插入·不做替换·自证用 difflib 校验无 delete 操作 + 逐行字符子序列校验**★) ★
★**订正源块**: ★**`logs/iss344/iss344_sec7.md`** (★本节 §7 的来源·可重放★) ★
