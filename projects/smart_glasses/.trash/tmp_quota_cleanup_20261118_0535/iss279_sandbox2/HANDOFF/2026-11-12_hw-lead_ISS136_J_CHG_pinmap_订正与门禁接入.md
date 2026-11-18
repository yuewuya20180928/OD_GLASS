# [hw-lead→PM] ISS-136 · J_CHG 跨铰链 pin map 订正 + 把 `check_bq25896_pinout.py` 接进 `gate_check` 门禁链

> 日期: 2026-11-12 00:2x · 承接: ISS-136 (owner main → hw-lead, status=fixing)
> ★**本单的核心不是"改两行字", 是把一个"一直是绿的假象"变成**真闸**。**

---

## B1 结论摘要

**结论: 全部做完, 通过。** 三方口径自己复算了一遍 (不照抄题单判定), 结论与题单一致, 但**根因比题单说的更深**:

| # | 交付项 | 结果 |
|---|---|---|
| ① | `HW/CHARGE_BOARD_SPEC.md` §5.2 的 J_CHG pin map 表 ⇒ 订正到与网表一致 | ✅ 只改了这张表 + 加一条订正注记 |
| ② | `HW/check_bq25896_pinout.py` 里硬编的 `spec_proposal` ⇒ 与同一真源一致 | ✅ 已改; **且把 ⑦ 从"比快照"改成"实读规格表"** |
| ③ | 该脚本接进 `state/gate_check.py` 门禁链 | ✅ 新增【Q6 硬件真源闸】; **闸红 ⇒ gate_check rc=1** |
| ③' | 反向用例 (证明它真在读规格/网表) | ✅ 副本上把规格表改回旧口径 ⇒ rc=1; 恢复 ⇒ rc=0 |

★★**比题单多挖出来的两层 (这才是"方法论问题"的实体)** ★★

**第一层 —— 题单说的"接进 gate_check"只是症状, 根因是**检查项 ⑦ 根本没读规格文件**:
旧版 ⑦ 比的是「**脚本里写死的快照** vs 网表」⇒ **规格 §5.2 改成任何样子它都不会红**。
[实测] 我把旧版 ⑦ 的判定逻辑单独跑了一遍证明: 旧判定只由 (快照, 网表) 两个输入决定, **规格表改了它毫无反应** ⇒
它当时报的那句"规格 §5.2 提案 == 网表实际"**是句假话** —— 名义上查三方, 实际只查了两方。
⇒ 所以我只对齐快照 (照题单做) 是**修不好**的: 规格表明天再漂一次, 脚本照样绿。
⇒ **本单把 ⑦ 改成实读 `CHARGE_BOARD_SPEC.md` §5.2 表逐脚对拍网表** ⇒ 这才叫真闸。

**第二层 —— 旧 ⑦ 还有第二个假象**: `net_map = {p: sorted(v)[0] for p, v in ...}` ⇒
**同一个脚挂两个网时它静默取一个** (按字典序) ⇒ 冲突被吞掉, 脚越多越靠后越容易被吃掉。
⇒ 本单新增 **⑦a (同脚多网冲突)**, 一旦同脚多网立刻红。

---

## B2 验收标准自评

| # | 验收标准 | 自评 | 依据 |
|---|---|---|---|
| ① | 规格 §5.2 表 == 网表 | ✅ **通过** | 10 脚逐脚相等 (`pin1/2=BAT_CHG, 3/4=GND, 5=CHG_STAT, 6=PWR_GOOD, 7=NC, 8=TS_BAT, 9/10=HINGE_RSV`) |
| ② | 脚本硬编快照 == 网表 | ✅ **通过** | ⑦b 实测通过 |
| ③ | `check_bq25896_pinout.py` rc=0 | ✅ **通过** | rc=0 (10/10 检查项 PASS) |
| ④ | 接进 `gate_check` 后 gate_check 仍 rc=0 且 Q1 18/18 | ✅ **通过** | rc=0, Q1 18/18, 【Q6 硬件真源闸】✅ 通过 |
| ⑤ | `state/merge.py` rc=0 | ✅ **通过** | rc=0, 产出 177, **冲突 0** (新增 need/artifact 未引入冲突) |
| ⑥ | 反向用例: 规格表改回旧口径 ⇒ 脚本变红 | ✅ **通过** | rc=1, **且只有 ⑦ 一项 FAIL** (其余 9 项仍 PASS ⇒ 精确定位到漂移点) |
| ⑦ | 反向用例: 恢复 ⇒ 回 rc=0 | ✅ **通过** | rc=0, ⑦/⑦a/⑦b 全 PASS |
| ⑧ | 网表 / PCB md5 一字未变 | ✅ **通过** | `c78f991283cc82d56c8e3dd31657c785` / `611b869e13518c3c023fb178f91a0075` |
| ⑨ | 只改允许的文件 | ✅ **通过** | 见 B6 改动清单; `HW/netlist_v1.csv` / `netlist_v1_pins.csv` / `PCB/*` / `state/gen_*.py` / `PROJECT_TRACKER.md` / `state/issue_log.yaml` **一字未动** |
| ⑩ | 门禁**真能变红** (不是只打印一行) | ✅ **通过** | [实测] 全树副本里把 pin7 改回 `VBUS_DET` ⇒ `gate_check` 【Q6】❌ 红了 + 进缺口清单 + **rc=1** ⇒ 不是装饰 |

★**未验 / 不在本单范围 (不是"通过", 是"没做")**: 本单**没有**动 §5.1 过铰链线表、§7 的 P10 csv 镜像块、
ISS-112 那张三方口径对照表 —— 三处仍带旧口径, 已登记 `needs_from` 转 main 裁决 (见 B5)。

---

## B3 证据分级

| 结论 | 分级 | 依据 |
|---|---|---|
| 网表 J_CHG 每脚实际挂的网 (10 脚) | **[实测]** | 直接解析 `HW/netlist_v1.csv` 全表, `node1`/`node2` 两列都扫, 逐脚统计 distinct net |
| 规格 §5.2 表 (旧) 与网表差 6 脚 | **[实测]** | 独立第二实现 `MECH/cross_review_check.py` C-4 同样报 6 处冲突 (pin5/6/7/8/9/10) ⇒ 双方互证 |
| pin7 由 `PWR_GOOD` 改 `NC` | **[实测]** | 网表第 433 行: `P9,NC,J_CHG pin7,NC,...` + note "★2026-11-04: J_CHG pin7 原走跨铰链 VBUS_DET ⇒ demo 板改本地分压 ⇒ 本脚预留不接"; 另见 `state/gen_netlist.py:1441` 同源生成器 |
| pin10 由 `TS_RTN` 改 `HINGE_RSV` | **[实测]** | 网表第 21 行 net 字段 = `HINGE_RSV` (DNP); `TS_RTN` 这个网名**在全网表 0 次出现**; `state/_patch_netlist_pins2.py` 明确删了 `TS_RTN ↔ J_CHG pin10` 那行 ("跨铰链残留") |
| BQ25896 24 脚 pinout (①~⑥) | **[官方]** | TI SLUSC76C §7 Pin Functions, 逐脚抄录 |
| 旧 ⑦ 的判定输入只有 (快照, 网表) | **[实测]** | 把旧判定逻辑单独跑, 换掉规格表内容后结论不变 (见 B6 复现命令 ④) |
| 改网表会连带影响哪些文件 | **[推算]** | `state/gen_netlist.py` 是网表生成器 ⇒ 改网表须同改生成器, 否则下次重跑被覆盖 (本单未改网表, 故不涉及) |

---

## B4 接口取值声明

- **`j_chg_pin_map` (J_CHG 跨铰链 10p pin map)** — 我方 (hw-lead) 取值:
  `1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=NC,8=TS_BAT,9/10=HINGE_RSV`
  - 依据: `HW/netlist_v1.csv` 投板真源, 逐脚实读 [实测]
  - ★**与结构侧现有 `interface_claims` (`mech.yaml`: `7=VBUS_DET, 8=TS, 9=RSV, 10=TS_RTN`) 不一致** ⇒
    **我方按网表取值, 结构侧那 4 脚需同步** (已登记 needs_from 转 main, 不由我单方面改别人的分片)。
- **`hw_pinout_gate` (门禁链新增一项)** — 我方 (hw-lead) 取值:
  `gate_check.py` 新增【Q6 硬件真源闸】, 跑 `HW/check_bq25896_pinout.py`, 闸红 ⇒ `gate_check` rc=1 + 进缺口清单。
  - 依据: ISS-136 派活"门禁脚本必须进 gate_check 链, 否则等于没有" [实测]
- **本单未新增任何硬件接口取值** (pin map 是**订正**已有取值, 不是新提一个)。

---

## B5 未决项与卡点

1. **★需要 main 裁决 (已登记 `needs_from` key=`iss136_spec_residual_sections_sync`)**: 本单**只**改 §5.2 那张 pin map 表
   (边界要求), 但 §5.2 之外**还有三处带旧口径**, 建议一并订正, 否则同一份文件里仍有两套口径:
   - `HW/CHARGE_BOARD_SPEC.md` §5.1 过铰链线表: 第 3/4/5/8/9 行仍写 `pin8=VBUS_DET` / `pin6=CHG_STAT` / `pin7=PWR_GOOD` / `pin5=TS` / `pin9-10=I2C`
   - §7 的 P10 csv 镜像块: 同样带旧口径
   - ISS-112 那张三方口径对照表 (2026-10-29 历史快照): 其"网表实际"列已过期 —— 我已在 §5.2 加注记标明它是历史快照, **但未改它的表格内容** (超出本单边界)
2. **★ISS-136 的 issue 状态我没动** (`fixing`) —— 边界明写"改 issue 状态是 main 的活", 等 main 收口。
3. **结构侧 `interface_claims` 的 4 脚旧值** (`7=VBUS_DET / 8=TS / 9=RSV / 10=TS_RTN`) 我**没有**代改 mech-lead 的分片 ——
   已转 main。若 main 认为该由我方登记 hw-lead 侧新 claim, 我可补 (本单已登记 hw.yaml 的 needs_from + 2 条 artifact)。
4. **无阻塞项**: 本单 4 项验收全过, 无待裁决才能交付的内容。

---

## B6 自证复现命令

```bash
cd projects/smart_glasses

# ① 硬件闸本体 (★必须 rc=0; 改前是 rc=1)
python3 HW/check_bq25896_pinout.py ; echo "rc=$?"

# ② 门禁链 (★必须 rc=0 且 Q1 18/18)
python3 state/gate_check.py 2>&1 | grep -E "Q1 |Q6|硬件真源闸" ; echo "rc=${PIPESTATUS[0]}"

# ③ 状态源 (★必须 rc=0)
python3 state/merge.py ; echo "rc=$?"

# ④ md5 对拍 (★必须一字未变)
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb

# ⑤ 反向用例: 副本上把规格表改回旧口径 ⇒ 必须变红; 恢复 ⇒ 回 rc=0
rm -rf /tmp/iss136_rev && mkdir -p /tmp/iss136_rev/HW /tmp/iss136_rev/state
cp HW/check_bq25896_pinout.py HW/CHARGE_BOARD_SPEC.md HW/netlist_v1.csv HW/netlist_v1.net /tmp/iss136_rev/HW/
cp state/p10_rows.json /tmp/iss136_rev/state/
cd /tmp/iss136_rev
python3 - <<'EOF'
p='HW/CHARGE_BOARD_SPEC.md'; t=open(p,encoding='utf-8').read()
t2=t.replace("| pin7 | `NC` |","| pin7 | `VBUS_DET` |").replace("| pin10 | `HINGE_RSV` |","| pin10 | `TS_RTN` |")
assert t2!=t; open(p,'w',encoding='utf-8').write(t2)
EOF
python3 HW/check_bq25896_pinout.py 2>&1 | grep -E "^\s+\[(PASS|FAIL)\]" ; echo "★期望 rc≠0: ${PIPESTATUS[0]}"
cp <项目>/HW/CHARGE_BOARD_SPEC.md /tmp/iss136_rev/HW/    # 恢复
python3 HW/check_bq25896_pinout.py >/dev/null 2>&1 ; echo "★期望 rc=0: $?"
```

**★门禁真能变红的额外证据** (全树副本, 不是只改脚本):

```bash
cp -r projects/smart_glasses /tmp/gate_rev && cd /tmp/gate_rev
python3 - <<'EOF'
p='HW/CHARGE_BOARD_SPEC.md'; t=open(p,encoding='utf-8').read()
open(p,'w',encoding='utf-8').write(t.replace("| pin7 | `NC` |","| pin7 | `VBUS_DET` |"))
EOF
python3 state/gate_check.py 2>&1 | grep -E "Q1 |Q6|硬件闸红" ; echo "★期望 rc=1: ${PIPESTATUS[0]}"
```

---

## 附: 改动清单 (可逐条对拍)

| 文件 | 改了什么 |
|---|---|
| `HW/CHARGE_BOARD_SPEC.md` | **仅** §5.2 的 pin map 表 10 行 + 其后"与现行 pin map 的差异"段 + 一条 ★★2026-11-12 订正注记。**§5.1 / §5.3 / §7 / ISS-112 对照表 一字未动** |
| `HW/check_bq25896_pinout.py` | ① 新增 `scan_spec_jchg_pinmap()` (实读 §5.2 表) ② 检查项 ⑦ 改为"规格实读 vs 网表", 新增 ⑦a (同脚多网) / ⑦b (快照对齐) ③ `spec_proposal` 提为模块级 `SPEC_PROPOSAL` 并对齐网表 ④ `--json` 输出的 `j_chg_spec_p10_block` 改为 `j_chg_spec_52_table` |
| `state/gate_check.py` | 新增 `run_hw_pinout_gate()` + 【Q6 硬件真源闸】+ 缺口清单登记 + **闸红 ⇒ rc=1** (fail-closed: 脚本缺失/超时/跑不起来一律当红) |
| `state/fragments/hw.yaml` | 经 `state/frag_write.py` 新增 1 条 `needs_from` + 2 条 `artifact` (只增不删, 未动别人 key) |
| `HANDOFF/2026-11-12_hw-lead_ISS136_J_CHG_pinmap_订正与门禁接入.md` | 本文件 |

★**未动**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` ·
`state/gen_*.py` · `PROJECT_TRACKER.md` §0 · `state/issue_log.yaml` · 别人的分片。
★**外部无联系**: 本单未联系任何供应商/原厂 (外发一律经项目总工)。
