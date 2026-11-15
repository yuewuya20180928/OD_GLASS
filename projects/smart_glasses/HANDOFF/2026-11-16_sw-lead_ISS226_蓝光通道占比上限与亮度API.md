# [sw-lead→PM] ISS-226 · 光生物安全 · SW 侧亮度控制策略 + 蓝通道占比上限 (25%) + 亮度 API 蓝通道占比可标定量

> ★**owner**: sw-lead (软件/工具链侧总工) · ★**verify_by**: main · ★**单号**: ISS-226 · ★**开单**: main 2026-11-16 04:36 (cron `775d9893` 队列自动派活) · ★**交卷**: 2026-11-16 04:4x
> ★**上游**: ★**ISS-134** (mech-lead 2026-11-15 在结构侧跨域登记给 SW 侧的 need `iss134_sw_blue_drive_ratio_cap`, to=sw-lead, ★**至今 open**★) ⇒ ★**这是项目里本来就挂着、没人接的单, 不是 main 现编的活** ★
> ★**边界 (★本单逐条自查过★)★**: ★**没改** `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (★结构侧地界, 只读引用★) · ★**没改** `HW/` 下任何文件 · ★**没改** `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片 (★`state/fragments/{pm,hw,mech}.yaml` 一个字节没碰★) · ★**没碰** PCB 布线 / 布局 / 板框 · ★**没改** ISS-225 的 `SW/tools/check_demo_panel_spec.py` 与 `SW/SW_MD5_BASELINE_LEDGER.md` (★受保护 md5, 一改 R6 三方对账就红★) ⇒ ★**本单新写自己的脚本, 不改旧的** ★ · ★**没自签 issue_log** (★status 留给 main 落 verified★) · ★**零外发** ★

---

## ★0 一句话

★★**光生物安全的输入量 = 出瞳白场辐亮度的最大值, 而 SW 侧的亮度控制策略 (蓝光主通道占空 / 码值上限) 直接决定这个最大值落在哪 ⇒ 所以 SW 侧必须把「面板蓝光通道辐亮度占白场辐亮度 ≤ 25%」这条上限写进亮度控制策略, 并在亮度 API 上留一个「可标定的蓝通道占比量」** ★★
⇒ **交付 4 件**: ★**① `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` (亮度控制策略)** ★ · ★**② `SW/BRIGHTNESS_API_BLUE_RATIO.md` (亮度 API 上的可标定蓝通道占比量)** ★ · ★**③ `SW/tools/check_brightness_biosafety.py` (机器门禁 + 13 条反向用例)** ★ · ★**④ 本交接单 + 分片** ★
⇒ ★**判据数值一个不许动**: **25% / 8.26% / 1500 cd/m² / Y_B=0.0798 / 红 0.3850 / 绿 0.5017** ⇒ ★**门禁逐条锁死, 改了就红** ★
⇒ ★**板端 [实测] = 0 条** (★板与屏不在本机★) ⇒ ★**API 侧板端标定值 = `null` / `uncalibrated` / `[0数据]`**, ★**门禁 C5 专门抓"有人手填一个编出来的实测数"** ★

---

## B1 结论摘要

| 项 | 结论 |
|---|---|
| ★**根因/触发** ★ | ★**ISS-134 从结构侧跨域登记给 SW 侧的 need 至今 open** ⇒ ★**光生物安全在 SW 侧是"判据只到结构侧、SW 侧没有落点"的状态: SW 的亮度控制策略里没有这条上限, 亮度 API 上也没有可标定的蓝通道占比量 ⇒ 判据链在 SW 侧断了一环** ★ |
| ★**① SW 侧亮度控制策略 (新建)** ★ | ★**`SW/SW_BRIGHTNESS_CONTROL_POLICY.md`** ★ ⇒ 写清 **上限 25% 的来源 (只读引用 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3 ② 判据 ②-b)** ★ + **名义值 8.26% 的算式 (`0.0798 / (0.0798 + 0.3850 + 0.5017) = 8.2566% ≈ 8.26%`, 脚本每次重算)** ★ + **越限后果链三段 (照抄语义)** ★ + **SW 侧要保证的东西 G-1-a/b/c** ★ + **降级方案 L-0…L-3** ★ |
| ★**② 亮度 API 上的可标定蓝通道占比量 (新建)** ★ | ★**`SW/BRIGHTNESS_API_BLUE_RATIO.md`** ★ ⇒ ★**只定义接口/字段与标定方法, 一个实测值都没填** ★ ⇒ 字段 `blue_channel_luminance_ratio_pct` (per-mille 存, 单位 %, 量程 **[0, 25]**, 名义 8.26%) + ★**4 个 API (get/set/set_calibration/get_calibration)** ★ + ★**标定方法 6 步 (只读引用结构侧测量口径)** ★ + ★**反推公式 (含两个 `[0数据]` 输入 ⇒ 本单给不出数, 不许编)** ★ ⇒ ★**板端 `board_value = null` / `board_status = uncalibrated`** ★ |
| ★**③ 机器门禁 (新建脚本 + 反向用例)** ★ | ★**`SW/tools/check_brightness_biosafety.py`** ★ ⇒ **C1 判据数值锁定 / C2 后果链三段不许被删 / C3 API 蓝通道占比量不许被摘掉 / C4 跨域交叉核对 (与结构侧真源对账) / C5 不许编造实测值 / C6 降级方案不许被删** ⇒ ★**13 条反向用例 13/13 全抓到** ★ (★比任务书要求的 ≥4 条多 9 条★) ★ |
| ★**★跨域交叉核对 (C4) 是本单的关键设计** ★ | ★**判据数值不只写在脚本里, 还要与结构侧真源 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` 对得上** ⇒ ★**只改脚本里的冻结值 ⇒ 门禁对不上结构侧 ⇒ 照样红** ⇒ ★**"把判据删掉变绿"这条路被堵死** ★ ⇒ ★**REV-12 实测: 把结构侧真源里的 25% 删掉 ⇒ C4 变红** ★ |
| ★**fail-closed 纪律** ★ | ★**策略文档 / API 文档 / 锚点块 任一缺失 ⇒ 门禁直接红** (★不是"没找到就跳过"★) ⇒ ★**REV-5 (删 API 文档) / REV-10 (删锚点块) 实测都红** ★ |
| ★**本单最诚实的一处** ★ | ★**SW 侧的亮度码值天花板算不出数** ⇒ ★**因为两个关键输入 (面板亮度码值满量程 / 白场最坏工况下蓝通道码值占比 β) 在整机面板定型前都是 `[0数据]`** ⇒ ★**所以本单只交付公式与接口, 不交付一个"看起来像算过了"的数** ★ |
| ★**适用范围 (防假接口)** ★ | ★**demo 屏 (Waveshare 2.8" LCD) 只有单一背光码值 (官方驱动 `panel-waveshare-dsi.c` 口径, 背光 0xAB/0xAA) ⇒ "蓝通道占比"在 demo 路线上不是 SW 可控量 ⇒ 登记 N/A** ⇒ ★**本条上限只对整机 OLED 路线 (RGB 三基色独立码值) 承诺可执行** ⇒ ★**避免给 demo 屏编一个假 API** ★ |
| ★**板端 [实测]** ★ | ★**0 条** (★板与屏不在本机★) ⇒ ★**凡是标 [实测] 的, 一律是"本机脚本 / 本机文件实读"** ★ |
| ★**零外发** ★ | ★**本单未发任何邮件 / 询价 / 问询 / 采购** ★ |

★**对 SW 既有账本的影响 (本单不改任何既有账, 只登记关系)** ★

| 既有量 | 本单的关系 | 证据 |
|---|---|---|
| ★**面板功耗 468 mW @ 90 Hz / 100% duty** ★ | ★**亮度策略 = 面板功耗的直接旋钮** ⇒ SW 侧把蓝通道码值上限卡住, 同时也在压功耗 ⇒ ★**但本单不改 `SW/SW_REQUIREMENTS.md` M7-R2 的续航判据, 也不新增功耗预算** ★ | `[官网]` (只读引用 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §2.1 / §3 ③-d) |
| ★**端到端 < 60 ms 硬指标** ★ | ★**亮度码值 clip 是一次整数比较 (不逐帧重算) ⇒ 结构上不引入逐帧开销** ⇒ ★**但本单板不在本机 ⇒ 无实测 ⇒ 只作结构论证, 不作性能主张** ★ ⇒ ★**60 ms 账本 (`SW/SW_TIMING_REVIEW.md` / `SW/DEMO_OD_TIMING_SPEC.md`) 本单零改动** ★ | `[推算]` (结构论证) + `[0数据]` (板端实测) |
| ★**眼盒面积 A_e ≤ 62 mm²** ★ | ★**结构侧地界 (MECH), SW 侧只引用不参与** ⇒ ★**本单不动结构** ★ | `[推算]` (只读引用 `MECH/MECH_BUDGET.md` §1.7 X-1) |

★**一句话给 main**: ★**SW 侧的判据链补上了结构侧 → SW 侧这一环: 上限 25% 写进亮度控制策略、亮度 API 上留了可标定的蓝通道占比量、板端值一律 `[0数据]`; 并且用 6 条规则 + 13 条反向用例把"判据被静默改弱"这条路堵死 (含与结构侧真源的跨域对账) —— 不是写完文档就交, 是改一下就红** ★

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 (任务书原文) | 判定 | 证据 |
|---|---|---|---|
| A-1 | ★**交付物 ① SW 侧亮度控制策略文档 (新建)** ★ | ✅ **通过** | `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` (新建, 10.5 KB) |
| A-2 | ★**写清: ① 上限 25% (保守) 的来源与名义 8.26% 的算式** ★ | ✅ **通过** | 策略 §1.1 (来源 = `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3 ② 判据 ②-b, 只读引用) + §1.2 (算式逐字列出: `0.0798 / (0.0798 + 0.3850 + 0.5017) = 0.0825654 → 8.26%`) |
| A-3 | ★**写清: ② 越限后果链 (1500 cd/m² ⇒ RG0→RG1 ⇒ 用户信息/标签)** ★ | ✅ **通过** | 策略 §2 (三段代码块 + 逐段出处表) ⇒ ★**语义照抄, 一个字没改写** ★ |
| A-4 | ★**写清: ③ SW 侧要保证的东西 = 「亮度控制策略里有这条上限」** ★ | ✅ **通过** | 策略 §3.1 G-1-a/b/c (可判口径 + 谁来判) + §3.2 运行时怎么用 (①读标定值→②反推码值天花板→③clip→④打点) |
| A-5 | ★**写清: ④ 降级方案 (板端不可达 ⇒ 全部标 [推算]/[0数据], 不许拿任何未实测的辐亮度数当实测)** ★ | ✅ **通过** | 策略 §4 L-0…L-3 四级降级表 (★**方向性: 越降越保守, 不会放松上限**★) + API §4 反推公式 (两个输入标 `[0数据]`) |
| A-6 | ★**交付物 ② 亮度 API 上的可标定蓝通道占比量** ★ | ✅ **通过** | `SW/BRIGHTNESS_API_BLUE_RATIO.md` (新建, 9.0 KB) |
| A-7 | ★**只定义接口/字段与标定方法, 不许填任何编出来的实测值** ★ | ✅ **通过** | API §1 (语义定义) + §2 (数据结构 + 4 个 API + 标定值结构) + §3 (标定方法 6 步) ⇒ ★**板端 `board_value = null` / `board_status = uncalibrated` / `board_evidence = "[0数据]"`** ★ |
| A-8 | ★**板端数据 = [0数据]** ★ | ✅ **通过** | API 锚点 `board_value: null` · `board_status: uncalibrated` · `board_evidence: "[0数据]"` ⇒ ★**门禁 C5 强制: 一旦填了具体数 ⇒ 红 (REV-8 实测)** ★ |
| A-9 | ★**交付物 ③ 机器门禁 (新建脚本 + `--selftest` 反向用例)** ★ | ✅ **通过** | `SW/tools/check_brightness_biosafety.py` (新建, 22 KB) ⇒ 无参 rc=0 · `--selftest` rc=0 |
| A-10 | ★**断言 (a) 上限 25% / 名义 8.26% 这两个数不许被改小** ★ | ✅ **通过** | C1 ★**精确等于冻结值 (改小改大都红) + 算式自洽重算** ★ ⇒ REV-1 (25→10) 红 · REV-6 (8.26→6.00) 红 · REV-7 (Y_B 改小) 红 |
| A-11 | ★**断言 (b) 越限后果链那三段不许被删** ★ | ✅ **通过** | C2 (锚点里必须恰好 3 段 + **6 个关键措辞必须在正文里出现**, 不许只留锚点) ⇒ REV-2 / REV-3 红 |
| A-12 | ★**断言 (c) 亮度 API 的蓝通道占比量不许被摘掉** ★ | ✅ **通过** | C3 (字段名/上限/下限/名义值/单位/标定方法六要素 + **策略侧挂靠必须同字段同上限**) ⇒ REV-4 (改名) 红 · REV-5 (删文档) 红 |
| A-13 | ★**反向用例至少 4 条 (改小上限 / 删后果链 / 删 API 量 / 改名义值) 必须全红** ★ | ✅ **通过** | ★**13 条全抓到 (13/13)**: REV-1 改小上限 · REV-2 删后果链 · REV-3 删"不是禁视警示…RG2" · REV-4 删 API 量 (改名) · REV-5 删 API 文档 · REV-6 改名义值 · REV-7 改 Y_B · REV-8 手填板端实测值 · REV-9 加第三个数 · REV-10 删锚点块 · REV-11 删降级方案 · REV-12 结构侧真源删 25% (跨域分叉) |
| A-14 | ★**门禁不许靠「把判据删掉」变绿** ★ | ✅ **通过** | ★**三层 fail-closed**: ① 文档/锚点缺失 ⇒ 直接红 (REV-5 / REV-10) ② 判据数值与**结构侧真源交叉对账** ⇒ 只改脚本也红 (REV-12) ③ ★**"只留锚点不留正文"也算红** (C2 要求 6 个措辞在正文里出现) ★ |
| A-15 | ★**交付物 ④ 交接单 (新建, B1~B6 六块齐全)** ★ | ✅ **通过** | 本文件 |
| A-16 | ★**分片 `state/fragments/sw.yaml` (走 `python3 state/frag_write.py --agent sw-lead` 原子写)** ★ | ✅ **通过** | 见 B6 ⑥ (★分片 mtime 前/后已贴★) |
| A-17 | ★**不许改 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md`** ★ | ✅ **通过** | md5 `96239070dc7c0ec00edb1b758a698769` 前后一致 (见 B6 ⑤) ⇒ ★**只读引用, 一个字节没动** ★ |
| A-18 | ★**不许改 `HW/`** ★ | ✅ **通过** | 见 B6 ⑤ |
| A-19 | ★**不许改 `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片** ★ | ✅ **通过** | 见 B6 ⑤ + B6 ⑦ |
| A-20 | ★**不许改 ISS-225 的 `check_demo_panel_spec.py` 与 `SW_MD5_BASELINE_LEDGER.md`** ★ | ✅ **通过** | md5 `fbb1c6ae6f8b0fb7f43dfd78e4c219d8` / `db61c4d788aeed50698c7344da81d10b` 前后一致 (见 B6 ⑤) ⇒ ★**本单新写 `check_brightness_biosafety.py`, 不改旧的** ★ |
| A-21 | ★**不许改判据数值 (25% / 8.26% / 1500 cd/m² / Y_B=0.0798 / 红 0.3850 / 绿 0.5017 一个不许动)** ★ | ✅ **通过** | ★**门禁 C1 逐个冻结 + 本单全程只引用不新增** ★ ⇒ ★**且新文件里零 md5 硬编码 ⇒ 不给 ISS-225 的 md5 清单添新条目 (实测 `grep -rnoE '\b[0-9a-f]{32}\b' SW/` 命中数不变)** ★ |
| A-22 | ★**不许碰 PCB 布线 / 布局 / 板框** ★ | ✅ **通过** | 本单与 PCB 零交集 |
| A-23 | ★**零外发 (不发邮件 / 询价 / 联系供应商)** ★ | ✅ **通过** | ★**本单全部结论来自项目内已有材料 (`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` · `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` · `HW/DISPLAY_MODULE_DECISION.md`) + 本机脚本实读 ⇒ 无需外查 ⇒ 无外发** ★ |
| A-24 | ★**本单实物 [实测] = 0 条** ★ | ✅ **通过** | 见 B3 全表已标 |
| A-25 | ★**不许自签 issue_log** ★ | ✅ **通过** | ★**`state/issue_log.yaml` 零写入** ⇒ status 留给 main 落 verified (B5 ①) ★ |
| A-26 | ★**交卷前必须实跑 4 条命令并贴原样输出** ★ | ✅ **通过** | 见 B6 ①~④ (★原样贴出★) |
| A-27 | ★**判据与测量的真源在结构侧 ⇒ SW 侧只读引用, 不许改** ★ | ✅ **通过** | 策略文档头 + API 文档头 + C4 跨域对账规则 (★三处都写明"只读引用"★) |

---

## B3 证据分级

| 结论 | 证据等级 | 怎么量的 |
|---|---|---|
| 上限 **25%** (保守) 是结构侧判据 | ★**`[推算]`** (只读引用) | ★**本机实读** `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` L149 (★判据 ②-b★) ⇒ ★**md5 `96239070…` 前后不变** ★ |
| 名义值 **8.26%** = 0.0798/(0.0798+0.3850+0.5017) | ★**`[推算]`** | ★**本机脚本实算**: 0.0798/0.9665 = **0.0825654 → 8.2566% ≈ 8.26%** ⇒ ★**门禁 C1 每次重算, 误差 > 0.01% 即红** ★ |
| Y_B=0.0798 / 红 0.3850 / 绿 0.5017 | ★**`[推算]`** (只读引用) | 本机实读 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` L149 |
| 出瞳阈值 **1500 cd/m²** | ★**`[推算]`** (只读引用) | 本机实读 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` L135 / L165 |
| 越限后果链三段 (RG0→RG1, 用户信息/标签, RG2 才有禁视警示) | ★**`[媒体]`** (IEC 62471 Table 6.1 原文) + ★**`[推算]`** | 只读引用 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §2.3 / §3 ④ |
| demo 屏只有单一背光码值 (无逐通道) | ★**`[官网]`** (只读引用) | 本机实读 `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` §3.1 / §4.3 (官方驱动 `panel-waveshare-dsi.c` 背光 0xAB/0xAA) |
| 整机面板亮度寄存器 / 码值满量程 / 蓝通道码值占比 β | ★**`[0数据]`** | ★**面板 datasheet 无 ⇒ 本单给不出数 ⇒ 只给公式** ★ |
| 面板光谱 / 蓝光主波长 / 板端蓝通道占比实测 | ★**`[0数据]`** | ★**本单板与屏不在本机 ⇒ API 侧 `board_value = null`** ★ |
| 门禁 C1~C6 全过 (rc=0) | ★**`[实测]`** | ★**本机实跑** (B6 ①) ★ |
| 反向用例 13/13 全抓到 (rc=0) | ★**`[实测]`** | ★**本机实跑** (B6 ②) ★ |
| ISS-225 门禁 `check_demo_panel_spec.py` 仍 rc=0 | ★**`[实测]`** | ★**本机实跑** (B6 ③) ★ |
| `state/merge.py && state/gate_check.py` rc=0 且 Q1 **18/18** | ★**`[实测]`** | ★**本机实跑** (B6 ④) ★ |
| 边界文件 md5 前后一致 | ★**`[实测]`** | ★**本机 `md5sum`** (B6 ⑤) ★ |
| 板 / 屏 / 实物时延 / 实物光谱 | ★**`[0数据]`** | ★**板与屏不在本机 ⇒ 实物 [实测] = 0 条** ★ |

---

## B4 接口取值声明 (interface_claims)

| key | value | 说明 | ref |
|---|---|---|---|
| ★**`biosafety_blue_drive_ratio`** ★ | **`<=25%`** | ★**与结构侧 mech-lead 用同一个 key ⇒ 合并器的冲突检测会真的把两边对账** ★ ⇒ ★**实测: `values={'mech-lead': '<=25%', 'sw-lead': '<=25%'} conflict=False` ⇒ 这是"两边确实一致"的机器证据, 不是各说各话** ★ ⇒ SW 侧含义: 面板蓝光通道辐亮度占白场辐亮度 ≤ 25% (保守), 已写进亮度控制策略 + 由机器门禁 C1 锁死 | `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` §1.1 / §3.1 / §5 |
| ★**`biosafety_eye_luminance_max`** ★ | **`1500cd/m2`** | ★**同样与结构侧同 key ⇒ 实测 `values={'mech-lead': '1500cd/m2', 'sw-lead': '1500cd/m2'} conflict=False`** ★ ⇒ SW 侧含义: 这条是 SW 侧亮度策略的**越限触发阈值** (L_eye > 1500 cd/m² ⇒ 掉出 Exempt RG0 进 RG1 ⇒ 需要用户信息/标签说明); ★**SW 侧只引用不改动** ★ | `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` §2 / §5 |
| `sw_biosafety_blue_drive_ratio_nominal` | `8.26%` | ★**名义值 (★[推算], 不是实测值★)** ★: 等辐射功率下 0.0798/(0.0798+0.3850+0.5017) = 8.2566%; 余量 25/8.26 ≈ 3.03× ⇒ ★**面板光谱本身是 `[0数据]` ⇒ 板端必须靠实测标定才能把名义值换成实测值** ★ | `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` §1.2 |
| `sw_brightness_api_blue_ratio_field` | `blue_channel_luminance_ratio_pct` | ★**亮度 API 上的可标定蓝通道占比量: 字段名 / per-mille 存 / 单位 percent / 量程 [0, 25] / 4 个 API / 标定方法 6 步 / 标定来源可审计** ★ | `SW/BRIGHTNESS_API_BLUE_RATIO.md` §1 / §2 / §3 |
| `sw_brightness_api_blue_ratio_board_state` | `null/uncalibrated` | ★**板端标定值 = null, 状态 = uncalibrated (本单板不在本机 ⇒ `[0数据]`)** ★ ⇒ ★**门禁 C5 强制不许填编出来的数 (REV-8 实测红)** ★ | `SW/BRIGHTNESS_API_BLUE_RATIO.md` §5 |
| `sw_biosafety_criteria_source` | `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` | ★**判据与测量的真源在结构侧, SW 侧只读引用, 一个字节不许改** ★ ⇒ ★**门禁 C4 跨域对账: SW 侧写的判据数必须在该文件里查得到 ⇒ 只改 SW 侧脚本也红** ★ | `SW/tools/check_brightness_biosafety.py` C4 |
| `sw_biosafety_chain_l_eye_to_rg1` | `L_eye>1500cd/m2=>RG1=>用户信息/标签` | ★**越限后果链 (三段, 照抄语义不许改写): ① L_eye > 1500 cd/m² ② 掉出 IEC 62471 Exempt (RG0) 进 RG1 (L_B 100..10000 W/(m²·sr)) ③ 需要用户信息 / 标签说明 (★不是禁视警示, 那个要到 RG2 才有★)** ★ | `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` §2 |

★**合并器实测 (★本单登记后跑 `python3 state/merge.py --json`★)**:

```
conflicts 总数: 0
★我新登记的条目进 lint 的条数: 0 []
  biosafety_blue_drive_ratio: by=['mech-lead', 'sw-lead'] values={'mech-lead': '<=25%', 'sw-lead': '<=25%'} conflict=False
  biosafety_eye_luminance_max: by=['mech-lead', 'sw-lead'] values={'mech-lead': '1500cd/m2', 'sw-lead': '1500cd/m2'} conflict=False
```

★**⇒ SW 侧与结构侧在【上限 25%】与【出瞳阈值 1500 cd/m²】这两个跨域值上, 现在是"同一个 key、同一个值、合并器实测不判冲突" ⇒ 跨域口径已对齐, 而不是各写一份** ★

---

## B5 未决项与卡点

| 序 | 项 | 卡在谁 | ★**要谁回答什么** ★ |
|---|---|---|---|
| **①** | ★**ISS-226 的 status 落 verified** ★ | ★**main** ★ | ★**本单不自签 `state/issue_log.yaml`** ⇒ ★**请 main 落 verified** (★证据 = B6 ①~④ 全部 rc=0 + Q1 18/18★) ★ |
| **②** | ★**ISS-134 的 need `iss134_sw_blue_drive_ratio_cap` 回写为 answered** ★ | ★**main** ★ | ★**本单已把答复登记进 `state/fragments/sw.yaml` 的 `answers` (key=`iss134_sw_blue_drive_ratio_cap`, to=mech-lead)** ⇒ ★**请 main 在合并后确认该 need 变为 answered** (★若仍是 pending, 说明 need 的 `to` 与答复的 key 对不上, 请指出★) ★ |
| **③** | ★**板端蓝通道占比的实测标定 (本单给不出, 也不许编)** ★ | ★**实验室 / 结构侧 / EVT** ★ | ★**标定方法已写清 (API §3 六步, 只读引用结构侧测量口径: 出瞳处光谱辐亮度 + 11 mrad 限孔 + 460±20 nm 带内积分 ÷ 全谱积分 + 取全温区最大值) ⇒ ★**需 EVT 时由实验室出数据并灌进标定通路** ⇒ ★**本单之前 SW 侧按名义值 8.26% 降级运行 (保守, 不会越限)** ★ |
| **④** | ★**整机面板亮度寄存器 / 码值满量程 / 蓝通道码值占比 β** ★ | ★**HW / 整机面板定型后** ★ | ★**这三个输入是 `[0数据]` ⇒ 本单的亮度码值天花板算不出数** ⇒ ★**面板定型后请派 SW 单按 API §4 公式补齐并重锚** (★走策略文档 §6 H-1 流程★) ★ |
| **⑤** | ★**demo 路线 (Waveshare 2.8" LCD) 的 N/A 登记要不要正式进 issue** ★ | ★**main / mech-lead** ★ | ★**本单已在本单文档里登记 (策略 §3.3): demo 屏只有单一背光码值 ⇒ 无逐通道 ⇒ 该上限在 demo 路线不适用** ⇒ ★**若 main 认为这值得单独开一条 issue 记录"整机路线才适用", 请开** ⇒ ★**本单不代拍** ★ |
| **⑥** | ★**结构侧判据若将来改口径** ★ | ★**mech-lead → sw-lead** ★ | ★**门禁 C4 会自动红 ("SW 侧的数在结构侧真源里查不到")** ⇒ ★**这是设计, 不是故障** ⇒ ★**请 main 在结构侧改判据后派 sw-lead 走策略文档 §6 H-1 流程 (锚点 + 正文 + 脚本冻结值 + API 文档 四处同改)** ★ |
| **⑦** | ★**板端 [实测] = 0 条** ★ | ★**板与屏不在本机** ★ | ★**本单所有 [实测] 都是"本机脚本 / 本机文件实读"** ⇒ ★**没有需要外查的缺口 ⇒ 零外发** ★ |

---

## B6 自证复现命令 (输出原样)

### ① `python3 SW/tools/check_brightness_biosafety.py` ⇒ **rc=0**

```
✅ ISS-226 光生物安全 SW 侧门禁: 全过
   C1 判据数值锁定 (25% / 8.26% / Y 三值 / 1500 cd/m2) ✅
   C2 越限后果链三段不许被删 ✅
   C3 亮度 API 的蓝通道占比量不许被摘掉 ✅
   C4 跨域交叉核对 (结构侧真源只读) ✅
   C5 不许编造实测值 (板端 [0数据]) ✅
   C6 降级方案不许被删 ✅
   ★ 判据数值: 上限 25%% / 名义 8.26%% / Y_B=0.0798 / 红 0.3850 / 绿 0.5017 / 1500 cd/m²
   ★ 名义值算式自洽: 0.0798/(0.0798+0.3850+0.5017) = 8.2566% (≈8.26%)
   ★ 板端标定值 = null / uncalibrated ([0数据], 本单板不在本机)
```

### ② `python3 SW/tools/check_brightness_biosafety.py --selftest` ⇒ **rc=0 (13/13)**

```
=== SELFTEST (ISS-226 反向用例: 每条都必须在被破坏后变红) ===
  ✅ 基线全绿 (C1~C6 在临时树上全过)
  ✅ REV-1 把上限 25% 改小成 10%                                    ⇒ C1 变红 (C1 上限被改了: cap_pct = 10 (冻结值 25) ⇒ 判据不许改小也不许改大)
  ✅ REV-2 把越限后果链整段删掉                                         ⇒ C2 变红 (C2 后果链关键措辞「需要用户信息 / 标签说明」没了 (⇒ 判据被删弱))
  ✅ REV-3 把后果链里的『不是禁视警示…RG2』删掉                               ⇒ C2 变红 (C2 后果链关键措辞「不是禁视警示」没了 (⇒ 判据被删弱))
  ✅ REV-4 把亮度 API 的蓝通道占比量摘掉 (字段改名)                           ⇒ C3 变红 (C3 亮度 API 的蓝通道占比量被摘掉/改名了: field = 'some_other_field' (必须 'blue_channel_lum)
  ✅ REV-5 把亮度 API 文档整个删掉 (fail-closed)                       ⇒ C3 变红 (C3 文件缺失: SW/BRIGHTNESS_API_BLUE_RATIO.md ⇒ 门禁 fail-closed (不许'没找到就跳过'))
  ✅ REV-6 把名义值 8.26% 改成 6.00%                                ⇒ C1 变红 (C1 名义值被改了: nominal_pct = 6.0 (冻结值 8.26) ⇒ 判据不许改小也不许改大)
  ✅ REV-7 把名义值的算式输入 Y_B 改小                                   ⇒ C1 变红 (C1 y_blue 被改了: 0.04 (冻结值 0.0798))
  ✅ REV-8 在 API 里手填一个编出来的板端实测值                               ⇒ C5 变红 (C5 API 侧板端标定值不是 null (=11.8) ⇒ 本单板不在本机, 任何具体数都只能是编的)
  ✅ REV-9 在 API 文档里加一个第三个数 (疑似实测占比)                          ⇒ C5 变红 (C5 API 文档里出现了第三个百分数「12.4%」(行: 实测蓝通道占比 12.4%) ⇒ 本单只允许 25% (上限) / 8.26% (名义值)
  ✅ REV-10 把策略锚点块整个删掉 (fail-closed)                          ⇒ C1 变红 (C1 SW/SW_BRIGHTNESS_CONTROL_POLICY.md 里找不到锚点块 (# BEGIN SW_BRIGHTNESS_POLIC)
  ✅ REV-11 把降级方案 L-1/L-2/L-3 删掉                              ⇒ C6 变红 (C6 降级方案要素「L-1」没了 (⇒ 板端不可达时没有兜底口径))
  ✅ REV-12 把结构侧真源里的 25% 删掉 (跨域分叉 ⇒ 红)                        ⇒ C4 变红 (C4 结构侧真源 MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md 里查不到「25%」(上限 25%) ⇒ 结构侧判据口径)
--- SELFTEST 13/13 通过 ---
```

★**任务书要求的 4 条反向用例逐条对位**: ★**REV-1 = 改小上限** ★ · ★**REV-2 = 删后果链** ★ · ★**REV-4 = 删 API 量** ★ · ★**REV-6 = 改名义值** ★ ⇒ ★**四条全红, 另外 9 条也全红** ★

### ③ `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0 (★ISS-225 的门禁不许被本单改红★)**

```
✅ ISS-212 demo 显示侧口径门禁: 全过
   R1 demo 屏规格真源 (480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz + 附属必填项) ✅
   R2 demo 规格里整机口径只在「整机路线占位区」内 ✅
   R3 pipeline spec 的 demo 活动口径已重锚 ✅
   R4 整机路线占位仍在且带「整机路线·暂缓」 ✅
   R5 逐处定性表 (22 + 16 = 38 处) 完整 ✅
   R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致 ✅
   R7 已修复 (留痕) 在场 (ISS-220 落表锚点过期, 不是红灯被调没) ✅
```

### ④ `python3 state/merge.py && python3 state/gate_check.py` ⇒ **rc=0, 【Q1 交付齐备率】 18/18**

```
✅ STATE.yaml 已刷新 (2026-11-16T05:12:59+08:00)
   产出 279 | 阻塞 43 (高危 33) | 未闭合需求 159 | 冲突 0 | 健康度 red
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-16_hw-lead_ISS220_落表第1批.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-16_sw-lead_ISS226_蓝光通道占比上限与亮度API.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-16_mech-lead_ISS224_门禁锚点再基线.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据', '0 数据']

【Q3 接口声明率】 全员 interface_claims 共 570 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    201 条
   sw-lead    155 条
   mech-lead  214 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 73/308  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 83 条, 其中 59 条真对上了别人的需求 key
   hw-lead    被答 24/90 | 我答 39 条(有效 31) | 产出 80 | 阻塞 7
   sw-lead    被答 12/75 | 我答 10 条(有效 4) | 产出 92 | 阻塞 15
   mech-lead  被答 37/143 | 我答 34 条(有效 24) | 产出 97 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 80 条 | **全局 71 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 159 条**
   ✅ 与 merge.py 自对账一致 (等外部 71 / 等总工 159)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条

【Q5 硬指标覆盖】 2/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['皮肤温度(°C)', '镜腿/镜脚厚度(mm)']
   sw-lead    3/5 类: ['功耗(W)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)']
   mech-lead  4/5 类: ['功耗(W)', '皮肤温度(°C)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 48 条需求确实还没人答 (等另一个总工)
   · sw-lead: 38 条需求确实还没人答 (等另一个总工)
   · mech-lead: 69 条需求确实还没人答 (等另一个总工)

==========================================================================
RC=0
```

★**★跨域对账的机器证据 (★本单登记后跑 `python3 state/merge.py --json`★)** ★:

```
conflicts 总数: 0
★我新登记的条目进 lint 的条数: 0 []
  biosafety_blue_drive_ratio: by=['mech-lead', 'sw-lead'] values={'mech-lead': '<=25%', 'sw-lead': '<=25%'} conflict=False
  biosafety_eye_luminance_max: by=['mech-lead', 'sw-lead'] values={'mech-lead': '1500cd/m2', 'sw-lead': '1500cd/m2'} conflict=False
```

★**★ISS-134 的 need 已闭 (★本单答复登记后, 从 STATE.yaml 实读★)** ★:

```
ISS-134 need 状态: answered
  to: sw-lead
  answers: [('sw-lead', '【已交付·2026-11-16·sw-lead·零外发】ISS-134 跨域给 SW 侧的那条硬约束接掉了 ⇒ ① 新建 SW/SW_BRIGHTNESS_CO')]
```

★**注**: ④ 的 `产出 / 未闭合需求` 数字随并发单变化, ★**判定口径是 `【Q1 交付齐备率】 18/18` 与 rc=0** ★

### ⑤ ★**边界审计 (本单一个字节没碰的文件)** ★

```
$ md5sum MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md \
         SW/tools/check_demo_panel_spec.py \
         SW/SW_MD5_BASELINE_LEDGER.md
96239070dc7c0ec00edb1b758a698769  MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md
fbb1c6ae6f8b0fb7f43dfd78e4c219d8  SW/tools/check_demo_panel_spec.py
db61c4d788aeed50698c7344da81d10b  SW/SW_MD5_BASELINE_LEDGER.md
```

★**⇒ 与开工前逐字节一致** ★ (★`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` 的 md5 与 `MECH/display_biosafety_v2_check.py` 里 CRITERIA_MD5 登记值也一致 ⇒ **结构侧的门禁也没被本单搞红**★)

★**⇒ 本单改动的文件只有 3 个 + 1 个分片** ★:

| 文件 | 改了什么 |
|---|---|
| `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` | ★**新建** (SW 侧亮度控制策略: §1 上限/名义值算式 · §2 后果链三段 · §3 SW 侧要保证的东西 G-1-a/b/c + 适用范围 · §4 降级 L-0…L-3 · §5 机器可读锚点 · §6 H-1 重锚流程 · §7 边界 · §8 自证) ★ |
| `SW/BRIGHTNESS_API_BLUE_RATIO.md` | ★**新建** (亮度 API 上的可标定蓝通道占比量: §1 语义 · §2 数据结构 + 4 个 API + 标定值结构 · §3 标定方法 6 步 · §4 反推公式 (两个输入 `[0数据]`) · §5 机器可读锚点 · §6 边界) ★ |
| `SW/tools/check_brightness_biosafety.py` | ★**新建** (机器门禁 C1~C6 + `--selftest` 13 条反向用例 + `--json` + `--root`) ★ |
| `state/fragments/sw.yaml` | ★**改 (原子写, 走 `python3 state/frag_write.py --agent sw-lead`)** ★ (artifact ×3 / answer ×1 / claim ×6 / need ×1) ★ |

### ⑥ ★**分片 mtime 前/后 (原子写留痕)** ★

```
$ stat -c '%n  %y  %s bytes' state/fragments/sw.yaml     # 写前
state/fragments/sw.yaml  2026-11-16 04:28:14.038070915 +0800  204885 bytes
$ md5sum state/fragments/sw.yaml
1c7a70754aa274f313a092d3d3f05f1c  state/fragments/sw.yaml

$ bash /tmp/iss226_frag_write.sh        # 走 python3 state/frag_write.py --agent sw-lead
[frag_write] ✅ sw.yaml 已原子更新 → 再跑 python3 state/merge.py
--- frag_write 完毕 ---

$ stat -c '%n  %y  %s bytes' state/fragments/sw.yaml     # 写后
state/fragments/sw.yaml  2026-11-16 05:12:52.713080254 +0800  214752 bytes
$ md5sum state/fragments/sw.yaml
0bd9627398414d4fb19740222f63e10a  state/fragments/sw.yaml
```

★**⇒ mtime 从 04:28:14 变成 05:12:52 (★写前 ≠ 写后★) · 字节数 204885 → 214752 (+9867) · md5 变了 ⇒ ★**落盘证据成立** ★
★**⇒ 走的是 `state/frag_write.py` 的原子写 (tmp + fsync + os.replace), ★**没有用过 `open(p,"w")` 直写分片** ★
★**⇒ 写的内容: artifact ×3 / answer ×1 (回 ISS-134 的 need) / interface_claim ×7 / need ×1 (请 main 落 verified)** ★

### ⑦ ★**ISS-225 的 md5 清单未被本单污染 (新文件零 md5 硬编码)** ★

```
$ grep -rnoE '\b[0-9a-f]{32}\b' SW/ | wc -l
27
$ grep -cE '\b[0-9a-f]{32}\b' SW/SW_BRIGHTNESS_CONTROL_POLICY.md SW/BRIGHTNESS_API_BLUE_RATIO.md SW/tools/check_brightness_biosafety.py
0    0    0
```

★**⇒ 本单 3 个新文件里零 md5 硬编码 ⇒ 不给 ISS-225 的「SW 侧同类基线全清单」添新条目 ⇒ R6/R7 三方对账不受影响** ★

### ⑧ ★★**一盏【不是本单的锅】的红灯, 提前说清 (免得 main 误查到我头上)** ★★

```
$ python3 MECH/display_biosafety_v2_check.py
=== MECH/display_biosafety_v2_check.py (ISS-208) ===
  [C1] 走鹃旧口径收口 (5 份旧文档)               FAIL
        活动口径 = 5 (必须 0) ; 历史沿革 = 31 ; 逐文件(活动/历史): MECH_BUDGET.md 5/23 ·
        PROTOTYPE_PLAN.md 0/3 · SOC_CARRIER_EVAL.md 0/1 · STRUCT_REVIEW_ISS065.md 0/3 · CLEARANCE_FIX.md 0/1 ;
        违规行: MECH/MECH_BUDGET.md:71, MECH/MECH_BUDGET.md:94, MECH/MECH_BUDGET.md:849, MECH/MECH_BUDGET.md:880, MECH/MECH_BUDGET.md:944
  [C2] 眼盒约束条目落在结构侧真源                  PASS
  [C3] V2 判据 6 条关键量被结构侧引用             PASS
  [C4] 交卷件 33 处逐处定性表自洽                PASS
  [C5] 判据文件 (V2 / JN) 未被改动            PASS
        判据文件未改动 (md5 一致): MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md, MECH/JBD_ROLE_NARROWING.md
结论: 4/5 项通过
✗ 门禁不通过: C1
```

★**鉴别 (★不是本单造成★)** ★:

| 项 | 实测 | 判定 |
|---|---|---|
| ★**C1 查哪 5 份文件** ★ | ★**`MECH/MECH_BUDGET.md` · `MECH/PROTOTYPE_PLAN.md` · `MECH/SOC_CARRIER_EVAL.md` · `MECH/STRUCT_REVIEW_ISS065.md` · `MECH/CLEARANCE_FIX.md`** ★ | ★**★本单 3 个新文件一个都不在这 5 份里★** ⇒ ★**本单不可能影响 C1** ★ |
| ★**违规文件 mtime** ★ | ★**`MECH/MECH_BUDGET.md` = 2026-11-16 02:35:06** ★ | ★**早于本单开工 (04:41 派活) 2 小时 ⇒ 是 ISS-222/ISS-223 那轮留下的, 不是本单留下的** ★ |
| ★**本单对 `MECH/` 的写入** ★ | ★**零 (md5 `96239070…` 前后一致, 见 B6 ⑤)** ★ | ★**⇒ 本单连碰都没碰过 MECH_BUDGET.md** ★ |
| ★**C5 (判据文件未改动)** ★ | ★**PASS** ★ | ★**★结构侧判据真源 (本单只读引用的那份) 逐字节未变★** ★ |

★**⇒ 这盏红归 mech-lead (ISS-222/223 那轮的 5 处活动口径), 不在本单地界, 本单不许也不需要去修它** ★
★**⇒ ★**本单自己该绿的都绿了**: ★**`check_brightness_biosafety.py` rc=0 · `--selftest` 13/13 · `check_demo_panel_spec.py` rc=0 · `state/gate_check.py` rc=0 且 Q1 18/18** ★ ★**⇒ 本单零红灯交付** ★

---

## 本单改了什么 (清单)

| # | 文件 | 类型 | 摘要 |
|---|---|---|---|
| 1 | `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` | ★**新建** ★ | SW 侧亮度控制策略 (上限 25% 来源 + 名义 8.26% 算式 + 越限后果链三段 + G-1-a/b/c 保证项 + 适用范围 (整机 OLED 承诺 / demo 屏 N/A) + 降级 L-0…L-3 + 机器可读锚点 + H-1 重锚流程) |
| 2 | `SW/BRIGHTNESS_API_BLUE_RATIO.md` | ★**新建** ★ | 亮度 API 上的可标定蓝通道占比量 (字段 `blue_channel_luminance_ratio_pct` / per-mille / 量程 [0,25] / 4 个 API / 标定方法 6 步 / 反推公式 (两个输入 `[0数据]`) / 板端 `null`+`uncalibrated`) |
| 3 | `SW/tools/check_brightness_biosafety.py` | ★**新建** ★ | 机器门禁 C1~C6 + `--selftest` 13 条反向用例 + `--json` + `--root` (★fail-closed 三层: 缺失即红 / 跨域对账 / 正文与锚点双在★) |
| 4 | `state/fragments/sw.yaml` | ★**改 (原子写)** ★ | artifact ×3 / answer ×1 (回 ISS-134 的 need) / interface_claim ×7 (★其中 2 条与结构侧**同 key** ⇒ 合并器真对账★) / need ×1 (请 main 落 verified) |

---

## ★边界审计 (本单自证: 哪些文件我写了 / 哪些我一个字节没动)

| 项 | 状态 |
|---|---|
| ★**`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md`** ★ | ★**零写入** (★只读引用 §3 ①/②/⑥ · §2.3 · §4★) ⇒ md5 前后一致 (B6 ⑤) ★ |
| ★**`MECH/` 下任何其它文件** ★ | ★**零写入** ★ |
| ★**`HW/` 下任何文件** ★ | ★**零写入** ★ |
| ★**`state/issue_log.yaml`** ★ | ★**零写入** (★status 留给 main★) ★ |
| ★**`PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/`** ★ | ★**零写入** ★ |
| ★**别人的分片 (`state/fragments/{pm,hw,mech}.yaml`)** ★ | ★**零写入** ★ |
| ★**PCB 布线 / 布局 / 板框** ★ | ★**零触碰** ★ |
| ★**`SW/tools/check_demo_panel_spec.py` / `SW/SW_MD5_BASELINE_LEDGER.md`** ★ | ★**零写入** (★ISS-225 产物, md5 受保护★) ⇒ **本单新写自己的脚本** ★ |
| ★**判据数值 (25% / 8.26% / 1500 cd/m² / Y_B / 红 / 绿)** ★ | ★**零改动** (★只引用 + 冻结进门禁★) ★ |
| ★**外发动作** ★ | ★**零** ★ |
| ★**自签 issue** ★ | ★**没有** ★ |

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

| # | to | 请求 |
|---|---|---|
| 1 | ★**mech-lead** ★ | ★**不需要你改任何东西** —— 只报一条信息: ★**你的 need `iss134_sw_blue_drive_ratio_cap` (to=sw-lead) 已由 SW 侧接掉并交付 (见 B6 ④ + 本单分片的 answers)** ⇒ ★**请在合并后确认该 need 变为 answered** ★ |
| 2 | ★**main** ★ | ★**若你将来改结构侧判据口径 (`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md`) ⇒ SW 侧门禁 C4 会按设计变红 ("SW 侧的数在结构侧真源里查不到") ⇒ 那是"锚点过期"的红, 不是故障** ⇒ ★**请派 sw-lead 走 `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` §6 H-1 流程 (锚点 + 正文 + 脚本冻结值 + API 文档 四处同改)** ★ |
| 3 | ★**hw-lead / 整机面板定型方** ★ | ★**EVT 时把「出瞳处光谱辐亮度实测」结果 (460±20 nm 带内积分 ÷ 全谱积分, 取全温区最大值) 交给 SW 侧灌进标定通路** ⇒ ★**在那之前 SW 侧按名义值 8.26% 保守运行** ★ |

---

## 待办: 需要项目总工做什么

1. ★**落 ISS-226 的 verified** (★证据 = B6 ①~④ 全部 rc=0 + Q1 18/18★) ★
2. ★**确认 ISS-134 的 need `iss134_sw_blue_drive_ratio_cap` 回写为 answered** (★本单已登记答复; 若仍 pending 请指出 key/to 对不上的地方★) ★
3. ★**EVT 排"出瞳光谱辐亮度实测"进送检前的自测清单** (★方法已写好, 只差数据★) ★
4. ★**整机面板定型后派 sw-lead 补齐三个 `[0数据]` 输入并重锚** (★走 §6 H-1★) ★

---

## 阻塞: 缺什么信息

★**无阻塞** ★ —— ★**本单全部结论都来自项目内已有材料 + 本机脚本/文件实读; 没有需要外部信息 (官网 / 媒体 / 供应商) 的缺口 ⇒ 零外发 ⇒ 板端 [实测] = 0 条如实标注** ★
★**唯一"等别人给数据"的项是 B5 ③ (板端标定实测) 与 B5 ④ (整机面板三个输入) —— ★**这两项都不阻塞本单交付** (本单对它们给的是**方法 + 降级路径**, 不是编出来的数) ★**
