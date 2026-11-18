# ONETRIP · S1 三侧同口径位号改名 —— 可执行清单 + NC 白名单解法 + BOM 证据回填判据

> ★**单号**: ISS-317 · ★**owner**: hw-lead (硬件总工) · ★**verify_by**: main · ★**job**: cron `fb67af40`
> ★**性质**: 内部活 · 纯分析 / 作业包 / 判据设计类 (HW 侧) · ★**零写板 · 零落表 · 零重生成 · 零改闸**
> ★**上游**: ISS-314 (verified) 的「口径决策包」· ★**下游**: 待 main 拍板 need `s1_ref_rename_caliber_20261118`
> ★**本文件所有数字都是从 `logs/iss317/` 的机器生成原始输出逐字搬来的** (★装配器 `logs/iss317/iss317_write_deliverable.py` 自带行数校验·不符即 abort★)

---

## §0 口径与边界自证

### §0-1 · 本单交付了什么 (★一句话★)

★**S1 位号改名不是「板侧 186 个封装改名」, 而是【表侧 218 个真实器件里 186 个改名】 ⇒ 真正要同口径同步的是【五侧】(板 + 网表 + 脚表 + BOM + 原理图) 而非 ISS-314 说的「三侧」; 并且【NC 白名单只豁免 1 个 ref: `J_USB_C`】, 不是 5 个也不是「186 个里挑一批」; 甲/乙/丙三选项的代价已用沙盒实跑量化, 且【丙的裸前缀写法会放过真错 ⇒ 只推荐丙-②(正则锚定)】★

### §0-2 · 改名口径 (★单源·逐字比对不一致即 abort★)

```
口径单源 = state/gen_kicad_sch.py::kicad_ref()
    末字符是数字 ⇒ 不动
    否则        ⇒ 加 "_1"
```

★**本单不改这个口径** (★只出清单·一个字节都不许落★) · 装配器 `logs/iss317/iss317_gen_rename_list.py` 在生成清单时对 `state/gen_kicad_sch.py` 的源码做正则逐字比对, **对不上就 abort** ★

### §0-3 · 边界自证 (★本单做到 / 没做到★)

| 边界 | 本单怎么保证 | 自证 |
|---|---|---|
| ★**零写板** ★ | 只读 `HW/PCB/demo_mainboard.kicad_pcb`; 所有改名都在 `tmp/iss317_sandbox/` 的副本上做 | ★md5 + mtime 交卷前后逐字节相同 (§6-1)★ |
| ★**零落表** ★ | 只读网表/脚表/BOM; 沙盒副本写 `tmp/iss317_sandbox/` | ★md5 交卷前后相同 (§6-1)★ |
| ★**零重生成** ★ | ★**一个生成器都没跑** (gen_netlist / gen_kicad_sch / gen_pcb_netlist_board / gen_bom 全部不跑) ★ | §6-3 命令清单可核 |
| ★**零改闸** ★ | 判据脚本只读; 沙盒副本 = ISS-314 留档副本 + 沙盒 harness (★`--pcb=` / selftest 落沙盒★) | ★项目闸脚本 md5 未变 (§6-1)★ |
| ★**零改既有文档正文** ★ | 本文件是**新建**交付物; 既有文档一个字节没动 | ★§6-3★ |
| ★**沙盒只写 `tmp/`** ★ | 所有沙盒产物落 `tmp/iss317_sandbox/`; ★**不写 `/tmp`** (★本机 `/tmp` 带 usrquota 且配额已满 ⇒ 假红★) | ★§6-2 目录清单★ |
| ★**零外发** ★ | ★**没发任何邮件/询价/问询/采购** ★官网资料全部自己 `curl` 下载 | ★§4 U-2/U-3 的 URL + 快照 md5★ |
| ★**不替老板拍板** ★ | 甲/乙/丙 + 丙-①/丙-② 全部列出代价, **一条都没替老板定** | ★§2-5★ |
| ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节没动 | ★status/verify_result 留给 main★ |

### §0-4 · ★**这一趟修掉了上一趟沙盒的 3 个缺陷** (★不然下面的读数全是假的★)

★**上一趟 (cont1) 的沙盒 `logs/iss317/iss317_sb_make.py` 有三个缺陷, 导致 A0/A1 读数被污染、乙/丙两场直接崩掉** ★

| # | 缺陷 | 后果 | 修法 (★v2 = `logs/iss317/iss317_sb_make_v2.py`★) |
|---|---|---|---|
| ① | 网表改名★按行★做 (ref 列按行判豁免·node 串整串不判) | 甲方案里 `ref=J_USB_C` 那行的 `node2="R_CC1_D"` 没改名 ⇒ 表侧宇宙少了 `R_CC1_D` ⇒ **假 delta** | ★改成按【token】判★ |
| ② | node 串里的★裸网名★也被改名 (`GND` ⇒ `GND_1`) | 网名被当器件改 ⇒ 判据读到的是不存在的网 | ★只有【真·器件宇宙 U】里的 token 才改名★ (★U = 218 个★) |
| ③ | `J_USB_C` 在 `rename_node` 里被★硬编死豁免★ | 连「全改名」场里 node 串的 `J_USB_C` 也没改名 ⇒ A0 场「缺失4/多余16」里★有 14 条是假的★ | ★豁免集合改由参数传入, 零硬编★ |

★**另修**: 乙方案的 `--selftest` 目标行替换写在 `if` 后面 ⇒ ★**Python 语法错**★ (A2 场直接 `SyntaxError` 崩掉); 丙方案的 `_nc_allowed` 替换★命中了自己★ ⇒ ★**无限递归**★ (A3/A4 场 `RecursionError` 崩掉) ★

★**修完之后 A0 场读数从「缺失4/多余16」变成「缺失0/多余2」—— 这才是真读数** ★

### §0-5 · ★**这一趟还修掉了改名清单生成器的一个列宽缺陷** (★不然 §1 表的「同步清单」是残的★)

★**上一趟的 `logs/iss317/iss317_gen_rename_list.py` 在打印 §D 表时把「改哪个真源(★同步清单★)」列只留了 22 字符宽 ⇒ ★被截断★** ★

| 后果 | 实测 |
|---|---|
| ★**35 个 ref 的同步清单被截断** ★ | ★其中 `J_USB_C` 丢了 3 条 (`GAP29` / `PLACE_OVERRIDE` / `NC_ALLOWED`)· `CONN_CAM` 丢了 2 条 (`CONN_CAM_PIN` / `--selftest 目标`) ★ |
| ★**后果很直接** ★ | ★**`NC_ALLOWED` 那条正是 §2 的核心** —— 它被切掉 ⇒ ★**看表的人根本不知道 `J_USB_C` 在白名单里** ★ |

★**修法 (★`logs/iss317/iss317_gen_rename_list_v2.py`★)**: 该列加宽到 160 + ★**额外输出 TSV 行** (★机器解析用·不受列宽/全角字符影响★)★ ⇒ 本文件的 §1 表从 TSV 行逐字搬来, 装配器还独立复核了「新ref == kicad_ref(旧ref)」逐行成立 ★

★**v1 的 `logs/iss317/rename_list_raw.txt` 保留在盘上作对照 (★它的 §D 表是残的·别拿它交卷★)** ★

---

## §1 逐条改名对照表 (★218 行·机器搬·一行不许漏·一行不许手抄★)

### §1-1 · 三个必须先说清的数

```
改名宇宙 (表侧真实器件)          : 218
★要改 (末字符是字母 ⇒ 加 _1)     : 186
★不动 (末字符是数字 ⇒ 一律不动)  :  32   ← ★ISS-314 说的「30 个不动」是【板侧】口径, 表侧是 32★
  · 其中在板侧 (MAIN_PCB)        : 156 要改 /  30 不动
  · 其中不在板侧 (CHG_BOARD)     :  30 要改 /   2 不动
```

★**⇒ 结论 1 (本单最重要的一条)**: 「三侧同口径」在计数上不完整 ⇒ ★**实际是【五侧同口径】** ★
★板侧只动 156 个, 而网表/脚表/BOM/原理图四侧要动 186 个 ⇒ ★**只改板侧 ⇒ 必然 C1 炸** (ISS-314 S3 实测 缺失350/多余352)★

★**⇒ 结论 2**: 「32 个不动」vs ISS-314 的「30 个不动」不是矛盾, 是口径差 —— 差 2 个 = ★板上没有、脚表里有的 CHG_BOARD 件: `R_CC1` / `R_CC2` ★

★**⇒ 结论 3**: ★**NC 白名单 5 个 ref 里, 末字符是数字 ⇒ 本来就不动: 4 个** (`J_SOM_P1` `J_SOM_P2` `J_SOM_P3` `J_SOM_P4`) ⇒ ★**真正需要豁免的只有 1 个: `J_USB_C`** ★ ⇒ 豁免清单 = 1 个 ref, 不是 5 个, 也不是「186 个里挑一批」

### §1-2 · 逐条对照表 (★共 218 行·每一行一个 ref★)

★**读表须知** ★

- 「旧ref(脚表侧现值)」与「旧ref(板侧现值)」★本机实测两侧【完全一致】★ (★board ⊆ pins 且逐名相同★)
  ⇒ ★真正分叉的是【表侧/板侧 (不带 `_1`)】 vs 【原理图侧 (带 `_1`)】★ ⇒ 第三列给的是原理图侧现值
- 「改哪个真源」列给的是★除四侧产物外★还要同批同步的★生成器/判据硬编码★清单
- 「改完的预期读数」= 改名后 C1 三项 (缺失/多余/同号异网) 的预期 ⇒ ★改名【不】解掉现状 5 条 delta★

| # | 旧ref(脚表侧现值) | 旧ref(板侧现值) | 旧ref(原理图侧现值) | 新ref(kicad_ref口径) | 改哪个真源(★同步清单★) | 板侧 | 动/不动 | 改完的预期读数 | 依赖顺序 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BT_432243 | BT_432243 | BT_432243 | BT_432243 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 2 | CHG_GND_STAR | CHG_GND_STAR | CHG_GND_STAR_1 | CHG_GND_STAR_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 3 | CONN_CAM | CONN_CAM | CONN_CAM_1 | CONN_CAM_1 | 四侧产物 + gen_pcb_netlist_board.py:221 CONN_CAM_PIN; check_pcb_nets.py:402 --selftest 目标 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 4 | CONN_LIGHT | CONN_LIGHT | CONN_LIGHT_1 | CONN_LIGHT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 5 | C_AC_CSI_D0_CK_N | C_AC_CSI_D0_CK_N | C_AC_CSI_D0_CK_N_1 | C_AC_CSI_D0_CK_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 6 | C_AC_CSI_D0_CK_P | C_AC_CSI_D0_CK_P | C_AC_CSI_D0_CK_P_1 | C_AC_CSI_D0_CK_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 7 | C_AC_CSI_D0_D0_N | C_AC_CSI_D0_D0_N | C_AC_CSI_D0_D0_N_1 | C_AC_CSI_D0_D0_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 8 | C_AC_CSI_D0_D0_P | C_AC_CSI_D0_D0_P | C_AC_CSI_D0_D0_P_1 | C_AC_CSI_D0_D0_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 9 | C_AC_CSI_D0_D1_N | C_AC_CSI_D0_D1_N | C_AC_CSI_D0_D1_N_1 | C_AC_CSI_D0_D1_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 10 | C_AC_CSI_D0_D1_P | C_AC_CSI_D0_D1_P | C_AC_CSI_D0_D1_P_1 | C_AC_CSI_D0_D1_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 11 | C_AC_CSI_D0_D2_N | C_AC_CSI_D0_D2_N | C_AC_CSI_D0_D2_N_1 | C_AC_CSI_D0_D2_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 12 | C_AC_CSI_D0_D2_P | C_AC_CSI_D0_D2_P | C_AC_CSI_D0_D2_P_1 | C_AC_CSI_D0_D2_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 13 | C_AC_CSI_D0_D3_N | C_AC_CSI_D0_D3_N | C_AC_CSI_D0_D3_N_1 | C_AC_CSI_D0_D3_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 14 | C_AC_CSI_D0_D3_P | C_AC_CSI_D0_D3_P | C_AC_CSI_D0_D3_P_1 | C_AC_CSI_D0_D3_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 15 | C_BAT | —(不在本板·CHG_BOARD) | C_BAT_1 | C_BAT_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 16 | C_BST | —(不在本板·CHG_BOARD) | C_BST_1 | C_BST_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 17 | C_BULK_LIGHT_1V8 | C_BULK_LIGHT_1V8 | C_BULK_LIGHT_1V8 | C_BULK_LIGHT_1V8 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 18 | C_BULK_LIGHT_3V3 | C_BULK_LIGHT_3V3 | C_BULK_LIGHT_3V3 | C_BULK_LIGHT_3V3 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 19 | C_BULK_SENSOR_AVDD | C_BULK_SENSOR_AVDD | C_BULK_SENSOR_AVDD_1 | C_BULK_SENSOR_AVDD_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 20 | C_BULK_SENSOR_CORE | C_BULK_SENSOR_CORE | C_BULK_SENSOR_CORE_1 | C_BULK_SENSOR_CORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 21 | C_BULK_SENSOR_VDD_IO | C_BULK_SENSOR_VDD_IO | C_BULK_SENSOR_VDD_IO_1 | C_BULK_SENSOR_VDD_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 22 | C_BULK_VDD_1V8_IO | C_BULK_VDD_1V8_IO | C_BULK_VDD_1V8_IO_1 | C_BULK_VDD_1V8_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 23 | C_BULK_VDD_3V3_IO | C_BULK_VDD_3V3_IO | C_BULK_VDD_3V3_IO_1 | C_BULK_VDD_3V3_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 24 | C_BULK_V_CORE | C_BULK_V_CORE | C_BULK_V_CORE_1 | C_BULK_V_CORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 25 | C_BULK_V_SOC_IO | C_BULK_V_SOC_IO | C_BULK_V_SOC_IO_1 | C_BULK_V_SOC_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 26 | C_DET_BAT | C_DET_BAT | C_DET_BAT_1 | C_DET_BAT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 27 | C_DET_VBUS_D | C_DET_VBUS_D | C_DET_VBUS_D_1 | C_DET_VBUS_D_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 28 | C_HF_LIGHT_1V8 | C_HF_LIGHT_1V8 | C_HF_LIGHT_1V8 | C_HF_LIGHT_1V8 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 29 | C_HF_LIGHT_3V3 | C_HF_LIGHT_3V3 | C_HF_LIGHT_3V3 | C_HF_LIGHT_3V3 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 30 | C_HF_SENSOR_AVDD | C_HF_SENSOR_AVDD | C_HF_SENSOR_AVDD_1 | C_HF_SENSOR_AVDD_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 31 | C_HF_SENSOR_CORE | C_HF_SENSOR_CORE | C_HF_SENSOR_CORE_1 | C_HF_SENSOR_CORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 32 | C_HF_SENSOR_VDD_IO | C_HF_SENSOR_VDD_IO | C_HF_SENSOR_VDD_IO_1 | C_HF_SENSOR_VDD_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 33 | C_HF_VDD_1V8_IO | C_HF_VDD_1V8_IO | C_HF_VDD_1V8_IO_1 | C_HF_VDD_1V8_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 34 | C_HF_VDD_3V3_IO | C_HF_VDD_3V3_IO | C_HF_VDD_3V3_IO_1 | C_HF_VDD_3V3_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 35 | C_HF_V_CORE | C_HF_V_CORE | C_HF_V_CORE_1 | C_HF_V_CORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 36 | C_HF_V_SOC_IO | C_HF_V_SOC_IO | C_HF_V_SOC_IO_1 | C_HF_V_SOC_IO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 37 | C_KEY_CAM | C_KEY_CAM | C_KEY_CAM_1 | C_KEY_CAM_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 38 | C_KEY_PWR | C_KEY_PWR | C_KEY_PWR_1 | C_KEY_PWR_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 39 | C_KEY_VM | C_KEY_VM | C_KEY_VM_1 | C_KEY_VM_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 40 | C_KEY_VP | C_KEY_VP | C_KEY_VP_1 | C_KEY_VP_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 41 | C_PMID | —(不在本板·CHG_BOARD) | C_PMID_1 | C_PMID_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 42 | C_REGN | —(不在本板·CHG_BOARD) | C_REGN_1 | C_REGN_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 43 | C_RST | C_RST | C_RST_1 | C_RST_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 44 | C_SUPV | C_SUPV | C_SUPV_1 | C_SUPV_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 45 | C_SW_IN | C_SW_IN | C_SW_IN_1 | C_SW_IN_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 46 | C_SW_OUT | C_SW_OUT | C_SW_OUT_1 | C_SW_OUT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 47 | C_SYS | —(不在本板·CHG_BOARD) | C_SYS_1 | C_SYS_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 48 | C_TEMP | C_TEMP | C_TEMP_1 | C_TEMP_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 49 | C_VBUS_DEMO | C_VBUS_DEMO | C_VBUS_DEMO_1 | C_VBUS_DEMO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 50 | C_VBUS_GND | C_VBUS_GND | C_VBUS_GND_1 | C_VBUS_GND_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | ★仍点名该 ref ⇒ delta 不变★ | BATCH-1 背靠背 |
| 51 | C_VBUS_IC | —(不在本板·CHG_BOARD) | C_VBUS_IC_1 | C_VBUS_IC_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 52 | C_VBUS_IN | —(不在本板·CHG_BOARD) | C_VBUS_IN_1 | C_VBUS_IN_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 53 | C_VBUS_OUT | —(不在本板·CHG_BOARD) | C_VBUS_OUT_1 | C_VBUS_OUT_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 54 | C_XTAL_IN | C_XTAL_IN | C_XTAL_IN_1 | C_XTAL_IN_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 55 | C_XTAL_OUT | C_XTAL_OUT | C_XTAL_OUT_1 | C_XTAL_OUT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 56 | D_CHG_LED | —(不在本板·CHG_BOARD) | D_CHG_LED_1 | D_CHG_LED_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 57 | D_ESD_CAM | D_ESD_CAM | D_ESD_CAM_1 | D_ESD_CAM_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 58 | D_ESD_DEMO | D_ESD_DEMO | D_ESD_DEMO_1 | D_ESD_DEMO_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 59 | D_ESD_LIGHT | D_ESD_LIGHT | D_ESD_LIGHT_1 | D_ESD_LIGHT_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 60 | D_ESD_TC | —(不在本板·CHG_BOARD) | D_ESD_TC_1 | D_ESD_TC_1 | 四侧产物 + gen_bom.py:307 GAP29 | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 61 | D_ESD_USB_D | D_ESD_USB_D | D_ESD_USB_D_1 | D_ESD_USB_D_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | ★仍点名该 ref ⇒ delta 不变★ | BATCH-1 背靠背 |
| 62 | D_LED_B | D_LED_B | D_LED_B_1 | D_LED_B_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 63 | D_LED_G | D_LED_G | D_LED_G_1 | D_LED_G_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 64 | D_LED_R | D_LED_R | D_LED_R_1 | D_LED_R_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 65 | D_TVS_VBUS | —(不在本板·CHG_BOARD) | D_TVS_VBUS_1 | D_TVS_VBUS_1 | 四侧产物 + gen_bom.py:307 GAP29 | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 66 | FB_DEMO | FB_DEMO | FB_DEMO_1 | FB_DEMO_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 67 | FB_VBUS | —(不在本板·CHG_BOARD) | FB_VBUS_1 | FB_VBUS_1 | 四侧产物 + gen_bom.py:307 GAP29 | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 68 | J_BOOT1 | J_BOOT1 | J_BOOT1 | J_BOOT1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 69 | J_CHG | J_CHG | J_CHG_1 | J_CHG_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 70 | J_DEBUG | J_DEBUG | J_DEBUG_1 | J_DEBUG_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 71 | J_SOM_P1 | J_SOM_P1 | J_SOM_P1 | J_SOM_P1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 72 | J_SOM_P2 | J_SOM_P2 | J_SOM_P2 | J_SOM_P2 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 73 | J_SOM_P3 | J_SOM_P3 | J_SOM_P3 | J_SOM_P3 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 74 | J_SOM_P4 | J_SOM_P4 | J_SOM_P4 | J_SOM_P4 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 75 | J_TYPE_C | —(不在本板·CHG_BOARD) | J_TYPE_C_1 | J_TYPE_C_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 76 | J_UART | J_UART | J_UART_1 | J_UART_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 77 | J_USB_C | J_USB_C | J_USB_C_1 | J_USB_C_1 | 四侧产物 + gen_bom.py:307 GAP29; gen_pcb_netlist_board.py:203 PLACE_OVERRIDE; check_pcb_nets.py:260-265 NC_ALLOWED | 在 | 改名 | ★非法NC 3 + C3 不符1★ (撞白名单) | BATCH-1 背靠背 |
| 78 | L_CHG | —(不在本板·CHG_BOARD) | L_CHG_1 | L_CHG_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 79 | Q1 | Q1 | Q1 | Q1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 80 | Q2 | Q2 | Q2 | Q2 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 81 | Q_AND | Q_AND | Q_AND_1 | Q_AND_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 82 | Q_CHG_LED | —(不在本板·CHG_BOARD) | Q_CHG_LED_1 | Q_CHG_LED_1 | 四侧产物 + gen_bom.py:307 GAP29 | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 83 | Q_ENVC | Q_ENVC | Q_ENVC_1 | Q_ENVC_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 84 | Q_PG | Q_PG | Q_PG_1 | Q_PG_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | ★仍点名该 ref ⇒ delta 不变★ | BATCH-1 背靠背 |
| 85 | R_BAT_DET_1 | R_BAT_DET_1 | R_BAT_DET_1 | R_BAT_DET_1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 86 | R_BAT_DET_2 | R_BAT_DET_2 | R_BAT_DET_2 | R_BAT_DET_2 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 87 | R_CC1 | —(不在本板·CHG_BOARD) | R_CC1 | R_CC1 | ★无需改 (已同口径)★ | 不在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 88 | R_CC1_D | R_CC1_D | R_CC1_D_1 | R_CC1_D_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 89 | R_CC2 | —(不在本板·CHG_BOARD) | R_CC2 | R_CC2 | ★无需改 (已同口径)★ | 不在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 90 | R_CC2_D | R_CC2_D | R_CC2_D_1 | R_CC2_D_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 91 | R_CE | —(不在本板·CHG_BOARD) | R_CE_1 | R_CE_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 92 | R_CHG_LED | —(不在本板·CHG_BOARD) | R_CHG_LED_1 | R_CHG_LED_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 93 | R_EN_VCORE | R_EN_VCORE | R_EN_VCORE_1 | R_EN_VCORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 94 | R_ID_JMP0 | R_ID_JMP0 | R_ID_JMP0 | R_ID_JMP0 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 95 | R_ID_JMP1 | R_ID_JMP1 | R_ID_JMP1 | R_ID_JMP1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 96 | R_ILIM | —(不在本板·CHG_BOARD) | R_ILIM_1 | R_ILIM_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 97 | R_JTAG_TCK | R_JTAG_TCK | R_JTAG_TCK_1 | R_JTAG_TCK_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 98 | R_JTAG_TDI | R_JTAG_TDI | R_JTAG_TDI_1 | R_JTAG_TDI_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 99 | R_JTAG_TDO | R_JTAG_TDO | R_JTAG_TDO_1 | R_JTAG_TDO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 100 | R_JTAG_TMS | R_JTAG_TMS | R_JTAG_TMS_1 | R_JTAG_TMS_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 101 | R_KEY_CAM | R_KEY_CAM | R_KEY_CAM_1 | R_KEY_CAM_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 102 | R_KEY_PWR | R_KEY_PWR | R_KEY_PWR_1 | R_KEY_PWR_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 103 | R_KEY_VM | R_KEY_VM | R_KEY_VM_1 | R_KEY_VM_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 104 | R_KEY_VP | R_KEY_VP | R_KEY_VP_1 | R_KEY_VP_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 105 | R_LED_B | R_LED_B | R_LED_B_1 | R_LED_B_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 106 | R_LED_G | R_LED_G | R_LED_G_1 | R_LED_G_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 107 | R_LED_R | R_LED_R | R_LED_R_1 | R_LED_R_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 108 | R_NTC_BAT | R_NTC_BAT | R_NTC_BAT_1 | R_NTC_BAT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 109 | R_OTG | —(不在本板·CHG_BOARD) | R_OTG_1 | R_OTG_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 110 | R_PD_ON | R_PD_ON | R_PD_ON_1 | R_PD_ON_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 111 | R_PG_PULL | R_PG_PULL | R_PG_PULL_1 | R_PG_PULL_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 112 | R_PSEL | —(不在本板·CHG_BOARD) | R_PSEL_1 | R_PSEL_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 113 | R_PU_BOOT_N | R_PU_BOOT_N | R_PU_BOOT_N_1 | R_PU_BOOT_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 114 | R_PU_CHG_STAT | —(不在本板·CHG_BOARD) | R_PU_CHG_STAT_1 | R_PU_CHG_STAT_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 115 | R_PU_I2CA_SCL | R_PU_I2CA_SCL | R_PU_I2CA_SCL_1 | R_PU_I2CA_SCL_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 116 | R_PU_I2CA_SDA | R_PU_I2CA_SDA | R_PU_I2CA_SDA_1 | R_PU_I2CA_SDA_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 117 | R_PU_I2CB_SCL | R_PU_I2CB_SCL | R_PU_I2CB_SCL_1 | R_PU_I2CB_SCL_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 118 | R_PU_I2CB_SDA | R_PU_I2CB_SDA | R_PU_I2CB_SDA_1 | R_PU_I2CB_SDA_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 119 | R_PU_ID0 | R_PU_ID0 | R_PU_ID0 | R_PU_ID0 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 120 | R_PU_ID1 | R_PU_ID1 | R_PU_ID1 | R_PU_ID1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 121 | R_PU_INT | —(不在本板·CHG_BOARD) | R_PU_INT_1 | R_PU_INT_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 122 | R_PU_PG | R_PU_PG | R_PU_PG_1 | R_PU_PG_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 123 | R_PU_RESET_N | R_PU_RESET_N | R_PU_RESET_N_1 | R_PU_RESET_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 124 | R_PU_SCL | —(不在本板·CHG_BOARD) | R_PU_SCL_1 | R_PU_SCL_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 125 | R_PU_SDA | —(不在本板·CHG_BOARD) | R_PU_SDA_1 | R_PU_SDA_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 126 | R_SEL_CK_N | R_SEL_CK_N | R_SEL_CK_N_1 | R_SEL_CK_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 127 | R_SEL_CK_P | R_SEL_CK_P | R_SEL_CK_P_1 | R_SEL_CK_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 128 | R_SEL_D0_N | R_SEL_D0_N | R_SEL_D0_N_1 | R_SEL_D0_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 129 | R_SEL_D0_P | R_SEL_D0_P | R_SEL_D0_P_1 | R_SEL_D0_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 130 | R_SEL_D1_N | R_SEL_D1_N | R_SEL_D1_N_1 | R_SEL_D1_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 131 | R_SEL_D1_P | R_SEL_D1_P | R_SEL_D1_P_1 | R_SEL_D1_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 132 | R_SEL_D2_N | R_SEL_D2_N | R_SEL_D2_N_1 | R_SEL_D2_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 133 | R_SEL_D2_P | R_SEL_D2_P | R_SEL_D2_P_1 | R_SEL_D2_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 134 | R_SEL_D3_N | R_SEL_D3_N | R_SEL_D3_N_1 | R_SEL_D3_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 135 | R_SEL_D3_P | R_SEL_D3_P | R_SEL_D3_P_1 | R_SEL_D3_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 136 | R_SER_CSI_MCLK | R_SER_CSI_MCLK | R_SER_CSI_MCLK_1 | R_SER_CSI_MCLK_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 137 | R_SER_FSIN | R_SER_FSIN | R_SER_FSIN_1 | R_SER_FSIN_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 138 | R_SER_RESET_N | R_SER_RESET_N | R_SER_RESET_N_1 | R_SER_RESET_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 139 | R_SER_SPI_CSn | R_SER_SPI_CSn | R_SER_SPI_CSn_1 | R_SER_SPI_CSn_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 140 | R_SER_SPI_MISO | R_SER_SPI_MISO | R_SER_SPI_MISO_1 | R_SER_SPI_MISO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 141 | R_SER_SPI_MOSI | R_SER_SPI_MOSI | R_SER_SPI_MOSI_1 | R_SER_SPI_MOSI_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 142 | R_SER_SPI_SCLK | R_SER_SPI_SCLK | R_SER_SPI_SCLK_1 | R_SER_SPI_SCLK_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 143 | R_SER_USB_D_N | R_SER_USB_D_N | R_SER_USB_D_N_1 | R_SER_USB_D_N_1 | 四侧产物 + gen_pcb_netlist_board.py:203 PLACE_OVERRIDE | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 144 | R_SER_USB_D_P | R_SER_USB_D_P | R_SER_USB_D_P_1 | R_SER_USB_D_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 145 | R_STAR_PGND | —(不在本板·CHG_BOARD) | R_STAR_PGND_1 | R_STAR_PGND_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 146 | R_SUPV_DIV1 | R_SUPV_DIV1 | R_SUPV_DIV1 | R_SUPV_DIV1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 147 | R_SUPV_DIV2 | R_SUPV_DIV2 | R_SUPV_DIV2 | R_SUPV_DIV2 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 148 | R_TS_PULL | R_TS_PULL | R_TS_PULL_1 | R_TS_PULL_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 149 | R_TS_TOP | —(不在本板·CHG_BOARD) | R_TS_TOP_1 | R_TS_TOP_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 150 | R_VBUS_DET_D1 | R_VBUS_DET_D1 | R_VBUS_DET_D1 | R_VBUS_DET_D1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 151 | R_VBUS_DET_D2 | R_VBUS_DET_D2 | R_VBUS_DET_D2 | R_VBUS_DET_D2 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 152 | SW_BOOT | SW_BOOT | SW_BOOT_1 | SW_BOOT_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 153 | SW_KEY_CAM | SW_KEY_CAM | SW_KEY_CAM_1 | SW_KEY_CAM_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 154 | SW_KEY_PWR | SW_KEY_PWR | SW_KEY_PWR_1 | SW_KEY_PWR_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 155 | SW_KEY_VM | SW_KEY_VM | SW_KEY_VM_1 | SW_KEY_VM_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 156 | SW_KEY_VP | SW_KEY_VP | SW_KEY_VP_1 | SW_KEY_VP_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 157 | SW_RST | SW_RST | SW_RST_1 | SW_RST_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 158 | TP_BAT | TP_BAT | TP_BAT_1 | TP_BAT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 159 | TP_BAT_CHG | TP_BAT_CHG | TP_BAT_CHG_1 | TP_BAT_CHG_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 160 | TP_BOOT | TP_BOOT | TP_BOOT_1 | TP_BOOT_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 161 | TP_CHG_STAT | —(不在本板·CHG_BOARD) | TP_CHG_STAT_1 | TP_CHG_STAT_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 162 | TP_CSI_CK_N | TP_CSI_CK_N | TP_CSI_CK_N_1 | TP_CSI_CK_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 163 | TP_CSI_CK_P | TP_CSI_CK_P | TP_CSI_CK_P_1 | TP_CSI_CK_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 164 | TP_CSI_D0_N | TP_CSI_D0_N | TP_CSI_D0_N_1 | TP_CSI_D0_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 165 | TP_CSI_D0_P | TP_CSI_D0_P | TP_CSI_D0_P_1 | TP_CSI_D0_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 166 | TP_DSI_CK_N | TP_DSI_CK_N | TP_DSI_CK_N_1 | TP_DSI_CK_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 167 | TP_DSI_CK_P | TP_DSI_CK_P | TP_DSI_CK_P_1 | TP_DSI_CK_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 168 | TP_DSI_D0_N | TP_DSI_D0_N | TP_DSI_D0_N_1 | TP_DSI_D0_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 169 | TP_DSI_D0_P | TP_DSI_D0_P | TP_DSI_D0_P_1 | TP_DSI_D0_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 170 | TP_DSI_D1_N | TP_DSI_D1_N | TP_DSI_D1_N_1 | TP_DSI_D1_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 171 | TP_DSI_D1_P | TP_DSI_D1_P | TP_DSI_D1_P_1 | TP_DSI_D1_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 172 | TP_DSI_D2_N | TP_DSI_D2_N | TP_DSI_D2_N_1 | TP_DSI_D2_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 173 | TP_DSI_D2_P | TP_DSI_D2_P | TP_DSI_D2_P_1 | TP_DSI_D2_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 174 | TP_DSI_D3_N | TP_DSI_D3_N | TP_DSI_D3_N_1 | TP_DSI_D3_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 175 | TP_DSI_D3_P | TP_DSI_D3_P | TP_DSI_D3_P_1 | TP_DSI_D3_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 176 | TP_FSIN | TP_FSIN | TP_FSIN_1 | TP_FSIN_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 177 | TP_I2CA_SCL | TP_I2CA_SCL | TP_I2CA_SCL_1 | TP_I2CA_SCL_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 178 | TP_I2CA_SDA | TP_I2CA_SDA | TP_I2CA_SDA_1 | TP_I2CA_SDA_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 179 | TP_I2CB_SCL | TP_I2CB_SCL | TP_I2CB_SCL_1 | TP_I2CB_SCL_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 180 | TP_I2CB_SDA | TP_I2CB_SDA | TP_I2CB_SDA_1 | TP_I2CB_SDA_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 181 | TP_ID | TP_ID | TP_ID_1 | TP_ID_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 182 | TP_JTAG | TP_JTAG | TP_JTAG_1 | TP_JTAG_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 183 | TP_KEY_PWR | TP_KEY_PWR | TP_KEY_PWR_1 | TP_KEY_PWR_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 184 | TP_KEY_VM | TP_KEY_VM | TP_KEY_VM_1 | TP_KEY_VM_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 185 | TP_KEY_VP | TP_KEY_VP | TP_KEY_VP_1 | TP_KEY_VP_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 186 | TP_LED_B | TP_LED_B | TP_LED_B_1 | TP_LED_B_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 187 | TP_LED_G | TP_LED_G | TP_LED_G_1 | TP_LED_G_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 188 | TP_LED_R | TP_LED_R | TP_LED_R_1 | TP_LED_R_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 189 | TP_LIGHT_3V3 | TP_LIGHT_3V3 | TP_LIGHT_3V3 | TP_LIGHT_3V3 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 190 | TP_MCLK | TP_MCLK | TP_MCLK_1 | TP_MCLK_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 191 | TP_PG | TP_PG | TP_PG_1 | TP_PG_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 192 | TP_PG_VCORE | TP_PG_VCORE | TP_PG_VCORE_1 | TP_PG_VCORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 193 | TP_PG_VIO | TP_PG_VIO | TP_PG_VIO_1 | TP_PG_VIO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 194 | TP_RESET | TP_RESET | TP_RESET_1 | TP_RESET_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 195 | TP_SYS | TP_SYS | TP_SYS_1 | TP_SYS_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 196 | TP_TS | —(不在本板·CHG_BOARD) | TP_TS_1 | TP_TS_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 197 | TP_UART | TP_UART | TP_UART_1 | TP_UART_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 198 | TP_USB_D_N | TP_USB_D_N | TP_USB_D_N_1 | TP_USB_D_N_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 199 | TP_USB_D_P | TP_USB_D_P | TP_USB_D_P_1 | TP_USB_D_P_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 200 | TP_VBUS | —(不在本板·CHG_BOARD) | TP_VBUS_1 | TP_VBUS_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 201 | TP_VCORE | TP_VCORE | TP_VCORE_1 | TP_VCORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 202 | TP_VIO | TP_VIO | TP_VIO_1 | TP_VIO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 203 | U_BATPROT | U_BATPROT | U_BATPROT_1 | U_BATPROT_1 | 四侧产物 + gen_bom.py:307 GAP29; gen_bom.py:100 OPN_FROM_BOARD | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 204 | U_CHG | —(不在本板·CHG_BOARD) | U_CHG_1 | U_CHG_1 | 四侧产物 + ★无额外硬编码★ | 不在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 205 | U_DCDC_VCORE | U_DCDC_VCORE | U_DCDC_VCORE_1 | U_DCDC_VCORE_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 206 | U_DCDC_VIO | U_DCDC_VIO | U_DCDC_VIO_1 | U_DCDC_VIO_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 207 | U_EN_SW | U_EN_SW | U_EN_SW_1 | U_EN_SW_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 208 | U_LDO_IO18 | U_LDO_IO18 | U_LDO_IO18 | U_LDO_IO18 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 209 | U_LDO_IO33 | U_LDO_IO33 | U_LDO_IO33 | U_LDO_IO33 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 210 | U_LDO_L18 | U_LDO_L18 | U_LDO_L18 | U_LDO_L18 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 211 | U_LDO_L33 | U_LDO_L33 | U_LDO_L33 | U_LDO_L33 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 212 | U_LDO_S12 | U_LDO_S12 | U_LDO_S12 | U_LDO_S12 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 213 | U_LDO_S18B | U_LDO_S18B | U_LDO_S18B_1 | U_LDO_S18B_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 214 | U_LDO_S28 | U_LDO_S28 | U_LDO_S28 | U_LDO_S28 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |
| 215 | U_PWR_SW | U_PWR_SW | U_PWR_SW_1 | U_PWR_SW_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 216 | U_SUPV | U_SUPV | U_SUPV_1 | U_SUPV_1 | 四侧产物 + gen_bom.py:307 GAP29 | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 217 | U_TEMP | U_TEMP | U_TEMP_1 | U_TEMP_1 | 四侧产物 + ★无额外硬编码★ | 在 | 改名 | 缺失0/多余2/同号异网3 (不变) | BATCH-1 背靠背 |
| 218 | X1 | X1 | X1 | X1 | ★无需改 (已同口径)★ | 在 | 不动 | 缺失0/多余2/同号异网3 (不变) | — |

### §1-3 · 依赖顺序 (★同批 = 同一个落表单号·背靠背·不许拆成两趟★)

```
BATCH-1 (★必须同批·背靠背·★):
  1) 网表侧 HW/netlist_v1.csv   —— ref 列 + node1/node2 里的器件名 (★先改★)
  2) 脚表侧 HW/netlist_v1_pins.csv —— ref 列
  3) BOM 侧  HW/BOM_v1.csv      —— ★由 state/gen_bom.py 生成 ⇒ 必须与 1/2 同批重跑★
  4) 板侧   HW/PCB/demo_mainboard.kicad_pcb —— ★由 state/gen_pcb_netlist_board.py 生成 ⇒ 同批重出★
  5) 原理图侧 demo_mainboard_p*.kicad_sch —— ★由 state/gen_kicad_sch.py 生成 ⇒
     ★**不改**★: kicad_ref() 对已带 _1 的 ref 是【幂等】的 ⇒ 重跑得同一张图
★中间态禁令: 1) 已落表但板未重出 ⇒ C1 炸成 缺失350/多余352 (★ISS-314 S3 实测★)
BATCH-2 (★判据侧·与 BATCH-1 同批★): state/check_pcb_nets.py 两处硬编码 (★见 §2★)
BATCH-3 (★生成器侧硬编码·与 BATCH-1 同批★):
     state/gen_bom.py:100 OPN_FROM_BOARD (U_BATPROT / Q1)
     state/gen_bom.py:307 GAP29 (29 个 ref 清单)
     state/gen_pcb_netlist_board.py:203 PLACE_OVERRIDE (J_USB_C / R_SER_USB_D_N)
     state/gen_pcb_netlist_board.py:221 CONN_CAM_PIN
BATCH-4 (★SW 侧位号注册表重建次序 · 与 BATCH-1 同批 · ★次序写死·不许自己改顺序★):
     ★**触发条件 = 【位号宇宙改过】(★不是「闸红了就重建」·★need `iss327_decide_registry_rebuild_trigger` 裁决★)★**
       · 位号宇宙没改 ⇒ **不重建** (★重建是一次性动作·不是每次跑闸都要重做★)
       · 位号宇宙改了 ⇒ **要重建** (★老名必须退出「真位号集合」·新名必须进来·否则下一轮改名会被【假 DRIFT】打中★)
     ★**次序写死 (★本单最容易踩的那颗雷·★[实测]·★依据 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` §4-1·★ISS-327 交卷页★)**:
         步1  SW 侧文档同批改名 (★第 7 件·★sw-lead★)         ⇒ **先做**
         步2  按改名后盘面重建冻结注册表 (★第 1 件·★sw-lead★) ⇒ **后做**
       ★**为什么次序不能反**: 重建命令按【当前盘面】分类 ⇒ 文档没同步时重建 ⇒ 收出来的表是错的
         (★[实测]: 文档未同步时重建只收得到 **18 条** · 文档已同步后重建收得到 **78 条**★)
         ⇒ ★**先重建注册表、后同步文档 = 把 58 条【真·改名漂移】洗成 56 条【真隐患】⇒ 一样红且更凶★ ★**
     ★**重建命令 (★只在本单批次内跑·★真件闸脚本一个字节不许改·★输出只到日志★)**:
         python3 SW/tools/check_sw_ref_reachability.py --freeze-registry
     ★**基线硬边界 (★need `iss327_decide_missing_baseline_mechanism` 裁决·★[实测]★)**:
         · `BASELINE_COUNT` **保持 3, 一字不改** (★文档同批改名 ⇒ 基线稳在 3★)
         · 上限 **只许收紧不许放宽**
         · ★**真出第 4 条真隐患时 ⇒ 走「带单号的登记台账」, 不许直接把 3 改成 4** ★
         · ★**重建后 `MISSING` 必须仍然 = 3** (★若变大 ⇒ 说明把「改名漂移」改叫「真隐患」了 ⇒ 停·★走 SOP §5 档②/③★)★
     ★**`DESIGNATOR_DRIFT` 语义 (★need `iss327_decide_drift_class_semantics` 裁决★)**:
         · 该类保留 · 语义写死 = 【文档与盘面不同步告警】
         · ★**处置方向与 `MISSING` 完全相反**: `DRIFT` 大 ⇒ 查【次序 / 同步】; `MISSING` 大 ⇒ 查【真隐患基线】★
     ★**登记义务**: 重建动作挂【落表单号】 (★ISS-312 既有口径★) ⇒ 留证【谁重建 / 何时 / 前后读数 (78 条 · `MISSING`=3)】
```

### §1-4 · 逐条验收命令 (★逐字可粘贴·每一条都能独立判★)

```bash
# ① 改名后 C1 三项 + C2 + C3 + 非法 NC (★主判据★)
bash state/pcbnew_py.sh state/check_pcb_nets.py 2>&1 | grep -E 'C1 |缺失 |C2 |C3 '

# ② 改名后原理图侧是否仍是同一张图 (★幂等性★)
md5sum HW/PCB/demo_mainboard_p*.kicad_sch

# ③ 改名后 BOM 侧证据行有没有消失 (★ISS-314 地雷 2 / 本单 §3★)
grep -c '板文件' HW/BOM_v1.csv

# ④ 改名后四侧位号集合是否同口径
python3 state/check_chain_content_anchor.py

# ⑤ 门禁链
python3 state/merge.py && python3 state/gate_check.py
```

---

## §2 NC 白名单三选项对照 (★C1/C2/C3 全部沙盒实跑·不许推算★)

### §2-1 · 问题陈述 (★ISS-314 §3-5 逐字★)

> ★**「三侧同口径改名」也撞死 `state/check_pcb_nets.py` 的 NC 白名单 (★S4 实测: 非法 NC 3 + C3 红 1★) ⇒ ★**【位号改名】与【受保护判据脚本一个字不许改】这两条 ★不可兼得★★ ⇒ 必须拍一个** ★

### §2-2 · ★**读数基线 (★同一判据脚本 + 原板 + 原网表★)★

```
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
```

★**这 5 条 delta (缺失0 / 多余2 / 同号异网3 / 非法NC0) 是现状固有的** ⇒ ★**改名【不】解掉它们** ★

### §2-3 · 三个选项 × C1/C2/C3 实跑读数 (★逐字搬自沙盒原始输出★)

★**判据脚本**: `logs/iss314/check_pcb_nets_reflookup.py` (★ISS-314 留档副本·只读·拷进沙盒跑★) + 沙盒 harness (★只加 `--pcb=` 与 selftest 落沙盒·判据方向一个字没改★)

| 选项 | 板+网表 | 判据 | C1 缺失 | C1 多余 | C1 同号异网 | ★非法 NC★ | C3 不符 | rc |
|---|---|---|---|---|---|---|---|---|
| ★底座 (全改名·判据不动)★ | 板改名 + 网表改名 | ★不动★ | 0 | 2 | 3 | ★**3**★ | 1 | rc=1 |
| ★**甲** (豁免 `J_USB_C`)★ | 板改名 + 网表改名, 但 `J_USB_C` 保持原名 | ★不动★ | 0 | 2 | 3 | ★**0**★ | 0 | rc=1 |
| ★**乙** (解封两行)★ | 板改名 + 网表改名 | ★解封 2 行★ | 0 | 2 | 3 | ★**0**★ | 0 | rc=1 |
| ★**丙-①** (裸前缀)★ | 板改名 + 网表改名 | ★改判据 (前缀)★ | 0 | 2 | 3 | ★**0**★ | 0 | rc=1 |
| ★**丙-②** (正则锚定)★ | 板改名 + 网表改名 | ★改判据 (正则)★ | 0 | 2 | 3 | ★**0**★ | 0 | rc=1 |

★**C2 一栏**: ★**五场的 C2 全部绿 (无「C2 针号/针数不符」行) ★** ⇒ ★**三选项的分歧【不在 C2】, 全在 C1 的「非法 NC」那一项 + C3★ ★

**★A0 · 底座: 五侧同口径全改名 (板改名 + 网表改名) · 判据一个字节不动** — 场景 `A0_base_5side`

★**这一场复现了 ISS-314 S5 的结论: 「非法 NC 3 + C3 红 1」⇒ 撞死白名单, 铁证★**

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 3
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 pad
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padA8
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padB8
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A1 · 甲方案: 豁免 `J_USB_C` 改名 (板+网表都保持 `J_USB_C`) · 判据不动** — 场景 `A1_jia_exempt`

★**甲方案的代价: C1/C2/C3 全绿, 但「五侧同口径」破了 —— `J_USB_C` 一个位号与其它 185 个口径不同★**

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A2 · 乙方案: 五侧同口径全改名 · 解封判据两行 (`NC_ALLOWED.add` + `--selftest` 目标)** — 场景 `A2_yi_unseal`

★**乙方案的读数: 与甲完全相同 (非法 NC 0 / C3 不符 0) ⇒ 【读数上甲乙等价】, 差别在「谁的口径」★★**

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A3 · 丙方案-① (裸前缀 `startswith("J_USB_C")`): 五侧同口径全改名** — 场景 `A3_bing_prefix`

★**这一场读数也是绿的 —— 但 ★它是不是把真错放过了? 见 §2-4 的 A6 反向用例★**

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A4 · 丙方案-② (正则锚定 `^J_USB_C(_\d+)?$`): 五侧同口径全改名** — 场景 `A4_bing_regex`

★**这一场读数与 A3 相同, 但 §2-4 证明它【没有】放过真错 ⇒ 它才是可用的丙★**

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

### §2-4 · ★**「变松的部分是否仍然会被抓住」—— 逐条证明 (★这是本节最要紧的一段★)**

★**ISS-314 只说「丙 = 改判据思路」, 没说不放宽。但改白名单 = 放宽「非法 NC」判据 ⇒ 必须证明没放宽真错。 本单用两个反向用例做了机器证明。** ★

#### §2-4-1 · 反向用例①: 非白名单器件长出一个 NC 焊盘 (★真错长什么样★)

★**造场**: 给 `C_BULK_SENSOR_CORE` (★**不在**白名单★) 的 pad1 删掉 `(net ...)` 行 ⇒ 它变成 NC 焊盘 ⇒ ★**这就是一个真错** ★

**★A5 · 丙-① (裸前缀) 跑反向用例①** — 场景 `A5_negcase_CBULK`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 481
缺失 0 · 多余 2 · 同号异网 4 · ★NC 焊盘 352 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 1
★NC 焊盘落在不该有 NC 的器件上: C_BULK_SENSOR_CORE_1 pad1
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A5b · 丙-② (正则锚定) 跑反向用例①** — 场景 `A5b_negcase_CBULK_regex`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 481
缺失 0 · 多余 2 · 同号异网 4 · ★NC 焊盘 352 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 1
★NC 焊盘落在不该有 NC 的器件上: C_BULK_SENSOR_CORE_1 pad1
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A5c · 基座 (判据不动) 跑反向用例① · 对照组** — 场景 `A5c_negcase_CBULK_base`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 481
缺失 0 · 多余 2 · 同号异网 4 · ★NC 焊盘 352 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 4
★NC 焊盘落在不该有 NC 的器件上: C_BULK_SENSOR_CORE_1 pad1
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 pad
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padA8
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padB8
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

★**⇒ 反向用例① 结论**: ★**丙-① / 丙-② / 基座 三者都抓住了 `C_BULK_SENSOR_CORE_1` 的非法 NC (非法 NC 各 1 / 1 / 4) ⇒ 三者都没在这一类真错上放宽** ★

#### §2-4-2 · ★反向用例② (★本单新增·专门打「裸前缀」★)**

★**造场**: 把 `C_BULK_SENSOR_CORE` ★**改名成 `J_USB_C_X`** (★仍不是白名单成员·但★**前缀**像★) 并给它造一个 NC 焊盘 ★
★**为什么要造这个**: ★**裸前缀白名单 `startswith("J_USB_C")` 会把 `J_USB_C_X` 也当成白名单成员** ⇒ ★**真错被放过** ★

**★A6 · 丙-① (裸前缀) 跑反向用例② ★★这一场就是陷阱★ ★** — 场景 `A6_prefixtrap_C1`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 481
缺失 0 · 多余 2 · 同号异网 4 · ★NC 焊盘 352 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A6b · 丙-② (正则锚定) 跑反向用例②** — 场景 `A6b_prefixtrap_C2`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 481
缺失 0 · 多余 2 · 同号异网 4 · ★NC 焊盘 352 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 1
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_X pad1
✅ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 0 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

**★A6c · 基座 (判据不动) 跑反向用例② · 对照组** — 场景 `A6c_prefixtrap_base`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 481
缺失 0 · 多余 2 · 同号异网 4 · ★NC 焊盘 352 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 4
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 pad
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padA8
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padB8
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_X pad1
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
### T5-b 映射歧义: 板侧同名封装出现两份 + 网表不改 (原表) ⇒ 期望 ③ 红「口径歧义」
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

★**⇒ 反向用例② 结论 (★机器读数·不是推理★)**:

| 判据 | 非法 NC 读数 | 谁被放过 | 判定 |
|---|---|---|---|
| ★**丙-① 裸前缀** ★ | ★**0** ★ | ★**`J_USB_C_X` 被放过 (基座是 4, 它是 0)★ | ★**❌ 放宽了真错 ⇒ 不可用** ★ |
| ★**丙-② 正则锚定** ★ | ★**1** ★ | 只放过 `J_USB_C_1` (合法), `J_USB_C_X` 仍被抓 | ★**✅ 没放宽** ★ |
| 基座 (判据不动) | ★**4** ★ | 一个都没放过 | ★对照组★ |

★**⇒ 所以: ISS-314 说的「丙 = 白名单按位号形状推导」, ★必须写成【正则锚定 `^J_USB_C(_\d+)?$`】, 写成裸 `startswith` 就会把真错放过 —— 这一点 ISS-314 没测出来, 本单测出来了** ★

### §2-5 · 三个选项的代价对照 (★供 main / 老板拍板·本单不拍★)

| 选项 | 做法 | 谁拍 | 代价 | 风险 | ★**谁放宽了判据**★ |
|---|---|---|---|---|---|
| ★**甲** ★ | `state/check_pcb_nets.py` 一个字节不许改 ⇒ 改名时把 `J_USB_C` 排除在改名之外 (★**只有它 1 个**·不是 5 个★) | main + 老板 (★因为「有的位号改有的不改」会让五侧口径不再统一★) | ★**改名单 ⇒ 清单里标「哪些 ref 豁免」= `J_USB_C` 这 1 个★** | ★**豁免的位号仍然带着问号 ⇒ KiCad BOM 侧问号不会归零 ⇒ 与 ISS-205 的「问号 = 0」判据冲突** ★ | ★**不放宽** ★ (★A1 实测 非法 NC 0 / C3 不符 0★) |
| ★**乙** ★ | 解封 `state/check_pcb_nets.py` 的 `NC_ALLOWED.add("J_USB_C")` + `--selftest` 目标 `CONN_CAM` 两行 ⇒ 白名单跟着改名走 | main (★它是「受保护判据脚本」的守门人★) | ★**动受保护判据 ⇒ 事后必须留证 + selftest 必须重跑全绿** ★ | ★**改白名单 = 放宽「非法 NC」判据 ⇒ 必须证明没放宽真错** ★ | ★**不放宽** ★ (★A2 实测 非法 NC 0 / C3 不符 0★) ★★但★ ★**放宽风险在「这两行本身」** ★: 白名单变成 `J_USB_C_1` ⇒ ★**精确**★ ⇒ 与甲同等严格 |
| ★**丙-① (裸前缀)** ★ | 把 NC 白名单从「硬编 ref 名单」改成「按位号形状推导」= `startswith("J_USB_C")` | main | ★**判据方向变了 ⇒ 必须重跑全部反向用例** ★ | ★**前缀匹配会把 `J_USB_C_X` 这种真错一起放过** ★ | ★**❌ 放宽了真错 (★A6 实测 非法 NC 0 vs 基座 4★) ⇒ 不推荐** ★ |
| ★**丙-② (正则锚定)** ★ | 同上, 但写成 `^J_USB_C(_\d+)?$` (★**精确锚定**★) | main | ★**判据方向变了 ⇒ 必须重跑全部反向用例** ★ | ★**白名单从「1 个硬编 ref」变成「1 条正则」⇒ 以后任何 `J_USB_C*` 改到别的形态都要重核** ★ | ★**不放宽** ★ (★A6b 实测 非法 NC 1, 与基座一致地抓住 `J_USB_C_X`★) |

★**⇒ 给 main 的一句话**: ★**甲/乙/丙-② 三者的 C1/C2/C3 读数完全相同 (非法 NC 0 / C3 不符 0); 真正的差别不在读数, 在【谁来承担口径不统一 / 动受保护判据 / 白名单变成正则】的代价 —— 这条只能老板拍** ★

### §2-6 · ★**`--selftest` 的实测 (★ISS-314 §6-④「假绿风险」的实测证据★)**

★**这一段是本单新发现的一条硬约束: 改名之后, `--selftest` 会【崩】, 不是「变红」—— 崩掉就没有假绿保护了** ★

**★S1 · 改名后的板 + 【未解封的判据】跑 `--selftest`** — 场景 `S1_selftest_base`

★**⇒ 崩溃 (ValueError), 不是判红** ★

```
rc=1
```

**★S2 · 改名后的板 + 【乙方案判据】跑 `--selftest`** — 场景 `S2_selftest_optB`

★**⇒ selftest 正常跑完并抓到了脚位对调 ⇒ 乙方案的两行是【必需的】, 不是可选的** ★

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 5 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
✅ 自检通过 —— 门禁**抓到了**脚位对调 (rc=1) ⇒ 本门禁不是假绿
rc=0
```

★**⇒ 结论**: ★**`state/check_pcb_nets.py` 的 `--selftest` 目标 (`CONN_CAM`) 也必须跟改名同步解封, 否则改名落地后 `--selftest` 直接崩 ⇒ 假绿保护消失 ⇒ 这就是 ISS-314 §6-④ 说的「④ `--selftest` 自己崩 ⇒ 假绿风险回来」的【实测证据】** ★

★**⇒ 落成可执行约束 (★抄进作业包★)**

```
★**判据脚本解封清单 = 两行, 不是一行★** (★BATCH-2·与 BATCH-1 同批★):
  ① state/check_pcb_nets.py  NC_ALLOWED.add("J_USB_C")   ⇒  NC_ALLOWED.add("J_USB_C_1")
  ② state/check_pcb_nets.py  --selftest 目标 "CONN_CAM" ⇒  "CONN_CAM_1"
★漏掉 ② 的后果 (★S1 实测★): --selftest 抛 ValueError 崩掉 ⇒ 假绿保护消失
★改完后必须重跑: bash state/pcbnew_py.sh state/check_pcb_nets.py --selftest   ⇒ 必须 rc=0 且打印「✅ 自检通过」
```

---

## §3 BOM 证据回填兜底: 机器可判的判据写法

### §3-1 · 地雷 (★ISS-314 §2-④ 逐字★)

> ★**`state/gen_bom.py` 用【精确 ref】读板 ⇒ 板侧改名 ⇒ 约 24 个末字符是字母的位号查不到 ⇒ 「封装/型号来源: 板文件 Value 属性」那些证据行会整段消失, opn 可能退回 `待定` / `[0数据]` ⇒ ★**没有任何报警**⇒ BOM 看起来是绿的, 证据已经没了** ★

★**本单用沙盒把「约 24 个」实测成了【精确数字 17 个】** (★§3-3 的 S1 场★) ★

### §3-2 · 三个兜底选项 × 判据写法 (★每一段都是机器可判的·不是散文★)

★**判据的共同骨架 (★三个选项共用★)**:

```
判据位置: state/gen_bom.py 的 main() 里「板文件是权威源」那一段
          (★当前: parse_board_footprints(PCB_FILE) ⇒ board.get(ref) 精确查★)
触发条件: ★board.get(ref) is None★ (★改名前查得到·改名后查不到★)
判定动作: ★**不许静默改写**★ ⇒ 要么【报警】(落红) 要么【明确写「板文件里没有这个位号」】
期望读数: ★改名前 N 行证据行数 == 改名后 N 行证据行数★ (★守恒★)
```

| 选项 | 做法 | ★**机器可判的判据文字 (★能直接变成脚本里的一行★)** ★ | 落红时机 |
|---|---|---|---|
| ★**甲 (落「乙 报警」)** ★ | 只加报警, 不改证据回填逻辑 | ```★若 board.get(ref) is None 且该 ref 在改名清单里 ⇒ print("[ISS-317-J1] 板文件查不到 {ref} ⇒ 板侧/BOM 侧位号不同口径", file=sys.stderr); sys.exit(3)``` ★ | ★**每次生成 BOM 都撞上就退非零** ★ |
| ★**乙 (落「甲 映射 + 乙」)** ★ | 加反查映射 + 加报警 | ```★m = {}★  ★for r in board:★  ★    if kicad_ref(r) in table_refs and r not in table_refs: m[kicad_ref(r)] = r★  ★ref2 = m.get(ref, ref)★  ★bb = board.get(ref2)★  ★if bb is None and ref in table_refs: ⇒ 报警 + 退非零★``` ★ | ★**同上, 但先试映射·映射不中才退★ ★ |
| ★**丙 (别的·本单建议)** ★ | ★**把「证据来源」写成【不依赖 ref 精确匹配】的形式**: ★证据行里同时落【板侧 ref】和【表侧 ref】两个字段★ ⇒ 改名后即使精确查不到, 也能靠板侧 ref 反查回表侧 ref ⇒ 证据不消失 | ```★memo 里写「板文件封装 {板侧ref} = {value}」★  ★同时新增一列 board_ref ★⇒ 判据: ★每条板文件证据行的 board_ref 必须在板文件里查得到★ ★ | ★**每次生成 BOM 都核 board_ref 一致性★ ★ |

★**⇒ 本单的建议 (★不替 main 拍·只给倾向★)**: ★**丙** 最稳 (★它不依赖任何「映射规则」·证据自己带着板侧 ref★), ★**甲** 最省事 (★一行 sys.exit(3)·但只报警不回填★), ★**乙** 最绕 (★要维护一张映射表·映射表本身也是新的真源·会漂★) ★

### §3-3 · ★**「如果只改板侧不改 BOM 侧」这个失败场景, 判据长什么样 (★本单最要紧的一句★)**

★**判据 J1 (★证据覆盖守恒★) —— 机器可判, 一行判红★**:

```
J1: 对 BOM 里每一条「以板文件为证据来源」的行:
    该行所依赖的板文件封装 ref, 必须【在改名后的板文件里查得到】
    ⇒ 查不到 ⇒ 判红
    ⇒ ★读数: 丢 N 个 (★N = 静默消失的证据行数★)★
```

★**这一句之所以是关键**: ★**「BOM 证据静默消失」的本质不是「BOM 变红了」, 而是「BOM 还是绿的但证据没了」⇒ 判据必须直接盯【证据覆盖率】, 而不是盯 BOM 的红绿** ★

★**实测 (★沙盒·`logs/iss317/iss317_sb_bom_silence.py`·只读·不跑 gen_bom.py★)**:

```

── 场景 S0 基线 ──
    板文件封装数            : 186
    BOM「板文件证据」行数   : 23
      BT_432243, CHG_GND_STAR, D_ESD_CAM, D_ESD_DEMO, D_ESD_LIGHT, D_ESD_USB_D, FB_DEMO, J_SOM_P2
      J_SOM_P4, Q1, Q_AND, Q_ENVC, Q_PG, SW_BOOT, SW_KEY_CAM, SW_KEY_PWR
      SW_KEY_VM, SW_KEY_VP, SW_RST, U_BATPROT, U_LDO_S28, U_SUPV, X1
    ★J1 逐条命中 (★ref 在改名后的板里还能查到吗★): 丢 0 个
    ⇒ J1 判定: ✅ 绿

── 场景 S1 只改板侧不改 BOM 侧 ──
    板文件封装数            : 186
    BOM「板文件证据」行数   : 23
      BT_432243, CHG_GND_STAR, D_ESD_CAM, D_ESD_DEMO, D_ESD_LIGHT, D_ESD_USB_D, FB_DEMO, J_SOM_P2
      J_SOM_P4, Q1, Q_AND, Q_ENVC, Q_PG, SW_BOOT, SW_KEY_CAM, SW_KEY_PWR
      SW_KEY_VM, SW_KEY_VP, SW_RST, U_BATPROT, U_LDO_S28, U_SUPV, X1
    ★J1 逐条命中 (★ref 在改名后的板里还能查到吗★): 丢 17 个
    ⇒ J1 判定: ❌ 判红 (★证据静默消失★)

── 场景 S2 对照 ──
    板文件封装数            : 186
    BOM「板文件证据」行数   : 23
      BT_432243, CHG_GND_STAR, D_ESD_CAM, D_ESD_DEMO, D_ESD_LIGHT, D_ESD_USB_D, FB_DEMO, J_SOM_P2
      J_SOM_P4, Q1, Q_AND, Q_ENVC, Q_PG, SW_BOOT, SW_KEY_CAM, SW_KEY_PWR
      SW_KEY_VM, SW_KEY_VP, SW_RST, U_BATPROT, U_LDO_S28, U_SUPV, X1
    ★J1 逐条命中 (★ref 在改名后的板里还能查到吗★): 丢 0 个
    ⇒ J1 判定: ✅ 绿

── 场景 S3 板+BOM 同步改名 ──
    板文件封装数            : 186
    BOM「板文件证据」行数   : 23
      BT_432243, CHG_GND_STAR_1, D_ESD_CAM_1, D_ESD_DEMO_1, D_ESD_LIGHT_1, D_ESD_USB_D_1, FB_DEMO_1, J_SOM_P2
      J_SOM_P4, Q1, Q_AND_1, Q_ENVC_1, Q_PG_1, SW_BOOT_1, SW_KEY_CAM_1, SW_KEY_PWR_1
      SW_KEY_VM_1, SW_KEY_VP_1, SW_RST_1, U_BATPROT_1, U_LDO_S28, U_SUPV_1, X1
    ★J1 逐条命中 (★ref 在改名后的板里还能查到吗★): 丢 0 个
    ⇒ J1 判定: ✅ 绿
```

★**⇒ 反向用例 (★破坏前绿·破坏后红·不是巧合自证★)**:

| 场景 | 板侧 | BOM 侧 | J1 读数 | 期望 | 实测 |
|---|---|---|---|---|---|
| ★**S0 基线** ★ | 原板 | 原 BOM | ★丢 0 个⇒ 绿 ★ | 绿 | ★绿 ✓★ |
| ★**S1 事故场 (★只改板侧★)** ★ | ★改名后的板★ | ★原 BOM★ | ★**丢 17 个 ⇒ 判红** ★ | 判红 | ★**判红 ✓** ★ |
| ★**S2 对照场** ★ | 原板 | 原 BOM | ★丢 0 个⇒ 绿 ★ | 绿 | ★绿 ✓★ |
| ★**S3 五侧同口径场** ★ | 改名后的板 | ★改名后的 BOM★ | ★丢 0 个⇒ 绿 ★ | 绿 | ★绿 ✓★ |

★**⇒ 结论**: ★**J1 能抓住「只改板侧不改 BOM 侧」, 且「五侧同口径」时不会误报 (S3 绿)** ★

★**★ 一句「不许这样写」 (★ISS-314 §2-④ 要的那句★)**:

```
★**不许**写成: 「BOM 生成成功 ⇒ 绿」★
★**不许**写成: 「BOM 里 [0数据] 的行数 == 0 ⇒ 绿」★
★**不许**写成: 「板文件 md5 没变 ⇒ 绿」★  (★改名落地后板 md5 必然变★)
★**必须**写成: 「★每一条板文件证据行都能在板文件里查到它引用的那个封装 ref★ ⇒ 才叫绿」
```

### §3-4 · ★**ISS-314 U-6 的边界 (★本单不越界★)**

★**ISS-314 U-6 已经把选型问题交给 main (「BOM 生成器要不要在改名后变红」是放行口径) ⇒ 本单只交「如果选了会变红, 判据该怎么写」, 不交「该不该变红」** ★

★**⇒ 交 main 的一句话**: ★**本单只证明「J1 这条判据能抓住静默消失且不误报」; 「BOM 生成器该不该在改名后变红」是放行口径, 留给 main 拍 (need `s1_ref_rename_caliber_20261118`)** ★

---

## §4 ISS-314 五条未验的补齐结果

| # | 未验项 | ★**补齐结果** ★ | 证据等级 |
|---|---|---|---|
| ★**U-1** ★ | 反向用例 T5 (映射歧义) / T6 (板侧 ref 改成表侧没有的名字) 的实际读数 | ★**已补齐 · 沙盒实跑** ★ (★见下 §4-1★) | ★**[实测]** ★ |
| ★**U-2** ★ | DMP3098L 官方引脚序 (1=G / 2=S / 3=D) 的官方出处 | ★**已补齐 · Diodes 官方手册 DS31447 Rev.8** ★ (★见下 §4-2★) | ★**[官网]** ★ |
| ★**U-3** ★ | ESD「必须紧贴连接器」的官方出处 | ★**已补齐 · TI 官方手册 §7.4.1 + Pin Functions 脚注 (2)** ★ (★见下 §4-3★) | ★**[官网]** ★ |
| ★**U-4** ★ | 「S1 的问号行数 = 0」今天的现值 | ★**已补齐 · 实跑 = 问号 0 行 / 总 219 行** ★ (★见下 §4-4★) | ★**[实测]** ★ |
| ★**U-5** ★ | 选①之后落表那一批的具体排期 | ★**已补齐 · 只给批次顺序与前置, 不替老板拍日期** ★ (★见下 §4-5★) | ★**[0数据]** (★日期★) |

### §4-1 · U-1 · T5 / T6 实跑 (★ISS-314 只出了设计·没跑★)

★**判据脚本**: `logs/iss314/check_pcb_nets_reflookup.py` (★只读·拷进沙盒跑★) ★

**★T5-b · 映射歧义: 板侧同名封装出现两份 + 网表不改 (原表)** — 场景 `T5b_ambig`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 1 · 多余 3 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
ℹ️ ★口径: 反查层命中 155 个板上位号 (板侧 X_1 ⇒ 表侧 X) ⇒ 【板侧位号与网表 ref 不同名】这件事【仍然成立】★
❌ ★口径歧义: 1 个板上位号反查后指向同一表侧 ref ⇒ 判红★
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
### T6-a 板侧 ref ⇒ <原名>_2 (表侧从来没有的名字) ⇒ 期望 ③ 红「口径未同步」
rc=1
```

★**⇒ T5 结论**: ★**③ 红, 文案「★口径歧义: 1 个板上位号反查后指向同一表侧 ref ⇒ 判红★」** ★
★**⇒ 达到了 ISS-314 设计的预期 (③ 红 + 文案「口径歧义」/「单射校验失败」)** ★

**★T6-a · 板侧 ref ⇒ `<原名>_2` (表侧从来没有的名字)** — 场景 `T6a_x2`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 3
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 pad
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padA8
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padB8
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
### T6-b 板侧 ref ⇒ <原名>_Z_1 (反查不命中) ⇒ 期望 ③ 红「口径未同步」
rc=1
```

**★T6-b · 板侧 ref ⇒ `<原名>_Z_1` (反查不命中)** — 场景 `T6b_xz1`

```
❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482
缺失 0 · 多余 2 · 同号异网 3 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 3
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 pad
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padA8
★NC 焊盘落在不该有 NC 的器件上: J_USB_C_1 padB8
❌ C3 每个器件焊盘数 == 网表推出的脚数 — 器件 185 个 · 不符 1 个
❌ ★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★
rc=1
```

★**⇒ T6 结论**: ★**③ 红, 文案「★口径未同步: 1 个板上位号在网表里找不到 (且反查不命中) ⇒ 它们是【真·多余器件】, 判红★」** ★
★**⇒ 达到了 ISS-314 设计的预期 (③ 红 + 文案「口径未同步」)** ★

★**⇒ U-1 判定: ★**ISS-314 的 T5/T6 从 [推算] 升成 [实测]** ★

### §4-2 · U-2 · DMP3098L 官方引脚序 (★自己上网查·零外发★)

| 项 | 内容 |
|---|---|
| ★**官方出处** ★ | ★**https://www.diodes.com/datasheet/download/DMP3098L.pdf** ★ |
| ★**厂商 / 文档号** ★ | ★**Diodes Incorporated · Document number: DS31447 Rev. 8 - 2** ★ |
| ★**原文摘录** ★ | ★**SOT-23 Top View · Pin Configuration 图: `D`(Drain) / `G`(Gate) / `S`(Source) ⇒ pin 1 = G, pin 2 = S, pin 3 = D** ★ |
| ★**快照** ★ | `tmp/iss317_tmp/web/DMP3098L_diodes_official.pdf` (★272,336 B·PDF v1.4★) |
| ★**抓取方式** ★ | ★**`curl -sL --max-time 60` (只读下载·未发任何邮件/询价/问询)★ ★ |
| ★**判定** ★ | ★**引脚序 1=G / 2=S / 3=D 有厂商官方手册背书 ⇒ ISS-314 / ISS-283 引用的这条 [官网] 级成立** ★ |
| ★**边界** ★ | ★**只证明引脚序, 不证明板上 land 的网络分配正确** ★ (★那 3 根线仍须按 ISS-283 §③-2 在板那一趟重画★) |

★**完整留档**: `logs/iss317/05_dmp3098l_official.txt` (★含逐字摘录 + 官方规格 + 快照 md5★) ★

### §4-3 · U-3 · ESD「必须紧贴连接器」的官方出处 (★自己上网查·零外发★)

★**本项目实际用的 ESD 器件**: `D_ESD_USB_D` = **TPD1E05U06DPYR** (TI · X1SON-2) · `D_ESD_DEMO` = PESD5V0S1BA (Nexperia) · `D_ESD_CAM` = TPD1E05U06DPYR ★

| 项 | 内容 |
|---|---|
| ★**官方出处** ★ | ★**https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf** ★ |
| ★**文档号** ★ | ★**SLVSBO7O – DECEMBER 2012 – REVISED AUGUST 2024** ★ |
| ★**原文摘录 ① (§7.4.1 Layout Guidelines·逐字★)** ★ | ★**「The optimum placement is as close to the connector as possible.」** ★ |
| ★**原文摘录 ② (Pin Functions 脚注 (2)·逐字★)** ★ | ★**「Place as close to the connector as possible.」** ★ |
| ★**快照** ★ | `tmp/iss317_tmp/web/TPD1E05U06_ti_official.pdf` (★2,801,483 B·PDF 10 页★) |
| ★**抓取方式** ★ | ★**`curl -sL --max-time 60` (只读下载·未发任何邮件/询价/问询)★ ★ |
| ★**判定** ★ | ★**「ESD 必须紧贴连接器」有厂商官方出处 ⇒ ISS-314 的 U-3 从 [推算] 升成 [官网]** ★ |
| ★**边界** ★ | ★**官方只说「as close as possible」, 没给数字 ⇒ 「多近才算够」★**没有官方数值**★ ⇒ ★**本单不编数字** ★ |

★**⇒ 落成可执行约束 (★抄进作业包·替代 note 自由文本★)**:

```
★**ESD 紧贴连接器** ⇒ 写成几何约束, 不写 note:
  ① ESD 器件的封装原点与它所保护的连接器封装原点之间的直线距离 (★或 ESD 到连接器『入口焊盘』的距离★)
     ≤ ★**D**★ mm   (★D 由结构域给·本单不替结构拍★)
  ② 该几何量由 ★state/ 下的一个只读脚本量出来★ ⇒ 输出一个数 ⇒ 判据直接比这个数
  ③ ★**本单给不出 D 的数值** ⇒ ★标 [0数据] + 降级方案★: ★先按「同页 + 同板 + ESD 的保护网是连接器相邻脚」这一可机判的弱判据兜住★
     (★已实测: D_ESD_USB_D 的保护网 = NET_USB_D_P_TYPEC, 正是 J_USB_C 的 A6/B6 脚 ⇒ 同网即相邻★)
```

★**完整留档**: `logs/iss317/06_esd_official.txt` ★

### §4-4 · U-4 · 「S1 的问号行数 = 0」今天的现值 (★实跑·ISS-314 没跑那条命令★)

★**命令 (★输出写项目内 `tmp/`, 不写 `/tmp` —— 本机 `/tmp` 带 usrquota 且配额已满 ⇒ 假红★)**:

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss317_tmp
mkdir -p "$TMPDIR"
bash state/kicad.sh sch export bom -o "$TMPDIR/bom_check.csv" --fields Reference,Value HW/PCB/demo_mainboard.kicad_sch
echo "问号行数 = $(grep -c '?' "$TMPDIR/bom_check.csv") / 总行数 = $(wc -l < "$TMPDIR/bom_check.csv")"
```

★**实测读数**:

```
Wrote bill of materials to '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss317_tmp/bom_check.csv'.
rc=0
```

★**判定**: ★**问号行数 = 0 / 总行数 = 219** ★
★**⇒ U-4 从 [未验] 升成 [实测]** ★
★**⇒ 与 ISS-314 的口径一致 (它也是 0 / 219) ⇒ 两边对得上** ★

★**★ 但这一条对 ISS-317 有一个★直接后果 ★**:

★**甲方案 (豁免 `J_USB_C`) 会让问号【不再为 0】** —— 因为 `J_USB_C` 是末字符是字母的位号, 原理图侧叫 `J_USB_C_1`, 而甲方案让它在表侧/板侧保持 `J_USB_C` ⇒ ★**KiCad 导出 BOM 时这一行的 Reference 查不到 Value ⇒ 问号 +1** ★
★**⇒ 这就是 ISS-314 给甲方案写的风险「豁免的位号仍然带着问号 ⇒ KiCad BOM 侧问号不会归零 ⇒ 与 ISS-205 的「问号 = 0」判据冲突」—— 本单把它【从 [推算] 升成 [推算·有机制依据]】: ★上面的现值 0 是【现状·没改名】时的值; 甲方案落地后这一条会破★ ★

### §4-5 · U-5 · 落表排期口径 (★不替老板拍日期★)

★**本单只给「批次顺序 + 前置 + 谁批」, 不给日期** (★日期是老板的★) ★

| 批次 | 内容 | 前置 (★必须先满足★) | 谁批 |
|---|---|---|---|
| ★**BATCH-1** ★ | 网表 + 脚表 + BOM + 板 + 原理图 ★**五侧同批** ★ | ★① NC 白名单方案 (甲/乙/丙-②) 已拍 ★② 落表表单号已开 ★③ §1 的 218 行清单逐行核对完 | ★main + 老板 ★ |
| ★**BATCH-2** ★ | `state/check_pcb_nets.py` 两行解封 (★与 BATCH-1 同批★) | ★★与 BATCH-1 同批背靠背★ ★(★漏一行 ⇒ `--selftest` 崩, 漏另一行 ⇒ C1 非法 NC 3★) | ★main (★受保护判据守门人★) ★ |
| ★**BATCH-3** ★ | 生成器侧硬编码 (`gen_bom.py` / `gen_pcb_netlist_board.py`) | ★与 BATCH-1 同批★ | ★main ★ |
| ★**BATCH-4** ★ | 板重出后的门禁链 + BOM 证据 J1 复核 | ★BATCH-1/2/3 全落 | ★main ★ |

★**★ 一句可抄的排期口径 (★给老板/排产用★)**:

```
★**BATCH-1/2/3 必须同批背靠背走完, 中间不得隔夜★**
★**理由 (★实测·不是经验值★)**: ★① 只落表不重出板 ⇒ C1 炸成 缺失350/多余352 (ISS-314 S3 实测)★
                              ★② 只改一侧 ⇒ C1 缺失0/多余2/同号异网3 不变, 但 --selftest 崩 (S1 实测) ⇒ 假绿保护消失★
                              ★③ 板 md5 第二次变 = 2-4 周 + ¥4-8K★
★**排期由老板定; 本单不填日期★
```

---

## §5 证据分级

| 证据 | 等级 | 来源 |
|---|---|---|
| 四侧/五侧现值盘点 (218 / 291 / 216 / 186) | ★**[实测]** ★ | 脚本自算, 非手抄 (`logs/iss317/iss317_gen_rename_list.py`) |
| 改名口径单源一致性 | ★**[实测]** ★ | ★与 `state/gen_kicad_sch.py::kicad_ref()` 源码逐字比对, 不一致即 abort ★ |
| 分组计数 (要改 186 / 不动 32 · 板侧 156/30) | ★**[实测]** ★ | 同上 |
| 单射校验 (改名后无碰撞) | ★**[实测]** ★ | 同上 |
| C1 现状基线 (缺失0/多余2/同号异网3/非法NC0) | ★**[实测]** ★ | `logs/iss317/01_c1_baseline_full.txt` |
| ★**A0~A6 / T5 / T6 / S1 / S2 全部读数** ★ | ★**[实测]** ★ | ★**沙盒实跑** ★ `logs/iss317/04b_sb_run_v2_raw.txt` (★含 v1 三个缺陷的修复说明★) |
| ★**丙-① 裸前缀会放过真错 (非法 NC 0 vs 基座 4)** ★ | ★**[实测]** ★ | ★**A6 反向用例② 实跑** ★ |
| ★**改名后 `--selftest` 崩 (ValueError)** ★ | ★**[实测]** ★ | ★**S1 实跑 + CTL1/CTL2 对照** ★ |
| ★**BOM 证据静默消失 (丢 17 个)** ★ | ★**[实测]** ★ | ★**§3 J1 判据沙盒实跑** ★ (`logs/iss317/12_bom_silence_judge_raw.txt`) |
| DMP3098L 引脚序 1=G/2=S/3=D | ★**[官网]** ★ | ★**Diodes DS31447 Rev.8** ★ (URL + 逐字摘录 + 快照 md5) |
| ESD「as close to the connector as possible」 | ★**[官网]** ★ | ★**TI SLVSBO7O §7.4.1 + Pin Functions 脚注 (2)** ★ |
| BOM 问号行数 = 0 / 总 219 | ★**[实测]** ★ | `bash state/kicad.sh sch export bom` (★输出落项目内 `tmp/`★) |
| 「甲方案会让问号不再为 0」 | ★**[推算]** ★ | ★机制依据: `J_USB_C` 是末字符是字母的位号, 原理图侧叫 `J_USB_C_1` ⇒ 甲方案下表侧/板侧仍叫 `J_USB_C` ⇒ 导出时查不到 Value ★★未实跑 (★本单不跑改名后的 KiCad 导出·零重生成★)★ ★ |
| 「改名只改 ref 名不改 (ref,pad)→net 映射 ⇒ 现状 5 条 delta 不变」 | ★**[推算]** ★ | ★**但 A0/A1 实测证实了它** (★缺失0/多余2/同号异网3 与基线逐字相同★) ⇒ 实际已升级为 [实测] ★ |
| 落表排期日期 | ★**[0数据]** ★ | ★不替老板拍 ⇒ 只给批次顺序与前置 ★ |
| 「ESD 距连接器多少 mm 才算够」 | ★**[0数据]** ★ | ★官方只说「as close as possible」·无数值 ⇒ ★**不编数字** ★ ⇒ 降级方案见 §4-3 ★ |

---

## §6 文件清单

### §6-1 · 零写板 / 零落表双证

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb
```

★**期望值**: 板 md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` ★

### §6-2 · 本单产出的文件

| # | 文件 | 内容 |
|---|---|---|
| 1 | ★**`HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md`** ★ | ★**本文件 (交付物 ①)** ★ |
| 2 | ★**`HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md`** ★ | ★**交卷页 (交付物 ②)· B0~B6 齐全** ★ |
| 3 | ★**`logs/iss317/`** ★ | ★**原始输出留档 (交付物 ③)· 见 §6-4** ★ |
| 4 | ★**`state/fragments/hw.yaml`** ★ | ★**分片 (交付物 ④)· 经 `state/frag_write.py --agent hw-lead` 原子写** ★ |

### §6-3 · 复现命令 (★逐字可粘贴★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 逐条改名清单 (★机器生成·非手抄★ · v2 = 列宽不截断 + TSV 输出★)
python3 logs/iss317/iss317_gen_rename_list_v2.py | tee logs/iss317/rename_list_raw_v2.txt

# ② 沙盒造场 v2 (★v1 的三个缺陷已修★·只写 tmp/iss317_sandbox/★)
python3 logs/iss317/iss317_sb_make_v2.py | tee logs/iss317/04a_sb_make_v2_raw.txt

# ③ 场景矩阵实跑 (★A0~A6 / T5 / T6 / S1 / S2★)
bash logs/iss317/iss317_sb_run_v2.sh | tee logs/iss317/04b_sb_run_v2_raw.txt

# ④ §3 BOM 证据静默消失判据 (★只读·不跑 gen_bom.py★)
python3 logs/iss317/iss317_sb_bom_silence.py | tee logs/iss317/12_bom_silence_run_raw.txt

# ⑤ 交付物装配 (★自带行数校验·不符即 abort★)
python3 logs/iss317/iss317_write_deliverable.py

# ⑥ 门禁链 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/merge.py && python3 state/gate_check.py

# ⑦ 占位符扫描 (★必须 0★)
#    ★命令逐字见 logs/iss317/10_placeholder_scan.txt (★本单交卷前跑的扫描留档★)
#    ★本文件正文【不含任何占位标记】⇒ 该扫描的期望读数 = 0★
```

### §6-4 · `logs/iss317/` 原始输出清单

| 文件 | 内容 |
|---|---|
| `rename_list_raw_v2.txt` | ★**218 行逐条改名对照表 (机器生成·★TSV 行是 §1 的源★)** ★ |
| `iss317_gen_rename_list_v2.py` | ★**清单生成器 v2 (★自带口径单源逐字比对·不一致即 abort★ + TSV 输出★)** ★ |
| `iss317_gen_rename_list.py` | ★**清单生成器 v1 (★★列宽 22 的截断缺陷·保留作对照·别拿它交卷★)** ★ |
| `rename_list_raw.txt` | ★**v1 的清单 (★「同步清单」列被截断·★作对照用★)** ★ |
| `iss317_sb_make_v2.py` / `iss317_sb_run_v2.sh` | ★**沙盒造场 v2 + 驱动 v2 (★v1 三个缺陷的修复版★)** ★ |
| `04a_sb_make_v2_raw.txt` | 沙盒造场 v2 原始输出 (★含每处定点替换的前后对照★) |
| `04b_sb_run_v2_raw.txt` | ★**★场景矩阵 A0~A6 / T5 / T6 / S1 / S2 实跑读数 (★§2 的源★)** ★ |
| `01_c1_baseline_full.txt` | C1 现状基线 (★§2-2 的源★) |
| `02_bom_export_raw.txt` / `07_bom_qmark_raw.txt` | BOM 导出原始输出 + 问号行数现值 |
| `05_dmp3098l_official.txt` | ★**U-2 官网留档 (URL + 逐字摘录 + 快照 md5)** ★ |
| `06_esd_official.txt` | ★**U-3 官网留档 (URL + 逐字摘录 + 快照 md5)** ★ |
| `12_bom_silence_judge_raw.txt` / `12_bom_silence_run_raw.txt` | ★**§3 J1 判据的 S0/S1/S2/S3 实跑读数** ★ |
| `iss317_sb_bom_silence.py` | §3 判据证明器 |
| `iss317_build_deliverable.py` / `iss317_write_deliverable.py` | 装配器 (★自带校验·不符即 abort★) |
| `08_zero_write_proof.txt` | ★**零写板 / 零落表 双证 (md5 + mtime 前后对照)** ★ |
| `09_merge_gate_output.txt` | ★**门禁链输出 (merge + gate_check)** ★ |
| `10_placeholder_scan.txt` | ★**占位符扫描结果** ★ |
| `11_frag_write_output.txt` | ★**分片写入输出 (state/frag_write.py)** ★ |
| `raw/` (19 个文件) | ★**v2 每一场的原始输出 (★A0~A6 / T5 / T6 / S1 / S2 / CTL0~CTL2★) ★** |
| `03b_sb_run_raw.txt` | ★**上一趟 v1 的场景矩阵 (★保留作对照: 里面 A2/A3/A4 是崩的★)** ★ |

---

★**交卷页**: `HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md` ★
