# ISS-354 cont2 · hw-lead · ★demo 主板可制造性收口 · 续做 · 纯查证 · 零写板

> ★**这是 cont2 续做派活 (★不是从零重开★)** ★
> ★**上一趟 cont1 的会话在 2026-11-23 05:41:57 撞到 3000 s 上限被掐死 (★`runTimeoutSeconds=3000` ⇒ 时间预算用完 ⇒ 不是你活干错了★) ⇒ 产物大半在盘 ⇒ 本单 = 从已完成位置续做** ★

## ★★一、上一趟怎么死的 / 已经做完了什么 (★main 本机实读, 不抄任何 agent 报告★) ★★

★**死因**: 会话 `c1e2205e-ec3f-4594-a61d-3818c0d5962a` (agent=hw-lead) 起于 04:51:57 · 撞 3000 s 上限 ⇒ ★**时间预算用完, 不是任务失败** ★

★**已在盘的产物 (★别重做·直接用★)**:

| 位置 | 内容 | 状态 |
|---|---|---|
| `logs/iss354/datasheets/` (4 份官方 PDF) + `logs/iss354/datasheets_txt/` | ★**tps7a20 / tps3808g01 / bq2970 / csd16406q3** 官方资料 ★ | ★已完成★ |
| `logs/iss354/tps7a20.txt` (341 KB) · `tps3808.txt` (140 KB) · `bq2970.txt` (153 KB) · `csd16406q3.txt` (56 KB) + `csd16406q3_raw.txt` | ★**PDF→文本抽取 (含 pin 表 / 封装图 / 尺寸) ★ | ★已完成★ |
| `logs/iss354/hirose_df40.txt` (68.9 KB) | ★**DF40C-100DS 原厂资料文本 (⇒ pin1「哪一排」的证据源) ★ | ★已完成★ |
| `logs/iss354/fp_compare.txt` (3.5 KB) · `board_fp_measure.txt` (4.4 KB) | ★**板面封装实测 vs BOM footprint 对拍 (⇒ 5 个 ref / 4 类不自洽的证据) ★ | ★已完成★ |
| `logs/iss354/som_row_nets.txt` (2.7 KB) | ★**SoM 座逐排网络清单 (⇒ pin1 排向判定) ★ | ★已完成★ |
| `logs/iss354/bom_cand_fit.txt` (1.5 KB) | ★**BOM「待选型」候选 + 代价 (⇒ 不代拍的那份) ★ | ★已完成★ |
| ★**`tmp/iss354/WP_APPEND.md` (24.7 KB)** ★ | ★**★「作业包追加段」正文已经写完 ★** ⇒ 只是**还没落盘**到 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ★ | ★**已写完·待落盘★** |
| ★**`tmp/iss354/WORKPACKET_BEFORE.md` (150.6 KB · md5 `d651a474b55e1a0dac5dc32184663bcb`) ★ | ★**落盘前的原文件快照 (⇒ 追加后可比对「零删除」) ★ | ★已完成★ |
| ★**`tmp/iss354/PREFLIGHT_BEFORE.md` (76.9 KB · md5 `581f116a6e41c6c7d6b9290874ade4c5`) ★ | ★**同上, PREFLIGHT 侧 ★ | ★已完成★ |

★**没做的 (★本单要补的就是这些★)**:
1. ★**作业包追加段落盘** (★`tmp/iss354/WP_APPEND.md` ⇒ 追加进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md`·★只追加·零删除★) ★
2. ★**PREFLIGHT 一票否决段落盘** (★若上一趟也写好了, 检查 `tmp/iss354/` 里有没有 `PREFLIGHT_APPEND.md`; 没有就照同样方式补写★)
3. ★**交卷页** `HANDOFF/2026-11-23_hw-lead_ISS354_*.md` (★零字, 上一趟一个字没写★)
4. ★**分片登记** (★`grep -c iss354 state/fragments/hw.yaml` 实测 = **0** ★ ⇒ 上一趟的结论一个字都没进台账★) ⇒ 只走 `python3 state/frag_write.py --agent hw-lead`
5. ★**自带闸** (★没有新建★) + `--selftest` 反向用例
6. ★**必跑项原样输出**

★**纪律**: ★**「不信上一趟」** ⇒ ★**引用上一趟的读数时必须注明「引用上一趟本机实测 (04:5x~05:4x)」并给出你自己的复跑读数, 两者不一致就写出来** ★

---

## ★★二、本单要补的 5 件 (★纯查证收口 · 零写板 · 零落表 · 零外发★) ★★

1. ★**落盘作业包追加段** ⇒ `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★用 `tmp/iss354/WP_APPEND.md`★) ⇒ ★**只追加·零删除** ⇒ ★**追加前后各打一次 md5 + 行数, 贴 §B6 (⇒ 证明「老字一字未删」) ★** ★
   ★★**★一条硬纠偏 (★上一趟 cont1 最后 10 秒才发现的, 别再踩★)★**: ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 是【生成器产物】(生成器 = `state/_iss277_build_preflight.py`) 且有【逐字比对闸】(钉板闸⑩ 板侧项全集重跑幂等闸) ⇒ ★**手改 PREFLIGHT ⇒ 闸当场红 ⇒ 而那个红会被误读成「板改坏了」★★ ⇒ ⇒ ★**本单【不许手改 PREFLIGHT】** ★ ⇒ ★**「一票否决段」改落到: ①WORKPACKET 追加段 ②交卷页正文 ③交卷页里另附一份 `HW/PCB/ISS354_DOWNCUT_VETO_LIST.md` (★新建·★不改 PREFLIGHT★)**** ⇒ ★**若你判断 PREFLIGHT 必须改 ⇒ 那是【生成器的事】, 不是手改的事 ⇒ 交 main 排期, 本单不许自己动生成器** ★
2. ★**交卷页** `HANDOFF/2026-11-23_hw-lead_ISS354_*.md` (★B0~B7 七块齐全 + ★页内引用路径逐个在盘 (MISS = 0)★ + ★**板指纹前后双证**★) ★
3. ★**分片**: 只走 `state/frag_write.py --agent hw-lead` ⇒ ★**交卷时 `grep -c iss354 state/fragments/hw.yaml` ≥ 5** ★ ⇒ 至少登记: ①SoM 座 pin1「哪一排」的判定 + 降级方案 + 下料前一票否决项 ②5 个 ref / 4 类封装脚号不自洽的**改项清单** ③BOM 待选型的候选 + 代价 (不代拍) ④本单自带闸 ⑤status=iss354-delivered ★
4. ★**自带闸** (★新写一个只读脚本, 路径你自己定, 交卷页里写清★): 断言 ★**那 5 个 ref / 4 类不自洽的「改项清单」在盘** ★ + ★**SoM pin1 排向的降级方案 + 一票否决项在盘** ★ ⇒ ★**必须带 `--selftest` 反向用例** (★临时副本里把一票否决项删掉 ⇒ 闸必须判红并点名★) ⇒ 末行 `ALL TESTS PASS` ★
5. ★**★加一件 (main 05:4x 本机实跑得到的·★hw.yaml 是你的地界★)★**: `state/fragments/hw.yaml` **L5226/L5227** 两条旧登记仍写着 「RK3572 NPU 与 RK3576 同代同架构 ⇒ 用 `target_platform='rk3576'` 转」 ⇒ ★**已被 ISS-250 官方反证 (RK3576=6 TOPS · RK3572=RKNN3-native) · 转换 target 已被 ISS-263 (rknn3-toolkit 1.2.0 支持 `rk3572`) 取代** ⇒ ★**请在你自己的分片里追加一条切题的取代标记 (★追加式·老条目保留作历史留档★)**: key=`iss353_hw_ledger_supersede_rk3572_target` · value=`RK3572 转换 target = rknn3-toolkit 1.2.0 + target_platform='rk3572' [实测 rc=0; 官方 README Supported Platforms 含 RK3572]; toolkit2 侧 rk3572 非法 [官网+实测]; 板端接受性 [0数据]` · note=`★已被 ISS-263 取代·本条保留作历史留档·结论不再引用★` ⇒ ★**这条是全仓最后 2 条「结论矛盾」之一 (main 实跑 `SW/tools/check_rk3572_target_caliber.py` ⇒ 结论矛盾 = 2 · 越权交 main 裁 = 2) ⇒ 加上这条, 那支闸的「结论矛盾」应降到 1** ★

---

## ★★三、边界 (★一条都不许越★) ★★

- ★**零写板**: `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 必须是 `611b869e13518c3c023fb178f91a0075` / mtime 必须是 `2026-11-06 07:07:17.362193413` ⇒ ★**开工前 + 交卷后各打一次, 双证贴 §B6** ★
- ★**零落表**: 不改网表 / 脚表 / BOM / 原理图 / 任何闸的判据方向 / `state/fragments/pm.yaml` / `state/fragments/sw.yaml` / `state/fragments/mech.yaml` / `state/issue_log.yaml` (★自签 issue_log 是 main 的地界★)
- ★**只写**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 追加段 · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 追加段 · 交卷页 · `logs/iss354/` · `state/fragments/hw.yaml` (★只走 `frag_write.py`★) · 新建的闸脚本
- ★**零外发 / 零采购 / 零联系供应商** (★老板 2026-11-12 02:02: 不再发信, 全靠自己查资料 + 标证据等级 + 查不到写降级方案★) ⇒ ★**`state/outbox/` 里的草稿一律不发** ★
- ★**不替老板拍板**: `C_VBUS_GND` 留位 / ESD 架构轴 (W-2 / W-1c) / U-1「这一趟画哪块物理产品」 ★**都不是本单的项** ⇒ ★**只交事实与改项清单** ★
- ★**沙盒纪律**: ★**临时文件/沙盒一律落项目盘 `$PWD/tmp/` (如 `tmp/iss354/`) ⇒ ★**不许写 `/tmp`** ★ (★2026-11-23 04:4x 实测 `/tmp` 配额已打满 ⇒ 写 /tmp 会让闸门拿到假读数★)

---

## ★★四、必跑项 (★交卷前跑, 原样输出贴 §B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 state/merge.py            # rc 必须 0
python3 state/gate_check.py       # rc 必须 0 · Q1 必须 18/18
python3 state/frag_write.py --agent hw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
grep -c iss354 state/fragments/hw.yaml   # 必须 >= 5
python3 <你定的那支闸>.py --selftest     # 末行 ALL TESTS PASS
```
