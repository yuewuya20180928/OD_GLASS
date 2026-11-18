# logs/iss313/ —— ISS-313 (mech-lead) 逐条取数命令 · 原始输出 · 改分片前后 md5

> **交卷人**: 结构总工 (mech-lead) 🔩 · **单号**: ISS-313 · **日期**: 2026-11-18
> ★本目录是本单的**原始证据留档**: 逐条取数命令 + 未加工的原始输出 + 改分片前后的 md5。
> ★交卷页 = `MECH/MECH_NEEDS_TRIAGE.md` · 交卷单 = `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` · 三者**同源**。

---

## 0 · 环境提示 (★本机已知事实★)

`/tmp` 是带 `usrquota` 的 tmpfs, 用户配额已打满 ⇒ 重定向到 `/tmp/x.log` 会得到 rc=120 + 0 字节空输出 (比红更坏)。
⇒ **本单所有临时目录与日志都指大盘**:

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss313_tmp
mkdir -p logs/iss313 tmp/iss313_tmp
```

★**不许** `rm -rf /tmp/*` (别的单正在建沙盒)。

---

## 1 · 文件索引

| 文件 | 内容 | 谁生成 |
|---|---|---|
| `iss313_data.py` | ★**唯一数据源**: 四类逐条分类 + 依据行 + 答复全文 + owner/一句话问法 | 手写 (本单) |
| `apply_iss313.py` | 应用器: 读分片 → 核对分类覆盖率 → 写分片 (走 `state/frag_write.py` 原子写) + 输出对账摘要 | 本单 |
| `gen_iss313_docs.py` | 文档生成器: 从同一数据源生成交卷页 + 交卷单 | 本单 |
| `mech.yaml.bak_pre_iss313` | 改分片**前**的 `state/fragments/mech.yaml` 副本 (md5 `f80056ae071880d9885d0034b3ab635d`) | `cp` |
| `mech.yaml.after_iss313` | 改分片**后**的副本 (md5 `285b8eae37658b5d845fdb76ea844a5e`) | `cp` |
| `_needs_dump.json` | 185 条 need 的逐条结构化 dump (key / to / waiting_on / item / due / decision) | python |
| `needs_full_dump.txt` | 185 条 need 的全文 dump (未截断) | python |
| `needs_read.txt` | 185 条 need 的逐条正文 (长条目截到 700 字) | python |
| `needs_listing.txt` | 185 条 need 的索引表 | python |
| `open_needs.txt` | 136 条**未闭合** need 的清单 + 四类归属 | python |
| `_need_status.json` | 每条 need 的闭合状态 (`by_answer` / `by_decision` / open) + `gate_inc` 标记 | python |
| `_iss313_apply_summary.json` | 本单应用结果摘要 (关/留/新答 + 改分片前后条数与 md5) | apply |
| `reciprocal_map.txt` | 185 条 key 与其它分片 `needs_from` 的同 key 重用情况 (共 5 条) | python |
| `evidence_A.txt` … `evidence_P.txt` | 逐项取证的**原始输出** (脚本口径 / 网表 / BOM / 决策记录 / 官网自查) | 见各文件头 |
| `gate_check_BEFORE.txt` | 改分片前的机检输出 | `state/gate_check.py` |
| `gate_check_AFTER.txt` | 改分片后的机检输出 | `state/gate_check.py` |
| `merge_after.txt` | 合并器输出 (改分片后) | `state/merge.py` |
| `md5_before_after.txt` | 改分片前后的 md5 对照 (板 / 闸脚本 / 分片) | `md5sum` |

---

## 2 · 逐条取数命令 (★全部可复现★)

### 2.1 分片现状与四类归属

```bash
export TMPDIR=$PWD/tmp/iss313_tmp
python3 - <<'EOF'
import yaml, collections
d = yaml.safe_load(open('state/fragments/mech.yaml'))
c = collections.Counter((n.get('waiting_on') or '(empty)') for n in d['needs_from'])
print('needs_from 总数:', len(d['needs_from']))
for k, v in c.most_common():
    print(' ', repr(k), v)
EOF
```

★**实测输出 (改分片前)**: `needs_from 总数: 185` · `(empty) 114` · `agent 34` · `boss 20` · `vendor 10` · `jbd 6` · `hw-lead 1`。
★**注意**: `waiting_on` 为空的 114 条, 合并器与门禁都按 `agent` 语义处理 (内部) ⇒ 真正的「内部未闭合」= 34 + 114 + 1。

### 2.2 闭合状态 (merge.py 口径: 被问方作答 / 老板 decision / 全局 decision key)

```bash
python3 - <<'EOF'
import yaml, sys
sys.path.insert(0, 'state')
from decision_truth import decision_keys
M = {'main':'pm.yaml','hw-lead':'hw.yaml','sw-lead':'sw.yaml','mech-lead':'mech.yaml'}
frs = {a: yaml.safe_load(open('state/fragments/'+f)) for a,f in M.items()}
dec = decision_keys(frs)
ans = {}
for a,d in frs.items():
    for x in (d.get('answers') or []):
        if x.get('key'): ans.setdefault(x['key'], []).append(a)
mech = frs['mech-lead']
closed = 0
for n in mech['needs_from']:
    k, to = n.get('key'), n.get('to')
    if to in ans.get(k, []) or k in dec or n.get('decision'):
        closed += 1
print('已闭合:', closed, ' / 未闭合:', len(mech['needs_from']) - closed)
EOF
```

★**实测输出 (改分片前)**: `已闭合: 49 / 未闭合: 136`。

### 2.3 官网自查 (★16 条外部依赖 ⇒ 零外发★)

```bash
# 逐条 web_search / web_fetch, 命中原文摘录在下方「§3 自查命中原文摘要」
```

### 2.4 机检前后对照

```bash
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb MECH/service_port_check.py state/fragments/mech.yaml
```

---

## 3 · 自查命中原文摘要 (★16 条外部依赖 · 零外发 ★)

| need key | 命中来源 | 关键原文 (摘) |
|---|---|---|
| `iss099_jchg_rfq` | Hirose FH12-10S-0.5SH(55) 官网/分销规格页 | `Current Rating 0.5A` · `FFC, FCB Thickness 0.30mm` · `Height Above Board 0.079" (2.00mm)` · `Pitch 0.020" (0.50mm)` · `Voltage Rating 50V` · `Mating Cycles 20` · `-40°C ~ 85°C` · `Zero Insertion Force (ZIF)` |
| `mech_mat_vendor_datasheet` (①VHB) | 3M VHB 5962 / 5962P 技术数据表 | `Thickness 1.6 mm ±10 %` · `Short Term Temperature Resistance 149 °C` · `Long Term Temperature Resistance 93 °C` · `90° Peel 39 N/cm` · `Dynamic Overlap Shear 550 kPa` · `Minimum Application Temperature 10 °C` · `Foam Density 590 kg/m³` |
| `mech_mat_vendor_datasheet` (②AA 3311) | Henkel LOCTITE AA 3311 产品页 | `ISO-10993 biocompatible` · `Wavelength for cure: UV / VIS` · `Viscosity 200-400 cP` · `>13 mm (0.51") depth of cure` · `1-part: no mixing required` |
| `mech_mat_anodize_process` / `mech_dfm_anodize_uniformity` | MIL-A-8625F | `the thickness of the coating shall not vary by more than +/- 20 percent for coatings up to 0.002 inches thick` · `Coatings over 0.002 inches shall not vary by more than +/- 0.0004 inches` · `Type III ... shall not be applied to aluminum alloys with a nominal copper content` |
| `mech_reltest_cell_samples` (Renata) | renata.com 锂聚合物电池页 | `ICP422339PR — Capacity 340 mAh / Thickness 4.6 mm / Width 23.5 mm / Length 40.5 mm` · `ICP582035PR-01 — Capacity 340 mAh / Thickness 6.4 mm / Width 20.5 mm / Length 37 mm` |
| `mech_reltest_cell_samples` / `iss091_cell_ir` (丰江) | battsysbattery.cn 软包聚合物电池 | `432243 · 3.7V · ≥420mAh · 4.3\22.0\43.5mm · 快充 40~60min · 脉冲放电 1~3A · 循环寿命 ≥500` (★无内阻项 ⇒ [0数据]★) |
| `jbd_waveguide_2d` / `iss017_waveguide_rainbow_metric` | jb-display.com | `Hummingbird Mini Ⅱ — 0.15 cc / 0.3 g / 60 mW` · `Hummingbird Ⅱ — 0.2 cc / 0.5 g / 95 mW` · `Hummingbird Ⅰ Polychrome Optical Module — 6000 nits / 30° FOV` · `彩虹效应抑制效率达 95%` · `全局亮度均匀性可提升至 >80%` · `色差 ΔE 降低至 0.02` · ★**2D 外形图 / 耦入区容差角 / 安装基准: 公开渠道无**★ |
| `jbd_dual_eye_module` / `jbd_optical_engine_dims` | pm.yaml 老板 decision | `visionox_inquiry_release` decision = 『作废, 不发 —— 老板 2026-11-04 09:5x 明确「视崖屏幕已经不用了」』 ⇒ 走鹃Ⅱ 前提作废 |
| `vendor_ars45_thermal_pad` | 老板政策 | `vendor_q19_boot_storage` decision = 『不再做任何邮件 / 供应商 / 原厂问询 ... 获取不到结果的 ... 自己去网上查找』+ 老板 10-29 00:49 跳过酷芯微 ⇒ 前提作废 |
| `mech_dfm_shrink_rate` | 行业通例 (ASTM D955-89) | `the molding shrinkage range of the ABS material is 0.29%-0.76%` + 各向异性 (流动向 vs 垂直流向不同) ⇒ 本域原用的 1.5% 假设偏保守 |
| `mech_dfm_mold_tolerance` | 行业通例 | 注塑 ±0.20~±0.30 (小件) / 压铸 ±0.20~±0.25 ⇒ 本单取值方向合理 |
| `mech_mat_waveguide_uv_cosmetic` | — | 波导/镀膜 UV 与化妆品耐受: 公开渠道查不到 ⇒ `[0数据]` ⇒ 降级方案 (硅胶侧承担相容性 + 涂层侧实测) |
| `iss099_fpc_vendor_capability` | 行业通例 | 分段铜厚 = 常见工艺但无统一公开规格; 0.5mm pitch 常规最小线宽/间隙 0.075-0.10mm ⇒ 0.40/0.10 属常规边界 |

---

## 4 · 改分片前后的 md5

| 文件 | 改前 | 改后 | 说明 |
|---|---|---|---|
| `state/fragments/mech.yaml` | `f80056ae071880d9885d0034b3ab635d` | `285b8eae37658b5d845fdb76ea844a5e` | ★本单**唯一**改动的分片 (经 `state/frag_write.py` 原子写) |
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**逐字节不变** (零写板) |
| `HW/PCB/demo_mainboard.kicad_pcb` (mtime) | `2026-11-06 07:07:17` | `2026-11-06 07:07:17` | ★**逐字节不变** |
| `MECH/service_port_check.py` | `db58ff6a2afc28b8bf517e3c57c56bc1` | `db58ff6a2afc28b8bf517e3c57c56bc1` | ★**逐字节不变** (零改闸) |
| `state/gate_check.py` / `state/merge.py` | 未改 | 未改 | ★**零改闸** |

★**本单只写了 4 处**: `MECH/MECH_NEEDS_TRIAGE.md` (新建) · `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` (新建) · `logs/iss313/` (新建) · `state/fragments/mech.yaml` (经 frag_write.py 原子写)。
★**没写**: 任何既有 .md 正文 · 任何闸脚本 · `HW/` `SW/` 任何文件 · `state/issue_log.yaml` · `hw.yaml` / `sw.yaml` / `pm.yaml`。
★**零外发**: 本单不发邮件 / 不询价 / 不问询 / 不采购 / 不联系任何厂商; `state/outbox/` 下的草稿 (含 `j_chg_rfq.md` / `jbd_query.md` / `visionox_display_inquiry.md`) **一律不发, 只留档**。

---

## 5 · 机检前后 (★原样输出见 `gate_check_BEFORE.txt` / `gate_check_AFTER.txt`★)

| 指标 | 改分片前 | 改分片后 |
|---|---|---|
| `mech-lead` 缺口清单条数 | 108 | **62** |
| `mech-lead` needs_total | 185 | 121 |
| `mech-lead` 被答 | 43 | 43 |
| 全局 等外部 | 70 | **49** |
| 全局 等另一个总工 | 341 | **306** |
| 自闭合 | 0 | **0** |
| Q1 齐备率 | 18/18 | **18/18** |
| merge rc / gate rc | 0 / 0 | **0 / 0** |
