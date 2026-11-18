# ONETRIP_REISSUE_MANIFEST · 「板只改一次」那一趟的【重出清单】 (ISS-311 · hw-lead · 2026-11-18)

> ★**派活**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-311
> ★**性质**: ★**内部活 · 纯分析 / 作业包类** ★ ⇒ ★**本单只交清单, 不执行任何重出** ★
> ★**本文件不是** `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的替代品 —— ★**那一份是【改板怎么做】, 本份是【做完之后哪些产物必须一起重出 + 一件不许漏】** ★

---

## ★0 · 一句话结论 + 边界自证 ★

### ★0-1 · 一句话结论 ★

★★**板只改一次那一趟, 要一起重出的产物共 20 类 / 投产包 74 件; 今天这两条红 (③ PCB + ⑤ 投产包) 不是一个病, 是三个病叠在一起** ★★:

| # | 病 | 证据 | 那一趟要做的动作 |
|---|---|---|---|
| ★**1** ★ | ★**板侧多了一个旧件** (`C_VBUS_GND` 2 个焊盘) ⇒ 环③「多余 2」 ★ | §1-2 | ★**重跑板生成器即自动消失** (★网表 L10/L12 的 board 列已是 `CHG_BOARD`★) ⇒ ★**改板: 是** ★ |
| ★**2** ★ | ★**板侧 3 处挂错网** (`Q_PG` pad1/pad3 对调 + `D_ESD_USB_D` pad1 挂 SoM 侧网) ★ | §1-4 | ★**改板: 是** (★重画 3 根线 + 挪 ESD 器件★) ⇒ ★**这是电气缺陷, 不是排版洁癖** ★ |
| ★**3** ★ | ★**投产包里的原理图是 11-17 12:30 的旧件** (★11 个不一致里 2 个是真旧, 9 个只是 uuid 抖动★) ★ | §2 | ★**重出投产包: 是** (★`gen_production_pack.sh` 自带 `cp -p` 归档 sch_src★) ⇒ ★**改板: 否** ★ |

★★**⇒ 板只改一次那一趟的产物面 = 板 (1 次 md5 变) + 原理图源文件同步 + Gerber/钻孔/坐标/装配/3D/doc 全套 + BOM + 投产包清单** ★★

### ★0-2 · ★★本单边界自证 (逐条) ★★

| # | 纪律 | 自证 |
|---|---|---|
| 1 | ★**零写板** ★ | ★**零写板** ★ · 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` · ★**交卷前后逐字节相同** (★B2-2 双证★) ★ |
| 2 | ★**零落表 / 零改网表真源** ★ | ★**零落表** ★ · `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` **md5 与 mtime 全未变** ★ |
| 3 | ★**零重生成** ★ | ★**零重生成** ★ · **没有跑过** `gen_netlist.py` / `gen_kicad_sch.py` / `gen_bom.py` / `gen_pcb_netlist_board.py` / `gen_production_pack.sh` · ★**`HW/PCB/production/` 下 74 个文件一个字节没动** ★ |
| 4 | ★**零改闸** ★ | ★**零改闸** ★ · `state/chain_gate.py` / `state/gate_check.py` / `state/merge.py` / `state/check_pcb_nets.py` / `state/check_chain_content_anchor.py` **md5 全未变** ★ |
| 5 | ★**零改既有文档正文** ★ | ★**零改** ★ · `BOARD_ONEPASS_WORKPACKET.md` / `BOARD_ONEPASS_PREFLIGHT.md` / `BOARD_ONEPASS_COMMIT_ORDER.md` / `BOARD_ONEPASS_MD5_LEDGER.md` / `BOARD_ONEPASS_S10_MANIFEST_SPEC.md` **只读不写** ★ · ★**本单交的是【另一份清单】, 不是【改好的那两个文件】** ★ |
| 6 | ★**零外发** ★ | ★**零外发** ★ · 没发邮件 / 没询价 / 没问询 / 没采购 · ★**本单全部结论只来自本机实跑 + 项目内文件, 连 web 搜索都没做** ★ |
| 7 | ★**不替老板拍板 · 不自签 issue_log** ★ | ★**没拍** ★ · 遇到 2 处需要拍板的 (★§4-5 地雷 1 的两个选项 / 地雷 2 的两个选项★) ★**只列选项与代价, 不选** ★ · ★**没签** ★ · `state/issue_log.yaml` 一个字节没动 ★ |
| 8 | ★**只写 4 个允许的落点** ★ | ★`HW/PCB/ONETRIP_REISSUE_MANIFEST.md` (★本文件·新建★) · `HANDOFF/2026-11-18_hw-lead_ISS311_板那一趟重出清单.md` (★新建★) · `logs/iss311/` (★新建★) · `state/fragments/hw.yaml` (★**经 `state/frag_write.py --agent hw-lead` 原子写**★) ★ ⇒ ★**`HW/PCB/production/` 一个字节没动** ★ |

---

## ★1 · 【C1 焊盘差异定位】逐条证据 ★

> ★**取数口径**: ★**直接 `import state/check_pcb_nets.py` 的 `netlist_pads()` / `board_pads()` / `compare()`** ★ ⇒ ★**与门禁同口径, 零漂移** ★
> ★**板侧行号 / 坐标**: ★**从 `.kicad_pcb` 原文逐行扫出** (★括号配平定位 `(property "Reference" …)` ⇒ 记 ref, 块内 `(pad "N" …` ⇒ 记行号★) ★
> ★**网表行号**: ★**从 `HW/netlist_v1.csv` 原文行号 (含表头 ⇒ 数据第 1 行 = L2)★ ★

### ★1-1 · 判定摘要 (★一句话★)

★★**板表推出的 (ref,焊盘号)→网络 = 480 条 · 板上带网络的 = 482 条 ⇒ 板比网表【多 2 个带网焊盘】; 这 2 个是【板侧多出来的旧件】, 不是【网表新加的脚】** ★★

★**同时必须知道: C1 的红不止这 2 条 —— 还有 3 条【同号异网】(★脚位对调 / 网名改过没同步★), 而 C1 判据是【缺失 / 多余 / 同号异网 三者任一 ⇒ 红】** ★
⇒ ★**⇒ 那一趟做完, C1 必须同时满足【缺失 0 · 多余 0 · 同号异网 0】, 只解决那 2 个不够** ★

| C1 三项 | 现状 (★2026-11-18 06:2x 实测★) | 那一趟做完后的验收值 |
|---|---|---|
| 缺失 (网表有 / 板没有) | ★**0** ★ | ★**0** ★ |
| 多余 (板有 / 网表没有) | ★**2** ★ | ★**0** ★ |
| 同号异网 (同一焊盘号挂不同网) | ★**3** ★ | ★**0** ★ |
| ★NC 焊盘 (无网, 允许) ★ | ★**351** ★ (★SOM 四组 100 脚座未用脚 + USB-C shield/A8/B8★) | ★**351** ★ |
| ★非法 NC (落在不该有 NC 的器件上) ★ | ★**0** ★ | ★**0** ★ |

★**自证**: `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ ★**rc=1** ★ · 原始输出 `logs/iss311/01_check_pcb_nets_raw.txt` ★

### ★1-2 · 【A】★板上有、网表里没有★ —— ★**2 条 (★= 任务书说的「差 2 个」★)** ★

| # | (ref, pad) | 板上网络名 | ★**板文件行号 + 坐标** ★ | 网表侧 | ★**判定** ★ |
|---|---|---|---|---|---|
| ★**A-1** ★ | `C_VBUS_GND` **pad1** | `GND` | ★**`.kicad_pcb` L8259** ★ (★`(pad "1" smd rect` 起始行★) · 封装原点 ★**(107.7, 42.5)** ★ · pad1 相对偏移 (0, 0.1) ⇒ 绝对 (107.7, 42.6) · ★**封装块起于 L8170, Reference 属性在 L8174** ★ | ★**网表里【没有】这个位号** ★ (★见 A-3★) | ★**板侧多出来的旧件** ★ |
| ★**A-2** ★ | `C_VBUS_GND` **pad2** | `VBUS_5V_CHG` | ★**`.kicad_pcb` L8267** ★ · 封装原点 (107.7, 42.5) · pad2 相对偏移 (1.6, 0.1) ⇒ 绝对 (109.3, 42.6) | ★**网表里【没有】这个位号** ★ | ★**板侧多出来的旧件** ★ |

★**板面原文 (★`HW/PCB/demo_mainboard.kicad_pcb` L8259-8275★)**:
```
(pad "1" smd rect
    (at 0 0.1) (size 0.6 0.9) (layers "F.Cu" "F.Mask" "F.Paste")
    (net "GND") ...)
(pad "2" smd rect
    (at 1.6 0.1) (size 0.6 0.9) (layers "F.Cu" "F.Mask" "F.Paste")
    (net "VBUS_5V_CHG") ...)
```

### ★1-3 · 【A】的根因: ★**网表里这个位号被划到了另一块板** ★

★**网表侧原文 (`HW/netlist_v1.csv` 表头 = `page,net,node1,node2,ref,value,type,dnp,evidence,tbd,note,conn_id,board,footprint,opn`)**:

| 网表行 | ref | net | node1 | node2 | dnp | ★**board 列** ★ |
|---|---|---|---|---|---|---|
| ★**L10** ★ | `C_VBUS_GND` | `GND` | `C_VBUS_GND` | `C_VBUS_GND` | `DNP` | ★**`CHG_BOARD`** ★ |
| ★**L12** ★ | `C_VBUS_GND` | `VBUS_5V_CHG` | `C_VBUS_GND` | `C_VBUS_GND` | `DNP` | ★**`CHG_BOARD`** ★ |

★**脚表侧同源 (`HW/netlist_v1_pins.csv` L148-149)**: `C_VBUS_GND.1` / `C_VBUS_GND.2` · board 列同 = `CHG_BOARD` ★

★★**⇒ 判定**: ★**`C_VBUS_GND` 现在是【充电板 (CHG_BOARD) 的 DNP 件】, 不在 demo 主 PCB (MAIN_PCB) 上** ★
★★**⇒ 它在板上 = 板是【这次落表之前】生成的旧货** ★
★★**⇒ 这一条【不需要手改板, 不需要改网表】⇒ 重跑板生成器时按 board 列过滤即自动消失** ★
★★**⇒ 但它【必须在那同一趟里消失】⇒ 因为它一消失, 板上封装数 186 → 185, 板 md5 就变了 ⇒ Gerber/投产包必须同趟重出** ★★

★**顺带记一条**: ★**网表里同前缀的 `C_VBUS_DEMO` (L424/L425) 是 MAIN_PCB 的另一颗件 (RAIL_DEMO_5V + GND) —— 它跟 `C_VBUS_GND` 【不是同一个东西】, 别在改板时把两者混为一谈** ★

### ★1-4 · 【B】★网表有、板上没有★ —— ★**0 条** ★

★**实测: 缺失 = 0** ⇒ ★**网表这一侧没有【新加的脚】** ⇒ ★**⇒ 差 2 的性质是【单边的】: 只有板侧多, 网表侧没多** ★

★**⇒ 结论落在【改板】一侧, 不落在【改网表】一侧** ★

### ★1-5 · 【C】★同号异网★ —— ★**3 条 (★C1 同样红, 但不在「差 2」里★)** ★

| # | (ref, pad) | ★**网表要求 (★网络名 + 网表行号★)** ★ | ★**板上实际 (★网络名 + 板行号 + 坐标★)** ★ | ★**性质** ★ |
|---|---|---|---|---|
| ★**C-1** ★ | `Q_PG` **pad1** | ★**`PWR_GOOD`** ★ · 网表 ★**L59** ★ (`node1=Q_PG` / `node2=J_CHG pin6`) | ★**`PWR_ON`** ★ · 板 ★**L2068** ★ · 封装原点 ★**(84.8, 29.5)** ★ | ★**脚位对调 (与 C-2 是同一处)** ★ |
| ★**C-2** ★ | `Q_PG` **pad3** | ★**`PWR_ON`** ★ · 网表 ★**L61** ★ (`node1=Q_PG` / `node2=U_PWR_SW pin2`) | ★**`PWR_GOOD`** ★ · 板 ★**L2084** ★ | ★**脚位对调 (与 C-1 是同一处)** ★ |
| ★**C-3** ★ | `D_ESD_USB_D` **pad1** | ★**`NET_USB_D_P_TYPEC`** ★ · 网表 ★**L417** ★ (`node1=D_ESD_USB_D` / `node2=NET_USB_D_P_TYPEC`) | ★**`USB_D_P_SRC`** ★ · 板 ★**L13012** ★ · 封装原点 ★**(94.95, 21.8)** ★ | ★**网名改过没同步 (★不是脚位问题★)** ★ |

#### ★1-5-1 · C-1/C-2 (`Q_PG` pad1/pad3 对调) —— ★**开机路径级电气缺陷** ★

★**网表侧现行写法 (★写法A★)**: pad1 = `PWR_GOOD` (G) · pad2 = `BAT_SW` (S) · pad3 = `PWR_ON` (D)
★**板上仍是旧写法B**: pad1 = `PWR_ON` (S) · pad2 = `BAT_SW` (D) · pad3 = `PWR_GOOD` (G)
★**⇒ 板上 pad1/pad3 的【网络】对调 ⇒ DMP3098L 的 1=G / 2=S / 3=D 引脚序下, 栅源之间接错 ⇒ 那 3 根线必须重画** ★
★**对应既有作业包条目**: `B11_Q_PG_LAND` (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S0 的 S6 行 + §3-S6★) · 追加行 `ISS-283 §③-2` ★

#### ★1-5-2 · C-3 (`D_ESD_USB_D` pad1 挂在 SoM 侧网) —— ★**ESD 器件挂到了 22Ω 串阻的【错误一侧】** ★

★**网表侧的网是拆开的**: `USB_D_P_SRC` (★SoM 侧·串阻前★, 网表 L291) · `NET_USB_D_P_TYPEC` (★Type-C 侧·串阻后★, 网表 L354/L417/L431)
★**串阻 `R_SER_USB_D_P` 本身**: ★**板 L5786 pad1 = `USB_D_P_SRC` · L5794 pad2 = `NET_USB_D_P_TYPEC`** ★ ⇒ ★**串阻位置是对的** ★
★**⇒ 但 ESD 的 I/O 脚 (`D_ESD_USB_D` pad1) 挂在 `USB_D_P_SRC` = 【串阻的 SoM 侧】⇒ ESD 保护不到 Type-C 出口那一段 ⇒ 与网表 note「紧贴 `J_USB_C`, 跨 D+ 与地」的要求相反** ★
★**⇒ 这一条不是排版问题, 是【ESD 保护位置错】⇒ 那一趟必须改** ★
★**对应既有作业包条目**: `B32_V2_NET_RENAME` (★ISS-283 §③-1·追加行★) · 同批还有 `B07_ESD_USB_D_3PIN` / `B08_ESD_USB_D_NEAR` / `B09_ESD_USB_D_MINUS` (★B-3 换 3 脚封装 + B-4 挪到 `J_USB_C` ≤ 3.0 mm + B-5 D− 侧也补 ESD★) ★
★**★三条必须同趟**: ★**换封装 ⇒ 挪位置 ⇒ 布线重跑 ⇒ 是一个原子操作 (★作业包 §3-S4「为什么必须同趟」★)** ★

### ★1-6 · ★★判定 ⇒ 板那一趟要做的具体动作 (★不许只交差集★) ★★

| # | 差 | ★**动作 (★谁做·落在哪★)** ★ | ★**改板? 改网表?** ★ | 验收判据 (★能跑的那条命令★) |
|---|---|---|---|---|
| ★**1** ★ | 多余 2 (`C_VBUS_GND`) | ★**重跑 `bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py`** ★ (★生成器按 `board` 列过滤, ★**不许手改板★**) | ★**只改板** ★ · ★**网表不动** ★ | ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ C1「多余」= **0** ★ |
| ★**2** ★ | 同号异网 3 (`Q_PG` ×2 + `D_ESD_USB_D` ×1) | ★**板那一趟同趟改** (★`Q_PG` 重画 3 根线 / `D_ESD_USB_D` 换 3 脚封装 + 挪位 + 重挂网★) | ★**只改板** ★ · ★**网表不动 (★网表已是现行写法A / 现行网名★)** ★ | ★同上 ⇒ C1「同号异网」= **0** ★ |
| ★**3** ★ | 缺失 0 | ★**无动作** ★ | — | ★C1「缺失」= **0** ★ |

★★**⇒ 一句话给老板**: ★**这 2 个差是【板侧多出来的旧件】, 全部落在【改板】一侧; 网表这一侧【一个字都不用改】(★网表已经是对的, 是板没跟上★) ⇒ 「板只改一次」那一趟的板侧动作 = ★**去掉 `C_VBUS_GND` + 重画 `Q_PG` 三根线 + ESD 三件 (换脚数/挪位/重挂网)**★** ★★

### ★1-7 · 自证命令 + 原始输出 (★★不许抄 chain_gate 的结论★★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss311_tmp        # ★本项目惯例: TMPDIR 指项目内, 别用 /tmp★

# ① 门禁原始输出 (★C1 那一段★)
bash state/pcbnew_py.sh state/check_pcb_nets.py            # ⇒ rc=1
# ★原始输出: logs/iss311/01_check_pcb_nets_raw.txt ★

# ② 本单的逐条探针 (★自己跑, 不抄①的结论★)
bash state/pcbnew_py.sh logs/iss311/probe_c1_diff.py        # ⇒ rc=0
# ★原始输出: logs/iss311/02_probe_c1_diff_raw.txt ★
```

★**探针脚本 `logs/iss311/probe_c1_diff.py` 的口径**: ★**`import state/check_pcb_nets.py` 的 `netlist_pads()` / `board_pads()` / `compare()`** ★ ⇒ ★**网表→焊盘推导逻辑不重写第二遍** ★ (★与生成器同源但与门禁同源 ⇒ 零漂移★) ★ · ★**板侧行号/坐标 = `.kicad_pcb` 原文逐行扫出** ★ · ★**网表行号 = CSV 原文行号** ★

---

## ★2 · 【原理图源文件 11 个不一致】逐条表 ★

> ★**取数口径**: ★**直接 `import state/check_chain_content_anchor.py::normalize_sch_text()`** ★ (★ISS-256 的归一化口径: 去 uuid / 去时间戳 / 去 generator·rev·date 串★) ⇒ ★**与 chain_gate ② 原理图准入那一栏完全同口径** ★

### ★2-1 · ★★关键一问的答案 (★两个数★) ★★

| 问 | ★**数** ★ | 是哪些 |
|---|---|---|
| ★**投产包里的原理图比 `HW/PCB/` 旧 (★⇒ 投板时用投产包 = 用旧原理图★)** ★ | ★**2 个** ★ | ★**`demo_mainboard_p1.kicad_sch` · `demo_mainboard_p10.kicad_sch`** ★ |
| ★**只是 uuid 抖动 (★⇒ 不是真缺件·不必重出★)** ★ | ★**9 个** ★ | ★**`demo_mainboard.kicad_sch` (根页) + `demo_mainboard_p2..p9.kicad_sch` (8 个)** ★ |

★★**⇒ 11 个不一致 = 2 个真旧 + 9 个 uuid 抖动 + 0 个缺页 + 0 个改名** ★★
★★**⇒ 但【11 个 md5 不一致】这件事本身仍然让 chain_gate ⑤ 必红** ⇒ ★**要绿, 11 个都得同步 (★不是只同步那 2 个★)** ★★
★★**⇒ 而同步的正确做法不是手 `cp`, 是 `bash state/gen_production_pack.sh` —— 它自带 `cp -p` 归档 `doc/sch_src/` (★`state/gen_production_pack.sh` 的「原理图源文件归档」块★)** ★★

★**★补一句 (★chain_gate ⑤ 那行「投产包比 原理图 旧」是怎么来的★)**: ★**`chain_gate.py` 判 stale 用的是 `mt(gerbers/demo_mainboard-F_Cu.gtl)` vs `mt(原理图)` (★11-17 21:59 vs 11-18 00:21★) ⇒ 投产包的 Gerber 比原理图旧 ⇒ 「投板用的是旧板的 Gerber」那句成立 —— ★**但真因是板本身旧 (11-06)⇒ 那一趟必须重出板 + 全套 Gerber** ★**

### ★2-2 · ★逐文件表 (★11 个一个不少★) ★

★**列**: ★**文件名 · 差异类型 · 差异证据 (md5 + 归一化指纹 + 差异行数) · 修法** ★

| # | ★**文件名** ★ | ★**差异类型** ★ | ★**源 md5** ★ (`HW/PCB/`) | ★**包 md5** ★ (`production/doc/sch_src/`) | ★**归一化指纹 (源)** ★ | ★**归一化指纹 (包)** ★ | ★**原文差异行** ★ | ★**归一化差异行** ★ | ★**修法** ★ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `demo_mainboard.kicad_sch` (★根页★) | ★**uuid 抖动** ★ | `e433793b…` | `ec4e3860…` | `680479d474…` | `680479d474…` ★**同** ★ | 65 | ★**0** ★ | ★**判据无关** (★归一化后一致★) ⇒ 只需同趟同步 md5 |
| 2 | ★**`demo_mainboard_p1.kicad_sch`** ★ | ★**内容旧** ★ | `c3feaf0d…` | `555732b8…` | `f88ea23a9a…` | `2838dd8ca8…` ★**不同** ★ | 2493 | ★**14** ★ | ★**重生成 (★同趟投产包重出时自动带★)** ★ |
| 3 | ★**`demo_mainboard_p10.kicad_sch`** ★ | ★**内容旧** ★ | `4ef53b33…` | `884bc508…` | `fe2332549a…` | `557…` ★**不同** ★ | 557 | ★**28** ★ | ★**重生成 (★同趟投产包重出时自动带★)** ★ |
| 4 | `demo_mainboard_p2.kicad_sch` | ★**uuid 抖动** ★ | `35ce505e…` | `75d94997…` | `b14387fe1d…` | `b14387fe1d…` ★**同** ★ | 283 | ★**0** ★ | ★**判据无关** ★ |
| 5 | `demo_mainboard_p3.kicad_sch` | ★**uuid 抖动** ★ | `2eb9b5f2…` | `50728649…` | `f9b403b2f6…` | `f9b403b2f6…` ★**同** ★ | 171 | ★**0** ★ | ★**判据无关** ★ |
| 6 | `demo_mainboard_p4.kicad_sch` | ★**uuid 抖动** ★ | `d811f683…` | `25559e31…` | `b2e4b11189…` | `b2e4b11189…` ★**同** ★ | 491 | ★**0** ★ | ★**判据无关** ★ |
| 7 | `demo_mainboard_p5.kicad_sch` | ★**uuid 抖动** ★ | `8486d28d…` | `4e4288d4…` | `ed52058d68…` | `ed52058d68…` ★**同** ★ | 517 | ★**0** ★ | ★**判据无关** ★ |
| 8 | `demo_mainboard_p6.kicad_sch` | ★**uuid 抖动** ★ | `dc34199f…` | `aa0544ac…` | `b231889ffb…` | `b231889ffb…` ★**同** ★ | 172 | ★**0** ★ | ★**判据无关** ★ |
| 9 | `demo_mainboard_p7.kicad_sch` | ★**uuid 抖动** ★ | `5938e052…` | `e386f534…` | `855a1fbfe5…` | `855a1fbfe5…` ★**同** ★ | 1525 | ★**0** ★ | ★**判据无关** ★ |
| 10 | `demo_mainboard_p8.kicad_sch` | ★**uuid 抖动** ★ | `09448515…` | `76fdec1d…` | `7aa3cd0dde…` | `7aa3cd0dde…` ★**同** ★ | 833 | ★**0** ★ | ★**判据无关** ★ |
| 11 | `demo_mainboard_p9.kicad_sch` | ★**uuid 抖动** ★ | `68fff37f…` | `d8d32f2e…` | `d4e94889fa…` | `d4e94889fa…` ★**同** ★ | 27 | ★**0** ★ | ★**判据无关** ★ |
| ★**附** ★ | `demo_mainboard.kicad_pro` | ★**无差异** ★ | `3e504d2b…` | `3e504d2b…` ★**同** ★ | `08bdbed809…` | `08bdbed809…` ★**同** ★ | 0 | ★**0** ★ | ★**无 (★它本来就是 11 个之外的第 12 件, md5 一致★)** ★ |

★★**⇒ 11 个不一致 (★chain_gate ⑤ 报的那 11 个★) = 上表 1~11 行; `.kicad_pro` 不在其中 (★md5 一致★) ★★

### ★2-3 · ★★方向判定: ★哪一份是新的? (★不许只说「不一致」★) ★★

★★**源 (`HW/PCB/`, 11-18 00:21:18) 是【新的】; 包 (`production/doc/sch_src/`, 11-17 12:30:22) 是【旧的】** ★★

★**判定锚点 = 网表真源 (★不看 mtime, 看内容与真源对不对得上★)**:

| 判据点 | ★**源 `HW/PCB/`** ★ | ★**包 `doc/sch_src/`** ★ | ★**网表/脚表真源** ★ | ★**谁对** ★ |
|---|---|---|---|---|
| ★`C_SYS` 的 `(dnp …)` (★p10 L613★) ★ | ★**`(dnp no)`** ★ | ★**`(dnp yes)`** ★ | ★`HW/netlist_v1_pins.csv` L142-143 = ★**`必装`** ★ (★ISS-302 已落表★) | ★**源** ★ |
| ★`C_SYS` 的 `Value` (★p10 L616/L619★) ★ | ★**`20µF X7R 6.3V`** ★ | ★**`20µF 6.3V`** ★ | ★脚表 L142-143 = ★**`20µF X7R 6.3V`** ★ | ★**源** ★ |
| ★`C_SYS` 符号的 pin1 名 (★p10 L194-198★) ★ | ★**`(name "" …)`** ★ (★非 DNP 不标名★) | ★**`(name "DNP" …)`** ★ | ★非 DNP ⇒ 不该标 DNP ★ | ★**源** ★ |
| ★`SYS_CHG` / `PGND` 标签颜色 (★p1 L1617/L1619, p10 L629/L631★) ★ | ★**无 `(color …)`** ★ | ★**`(color 255 0 0 1)`** ★ | ★`state/gen_kicad_sch.py` L101 `DNP_COLOR` + L321 = ★**只有 DNP 脚才染红并标名** ★ ⇒ ★**必装件不该红** ★ | ★**源** ★ |

★★**⇒ 生产者侧证据 (★把生成器逻辑读出来, 不是猜★)**: ★**`state/gen_kicad_sch.py` L101 `DNP_COLOR = "255 0 0 1"` + L321 `(name "DNP" if p["dnp"] else "")` + L381 (染红只给 DNP 脚标签)** ★
★★**⇒ 投产包里 `C_SYS` 是 DNP 版 (★红 + 标名 DNP★), 源里是必装版 ⇒ 投产包 = ISS-302 落表【之前】的原理图** ★★
★★**⇒ 这就是「投产包里的原理图比 `HW/PCB/` 旧」的实锤** ★★

★**★顺带一条实测**: ★**`HW/netlist_v1.csv` md5 = `6aee500e…`, 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` L1466 登记的就是它 (★ISS-302 · 2026-11-18 00:3x★) ⇒ 网表侧已是最新** ★

### ★2-4 · 修法 (★逐条·★不许只写「重生成」★) ★

| 差异类型 | 件数 | ★**修法** ★ | ★**由谁/哪个命令做** ★ |
|---|---|---|---|
| ★**内容旧** ★ | ★**2** ★ (p1 / p10) | ★**重生成** ★ ⇒ ★**源侧已对, 不需要再生成原理图; 要做的是【把新源同步进投产包】** ★ ⇒ ★**同趟 `bash state/gen_production_pack.sh` 时自动 `cp -p` 归档 (★脚本自带, 不许手 `cp`★)** ★ | ★**hw (板那一趟)** ★ · `state/gen_production_pack.sh` ★ |
| ★**uuid 抖动** ★ | ★**9** ★ | ★**判据无关** ★ (★归一化后一致 ⇒ ★**不是真缺件, 不必单独重出原理图**★) ⇒ ★**但 md5 闸照样红 ⇒ 仍需同趟同步** ★ | ★**同上** ★ |
| ★**缺页** ★ | ★**0** ★ | — | — |
| ★**改名** ★ | ★**0** ★ | — | — |

★★**★注意一个容易搞错的点★**: ★**chain_gate ⑤ 判的是 md5 一致 (★`check_sch_src_pack()` 里 `_md5(src) != _md5(dst)`★), 不是归一化一致** ⇒ ★**⇒ 那 9 个 uuid 抖动的件【也必须被同步】, 否则 ⑤ 照样红** ★★
★★**★但归一化口径告诉我们: 那 9 个不是【原理图内容旧】, 只是【每次生成重铸 uuid】⇒ ⇒ 【不必单独重出原理图, 只需让投产包跟上一次生成】★★ ★★

### ★2-5 · 自证命令 + 原始输出 ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss311_tmp
python3 logs/iss311/probe_sch_src_diff.py        # ⇒ rc=0
# ★原始输出: logs/iss311/03_probe_sch_src_diff_raw.txt ★
```

★**探针口径**: ★**`import state/check_chain_content_anchor.py::normalize_sch_text()`** ★ ⇒ 与 chain_gate ② 原理图准入那一栏逐字同口径 ★ · 差异行数用 `difflib` 算 (★原文一遍 + 归一化一遍★) ★

---

## ★3 · 【「板那一趟」重出清单】★**主表** ★

> ★**列**: ★**产物名 · 生成器入口命令 (★逐字可跑★) · 上游依赖 · 现值 (md5 + 时间戳) · 板那一趟做完后的验收判据 (★能跑的那条命令 + 期望值★) · 顺序位 · 归属人** ★
> ★**★所有命令都已在本机实测存在 (★`test -e` 逐条跑过★) ⇒ 没有「缺, 需新建」的条目** ★

### ★3-0 · 顺序位编号约定 ★

| 顺序位 | 含义 |
|---|---|
| ★**①** ★ | ★**条件步** (★只有当 §4-5 地雷被拍成「要落表」时才跑★) ★ |
| ★**②** ★ | 网表侧 (★真源★) |
| ★**③** ★ | 原理图侧 |
| ★**④** ★ | ★**板 (★唯一会改 md5 的件·★全表只有它★)** ★ |
| ★**⑤** ★ | BOM (★★必须在板之后★ ★) |
| ★**⑥** ★ | 投产包 (★Gerber / 钻孔 / 坐标 / 贴片 / 装配 / 3D / doc / sch_src / 清单★) ★ |
| ★**⑦** ★ | 收尾 (★闸 / 留证 / 台账 / 分片★) ★ |

### ★3-1 · 主表 (★每一件产物一行★) ★

| # | ★**产物名** ★ | ★**生成器入口命令 (★逐字可跑★)** ★ | ★**上游依赖** ★ | ★**现值 (md5 / 时间戳)** ★ | ★**做完后的验收判据 (命令 + 期望值)** ★ | ★**顺序位** ★ | ★**归属** ★ |
|---|---|---|---|---|---|---|---|
| ★**1** ★ | ★**网表 `HW/netlist_v1.csv`** ★ | ★`python3 state/gen_netlist.py` ★ | ★`HW/SCHEMATIC_V1_SPEC.json` + 落表台账 ★ | `6aee500e60ba0732f83a9cf557ba90ab` / 2026-11-18 00:21:08 ★**✅ 已绿** ★ | ★`python3 state/chain_gate.py` ⇒ ① 准入「网表 md5 == 台账最新登记」★ | ★**① (条件)** ★ | ★**hw** ★ |
| ★**2** ★ | ★**脚级真值表 `HW/netlist_v1_pins.csv`** ★ | ★`python3 state/gen_netlist_pins.py` ★ (★上游: `python3 state/gen_kicad_net.py` ⇒ `HW/netlist_v1.net`★) | ★网表 + `.net` ★ | `9174309df1ec9411ac8e8d9e80ee386a` / 2026-11-18 00:21:08 ★**✅ 已绿** ★ | ★`python3 state/chain_gate.py` ⇒ ② 原理图准入「位号 218 == 脚表 218 · 标签 584 == 脚 584」★ | ★**① (条件)** ★ | ★**hw** ★ |
| ★**3** ★ | ★**原理图 11 页 + `.kicad_pro`** ★ (★`demo_mainboard.kicad_sch` + `demo_mainboard_p1..p10.kicad_sch` + `demo_mainboard.kicad_pro`★) | ★`python3 state/gen_kicad_sch.py` ★ | ★脚表 (★`netlist_v1_pins.csv`★) ★ | 11 页全 = `e433793b…`(根) / `c3feaf0d…`(p1) / `4ef53b33…`(p10) … · `.kicad_pro` = `3e504d2b…` / 全 11 页 2026-11-18 00:21:18 ★**✅ 已绿** ★ | ★`python3 state/chain_gate.py` ⇒ ② 准入 ✅ · ★`python3 state/check_sch_loadable.py` ⇒ rc=0 ★ · ★`python3 state/check_sch_pinfull.py` ⇒ K=0 ★ | ★**③** ★ | ★**hw** ★ |
| ★**4** ★ | ★**★板 `HW/PCB/demo_mainboard.kicad_pcb` (★全表唯一会改 md5 的件★)** ★ | ★`bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py` ★ | ★网表 (★`HW/netlist_v1.csv`★) + 生成器改动 (★S7 DNP 标记 / S3 Value 取值 / S4 ESD 3 脚封装 + 钉位★) ★ | ★**`611b869e13518c3c023fb178f91a0075` / 2026-11-06 07:07:17** ★ | ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ ★**rc=0 · C1 缺失 0 / 多余 0 / 同号异网 0** ★ · ★`python3 state/check_pcb_drc.py` ⇒ ★**unc=0 · DRC=0** ★ | ★**④** ★ | ★**hw** ★ |
| ★**5** ★ | ★**BOM `HW/BOM_v1.csv`** ★ | ★`python3 state/gen_bom.py` ★ | ★脚表 + ★**板文件 (★`gen_bom.py` 读板封装的 Value/焊盘数回填 opn/封装/证据★ ⇒ ★必须在板之后★)** ★ | `5b9993992405904a60ac96a020b375d8` / 2026-11-18 00:21:08 ★**✅ 现在绿, 但板一改就会红** ★ | ★`python3 state/chain_gate.py` ⇒ ④ 准入「逐行一致: 218 行 (位号,value,dnp) == 脚表聚合」★ · ★准出「位号 218 个全对 · DNP 42 个一致 · 伪器件 0 个」★ | ★**⑤ (★板之后★)** ★ | ★**hw** ★ |
| ★**6** ★ | ★**Gerber (canonical `HW/PCB/gerbers/` 32 件)** ★ | ★`bash state/kicad.sh pcb export gerbers -o HW/PCB/gerbers/ HW/PCB/demo_mainboard.kicad_pcb` ★ (★`gen_production_pack.sh` 内也跑一遍再复制★) | ★**板** ★ | 32 件, mtime 2026-11-17 21:59:43 ★**★由旧板 611b869e 出的★** ★ | ★`ls HW/PCB/gerbers \| wc -l` ⇒ ★**32** ★ · ★每件 md5 必须 ≠ 旧值 (★板变了 Gerber 必变★) ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**7** ★ | ★**投产包 Gerber `production/gerbers/` (★32 件 + `job.gbrjob` 在内★)** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 32 件 / 2026-11-17 21:59:43 ★ | ★`ls HW/PCB/production/gerbers \| wc -l` ⇒ ★**32** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**8** ★ | ★**钻孔 `production/drill/` (★4 件: PTH.drl / NPTH.drl / PTH 钻孔图 PDF / NPTH 钻孔图 PDF★)** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 4 件 / 2026-11-17 21:59:44 | ★`ls HW/PCB/production/drill \| wc -l` ⇒ ★**4** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**9** ★ | ★**坐标 / 贴片 CPL `production/pos/demo_mainboard-pos.csv`** ★ | ★`bash state/gen_production_pack.sh` ★ (★`kicad.sh pcb export pos --side both --format csv --units mm`★) | ★板 ★ | 12,659 B / 2026-11-17 21:59:45 | ★`ls HW/PCB/production/pos \| wc -l` ⇒ ★**1** ★ · ★**位号个数必须与板上的贴片件一致 (★板改了封装数 ⇒ CPL 必改★)** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**10** ★ | ★**装配 `production/assembly/` (★3 件: `ipc2581.xml` + `assembly-top.pdf` + `assembly-bottom.pdf`★)** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 3 件 / 2026-11-17 21:59:47-49 | ★`ls HW/PCB/production/assembly \| wc -l` ⇒ ★**3** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**11** ★ | ★**3D 模型 `production/3d/demo_mainboard.step`** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 11,962 B / 2026-11-17 21:59:52 | ★`test -s HW/PCB/production/3d/demo_mainboard.step` ⇒ rc=0 ★ · ★**必须与新板同版 (★step 里不含板 md5 ⇒ 靠 MANIFEST 连带证明★)** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**12** ★ | ★**PCB 图 PDF `production/doc/demo_mainboard-pcb-{all,top,bottom}.pdf`** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 3 件 / 2026-11-17 21:59:50-51 | ★`ls HW/PCB/production/doc/demo_mainboard-pcb-*.pdf \| wc -l` ⇒ ★**3** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**13** ★ | ★**外形 DXF `production/doc/demo_mainboard-Edge_Cuts.dxf`** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 6,801 B / 2026-11-17 21:59:53 | ★`test -s …Edge_Cuts.dxf` ⇒ rc=0 ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**14** ★ | ★**裸板测试网表 D356 `production/doc/demo_mainboard.d356`** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 104,976 B / 2026-11-17 21:59:54 | ★`test -s …d356` ⇒ rc=0 ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**15** ★ | ★**板统计 `production/doc/board-stats.txt`** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 ★ | 1,435 B / 2026-11-17 22:00:07 | ★`test -s …board-stats.txt` ⇒ rc=0 ★ · ★**★注意: 这个文件里【没有 md5 字段】(★实测 `grep -ci md5` = 0★) ⇒ 它的判据不是「板 md5」★** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**16** ★ | ★**原理图 PDF `production/doc/demo_mainboard-sch.pdf`** ★ | ★`bash state/gen_production_pack.sh` ★ (★`kicad.sh sch export pdf`★) | ★**原理图 (③)** ★ | 690,248 B / 2026-11-17 22:00:09 | ★`test -s …sch.pdf` ⇒ rc=0 ★ · ★**必须比原理图新 (★chain_gate ⑤ stale 判据就查这个★)** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**17** ★ | ★**原理图 SVG `production/doc/sch_svg/` (★11 件: 根页 + P1..P10★)** ★ | ★`bash state/gen_production_pack.sh` ★ (★`kicad.sh sch export svg`★) | ★原理图 (③) ★ | 11 件 / 2026-11-17 22:00:09 | ★`ls HW/PCB/production/doc/sch_svg \| wc -l` ⇒ ★**11** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**18** ★ | ★**KiCad 原理图网表 `production/doc/demo_mainboard-kicad.net`** ★ | ★`bash state/gen_production_pack.sh` ★ (★`kicad.sh sch export netlist`★) | ★原理图 (③) ★ | 380,430 B / 2026-11-17 22:00:10 | ★`test -s …kicad.net` ⇒ rc=0 ★ · ★**必须与网表逐脚零差异 (★parity 判据★)** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**19** ★ | ★**KiCad BOM `production/doc/demo_mainboard-kicad-bom.xml`** ★ | ★`bash state/gen_production_pack.sh` ★ (★`kicad.sh sch export bom`★) | ★原理图 (③) ★ | 11,476 B / 2026-11-17 22:00:10 | ★`test -s …kicad-bom.xml` ⇒ rc=0 ★ · ★**问号行数 = 0 (★S1 改名的机器判据★)** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**20** ★ | ★**原理图源文件归档 `production/doc/sch_src/` (★12 件 = 11 个 `.kicad_sch` + 1 个 `.kicad_pro`★)** ★ | ★`bash state/gen_production_pack.sh` ★ (★脚本自带 `cp -p` 归档块★) · ★**备选 (★chain_gate 自己给的那条·但只手同步 12 件·不重出其余 62 件★)**: ★`cp -p HW/PCB/demo_mainboard*.kicad_sch HW/PCB/demo_mainboard.kicad_pro HW/PCB/production/doc/sch_src/` ★ | ★原理图 (③) ★ | 12 件 · 11 个 `.kicad_sch` 全部 mtime 2026-11-17 12:30:22 (★★比源旧★★) · `.kicad_pro` 2026-11-04 23:47:30 ★ | ★`python3 state/chain_gate.py` ⇒ ⑤ 准入「原理图源文件: 12 个源文件齐全 · 与 `HW/PCB/` 一一对应 · 内容 md5 全一致」★ | ★**⑥** ★ | ★**hw** ★ |
| ★**21** ★ | ★**投产包清单 `HW/PCB/production/MANIFEST.md5`** ★ | ★`bash state/gen_production_pack.sh` ★ (★脚本末段调 `bash state/gen_production_manifest.sh "$OUT" "$PCB"`★) | ★板 (★清单里的 `BOARD_MD5` 行 = 盘上板 md5★) + 投产包全部文件 ★ | `b78b9648b3001bc7c5b43a866064c94c` / 2026-11-17 22:00:11 · ★**数据行 73 行 + 清单自身 = 74 件** ★ | ★`python3 HW/check_onepass_s10_manifest.py` ⇒ ★**rc=0 · M1~M4 全绿** ★ ⇒ ★**M2: 清单 `BOARD_MD5` == 盘上板 md5** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**22** ★ | ★**★投产包全量 (★74 件 = 上表 6~21 全部 + 目录骨架★)** ★ | ★`bash state/gen_production_pack.sh` ★ | ★板 + 原理图 ★ | ★**74 件 (★现状 rc: `HW/check_onepass_s10_manifest.py` rc=0·M1~M4 全绿★)** ★ | ★`find HW/PCB/production -type f \| wc -l` ⇒ ★**74** ★ · ★`python3 state/chain_gate.py` ⇒ ★**⑤ 准入 ✅ + 准出 ✅** ★ · ★**rc=0** ★ | ★**⑥** ★ | ★**hw** ★ |
| ★**23** ★ | ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md`** ★ | ★**人工追加 (★main 落★)** ★ | ★网表/脚表/BOM 的新 md5 ★ | ★**台账 L1466 已登记网表 `6aee500e…` (★ISS-302·11-18 00:3x★)** ★ | ★`python3 state/chain_gate.py` ⇒ ① 准入「网表 md5 == 落表台账最新登记」★ | ★**⑦** ★ | ★**main** ★ |
| ★**24** ★ | ★**分片 `state/fragments/hw.yaml`** ★ | ★`python3 state/frag_write.py --agent hw-lead --add-artifact path=… summary=…` ★ | ★本单/那一趟的结论 ★ | ★**收工时重写 (★走原子写★)** ★ | ★`python3 state/merge.py` ⇒ ★**rc=0** ★ · ★`python3 state/gate_check.py` ⇒ ★**Q1 18/18** ★ | ★**⑦** ★ | ★**hw** ★ |
| ★**25** ★ | ★**旧 md5 引用点 (★`611b869e…` 全仓★)** ★ | ★`grep -rn "611b869e13518c3c023fb178f91a0075" . --include=*.py --include=*.sh --include=*.md --include=*.json` ★ | ★新板 md5 ★ | ★**现状: 多处引用 (★作业包 §5 / 各闸的保护基线 / 留证链★)** ★ | ★**上条命令命中数 = 0** ★ (★作业包 §3-S9★) ★ | ★**⑦** ★ | ★**hw + main** ★ |

### ★3-2 · ★投产包子目录逐件清单 (★74 件一件不漏★) ★

| 子目录 | 件数 | 内容 | 现状 mtime | 那一趟 |
|---|---|---|---|---|
| `production/gerbers/` | ★**32** ★ | F/B 铜 + 6 内层 + 阻焊/丝印/粘贴/外形/Adhesive/Courtyard/Margin/User×N + `job.gbrjob` | 2026-11-17 21:59:43 | ★**全量重出** ★ |
| `production/drill/` | ★**4** ★ | PTH.drl / NPTH.drl / PTH 钻孔图 PDF / NPTH 钻孔图 PDF | 2026-11-17 21:59:44 | ★**全量重出** ★ |
| `production/pos/` | ★**1** ★ | `demo_mainboard-pos.csv` (CPL, 双面, mm) | 2026-11-17 21:59:45 | ★**重出** ★ |
| `production/assembly/` | ★**3** ★ | `ipc2581.xml` / `assembly-top.pdf` / `assembly-bottom.pdf` | 2026-11-17 21:59:47-49 | ★**重出** ★ |
| `production/3d/` | ★**1** ★ | `demo_mainboard.step` | 2026-11-17 21:59:52 | ★**重出** ★ |
| `production/doc/` | ★**9** ★ | `demo_mainboard-pcb-{all,top,bottom}.pdf` (3) + `Edge_Cuts.dxf` + `demo_mainboard.d356` + `board-stats.txt` + `demo_mainboard-sch.pdf` + `demo_mainboard-kicad.net` + `demo_mainboard-kicad-bom.xml` | 2026-11-17 21:59:50–22:00:10 | ★**全量重出** ★ |
| `production/doc/sch_src/` | ★**12** ★ | 11 个 `.kicad_sch` + `demo_mainboard.kicad_pro` | ★**11 个 = 2026-11-17 12:30:22 (★旧★)** ★ + `.kicad_pro` 11-04 23:47:30 | ★**全量重出 (★脚本自带 cp -p★)** ★ |
| `production/doc/sch_svg/` | ★**11** ★ | 根页 SVG + P1..P10 SVG | 2026-11-17 22:00:09 | ★**全量重出** ★ |
| `production/MANIFEST.md5` | ★**1** ★ | 73 数据行 + 3 头字段 (★`BOARD_MD5` / `GENERATED_AT` / `FILE_COUNT`★) | 2026-11-17 22:00:11 | ★**重出 (★随包一起★)** ★ |
| ★**合计** ★ | ★**74** ★ | — | — | ★**一件不许留旧** ★ |

---

## ★4 · 顺序 + 依赖图 + 同趟出清单 + 归属 ★

### ★4-1 · 依赖图 (★谁是谁的上游★) ★

```
                        ┌─────────────────────────────────────────────┐
                        │ HW/SCHEMATIC_V1_SPEC.json + 落表台账        │
                        │ (HW/SCHEMATIC_LANDING_V1_LANDED.md)         │
                        └──────────────────┬──────────────────────────┘
                                           │  (① 条件步: 要落表才跑)
                                           ▼
   ①  python3 state/gen_netlist.py  ──▶  HW/netlist_v1.csv
                                           │  python3 state/gen_kicad_net.py
                                           ▼
                              HW/netlist_v1.net
                                           │  python3 state/gen_netlist_pins.py
                                           ▼
   ②  python3 state/gen_netlist_pins.py ──▶ HW/netlist_v1_pins.csv
                                           │                    │
                    ┌──────────────────────┘                    │
                    ▼                                           │
   ③  python3 state/gen_kicad_sch.py ──▶ 11 个 .kicad_sch        │
                    │                        + .kicad_pro        │
                    │                                           │
                    │                                           │
                    │         ★★ S1 位号改名 ★★                 │
                    │   (★板侧 156 个加 _1 ⇒ 见 §4-5 地雷 1★)   │
                    │                                           │
                    ▼                                           ▼
   ④  bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py
                    │
                    │  HW/PCB/demo_mainboard.kicad_pcb   ★★全表唯一改 md5 的件★★
                    │  ★★ gen_bom.py 要读板的封装 Value / 焊盘数 ★★
                    │  ★★ ⇒ BOM 必须在板之后 ★★
                    ▼
   ⑤  python3 state/gen_bom.py ──▶ HW/BOM_v1.csv
                    │
                    ▼
   ⑥  bash state/gen_production_pack.sh
        ├──▶ production/gerbers/  (32)
        ├──▶ production/drill/    (4)
        ├──▶ production/pos/      (1)   CPL
        ├──▶ production/assembly/ (3)   IPC-2581 + 装配图
        ├──▶ production/3d/       (1)   STEP
        ├──▶ production/doc/      (9)   PCB PDF×3 + DXF + D356 + stats + sch.pdf + kicad.net + kicad-bom.xml
        ├──▶ production/doc/sch_src/ (12) ★脚本自带 cp -p★
        ├──▶ production/doc/sch_svg/ (11)
        └──▶ production/MANIFEST.md5  (1)  BOARD_MD5 == 盘上板 md5
                    │
                    ▼
   ⑦  python3 state/chain_gate.py   (rc=0)
        python3 state/check_pcb_drc.py (unc=0 · DRC=0)
        python3 HW/check_onepass_s10_manifest.py (M1~M4)
        bash state/verify_and_release.sh → bash state/board_publish_gate.sh
        python3 state/merge.py && python3 state/gate_check.py
        人工: 落表台账追加 + 决策页 + state/fragments/hw.yaml (frag_write.py)
```

### ★4-2 · ★硬顺序 (★照 chain_gate 口径★) ★

★★**网表 → 原理图 → 板 → BOM → 投产包** ★★ ⇒ ★**BOM 在板之后 (★因为它读板★) · 投产包在一切之后 (★因为它读板 + 原理图★)** ★

★★**★一条补充 (★chain_gate 的「五环」里没有、但实际存在的第六个依赖★)**: ★**`HW/PCB/production/` 是【整包 rm -rf 重建】的 (★`state/gen_production_pack.sh` L25 `rm -rf "$OUT"`★) ⇒ ★**它不是【增量刷新】, 是【整包换新】⇒ ⇒ 那一趟只要板或原理图动了, 这 74 件就【全部】是新的; 不许只 cp 一两个** ★★

### ★4-3 · ★★「同趟出」清单 (★不许留旧件混进去★) ★★

> ★**★为什么必须列这张表: 今天的 ⑤ 红, 就是因为投产包里【混着 11-17 12:30 的旧原理图】+【11-17 21:59 的旧板 Gerber】⇒ 旧件混进去 = 板厂按旧件投板 = 2-4 周 + ¥4-8K 返工** ★

| # | ★**必须同趟重出的产物** ★ | ★**理由 (★为什么不能留旧件★)** ★ |
|---|---|---|
| ★**1** ★ | ★**板 `HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**唯一改 md5 的件** ★ ⇒ 所有下游都跟着变 ★ |
| ★**2** ★ | ★**Gerber 32 件 (★canonical `HW/PCB/gerbers/` + 投产包副本★)** ★ | ★**Gerber 是投板依据; 板一变它必变** ★ |
| ★**3** ★ | ★**钻孔 4 件** ★ | ★**孔位/孔径跟着板走 (★C_VBUS_GND 拿掉 = 少 2 个焊盘, ESD 换封装 = 焊盘变★)** ★ |
| ★**4** ★ | ★**坐标 CPL 1 件** ★ | ★**贴片坐标 = 板面落位; 封装数 186→185 + ESD 挪位 ⇒ CPL 必变** ★ |
| ★**5** ★ | ★**装配 3 件 (IPC-2581 + 顶/底装配图 PDF)** ★ | ★**同上** ★ |
| ★**6** ★ | ★**3D STEP 1 件** ★ | ★**同上** ★ |
| ★**7** ★ | ★**doc 9 件 (PCB PDF×3 / DXF / D356 / board-stats / sch.pdf / kicad.net / kicad-bom.xml)** ★ | ★**PCB PDF/DXF/D356 跟板走; sch.pdf/kicad.net/kicad-bom.xml 跟原理图走** ★ |
| ★**8** ★ | ★**sch_src 12 件 (★11 个 `.kicad_sch` + `.kicad_pro`★)** ★ | ★**★今天 ⑤ 红的直接原因; 且【11 个里 9 个只是 uuid 抖动】⇒ 一起同步才绿** ★ |
| ★**9** ★ | ★**sch_svg 11 件** ★ | ★**跟原理图走 (★给人看的渲染件, 但同批出免得评审人翻到旧图★)** ★ |
| ★**10** ★ | ★**`MANIFEST.md5`** ★ | ★**它声明「这一包是这一版板出的」⇒ 板变了它必须跟着重写 (★`BOARD_MD5` 行★)** ★ |
| ★**11** ★ | ★**BOM `HW/BOM_v1.csv`** ★ | ★**★它读板封装的 Value/焊盘数 ⇒ 板一改它就过期 ⇒ 环④ 会红** ★ |
| ★**12** ★ | ★**(条件) 网表 / 脚表 / 落表台账** ★ | ★**只有当 §4-5 地雷 1 拍成「三侧同口径改名」时才动; 不拍就不动 (★动了就得重出 3~12 全部★)** ★ |

### ★4-4 · 归属表 (★每件归给谁★) ★

| 归属 | 件 | 备注 |
|---|---|---|
| ★**hw** ★ | ★**① 网表 · ② 脚表 · ③ 原理图 11 页 + `.kicad_pro` · ④ 板 · ⑤ BOM · ⑥ 投产包 74 件 (含 Gerber/钻孔/CPL/装配/3D/doc/sch_src/sch_svg/MANIFEST) · ⑦ 分片** ★ | ★**板那一趟的执行面全在 hw** ★ |
| ★**sw** ★ | ★**不占本趟产物** ★ | ★**只关心一件事: 那一趟不许改网表语义 (★若真要落表, 须 sw-lead 复核 USB D+/D− 两侧网名拆分 (★`USB_D_P_SRC` / `NET_USB_D_P_TYPEC`★) 没被合并回去★)** ★ |
| ★**mech** ★ | ★**不占本趟产物** ★ | ★**只关心: 板 md5 一变, MECH 侧「读板」的判据全部要重锚 (★作业包 §3-S9 + `MECH/board_port_opening_s6_check.py`★)** ★ |
| ★**main** ★ | ★**落表台账追加 · 决策页刷新 · issue_log 签字 · 对外放行** ★ | ★**★C_VBUS_GND 留不留 = 老板/PM 域 (`boss_c_vbus_gnd_reserve_pad_20261117`) ⇒ main 拍, hw 不拍** ★ |

### ★4-5 · ★★★两个【必须开工前拍】的隐藏地雷 (★本单挖出来的·★不替老板拍★) ★★★

#### ★★地雷 1 · ★S1 板侧位号加 `_1` ⇒ 环③ C1 会【从「多余 2」变成「缺失 350 · 多余 352」】★★

★**实测 (★沙盒实验, ★项目文件一个字节没动★)**: ★**`logs/iss311/06_probe_s1_refsuffix_c1_collision.txt`** ★

| 场景 | C1 缺失 | C1 多余 | C1 同号异网 |
|---|---|---|---|
| ★**现役板 (基线)** ★ | ★**0** ★ | ★**2** ★ | ★**3** ★ |
| ★**沙盒: 按 ISS-205 规则给 156 个板上位号加 `_1`** ★ | ★**350** ★ | ★**352** ★ | ★**0** ★ |
| ★**反证: 网表侧 ref 也按同规则改口径 (只算, 不落表)** ★ | ★**0** ★ | ★**2** ★ | ★**3** ★ |

★**根因 (★本机实读★)**:
- ★**`state/check_pcb_nets.py` 的 `board_pads()` 取 `fp.GetReference()` 原样, `netlist_pads()` 取网表 ref 原样, `compare()` 直接比 (ref,pad) 键 ⇒ ★**两侧都没有「图上位号 → 表侧 ref」的反查** ★
- ★**`state/gen_kicad_sch.py::kicad_ref()` (ISS-205) = 末字符是数字 ⇒ 不动; 否则加 `_1`** ⇒ ★**原理图侧已经全用 `X_1`** (★实测: 11 页里 218 个位号中 187 个带 `_1`, 其中 186 个是改名来的, 1 个是原生 `R_BAT_DET_1`★)
- ★**`state/gen_pcb_netlist_board.py` 里 `kicad_ref` / `_1` 映射 = 零处命中** ⇒ ★**板生成器现在写的是【表侧原名】** (★实测: 板上 186 个位号, 带 `_1` 的只有 1 个 = `R_BAT_DET_1`★)
- ★**作业包 §5 的受保护表写「网表/脚表/BOM 逐字节不变」, 而 §3-S1 写「板侧 156 个封装位号要加 `_1`」⇒ ★**两者【自相矛盾】: 板改了名, 网表不改名 ⇒ C1 必红** ★

★**⇒ 两个选项 (★我不选, 交 main / 老板拍★)**:

| 选项 | 做法 | 代价 | 风险 |
|---|---|---|---|
| ★**①** ★ | ★**三侧同口径改名 (★网表 + 脚表 + 板 + BOM 一起落表★)** ⇒ 板生成器加 `kicad_ref()` 映射 (★照 `state/gen_kicad_sch.py` 同规则★) | ★**要落表 (★台账 + 网表 + 脚表 + BOM 全改★)** ⇒ ★**那一趟的工作量与风险都上一个台阶** ★ | ★**落表批次与板那一趟必须同批完成, 否则中间态更乱** ★ |
| ★**②** ★ | ★**板侧暂不加 `_1` (★S1 只做原理图侧, 板侧推迟或单开一批★)** ⇒ 板继续用表侧原名 | ★**板侧位号仍是 KiCad「未标注」态 ⇒ KiCad 导出 BOM 仍带 `?` ⇒ ★**那条 S1 验收判据 (问号行数 = 0) 在板侧达不到** ★ | ★**要另找一条问号清零的路径 (★例如改 KiCad 侧标注口径, 而不是改位号★)** ★ |

★★**⇒ 不管拍哪个, 【必须在开工前拍】: 因为 S1 是板侧改动 ⇒ 一旦改了名而网表没同步, 环③ 从「红 2 条」变成「红 702 条」⇒ 那一趟白跑** ★★

#### ★★地雷 2 · ★板侧位号改名 ⇒ BOM 的【板文件权威源回填】会静默失效★★

★**根因 (★本机实读★)**: ★**`state/gen_bom.py` 用【精确 ref】读板** ——
- ★**L277-303**: `board.get(ref, {})` 读 `J_SOM_P2` / `J_SOM_P4` ⇒ ★**读不到 ⇒ 板级归属 / 页位 / 封装 / opn 回填整段丢失** ★
- ★**L307-330 (★GAP29 定义在 L307 · 读板在 L317★)**: `board.get(ref)` 读 29 个器件的板封装 Value/焊盘数 ⇒ ★**其中约 24 个位号末字符是字母 (★会改名★) ⇒ 改完名就查不到 ⇒ ★**「封装/型号来源: 板文件 Value 属性 = …」那些证据行会整段消失, opn 可能退回 `待定` / `[0数据]`** ★
- ★**`state/gen_bom.py` L143-175 `_pick_value()`**: ★**表侧 value 为主, 板文件 Value 只作兜底 ⇒ 改名的器件一旦表侧 value 也空, 就会掉到兜底分支 ⇒ 兜底也读不到 ⇒ value 变 `待定`** ★

★★**⇒ 这条地雷的根和地雷 1 是同一个: 【板侧 ref 名与表侧 ref 名不一致时, 所有按 ref 读板的代码路径都会失效】★★
★★**⇒ 那两个受保护判据脚本 (`check_pcb_nets.py` / `check_pcb_drc.py`) 是不许改的 ⇒ ⇒ 口径必须在【数据侧】统一, 不能在【判据侧】打补丁** ★★

---

## ★5 · 证据分级 + 自证命令 ★

### ★5-1 · 证据分级 (★逐条标★) ★

| 结论 | ★**证据等级** ★ | 依据 |
|---|---|---|
| C1 = 缺失 0 / 多余 2 / 同号异网 3 / NC 351 / 非法 NC 0 | ★**[实测]** ★ | ★本机实跑 `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ rc=1 (★原始输出 `logs/iss311/01_check_pcb_nets_raw.txt`★) ★ |
| `C_VBUS_GND` pad1=GND (板 L8259) / pad2=VBUS_5V_CHG (板 L8267), 封装原点 (107.7, 42.5) | ★**[实测]** ★ | ★`.kicad_pcb` 原文逐行扫出 (★`logs/iss311/02_probe_c1_diff_raw.txt`★) ★ |
| 网表 L10/L12 的 `board` 列 = `CHG_BOARD` ⇒ 该件不在 MAIN_PCB | ★**[实测]** ★ | ★`HW/netlist_v1.csv` 原文 ★ |
| `Q_PG` pad1/pad3 网名与网表对调; `D_ESD_USB_D` pad1 挂在 SoM 侧网 | ★**[实测]** ★ | ★板 L2068/L2084/L13012 vs 网表 L59/L61/L417 ★ |
| 原理图 11 个不一致 = 9 uuid 抖动 + 2 内容旧 (p1/p10) | ★**[实测]** ★ | ★`python3 logs/iss311/probe_sch_src_diff.py` (★原始输出 `logs/iss311/03_probe_sch_src_diff_raw.txt`★) ★ |
| 源是新的 / 包是旧的 (p1/p10 内容差的 4 个判据点) | ★**[实测]** ★ | ★对 `HW/netlist_v1_pins.csv` L142-143 (★`C_SYS` = 必装 / `20µF X7R 6.3V`★) + `state/gen_kicad_sch.py` L101/L321/L381 的 DNP 规则 ★ |
| 板侧 156 个位号加 `_1` ⇒ C1 变「缺失 350 / 多余 352」 | ★**[实测]** ★ | ★沙盒实验 (`logs/iss311/06_probe_s1_refsuffix_c1_collision.txt`) ★ · ★**沙盒只写 `tmp/iss311_tmp/`, 项目文件零改动; 跑完已删** ★ |
| 板侧改名 ⇒ BOM 板文件回填失效 | ★**[实测]** ★ | ★`state/gen_bom.py` L277-303 / L307-330 / L143-175 按精确 ref 读板 (★本机实读代码★) ★ |
| `D_ESD_USB_D` 的 ESD 位置要求「紧贴 J_USB_C」 | ★**[推算]** ★ | ★依据是网表 note 原文 (★`HW/netlist_v1.csv` L417 的 note 列, ★转述 TI/模组厂指引★) ⇒ ★**未查官方原文 ⇒ [推算], 不是 [官网]** ★ |
| `Q_PG` 的 1=G / 2=S / 3=D 引脚序 | ★**[推算]** ★ | ★依据是作业包 §3-S0 的 `B11_Q_PG_LAND` 行转述 (★引 DMP3098L★) ⇒ ★**本单未查 DMP3098L 官方 datasheet ⇒ [推算]** ★ |
| `C_VBUS_GND` 留不留 | ★**[0数据]/待拍]** ★ | ★**老板/PM 域 (`boss_c_vbus_gnd_reserve_pad_20261117`) ⇒ ★**本单不拍, 只交事实与两条路的代价** ★ |
| 板侧改名 vs 网表侧改名, 选哪个 | ★**[0数据]/待拍]** ★ | ★**§4-5 地雷 1 ⇒ ★**本单只列两个选项与代价, 不选** ★ |

### ★5-2 · ★自证命令 (★main 复验时照这条跑★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss311_tmp          # ★本项目惯例: TMPDIR 指项目内, 别用 /tmp (★历史上多单因 /tmp 配额假红★)

# ★★① 现状基线 (★两条红如实在, 本单不许自己去改绿★)
python3 state/chain_gate.py                          # ⇒ rc=1 (③ PCB + ⑤ 投产包)
# ★原始输出: logs/iss311/04_chain_gate_baseline.txt ★

# ★★② C1 逐条证据
bash state/pcbnew_py.sh state/check_pcb_nets.py      # ⇒ rc=1
bash state/pcbnew_py.sh logs/iss311/probe_c1_diff.py # ⇒ rc=0
# ★原始输出: logs/iss311/01_check_pcb_nets_raw.txt / 02_probe_c1_diff_raw.txt ★

# ★★③ 原理图 11 个不一致逐条
python3 logs/iss311/probe_sch_src_diff.py            # ⇒ rc=0
# ★原始输出: logs/iss311/03_probe_sch_src_diff_raw.txt ★

# ★★④ S1 位号改名 × C1 的相撞实验 (★沙盒, 不碰项目★)
bash state/pcbnew_py.sh logs/iss311/probe_s1_refsuffix_c1_collision.py   # ⇒ rc=0
# ★原始输出: logs/iss311/06_probe_s1_refsuffix_c1_collision.txt ★

# ★★⑤ 现值表
cat logs/iss311/05_current_values.txt

# ★★⑥ 交卷前必跑
python3 state/chain_gate.py
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/production/MANIFEST.*
```

### ★5-3 · ★零写板双证 (★交卷前后逐字节相同★) ★

| 件 | ★**交卷前** ★ | ★**交卷后** ★ | 结论 |
|---|---|---|---|
| ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17`** ★ | ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17`** ★ | ★**零写板 ✔** ★ |
| ★**`HW/PCB/production/MANIFEST.md5`** ★ | ★**md5 `b78b9648b3001bc7c5b43a866064c94c`** ★ | ★**md5 `b78b9648b3001bc7c5b43a866064c94c`** ★ | ★**零重生成 ✔** ★ |
| ★**`HW/PCB/production/` 74 件** ★ | ★**总件数 74** ★ | ★**总件数 74** ★ | ★**零重生成 ✔** ★ |
| ★**`HW/netlist_v1.csv`** ★ | ★**`6aee500e60ba0732f83a9cf557ba90ab`** ★ | ★**同** ★ | ★**零落表 ✔** ★ |
| ★**`HW/netlist_v1_pins.csv`** ★ | ★**`9174309df1ec9411ac8e8d9e80ee386a`** ★ | ★**同** ★ | ★**零落表 ✔** ★ |
| ★**`HW/BOM_v1.csv`** ★ | ★**`5b9993992405904a60ac96a020b375d8`** ★ | ★**同** ★ | ★**零落表 ✔** ★ |
| ★**`state/chain_gate.py` / `gate_check.py` / `merge.py`** ★ | ★**未改** ★ | ★**未改** ★ | ★**零改闸 ✔** ★ |
| ★**`BOARD_ONEPASS_WORKPACKET.md` / `BOARD_ONEPASS_PREFLIGHT.md`** ★ | ★**只读** ★ | ★**只读** ★ | ★**零改既有文档 ✔** ★ |

---

## ★附 · 与既有作业包的关系 (★不重复、不替代★) ★

| 本清单的件 | ★**既有权威件** ★ | ★**关系** ★ |
|---|---|---|
| §1 C1 差 2 定位 | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S2 (★B-1 `C_VBUS_GND`★) · §3-S0 (★`B11_Q_PG_LAND` / `B32_V2_NET_RENAME`★) | ★**本清单补【逐条证据 + 行号 + 坐标】, 不重复写【怎么做】** ★ |
| §2 原理图 11 个 | `state/chain_gate.py::check_sch_src_pack()` | ★**本清单补【归一化口径下的分类 + 方向判定】, 不改闸** ★ |
| §3 重出清单主表 | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S1~S13 + §4 每步的闸 | ★**本清单补【产物级的一张表 + 同趟出清单】** ★ |
| §4-5 两颗地雷 | ★**无 (★本单新挖出来的★)** ★ | ★**★作业包 §5 写「网表/脚表/BOM 逐字节不变」, §3-S1 写「板侧 156 个要加 `_1`」⇒ ★**这两条自相矛盾 ⇒ 本单把冲突摆出来, 不替 main 拍** ★ |

★**★权威页分工**: ★**「怎么改板」= `BOARD_ONEPASS_WORKPACKET.md` (★改那一份, 不改它★) · 「改完要重出哪些」= 本文件 · 「S10 清单格式契约」= `BOARD_ONEPASS_S10_MANIFEST_SPEC.md` · 「板侧项全集」= `BOARD_ONEPASS_PREFLIGHT.md`★ ★★

★**★本文件到 2026-11-18 06:2x 的实测基线为准 (★`logs/iss311/05_current_values.txt`★); 那一趟跑完后, 本文件的【现值】列就过期了 ⇒ ★**那一趟收工时应重刷一次本文件的现值列** (★或直接归档为「那一趟的输入快照」★)★★ ★★
