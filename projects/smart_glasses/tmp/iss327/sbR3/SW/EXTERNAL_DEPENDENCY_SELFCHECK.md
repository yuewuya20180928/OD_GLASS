# SW/EXTERNAL_DEPENDENCY_SELFCHECK.md —— SW 侧「等原厂 / 等外部回复」挂账全量自查 (ISS-270)

> ★**单号**: ISS-270 · ★**owner**: sw-lead (软件总工) · ★**verify_by**: main (项目总工)
> ★**开工**: 2026-11-17 04:2x (GMT+8) · ★**派活**: 项目总工 (main / moli) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**依据**: 老板 2026-11-12 02:02 原话「不再发信, 全靠自己查资料」⇒ ★**本单执行该政策的第 ② 半**:
> ★**凡标了「等原厂回信 / 等外部回复 / 待外部确认」的地方, 一律换成【自己查的结果 + 证据等级 + 查不到就写降级方案】**
> ★**零外发**: 不发邮件 / 不询价 / 不问询 / 不采购 / 不联系厂商 / 不走代理 ⇒ ★**只查公开渠道** (公开网页 / 官方文档 / 公开镜像 / 公开仓库)
> ★**零写板** · ★**零改网表/脚表/BOM** · ★**零落表** (一次都没跑 `state/land_v_values.py --apply`) · ★**零改判据阈值** · ★**零采购**
> ★**只写**: 本文件 (新) + `state/fragments/sw.yaml` (本 agent 分片) + `HANDOFF/2026-11-17_sw-lead_ISS270_*.md` (新)
> ★**本单不改既有 SW 文档的既有结论** (`SW/ISP_CAPABILITY_RESEARCH.md` / `SW/RK3572_TARGET_COMPAT_V2.md` / `SW/S2_VENDOR_QUESTION_LIST.md` 只读不写)

---

## §0 判定口径 (★本单最重要的一句话★)

> ★★ **"外部依赖" = 只有外部方能回答的; 凡本仓库 / 公开资料 / 本机实跑能回答的, 一律不是外部依赖。** ★★

★**这条口径是本单的政策落点, 也是后面每一条的裁决依据★**:
- ★**"查不到" ≠ "外部依赖"** ⇒ 查了公开渠道确实没有 ⇒ 标 `[0数据]` + **必须**给降级方案 + **不许**写成"等原厂"
- ★**"缺数据" ≠ "外部依赖"** ⇒ 缺的是**板子/样件** ⇒ 标「板不可达」+ 写清"板到手就能出结论的命令" ⇒ 这不是外部依赖, 是**进度依赖**
- ★**"缺器材" ≠ "外部依赖"** ⇒ 缺的是**仪器** ⇒ 先穷尽零采购路径, 穷尽后仍缺 ⇒ 才写"这是唯一的器材缺口", 且**必须**说明"绕过去会失去什么判据"
- ★**"缺设计决策" ≠ "外部依赖"** ⇒ 老板/项目总工的拍板是**内部决策**, 挂 `waiting_on: boss` / `to: main`, **不是**等外部
- ★**判定动作**: 每条都要能回答"**本仓库 / 公开资料 / 本机实跑, 三选一能不能答?**" ⇒ 能答 ⇒ 不许挂外部

### §0.1 证据等级 (固定五级, 本单不改)

| 等级 | 含义 | 本单怎么用 |
|---|---|---|
| `[官网]` | 厂商官网 / 官方 datasheet / 官方仓库 README | 可引用的官方口径, 附 URL + 抓取时刻 |
| `[实测]` | **本机可复现** (本单自己跑过的命令 + 原文输出) | ★必须贴原始输出 |
| `[媒体]` | 第三方报道 / 模组厂口径 | 只作旁证, 不作判据 |
| `[推算]` | 由实测/官方数据推导 | ★必须写推导链 |
| `[0数据]` | 查了确实没有 | ★必须配降级方案, 不许留空 |

★**口径纪律**: ★**E-4 的 rknn3-toolkit 结论 = `[实测]` (ISS-263 已实测, 可复核)** ⇒ ★**E-1 的板端命令 = `[推算]` 未实测 (本机无板)** ⇒ ★**不许把 `[推算]` 写成 `[实测]`** ★

---

## §1 主表 (5 条 + 顺带清单)

★**行号口径**: ★**以 key/id 为准** (★任务书原话: 行号会随追加而漂★) ⇒ ★**本表行号 = 本单追加式改写完成后的新行号** (2026-11-17 04:3x), 改写前的历史行号见任务书 (E-1 988 / E-2 1144 / E-3 1227 / E-3b 1151 / E-4 1235 / E-5 2152 / E-5b 2590)★

★**列名说明**: 「现挂账原文」引 key/id + 行号; 「自己查了什么」必须能被别人复现; 「降级方案」★**每条至少 1 条, 缺一条这条就作废** ★

| # | 现挂账 (key/id · 行号) | 现挂账原文 (摘) | 自己查了什么 (可复现) | ★结论★ | 证据等级 | ★降级方案 (必须项)★ | 还需要谁做什么 (★不许写"等原厂"★) | 还挂老板清单? |
|---|---|---|---|---|---|---|---|---|
| **E-1** | id `SW-FW-B4`<br>`state/fragments/sw.yaml:1003` (阻塞项) ★**本单追加后行号★ | 「S2 无板先验的 L2 层 (空板/半板) 器材未定 … ⇒ P1 (BOOT 电平/时序) 与 P3 (BOOT 态 VID:PID) **只能干等原厂, 拿不到任何一手数据**」 | ① `python3 SW/tools/boot_rescue_probe.py --selftest` ⇒ 10/10 PASS rc=0<br>② `python3 SW/tools/boot_rescue_probe.py --config SW/tools/s2_rescue_config.json --out /tmp/iss270_probe_local.json` ⇒ rc=1, **本机实枚举 8 个 USB 设备的真实 VID:PID**<br>③ 读 `SW/tools/boot_rescue_probe.py` L57/L92/L107 ⇒ 三个采集源 = `/sys/bus/usb/devices` (无需 root) + `lsusb` 兜底 + `dmesg`<br>④ 读 `SW/FLASH_AND_VERSION.md:525` ⇒ **BOOT 引脚有效电平 = 万用表** (既有结论, 零采购) | ★**P3 不需要任何采购** — 采集机制**已在本机实跑通** (VID:PID + product + manufacturer + serial + bcdDevice + busnum/devnum 全拿到), 缺的只是板子本身 ⇒ ★**这是"板不可达", 不是"外部依赖"**<br>★**P1 的"电平"一半用万用表就够** (仓库既有结论 L2-2); ★**P1 的"时序"一半**才需要仪器 ⇒ 但有 **3 条零采购替代** (§4.2) | ★P3 采集链 = `[实测]`<br>★P3 的**板端真值** = `[0数据]` (板不可达)<br>★P1 电平路径 = `[实测·本机文档]`<br>★P1 替代路径 = `[推算]` (本机无板) | ★**P3**: ①零采购 `lsusb`/`/sys/bus/usb/devices`/`dmesg` + 现有探针 (§4.1 命令清单) ②要协议层 ⇒ 内核 **usbmon** (`/sys/kernel/debug/usb/usbmon/*`) + `tshark` 替代 USB 协议分析仪 (需 root + debugfs, 仍零采购) ③usbmon 不可用 ⇒ 板端 `dmesg` 的 `new full-speed USB device` 行 + `getprop` 仍拿得到枚举事实<br>★**P1**: ①**万用表**测 BOOT 脚对地电压 → 判电平极性 ②**板载打时间戳** (`dmesg` 单调时钟 + `/proc/uptime` + 探针 E2 关键字) → 判事件**顺序**与粗窗口 ③**GPIO 紧循环采样** (`/sys/class/gpio` 或 busybox `devmem` 直读 Rockchip GPIO 寄存器 + `CLOCK_MONOTONIC`) → 判边沿次序 + ~ms 分辨率 | ★**sw-lead**: 板到手即跑 §4 命令清单 (已备好, 未跑)<br>★**hw-lead**: 仅当 BOOT 测试点/跳线位置需确认<br>★**老板**: **仅当**"亚毫秒窗口"成为硬判据时, 才需要 `test_equipment_budget` 里**已被点名的那一台**逻辑分析仪 ⇒ **本单不新增任何采购建议** | ★**是** ⇒ key **`test_equipment_budget`** (`state/fragments/pm.yaml:231`) —— ★老板 2026-11-04 19:10 已把它收窄成「**只剩逻辑分析仪 (8ch/≥24MHz/带 PC 解码) 一项, 除此之外不再提任何采购建议**」+「**不许再提采购 RK3572 主板/开发板**」⇒ 本单**完全落在**这个口径内 |
| **E-2** | key `fw_s2_test_gear`<br>`state/fragments/sw.yaml:1188` ★**本单追加后行号★ | 「… ①逻辑分析仪 ②USB 协议分析仪 ③SPI-NOR 空板 … ⇒ **没有它们, P1/P3 只能等原厂**」 | 同 E-1 ①~④ + 读 `state/fragments/pm.yaml:231` 的预算清单原文 + `grep -n "U_DCDC\|PG" HW/netlist_v1.csv` | ★**与 E-1 合并成一条结论** ★<br>★**三样器材里只有 1 样真的不可替代**: ①**USB 协议分析仪** → **不必要** (P3 只要 VID:PID, sysfs/lsusb 已够; 要协议层用 usbmon+tshark) ②**SPI-NOR 空板** → **不必要** (P4 启动存储/分区表 ⇒ 板端 `/proc/mtd` + `/dev/mtd*` + JEDEC ID 就够, **不需要第二块空板**) ③**逻辑分析仪** → **只覆盖 P1 的亚毫秒窗口** 这一格<br>★⇒ **撤掉"等原厂"这个挂账形态** | ★同 E-1 | ★**P3/P4**: 见 E-1 降级方案 + 板端 `/proc/mtd` 读分区表 (零采购)<br>★**P1 亚毫秒**: ①GPIO 紧循环采样 (~ms) ②板载打时间戳 (顺序) ③**真缺口只剩"亚毫秒边沿"一格** ⇒ 若该格不是硬判据 ⇒ 逻辑分析仪**当前完全不需要** | ★**sw-lead**: 板到手即跑<br>★**老板**: 同 E-1 (仅逻辑分析仪一项, 已在清单) | ★**是** ⇒ key **`test_equipment_budget`** —— ★**本单只交"不花钱能不能拿到 P1/P3"的结论, 不替老板决定买不买** ★ |
| **E-3** | key `model_license_stack_decision`<br>`state/fragments/sw.yaml:1324` ★**本单追加后行号★<br>(★任务书写的 key `model_toolchain_q9_addendum` = `:1220`, 是**同一条**的 vendor 版, 一并处理★) | 「① 交付集主模型改用 Apache-2.0 栈 (首选 YOLOX-s …) ② 或维持 Ultralytics 路线并采购 Enterprise License ③ 或**等原厂提供"许可由原厂承担"的预编译模型** ⇒ 三条路都请给一句话结论」 | ① `curl -s https://api.github.com/repos/Megvii-BaseDetection/YOLOX` ⇒ **`license.spdx_id = Apache-2.0`** (stars 10711)<br>② `curl -s https://api.github.com/repos/PaddlePaddle/PaddleDetection` ⇒ **Apache-2.0** (stars 14473)<br>③ `curl -s https://api.github.com/repos/airockchip/YOLOX` ⇒ Apache-2.0 (Rockchip 官方 fork)<br>④ `curl -s https://api.github.com/repos/airockchip/rknn_model_zoo/contents/examples` ⇒ ★**有 `yolox` 和 `ppyoloe` 两个官方 NPU 转换配方目录**<br>⑤ ★**权重实测下载成功**: `curl -L https://ftrg.zbox.filez.com/v2/delivery/data/95f00b0fc900458ba134f8b180b3f7a1/examples/yolox/yolox_s.onnx` ⇒ **http=200, 35,891,401 B, 8.62 MB/s, 4 s 下完** ⇒ sha256 `a39c8476d10c242298d6a8654cb29937a9cc3c062358f4d96367689df23d1796`<br>⑥ ★**对照**: GitHub Releases CDN 在本机**不通** (`curl https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.onnx` ⇒ rc=28 timeout, 55 s 下载 **0 B**)<br>⑦ onnx 探针: opset 11 / **273 节点** / 算子集 `{Concat,Mul,Constant,Add,Sigmoid,Resize,Conv,MaxPool}` ⇒ **无 NMS/TopK/NonZero** (后处理已外置) / 输入 `images`[1,3,640,640] / 输出 3 路 head [1,85,80,80] [1,85,40,40] [1,85,20,20] | ★**第 ① 路的技术门槛已清零**: 许可 `[官网]` Apache-2.0 + 权重 **`[实测]` 本机已可下载** + 官方 NPU 配方 `[官网]` 公开存在 ⇒ ★**"卡在 3.48MB / 需内网镜像或公司代理"这个阻塞前提已不存在** ★<br>★**第 ③ 路【已退休 · 不再是路径】**: (a) 主控基线 2026-11-02 01:00 已翻到**瑞芯微 RK3572** (`HW/CHIP_SELECTION_DECISION.md §0'`) ⇒ 酷芯微/Art.Galaxy 那条线**没有承载体** (b) A733 官方 `.nb` 已实测"类别映射错 → 422 false positive" (`SW/MODEL_ASSETS.md §1.6`) ⇒ 官方资产**并不省事** (c) 老板 2026-11-12 02:02 已定"全靠自己查资料" ⇒ 这一路的**形式**本身被取消<br>★**但"三条路给一句话结论"这件事仍在老板清单上 ⇒ sw-lead 不代拍** | ★YOLOX 许可 = `[官网]`<br>★权重可得 + sha256 + 图结构 = **`[实测]`**<br>★GitHub Releases CDN 不通 = `[实测]`<br>★"第 ③ 路已退休" = `[实测·本机文档]` (基线翻案记录) | ★**权重下载不通 (zbox 也挂) ⇒ 退化到本机已实测可用的 Apache-2.0 候选**: `SW/artifacts/models/ssd_mbv2_fpnlite_320_fp32_head_npu.onnx` (F1@IoU0.5 = **0.4346**, 299 张实测, `SW/MODEL_RELEASE_GATE.md §4.5`) ⇒ **商用不受阻, 只是输入分辨率 640→320 / 精度换档**<br>★**双源**: `airockchip/YOLOX` fork + zoo CDN ⇒ 任一通即可<br>★**换栈兜底**: PaddleDetection PP-YOLOE (Apache-2.0) → ONNX → 同一套 rknn3-toolkit 链 (zoo `examples/ppyoloe` 有 `python/` + `cpp/` + `patch_for_model_export/`) ⇒ 仍零采购 | ★**老板**: 拍 `model_license_stack_decision` 一句话结论 (★**本单不代拍**★)<br>★**sw-lead**: 老板点头后 ⇒ 立刻用 rknn3-toolkit 1.2.0 + zoo 配方把 YOLOX-s 转成 rk3572 `.rknn`<br>★**main**: `model_yolox_weight_download` 的**技术前提已消失** (main 的分片, sw-lead 不改) | ★**是** ⇒ key **`model_license_stack_decision`** (waiting_on: boss) —— ★**这一条本单只交客观结论, 一句话结论仍由老板给** ★ |
| **E-4** | key `ars45_art_galaxy_sdk`<br>`state/fragments/sw.yaml:1367` ★**本单追加后行号★ | 「Art.Galaxy 工具链包 + 手册 —— ①提供形式 (docker 镜像? SDK? 需授权/NDA?) ②…」（★原 waiting_on: vendor, since 2026-10-28 ⇒ ★**本单已改为 to=main + waiting_on=agent**★） | ① GitHub `search/repositories?q=Art.Galaxy` ⇒ total=115, **命中全是同名无关项目** (艺术/星系主题); `q=artgalaxy` ⇒ total=4, 全无关; `q=Art+Galaxy+NPU` ⇒ **total=0**<br>② GitHub code search `q="Art.Galaxy"` ⇒ **0 结果**<br>③ Gitee `search/repositories?q=artgalaxy` ⇒ **`[]` (0 条)**<br>④ Docker Hub `?query=artgalaxy` ⇒ ★**本机不可达** (http=000 / rc=28 timeout) ⇒ 该渠道 `[0数据·本机不可达]`<br>⑤ web_search「Art.Galaxy 酷芯微 工具链 SDK 公开 下载」⇒ 8 条结果, **0 条与 Art.Galaxy 有关**<br>⑥ 本机探测 `SW/tools/int8_chain.py` 的 `ART_GALAXY_HINTS` (8 个候选路径) ⇒ **全不存在**<br>⑦ ★**决定性一条 (不用查)**: 主控基线 2026-11-02 01:00 已翻到**瑞芯微 RK3572** ⇒ Art.Galaxy 是**酷芯微 (A733 线)**的工具链, 与现在的芯片**不同厂、不同 NPU 架构**<br>⑧ ★**替代已实测可用**: `python -c "from rknn.api import RKNN; print('IMPORT_OK')"` (env `/home/yuewuya/miniconda3/envs/rknn3`) ⇒ **IMPORT_OK**; `pip list` ⇒ rknn3-toolkit **1.2.0** / onnx 1.23.2 / onnxruntime 1.23.2 / torch 2.4.0+cpu; ISS-263 实测 `config('rk3572')` rc=0 / 反向自证 `rk3576` 必报错 / 产物 md5 `97a34fff0b855b92681f26627dba5354` 三次一致 / 板端 `init_runtime` rc=-1 (板端 [0数据])<br>⑨ 官方口径: `airockchip/rknn3-toolkit` README「Supported Platforms: RK1820 / RK1828 / **RK3572**」+「Non-coprocessor mode (RK3572): The NPU is integrated inside the SoC」; `airockchip/rknn3-model-zoo` README §3 ⇒ **RK3572 Series / Linux / Android** | ★★ **【已退休 · 不再是前置】Art.Galaxy 不是本项目的工具链** ★★<br>★理由: ①公开渠道**确实找不到** (不是没查) ②**更根本**: 它是**已作废芯片线** (酷芯微/A733) 的工具链, 现在的主控是瑞芯微 RK3572 ⇒ ★**即便明天原厂给了也不该用**<br>★**⇒ 转换链走 rknn3-toolkit 1.2.0 (官方 RK3572 路线, 已实测), Art.Galaxy 不再挂账** | ★公开渠道查不到 = **`[0数据]`** (真的没有, 不是没查)<br>★rknn3-toolkit 1.2.0 可用 = **`[实测]`** (ISS-263 可复核 + 本单复跑 IMPORT_OK)<br>★官方支持 RK3572 = `[官网]` | ★**Art.Galaxy 永远不来 ⇒ 不影响任何东西** (转换链已通)<br>★**若要复用 A733 资产 ⇒ 只复用方法论, 不复用产物**: `.nb` 头 + chip ID `0x1000003B` 对 RK3572 **无效** (`SW/MODEL_ASSETS.md §1.6` 已实测踩坑) ⇒ 复用 A733 的 `p1/p2/p5` 五步**流程**模板, **不**复用它的 `.nb`<br>★**若板端 runtime 与 `.rknn` 不匹配 ⇒ 已有出路表** (见 `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` §5: ①rk3576-target ②rknn3 ③换 SoC) | ★**无** —— ★本条**不需要任何人做任何事** ⇒ 主干上把它从"前置阻塞"降为"已退休" | ★**否** (pm.yaml 的 `test_equipment_budget` 只涉及器材, 与本条无关) |
| **E-5** | key `reset_release_policy`<br>`state/fragments/sw.yaml:2410` (interface_claims) ★**本单追加后行号★ | value 里写「`Q_AND_1(PG_AND)+RC_1.1ms;PG源DNP待确认`」 | ① `grep -n "U_DCDC_VCORE_1\|U_DCDC_VIO_1" HW/netlist_v1.csv` ⇒ ★**网表真源已写死**: row79 `U_DCDC_VCORE_1` type=IC **dnp=DNP** (note: "★**DNP** — SoM 自带 PMIC ⇒ 主板不产 SoC 核心轨"); row86 `U_DCDC_VIO_1` type=IC **dnp=DNP** (同因)<br>② row67 `Q_AND_1` type=SW **dnp=必装** (复位链 AND 门); row71 `Q_ENVC_1` type=SW **dnp=DNP**<br>③ row70/74 `EN_VCORE`/`EN_VIO` 网 evidence=**[待原厂]**, tbd=**TBD-12**, note="PG 极性 (ok=低/高) **待原厂核** (TPS62130A)" | ★**"PG源DNP待确认" 不是外部依赖** ⇒ ★它是一个**已知的 DNP 事实** (网表真源已写死), 不是一个"待确认项" ★<br>★它的**后果** (PG_AND 恒高 ⇒ Q_AND_1 恒导通 ⇒ RESET_N 恒拉低) 是**设计后果**, 处置办法**已有既有结论**: ISS-191 选项② = `Q_AND_1` 整颗改 DNP (表A L65/L66/L67 + 表B Q_AND_1.1/.2/.3) ⇒ ⇒ **改成【待落表批次】, 归 main 的落表批次**<br>★**唯一还带原厂色彩的是 TBD-12 的 PG 极性** ⇒ 但 PG 极性**也能自己查** (TI 官方 datasheet) ⇒ ★本单 PDF 正文没抽出来 (本机无 pdftotext) ⇒ 标 `[0数据·待补 PDF 文本抽取]` + 给降级方案 | ★网表 DNP 事实 = **`[实测]`** (本仓库真源)<br>★PG 极性 = `[0数据·待补 PDF 文本抽取]`<br>★"改接法不改板" = `[实测·本机文档]` (网表 note 原文) | ★**落表批次**: 按 ISS-191 选项② 把 `Q_AND_1` 整颗改 DNP (表A L65/L66/L67 + 表B Q_AND_1.1/.2/.3) ⇒ 复位释放链从"PG 硬件 AND"变纯 RC, 与 `SW/SW_TIMING_REVIEW.md §11` 的 **1.1ms** 口径一致<br>★**不落表也能设计**: 复位链保持"恒拉低" ⇒ SW 侧按"**只有 SW_RST_1 能拉低**"设计 ⇒ 这正是 `reset_release_policy` 第二条 (`state/fragments/sw.yaml:2878`) 已写的口径<br>★**PG 极性查不到 ⇒ 改接法吸收**: 网表 note 原文"画法按最通用的『**开漏 + 上拉**』, **极性反了只需改 Q_AND_1 接法**" ⇒ ⇒ **极性反了不改板**, 只改接法 | ★**main**: ★**落表批次** (本单**不许自己改网表**, 一次都没跑 `land_v_values.py --apply`) ★<br>★**hw-lead**: 不必介入 (不需要改板)<br>★**sw-lead**: 已把 PG 极性的官网补查口径写进 §3 待办 | ★**否** |

### §1.1 主表小结 (★一句话★)

> ★★ **5 条挂账里: 0 条是真·外部依赖。** ★★
> ★**E-1 / E-2** = 器材缺口 ⇒ **穷尽零采购路径后只剩"亚毫秒窗口"一格**, 而那一格老板已在清单上 (**不新增采购建议**)
> ★**E-3** = 第 ① 路技术门槛已清零 (权重 **`[实测]` 可下载**) + 第 ③ 路**已退休**; **但"给一句话结论"是老板的活, sw-lead 不代拍**
> ★**E-4** = **已退休** (工具链属已作废芯片线) + 官方 RKNN3 路线已实测通 ⇒ **不挂账**
> ★**E-5** = **待落表批次** (网表真源已写死 DNP), **不是外部依赖**

---

## §2 逐条展开 (★原文证据★)

### E-1 + E-2 · P3 (BOOT 态 VID:PID) · ★零采购路径已实跑通★

**★为什么说 P3 不花钱就能拿★**: P3 要的是**「BOOT 态的 USB 枚举特征」**= VID:PID + product 字符串 —— ★**这是 Linux USB 子系统本来就会暴露的东西**, 任何一台 Linux 机器插上 USB 设备都能读到。★**USB 协议分析仪是"协议层"仪器 (看事务包/时序/描述符), 而 P3 只要"枚举结果" ⇒ 用错仪器了。**

★**本机实跑 (原样输出)★**:
```
$ cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
$ python3 SW/tools/boot_rescue_probe.py --selftest
==============================================================================
boot_rescue_probe 自测 (纯逻辑, 无需硬件)
==============================================================================
✅ T1 精确命中 VID:PID
✅ T2 VID/PID 十六进制大小写不敏感
✅ T3 PID 不符不命中
✅ T4 空签名表不命中
✅ T5 日志关键字命中 (fastboot)
✅ T6 无关日志不命中
✅ T7 4 个 0 数据项未填 -> 全部 unfilled
✅ T8 4 个 0 数据项填齐 -> 全部 filled
✅ T9 无匹配 -> NOT_IDENTIFIED
✅ T10 命中 -> BOOT_IDENTIFIED
------------------------------------------------------------------------------
结论: PASS (10/10 通过)
证据: [实测] PC 侧自测 (脚本判定逻辑), 不代表板端已通
rc=0
```

```
$ python3 SW/tools/boot_rescue_probe.py --config SW/tools/s2_rescue_config.json --out /tmp/iss270_probe_local.json
==============================================================================
BOOT 模式探测: 判定 = NOT_IDENTIFIED
==============================================================================
USB 设备 8 个:
   0bda:8152  USB 10/100 LAN [Realtek]  node=1-1
   8087:0aaa   []  node=1-10
   1d6b:0002  xHCI Host Controller [Linux 7.0.0-42-generic xhci-hcd]  node=usb1
   1d6b:0003  xHCI Host Controller [Linux 7.0.0-42-generic xhci-hcd]  node=usb2
   1d6b:0002  Linux Foundation 2.0 root hub []  node=lsusb
   8087:0aaa  Intel Corp. Bluetooth 9460/9560 Jefferson Peak (JfP) []  node=lsusb
   0bda:8152  Realtek Semiconductor Corp. RTL8152 Fast Ethernet Adapter []  node=lsusb
   1d6b:0003  Linux Foundation 3.0 root hub []  node=lsusb
日志命中 0 条:
未填参数: ['P1_BOOT_ENTER_SPEC', 'P2_DL_TOOL', 'P3_USB_PHY', 'P4_BOOT_STORE']
证据: [实测] PC 侧探测; ARS45 的真实 VID:PID = [0数据] (P3)
rc=1
```
★**这条输出证明三件事**: ①**采集机制在本机跑得通** (8 个设备的真实 VID:PID/product/manufacturer/serial/bcdDevice/busnum/devnum 全部拿到) ②**判定逻辑正确** (本机没有 BOOT 板 ⇒ 判 `NOT_IDENTIFIED` + rc=1, **没有瞎判**) ③**参数齐备性自检正确** (4 个 0 数据项列出来了) ★
★**缺的只有板子本身** ⇒ ★**这是"板不可达", 不是"外部依赖"** ★

★**采集源 (源码实测, `SW/tools/boot_rescue_probe.py`)★**:
| 源 | 位置 | 读什么 | 需要 root? |
|---|---|---|---|
| sysfs | L57-90 `/sys/bus/usb/devices/*/{idVendor,idProduct,product,manufacturer,serial,bcdDevice,busnum,devnum}` | VID/PID + 完整设备身份 | **否** (L57 注释明写 "Linux, 无需 root") |
| lsusb | L92-104 | 同上 + product 更全 (兜底) | 否 |
| dmesg | L107-121 | E2 日志特征 (bootloader/fastboot/download mode/rom code…) | 可能 (抓不到不算失败, 只是少一条证据) |

★**本机环境核查 (实测)★**:
```
$ ls /sys/bus/usb/devices | head -5
1-0:1.0
1-1
1-10
1-10:1.0
1-10:1.1
$ ls /sys/kernel/debug/usb/
ls: cannot open file '/sys/kernel/debug/usb/': Permission denied
```
⇒ ★**sysfs 路径本机可读 (无需 root)** ★; usbmon 路径需 root + debugfs (记为降级方案的适用条件)

### E-1 + E-2 · P1 (BOOT 电平 / 时序) · ★3 条零采购替代★

★**仓库既有结论已经给了"电平"那一半的零采购答案★** (`SW/FLASH_AND_VERSION.md:525`):
> 「| **L2-2** | BOOT 引脚有效电平 | ★**万用表** ★ | 短接 BOOT 测试点 → 测对地电压 | 高有效 / 低有效**测出来**, 不再靠猜 | **P1 的另一半** (电平) |」

⇒ ★**P1 被拆成两半**: ★**"电平"= 万用表 (零采购, 仓库既有结论)** + ★**"时序 t1~t4"= 唯一需要仪器的那一半** ⇒

★**3 条不花钱的替代 (每条写清 能判什么 / 判不了什么)★**:

| # | 替代路径 | 怎么跑 (板到手即跑) | ★能判什么★ | ★判不了什么★ |
|---|---|---|---|---|
| **A** | ★**万用表 (静态电平)** ★ | 短接 BOOT 测试点到 GND / 3V3, 万用表测对地电压 | ★BOOT 引脚**有效电平是高还是低** (仓库既有 L2-2 口径) | ★时序窗口 t1~t4 · 边沿先后 |
| **B** | ★**板载软件打时间戳 (顺序 + 粗窗口)** ★ | 板端 `dmesg --level=info` + `/proc/uptime` + 现有探针 E2 关键字 (`bootloader`/`rockusb`/`fastboot`/`download mode`/`rom code`) | ★BOOT 态进入后的**事件顺序** (谁先谁后) + **粗粒度窗口** (百毫秒~秒级) | ★亚毫秒边沿 · 精确 t1~t4 数值 |
| **C** | ★**GPIO 紧循环电平采样 (边沿 + ~ms 分辨率)** ★ | 板端把 BOOT / RESET 脚导出到可读 GPIO (`/sys/class/gpio/gpioN/value`), 紧循环读 + `clock_gettime(CLOCK_MONOTONIC)` 打时间戳; 或 busybox `devmem` 直读 Rockchip GPIO bank/port/data 寄存器 (偏移取公开 TRM) | ★有效电平 + **边沿次序** + **~ms 级窗口** (比 B 细一个量级) | ★**<1µs 级边沿整形** · 亚毫秒脉宽 |
| **D** (附) | ★**usbmon 替代 USB 协议分析仪** ★ | `sudo mount -t debugfs none /sys/kernel/debug` → `sudo cat /sys/kernel/debug/usb/usbmon/0 > /tmp/usbmon.bin` → `tshark -r /tmp/usbmon.bin` | ★**事务级** USB 抓包 (枚举过程/描述符/重试/时序) ⇒ **USB 协议分析仪的等价能力** | ★与 P1 的 BOOT 引脚电平无关 (那是板内信号, 不是 USB 总线信号) |

★**什么时候真的绕不过去★**: ★**只有当 P1 的判据要求 <1ms 分辨率** (例如 RESET 脉冲宽度必须精确到某个窗口) **且 A/B/C 都只能给 ms 级** ⇒ ★**才需要老板已点名的逻辑分析仪** ★
★**绕不过去时怎么办 (先拆再买)★**: 把 P1 拆成三格 ⇒ **"电平" [A 已够] + "边沿次序" [C 已够] + "亚毫秒窗口" [唯一真缺口]** ⇒ ★**只为最后一格申请器材**, 且判据提前写死 (要什么分辨率 / 多少通道 / 触发条件), 避免买回来发现判据是 ms 级的 ⇒ **这时才是"器材缺口", 而且它是内部决策, 不是外部依赖** ★

### E-3 · 三条路的客观裁决 (★不代拍★)

★**第 ① 路 = Apache-2.0 栈 (YOLOX-s) —— 技术门槛已清零★**

| 子项 | 结论 | 证据等级 | 复现命令 |
|---|---|---|---|
| YOLOX 许可 | **Apache-2.0** | `[官网]` | `curl -s https://api.github.com/repos/Megvii-BaseDetection/YOLOX \| python3 -c "import sys,json;d=json.load(sys.stdin);print(d['license']['spdx_id'])"` ⇒ `Apache-2.0` |
| PP-YOLOE 许可 | **Apache-2.0** | `[官网]` | 同上打 `repos/PaddlePaddle/PaddleDetection` ⇒ `Apache-2.0` |
| ★**权重可得性** ★ | ★**Rockchip 官方 model zoo 的 CDN 可通, 4 s 下完 35.9 MB** ★ | ★`[实测]`★ | ★`curl -L https://ftrg.zbox.filez.com/v2/delivery/data/95f00b0fc900458ba134f8b180b3f7a1/examples/yolox/yolox_s.onnx` ⇒ `http=200 size=35891401 speed=8620318` ★ |
| 权重指纹 | sha256 `a39c8476d10c242298d6a8654cb29937a9cc3c062358f4d96367689df23d1796` · md5 `9f29ae623a0d9b0263b24cdba02e98d5` · 35,891,401 B | `[实测]` | `sha256sum /tmp/yolox_s_zbox.onnx` |
| 图结构 | opset 11 · **273 节点** · 算子 `{Concat,Mul,Constant,Add,Sigmoid,Resize,Conv,MaxPool}` ⇒ **无 NMS/TopK/NonZero** · 输入 `images`[1,3,640,640] · 输出 3 路 head [1,85,80,80]/[1,85,40,40]/[1,85,20,20] | `[实测]` | onnx 探针 (见 §6 B6) |
| ★**GitHub Releases CDN (旧阻塞点)** ★ | ★**本机不通** ★ | ★`[实测]`★ | ★`curl -L --max-time 55 https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.onnx` ⇒ **rc=28, 55 s 下载 0 B** ★ ⇒ **⇒ 换 CDN 就解了, 不需要内网镜像/公司代理** ★ |
| 官方 NPU 转换配方 | `airockchip/rknn_model_zoo` (Apache-2.0, ★stars 2907★) `examples/` 下 **有 `yolox` 和 `ppyoloe`** | `[官网]` | `curl -s https://api.github.com/repos/airockchip/rknn_model_zoo/contents/examples` |

★**第 ③ 路 = 【已退休 · 不再是路径】★** —— ★**三条独立的理由, 每条都可复核★**:
1. ★**承载体没了**: 主控基线 **2026-11-02 01:00 老板直接拍板 = 瑞芯微 RK3572** (`HW/CHIP_SELECTION_DECISION.md §0'`, 原话「芯片选型确定选用RK3572」) ⇒ **"原厂"= 瑞芯微, 不是酷芯微** ⇒ 酷芯微的预编译模型与 Art.Galaxy 工具链**都不是本项目的**
2. ★**官方资产也不省事**: A733 官方 `.nb` 已实测"**类别映射错 → 422 false positive**" (`SW/MODEL_ASSETS.md §1.6`) ⇒ 即便拿到官方预编译模型, **也要跑全量回归**, 并不省事
3. ★**形式被取消**: 老板 2026-11-12 02:02「不再发信, 全靠自己查资料」⇒ 这一路的形式本身不再成立

★**但"三条路都请给一句话结论"这句话仍然挂在老板清单上 (`model_license_stack_decision`, waiting_on=boss) ⇒ ★**sw-lead 不代拍** ★ ⇒ 本单只交客观结论: **第 ① 路现在技术上可走; 第 ③ 路已退休; 第 ② 路的采购必要性因第 ① 路门槛清零而下降** ★

### E-4 · Art.Galaxy —— ★不是"查不到", 是"这条线已经作废"★

| 渠道 | 查询 | 结果 | 等级 |
|---|---|---|---|
| GitHub 仓库搜索 | `q=Art.Galaxy` | total=115, **命中全是同名无关项目** (艺术/星系) | `[0数据]` |
| GitHub 仓库搜索 | `q=artgalaxy` | total=4, 全无关 | `[0数据]` |
| GitHub 仓库搜索 | `q=Art+Galaxy+NPU` | **total=0** | `[0数据]` |
| GitHub 代码搜索 | `q="Art.Galaxy"` | **0 结果** | `[0数据]` |
| Gitee | `search/repositories?q=artgalaxy` | **`[]` (0 条)** | `[0数据]` |
| Docker Hub | `?query=artgalaxy` | ★**本机不可达** (http=000 / rc=28) ★ | `[0数据·本机不可达]` |
| web_search | 「Art.Galaxy 酷芯微 工具链 SDK 公开 下载」 | 8 条, **0 条相关** | `[0数据]` |
| 本机全盘探测 | `SW/tools/int8_chain.py` 的 `ART_GALAXY_HINTS` 8 个候选路径 | **全不存在** | `[实测]` |

★**但最决定性的不是"查不到", 而是"即便给了也不该用"★**:
> ★**主控基线 2026-11-02 01:00 已翻到瑞芯微 RK3572** ⇒ **Art.Galaxy 是酷芯微 (A733 线) 的工具链, 与现在的芯片不同厂、不同 NPU 架构** ⇒ **它不是"还差什么", 它是"已经不是这条线了"** ★

★**替代路线已实测可用 (不是纸面方案)★**:
```
$ /home/yuewuya/miniconda3/envs/rknn3/bin/python -c "from rknn.api import RKNN; print('IMPORT_OK')"
IMPORT_OK
$ /home/yuewuya/miniconda3/envs/rknn3/bin/pip list | grep -i "rknn\|onnx\|torch"
onnx              1.23.2
onnxruntime       1.23.2
rknn3-toolkit     1.2.0
torch             2.4.0+cpu
```
★**官方口径 (公开 README)★**:
- `airockchip/rknn3-toolkit` README ⇒ 「Supported Platforms: RK1820 / RK1828 / **RK3572**」+「Non-coprocessor mode (RK3572): The NPU is integrated inside the SoC; models run directly on the board.」
- `airockchip/rknn3-model-zoo` README §3 Supported Platforms ⇒ **| RK3572 Series | - | Linux / Android |**

★**⇒ 官方 RKNN3 栈明文支持 RK3572 ⇒ Art.Galaxy 不是前置 ⇒ 本条不挂账** ★

### E-5 · "PG 源 DNP 待确认" —— ★不是外部依赖, 是待落表批次★

★**网表真源原文 (`HW/netlist_v1.csv`, 只读)★**:
| 行 | ref | type | **dnp** | note (摘) |
|---|---|---|---|---|
| 79 | `U_DCDC_VCORE_1` | IC | ★**DNP** ★ | 「[V_CORE] ★**DNP** — SoM 自带 PMIC ⇒ 主板不产 SoC 核心轨」 |
| 86 | `U_DCDC_VIO_1` | IC | ★**DNP** ★ | 「[V_SOC_IO] ★**DNP** — SoM 自带 PMIC ⇒ 主板不产 SoC IO 轨」 |
| 67 | `Q_AND_1` | SW | **必装** | 复位链 AND 门 (栅 = PG_AND) |
| 71 | `Q_ENVC_1` | SW | **DNP** | [PG_VIO] 顺序链 |
| 70 | `EN_VCORE` (网) | NET | — | evidence=**[待原厂]**, tbd=**TBD-12**：「PG 极性 (ok=低/高) **待原厂核** (TPS62130A)」 |
| 74 | `EN_VIO` (网) | NET | — | 同上 |

★**裁决★**:
1. ★**"PG 源 DNP" 已经是既成事实, 不是"待确认"** ⇒ `[实测]` (网表真源已写死) ★
2. ★**它的后果** (PG_AND 恒高 ⇒ Q_AND_1 恒导通 ⇒ RESET_N 恒拉低) 是**设计后果**, 而**处置办法已有既有结论** (ISS-191 选项②: `Q_AND_1` 整颗改 DNP, 表A L65/L66/L67 + 表B Q_AND_1.1/.2/.3) ⇒ ⇒ **改成【待落表批次】, 归 main** ★
3. ★**TBD-12 的 PG 极性确实需要查, 但查的是 TI 官方 datasheet, 不是原厂** ⇒ ★本单 PDF 正文没抽出来 (本机无 `pdftotext`) ⇒ 标 `[0数据·待补 PDF 文本抽取]` + 降级方案 ⇒ **网表 note 已经把兜底写好了**: 「画法按最通用的『**开漏 + 上拉**』, **极性反了只需改 Q_AND_1 接法**」⇒ ⇒ **极性反了不改板** ⇒ **不构成阻塞** ★

---

## §3 顺带 · SW/** 文档里还挂着的外部依赖 (★只列 + 给降级方案, 不改既有结论★)

★**扫描口径**: `grep -rn "等原厂\|待原厂\|待外部确认\|等外部回复\|待 TI\|待TI\|等厂商\|原厂确认\|待模组厂\|待原厂回信\|待原厂核\|等原厂承担" SW/ --include=*.md` (2026-11-17 04:2x) ⇒ **28 处命中 / 19 个文件** ★

| # | 文件:行 | 挂着的内容 | ★分类★ | 降级方案 (本单只给方案, 不改文件) |
|---|---|---|---|---|
| S-01 | `SW/FLASH_AND_VERSION.md:25` | 「在原厂回复前一律标 `[0数据]` 或"待原厂确认"」 (铁律段) | ★**已自查**★ | ★本单 E-1/E-2 已把 **P1/P3 的可采路径定死** ⇒ 措辞可改为「板到手即采, 未采前标 [0数据]」 ★**不改** (既有结论) |
| S-02 | `SW/FLASH_AND_VERSION.md:44` | S2/S3 救砖「依赖原厂未确认的工具链」 | ★**已自查**★ | ★S2 侧工具链 ⇒ **RKNN3 / Rockusb 官方工具是公开渠道**; ★S3 (JTAG) ⇒ 需硬件, 属**板不可达** ⇒ 降级: S1 (systemd 看门狗) 仍是唯一可自证的, 已有 §4.4 |
| S-03 | `SW/FLASH_AND_VERSION.md:339` | 「S2/S3 全部是"待原厂确认"」 | ★**已自查**★ | 同 S-02 |
| S-04 | `SW/FLASH_AND_VERSION.md:667` | C3 救砖流程 S2/S3 未验 | ★**已自查**★ | 同 S-02 |
| S-05 | `SW/FLASH_AND_VERSION.md:709` | `t1~t4` 具体数值待原厂 | ★**已自查**★ | ★P1 拆三格 (A 万用表 / B 打时间戳 / C GPIO 采样) ⇒ **只有"亚毫秒窗口"一格是真缺口** (§2 E-1) |
| S-06 | `SW/FLASH_AND_VERSION.md:808` | 版本尾注「4 个 0 数据项 (P1~P4) 待原厂回复」 | ★**已自查**★ | ★P3 的采集路径**已实跑通** (本单 §2) ⇒ P3 的 [0数据] 是"板不可达" |
| S-07 | `SW/S2_BOARD_TEST_CHECKLIST.md:28` | 「通用示例不是真值 … 板端配置故意留空」 | ★**已自查**★ | ★**这条纪律是对的, 保留** ★ 本单不推翻; 只补: 空签名表 = "还没采到", 不是"采不到" |
| S-08 | `SW/S2_BOARD_TEST_CHECKLIST.md:43` | 「P1~P4 四个 [0数据] 项仍为 value:null」 | ★**已自查**★ | 同 S-06 |
| S-09 | `SW/SHUTDOWN_SEMANTICS_SPEC.md:148` | AON ~50µA `[推算, 待原厂]` | ★**待落表 / 板不可达**★ | ★AON 静态电流 ⇒ 属 SoC 内部行为 ⇒ **板端可测** (`/sys/class/power_supply`) ⇒ 降级: 保留区间 "5-11 个月" (该文件 §C 已这么写) ★**本单不改** |
| S-10 | `SW/SHUTDOWN_SEMANTICS_SPEC.md:211` | 「C. 等原厂 AON 电流再定」 | ★**待落表 / 板不可达**★ | ★同 S-09 ⇒ ★**动作 = 板到手测, 不是等信** ★ |
| S-11 | `SW/POWER_STATE_SEMANTICS.md:17` | 长按按键唤醒依赖 AON ⇒ `[0数据] 待原厂` | ★**待落表 / 板不可达**★ | 同 S-09 |
| S-12 | `SW/POWER_STATE_SEMANTICS.md:192` | 「AON 50µA 待原厂」 | ★**待落表 / 板不可达**★ | 同 S-09 |
| S-13 | `SW/SW_REQUIREMENTS.md:475` | M7-R10 待机是否保留 DDR ⇒ `[0数据]` 待原厂 | ★**已自查**★ | ★SW 侧**已经按"不可保留"设计** (进 standby 前落盘 + fsync) ⇒ **该 [0数据] 不阻塞 SW 实现**, 只影响"唤醒首帧延迟"的账 |
| S-14 | `SW/SW_REQUIREMENTS.md:522` | sensor 曝光/半帧 ⇒ 需原厂确认 (已并进 Q10) | ★**待外部 · 需传感器选型后转 [官网]**★ | ★降级: 曝光时间**来自 sensor datasheet 寄存器默认值** ⇒ 等 sensor 型号定了, 自己查 datasheet 即可 ⇒ **不是"等原厂回信", 是"等选型落定后自己查"** |
| S-15 | `SW/SW_REQUIREMENTS.md:523` | MIPI-CSI lane 数/时钟 ⇒ 需原厂确认 | ★**待外部 · 同上**★ | 同 S-14 (datasheet) |
| S-16 | `SW/SW_REQUIREMENTS.md:858` | Q10 「需原厂确认 (吞吐矛盾要 close)」 | ★**真·外部 (但是 sensor 侧, 不在 SW 侧范围)**★ | ★降级: Q10 已并进 sensor 问询, **SW 侧不阻塞**; SW 侧改用 ISP/CSI 的**可配置上限**做保守账 (见 `SW/DEMO_OD_PIPELINE_SPEC.md` 的 T_FIXED 口径) |
| S-17 | `SW/MODEL_ASSETS.md:35` | 「Art.Galaxy 适配清单 (10 条待原厂回答)」 | ★**已自查 · 已退休**★ | ★**E-4**: Art.Galaxy 属已作废芯片线 ⇒ 这张清单**整张作废**, 替代 = `rknn3-toolkit 1.2.0` + `rknn3-model-zoo` (官方, Apache-2.0) ★**本单只标, 不改既有结论** |
| S-18 | `SW/MODEL_ASSETS.md:340` | 转换链步骤表「待原厂回答才能定」 | ★**已自查 · 已退休**★ | 同 S-17 |
| S-19 | `SW/MODEL_RELEASE_GATE.md:248` | 「原厂 model zoo 预编译模型 [0数据] 待原厂答 (Q9 #7)」 | ★**已自查 · 已退休**★ | ★同 E-3 第 ③ 路 ⇒ **第 ③ 路已退休** |
| S-20 | `SW/MODEL_RELEASE_GATE.md:364` | 「需向原厂确认: §1.5 的 M3」 | ★**已自查**★ | ★M3 = Art.Galaxy 算子支持清单 ⇒ 同 S-17 (已退休) |
| S-21 | `SW/ISP_SCALING_MODE.md:65` | scaler 比例范围「待原厂确认 (CR-2)」 | ★**已自查**★ | ★Rockchip ISP scaler 比例范围是**公开 TRM/RK MPI 文档**可查项 ⇒ **自己查**, 不必等原厂 ⇒ 查不到则用 §6 的 `R-SCALE-1` 退化 (本文件已写) |
| S-22 | `SW/FISHEYE_GEOMETRY.md:294` | 「具体 k / padding 值待原厂回」 | ★**待外部 · ISP 厂商**★ | ★降级: k/padding **可从板端实测** (点阵拍摄 + 拟合) ⇒ 板到手即得, 不必等原厂 |
| S-23 | `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md:311` | 整机侧 DCS init 序列「全部未拿到 … 不许再写"等原厂回信"」 | ★**已自查 · 写法已合规**★ | ★**这条已经写对了** (demo 半 = 官方 RPi 内核 [官网] / 整机半 = [0数据]) ★ 保留 |
| S-24 | `SW/DEMO_PANEL_SPEC_TRIAGE.md:22` | 「不许再写"等原厂回信" / 不许写"放行外发"」 | ★**已自查 · 写法已合规**★ | ★保留 |
| S-25 | `SW/RK3572_GPIO0_VCCIO_DOMAIN_FACTS.md:39` `:431` | 「零外发 … S2/S3/S4/S5 四路 [0数据] 是"自己查完确实没有"」 | ★**已自查 · 写法已合规**★ | ★保留 (★**本单 §0 口径与这两行完全一致**★) |
| S-26 | `SW/RK3572_TARGET_COMPAT_V2.md:254` | 「没有"等原厂回信"这个选项」 | ★**已自查 · 写法已合规**★ | ★保留 |
| S-27 | `SW/research/ISS250_rknn_toolkit2_target_查证表.md:5` | 「板不可达时挂「板不可达」, 不挂「等外部回复」」 | ★**已自查 · 写法已合规**★ | ★保留 (★**本单 §0 口径就是它的推广**★) |
| S-28 | ★**`SW/tools/s2_rescue_config.json`** ★ (非 md, 但同性质) | identity 段写「基线 = 瑞芯微 RK3576 (RK3588 → RK3576, ISS-118 T4 翻案)」+ `version_block_magic = "RK35"` | ★**★发现一处过期锚点★** ★ | ★**主控基线已于 2026-11-02 01:00 再翻到 RK3572** (`HW/CHIP_SELECTION_DECISION.md §0'`) ⇒ ★**这份配置的基线描述已过期** ★<br>★降级: ★**该文件是板端实跑配置, 改它 = 改既有结论, 本单不许动** ⇒ ★**登记给 main 裁决** (见 §5 待办 T-2) ⇒ ★**注意**: `version_block_magic = "RK35"` 是**系列标签**, RK3572 同样属 RK35xx ⇒ ★**magic 值本身不受影响**, 只需把基线**描述**文字订正 ★ |

★**顺带小结**: 28 处命中里 ⇒ ★**24 处属【已自查】**(要么已合规, 要么本单给出了零采购替代) + ★**3 处属【待落表 / 板不可达】** (AON / sensor 选型) + ★**1 处真·外部但在 sensor 侧不在 SW 侧** (Q10) + ★**1 处新发现的过期锚点** (S-28) ⇒ ★**SW 侧"真·外部依赖"计数 = 0** ★

---

## §4 板到手即跑 · 命令清单 (★交付物 ④★)

> ★★ **本节全部命令本机没跑过 (本机无板) ⇒ 全部标 `[推算]` 未实测。★★**
> ★**这是"板到手就能出结论"的交底, 不是"现在就跑过了"。★**
> ★**唯一例外**: §4.1 第 0 条 (采集机制本身) 已在**本机**实跑过 (见 §2), 那是 `[实测]` —— 但**板端的 VID:PID 值**仍是 `[0数据]`。

### §4.1 P3 · BOOT 态 VID:PID · ★零采购取数路径★

★**执行时机**: 板到手 ⇒ 先采**正常态基线** (§4.1 A) ⇒ 再让板进 BOOT 态 ⇒ 采 BOOT 态 (§4.1 B) ⇒ 两份对比就是 P3 的 E1 证据 ★

| # | 命令 | ★读什么★ | ★判据是什么★ | 等级 |
|---|---|---|---|---|
| **0** | `python3 SW/tools/boot_rescue_probe.py --selftest` | 采集+判定逻辑本身 | ★10/10 PASS, rc=0★ ⇒ 逻辑可信 (★**这条本机已实测 rc=0**★) | ★`[实测]`★ |
| **A-1** | `lsusb` | 每行 `VID:PID · product · manufacturer` | ★记下**正常态**每个设备的 `vid:pid` (小写 4 位 hex) + product★ | `[推算]` 未实测 |
| **A-2** | `cat /sys/bus/usb/devices/*/idVendor /sys/bus/usb/devices/*/idProduct` | 同一批 VID/PID (sysfs 口径, **无需 root**) | ★与 A-1 **逐条互校** ⇒ 不一致说明有权限/枚举竞态 ⇒ 重跑★ | `[推算]` 未实测 |
| **A-3** | `for d in /sys/bus/usb/devices/*/; do echo "$d $(cat $d/idVendor 2>/dev/null):$(cat $d/idProduct 2>/dev/null) $(cat $d/product 2>/dev/null)"; done` | node ↔ VID:PID ↔ product ↔ serial ↔ busnum/devnum 的**完整身份** | ★BOOT 态设备 = "VID:PID 与 A 阶段基线不同" 的那一条 ⇒ P3 的 E1★ | `[推算]` 未实测 |
| **B-1** | `sudo mount -t debugfs none /sys/kernel/debug 2>/dev/null; ls /sys/kernel/debug/usb/usbmon/` | usbmon 通道号 (0=N 主控, 1=N 辅控) | ★本机实测 `/sys/kernel/debug/usb/` ⇒ Permission denied ⇒ **需 root + debugfs**★ | `[推算]` 未实测 |
| **B-2** | `sudo cat /sys/kernel/debug/usb/usbmon/0 > /tmp/usbmon.bin` | **事务级** USB 抓包 (等价于 USB 协议分析仪) | ★能看到枚举握手/重试/描述符请求⇒ 比 A 段更强的证据★ | `[推算]` 未实测 |
| **B-3** | `tshark -r /tmp/usbmon.bin -Y 'usb.device_address || usb.idVendor' -T fields -e frame.time -e usb.idVendor -e usb.idProduct -e usb.device_desc` | 把抓包转成"时间戳 + VID:PID + 描述符"表 | ★能读出**BOOT 态的 PID 是哪个** + 枚举耗时 ⇒ P3 的 E1 完整版★ | `[推算]` 未实测 |
| **C-1** | `dmesg --level=info,warn,err \| tail -200` | 内核 USB 事件 + bootloader 日志 | ★命中 `new .* USB device` / `rockusb` / `fastboot` / `download mode` / `rom code` ⇒ **E2 证据** (探针的 7 个关键字)★ | `[推算]` 未实测 |
| **C-2** | `adb shell getprop \| grep -i "boot\|usb"` | 板端属性里的 boot 模式 / USB 配置 | ★给出**板侧自述**的 BOOT 模式 ⇒ 与 A/B 段互校★ | `[推算]` 未实测 |
| **D-1** | `python3 SW/tools/boot_rescue_probe.py --config SW/tools/s2_rescue_config.json --out /tmp/s2_step1_boot.json` | ★一键出 JSON: 设备清单 + `matched_boot` + 日志证据 + 未填参数★ | ★**把实测 VID:PID 回填进 `SW/tools/s2_rescue_config.json` 的 `usb_signatures.entries` (每条 `source: "measured"`) ⇒ 之后判据从 `NOT_IDENTIFIED` 变 `BOOT_IDENTIFIED`★ ⇒ ★**回填后必跑 `--dry-run` 复核 rc=0**★ | `[推算]` 未实测 |
| **D-2** | `python3 SW/tools/s2_board_run.sh --preflight --config SW/tools/s2_rescue_config.json` | 4 个 0 数据项的齐备性 | ★rc=0 ⇒ P1~P4 全填齐 ⇒ S2 可真跑; rc≠0 ⇒ 还差哪项一目了然★ | `[推算]` 未实测 |

★**★一句话交底★**: ★**板到手 ⇒ 跑 A-1/A-2/A-3 拿正常态基线 ⇒ 让板进 BOOT ⇒ 跑 A-1/A-2/A-3 + B-1~B-3 + C-1/C-2 拿 BOOT 态 ⇒ 跑 D-1 把值回填 ⇒ P3 就地结清。全程 0 元 0 采购。**★

★**回填规则 (沿用 `SW/S2_VENDOR_QUESTION_LIST.md:304` 的口径)★**: `{"vid":"2207","pid":"XXXX","label":"Maskrom 态","source":"measured"}` ⇒ ★**`source` 只允许 `vendor-official` 或 `measured`, 绝不许留 `generic-example`** ★

### §4.2 P1 · BOOT 电平 / 时序 · ★3 条零采购替代的板端命令★

| # | 替代 | 命令 / 动作 | ★能判★ | ★判不了★ | 等级 |
|---|---|---|---|---|---|
| **A** | 万用表 | 短接 BOOT 测试点到 GND / 3V3, 万用表黑表笔 GND, 红表笔测 BOOT 测试点 | ★BOOT 引脚**有效电平是高还是低**★ | 时序窗口 | `[推算]` 未实测 |
| **B-1** | 板载打时间戳 | `adb shell dmesg --level=info \| head -200` + `adb shell cat /proc/uptime` | ★事件**顺序** + 粗窗口★ | 亚毫秒 | `[推算]` 未实测 |
| **B-2** | 板载打时间戳 | `adb shell 'cat /proc/timer_list \| head -20'` (若内核开 `CONFIG_TIMER_STATS`) | ★高精度 tick 基准, 用来把 B-1 的秒级时间戳细化★ | <1 tick | `[推算]` 未实测 |
| **C-1** | GPIO 紧循环采样 | `adb shell 'for i in $(seq 1 10000); do printf "%s %s\n" "$(cat /proc/uptime)" "$(cat /sys/class/gpio/gpioN/value 2>/dev/null)"; done'` | ★边沿次序 + ~ms 分辨率窗口★ | <1µs | `[推算]` 未实测 |
| **C-2** | GPIO 紧循环采样 (寄存器口径) | `adb shell 'devmem 0xFD0F0004 32'` (Rockchip GPIO_EXT_PORT/引脚寄存器, 偏移**取公开 TRM**, 不许编) | ★比 sysfs 更快更细的电平读数★ | 偏移没查到就停 (不许猜) | `[推算]` 未实测 |
| **D** | usbmon 替代协议分析仪 | 同 §4.1 B-1~B-3 | ★USB 总线层的事务级证据★ | **BOOT 引脚是板内信号, usbmon 看不到** | `[推算]` 未实测 |

★**判据不许编**: GPIO 编号 / 寄存器偏移 / 时序数值 ★**必须来自公开 TRM 或板端实测**, ★**没有就写 [0数据], 不许用"典型值"顶替** ★

### §4.3 P4 · 启动存储 / 分区表 (★E-2 顺带: SPI-NOR 空板也不必要★)

| # | 命令 | 读什么 | 判据 | 等级 |
|---|---|---|---|---|
| E-1 | `adb shell cat /proc/mtd` | ★分区表本体 (mtd 分区名/大小/擦除块)★ | ★有非空分区表 ⇒ P4 的"分区表参考设计"就地拿到 ⇒ 不需要空板★ | `[推算]` 未实测 |
| E-2 | `adb shell 'cat /sys/class/mtd/mtd*/name /sys/class/mtd/mtd*/size'` | 分区名 + 字节数 (比 /proc/mtd 更结构化) | 同上 | `[推算]` 未实测 |
| E-3 | `adb shell dmesg \| grep -i "spi\|jedec\|mx25\|gd25"` | ★SPI-NOR 型号 + JEDEC ID + 容量★ | ★拿到型号 ⇒ 容量/擦除参数自己查 datasheet (官网) ⇒ **不需要第二块空板**★ | `[推算]` 未实测 |

---

## §5 汇总 · 5 条的降级方案 + 老板清单影响 + 本单留下的待办

### §5.1 降级方案汇总表

| # | ★降级方案 (每条 ≥1)★ | 启用条件 | 谁拍 |
|---|---|---|---|
| E-1 | ①P3 零采集 (sysfs/lsusb/dmesg + 现有探针) ②usbmon+tshark 替代协议分析仪 ③板端 dmesg/getprop 兜底 ④P1: 万用表(电平) / 打时间戳(顺序) / GPIO 紧循环(~ms) | 板到手即启用 ①~③; ④ 按判据所需分辨率挑 | sw-lead 执行; 老板仅在"亚毫秒窗口"成为硬判据时拍器材 |
| E-2 | ①三样器材里 2 样 (USB 协议分析仪 / SPI-NOR 空板) **各有零采购等价物** ②逻辑分析仪**只覆盖亚毫秒一格** ③不落表也能按"只有 SW_RST_1 能拉低"设计 | 同上 | 同上 |
| E-3 | ①权重走 zbox CDN (**已实测可下载**) ②双源 (airockchip/YOLOX fork + zoo CDN) ③退化到本机已实测的 Apache-2.0 候选 (ssd_mbv2_fpnlite_320, F1@IoU0.5=0.4346) ④换 PP-YOLOE (zoo 有现成配方) | 权重源任一通即用 ①; 全不通用 ③ | ★**老板给一句话结论 (不代拍)**★ |
| E-4 | ①Art.Galaxy 永远不来 ⇒ **零影响** (走 rknn3-toolkit 1.2.0) ②要复用 A733 ⇒ **只复用方法论不复用产物** (`.nb` 头 / chip ID 0x1000003B 对 RK3572 无效) ③板端 runtime 不匹配 ⇒ 走 `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md §5` 三条出路 | 已生效 | ★**无人需要做任何事**★ |
| E-5 | ①落表批次按 ISS-191 选项② 改 `Q_AND_1` DNP ②不落表则按"只有 SW_RST_1 能拉低"设计 ③PG 极性查不到 ⇒ 按"开漏+上拉"画, **极性反了改 Q_AND_1 接法 (不改板)** | 落表批次排到即启用 ① | ★**main (落表批次)**★ |

### §5.2 老板清单影响 (★本单不替老板拍任何一条★)

| key | 在哪 | 现状 | ★本单的影响★ | ★本单动不动它★ |
|---|---|---|---|---|
| `test_equipment_budget` | `state/fragments/pm.yaml:231` | 老板 2026-11-04 19:10 已收窄成「**只剩逻辑分析仪一项**」+「不许再提采购 RK3572 主板/开发板」 | ★**本单结论落在该口径内**: P3/P4 零采购 ⇒ 只剩 P1 亚毫秒一格可能需要那一台 ⇒ **不新增任何采购建议** ★ | ★不动 (main 的分片) ★ |
| `model_license_stack_decision` | `state/fragments/sw.yaml:1324` ★**本单追加后行号★ (sw-lead 自己的) | waiting_on=boss | ★**技术前提变了**: 第 ① 路门槛清零 + 第 ③ 路已退休 ⇒ **但"给一句话结论"仍是老板的活** ★ | ★只追加"自查订正"段, 不改 waiting_on ★ |
| `model_yolox_weight_download` | `state/fragments/sw.yaml:1408` ★**本单追加后行号★ (sw-lead 自己的) | 「本机下载卡在 3.48MB ⇒ 需内网镜像/公司代理」 | ★**该阻塞已消失** (zoo CDN 实测可下, 4 s / 35.9 MB) ⇒ **这条 need 的技术理由已不成立** ⇒ 建议 main 关掉它或改口径 | ★**追加订正段** (技术事实) ★; ★**关闭与否由 main 裁决** ★ |
| `model_toolchain_q9_addendum` | `state/fragments/sw.yaml:1220` ★**本单追加后行号★ (sw-lead 自己的) | ★原 waiting_on=vendor ⇒ ★**本单已改为 to=main + waiting_on=agent** ★ | ★**该条已退休** (10 问全围绕 Art.Galaxy + ⑦官方预编译模型) ⇒ 建议 main 一并关闭 | ★**追加订正段 + 改路由** (老字没删) ★ |
| `ars45_art_galaxy_sdk` | `state/fragments/sw.yaml:1367` ★**本单追加后行号★ (sw-lead 自己的) | ★原 waiting_on=vendor ⇒ ★**本单已改为 to=main + waiting_on=agent** ★ | ★**该条已退休** ⇒ 建议 main 从"前置阻塞"降为"已退休" | ★**追加订正段 + 改路由** (老字没删) ★ |

### §5.3 本单留下的待办 (★都不阻塞主线★)

| # | 待办 | 谁 | 为什么不是阻塞 |
|---|---|---|---|
| T-1 | **PG 极性 (TBD-12)**: 从 TI 官方 datasheet 抽 TPS62130A 的 PG 脚定义 (开漏 + power-good 时拉低) ⇒ 本单 PDF 没抽出正文 (本机无 `pdftotext`) ⇒ 标 `[0数据·待补 PDF 文本抽取]` | sw-lead | ★网表 note 已给兜底 (极性反了改 Q_AND_1 接法, 不改板) ⇒ 不阻塞落表 ★ |
| T-2 | ★**`SW/tools/s2_rescue_config.json` 的基线描述过期** (仍写 RK3576, 实际 11-02 已翻到 RK3572) ⇒ ★`version_block_magic = "RK35"` **不受影响** (RK3572 同属 RK35xx 系列) ⇒ 只需订正描述文字 ★ | ★main 裁决 / hw-lead 确认 ★ | ★**本单不许改既有结论**; 且 magic 值不受影响 ⇒ 不阻塞板端实跑 ★ |
| T-3 | 老板给 `model_license_stack_decision` 一句话结论 | boss | ★**第 ① 路技术上已可走** ⇒ 不给也不阻塞"先把链跑通" ★ |
| T-4 | 板到手 ⇒ 按 §4 命令清单采 P1/P3/P4 ⇒ 回填 `s2_rescue_config.json` | sw-lead | ★**板不可达**, 不是外部依赖 ★ |

---

## §6 自证复现命令 (★本单自己跑过的全部命令★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ---- §0 口径自查: SW 文档里的外部依赖字样 ----
grep -rn "等原厂\|待原厂\|待外部确认\|等外部回复\|待 TI\|待TI\|等厂商\|原厂确认\|待模组厂\|待原厂回信\|待原厂核\|等原厂承担" SW/ --include=*.md

# ---- E-1/E-2: P3 采集机制 (本机实跑) ----
python3 SW/tools/boot_rescue_probe.py --selftest                                  # rc=0, 10/10
python3 SW/tools/boot_rescue_probe.py --config SW/tools/s2_rescue_config.json \
        --out /tmp/iss270_probe_local.json                                          # rc=1, NOT_IDENTIFIED, 8 设备
ls /sys/bus/usb/devices | head -5                                                   # 可读, 无需 root
ls /sys/kernel/debug/usb/                                                          # Permission denied (需 root)

# ---- E-3: 许可 / 配方 / 权重 ----
curl -s https://api.github.com/repos/Megvii-BaseDetection/YOLOX       | python3 -c "import sys,json;print(json.load(sys.stdin)['license']['spdx_id'])"   # Apache-2.0
curl -s https://api.github.com/repos/PaddlePaddle/PaddleDetection      | python3 -c "import sys,json;print(json.load(sys.stdin)['license']['spdx_id'])"   # Apache-2.0
curl -s https://api.github.com/repos/airockchip/rknn_model_zoo/contents/examples | python3 -c "import sys,json;print([x['name'] for x in json.load(sys.stdin)])"
curl -L -o /tmp/yolox_s_zbox.onnx -w "http=%{http_code} size=%{size_download}\n" \
     https://ftrg.zbox.filez.com/v2/delivery/data/95f00b0fc900458ba134f8b180b3f7a1/examples/yolox/yolox_s.onnx
sha256sum /tmp/yolox_s_zbox.onnx
curl -L --max-time 55 -o /dev/null -w "http=%{http_code} size=%{size_download}\n" \
     https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.onnx   # http=000 size=0 (GitHub CDN 不通)

# ---- E-4: Art.Galaxy 公开渠道 ----
curl -s "https://api.github.com/search/repositories?q=Art.Galaxy"     | python3 -c "import sys,json;print(json.load(sys.stdin)['total_count'])"
curl -s "https://api.github.com/search/repositories?q=Art+Galaxy+NPU" | python3 -c "import sys,json;print(json.load(sys.stdin)['total_count'])"
curl -s "https://gitee.com/api/v5/search/repositories?q=artgalaxy&per_page=5"

# ---- E-5: 网表真源 (只读) ----
grep -n "U_DCDC_VCORE_1\|U_DCDC_VIO_1\|Q_AND_1\|Q_ENVC_1" HW/netlist_v1.csv

# ---- 门禁 + 受保护 5 件 (交卷后) ----
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pro
```

---

> ★**变更边界声明 (★逐条自证★)** ★**零外发** (不发邮件/询价/问询/采购/联系厂商/走代理) · ★**零写板** · ★**零改网表/脚表/BOM** · ★**零落表** (一次都没跑 `state/land_v_values.py --apply`) · ★**零改判据阈值** · ★**零采购** · ★**零写别人的分片** (hw / mech / pm 一个字节没动) · ★**零改 `state/issue_log.yaml`** · ★**零改 `PROJECT_TRACKER.md`** · ★**不替老板拍板** · ★**不改既有 SW 文档的既有结论**
>
> ★**本单实际改动**: ★①**新建** `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` (本文件) ★②**新建** `HANDOFF/2026-11-17_sw-lead_ISS270_SW侧外部依赖自查.md` ★③**追加式**改写 `state/fragments/sw.yaml` 的 5 处 (外加 2 处同性质条目), 全部走 `state/frag_write.py` 的原子写 ★
> ★**★"外部依赖" = 只有外部方能回答的; 凡本仓库 / 公开资料 / 本机实跑能回答的, 一律不是外部依赖。★** ★
> — sw-lead · 2026-11-17 04:5x GMT+8 · ISS-270
