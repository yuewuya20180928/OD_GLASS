# ROUND_LOG_main · 2026-11-25 00:1x · 老板清单 55 → 39 (★16 条 main 地界待拍项自己闭·★一件没代老板拍板★)

★**签收闸**: `state/_apply_20260725_0015_main_close_self_solvable_needs.py` (★落盘·★fail-closed★) + `state/_apply_20260725_0100_main_record_close_self_solvable.py` (★落记录·★fail-closed★)
★**备份 (★脚本现场取 `time.strftime` ⇒ 真实 stamp `20260725_00xx`★)**: `state/fragments/pm.yaml.bak_20260725_0045_main_close_self_solvable` · `state/fragments/pm.yaml.bak_20260725_0047_main_close_self_solvable` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_<stamp>_main_close_self_solvable` · `state/LESSONS.md.bak_<stamp>_main_l34` · `MEMORY.md.bak_<stamp>_main_l34_pointer`

---

## ★★一 · 分类 (★本机逐条实读·★不是印象★) ★★

| 分类 | 条数 | 判据 |
|---|---|---|
| A 真·老板拍 | **34** | 取舍 / 预算 / 授权 / 外观 / 标准 / 合规 / 产品范围 / 对外承诺 |
| B main 自己能解 | **21** | 查资料 / 机器可判 / 已定政策 / 前提已消失 / 已被工程手段消解 |
| C 要资源 (不是拍板) | **6** | 本机物理上做不到 (无打印机 / 无量具 / 无台架 / 无预算) |

★**⇒ 老板真正要看的决定数 = 22 个 (34 条经同源合并后)** ★

---

## ★★二 · 本轮闭掉的 16 条 (★每条带 ★边界声明·★全部按 need 原 key·★L-32★) ★★

★**A 组 12 条** (本来路由就是 `to=main`): `iss079_phip_manual_fetch` · `model_license_stack_decision` · `iss250_pick_downgrade_route` · `iss250_n3_threshold_recheck` · `demo_od_model_route_m1_vs_m2` · `demo_od_path_a_vs_b` · `iss191_boss_pick_fix_option` · `iss191_boss_q_envc_unify` · `iss191_boss_r_pg_pull_dnp` · `iss234_boss_pick_5q` · `s2_version_block_magic_decision` · `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` ★
★**B 组 4 条改路由** (全在 pm.yaml·零改他人分片): `board_p41_promote` · `self_research_policy_202612` · `boss_dled_g_expose_decision_20261117` · `boss_state_value_acceptance_drift_20261117` ★
★**+ `iss206_...` 在 pm.yaml 那份也改 to** (★同一 need 两份·必须同 to·否则 advance.py 重复列入·★本轮实测踩到★) ★

---

## ★★三 · ★★自曝两条机制缺陷 (★自己犯自己修★) ★★

★**① 字段语义不对 ⇒ 机制静默失效 ⇒ L-34**: 4 条的「★边界」写进 `ref` 而非 `value` ⇒ 判据查 value 时看不见 ⇒ **L-22 的镜像面** (★不只键要对齐, 值放在哪个字段也要对★) ★
★**② 修 bug 的修法本身有 bug**: `A = _fixed` 只留下 4 条 ⇒ **16 条只落了 4 条而脚本自报绿** ⇒ ⇒ 必须**逐件回读盘上实物** (★L-28 第③款★) ★

---

## ★★四 · fail-closed 触发 4 次 (★全部零写盘·★全部是我自己的判据缺陷★) ★★

① 关键词表查自己的答案措辞 ⇒ 误报 6 条 (★否定语境★) ② 「路由事实」判据与「要改路由的那批」自相矛盾 ③ 「★边界」查错字段 ④ 模块级 `import re` 被 walrus 遮蔽 ⇒ NameError ★

---

## ★★五 · 最终读数 (★本机实跑) ★★

★**板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ 逐字节未动 (18 天)** ★ ⇒ **G1 仍开, 不许投板** ★
★`merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账) · `stage_gate.py` rc=1 (G1 仍开·按设计就该红) · `advance.py` decisions **55 → 39** · internal 0 · approvals 0 · waiting 0 ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零改其他 agent 分片 · 零挂链 · 零外发 · 未伪造 decision: 字段 · 一件没代老板拍板** ★

---

## ★★六 · ★★补记 (★2026-11-25 01:2x)★: ★★一条【读数环节的自曝】(★L-35)★★

★**现象**: ★**收尾复核时我用 `echo "  $(basename $g) rc=$?"` 读门禁 rc ⇒ ⇒ 【命令替换 `$(basename $g)` 先执行 ⇒ 它的 exit code (0) 覆盖了 `$?`】⇒ ⇒ "
★**★★⇒ `issue_check.py` (真 rc=1 · 19 条既有老账) 与 `stage_gate.py` (真 rc=1 · G1 仍开) 都被读成了 rc=0 ⇒ ⇒ 【差点把两条真红报成绿】★★★ ★ ★
★**★⇒ 正确写法**: ★**shell: `rc=$?` 先存再打印 · python: `subprocess.run(...).returncode`** ★ ★
★**★⇒ ★★本轮【自己写的两个脚本不受影响】(★用 `returncode`·★不用 `$?`)⇒ ⇒ 落盘结论仍成立 ★★ ⇒ ⇒ "
★**★⇒ ⇒ 落成 **L-35** + 一页 §㊿ §⑦ 补记 ⇒ ⇒ 【三个自曝同族: 字段语义写错字段 (L-34) · 修 bug 的修法本身有 bug · 读 rc 的方式被静默替换 (L-35) ⇒ ⇒ 共同点 = 【证据链某一环被替换 ⇒ 整条链看起来正常而实际失效】】★★ ★ ★
★**★⇒ ★★门禁最终读数 (★用正确方式重测★)★**: ★**merge.py 0 · gate_check.py 0 · issue_check.py 1 (19 条既有逾期老账·本轮零新增) · stage_gate.py 1 (G1 仍开·缺 1 项 = PCB 布线 unconnected 45→0) · advance.py decisions 39 · internal 0 · approvals 0 · waiting 0** ★ ★
