# ISS-350 · sw-lead · ★PCB 线·存储轴 Q3 分档写回 SW 侧·纯口径·零写板★

★**题**: ISS-346 (Q3 存储轴可判矩阵) 已由 main 于 2026-11-23 03:4x 签收 (★21 条验收全绿 + `--self-test` 3/3 `ALL TESTS PASS`★) ⇒ ★**Q3 从「整卡」变成「分档」**★ ⇒ ★**SW 侧 (你的分片 `sw.yaml`) 的措辞还是旧的 ⇒ 机器读到的还是错的口径**★

★**main 的裁定已经落进 `state/fragments/pm.yaml`** (key `iss346_q3_storage_tier_verdict_20261123`, to=boss) ⇒ ★**你只需把 SW 侧自己的分片跟上**★

★**[实测] ISS-346 的机器判决 (5×4 矩阵 20/20 格 · failures=0)**: ① 只 ADB push 档 ⇒ 板侧零动作 ⇒ 不卡 ② 外挂 SPI-NOR 档 ⇒ `J_BOOT1` 焊盘位已在板 + 4 条 0Ω 串阻位必装 ⇒ ★**PCB 层零动作**★ ⇒ 台架板档与产品板档都不卡 ③ eMMC 档 ⇒ 板宽 12→15 mm ⇒ 台架板档 `B160x100` 板面代价 ≈ 0 ⇒ 不卡 ⇒ ★**只有「eMMC + 产品板档 (F30A / P60x15)」才卡 (时限型)**★

---

## ★★本单只做 4 件 (★纯口径 · 零写板 · 零落表★) ★★

### (1) ★**改 `sw.yaml` 里 `iss338_need_boot_storage_answer` 的措辞 3 条** ★

★**只走 `python3 state/frag_write.py --agent sw-lead --set-json <file> --set-field answers` (★整段替换该字段, 禁止手改 YAML★)★

| # | 现状 | 改为 |
|---|---|---|
| ① | 「**3 条** `SPI_*_BOOT`」 | ★**4 条**★ (`SPI_SCLK_BOOT` / `SPI_CSn_BOOT` / `SPI_MOSI_BOOT` / `SPI_MISO_BOOT` = 网表 `HW/netlist_v1.csv` L202 / L204 / L206 / L208) |
| ② | 「若外挂 SPI-NOR ⇒ **板要重出**」 | ★**不成立**★ ⇒ 改「★外挂 SPI-NOR 走 `J_BOOT1` 焊盘位 ⇒ **板侧零动作, 不重出板**★; 只有『主板上焊 SPI-NOR 芯片』才需要改板 (★该路已被网表明写『不画存储芯片』否掉★)」 |
| ③ | 问原厂「主板侧启动存储焊盘位不引出 (J_BOOT1 DNP)」 | ★**主板侧 `J_BOOT1` 焊盘位与 4 条 SPI 走线已在板 (只 pin5/pin6 的 CONN 位 DNP); 请确认 SoM 侧是否引出这 4 条 SPI boot pin (我方网表侧记为 `SoC_NC`)★** ★**★这一句才是真正要问原厂的 (SoM 是否引出 boot pin)★** ★ |

★**零重复 key**: `--set-json` 整段替换前先 `--show` 核对条目数与 key, ★**不许因为替换而丢条目**★

### (2) ★**补登记 ISS-346 的结论到 sw.yaml** (`--add-claim` / `--add-answer`)

- key `iss346_q3_storage_tier_verdict_sw` (value = Q3 分档结论 + 板侧时点 + 音频轴「与存储轴互不依赖」一条)
- ★**只登记, 不新增拍板项, 不代老板拍**★

### (3) ★**零铜网 / 分级口径复核 (只核对, 不改)**

确认 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 里与 4 条 `SPI_*_BOOT` 相关的判定仍是【必需】 (★与 ISS-344 的分级口径一致★) ⇒ ★**不许改那个文件, 只把核对结论写进交卷页**★

### (4) ★**交卷页**

`HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md` —— ★B0~B7 七块齐全★ + ★页内引用路径逐个在盘 (MISS = 0)★ + ★**板指纹前后双证**★

---

## ★★纪律 (★一条不许破★) ★★

- ★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 必须逐字节不变)★
- ★**零落表** (不改网表 / 脚表 / BOM / 原理图 / 闸脚本)★
- 只写 `state/fragments/sw.yaml` (自己的分片) + 交卷页 + `logs/iss350/`
- ★**零外发** (★不许任何邮件 / 询价 / 问询 / 采购 —— 老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案
- 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标
- ★**不替老板拍板**★ (★音频做不做本单不判 / 不建议 / 不代拍★)
- 写分片只用 `state/frag_write.py`

## ★★必跑项 (交卷前) ★★

```bash
python3 state/merge.py                       # rc 必须 0
python3 state/gate_check.py                   # Q1 必须 18/18
python3 state/frag_write.py --agent sw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb        # 必须 611b869e13518c3c023fb178f91a0075
```

## ★★交卷物 ★★

交卷页 + `logs/iss350/` + sw.yaml 分片 (改 1 条措辞 + 登记 1~2 条) ⇒ ★**回 main 签收**★

★**参考**: `SW/STORAGE_CAPACITY_MATRIX.md` · `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md` (★ISS-346 交卷页 · §B7-2 就是本单题面的来源★) · `state/fragments/pm.yaml` 的 `iss346_q3_storage_tier_verdict_20261123` (★main 的裁定原文★)
