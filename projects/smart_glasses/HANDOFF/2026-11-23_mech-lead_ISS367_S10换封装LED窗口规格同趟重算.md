# ISS-367 · mech-lead · 「板只改一次」S10 换封装后 LED 窗口规格同趟重算

> ★**一句话** ★: ★**「板只改一次」那一趟的 S10 把 `D_LED_G` 换成官方 0805 land ⇒ `MECH/check_board_frame_coords.py` 的
> `led_space()` 算出来的【两条整高自由带】/【封装原点窗口】/【可落位块数】/【净距敏感度 sweep】**四组全变**
> ⇒ ★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块** 与 ★**`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格**
> 这两处**必须同一次改写** ⇒ 本单已按实算逐字改完, 并用一条新机器闸钉住 (★`MECH/check_onepass_s10_led_spec_sync.py`·
> L0~L6 全绿 · `--selftest` 7/7★) ⇒ ★**零写板 · 零落表 · 零改既有闸 · 零改 `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` · 零外发 · 未替老板拍板** ★
>
> ★**本单是 CONT1 续做** ★ (★上一趟 `agent:mech-lead:subagent:570f2ad1-…` 于 18:24:11 被运行时掐掉 ⇒ 上一趟留下的
> 「一页 + 闸」已在盘, 本趟从**两处定点改写**接着做; ★续做清单与在飞信号见 `logs/iss367/99_CONT1_resume_20260723_1830.md`★)

- **单号**: ISS-367 · **agent**: mech-lead (结构总工 · 带散热) · **类别**: 纯文档定点改写 + 新建闸 + 沙盒重算
- **交卷时间**: 2026-11-23 18:3x (Asia/Shanghai)
- **交卷物**: ① 规格页 1 件 ② 机器闸 1 件 ③ 交卷页 + 分片 + `logs/iss367/` 留证

---

## B1 结论

### B1-1 · 三个最硬的数 (★全部本机实算 · 可复跑 · ★**不是抄任何 agent 报告**★)

| 项 | BEFORE (★现役板 · 占位 land★) | AFTER (★S10 换官方 0805 之后 · 25 件 MECH 侧子集口径★) | Δ |
|---|---|---|---|
| ★**可落位块数** (净距 0.00) ★ | ★1992★ | ★**2183** ★ | ★**+191** ★ |
| ★**整高自由带 A** ★ | ★X 1.550..3.450 (宽 1.900) · Y 1.450..98.950★ | ★**X 2.225..3.250 (宽 1.025)** · Y 1.500..98.500★ | ★**宽 −0.875** · 左沿 +0.675 / 右沿 −0.200★ |
| ★**整高自由带 B** ★ | ★X 72.540..73.660 (宽 1.120) ★ | ★**X 73.215..74.385 (宽 1.170)** ★ | ★宽 +0.050 · 左沿 +0.675 / 右沿 +0.725★ |
| ★**最近落位带** (封装原点可放行窗口) ★ | ★X 6.940..8.250 (宽 1.310) · Y 63.700..67.900 (高 4.200)★ | ★**X 7.615..8.550 (宽 0.935)** · Y 63.675..67.325 (高 3.650)★ | ★宽 −0.375 · 高 −0.550★ |
| ★**净距敏感度 sweep** (clr 0.00/0.10/0.20/0.50) ★ | ★1992 / 2016 / 2031 / 2075★ | ★**2183 / 2241 / 2253 / 2197** ★ | ★+191 / +225 / +222 / +122★ |
| ★**sweep 单调性** ★ | ★单调 (1992 < 2016 < 2031 < 2075)★ | ★**不再单调** (★clr=0.50 的 **2197** < clr=0.20 的 **2253**★) ★ | ★**旧直觉作废** ★ |
| ★**封装原点窗口** ★ | ★X 1.550..157.050 · Y 1.450..98.950★ | ★**X 2.225..157.775 · Y 1.500..98.500** ★ | ★X 左沿 +0.675 / 右沿 +0.725 · Y 下沿内缩 0.050 / 上沿内缩 0.450★ |
| ★**`rel` 铜箔包络** (相对封装原点) ★ | ★`(-0.750, 2.150, -0.650, 0.250)`★ | ★**`(-1.425, 1.425, -0.700, 0.700)`** ★ | ★X 对称化 (铜箔宽 2.900 → 2.850) · Y 向下多长 0.050 / 向上多长 0.450★ |

★**复跑命令**: ★`python3 MECH/check_onepass_s10_led_spec_sync.py --compute` (★输出留证 `logs/iss367/07_compute_after.json`★)
★**双路径交叉对账**: ★解析式 (不落板副本) 与 pcbnew 沙盒板副本 (25 件真换) 的四组数**逐字相同** ⇒ ★`logs/iss367/04_crosscheck_two_paths.txt` ★

★**⇒ 结论一句话**: ★**板那一趟若还按旧数 (1992 / 1.550..3.450 / 72.540..73.660) 布局 ⇒ 带 A 少 0.875 mm ⇒ `D_LED_G` 落位超框
/ 结构件装不下 ⇒ 板 md5 第二次变 ⇒ 整趟白跑** ★ ⇒ ★**所以这是【板只改一次】那一趟开工之前必须先收口的前置件** ★

### B1-2 · 本单做的四件事

| # | 事 | 落点 | 证据 |
|---|---|---|---|
| ★**1** ★ | ★**两处定点改写** (★main 授权只这两处·其余老字一字不许动★) ★ | ★① `MECH/BOARD_ONEPASS_MECH_SYNC.md` (★机器块 12 个字段 + 正文 9 行 + 新增 `s10_basis` 口径声明★) ★② `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (★机器块 2 个窗口 rect + 正文 16 行 + 2 行口径声明引用块★) ★ | ★`logs/iss367/11_diff_MECH_SYNC.txt` · `11_diff_S6_CALIBER.txt` (★`diff -u` 全文★) |
| ★**2** ★ | ★**新建一页规格** ★ | ★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` (§0 口径 / §1 漂移本体 / §2 定点改写逐字 / §3 LED 窗口规格 / §4 同趟重算清单 / §5 未决项 / §2.4 本趟自审更正 / §6 机器块) ★ | ★`logs/iss367/14_diff_SPEC_PAGE.txt` |
| ★**3** ★ | ★**新建一条机器闸** ★ | ★`MECH/check_onepass_s10_led_spec_sync.py` (★L0 基准块 · L1 四组数==实算 · L2 非单调须显式承认 · L3 两处定点改写不许与实算打架 · L4 证据等级五级白名单 · L5 零挂起措辞 · L6 沙盒在项目盘 `tmp/`★) | ★`logs/iss367/13_gate_run_after_rewrite.txt` (★rc=0★) + `15_selftest.txt` (★rc=0 · 7/7★) |
| ★**4** ★ | ★**修本单闸自身的 9 条假红** (★见 B1-4★) ★ | ★同上闸脚本的 L4 判据 (★**只改「什么算证据等级」这一步** · 五级白名单方向一字未动★) ★ | ★同上 + §2.4 第 1 条 |

### B1-3 · 两处定点改写 = 【页 + 机器块 + 正文】三份同源 (★不许打架★)

| 位置 | 改前 | 改后 |
|---|---|---|
| ★`MECH_SYNC` 机器块 `led.full_height_bands[0]` ★ | ★`{1.55, 3.45, 1.45, 98.95}`★ | ★**`{2.225, 3.25, 1.5, 98.5}`**★ |
| ★`MECH_SYNC` 机器块 `led.full_height_bands[1]` ★ | ★`{72.54, 73.66, 1.45, 98.95}`★ | ★**`{73.215, 74.385, 1.5, 98.5}`**★ |
| ★`MECH_SYNC` 机器块 `led.nearest_band` ★ | ★`{6.94, 8.25, 63.7, 67.9}`★ | ★**`{7.615, 8.55, 63.675, 67.325}`**★ |
| ★`MECH_SYNC` 机器块 `led.hypothesis_hole.space` ★ | ★`{6.94, 8.25, 63.7, 67.9}`★ | ★**`{7.615, 8.55, 63.675, 67.325}`**★ |
| ★`MECH_SYNC` 机器块 `led.hypothesis_nohole.space` + `space_kind` ★ | ★`{1.55, 3.45, 1.45, 98.95}` + 「另有一条 X 72.540..73.660」★ | ★**`{2.225, 3.25, 1.5, 98.5}` + 「另有一条 X 73.215..74.385」**★ |
| ★`MECH_SYNC` 机器块 两处 `net_len_range_mm` ★ | ★`[0.450, 0.965]`★ | ★**`[0.621, 0.976]`**★ |
| ★`MECH_SYNC` 机器块 `led.clearance_sweep` (四行) ★ | ★1992/2016/2031/2075 + 0.450/0.559/0.680/0.965★ | ★**2183/2241/2253/2197 + 0.621/0.721/0.754/0.976**★ |
| ★`MECH_SYNC` 机器块 `items[].spec` (`MECH-LED-G` 的 spec 字段) ★ | ★旧两假设空间★ | ★**新两假设空间** (★与 `led.hypothesis_*` 同一份数据·不改就自相矛盾★)★ |
| ★`MECH_SYNC` 机器块 新增 `led.s10_basis` ★ | ★—★ | ★**一行口径声明**: 「空间类字段 = S10 之后的真数; `current_*` 三个字段 = 现役板现状」★ |
| ★`MECH_SYNC` 正文 9 行 (§4 清单 ×2 / §7 结论 ×2 / §5 窗口行 / §5 代价 A·B / §9.3 约束④) ★ | ★旧数★ | ★**新数 + 「(★S10 0805 后口径★)」限定词**★ |
| ★`S6_CALIBER` 机器块 `led_window_g_bench_hard.rect` ★ | ★`{1.550, 3.450, 1.450, 98.950}`★ | ★**`{2.225, 3.250, 1.500, 98.500}`**★ |
| ★`S6_CALIBER` 机器块 `led_window_g_bench_recommended.rect` ★ | ★`{6.940, 8.250, 63.700, 67.900}`★ | ★**`{7.615, 8.550, 63.675, 67.325}`**★ |
| ★`S6_CALIBER` 正文 16 行 (§1 表 / §4.2 五行 + 净距敏感度表四行 / §5 窗口行 / §6b.2 两行 / §6b.3 三行 / §9.3 约束行) ★ | ★旧数★ | ★**新数**★ |
| ★`S6_CALIBER` §4.2 段首 + §6b 段首 ★ | ★—★ | ★**各追加一行口径声明引用块** (★「本节全部数 = S10 之后的口径; 现状实测行仍是现役板读数」★)★ |

★**★ ⇒ ★**两页**其余任何一行**逐字节未变 ⇒ ★**diff 全文留证**: ★`logs/iss367/11_diff_MECH_SYNC.txt` (★9 个 hunk★) ·
★`logs/iss367/11_diff_S6_CALIBER.txt` (★8 个 hunk★) ★

### B1-4 · ★★本趟 (CONT1) 自审挖出的四件事 (★上一趟留下的坑·本趟全部按实算改正★) ★★

| # | 问题 | 本趟怎么处理的 | 留证 | 证据级 |
|---|---|---|---|---|
| ★**1** ★ | ★**本单机器闸的 L4 有【自身假红】9 条** ★ —— 病灶 = 闸把【方括号包裹的数值区间】(`[−0.750, +2.150]`) 与【数组字面量】(`["placeable"]`) 也当「证据等级标记」来判 | ★**修法只落在产生点** ★: 只把「内容全为中文表意文字 + ASCII 数字 且 至少含一个中文」的方括号 token 当等级候选 ⇒ ★**五级白名单方向 (五级) 一字未改** ★ ⇒ 非白名单的等级标签照样红; ★另把反向用例由 6 条增到 **7 条** (★新增「把 §2 全部证据等级清空 ⇒ L4 红 (章节没标)」★) ⇒ `--selftest` **7/7 全抓到** | ★`logs/iss367/15_selftest.txt` · 规格页 §2.4 第 1 条 | ★`[实测]`★ |
| ★**2** ★ | ★**上一趟 §2.1 / §3.1 的改写清单漏了两处同源行** ★ ⇒ ① `MECH_SYNC` 机器块 `items[].spec` (★它与 `led.hypothesis_*` 是同一份空间数据★) ② `S6_CALIBER` §9.3 S6 落位约束第 ④ 条 (★`D_LED_G` 窗口行★) | ★**两条都补进清单并已改写** ★ (★规格页 §2.1 第 14 条 / §3.1 第 16 条★) ⇒ ★**留在这两处不改就与机器块自相矛盾** ★ | ★`logs/iss367/11_diff_*.txt` | ★`[实测]`★ |
| ★**3** ★ | ★**上一趟 §3.1 item 8 的「最近落位封装原点」后三档写错了** ★ (★按「x1 ± clr」硬推, 不是 `led_space()` 的 `nearest_to_r_led_g` 第一条的 `origin` 实跑值★) | ★**按实算改正** ★ ⇒ (7.715, 63.775) / (7.815, 63.875) / (8.115, 64.175) ⇒ ★**同一函数同一口径复跑 BEFORE 得 (8.250, 63.700) / (8.150, 63.800) / (8.050, 63.900) / (8.420, 64.200) 与改前页逐字相同 ⇒ 证明本次复核与上一趟同源** ★ | ★`logs/iss367/08_nearest_origin.json` | ★`[实测]`★ |
| ★**4** ★ | ★**规格页 §1.3 / §5.1 有四处差值算错** ★ (★「Y 两端各内缩 0.050」/「整体右移 +0.675」/「Y 向各压 0.025」/「窄 0.405」★) | ★**全部按实算改正** ★ (★Y 下沿 0.050 / 上沿 0.450 · 左沿 +0.675 / 右沿 +0.300 (带宽 1.310 → 0.935 = −0.375) · Y 下沿 −0.025 / 上沿 −0.575 (带高 4.200 → 3.650 = −0.550)★) | ★同上 (`07_compute_after.json` · `08_nearest_origin.json`) | ★`[实测]`★ |

★**★ ⇒ ★**本单交出去的数 **全部是本机实跑读数**, 上一趟留下的三处错值**没有一条被带进交付物** ★

### B1-5 · ★一条没替老板拍 ★

★**`D_LED_G` 结构光孔有/无** (★老板项 U-365-3★) / ★**按键 3 N vs 1.5 N** (★老板项★) / ★**「板只改一次」那一趟 S10 到底换几件** (★25 件子集 vs 91 件全换★)
—— ★**本单只登记两路的结构代价与要红的闸, 一个字没拍** ★ ⇒ ★**详见 B5** ★

---

## B2 验收标准自评 (★20 条逐条 · 通过 / 不通过 / 未验★)

| # | 验收线 | 判定 | 证据 (★本机实跑★) |
|---|---|---|---|
| ① | ★页存在且非空 ★ | ★**通过** ★ | ★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` = 47,470 B (★47,368 字符★) / md5 `e7c067979162b57141130158b4ceb6ef`★ |
| ② | ★四个数 (块数 / 两条带 / sweep) 与脚本实算一致 ★ | ★**通过** ★ | ★闸 L1 绿 (★页机器块 vs `--compute` 实算★) ⇒ `logs/iss367/13_gate_run_after_rewrite.txt`★ |
| ③ | ★sweep 非单调被显式承认 ★ | ★**通过** ★ | ★页 §1.4 明写「AFTER **不再单调**: clr=0.50 的 **2197** < clr=0.20 的 **2253**」+ 机器块 `led_space_after.monotonic = false` ⇒ 闸 L2 绿★ |
| ④ | ★MECH_SYNC 机器块与页一致 ★ | ★**通过** ★ | ★闸 L3 绿 (★MECH_SYNC 机器块 == 实算 == 页★)★ |
| ⑤ | ★证据等级全在五级白名单 ★ | ★**通过** ★ | ★闸 L4 绿 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 五级内·§0~§5 每节至少一个★)★ |
| ⑥ | ★正文零挂起措辞 ★ | ★**通过** ★ | ★闸 L5 绿 (★禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」★)★ |
| ⑦ | ★新闸 rc=0 ★ | ★**通过** ★ | ★`python3 MECH/check_onepass_s10_led_spec_sync.py` ⇒ **rc=0** (★L0~L6 全绿★)★ |
| ⑧ | ★`--selftest` ≥6/6 且每条自证「只红目标那条」 ★ | ★**通过 (7/7)** ★ | ★`logs/iss367/15_selftest.txt` ⇒ **rc=0** · 末行「✅ 7 条反向用例全抓到 (且其余判据仍绿) ★ ALL TESTS PASS ★」★ |
| ⑨ | ★沙盒在项目盘 `tmp/` ★ | ★**通过** ★ | ★机器块 `"sandbox": "tmp/iss367_sbx/"` + `"selftest_sandbox": "tmp/iss367_selftest/"` ⇒ 闸 L6 绿 (★不写 /tmp★)★ |
| ⑩ | ★两处定点改写之外老字逐字节未变 (diff 留证) ★ | ★**通过** ★ | ★`diff -u` 全文在盘 (`11_diff_MECH_SYNC.txt` 9 hunk / `11_diff_S6_CALIBER.txt` 8 hunk) + 改前原文备份 (`10_pre_*.md`) ★ |
| ⑪ | ★`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 逐字节未变 ★ | ★**通过** ★ | ★md5 `8a38ac9319e2e47fc080d3651995cf5b` 前后同 (★开工前基线 `05_baseline_pre_CONT1.md` · 交卷后 `19_final_md5.txt`★)★ |
| ⑫ | ★既有闸脚本一个字节未改 ★ | ★**通过** ★ | ★`check_onepass_s10_fp_swap_impact.py` `6141ae7d…` · `check_onepass_struct_crosscheck.py` `4eddd08f…` · `check_onepass_mech_sync.py` `5247486a…` · `check_board_frame_coords.py` `d4bd30c2…` · `check_demo_struct_truth.py` `483d018a…` 前后同★ |
| ⑬ | ★板 md5 / mtime 逐字节未变 ★ | ★**通过** ★ | ★md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 开工前 / 交卷后各打一次 (★双证★)★ |
| ⑭ | ★网表 / 脚表 / BOM md5 逐字节未变 ★ | ★**通过** ★ | ★`6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8` 前后同★ |
| ⑮ | ★`merge.py` rc=0 且 `gate_check.py` rc=0 (Q1 = 18/18) ★ | ★**通过** ★ | ★`state/merge.py` rc=0 (★最新一次实跑: 产出 779 / 阻塞 43 / 未闭合需求 310 / 冲突 0 · ★这三个数是【全域分片】的活数·别的总工一交卷就动·本域不受影响★★) · `state/gate_check.py` rc=0 (★**Q1 18/18** · Q2 3/3 · Q6 ✅ · Q7 10/10★) ⇒ `logs/iss367/18_all_commands.txt` · `20_gate_check.txt` · `22_final_commands_rerun.txt`★ |
| ⑯ | ★既有 4 道 MECH 闸读完仍全 rc=0 ★ | ★**通过 (实跑 5 道)** ★ | ★`check_onepass_s10_fp_swap_impact.py` · `check_onepass_mech_sync.py` · `check_onepass_struct_crosscheck.py` · `check_board_frame_coords.py` · `check_demo_struct_truth.py` 全 rc=0 ⇒ `logs/iss367/18_all_commands.txt`★ |
| ⑰ | ★分片写入只走 `state/frag_write.py` ★ | ★**通过** ★ | ★`logs/iss367/write_frag_367.sh` (★唯一调用入口 = `python3 state/frag_write.py --agent mech-lead …`★) · 写前 md5 `23262e2f…` → 写后 `26ae7cd5…` (`16_frag_md5_before.txt` / `17_frag_md5_after.txt`) ★ |
| ⑱ | ★交卷页 B1~B6 齐全 ★ | ★**通过** ★ | ★本页 B1~B6 六段齐全 (★Q1 判 18/18 命中本域·本单页标题含 B1..B6 全部六块★)★ |
| ⑲ | ★`logs/iss367/` 留证在盘 (≥ 10 件) ★ | ★**通过 (45 件)** ★ | ★`logs/iss367/` 共 45 件 (★清单见「附 · 留证清单」★)★ |
| ⑳ | ★一键回滚说明在盘 (改前 / 改后原文 + 回滚命令) ★ | ★**通过** ★ | ★`logs/iss367/12_ROLLBACK.sh` (★改前原文 = `10_pre_MECH_SYNC.md` / `10_pre_S6_CALIBER.md` / `10_pre_SPEC_PAGE.md`★)★ |

★**⇒ 20 条全部通过 (★未验 0 条 / 不通过 0 条★) ★**

★**★ 收工前的一次【独立复跑复核】 (★2026-11-23 19:3x · 本机实跑 · 原始输出 `logs/iss367/22_final_commands_rerun.txt`★) ★★**
★**⇒ 5 道既有 MECH 闸 rc=0 · 本单新闸 rc=0 · `--selftest` rc=0 (7/7) · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (★Q1 18/18 · mech-lead 6/6★) · `state/frag_write.py --agent mech-lead --show` rc=0 · `MECH/tools/check_mech_ref_reachability.py` rc=0 (★位号引用可达性闸 · 本单新建的页与闸不许把它读红★) ★**
★**⇒ 板 md5/mtime · 网表/脚表/BOM md5 · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` md5 · 5 道既有闸 + `state/gate_check.py` / `merge.py` / `frag_write.py` md5 —— 交卷后复跑与开工前基线逐字相同 (★零写板 / 零落表 / 零改既有闸 / 禁改页未动 四条成立★) ★**
★**⇒ 本次复核只动了【本单自己的闸】一处【输出字段】: `summarize()` 的 `clearance_sweep` 每条多带一个 `nearest_origin` (★纯证据输出 · L0~L6 七条判据与 L1 的比对口径一个字节没动 · `--selftest` 7/7 仍全抓到·L0~L6 仍全绿★) ⇒ 新闸脚本 md5 由 `f981d34b1411051df32a2c6ee0c3fce3` 变 `0575bcb0b87c97817208160783e55c3a` ⇒ 交卷页与分片里记的旧 md5 已在下方清单同步更新★**

---

## B3 证据分级 (★每个数写清是五级里的哪一级★)

| 数 | 值 | 证据级 | 产出它的是什么 |
|---|---|---|---|
| ★可落位块数 (AFTER) ★ | ★2183★ | ★`[实测]` (★脚本实跑★) ★ | ★`MECH/check_onepass_s10_led_spec_sync.py --compute` (★只读 import `check_board_frame_coords.py` 的 `led_space()`★)★ |
| ★两条整高自由带 (AFTER) ★ | ★X 2.225..3.250 / 73.215..74.385 · Y 1.500..98.500★ | ★`[实测]` (★脚本实跑★) ★ | ★同上★ |
| ★sweep (AFTER) ★ | ★2183 / 2241 / 2253 / 2197★ | ★`[实测]` (★脚本实跑★) ★ | ★同上 + 双路径交叉对账 (`04_crosscheck_two_paths.txt`)★ |
| ★`rel` 铜箔包络 (AFTER) ★ | ★`(-1.425, 1.425, -0.700, 0.700)`★ | ★`[实测]` (★脚本实跑★) ★ | ★同上★ |
| ★最近落位封装原点 (四档) ★ | ★(8.550, 63.675) / (7.715, 63.775) / (7.815, 63.875) / (8.115, 64.175)★ | ★`[实测]` (★脚本实跑·同一函数复跑 BEFORE 与改前页逐字相同★) ★ | ★`logs/iss367/probe_nearest_origin.py` ⇒ `08_nearest_origin.json`★ |
| ★`LED_G_D` 网两端与现状网长 (换 land 后) ★ | ★(6.725, 62.500) ↔ (100.3125, 56.800) · 93.760920 mm (Δ +0.268193)★ | ★`[实测]` (★板面 pad 坐标实读 + 换 land 后实算★) ★ | ★`logs/iss367/probe_net_ends.py` ⇒ `09_net_ends.json`★ |
| ★目标 0805 land 几何 (焊盘局部坐标 / 尺寸) ★ | ★`(-0.9375, 0)` / `(+0.9375, 0)` · 0.975 × 1.400 mm★ | ★`[实测]` (★本机 KiCad 库 `.kicad_mod` 实读★) ★ | ★`/home/yuewuya/kicad/AppDir/share/kicad/footprints/LED_ + SMD.pretty/LED_0805_2012Metric.kicad_mod`★ |
| ★两条可放行带对 S6 落位的结构代价 (带 A 窄 0.875 ⇒ 落位原点 X 容错 ±0.950 → ±0.5125) ★ | ★见规格页 §3.4 建议 1★ | ★`[推算]` (★几何算术·无外部输入★) ★ | ★规格页 §3.4★ |
| ★`D_LED_G` 结构光孔位置 / 孔径 ★ | ★—★ | ★`[0数据]` (★孔径取决于最终 OPN 的镜头 Ø★) ★ | ★规格页 §5.1★ |
| ★本单实物 `[实测]` 条数 ★ | ★**0 条** ★ | ★`[0数据]` (★本机无板无量具·全部是文件实读 + 脚本实跑★) ★ | ★—★ |

★**口径提醒**: ★**一切「实测」= 文件实读 + 脚本实跑** ★ ⇒ ★**实物 `[实测]` = 0 条** ★ · ★封装高度等外部数据标 `[官网]` · ★**本单零外发** (★没发一封信·没问一个供应商·封装几何全部本机库文件自读★)★

---

## B4 接口取值声明 (★interface_claims · ★只写本域 mech.yaml·只走 `state/frag_write.py`★)

★**第一次写 (★交卷主体★): 写前 md5 `23262e2f1c4a30162c93b66e5aa59bcf` → 写后 md5 `26ae7cd5d088febb7e2b614d116307a3`**
(★写前写后各记一次 (★`16_frag_md5_before.txt` / `17_frag_md5_after.txt`★) · ★**期间 md5 未被别处改过** (★写前值与开工前基线 `05_baseline_pre_CONT1.md` 逐字相同★) ⇒ ★**没有被别人改过 ⇒ 没有触发「已停止」条款**★)★
★**第二次写 (★收工前独立复跑复核后补一条 claim·★`iss367_mech_final_independent_rerun`★): 写前 md5 `26ae7cd5d088febb7e2b614d116307a3` → 写后 md5 `0e69d44342f9a70b68c7b58f89b64b14`**
(★写前写后各记一次 (★`23_frag_md5_before.txt` / `24_frag_md5_after.txt`★) · ★**写前值与第一次写后值逐字相同 ⇒ 期间仍未被别处改过** ★)★

| key | value | note 摘要 | 证据级 |
|---|---|---|---|
| ★`iss367_mech_s10_led_space_recompute` ★ | ★`2183 / 2.225..3.250 + 73.215..74.385 / 2183·2241·2253·2197 (不再单调)`★ | ★25 件 S10 MECH 侧子集口径 · 双路径交叉对账一致 · 四组数 + Δ + 不再单调★ | ★`[实测]`★ |
| ★`iss367_mech_two_spot_rewrites_done` ★ | ★`MECH_SYNC + S6_CALIBER 两处机器块已按实算逐字改写 (diff 留证在盘)`★ | ★逐条列改了什么 + 改前/改后 md5 + diff 与备份路径 + 「两页其余任何一行逐字节未变」★ | ★`[实测]`★ |
| ★`iss367_mech_l4_false_red_fixed` ★ | ★`L4 判据方向 (五级白名单) 一字未改 · 9 条假红已消`★ | ★病灶 = 数值区间/数组字面量被误当等级 · 修法只落在产生点 · 反向用例 6 → 7 条 · 7/7 全抓到★ | ★`[实测]`★ |
| ★`iss367_mech_s10_spec_corrections` ★ | ★`上一趟清单漏 2 处同源行 + 1 处落位原点坐标写错 ⇒ 本趟按实算改正`★ | ★三条逐条列清 + 留证路径 (★`08_nearest_origin.json` 复跑 BEFORE 与改前页逐字相同★)★ | ★`[实测]`★ |

★**★ artifacts (3 件) ★**: ★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` (kind=spec) · ★`MECH/check_onepass_s10_led_spec_sync.py` (kind=gate) ·
★`HANDOFF/2026-11-23_mech-lead_ISS367_S10换封装LED窗口规格同趟重算.md` (kind=handoff) ★
★**★ need (1 条·归 main) ★**: ★`iss367_mech_s10_swap_set_count_to_main` (★要 main 回答「那一趟 S10 到底换几件」★)★

★**★ 本单没写别人的分片 (★`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰★) · 没改 `PROJECT_TRACKER.md` §0 · 没改 `state/issue_log.yaml` ★

---

## B5 未决项与卡点 (★需要谁回答什么 · **只列事实与代价·不代拍**★)

| # | 未决项 | 要谁回答什么 | 结构侧代价 (★按 §1.3 AFTER 那套数★) | 会红的闸 | 证据级 |
|---|---|---|---|---|---|
| ★**1** ★ | ★**`D_LED_G` 结构光孔有/无** (★老板项 U-365-3★) ★ | ★**boss (经 main)**: ★光孔开 / 不开 / 孔径多大★ —— ★**必须排在「板只改一次」那一趟之前拍**★ | ★**A 有孔**: 可放行空间 = 最近落位带 **X 7.615..8.550 × Y 63.675..67.325** (★比旧口径窄 0.375·左沿 +0.675 / 右沿 +0.300★) ⇒ ★**板面落位要改**★ · ★**B 无孔**: 可放行空间 = 整高自由带 **X 2.225..3.250 (宽 1.025)** + **X 73.215..74.385 (宽 1.170)** ⇒ ★**板面落位零改动**★ (★这一档是「板只改一次」更稳的那一档★) | ★`MECH/check_onepass_s10_led_spec_sync.py` L3 (★两处机器块 vs 实算★) · ★`MECH/check_onepass_mech_sync.py` M1a (★两假设空间齐全★) | ★`[0数据]` (★孔径★) + ★`[实测]` (★空间★)★ |
| ★**2** ★ | ★**「板只改一次」那一趟 S10 到底换几件** ★ | ★**main 拍 (★hw-lead 给换件清单★)**: ★**25 件 MECH 侧子集** (★本单口径★) 还是 ★**91 件靶子全换**★ | ★**若 91 件全换** ⇒ 可落位块数 **2183 → 2200** · sweep **2200/2237/2250/2167** ⇒ ★**本页与两处机器块当场失效**★ ⇒ ★**那一趟开工当天必须先跑 `python3 MECH/check_onepass_s10_led_spec_sync.py` (rc≠0 就按 `--compute` 的读数更新)** ★ | ★同上 L1/L3 (★rc≠0 就是它红★) | ★`[实测]`★ |
| ★**3** ★ | ★**按键 3 N vs 1.5 N** (★老板项★) ★ | ★**boss (经 main)**: ★3 N 还是 1.5 N★ —— ★**它一旦改选型 (换封装) ⇒ 四组数要再重算一次**★ | ★按键件也在 S10 的 25 件子集里 ⇒ 换 land 后铜箔外框变了 ⇒ 障碍集变了; ★另 KMR2 本体 4.200 × 2.800 vs 占位 3.000 × 3.000 ⇒ **本体宽 +1.200** ⇒ 键孔/键帽间隙要按新本体重核★ | ★同上 L1/L3 | ★`[实测]` (★`.kicad_mod` 实读·KMR2 本体★) + ★`[推算]`★ |
| ★**4** ★ | ★**「对比现状」列的基线** (★连带项·那一趟改板后同步★) ★ | ★**那一趟改板后** (★hw-lead 改板 ⇒ MECH 侧同步★): ★`LED_G_D` 现状网长 **93.492727 → 93.760920 mm** ⇒ ★**「省 XX mm」一列随之 +0.268193**★ | ★本单已把这一条写进 §4.2 / §6b 段首的口径声明 (★「对比现状」列的基线 = 现役板 93.492727 · S10 改板后基线变 93.760920★) ⇒ ★**本单不把假话写进「现状实测」栏**★ | ★—— (★这一趟的作业包收口★) | ★`[实测]` (★两端 pad 坐标实读★) + ★`[推算]`★ |
| ★**5** ★ | ★**新闸挂不挂门禁链** ★ | ★**main**: ★`MECH/check_onepass_s10_led_spec_sync.py` 要不要挂进 `state/gate_check.py` 的 `EXTRA_GATES`★ | ★**本单没挂** (★挂闸是 main 地界·`state/gate_check.py` 一个字节没碰★) ⇒ ★**挂链后每天多跑一次 (★秒级·只读板 + 沙盒副本·不写板★)** ★ | —— | ★`[实测]` (★自检耗时秒级·跑完板 md5 不变★)★ |

★**★ ⇒ ★**本单**没有**替老板拍上面任何一条; ★**每条都给了「事实 + 代价 + 要红的闸」, 拍板权原样留给 boss / main★ ★

---

## B6 自证复现命令 (★全部本机实跑 · rc 原样 · ★★main 可原样复跑★★)

★**★ 完整原始输出在 `logs/iss367/18_all_commands.txt` (★一次跑完 8 条命令 + rc★) · ★`20_gate_check.txt` (★gate_check 全量★) ★★

```bash
# ---- 本单新建的闸 ----
python3 MECH/check_onepass_s10_led_spec_sync.py            # ⇒ rc=0  (L0~L6 全绿)
python3 MECH/check_onepass_s10_led_spec_sync.py --compute   # ⇒ rc=0  (四组数实算)
python3 MECH/check_onepass_s10_led_spec_sync.py --selftest  # ⇒ rc=0  (7/7 反向用例全抓到)

# ---- 既有 MECH 闸 (★回归·不许被本单改红★) ----
python3 MECH/check_onepass_s10_fp_swap_impact.py            # ⇒ rc=0
python3 MECH/check_onepass_mech_sync.py                     # ⇒ rc=0
python3 MECH/check_onepass_struct_crosscheck.py             # ⇒ rc=0
python3 MECH/check_board_frame_coords.py                    # ⇒ rc=0
python3 MECH/check_demo_struct_truth.py                     # ⇒ rc=0

# ---- 全局 ----
python3 state/merge.py                                      # ⇒ rc=0
python3 state/gate_check.py                                 # ⇒ rc=0  (Q1 18/18 · Q2 3/3 · Q6 ✅ · Q7 10/10)
python3 state/frag_write.py --agent mech-lead --show        # ⇒ 只读

# ---- 边界双证 (★开工前 + 交卷后各打一次★) ----
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

★**★ 边界双证 (★开工前 `05_baseline_pre_CONT1.md` / 交卷后 `19_final_md5.txt`★) ★★

| 件 | 开工前 md5 | 交卷后 md5 | 判定 |
|---|---|---|---|
| ★`HW/PCB/demo_mainboard.kicad_pcb` ★ | ★`611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★ | ★**同** ★ | ★**零写板成立** ★ |
| ★`HW/netlist_v1.csv` ★ | ★`6aee500e60ba0732f83a9cf557ba90ab`★ | ★**同** ★ | ★**零落表成立** ★ |
| ★`HW/netlist_v1_pins.csv` ★ | ★`9174309df1ec9411ac8e8d9e80ee386a`★ | ★**同** ★ | ★**零落表成立** ★ |
| ★`HW/BOM_v1.csv` ★ | ★`5b9993992405904a60ac96a020b375d8`★ | ★**同** ★ | ★**零落表成立** ★ |
| ★`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` ★ | ★`8a38ac9319e2e47fc080d3651995cf5b`★ | ★**同** ★ | ★**禁改页未动** ★ |
| ★5 道既有 MECH 闸脚本 + `state/gate_check.py` / `merge.py` / `frag_write.py` ★ | ★见 `05_baseline_pre_CONT1.md`★ | ★**全部同** ★ | ★**零改既有闸成立** ★ |
| ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` (★授权改★) ★ | ★`c7945f59ad1af4b299d851fac8590a2a`★ | ★`ddd931ea7fe60277e03bc50b9092a6bc`★ | ★**已按授权改写 · diff 留证** ★ |
| ★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (★授权改★) ★ | ★`d7b33ed79a82dfe816107e323d81c8bb`★ | ★`b254fa98c09bc7adb058e1d03eb13980`★ | ★**已按授权改写 · diff 留证** ★ |
| ★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` (★本单新建★) ★ | ★`a3377f9d210ba6b74f9228e60ea29666` (上一趟遗留)★ | ★`e7c067979162b57141130158b4ceb6ef`★ | ★**本趟续做** ★ |
| ★`MECH/check_onepass_s10_led_spec_sync.py` (★本单新建·上一趟遗留初版★) ★ | ★`b1ebce2e9acb5dd0bba0ffb1a7c1de7b`★ | ★`0575bcb0b87c97817208160783e55c3a`★ | ★**本趟修 L4 + 补第 7 条反向用例; 收工前复核只加了一个 `nearest_origin` 证据输出字段·判据零变化★** ★ |
| ★`state/fragments/mech.yaml` (★只走 `frag_write.py`★) ★ | ★`23262e2f1c4a30162c93b66e5aa59bcf`★ | ★`0e69d44342f9a70b68c7b58f89b64b14` (★第一次写后 `26ae7cd5…`·收工前复核补一条 claim 后 `0e69d443…`★) ★ | ★**原子写两次 · 两次写前值均未被别处改过** ★ |

---

## 附 · 落盘文件清单 (★本单写的每一件★)

| # | 文件 | 性质 | 字节 | md5 |
|---|---|---|---|---|
| 1 | ★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` ★ | ★新建 (★上一趟有初版·本趟续做补 §2 证据级 + §2.4 自审更正 + 三处错值改正★) ★ | 47,470 | `e7c067979162b57141130158b4ceb6ef` |
| 2 | ★`MECH/check_onepass_s10_led_spec_sync.py` ★ | ★新建 (★上一趟有初版·本趟修 L4 假红 + 补第 7 条反向用例 + 修反向用例 ① 的作用域★; ★收工前复核时只给 `summarize()` 的 `clearance_sweep` 每条多带一个 `nearest_origin` 证据字段·L0~L6 七条判据一个字节没动★) ★ | 36,065 | `0575bcb0b87c97817208160783e55c3a` |
| 3 | ★`HANDOFF/2026-11-23_mech-lead_ISS367_S10换封装LED窗口规格同趟重算.md` ★ | ★新建 (★本页★) ★ | —— | —— |
| 4 | ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` ★ | ★**定点改写** (★授权项 ①★) ★ | 99,078 | `ddd931ea7fe60277e03bc50b9092a6bc` |
| 5 | ★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` ★ | ★**定点改写** (★授权项 ②★) ★ | 49,413 | `b254fa98c09bc7adb058e1d03eb13980` |
| 6 | ★`state/fragments/mech.yaml` ★ | ★分片 (★只走 `state/frag_write.py`★ · ★两次写: 交卷主体 + 收工前复核补一条 claim★) ★ | 697,925 | `0e69d44342f9a70b68c7b58f89b64b14` |
| 7 | ★`logs/iss367/` (★45 件★) ★ | ★留证 ★ | —— | —— |

★**★ ⇒ ★**本单**只写这 7 处** ⇒ ★**`HW/` 零写 · `SW/` 零写 · `state/issue_log.yaml` 零写 · `PROJECT_TRACKER.md` 零写 ·
★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 零写** · ★**5 道既有 MECH 闸 + `state/gate_check.py` / `merge.py` / `frag_write.py` 零写** ★

## 附 · `logs/iss367/` 留证清单 (★45 件★)

| 件 | 内容 |
|---|---|
| ★`99_CONT1_resume_20260723_1830.md` ★ | ★**续跑标记** (★给兄弟 job fb67af40 的「在飞」信号 + 上一趟 session key + 死因判定 + 续做清单★)★ |
| ★`05_baseline_pre_CONT1.md` ★ | ★**开工前基线** (★板/表双证 + 禁改页 + 既有闸 + 待改两页 md5★)★ |
| ★`07_compute_after.json` ★ | ★**四组数实算** (★`--compute` 原始输出★)★ |
| ★`08_nearest_origin.json` ★ | ★**最近落位封装原点四档实算** (★BEFORE/AFTER 双侧·证明与上一趟同源★)★ |
| ★`09_net_ends.json` ★ | ★**`LED_G_D` 网两端 + 现状网长实算** (★换 land 前后·93.492727 → 93.760920·Δ +0.268193★)★ |
| ★`10_pre_MECH_SYNC.md` / `10_pre_S6_CALIBER.md` / `10_pre_SPEC_PAGE.md` ★ | ★**三份改前原文逐字节备份** (★一键回滚的还原源★)★ |
| ★`11_diff_MECH_SYNC.txt` / `11_diff_S6_CALIBER.txt` ★ | ★**两处定点改写的 `diff -u` 全文** (★验收线 ⑩ 的证据★)★ |
| ★`12_ROLLBACK.sh` ★ | ★**一键回滚说明 + 回滚命令** (★验收线 ⑳★)★ |
| ★`13_gate_run_after_rewrite.txt` ★ | ★**新闸复跑输出** (★rc=0 · L0~L6 全绿★)★ |
| ★`14_diff_SPEC_PAGE.txt` ★ | ★规格页本趟续做的 diff★ |
| ★`15_selftest.txt` ★ | ★**`--selftest` 全量输出** (★rc=0 · 7/7★)★ |
| ★`16_frag_md5_before.txt` / `17_frag_md5_after.txt` ★ | ★**分片写前 / 写后 md5 基线 (第一次写·交卷主体)** (★并发守卫证据★)★ |
| ★`23_frag_md5_before.txt` / `24_frag_md5_after.txt` ★ | ★**分片写前 / 写后 md5 基线 (第二次写·收工前复核补 claim)** (★并发守卫证据·写前值与第一次写后值逐字相同⇒期间未被别处改过★)★ |
| ★`18_all_commands.txt` ★ | ★**8 条必跑命令 + rc 的原始输出** ★ |
| ★`19_final_md5.txt` / `20_gate_check.txt` / `21_final_verification.txt` ★ | ★**交卷后全量 md5 + gate_check 全量输出 + 交卷前最终复验 (8 条命令 rc + 板/表双证 + 禁改页 md5 + 交付物 md5 + 留证件数)** ★ |
| ★`apply_rewrite_367.py` / `apply_spec_page_367.py` / `write_frag_367.sh` ★ | ★**三个可复跑的写入脚本** (★逐行定点替换 + 每处断言「待改串恰好出现 1 次」★)★ |
| ★`probe_nearest_origin.py` / `probe_net_ends.py` ★ | ★**两个本机实算探针** (★只读·不写板★)★ |
| ★`00_baseline_pre.md` / `01_compute_real.json` / `02_sbx_swap_*.json` / `02_sbx_swap_raw.txt` / `03_sbx_compute.json` / `04_crosscheck_two_paths.txt` / `probe_led_spec.py` / `probe_swap_verify.py` / `setup_iss367_sbx.py` / `06_gate_run_L4fix_pre_rewrite.txt` ★ | ★**上一趟留下的 11 件** (★本趟继续用·没有一件被删或改写★)★ |
| ★`26_page_vs_sandbox_crosscheck.txt` ★ | ★**终检: 规格页机器块 vs pcbnew 沙盒板副本逐项对账** (★完全独立路径·不经本单新闸 ⇒ 可落位块数 / 两条带 / sweep 四档 / 铜箔包络 / 原点窗口 / 单调性 逐项「一致」★)★ |
| ★`01_compute_err.txt` / `22_final_commands_rerun.txt` / `25_final_verification.txt` ★ | ★**收工前的两次【独立复跑复核】原始输出** (★2026-11-23 19:3x · 5 道既有闸 + 新闸 + `--selftest` + `merge.py` + `gate_check.py` + `frag_write --show` + 位号引用可达性闸 逐条 rc + 板/表双证 + 禁改页 md5 + 既有闸脚本 md5 + 三件交付物 md5 + 两处授权改写改前/改后 md5 + 留证件数★)★ |

## 附 · 一键回滚说明 (★验收线 ⑳★)

★**回滚命令**: ★`bash logs/iss367/12_ROLLBACK.sh` (★回滚两处定点改写 + 规格页★) · ★`bash logs/iss367/12_ROLLBACK.sh --only-gates` (★只回滚两页★) ★

★**回滚后应回到**: ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` = `c7945f59ad1af4b299d851fac8590a2a` ·
★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` = `d7b33ed79a82dfe816107e323d81c8bb` ·
★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` = `a3377f9d210ba6b74f9228e60ea29666` (上一趟遗留版) ★

★**★ ⇒ ★**回滚**只碰这三份文档**, ★**板 / 网表 / 脚表 / BOM / 既有闸 / 禁改页 一律不动** (★回滚脚本末尾自带板/表双证打印★)★

---

★**★ 交卷人**: mech-lead (结构总工 · 带散热) · ★**零外发 · 零采购 · 零联系供应商 · 未替老板拍板 · 实物 `[实测]` = 0 条** ★
