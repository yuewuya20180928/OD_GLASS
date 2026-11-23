# 「板那一趟」腿 B（网表节点具名 200 条）对 SW 侧判据链的影响面

★**单号**: ISS-370 · sw-lead · 2026-11-23 ★
★**类别**: 纯分析 + 作业包 + 新建闸 + 沙盒预演 · **零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发** ★
★**一句话**: ★**腿 B 会把 SW 侧 5 道闸打红, 其中 13 条是【语义破坏】(取链层崩) + 3 条是【落表义务】(合法落表即解) ⇒ 这一趟本来就必须做腿 B ⇒ 不提前查清, 开工当天 SW 门禁当场红 ⇒ 要么硬改闸(把红项调没) 要么板 md5 变第二次(违「板只改一次」)** ★

★**本单的核心结论 (★本机实跑·不是转述★)**:
★**① 腿 B 真落盘那天, SW 侧 `timing_check.py` 的红数不是 15, 是 16** ★
★**② 第 16 条是 `--netlist` 沙盒【结构性看不见】的那一条** (★它直接读【盘上真源】·不读 `--netlist` 参数★) ★
★**③ 13 条语义红的根因不是「改名会坏」, 是【取中点网靠精确字符串相等】⇒ 同批加一层归一化即可全回绿, 判据方向一条不用改** ★
★**④ 补丁只回绿语义红, 3 条落表义务红必须【合法落表】才解 ⇒ 落表那一件是【跨域·hw-lead 的地界】** ★

---

<!-- ISS370-IMPACT:BEGIN -->
```json
{
  "schema": "iss370-legb-sw-impact/1",
  "generated": "2026-11-23 CONT1 sw-lead",
  "counts": {
    "changed_cells": 196,
    "changed_columns": ["node1", "node2"],
    "node1_cells": 120,
    "node2_cells": 76,
    "rows_before": 513,
    "rows_after": 517,
    "rows_delta": 4
  },
  "red_count": 15,
  "reds": [
    {"no": 1,  "text": "ADC 源阻抗 = 37.5k (★ISS-291: 判决对象 = BAT_DET 链 → pin38 SARADC_VIN5★)", "class": "语义破坏", "fix": "在 resolve_chain_landing() 的节点比较前加一层归一化 (剥掉节点串尾部的 ' pinN' 后缀), 判据方向不变", "gate": "SW/tools/timing_check.py", "selfcheck": "落表仿真 rc=1 且 SELFTEST 由 69/85 回 82/85, 本条由 FAIL 转 PASS"},
    {"no": 2,  "text": "ADC tau = 3.75ms (★ISS-291 口径★)", "class": "语义破坏", "fix": "同上 (tau 由链上的 R_th 与 C 实读, 链取不到 ⇒ 无值)", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 3,  "text": "ADC 12bit 建立 33.8ms ≤ 300ms 红线 (★ISS-291 口径: 老口径的 451ms 是**假红**★)", "class": "语义破坏", "fix": "同上", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 4,  "text": "ADC 漏电偏移 37.5mV ≤ 0.4V 红线 (★ISS-291 口径: 老口径的 0.50V 是**假红**★)", "class": "语义破坏", "fix": "同上", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 5,  "text": "网表锚点: 现行网表 = 513 数据行 (行数不许变)", "class": "落表义务", "fix": "腿 B 补行 4 条 ⇒ 数据行 513→517 ⇒ 该判据的 513 是【落表前的行数锚点】; 合法落表时把它同步到 517 (判据方向不许变, 阈值不许调松)", "gate": "SW/tools/timing_check.py", "selfcheck": "落表后该条由 FAIL 转 PASS (★该条只出现在【补行】变体里, 不出现在【只改名】变体里★)"},
    {"no": 6,  "text": "网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)", "class": "落表义务", "fix": "腿 B 网表 md5 = 724f0bf71cb7ec6c74e389cf9cd8d3fe 未登记在落表台账链上; 落表那一跳把新 md5 登记进链 ⇒ 该条自动绿 (判据方向一个字不改)", "gate": "SW/tools/timing_check.py", "selfcheck": "落表后该条由 FAIL 转 PASS (★该条在【只改名】与【只补行】两个变体里都出现★)"},
    {"no": 7,  "text": "F4' 实读: ADC 判决对象 = BAT_DET 链 (落点 J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域); BAT_DET 三颗必装", "class": "语义破坏", "fix": "同上 (落点取不到 ⇒ 判决对象判不出 BAT_DET 链)", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 8,  "text": "F4 实读: 漏电偏移 37.5mV = 2.1% FS ⇒ 与网表 L182 note 写死的数**逐字对上** (口径同源)", "class": "语义破坏", "fix": "同上", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 9,  "text": "F4 实读: 判决源 = SoM 脚表 signal 列 (落点判 SAR-ADC), 取链模式 = by_landing_pin", "class": "语义破坏", "fix": "同上 (active_chain_pin 取不到 ⇒ 判决源判不出)", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 10, "text": "F4 实读: ADC 节点 @4.2V = 1.575V ≤ abs-max 1.98V (FS 利用率 87.5%)", "class": "语义破坏", "fix": "同上 (节点电压由分压实读, 链取不到 ⇒ 无值)", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 11, "text": "F4D 实读: VBUS_DET_D 落点 = J_SOM_P1 pin100 = USB_DRD1_VBUSDET (数字脚 ⇒ 不进 ADC 判据)", "class": "语义破坏", "fix": "同上 (VBUS_DET_D 链同样被腿 B 改名 ⇒ 它的落点也取不到)", "gate": "SW/tools/timing_check.py", "selfcheck": "同上, 本条由 FAIL 转 PASS"},
    {"no": 12, "text": "REV-12 反向: 把满量程 V_DET_FS 改回 3.3 (老口径) ⇒ 满量程/口径同源判据必须变红", "class": "反向用例", "fix": "派生红: 该反向用例断言【未改动的正向判据必须先绿】, 正向判据被腿 B 打塌 ⇒ 断言的前半句不成立 ⇒ 连带红; 修好第 1 件后自动回绿", "gate": "SW/tools/timing_check.py", "selfcheck": "落表仿真+补丁后本条由 FAIL 转 PASS (★反向用例本身一个字不许改★)"},
    {"no": 13, "text": "REV-13 反向: 把取链规则改回「元组第一条」⇒ 判决对象判据必须变红 (不许悄悄换回错对象)", "class": "反向用例", "fix": "派生红 (同第 12 条); 修好第 1 件后自动回绿", "gate": "SW/tools/timing_check.py", "selfcheck": "落表仿真+补丁后本条由 FAIL 转 PASS"},
    {"no": 14, "text": "REV-14 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ 「ADC 输入悬空」判据必须变红", "class": "反向用例", "fix": "派生红 (同第 12 条); 修好第 1 件后自动回绿", "gate": "SW/tools/timing_check.py", "selfcheck": "落表仿真+补丁后本条由 FAIL 转 PASS"},
    {"no": 15, "text": "REV-15 反向: 把 BAT_DET 的下臂 60k 改成 100k ⇒ @4.2V 节点 2.1V > 1.98V abs-max ⇒ 过压判据必须变红", "class": "反向用例", "fix": "派生红 (同第 12 条); 修好第 1 件后自动回绿", "gate": "SW/tools/timing_check.py", "selfcheck": "落表仿真+补丁后本条由 FAIL 转 PASS"}
  ],
  "landing_only_reds": [
    {"no": 16, "text": "网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)", "class": "落表义务", "fix": "该判据直接读【盘上真源】(timing_check.py L325: disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)) ⇒ --netlist 覆盖改不到它; 腿 B 真落盘且未落表 ⇒ 盘上 md5 724f0bf71cb7 ≠ 台账链头 6aee500e60ba ⇒ 红; 落表那一跳把新 md5 登记进链 ⇒ 自动绿", "gate": "SW/tools/timing_check.py", "selfcheck": "落表后该条由 FAIL 转 PASS"}
  ],
  "samebatch": [
    {"no": 1, "file": "SW/tools/timing_check.py", "owner": "SW 域 (我)", "timing": "必须同批", "kind": "脚本", "fix": "在 resolve_chain_landing() 里把 node1/node2 两行改成 _node_ref(x.get('node1')) / _node_ref(x.get('node2')), 并新增 _node_ref(s) = re.sub(r'\\s+pin\\d+\\s*$', '', (s or '').strip()); 只比位号, 脚号本就不是这条判据的输入, 判据方向一个字不改", "readback": "改前 rc=1 · SELFTEST 69/85 (16 红) ⇒ 改后 rc=1 · SELFTEST 82/85 (只剩 3 条落表义务红, 13 条语义红全回绿)", "evidence": "[实测]"},
    {"no": 2, "file": "SW/tools/check_timing_review_adc_sync.py", "owner": "SW 域 (我)", "timing": "必须同批", "kind": "脚本 (★本单结论: 不需要改·随第 1 件自动回绿·但必须同批复跑自证★)", "fix": "一个字不许改; 它读 timing_check 的 ADC 字段, 腿 B 下 fail-closed 报 rc=2 (字段全 None), 第 1 件修好后自动 rc=0 (29/29)", "readback": "改前 rc=2 ⇒ 改后 rc=0 (29/29 项通过)", "evidence": "[实测]"},
    {"no": 3, "file": "HW/netlist_v1.csv (真源落表)", "owner": "跨域 · 不是 SW 的域 · 只给改法", "timing": "必须同批", "kind": "数据", "fix": "腿 B 那一跳由 hw-lead 把改名 196 格 + 补行 4 条落到 HW/netlist_v1.csv; SW 侧只给改法, 不碰 HW/ 下任何文件", "readback": "落表后盘上 md5 由 6aee500e60ba 变 724f0bf71cb7 ⇒ SW 侧第 3/4/5 件自动解锁", "evidence": "[实测]"},
    {"no": 4, "file": "HW/SCHEMATIC_LANDING_V1_LANDED.md (落表台账)", "owner": "跨域 · 不是 SW 的域 · 只给改法", "timing": "必须同批", "kind": "数据", "fix": "落表那一跳把腿 B 新 md5 724f0bf71cb7ec6c74e389cf9cd8d3fe 登记进网表落表链 (链头前移) + 填落表单号; SW 侧一个字不改", "readback": "落表前: md5 锚点红 + 三方对账红 + R6 红 + W6 红 ⇒ 落表后四条同时绿 (实测机制: 链头前移 ⇒ md5 ∈ 登记状态)", "evidence": "[实测]"},
    {"no": 5, "file": "SW/SW_MD5_BASELINE_LEDGER.md (§1 锚点块)", "owner": "SW 域 (我)", "timing": "必须同批", "kind": "数据", "fix": "锚点块里的 HW/netlist_v1.csv 那条重锚到落表后的新 md5 + 落表单号 (H-1 重锚机制); prev_md5 保留旧值作历史留痕; 不许手改 md5 凑绿", "readback": "落表前: 锚点副本 md5 链头对不上 ⇒ 三方对账红 ⇒ 落表后绿", "evidence": "[实测]"},
    {"no": 6, "file": "state/issue_log.yaml (落表留痕)", "owner": "跨域 · 不是 SW 的域 · 只给改法", "timing": "必须同批", "kind": "数据", "fix": "落表那一跳在 issue_log 里留【文件名 + 新 md5】的落表留痕; 留痕缺失时 check_landing_trace_obligation.py 会红", "readback": "本单实测: 留痕闸在腿 B 落盘但未留痕时 rc=0 (它只判留痕条目在不在, 不判盘上 md5) ⇒ 落表那一跳必须补一条留痕", "evidence": "[实测]"},
    {"no": 7, "file": "SW/tools/check_demo_panel_spec.py (R6 三方对账)", "owner": "跨域 · 不是 SW 的域 · 只给改法", "timing": "必须同批", "kind": "脚本 (★本单结论: 不需要改·落表后自动绿·但必须同批复跑自证★)", "fix": "一个字不许改; R6 判【盘上真源 md5 vs 落表台账链头】⇒ 腿 B 落盘未落表 ⇒ 红 ⇒ 落表后链头前移 ⇒ 自动绿", "readback": "改前 rc=1 (R6 台账链红) ⇒ 落表后 rc=0", "evidence": "[实测]"},
    {"no": 8, "file": "SW/tools/check_onepass_sw_sync.py (W6 受保护 5 件)", "owner": "跨域 · 不是 SW 的域 · 只给改法", "timing": "必须同批", "kind": "脚本 (★本单结论: 不需要改·落表后自动绿·但必须同批复跑自证★)", "fix": "一个字不许改; W6 判【盘上 md5 在落表台账里查得到 + 盘上 md5 == 台账链头】⇒ 腿 B 落盘未落表 ⇒ 两条子错 ⇒ 落表后自动绿", "readback": "改前 rc=1 (W6 两条子错) ⇒ 落表后 rc=0", "evidence": "[实测]"},
    {"no": 9, "file": "HW/netlist_v1_pins.csv (脚表)", "owner": "跨域 · 不是 SW 的域 · 只给改法", "timing": "可板后补", "kind": "数据", "fix": "腿 B 补的 4 条行的节点在脚表里【本来就有】(补行 note 自证: 脚表 netlist_v1_pins.csv 已有该脚) ⇒ 脚表一个字不许改; mtime 被顶到 2026-11-23 19:19:15 是别的事留下的假象, 内容 md5 仍等于基线", "readback": "本单实测: 脚表 md5 = 9174309df1ec9411ac8e8d9e80ee386a (与基线逐字节相同) ⇒ 零改动成立", "evidence": "[实测]"},
    {"no": 10, "file": "SW/tools/check_onepass_legb_sw_impact.py (本单新建闸)", "owner": "SW 域 (我)", "timing": "可板后补", "kind": "脚本", "fix": "本单已交; ★零挂链★ —— 不写进 state/gate_check.py (挂链是 main 的机制地界, ISS-330/333/362 同款)", "readback": "裸跑 rc=0 · --selftest 9/9 PASS", "evidence": "[实测]"}
  ],
  "degradation": [
    {"item": 1, "way": "沙盒验证法", "text": "若那一趟来不及加归一化层, 可退到【沙盒验证法】: 把腿 B 网表喂进 timing_check --netlist, 人工读出 13 条语义红的原文, 但★这一条只是把红项登记下来, 不等于闸绿★ ⇒ 门禁链仍是红的, 不许当解法"},
    {"item": 2, "way": "沙盒验证法", "text": "改设计路径绕开: 若不许改 timing_check.py, 唯一另一条路是【腿 B 的节点串保持裸位号】(即不做具名), 但★那等于取消腿 B 这一跳★ ⇒ 属设计路径回退, 代价写在 §5"},
    {"item": 3, "way": "沙盒验证法", "text": "落表那一跳若排不进同一窗口, 可退到【沙盒验证法】: 先在 tmp/iss370_sbx/ 的镜像根里落表验一遍 (本单已建 land_root/land_root_fix 两个镜像根), 但★落表不许用沙盒代替真落表★"},
    {"item": 4, "way": "官网参数可满足的等效件", "text": "落表台账链前移这一件没有等效件可替 (它是唯一权威源); 可退到【沙盒验证法】先验链头前移后四条红同时绿 (本单已实测机制成立)"},
    {"item": 5, "way": "沙盒验证法", "text": "锚点重锚可退到【沙盒验证法】: 镜像根里改锚点副本后跑三方对账, 但★不许手改 md5 凑绿★ —— 锚点 md5 必须在台账链上且落表单号要对得上"},
    {"item": 6, "way": "沙盒验证法", "text": "留痕可退到【沙盒验证法】: 镜像根的 state/issue_log.yaml 副本里补一条留痕再跑 check_landing_trace_obligation.py"},
    {"item": 7, "way": "沙盒验证法", "text": "R6 没有等效件; 可退到【沙盒验证法】确认落表后链头前移 ⇒ R6 自动绿, 不许改 R6 判据"},
    {"item": 8, "way": "沙盒验证法", "text": "W6 同 R6: 不许改 W6 判据; 落表后自动绿"},
    {"item": 9, "way": "改设计路径绕开", "text": "脚表零改动; 若哪天真要改脚表, 等效件路径 = 改脚表落表链 (跨域) —— ★本单实测脚表一个字不用动★"},
    {"item": 10, "way": "沙盒验证法", "text": "新闸挂链与否归 main; 本单只保证闸本身裸跑 rc=0 + selftest 全过, 挂不挂链不影响闸的正确性"}
  ],
  "protected": {
    "board_md5": "611b869e13518c3c023fb178f91a0075",
    "netlist_md5": "6aee500e60ba0732f83a9cf557ba90ab",
    "pins_md5": "9174309df1ec9411ac8e8d9e80ee386a",
    "bom_md5": "5b9993992405904a60ac96a020b375d8"
  }
}
```
<!-- ISS370-IMPACT:END -->

---

## §0 · 口径与读数 (★每个数字都能被 §6 的某条命令复现★)

★**读数口径**: ★**本单所有读数 = 本单自己 2026-11-23 19:4x~20:0x 本机实跑** ★
★**main 17:4x~17:5x 的读数本单独立复现过, 一致** ⇒ 但**本单页里写的每个数字都是本单自己跑出来的**, 留证在 `logs/iss370/2*.txt` ★

### §0-1 · 腿 B 是什么 (★只读·没重做★)

| 项 | 值 | 来源 |
|---|---|---|
| 指令全清单 | `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` §2.2 (200 条 = 改名 196 + 补行 4) | ★只 grep 了要的行, 176 KB 未整读 ★ |
| 腿 B 网表副本 | `tmp/iss364_sbx/netlist_v1_legB.csv` · 145,179 B · md5 `724f0bf71cb7ec6c74e389cf9cd8d3fe` | 盘上实读 |
| 改动格数 | ★**196** ★ (node1 **120** 格 + node2 **76** 格) | ★本单自己逐格比对 ★`logs/iss370/30_CONT1_g1_numbers.txt` |
| 改动栏 | ★**⊆ {node1, node2}** ★ (实际改动栏集合 = `['node1','node2']`) | 同上 |
| 未动栏 | `net` / `ref` / `value` / `type` / `dnp` / `board` / `footprint` / `conn_id` / `note` … **一格未动** | 同上 |
| 行数 | ★**513 → 517** ★ (Δ = **+4** = 补行 4 条) | 同上 |

★**⇒ 腿 B 的全部破坏面只有两个来源: ① `node1`/`node2` 两栏的「裸位号 → 具名脚」改名 ② 数据行 +4** ★

### §0-2 · ★**根因 (★本单读源码定位·不是转述★)** ★

★**`SW/tools/timing_check.py` L1013 `resolve_chain_landing()` · 判中点网的那三行 (★逐字★)**: ★

```python
def resolve_chain_landing(nl: Netlist, r_top: str, r_bot: str) -> dict:
    ...
    for x in nl.rows:
        a = (x.get("node1") or "").strip()
        b = (x.get("node2") or "").strip()
        if {a, b} == {r_top, r_bot}:          # ★★ L1026 ★★ 精确字符串相等 ★★
```

★**腿 B 前后的 BAT_DET 链行 (★本单实读两行网表★)**:

| | 网表 L181 `net=BAT_DET` |
|---|---|
| 基线 | `node1=R_BAT_DET_1` · `node2=R_BAT_DET_2` ⇒ `{R_BAT_DET_1, R_BAT_DET_2} == {r_top, r_bot}` ⇒ **成立** ⇒ `mid_net=BAT_DET` |
| 腿 B | `node1=R_BAT_DET_1 pin1` · `node2=R_BAT_DET_2 pin1` ⇒ **不成立** ⇒ `mid_net=""` |

★**⇒ 后果链 (★本单用 `--json` 实读, 不是推的★)**:
`mid_net=""` ⇒ `classify_landing()` 返回 `UNKNOWN` ⇒ **两条链 (BAT_DET + VBUS_DET_D) 都没有落点** ⇒ `F4_adc_det.active_chain = "(无: fail-closed)"` · `chain_select_reason = "★没有任何装机链落到 SAR-ADC 脚 ⇒ ADC 输入悬空 / 无判据 ⇒ fail-closed★"` · `landing_net=""` · `som_pin=""` · `pin_class="UNKNOWN"` ⇒
★**⇒ 依赖落点的字段全部变成 None: `rth_ohm` / `tau_ms` / `t_settle_to_half_lsb_ms` / `leak_offset_v` / `leak_offset_pct_fs` / `node_v_at_supply` / `fs_utilization_pct` / `active_chain_pin`** ⇒ ★**⇒ 13 条语义红 (9 条判据红 + 4 条反向用例派生红) 全部从这里来** ★

★**★关键: 判据方向一个字没坏, 坏的是【比较用的字符串形态】★** ★
⇒ 修法 = **在比较前把节点串归一化成位号** (剥掉 ` pinN` 后缀) ⇒ 脚号本来就不是这条判据的输入 ⇒ ★**判据方向不变 / 阈值不变 / 落点分类不变** ★

### §0-3 · ★**三组对照 (★本单自己实跑·读数原样★)** ★

| 组 | 网表 | `timing_check.py` 读数 | rc | 留证 |
|---|---|---|---|---|
| ★**基线** ★ | 真网表 `HW/netlist_v1.csv` | ★**85/85 全过** ★ | 0 | `logs/iss370/21_CONT1_timing_baseline.txt` |
| ★**对照组 (证明不是路径问题)** ★ | 真网表内容·换路径 `tmp/iss370_sbx/netlist_REAL_copy.csv` | ★**85/85 全过** ★ | 0 | `logs/iss370/23_CONT1_timing_REAL_copy.txt` |
| ★**腿 B 全量** ★ | `tmp/iss364_sbx/netlist_v1_legB.csv` | ★**70/85 · 15 条红** ★ | 1 | `logs/iss370/22_CONT1_timing_legB_full.txt` |

★**⇒ 上表这三行 = `--netlist` 覆盖口径下的读数。★下面 §0-4 是【落表仿真】口径, 两口径数字不一样, 差的那一条是本单最重要的发现。** ★

### §0-4 · ★★【两变体拆解】(★把「改名」与「补行」两个作用分开★) ★★

| 变体 | 构造 | 读数 | 红项构成 |
|---|---|---|---|
| ★**R = 只改名** (196 格 · 0 补行 · 513 行) ★ | `tmp/iss370_sbx/netlist_v1_rename_only.csv` (★只读现成的·没重新生成★) | ★**71/85 · 14 条红** ★ | 13 条语义红 + 1 条落表义务红 (md5 锚点) |
| ★**A = 只补行** (4 行 · 0 改名 · 517 行) ★ | `tmp/iss370_sbx/netlist_v1_rowadd_only.csv` (★只读现成的★) | ★**73/85 · 2 条红** ★ | ★**2 条全是落表义务红** ★ (行数锚点 + md5 锚点) |

★**本单自己算的三组关系 (★留证 `logs/iss370/26_CONT1_fail_sets.txt`★)**:
- `R − A` = **13 条** = 语义红 (9 条判据红 + 4 条反向用例派生红) ⇒ ★**改名单独就造成全部语义破坏** ★
- `A − R` = **1 条** = `网表锚点: 现行网表 = 513 数据行 (行数不许变)` ⇒ ★**行数锚点红只由补行引起** ★
- `R ∩ A` = **1 条** = `网表锚点: 现行网表 md5 ∈ 落表台账登记的状态` ⇒ ★**任何内容改动都会触发 md5 锚点红 ⇒ 它是落表义务, 不是语义破坏** ★
- 13 + 1 + 1 = **15** ✓

★**★⚠ 一处必须写清的差异 (★派活书 §一 G4 的措辞与实测对不上·本单以实测为准★)** ★
★**派活书 G4 写「只改名变体的红项里没有落表义务红」⇒ ★实测【不成立】**: 只改名变体【确实】含 1 条落表义务红 (md5 锚点), 因为 md5 锚点判的是【内容变了没有】, 改名当然变了内容 ★
★**⇒ 本单的 G4 按【实测成立的分离关系】实现**: ★
★**① 只补行变体的红项 【全部】 是落表义务红, 且【一条语义红都没有】 ★**
★**② 只改名变体的红项里, 【凡与只补行变体同名的】 都归落表义务, 【其余 13 条】 全归语义破坏/反向用例 ★**
★**③ 三者关系 `腿B全量 = 只改名 ∪ 只补行` (集合并, 不多不少) ★**
★**⇒ 这才是「两类红可分离」的机器证明; 派活书那一句措辞若照抄, 闸会【恒红】(= 判据自毁)** ★

### §0-5 · ★★【落表仿真: 真落盘那天真实的红数 = 16, 不是 15】★★

★**★为什么 `--netlist` 口径看不见第 16 条★**: ★
`timing_check.py` L325: `disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)` ⇒ 判据 **「网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立」** 直接读【**盘上真源**】⇒ **`--netlist` 参数覆盖不到它** ⇒ ★**沙盒跑 15 条, 真落盘那天是 16 条** ★

★**本单为此自建了【镜像工程根】(★不写 /tmp·不碰真件★)**: ★
`tmp/iss370_sbx/land_root/` = `HW/netlist_v1.csv` 换成腿 B 网表 + 其余全软链真件 + `SW/tools/timing_check.py` 是真件副本 ⇒ ★`_PROJECT_ROOT` 算成镜像根 ⇒ 「盘上真源」读到的就是那份腿 B 网表** ★

| 镜像根 | 网表 | timing_check.py | 读数 | rc |
|---|---|---|---|---|
| `land_root_base` (对照) | 基线网表副本 | ★**真件副本 (一字未改)** ★ | ★**85/85 全绿** ★ | 0 |
| `land_root` (改前) | ★**腿 B 网表** ★ | ★**真件副本 (一字未改)** ★ | ★**69/85 · 16 条红** ★ | 1 |
| `land_root_fix` (改后) | ★**腿 B 网表** ★ | ★**补丁副本 (只改沙盒·真件一字未动)** ★ | ★**82/85 · 3 条红** ★ | 1 |

★**⇒ 落表仿真多出来的那 1 条 = `网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)` (★§1-补 第 16 条★)** ★
★**⇒ 改后剩下的 3 条 = 行数锚点 + md5 锚点 + 三方对账 ⇒ 全是落表义务 ⇒ 合法落表即可解 ⇒ 【语义红 13 条全部回绿】** ★

★**留证**: `logs/iss370/28_CONT1_landing_sim.txt` · 脚本 `tmp/iss370_sbx/gen_landing_sim.py` ★

### §0-6 · ★★【SW 侧哪些闸会红 / 哪些不受影响】(★负结论也写·省下一个人重查★)★★

★**本单自建镜像根跑闸电池 (★`tmp/iss370_sbx/gen_gate_battery.py` · 留证 `logs/iss370/29_CONT1_gate_battery.txt`★)**: ★

| 闸 | 对照 (基线镜像) | ★**改前 (腿 B 落盘)** ★ | ★**改后 (+补丁)** ★ | 归类 |
|---|---|---|---|---|
| `SW/tools/timing_check.py` | rc=0 · 85/85 | ★**rc=1 · 69/85 · 16 红** ★ | ★**rc=1 · 82/85 · 3 红** ★ | 语义破坏 + 落表义务 |
| `SW/tools/check_timing_review_adc_sync.py` | rc=0 · 29/29 | ★**rc=2** (ADC 字段全 None ⇒ fail-closed) ★ | ★**rc=0 · 29/29** ★ | ★**语义破坏 ⇒ 第 1 件修好后自动绿** ★ |
| `SW/tools/check_demo_panel_spec.py` (R6) | rc=0 | ★**rc=1** (R6 台账链红) ★ | rc=1 | 落表义务 |
| `SW/tools/check_onepass_sw_sync.py` (W1~W6) | rc=0 | ★**rc=1** (W6 两条子错) ★ | rc=1 | 落表义务 |
| `SW/tools/check_onepass_sw_release.py` (10 道子闸) | ★**rc=0 (10/10 绿)** ★ | ★**rc=1** (7 道子闸红) ★ | rc=1 (6 道红, 少 1 道) | 汇总闸 |
| `SW/tools/check_shutdown_semantics.py` | rc=0 | ★**rc=0** ★ | rc=0 | ★**不受影响** ★ |
| `SW/tools/check_sw_ref_reachability_v2.py` | rc=0 | ★**rc=0** ★ | rc=0 | ★**不受影响** ★ |
| `SW/tools/check_landing_trace_obligation.py` | rc=0 | ★**rc=0** ★ | rc=0 | ★**不受影响** (★但同批要留痕★) |
| `SW/tools/check_load_switch_selection.py` | rc=0 | ★**rc=0 · PASS** ★ | rc=0 | ★**不受影响** ★ |

★**⇒ 真正被腿 B 打红的 SW 闸 = 4 道 (timing_check / adc_sync / demo_panel_spec R6 / sw_sync W6) + 1 道汇总闸 (sw_release) ★**
★**⇒ 其余 4 道实测不受影响 (★negative 结论已写·下一个人不必重查★)** ★

★**★一处沙盒完整性自坑 (★本单自己踩到并修好·必须留痕★)** ★
★**第一版镜像根只软链了 `*.py` ⇒ 两道 R6 反向用例闸 (`..._r6_chainjudge_selftest.py` / `..._r6_hardprot_iss315_selftest.py`) 在镜像根里【假红 rc=2】** ★
★**真因 = 它们要读同目录下的判据备份 `check_demo_panel_spec.py.bak_iss312` / `.bak_iss315` ⇒ 镜像根没软链 ⇒ 报「找不到修前的判据备份」** ★
★**⇒ 补上 `.bak_iss*` 软链后, 对照组发布闸回到 rc=0 (10/10 绿) ⇒ 与真项目根实跑一致 ⇒ 镜像根才可信** ★
★**⇒ 这一条说明: ★沙盒读数必须先跑【对照】, 对照不绿 = 沙盒不完整, 不是腿 B 的影响★** ★

### §0-7 · ★**一处 mtime 假象 (★不写清楚, 下一个人会误判成落表★)** ★

| 文件 | mtime | 内容 md5 | 判定 |
|---|---|---|---|
| `HW/netlist_v1_pins.csv` | ★**2026-11-23 19:19:15** ★ | ★`9174309df1ec9411ac8e8d9e80ee386a` (★= 基线·逐字节相同★) | ★**不是落表** ★ —— 只是 mtime 被顶了 |
| `HW/netlist_v1.csv` | 2026-11-18 00:21:08 | `6aee500e60ba0732f83a9cf557ba90ab` (= 基线) | 未动 |
| `HW/BOM_v1.csv` | 2026-11-18 00:21:08 | `5b9993992405904a60ac96a020b375d8` (= 基线) | 未动 |
| `HW/PCB/demo_mainboard.kicad_pcb` | 2026-11-06 07:07:17 | `611b869e13518c3c023fb178f91a0075` (= 基线) | 未动 |

★**⇒ 任何按 mtime 判的闸会假红 ⇒ 一律按内容 md5 判** ★

### §0-8 · ★**保护基线 (★开工前 + 交卷后各打一次·见交卷页 B6-2★)** ★

| 件 | md5 | 备注 |
|---|---|---|
| 板 `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | 4,940,213 B · mtime 2026-11-06 07:07:17.362193413 |
| 网表 `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | 143,198 B |
| 脚表 `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | 146,055 B (★mtime 假象见 §0-7★) |
| BOM `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | 44,881 B |

---

## §1 · ★**§1 共 15 条红** ★ 逐条表 (★分类 = 语义破坏 / 落表义务 / 反向用例 三选一★)

★**归类口径 (★本单自己定的★)**:
- ★**语义破坏** = 腿 B 的改名让判据**取不到它要取的物理量** ⇒ 改法在 SW 侧脚本 ⇒ **必须同批修** ★
- ★**落表义务** = 网表内容/行数变了, 但台账还没跟上 ⇒ **合法落表 + 重锚即解** ⇒ **不是 SW 的域** ★
- ★**反向用例** = 反向用例断言【正向判据必须先绿】, 正向塌了 ⇒ 连带红 ⇒ **本身一个字不许改, 随正向修好自动回绿** ★

★**★三条反向用例 (第 12~15 条) 为什么被归成「反向用例」而不是「语义破坏」★**: ★
★**本单读了源码**: `_mk_reverse*()` 生成的每条反向用例都断言 `xxx_ok(未改动) is True` **且** `xxx_ok(改后) is False` ⇒ 腿 B 下【未改动的那一侧】就已经塌了 ⇒ **断言前半句不成立 ⇒ 反向用例自己报红** ⇒ ★**它不是独立破坏, 它是被牵连的证人** ★

| # | 红项原文 | ★**红因 (★本单复核过★)** ★ | 归类 | 修法 | 会红的闸 | 修完怎么自证回绿 |
|---|---|---|---|---|---|---|
| 1 | `ADC 源阻抗 = 37.5k (★ISS-291: 判决对象 = BAT_DET 链 → pin38 SARADC_VIN5★)` | ★`resolve_chain_landing()` L1026 精确相等不成立 ⇒ `mid_net=""` ⇒ `rth_ohm=None` ★ | 语义破坏 | ★**§2 第 1 件**: 节点串比较前加 `_node_ref()` 归一化层 ★ | `timing_check.py` | 落表仿真 rc=1 且 SELFTEST 69/85 → 82/85, 本条 FAIL→PASS |
| 2 | `ADC tau = 3.75ms (★ISS-291 口径★)` | ★同第 1 条 (τ = R_th·C, 链取不到 ⇒ 无值) ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同上 |
| 3 | `ADC 12bit 建立 33.8ms ≤ 300ms 红线 (★ISS-291 口径: 老口径的 451ms 是**假红**★)` | ★同第 1 条 ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同上 |
| 4 | `ADC 漏电偏移 37.5mV ≤ 0.4V 红线 (★ISS-291 口径: 老口径的 0.50V 是**假红**★)` | ★同第 1 条 ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同上 |
| 5 | `网表锚点: 现行网表 = 513 数据行 (行数不许变)` | ★补行 4 条 ⇒ 数据行 517 ≠ 513 ⇒ 锚点里的行数是【落表前值】 ★ | ★**落表义务** ★ | ★**落表那一跳把 513 同步到 517** (★判据方向不许变·阈值不许调松★) ★ | `timing_check.py` | 落表后 PASS; ★**该条只在【只补行】变体里出现·不在【只改名】变体里出现⇒ 分类自证** ★ |
| 6 | `网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)` | ★腿 B 网表 md5 `724f0bf71cb7…` 不在落表台账链上 ⇒ **任何内容改动都会触发它** ★ | ★**落表义务** ★ | ★**落表那一跳把新 md5 登记进链** (判据方向一个字不改) ★ | `timing_check.py` · `check_demo_panel_spec.py` (R6) · `check_onepass_sw_sync.py` (W6) | 落表后 PASS; ★**该条在【只改名】与【只补行】两个变体里都出现⇒ 分类自证** ★ |
| 7 | `F4' 实读: ADC 判决对象 = BAT_DET 链 (落点 J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域); BAT_DET 三颗必装` | ★判决对象要靠落点 ⇒ 落点空 ⇒ 判不出 BAT_DET 链 ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同第 1 条 |
| 8 | `F4 实读: 漏电偏移 37.5mV = 2.1% FS ⇒ 与网表 L182 note 写死的数**逐字对上** (口径同源)` | ★同第 1 条 (偏移量由链实读) ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同第 1 条 |
| 9 | `F4 实读: 判决源 = SoM 脚表 signal 列 (落点判 SAR-ADC), 取链模式 = by_landing_pin` | ★`active_chain_pin` 取不到 ⇒ 判决源判不出 ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同第 1 条 |
| 10 | `F4 实读: ADC 节点 @4.2V = 1.575V ≤ abs-max 1.98V (FS 利用率 87.5%)` | ★节点电压由分压实读 ⇒ 链取不到 ⇒ 无值 ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同第 1 条 |
| 11 | `F4D 实读: VBUS_DET_D 落点 = J_SOM_P1 pin100 = USB_DRD1_VBUSDET (数字脚 ⇒ 不进 ADC 判据)` | ★**VBUS_DET_D 链也被腿 B 改了名** ⇒ 它的落点同样取不到 ⇒ 数字链判据塌 ★ | 语义破坏 | 同第 1 件 | `timing_check.py` | 同第 1 条 |
| 12 | `REV-12 反向: 把满量程 V_DET_FS 改回 3.3 (老口径) ⇒ 满量程/口径同源判据必须变红` | ★**派生红**: 反向用例断言【未改动侧必须先绿】, 正向已塌 ⇒ 前半句不成立 ★ | ★**反向用例** ★ | ★**反向用例本身一个字不许改**·随第 1 件修好自动回绿 ★ | `timing_check.py` | 落表仿真+补丁后本条 FAIL→PASS |
| 13 | `REV-13 反向: 把取链规则改回「元组第一条」⇒ 判决对象判据必须变红 (不许悄悄换回错对象)` | ★派生红 (同第 12 条) ★ | ★**反向用例** ★ | 同第 12 条 | `timing_check.py` | 同第 12 条 |
| 14 | `REV-14 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ 「ADC 输入悬空」判据必须变红` | ★派生红 (同第 12 条) ★ | ★**反向用例** ★ | 同第 12 条 | `timing_check.py` | 同第 12 条 |
| 15 | `REV-15 反向: 把 BAT_DET 的下臂 60k 改成 100k ⇒ @4.2V 节点 2.1V > 1.98V abs-max ⇒ 过压判据必须变红` | ★派生红 (同第 12 条) ★ | ★**反向用例** ★ | 同第 12 条 | `timing_check.py` | 同第 12 条 |

★**★补充说明: 为什么 REV-11 / REV-16 / REV-17 没红 (★负面对照·说明分类不是硬凑的★)** ★
- ★**REV-11** 断的是 `_bat_det_all_populated()` ⇒ 判的是 `dnp` 栏 ⇒ ★**腿 B 一格没动 `dnp` 栏** ⇒ 绿 ★
- ★**REV-16 / REV-17** 断的是数字链的静态电流 / 节点电平 ⇒ ★**这两个量不依赖落点** (`static_current_ua` / `node_v_nom` 由电阻值与供电算) ⇒ 绿 ★
- ★**⇒ 恰好是【依赖落点的量】全塌, 【不依赖落点的量】不塌 ⇒ 根因定位成立** ★

### §1-补 · ★**第 16 条 (★只在【落表仿真】里出现·`--netlist` 口径结构性看不见★)** ★

| # | 红项原文 | ★**红因 (★本单复核过★)** ★ | 归类 | 修法 | 会红的闸 | 修完怎么自证回绿 |
|---|---|---|---|---|---|---|
| 16 | `网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)` | ★**该判据直接读【盘上真源】** (`timing_check.py` L325: `disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)`) ⇒ ★**`--netlist` 覆盖改不到它** ⇒ 腿 B 真落盘且未落表 ⇒ 盘上 md5 `724f0bf71cb7` ≠ 台账链头 `6aee500e60ba` ⇒ 红 ★ | ★**落表义务** ★ | ★**落表那一跳把链头前移到腿 B 新 md5** (+ `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点副本重锚) ⇒ 自动绿 ★ | `timing_check.py` · `check_demo_panel_spec.py` (R6) · `check_onepass_sw_sync.py` (W6) · 三道 R6 反向用例闸 | 落表仿真 + 补丁后本条 FAIL→PASS (★改后只剩 3 条落表义务红, 本条在其中★) |

★**★本单的方法论贡献 (★一句话★)** ★
★**「腿 B 会打红 SW 门禁」这件事, 派活书给的是 15 条; 本单独立实跑落表仿真给的是 16 条 ⇒ ★差的那一条恰恰是【真落盘那天才出现的那一条】⇒ ★只跑 `--netlist` 的沙盒会低估破坏面★** ★

---

## §2 · ★★「腿 B ⇒ SW 侧必须同批改的活」总表 (★本单的真命门★) ★★

★**8 字段口径 (★逐件不许空★)**: ★**件号 / 改哪个文件 / 归属 / 时序 / 改的是脚本还是数据还是夹具还是文档 / 改法 / 沙盒实测读数 / 证据等级** ★

| # | 改哪个文件 | 归属 | 时序 | 改的是 | 改法 (★照着就能干·不许写「调整相关逻辑」★) | 沙盒实测读数 (改前 → 改后) | 证据等级 |
|---|---|---|---|---|---|---|---|
| ★**1** ★ | `SW/tools/timing_check.py` | ★**SW 域 (我)** ★ | ★**必须同批** ★ | ★**脚本** ★ | ★在 `resolve_chain_landing()` (L1013) 里把 `a = (x.get("node1") or "").strip()` / `b = (x.get("node2") or "").strip()` 两行换成 `a = _node_ref(x.get("node1"))` / `b = _node_ref(x.get("node2"))`; 并在 L1013 之前插入 `def _node_ref(s) -> str: return re.sub(r"\s+pin\d+\s*$", "", (s or "").strip())` ★★判据方向一个字不改: 仍然只比【位号】, 脚号 pinN 本来就不是这条判据的输入; 阈值 300ms / 0.4V / 1.98V / 1.8V 域 / 513 行锚点 一条都不许动★★ ★ | ★**改前 rc=1 · SELFTEST 69/85 (16 红)** ★ ⇒ ★**改后 rc=1 · SELFTEST 82/85 (3 红·13 条语义红全回绿)** ★ | ★**[实测]** ★ |
| ★**2** ★ | `SW/tools/check_timing_review_adc_sync.py` | ★**SW 域 (我)** ★ | ★**必须同批** ★ | ★**脚本 (★本单结论: 不需要改·随第 1 件自动回绿·但必须同批复跑自证★)** ★ | ★一个字不许改; 它消费 `timing_check` 的 ADC 字段, 腿 B 下字段全 None ⇒ fail-closed 报 rc=2 ⇒ 第 1 件修好后自动 rc=0; ★那一趟必须同批复跑它并把 29/29 贴进交卷页★ ★ | ★**改前 rc=2** ★ ⇒ ★**改后 rc=0 (29/29 项通过)** ★ | ★**[实测]** ★ |
| ★**3** ★ | `HW/netlist_v1.csv` (网表真源落表) | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**必须同批** ★ | ★**数据** ★ | ★腿 B 那一跳由 hw-lead 把改名 196 格 + 补行 4 条落进 `HW/netlist_v1.csv`; ★SW 侧只给改法, 本单 `HW/` 下【一个文件都没碰】★ ★ | ★**落表前: 盘上 md5 = 6aee500e60ba** ★ ⇒ ★**落表后: 盘上 md5 = 724f0bf71cb7** ★ ⇒ SW 侧第 4/5/7/8 件同时解锁 ★ | ★**[实测]** ★ |
| ★**4** ★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` (落表台账链) | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**必须同批** ★ | ★**数据** ★ | ★落表那一跳把腿 B 新 md5 `724f0bf71cb7ec6c74e389cf9cd8d3fe` 登记进网表落表链 (链头前移) + 填落表单号 (★判据方向一个字不许改·不许手改 md5 凑绿★); ★SW 侧一个字不改★ ★ | ★**落表前: md5 锚点红 + 三方对账红 + R6 红 + W6 红 (4 道)** ★ ⇒ ★**落表后 4 道同时绿** ★ | ★**[实测]** ★ |
| ★**5** ★ | `SW/SW_MD5_BASELINE_LEDGER.md` (§1 锚点块) | ★**SW 域 (我)** ★ | ★**必须同批** ★ | ★**数据** ★ | ★按 H-1 重锚机制, 把锚点块里 `HW/netlist_v1.csv` 那条的 `md5` 改写成落表后的新 md5 + `by` 填落表单号; `prev_md5` 保留旧值作历史留痕; ★不许手改 md5 凑绿—— 锚点 md5 必须在台账链上且落表单号要与台账产出该 md5 的单号对得上★ ★ | ★**落表前: 三方对账红** ★ ⇒ ★**落表后绿** ★ | ★**[实测]** ★ |
| ★**6** ★ | `state/issue_log.yaml` (落表留痕) | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**必须同批** ★ | ★**数据** ★ | ★落表那一跳在 issue_log 里留【文件名 + 新 md5】的落表留痕; ★本单实测: 留痕闸判的是【留痕条目在不在】不判盘上 md5 ⇒ 腿 B 落盘但没留痕时它仍然绿 ⇒ ★但那一跳必须补留痕, 否则将来另一次落表会把账做乱★ ★ | ★**本单实测: 腿 B 落盘未留痕 ⇒ 留痕闸 rc=0 (绿)** ★ ⇒ ★**留痕缺失的风险点在台账链, 不在这道闸** ★ | ★**[实测]** ★ |
| ★**7** ★ | `SW/tools/check_demo_panel_spec.py` (R6 三方对账) | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**必须同批** ★ | ★**脚本 (★本单结论: 不需要改·落表后自动绿·但必须同批复跑自证★)** ★ | ★一个字不许改; R6 判【盘上真源 md5 vs 落表台账链头】⇒ 腿 B 落盘未落表 ⇒ 红 ⇒ 落表后链头前移 ⇒ 自动绿; ★要改 R6 判据 = 把红项调没 = 绝对禁止★ ★ | ★**改前 rc=1** ★ (★`R6 台账链: 盘上真源 md5 HW/netlist_v1.csv = 724f0bf71cb7 ≠ 台账最新记录 6aee500e60ba`★) ⇒ ★**落表后 rc=0** ★ | ★**[实测]** ★ |
| ★**8** ★ | `SW/tools/check_onepass_sw_sync.py` (W6 受保护 5 件) | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**必须同批** ★ | ★**脚本 (★本单结论: 不需要改·落表后自动绿·但必须同批复跑自证★)** ★ | ★一个字不许改; W6 判【盘上 md5 在落表台账里查得到】+【盘上 md5 == 台账链头】⇒ 腿 B 落盘未落表 ⇒ 两条子错 ⇒ 落表后自动绿; ★要改 W6 判据 = 绝对禁止★ ★ | ★**改前 rc=1** ★ (★2 条子错: ① 腿 B md5 在落表台账里查不到 ② 盘上 md5 ≠ 台账链头★) ⇒ ★**落表后 rc=0** ★ | ★**[实测]** ★ |
| ★**9** ★ | `HW/netlist_v1_pins.csv` (脚表) | ★**跨域 · 不是 SW 的域 · 只给改法** ★ | ★**可板后补** ★ | ★**数据** ★ | ★**一个字不许改** —— 腿 B 补的 4 条行的节点在脚表里【本来就有】(★补行行的 note 自证: 脚表 `netlist_v1_pins.csv` 已有该脚·如 `R_BAT_DET_2 pin2 · net GND`★) ⇒ 脚表零改动; ★注意 mtime 被顶到 2026-11-23 19:19:15 是假象, 一律按内容 md5 判★ ★ | ★**本单实测: 脚表 md5 = 9174309df1ec9411ac8e8d9e80ee386a = 基线·逐字节相同** ★ ⇒ ★**零改动成立** ★ | ★**[实测]** ★ |
| ★**10** ★ | `SW/tools/check_onepass_legb_sw_impact.py` (本单新建闸) | ★**SW 域 (我)** ★ | ★**可板后补** ★ | ★**脚本** ★ | ★本单已交; ★**零挂链** —— 不写进 `state/gate_check.py` (★挂链是 main 的机制地界·ISS-330/333/362 同款★); ★那一趟开跑前手工跑一次即可★ ★ | ★**裸跑 rc=0** ★ · ★**`--selftest` 9/9 PASS** ★ | ★**[实测]** ★ |

★**★跨域那几件单独点名 (★件 3 / 4 / 6 / 7 / 8 / 9★)**: ★
★**① 网表真源落表 (件 3) ② 落表台账链前移 (件 4) ③ issue_log 留痕 (件 6) —— 这三件是【hw-lead / main 的地界】★**
★**④ R6 (件 7) 与 W6 (件 8) 是【跨域】—— 判决源在 SW/ 下, 但【锚点链头】在 HW/ 的落表台账里 ⇒ SW 侧无权改判据, 只登记 + 给改法 + 给时序 + 给会红哪道闸** ★
★**⑤ 本单 `HW/` 下【一个文件都没碰】(★md5 见 §0-8★), 全部改法只写在【清单的字】里, 那一趟还没到** ★

★**★时序口径 (★为什么第 3/4/5/6 件是「必须同批」而不是「可板后补」★)** ★
★**腿 B 落盘到落表登记之间【有一个时间窗】⇒ 那个窗里 SW 侧【4 道闸是红的】⇒**
★**⇒ 顺序必须是: ① 腿 B 落表 (件 3) ② 落表台账链前移 (件 4) ③ SW 锚点重锚 (件 5) ④ 留痕 (件 6) —— 四步必须连着做完, 中途停 ⇒ 门禁链红着交班** ★
★**⇒ 而第 1 件 (取链归一化) 与落表【没有先后依赖】⇒ 但【必须同批】, 因为不改它, 落表做完还是 13 条语义红** ★

---

## §3 · ★三条反向自证 (★每条都自证成功★) ★

| # | 自证 | 喂什么 | 期望 | ★**本单实跑读数** ★ | 结论 |
|---|---|---|---|---|---|
| ① | ★**只改名不补行 ⇒ 13 条语义红必须全在** ★ | `tmp/iss370_sbx/netlist_v1_rename_only.csv` (★只读现成的·没重新生成★) | 14 条红 = ★**13 条语义红 (9 判据 + 4 反向用例) + 1 条落表义务红 (md5 锚点)** ★ | ★**rc=1 · 71/85 · 14 条红** ★ · 逐条红项原文见 `logs/iss370/26_CONT1_fail_sets.txt` ★ | ★**自证成功** ★ |
| ② | ★**只补行不改名 ⇒ 2 条落表义务红必须全在, 语义红必须全不在** ★ | `tmp/iss370_sbx/netlist_v1_rowadd_only.csv` (★只读现成的★) | ★**2 条红, 全是落表义务 (行数锚点 + md5 锚点); 13 条语义红一条都不在** ★ | ★**rc=1 · 73/85 · 2 条红** ★ (`网表锚点: 现行网表 = 513 数据行 (行数不许变)` + `网表锚点: 现行网表 md5 ∈ 落表台账登记的状态`) ★ | ★**自证成功** ★ |
| ③ | ★**喂真网表 ⇒ 必须 85/85 全绿 (证明沙盒没污染)** ★ | ① 真项目根 `python3 SW/tools/timing_check.py` ② 镜像根 `land_root_base` (基线网表副本) ③ `--netlist` 对照组 `netlist_REAL_copy.csv` | ★**三处都 85/85 · rc=0** ★ | ★**① 85/85 rc=0 ② 85/85 rc=0 ③ 85/85 rc=0** ★ | ★**自证成功** ★ |

★**★第 ④ 条自证 (★本单加的·因为它才是真命门★)** ★
| # | 自证 | 期望 | ★**本单实跑读数** ★ | 结论 |
|---|---|---|---|---|
| ④ | ★**补丁只回绿语义红, 落表义务红一条都不许被顺手调没** ★ | 落表仿真 + 补丁 ⇒ ★**69/85 (16 红) → 82/85 (3 红)**, 且剩下的 3 条 = 行数锚点 + md5 锚点 + 三方对账 (★全是落表义务★) | ★**land_root: 69/85 · 16 红** ★ ⇒ ★**land_root_fix: 82/85 · 3 红** ★ (★补丁只动 `resolve_chain_landing` 的字符串比较, 一条判据阈值都没碰★) ★ | ★**自证成功** ★ |

---

## §4 · 降级方案 (★逐件必填·一件不空·三选一: 官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开★)

★**★口径声明**: ★**本单【没有一件】用「官网参数可满足的等效件」这一档** —— 理由: ★
★**腿 B 的破坏面是【字符串形态】问题, 不是【器件选型】问题 ⇒ 没有「换一个官网等效件就能绕开」的路径** ★
★**⇒ 10 件里: 沙盒验证法 9 件 + 改设计路径绕开 1 件 (件 2) ⇒ 一件不空** ★

| 件 | 降级档 | 逐字降级方案 (★照着能干★) |
|---|---|---|
| ★**1** ★ | ★**沙盒验证法** ★ | ★若那一趟来不及改 `timing_check.py`: 在 `tmp/iss370_sbx/land_root/` 镜像根里跑一遍, 把 13 条语义红的原文逐条抄进那一趟的交卷页 ⇒ ★**但这只是把红项登记下来, 不等于闸绿** ⇒ 门禁链仍是红的 ⇒ **不许当解法** ⇒ 真解法只有「同批加 `_node_ref()` 归一化层」这 3 行 ★ |
| ★**2** ★ | ★**改设计路径绕开** ★ | ★若不许改 `timing_check.py` (受保护资产), 唯一另一条路是【腿 B 的节点串保持裸位号】= **取消腿 B 这一跳** ⇒ 代价: 200 条具名指令全部作废 ⇒ **属设计路径回退, 不是技术降级** ⇒ ★**代价登记在 §5, 归老板拍** ★ |
| ★**3** ★ | ★**沙盒验证法** ★ | ★若落表那一跳排不进同一窗口: 先在 `tmp/iss370_sbx/land_root_fix/` 镜像根里验完 (本单已建好), 但 ★**落表不许用沙盒代替真落表**★ —— 真落表这一件本身没有降级路径, 只有「晚几天做」的时序代价 ★ |
| ★**4** ★ | ★**沙盒验证法** ★ | ★落表台账链前移没有等效件 (它是唯一权威源); 可退到【沙盒验证法】: 在镜像根的 `state/` 副本里模拟链头前移 ⇒ 实测机制成立 (落表后 4 道红同时绿) ★ |
| ★**5** ★ | ★**沙盒验证法** ★ | ★锚点重锚可退到【沙盒验证法】: 在镜像根里改锚点副本后跑三方对账 ⇒ 但 ★**不许手改 md5 凑绿**★ —— 锚点 md5 必须在台账链上, 且落表单号要与台账产出该 md5 的单号对得上 ★ |
| ★**6** ★ | ★**沙盒验证法** ★ | ★留痕可退到【沙盒验证法】: 在镜像根的 `state/issue_log.yaml` 副本里补一条留痕再跑 `check_landing_trace_obligation.py` ⇒ 本单实测该闸只判留痕条目在不在, 不判盘上 md5 ★ |
| ★**7** ★ | ★**沙盒验证法** ★ | ★R6 没有等效件可替; 可退到【沙盒验证法】确认落表后链头前移 ⇒ R6 自动绿 ⇒ **不许改 R6 判据** ★ |
| ★**8** ★ | ★**沙盒验证法** ★ | ★W6 同 R6: 不许改 W6 判据; 落表后自动绿 ★ |
| ★**9** ★ | ★**改设计路径绕开** ★ | ★脚表零改动; 若哪天真要改脚表, 绕开路径 = 改脚表自己的落表链 (跨域) —— ★**本单实测脚表一个字不用动, 这一件本来就不需要降级方案**★ ★ |
| ★**10** ★ | ★**沙盒验证法** ★ | ★新闸挂不挂链归 main; 本单只保证闸本身裸跑 rc=0 + selftest 9/9 全过 ⇒ 挂不挂链不影响闸的正确性 ★ |

---

## §5 · 未决项与卡点 (★只登记·**不代拍**★) ★

### §5-1 · ★**要老板拍的 (★本单只登记缺口 + 依据 + 代价·不代选★)** ★

| # | 缺口 | 依据 | 代价 (★选 A / 选 B 各是什么后果★) | 状态 |
|---|---|---|---|---|
| ★**U1** ★ | ★**腿 B 那一趟, 【腿 B 落表】与【SW 侧取链归一化】谁先做? ★** | ★实测: 不做归一化 ⇒ 落表做完仍 13 条语义红; 不做落表 ⇒ 4 道闸红 (含 2 道 R6 反向用例闸因「基线不绿」而 rc=2) ★ | ★**选 A (先落表再改闸)**: 中间窗口门禁链红着, 窗口有多长要 hw-lead 排期 ★ **选 B (先改闸再落表)**: 窗口里只有 13 条语义红, 落表那一步一做完就全绿 ⇒ **窗口更干净** ★ | ★**登记·待拍** ★ |
| ★**U2** ★ | ★**第 513 行锚点改 517: 这是【判据阈值】变更, 谁批? ★** | ★`timing_check.py` L2140 硬写 `netlist_data_rows == 513`; 腿 B 合法补 4 行 ⇒ 判据必须跟着走 ★ | ★**选 A (改成 517)**: 判据跟着真源走, 但这是【受保护判据】⇒ 需批准 ★ **选 B (不改)**: 那条红永久挂着 ⇒ **门禁链永远红** ⇒ 不可接受 ★ | ★**登记·待拍** ★ |
| ★**U3** ★ | ★**要不要取消腿 B (退回裸位号)? ★** | ★§4 件 2 的改设计路径绕开 ★ | ★**选 A (照做腿 B)**: 承担 10 件同批清单 + 一次落表 ★ **选 B (取消)**: 200 条具名指令作废, 网表继续裸位号 ⇒ 后续脚表核对仍靠人眼 ★ | ★**登记·待拍** ★ |

### §5-2 · ★**要 main 裁的 (★写清「要谁回答什么」★)** ★

| # | 要谁 | 回答什么 | 为什么归 main | 状态 |
|---|---|---|---|---|
| ★**U4** ★ | ★**main** ★ | ★**新闸 `SW/tools/check_onepass_legb_sw_impact.py` 挂不挂进 `state/gate_check.py`? ★** | ★挂链是 main 的机制地界 (ISS-330/333/362 同款) ⇒ 本单**零挂链**, 只交脚本 ★ | ★**登记·待裁** ★ |
| ★**U5** ★ | ★**main** ★ | ★**腿 B 落表单号是谁签? ★** (★落表台账链前移 + `state/issue_log.yaml` 留痕都要单号·而单号是 main 签的★) | ★`state/issue_log.yaml` 是 main 的地界 ⇒ 本单一个字没写 ★ | ★**登记·待裁** ★ |
| ★**U6** ★ | ★**main** ★ | ★**腿 B 那一趟的「板只改一次」窗口有多长? ★** (★决定 §5-1 U1 的中间窗口代价★) | ★排期归 main ★ | ★**登记·待裁** ★ |
| ★**U7** ★ | ★**hw-lead** ★ | ★**腿 B 落表那一跳, 落表台账链前移与网表写盘是【同一个原子动作】还是【两步】? ★** | ★落表台账在 HW/ 下 ⇒ hw-lead 的地界 ⇒ SW 侧只给改法 ★ | ★**登记·待交 need** ★ |

### §5-3 · ★**本单【没有】做的事 (★防止下一个人误以为已经做过了★)** ★

| # | 没做 | 为什么 | 
|---|---|---|
| ★**N1** ★ | ★**没改 `SW/tools/timing_check.py`** ★ | ★零改既有闸 ⇒ §2 件 1 的改法只是【清单里的字】★ |
| ★**N2** ★ | ★**没碰 `HW/` 下任何文件** ★ | ★零落表 + 不写别人的域 ⇒ md5 见 §0-8★ |
| ★**N3** ★ | ★**没把新闸挂进 `state/gate_check.py`** ★ | ★零挂链 (main 的机制地界)★ |
| ★**N4** ★ | ★**没写 `state/issue_log.yaml` / `state/dispatch_log.yaml`** ★ | ★那两份是 main 的地界★ |
| ★**N5** ★ | ★**没动 `SW/BOARD_ONEPASS_SW_SYNC.md` / `SW/SW_MD5_BASELINE_LEDGER.md` / `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 的正文** ★ | ★零改既有页面正文 ⇒ 只在交卷页里给建议 ★ |

---

## §6 · 自证复现命令 (★全部在本项目根下跑·★全部只读真件★)

```bash
# ★§0-3 三组对照 (★本单自己跑的读数出处★) ★
python3 SW/tools/timing_check.py                                                   # ★85/85 · rc=0 ★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_REAL_copy.csv   # ★85/85 · rc=0 ★
python3 SW/tools/timing_check.py --netlist tmp/iss364_sbx/netlist_v1_legB.csv     # ★70/85 · 15 红 · rc=1 ★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rename_only.csv  # ★71/85 · 14 红 · rc=1 ★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rowadd_only.csv  # ★73/85 · 2 红 · rc=1 ★

# ★§0-4 / §3 红项集合逐条 (★本单自己跑的★) ★
grep '\[FAIL\]' logs/iss370/22_CONT1_timing_legB_full.txt
grep '\[FAIL\]' logs/iss370/24_CONT1_timing_rename_only.txt
grep '\[FAIL\]' logs/iss370/25_CONT1_timing_rowadd_only.txt

# ★§0-5 落表仿真 (★自建镜像工程根·真件零改动★) ★
python3 tmp/iss370_sbx/gen_landing_sim.py     # ★改前 69/85 (16 红) · 对照 85/85 · 改后 82/85 (3 红) ★

# ★§0-6 闸电池 (★三套镜像根对比★) ★
python3 tmp/iss370_sbx/gen_gate_battery.py

# ★§0-1 三个数 (★改动格数 / 改动栏 / 行数★) ★
python3 - <<'PY'
import csv
def rows(p):
    with open(p, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
b=rows("HW/netlist_v1.csv"); l=rows("tmp/iss364_sbx/netlist_v1_legB.csv")
def sig(r): return (r.get("ref",""),r.get("net",""),r.get("value",""),r.get("type",""),r.get("dnp",""))
bs={}
for r in b: bs.setdefault(sig(r),[]).append(r)
n=0; cols={}
for r in l:
    c=bs.get(sig(r))
    if not c: continue
    br=c.pop(0)
    for k in br:
        if (br.get(k) or "")!=(r.get(k) or ""): n+=1; cols[k]=cols.get(k,0)+1
print("改动格数 =", n, "· 改动栏 =", sorted(cols), "· 行数 =", len(b), "->", len(l))
PY

# ★本单新建闸 ★
python3 SW/tools/check_onepass_legb_sw_impact.py              # ★rc=0 ★
python3 SW/tools/check_onepass_legb_sw_impact.py --selftest   # ★9/9 PASS ★

# ★边界自证 (★md5 交卷前后逐字节相同★) ★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**★边界自证 (★本单做到 / 没做到★)** ★

| 边界 | 怎么保证 | 自证 |
|---|---|---|
| ★**零写板** ★ | 只读板; 所有写操作只发生在 `tmp/iss370_sbx/` 的副本上 | ★板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` + size 4,940,213 B 交卷前后逐字节相同 ★ |
| ★**零落表** ★ | 只读网表 / 脚表 / BOM / 落表台账 / issue_log | ★四件 md5 交卷前后相同 (§0-8)★ |
| ★**零改既有闸** ★ | `SW/tools/*.py` + `state/*.py` 全部文件 md5 不变 | ★交卷页 B6-2 逐件 md5 对照 ★ |
| ★**零改既有页面正文** ★ | 只新建 2 个文件 (`SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` + `SW/tools/check_onepass_legb_sw_impact.py`) | ★既有页面 md5 交卷前后相同 ★ |
| ★**零挂链** ★ | 新闸不写进 `state/gate_check.py` | ★`state/gate_check.py` md5 不变 ★ |
| ★**零外发** ★ | 本单零外部调用 (不发邮件 / 不询价 / 不问询 / 不采购) | ★本单零网络请求 ★ |
| ★**不替老板拍板** ★ | §5 只登记缺口 + 依据 + 代价 | ★U1~U3 三条都写「登记·待拍」★ |
| ★**不写别人的分片** ★ | 只写 `state/fragments/sw.yaml` (经 `state/frag_write.py --agent sw-lead` 原子写) | ★`hw.yaml` / `mech.yaml` / `pm.yaml` 本单一个字节都没写 ★ |
| ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节没写 | ★md5 未变 ★ |
| ★**沙盒在项目盘** ★ | 所有副本落在 `tmp/iss370_sbx/` | ★不写 /tmp (★系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)★ |

---

★**本页结束 · ISS-370 · sw-lead · 2026-11-23 CONT1** ★
