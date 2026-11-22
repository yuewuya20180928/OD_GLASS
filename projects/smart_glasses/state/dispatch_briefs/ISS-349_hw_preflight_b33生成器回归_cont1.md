# ISS-349 cont1 · hw-lead · ★PCB 线·零写板·收尾续单★

★**题**: 上一轮 (2026-11-23 01:4x 派) 的会话在【最后一步】被 abort 掐死 ⇒ ★**产物其实已落盘, 只差「分片登记 + 终检」两件**★。

★**main 2026-11-23 03:5x 本机独立复核 (★不抄任何 agent 报告★) 已确认在盘的**:
1. 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md` (42,143 B) —— B0~B7 齐全
2. ★**页内引用 38 个路径 · MISS = 0**★ (main 实读复核)
3. 新闸 `HW/check_preflight_regen_idempotent.py` (24,990 B) —— 裸跑 rc=0 · `--selftest` 末行 `ALL TESTS PASS` (★main 实跑★)
4. 生成器 `state/_iss277_build_preflight.py` 已含 `B33_PIN_LAND_1P27` (第 689/691 行) · 清单页 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 含 3 处
5. ★**板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动**★

★**唯一缺的**: ★**`state/fragments/hw.yaml` 里 `iss349` 命中 = 0**★ ⇒ 你的结论与产物**没有进 STATE.yaml** (merge 读不到) ⇒ ★**这就是本续单存在的全部理由**★

---

## ★★本单 (cont1) 只做 3 件 ★★

### (1) ★**分片登记** —— ★只走 `python3 state/frag_write.py --agent hw-lead`★ (★禁止 `open(p,"w")★)

- `--add-artifact path=HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md kind=handoff version=v1.0 summary="..."`
- `--add-artifact path=HW/check_preflight_regen_idempotent.py kind=gate version=v1.0 summary="..."`
- `--add-answer key=iss349_preflight_b33_generator_fixed to=main value="..." ref="HW/PCB/BOARD_ONEPASS_PREFLIGHT.md + HW/check_preflight_regen_idempotent.py + state/_iss277_build_preflight.py"`
- `--add-claim key=iss349_preflight_regen_idempotent value="..." note="..."`
- `--add-claim key=preflight_regen_gate_rc value="0 = 全过 · 1 = 闸红 · 2 = 用法错 · 3 = 闸崩" note="★接口取值声明·main 侧挂进 state/gate_check.py 时用★"`

★**零重复 key**: 先 `--show` 看有没有同 key ⇒ 有就 `--set-json` 原子去重, ★**不要新建第二条**★

### (2) ★**终检补跑** (★上一轮就是死在这一步★)

- 跑 `python3 HW/check_preflight_regen_idempotent.py` 与 `python3 HW/check_preflight_regen_idempotent.py --selftest`
- ★**把原样输出贴进交卷页 §B6 的新增小节** (★追加式 · 老字一字未删★)
- 再跑一遍「页内引用路径逐个在盘」⇒ ★**MISS = 0**★

### (3) ★**交 main 的 3 条** (§B5/B7-4 已写, 复核一遍即可) + ★**附项 1**★

★**附项 1 (★同一分片 · 零写板 · ISS-346 交回的订正★)**: `state/fragments/hw.yaml` 里 `q3_storage_and_audio` 的 `item` 措辞:
- 现状: 「外挂 SPI-NOR 16-64MB」
- ★**改为: 「外挂 SPI-NOR ≥128 MiB (1 Gbit) 起」**★
- 依据: ★**ISS-080 已锁死 flash ≥128MB**★ · 且 ★**Winbond 料号里的数字是 Mbit 不是 MB**★ (`W25Q64` = 8 MB) · ISS-346 机器判决 (5×4 矩阵 20/20 格)
- ★**只改这一句措辞, 不动 `to` / `due` / 其它字段**★ ⇒ ★**这条是【老板拍板页 §① 第 6 行】的口径来源, 不改 ⇒ 老板看到的题面是错的**★

---

## ★★纪律 (★一条不许破★) ★★

- ★**零写板** (板 md5/mtime 必须逐字节不变)★
- ★**零落表** (不改网表 / 脚表 / BOM / 原理图)★
- ★**零改闸** (只动自己的新闸, 不改别人的闸)★
- ★**零写别人的分片** (只写 `state/fragments/hw.yaml`)★
- ★**零外发** (★不许任何邮件 / 询价 / 问询 / 采购 —— 老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案
- 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标
- ★**不替老板拍板**★
- 写分片只用 `state/frag_write.py`

## ★★必跑项 (交卷前) ★★

```bash
python3 state/merge.py            # rc 必须 0
python3 state/gate_check.py        # Q1 必须 18/18
python3 HW/check_preflight_regen_idempotent.py --selftest   # 末行 ALL TESTS PASS
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须 611b869e13518c3c023fb178f91a0075
```

## ★★交卷物 ★★

交卷页 (追加式补 §B6-终检 + §B7-4 复核) + `logs/iss349/` 日志 + hw.yaml 分片登记 (5~6 条) ⇒ ★**回 main 签收**★

★**参考**: 权威任务书 `state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_修复.md` (★仍以此为准★) · 上一轮交卷页在盘可读
