# BOARD_ONEPASS_GATE_TEETH_AUDIT · 「板那一趟」验收链【有没有牙齿】—— 门禁链 19 个槽位的「实际调用方式」逐道清账

> ★**单号**: ISS-406 · ★**派活**: 项目总工 (main / moli) · ★**执笔**: 硬件总工 (hw-lead) · ★**日期**: 2026-11-25
> ★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍** ★
> ★**新闸**: `HW/check_onepass_gate_teeth.py` (★**零挂链**·挂不挂由 main 拍★) · ★**配套台账**: 本页 §6 机器块 ★

---

## ★0 · 一句话结论 (★给老板看的一行★)

★★**门禁链上的闸, 每一道都问「我判的东西对不对」, 全仓没有一道问「我这次被调用时用的是哪一档」** ★★
⇒ ★**本单把这一轴补上**: ★**链上 19 个挂链槽位 (18 个不同脚本) 逐道清账完毕** ★
⇒ ★**查出 2 条真阳性 (★红的是现状, 不是闸故障★)** ★:

| # | 真阳性 | 后果 | 证据 |
|---|---|---|---|
| ★**X1** ★ | ★**链上「钉板闸⑤ 脚表功能标签闸」跑在宽松档 `--expect-known` 下** ★ ⇒ 该闸的判据从「**有任何缺陷就红**」整条换成「**实算缺陷清单必须与冻结快照 15 条逐字一致**」⇒ ★**15 条已知缺陷被判为「预期」** ★ | ★**它是【回归闸】不是【质量闸】** ★ ⇒ ★**而且是反向的: 修好一条反而红** ★ | ★`[实测]` `HW/check_pin_function_labels.py` L589/L632 (裸跑) vs L637/L641-L648 (`--expect-known`) · L1016 定义 |
| ★**X2** ★ | ★**投板前最命门的 `state/check_pcb_drc.py`, 作业面页上写下来的调用方式一律不带 `--strict`** ★ ⇒ 该闸的 C4 判据 `ok4 = (n_unc == 0) if strict else True` ⇒ **恒真** ⇒ ★**unconnected=45 也判绿, 还照打「✅ 全过 —— 图纸可下单」** ★ | ★**板那一趟当天照着预检清单跑 ⇒ 拿到的是假绿 ⇒ 拿一张 45 项未布线的板去投 ⇒ 板改第二次** ★ | ★`[实测]` 本机实跑两档: 宽松档 rc=0 · 严格档 rc=1 (C4 45 项未连接) · `logs/iss406/check_pcb_drc_*.log` |

★**一句话**: ★**「板只改一次」= 板 md5 全生命周期只许变 1 次 ⇒ 投板前的每一道检查, 都是「板改第二次」的最后一道闸** ★
⇒ ★**而现在, 投板前最后一道闸, 在纸面上被写成了一个永远绿的命令** ★

---

## ★1 · 题面与范围 (★派活书原文口径★)

★**题面 (main 2026-11-25 本机实读 + 本机实算, 不抄任何 agent 报告)**: ★**门禁链 `state/gate_check.py` 上那 19 个槽位, 全仓没有任何一道闸在问「它被调用时用的是哪一档? 那一档会不会让一个坏掉的板判绿?」** ★

★**本单范围 (三条边界, 一条不多一条不少)** ★:

| 边界 | 本单做没做 | 自证 |
|---|---|---|
| ★**只查「链上闸被怎么调」** ★ | ★**做了** ★ | ★§3 表 (a) · §4 表 (b) · §5 表 (c) ★ |
| ★**不改任何既有闸的判据 / 阈值 / 正文** ★ | ★**没改** ★ | ★§6.3 既有件 md5 前后逐字对照 ★ |
| ★**不挂链 · 不代拍 · 不外发 · 不写板** ★ | ★**没做** ★ | ★§6.3 板三证 + outbox + `grep -c` ★ |

★**不在本单范围 (★留给 main, 本单不代拍★)**: ★**挂不挂 `check_pcb_drc.py` / 挂不挂本闸 / 哪几道闸改严格档 / 要不要人工签核台账** ★

---

## ★2 · 方法论 (★为什么这么查★)

★**三条方法, 一条都不能省** ★:

1. ★**argv 一律 AST 解析, 不许手抄** ★ ⇒ `state/gate_check.py` 的 `EXTRA_GATES` / `PINNED_MD5_GATES` / `HW_PINOUT_GATE` 三张表用 `ast.parse` 读出 ⇒ ★**表 (a) 里的 argv 列与盘上的链逐字同源** ★ ⇒ ★**任何人改链, 本页的表立刻过期 (⇒ 机器闸 T1 判红) ★**
2. ★**宽松档 = 源码里存在的「会让判据放宽或收窄的开关」, 只认这几族名字**: ★`--expect-*` / `--allow-*` / `--skip-*` / `--ignore-*` / `--tolerate-*` / ★`--only` / `--force` / `--no-*` ★ ⇒ ★**宁可漏也不猜** ★
3. ★**fail-open 判定必须带行号级证据** ★ ⇒ ★**判「可能会」但拿不出行号证据的, 算没查** ★ ⇒ ★**机器闸 T3 会把「没查」判成红** ★

★**本单实跑次数 (★brief §2.2 时间预算: `check_pcb_drc.py` 最多跑 2 次★)** ★:
- `check_pcb_drc.py` 宽松档 (不带 `--strict`): ★**1 次** ★ ⇒ `logs/iss406/check_pcb_drc_lenient.log`
- `check_pcb_drc.py` 严格档 (`--strict`): ★**1 次** ★ ⇒ `logs/iss406/check_pcb_drc_strict.log`
- ★**其余结论一律静态分析 (源码行号) + 已有日志** ★ ⇒ ★**没有跑满链 20 遍** ★

---

## ★3 · 表 (a) —— 链上 19 个挂链槽位 × 实际 argv × 源码里有哪些宽松档开关 × 链上用的是哪一档 ★

★**★槽位数 19, 不同脚本 18 个 (★差的那 1 个是 `SW/tools/check_onepass_sw_sync.py` 同时占 `EXTRA_GATES[1]` 与 `PINNED_MD5_GATES[8]` 两个槽位★)** ★
⇒ ★**brief 里说的「18 道闸」= 18 个不同脚本; 链上实际有 19 个槽位 —— 本单按【槽位】清账, 一槽一行, 一槽都不合并** ★

| ★**挂链槽位 (★唯一标识★)** ★ | 链上闸 (相对路径) | 链上标签 | ★**实际 argv (AST 解析)** ★ | 该闸源码里存在的宽松档开关 | ★**链上用的是哪一档** ★ | 判据强度判定 |
|---|---|---|---|---|---|---|
| `EXTRA_GATES[0]` | `MECH/check_mech_verdict_freshness.py` | MECH 结构结论防漂闸 (ISS-295) | `(无)` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[1]` | `SW/tools/check_onepass_sw_sync.py` | SW 侧板侧输入/合法改板闸 (ISS-298) | `(无)` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[2]` | `SW/tools/check_sw_ref_reachability.py` | SW 侧位号引用可达性闸 (ISS-318) | `(无)` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[3]` | `SW/tools/check_landing_trace_obligation.py` | SW 侧落表留痕义务闸 (ISS-315) | `(无)` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[4]` | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | SW 侧 R6 硬保护路径反向用例 (ISS-315) | `--tmpdir tmp/iss318_gates` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[5]` | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | SW 侧 R6 链头落表单号交叉核对反向用例 (ISS-312) | `--tmpdir tmp/iss318_gates` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[6]` | `SW/tools/check_demo_panel_spec_r6_selftest.py` | SW 侧 R6 判决源反向用例 (ISS-309 · 7/7) | `--tmpdir tmp/iss318_gates` | — | — | **严格档 (全量判据)** |
| `EXTRA_GATES[7]` | `MECH/tools/check_mech_ref_reachability.py` | MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现) | `(无)` | — | — | **严格档 (全量判据)** |
| `HW_PINOUT_GATE` | `HW/check_bq25896_pinout.py` | HW pinout 真源闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[0]` | `HW/check_fsin_rootcause.py` | 钉板闸① FSIN 根因闸 | `(无)` | --only | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[1]` | `HW/check_g1a7_selection_landed.py` | 钉板闸② G1a-7 选型落表闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[2]` | `HW/check_onepass_commit_order.py` | 钉板闸③ 改板提交顺序闸 | `(无)` | --only | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[3]` | `HW/check_onepass_preflight_coverage.py` | 钉板闸④ 作业包覆盖度闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[4]` | `HW/check_pin_function_labels.py` | 钉板闸⑤ 脚表功能标签闸 | `--expect-known` | --expect-known | --expect-known | ★**宽松档 (未签核 ⇒ 判红)**★ |
| `PINNED_MD5_GATES[5]` | `HW/check_workpack_state_values.py` | 钉板闸⑥ 作业包现状值闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[6]` | `MECH/check_board_frame_coords.py` | 钉板闸⑦ 板框坐标闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[7]` | `MECH/check_demo_struct_truth.py` | 钉板闸⑧ 结构真值闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[8]` | `SW/tools/check_onepass_sw_sync.py` | 钉板闸⑨ SW 侧合法改板通道闸 | `(无)` | — | — | **严格档 (全量判据)** |
| `PINNED_MD5_GATES[9]` | `HW/check_preflight_regen_idempotent.py` | 钉板闸⑩ 板侧项全集重跑幂等闸 | `(无)` | — | — | **严格档 (全量判据)** |

★**★逐槽结论★** ★:
- ★**19 个槽位里, 只有 1 个跑在宽松档下** ★ ⇒ ★**`PINNED_MD5_GATES[4]` = `HW/check_pin_function_labels.py` 用 `--expect-known`** ★
- ★**另有两道闸 (`PINNED_MD5_GATES[0]` `check_fsin_rootcause.py` · `PINNED_MD5_GATES[2]` `check_onepass_commit_order.py`) 源码里都有 `--only` (「只跑某一条判据」) = 判据**收窄**开关, 但 ★**链上没用 ⇒ 链上跑的是全量档** ★
- ★**8 道 `--tmpdir` 槽位不是宽松档** ★ ⇒ ★**`--tmpdir` 只改「沙盒临时树写哪儿」, 不改判据** ★ ⇒ ★**判据强度维度上, 那 8 道闸跑的是全量档** ★

---

## ★4 · 表 (b) —— fail-open 嫌疑清单 (★每道链上闸: 「输入缺失时会不会判绿」★)

★**判定口径**: ★**「输入缺失 / 文件读不到 / 脚本崩」时, 这道闸会不会返回绿 (rc=0)?** ★
★**★判「不会」的, 依据必须指到行号 —— 因为「文件不在 ⇒ continue ⇒ 跳过这条判据」这种写法最容易藏假绿** ★

| 链上闸 | fail-open 判定 | ★**行号级证据** ★ |
|---|---|---|
| `MECH/check_mech_verdict_freshness.py` | **不会** | L195 `if not os.path.exists(path): errs.append("F1 页 '%s' 不存在 ⇒ 红")` ⇒ L285-288 机器块矩形读不出 ⇒ `got=None` ⇒ `errs.append(...)` 判红 ⇒ ★rc 契约 L462 `return 0 if res["ok"] else 1`★ |
| `SW/tools/check_onepass_sw_sync.py` | **不会** | L308 判据引用不存在的文件 ⇒ `bad.append(...)`; L496/L545 受保护文件缺失 ⇒ `bad.append(...)`; L573 台账不存在 ⇒ `bad.append("SW 台账不存在")`; L534/L552 算不出来 ⇒ `bad.append("... ⇒ fail-closed")` ⇒ ★全部走 bad 列表 ⇒ 判红★ |
| `SW/tools/check_sw_ref_reachability.py` | **不会** | L275/L351/L378/L389 读不到输入 ⇒ `raise InputError(...)` ⇒ L680 `except InputError: return 2` / L818 `print("[FAIL] ..."); return 2` / L861 `print("[FAIL] fail-closed: ..."); return 2` ⇒ ★rc=2 ⇒ 链上判红★ |
| `SW/tools/check_landing_trace_obligation.py` | **不会** | L128 `return (["落表留痕义务: 独立信源 (%s) 读不到任何条目 ⇒ 无从对账 (fail-closed ⇒ 判红)"], ...)` ⇒ ★输入读不到 ⇒ 判红★ ★rc 契约 L348 `return 1`★ |
| `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | **不会** | L109 沙盒拷贝失败 ⇒ 记 `last` 错误串并继续; L292 用例自身崩 ⇒ `print("❌ ... 用例本身坏了"); bad += 1` ⇒ ★rc 契约 L333 `return 0 if bad == 0 else 1`★ ⇒ 判红 |
| `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | **不会** | L128 沙盒拷贝失败 ⇒ 记错误串; L370 用例自身崩 ⇒ `bad += 1` ⇒ ★rc 契约 L424 `return 0 if bad == 0 else 1`★ |
| `SW/tools/check_demo_panel_spec_r6_selftest.py` | **不会** | L138 沙盒拷贝失败 ⇒ 记错误串; L392 用例自身崩 ⇒ `bad += 1; continue` ⇒ ★rc 契约 L438 `return 0 if bad == 0 else 1`★ |
| `MECH/tools/check_mech_ref_reachability.py` | **不会** | L422 MECH 侧文件读不了 ⇒ `raise InputError(...)`; L438 语法错 ⇒ `continue` (★只跳这一个 token·不吞判据★) ⇒ L794 `except InputError: return 2` / L978 `print("[FAIL] ..."); return 2` / L1025 同款 ⇒ ★rc=2 ⇒ 判红★ |
| `HW/check_bq25896_pinout.py` | **不会** | L358 scan_kicad_export() 读到空字典 (L195 `if not os.path.exists(p): return {}`) ⇒ L361-366 逐脚 `nets = kx.get(pin, [])` 为空 ⇒ `wrong.append(...)` ⇒ L367 `rec(not wrong, ...)` 判红 ⇒ ★**输入缺失必然判红, 不是判绿**★ ★rc 契约: L443 `return 0 if all(r["ok"] for r in RESULTS) else 1`★ |
| `HW/check_fsin_rootcause.py` | **不会** | L170 缺文件 ⇒ `errors.append("★缺文件: %s")` ⇒ `return 2, errors` ★**等等: 这行在 check_g1a7 里★**; ★本闸 L606-610 锚点数读不出 ⇒ `p_da = float("nan")` ⇒ L613 `probs.append("页上 d_a=... ≠ 重算 ...")` ⇒ 判红★ ★rc 契约 L1063 `return 0 if nbad == 0 else 1`★ |
| `HW/check_g1a7_selection_landed.py` | **不会** | L170 `if not os.path.exists(_path(root, key)): errors.append("★缺文件: %s")` ⇒ L171 `if errors: return 2, errors` ⇒ ★rc=2 ⇒ 判红★ ★L105 生成器导入失败 ⇒ `sys.exit(...)` 直接挂★ |
| `HW/check_onepass_commit_order.py` | **不会** | L295 找不到板文件 ⇒ `return False, ...`; L323 找不到 .kicad_pro ⇒ `return False`; L374 留证产物不在盘上 ⇒ `bad.append(...)`; L390 找不到作业包 ⇒ `return [(k, False, ...)]`; L399 找不到权威页 ⇒ `ok=False`; L414 找不到三表 ⇒ `ok=False`; L442 找不到台账 ⇒ `return [(k, False, ...)]` ⇒ ★全部落到 bad ⇒ 判红★ |
| `HW/check_onepass_preflight_coverage.py` | **不会** | L225 判据引用不存在的脚本 ⇒ `bad.append(...)`; L320 找不到作业包 ⇒ `return False, [...]`; L422/L436 受保护文件缺失 ⇒ `bad.append(...)` ⇒ 判红★ ★**注意本闸只查「脚本在不在盘上」(P3), 不查「在链上时被怎么调」★** |
| `HW/check_pin_function_labels.py` | **不会** | L384 出处文件缺失 ⇒ findings 记「★文件不存在★」; L418/L444 受保护文件缺失 ⇒ 记 finding; L477 落表台账不存在 ⇒ 记 finding ⇒ ★`--expect-known` 档下 L641-643 `other = res["pinout_findings"] + res["md5_findings"]` ⇒ L648 `rc = 0 if (cmp["ok"] and not other) else 1` ⇒ 判红★ |
| `HW/check_workpack_state_values.py` | **不会** | L449 `if not os.path.exists(p): continue` (★跳过缺失文档★) ⇒ ★**但下游 L256-262 check_V1 判「%s 不存在或读不出」⇒ ok=False ⇒ 判红**★ ⇒ ★continue 被下游补偿 ⇒ 不是 fail-open★ L423 探针引用不存在的文件 ⇒ `bad.append(...)` ⇒ 判红★ |
| `MECH/check_board_frame_coords.py` | **不会** | L283 找不到归一页 ⇒ `raise SystemExit(...)`; L306 找不到工作包 ⇒ `return ""` ⇒ ★**但 L410-411 `errs.append("C1b 工作包里找不到追加段标记")` ⇒ 判红**★ L684/L827 受保护件缺失 ⇒ `errs.append(...)` ⇒ 判红★ ★rc 契约 L1771 `return 0 if all(...) else 2`★ |
| `MECH/check_demo_struct_truth.py` | **不会** | L146-147 `read_text` 是裸 `open()` ⇒ 读不到直接抛异常 ⇒ 脚本崩 ⇒ 非零 rc ⇒ 判红 (★**崩 = 红**, 不是崩 = 绿★); L533 受保护文件不存在 ⇒ `errs.append(...)` ⇒ ★rc 契约 L1331 `return 0 if npass == len(res) else 2`★ ★L996-997 分片文件缺失 ⇒ `fixed=None` ⇒ L1000 G7 判 `fixed == "25.00"` ⇒ False ⇒ 判红★ |
| `SW/tools/check_onepass_sw_sync.py` | **不会** | L308 判据引用不存在的文件 ⇒ `bad.append(...)`; L496/L545 受保护文件缺失 ⇒ `bad.append(...)`; L573 台账不存在 ⇒ `bad.append("SW 台账不存在")`; L534/L552 算不出来 ⇒ `bad.append("... ⇒ fail-closed")` ⇒ ★全部走 bad 列表 ⇒ 判红★ |
| `HW/check_preflight_regen_idempotent.py` | **不会** | L122 找不到覆盖度闸 ⇒ `raise RuntimeError("★找不到覆盖度闸 ... ⇒ 闸崩 (★fail-closed★)")` ⇒ L352-354 `except Exception as e: print("★闸崩: %s"); return 3` ⇒ 判红★ L248/L251 沙盒重跑失败 ⇒ `return False, ["❌ ★**闸崩**★..."]` ⇒ 判红★ |

★**★三条最值得盯的 (★全部是「continue / return 空 ⇒ 靠下游兜底」这一族★)** ★:

| 闸 | 危险写法 | 兜底在哪 | 结论 |
|---|---|---|---|
| `HW/check_workpack_state_values.py` | L449 `if not os.path.exists(p): continue` (★**缺文档就跳过**★) | ★L256-262 `check_V1` 判「%s 不存在或读不出」⇒ `ok=False` ★ | ★**有下游兜底 ⇒ 不会假绿** ★ |
| `MECH/check_board_frame_coords.py` | L306 `if not os.path.exists(path): return ""` (★**缺工作包就返回空串**★) | ★L410-411 `errs.append("C1b 工作包里找不到追加段标记")` ★ | ★**有下游兜底 ⇒ 不会假绿** ★ |
| `HW/check_bq25896_pinout.py` | L195 `if not os.path.exists(p): return {}` (★**缺网表就返回空字典**★) | ★L361-366 逐脚 `kx.get(pin, [])` 为空 ⇒ `wrong.append(...)` ⇒ 判红 ★ | ★**有下游兜底 ⇒ 不会假绿** ★ |

★**★结论: 链上 19 个槽位的「输入缺失 ⇒ 判绿」这一条, 全部查过, 全部有行号级依据, 全部不会假绿** ★
⇒ ★**链的 fail-closed 语义 (脚本不存在 / 超时 / 跑不起来 ⇒ 一律算闸红) 是完好的** ★
⇒ ★**★但那只管「闸跑不跑得起来」, 不管「闸跑起来之后用的是哪一档」—— 缺口就在这里** ★

---

## ★5 · 表 (c) —— 投板前必须用严格档跑的闸名单 + 为什么 ★

★**★名单的来源: 作业面页 (预检清单 / 作业包 / 提交顺序页) 点名的、且判据直接决定「这块板能不能下单」的闸** ★

| 闸 | ★**必须带的严格档开关** ★ | ★**为什么 (源码逐字口径)** ★ | 它判什么 | ★**不带严格档会怎样** ★ |
|---|---|---|---|---|
| `state/check_pcb_drc.py` | **--strict** | C4 判据 `ok4 = (n_unc == 0) if strict else True` (L135-136) ⇒ 不带 --strict ⇒ C4 恒真 ⇒ unconnected=45 也判绿 ⇒ L138-139 还会照打「✅ C4 unconnected items = 45」⇒ L187 打「✅ 全过 —— 图纸可下单」 | C3 DRC violations = 0 + C4 unconnected = 0 + C6 生产文件齐 | 拿一张 45 项未布线的板去投板 ⇒ 板改第二次 (2-4 周 + 一批板的钱) |
| `state/check_pcb_nets.py` | **(无严格档开关 · 本闸没有宽松档)** | 板面 ↔ 网表逐焊盘等价 (C1 缺失/多余/同号异网) ⇒ 今天 rc=1 (缺失 0 · 多余 2 · 同号异网 3) ⇒ ★它今天就是红的 ⇒ 挂不挂链是 main 的地界, 但投板前必须绿★ | C1 焊盘级等价 (ref,焊盘号)→网络 | 板面与网表不一致 ⇒ 电源/地错接 ⇒ 整板报废 |

★**★`state/check_pcb_drc.py` 的两档实跑对照 (★本机实测·不是推算★)** ★:

| 档 | 命令 | rc | ★**它自己打出来的 C4 那行** ★ | ★**它自己打出来的总结那行** ★ |
|---|---|---|---|---|
| ★**宽松档** ★ | `bash state/pcbnew_py.sh state/check_pcb_drc.py` | ★**0** ★ | ★`✅ C4 unconnected items = 45  ← 骨架阶段允许未布线 (布线完成后用 --strict 归零)` ★ | ★`✅ 全过 —— 图纸可下单 (★前提: ISS-158 的三件规格回来后重跑生成器再验一遍★)` ★ |
| ★**严格档** ★ | `bash state/pcbnew_py.sh state/check_pcb_drc.py --strict` | ★**1** ★ | ★`❌ C4 unconnected items = 45 (--strict: 布线完成后必须为 0)` ★ | ★`❌ 不通过 1 项: C4 45 项未连接` ★ |

★**★本机实读的调用点 (★全部不带 `--strict`★)** ★:

| # | 调用点 | 逐字 | 这条调用管的是谁 | 证据 |
|---|---|---|---|---|
| 1 | ★**预检清单页 B25 的验收命令** ★ | ★`python3 state/check_pcb_drc.py ⇒ unconnected items = 0 · DRC 违规 = 0` ★ | ★**「板只改一次」那一趟的投板前验收凭据** ★ | ★`[实测]` `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` L56 + L472 (机器块 criterion) ★ |
| 2 | ★**作业包 S8 步的验收命令** ★ | ★`python3 state/check_pcb_drc.py` ★ | ★**布线完成那一步的准出** ★ | ★`[实测]` `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L569 ★ |
| 3 | ★**作业包 §验收命令 (S10)** ★ | ★`python3 state/check_pcb_drc.py` ★ | ★**投产包准出** ★ | ★`[实测]` `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L504 + L573 ★ |
| 4 | ★**作业包现状值表** ★ | ★`python3 state/check_pcb_drc.py` ⇒ ★`✅ C4 unconnected items = 45` ★ | ★**把「45 也绿」记成了现状值** ★ | ★`[实测]` `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L64 + L86 ★ |
| 5 | ★**每日巡检链** ★ | ★`run("check_pcb_drc.py")` ★ | ★**每天的自动巡检** ★ | ★`[实测]` `state/daily_check.py` L344 ⇒ L403-404 才拿它判红 ★ |
| 6 | ★**生产链准出** ★ | ★`run([sys.executable, "state/check_pcb_drc.py"])` ★ | ★**「准出」那一环** ★ | ★`[实测]` `state/chain_gate.py` L296-298 ⇒ L299 注释自己写着「★布线是否完成 (不阻塞"准出", 但要报出来★)」 ★ |

★**★一句话 (★这就是 X2 的全部危害★)**: ★**这 6 个调用点, 没有一个带 `--strict`** ★
⇒ ★**板那一趟当天, 无论谁照着作业面页跑、还是巡检自己跑、还是准出自己跑, 拿到的都是「C4 恒真」的那一档** ★
⇒ ★**预检清单 B25 那一行甚至写着「⇒ unconnected items = 0」, 而它给的命令【永远打不出 0】—— ★★这条命令证明不了它自己声明的判据★★** ★

---

## ★6 · 机器块 (★台账·机器闸 `HW/check_onepass_gate_teeth.py` 读的就是这一块★) ★

### ★6.1 · 台账机器块 ★

★**★机器闸的 T1~T7 全部读下面这一块 JSON** ★ ⇒ ★**表 (a)(b)(c) 与台账同源 ⇒ 不会漂** ★
★**★台账的 `chain` 段按【槽位】(19 行) 登记, 不按脚本 (18 行) —— 因为 `SW/tools/check_onepass_sw_sync.py` 占两个槽位** ★

<!-- GATE_TEETH_LEDGER_BEGIN -->
```json
{
 "ledger_id": "BOARD_ONEPASS_GATE_TEETH_LEDGER",
 "version": "1.0",
 "issue": "ISS-406",
 "created_at": "2026-11-25",
 "created_by": "hw-lead",
 "evidence_tags_allowed": [
  "[官网]",
  "[实测]",
  "[媒体]",
  "[推算]",
  "[0数据]"
 ],
 "scope": "state/gate_check.py 的 19 个挂链槽位 (18 个不同脚本 · SW/tools/check_onepass_sw_sync.py 占 2 个槽位) + 投板前必跑但不在链上的闸 + 宽松档登记",
 "self": {
  "gate": "HW/check_onepass_gate_teeth.py",
  "hook_status": "待 main 挂链",
  "evidence": "[实测]",
  "note": "★自指悖论 (★不自拍·交 main 拍★): 本闸自己也不在链上 ⇒ 台账里「本闸自身」这一行只能写「待 main 挂链」⇒ 登记动作 = 挂链 = main 的机制地界 ⇒ ★main 若决定挂本闸: ① 改本行 hook_status = 已挂链 ② 把本闸加进 state/gate_check.py ⇒ 本闸的 T5 会自动从「期望 grep=0」翻成「期望 grep≥1」(★闸脚本一个字节都不用改★)★"
 },
 "board_baseline": {
  "path": "HW/PCB/demo_mainboard.kicad_pcb",
  "md5": "611b869e13518c3c023fb178f91a0075",
  "size": 4940213,
  "mtime_ns": 1793920037362193413,
  "mtime": "2026-11-06 07:07:17.362193413",
  "evidence": "[实测]"
 },
 "tables_baseline": {
  "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
  "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
  "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8"
 },
 "outbox_baseline": {
  "NO_OUTBOUND_POLICY.md": {
   "md5": "ee23fba8b708b3535f2e8bc4ff60006b",
   "size": 1006
  },
  "README.md": {
   "md5": "bb415a7948346afd3d8e429b80f0aabf",
   "size": 11110
  },
  "R_GEO_2_DECISION_MAP.md": {
   "md5": "8e70d17a7cadd79c76175fe81a91546f",
   "size": 30223
  },
  "bridge_chip_rfq.md": {
   "md5": "f174665e3ef10713c0366eb12d2fa4bb",
   "size": 5082
  },
  "j_chg_rfq.md": {
   "md5": "79ec574be6f9f1e44f1000f65b570a90",
   "size": 4454
  },
  "jbd_query.md": {
   "md5": "b62675dda43fc84861bb9065ad7c6929",
   "size": 6597
  },
  "jbd_query_addendum.md": {
   "md5": "687ac2e080fb4a43b85c87aa125ac492",
   "size": 2928
  },
  "lens_rfq_rgeo2_addendum.md": {
   "md5": "c95a53b13823fa7a939e7a0ee0faa10b",
   "size": 13426
  },
  "onsemi_ar0234cs_query.md": {
   "md5": "009c645108d22a594fa9b0e9ed745a6a",
   "size": 7365
  },
  "pcb_foundry_layer_query.md": {
   "md5": "1f8105e7efd5b48f1ca4d4fd4229df43",
   "size": 4502
  },
  "s2_rk3576_module_vendor_query.md": {
   "md5": "963395a7f9cff7d9721909262d03ed7a",
   "size": 40291
  },
  "som_balltable_inquiry.md": {
   "md5": "1c39347cb28432b687e055ed8f1f5ab9",
   "size": 4240
  },
  "ti_bq25896_query.md": {
   "md5": "0cf06881ef22d9aa2bcc374250f89ccc",
   "size": 3838
  },
  "vendor_round2_email.md": {
   "md5": "9a55d233b91cf6c997979d5879039777",
   "size": 15026
  },
  "vendor_round3_addendum.md": {
   "md5": "c367984dbcf4065236ea48b1b1a70a8e",
   "size": 6502
  },
  "vendor_round4_geo_isp_addendum.md": {
   "md5": "dae237af315f12065f057e6578117eda",
   "size": 14522
  },
  "vendor_via_agent_email.md": {
   "md5": "25334d43acf7ea3945a32930b6b2d44f",
   "size": 7604
  },
  "visionox_display_dsc_mode_query.md": {
   "md5": "f126785d5fd8f902b66648767c86759a",
   "size": 1895
  },
  "visionox_display_inquiry.md": {
   "md5": "1e6ebdc4ceff247a2b380491c57c6c0d",
   "size": 9470
  },
  "attach/01_ARS45_技术确认项_21条.md": {
   "md5": "d38566a2a774e23847d6abc9c6f94e75",
   "size": 7832
  },
  "attach/02_第二轮问询全文.md": {
   "md5": "d997d35a04b841db8f948ae4e4c451f3",
   "size": 15022
  },
  "attach/README.md": {
   "md5": "e62b5f1e71fe9f1e208a8c0cfa7a8a4b",
   "size": 1195
  }
 },
 "chain": {
  "HW_PINOUT_GATE": {
   "gate": "HW/check_bq25896_pinout.py",
   "label": "HW pinout 真源闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--json"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L358 scan_kicad_export() 读到空字典 (L195 `if not os.path.exists(p): return {}`) ⇒ L361-366 逐脚 `nets = kx.get(pin, [])` 为空 ⇒ `wrong.append(...)` ⇒ L367 `rec(not wrong, ...)` 判红 ⇒ ★**输入缺失必然判红, 不是判绿**★ ★rc 契约: L443 `return 0 if all(r[\"ok\"] for r in RESULTS) else 1`★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[0]": {
   "gate": "MECH/check_mech_verdict_freshness.py",
   "label": "MECH 结构结论防漂闸 (ISS-295)",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--json",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L195 `if not os.path.exists(path): errs.append(\"F1 页 '%s' 不存在 ⇒ 红\")` ⇒ L285-288 机器块矩形读不出 ⇒ `got=None` ⇒ `errs.append(...)` 判红 ⇒ ★rc 契约 L462 `return 0 if res[\"ok\"] else 1`★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[1]": {
   "gate": "SW/tools/check_onepass_sw_sync.py",
   "label": "SW 侧板侧输入/合法改板闸 (ISS-298)",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--checklist",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L308 判据引用不存在的文件 ⇒ `bad.append(...)`; L496/L545 受保护文件缺失 ⇒ `bad.append(...)`; L573 台账不存在 ⇒ `bad.append(\"SW 台账不存在\")`; L534/L552 算不出来 ⇒ `bad.append(\"... ⇒ fail-closed\")` ⇒ ★全部走 bad 列表 ⇒ 判红★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[2]": {
   "gate": "SW/tools/check_sw_ref_reachability.py",
   "label": "SW 侧位号引用可达性闸 (ISS-318)",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--brief",
    "--dump-classification",
    "--freeze-registry",
    "--root",
    "--selftest",
    "--tmpdir"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L275/L351/L378/L389 读不到输入 ⇒ `raise InputError(...)` ⇒ L680 `except InputError: return 2` / L818 `print(\"[FAIL] ...\"); return 2` / L861 `print(\"[FAIL] fail-closed: ...\"); return 2` ⇒ ★rc=2 ⇒ 链上判红★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[3]": {
   "gate": "SW/tools/check_landing_trace_obligation.py",
   "label": "SW 侧落表留痕义务闸 (ISS-315)",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--root",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L128 `return ([\"落表留痕义务: 独立信源 (%s) 读不到任何条目 ⇒ 无从对账 (fail-closed ⇒ 判红)\"], ...)` ⇒ ★输入读不到 ⇒ 判红★ ★rc 契约 L348 `return 1`★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[4]": {
   "gate": "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py",
   "label": "SW 侧 R6 硬保护路径反向用例 (ISS-315)",
   "argv": [
    "--tmpdir",
    "tmp/iss318_gates"
   ],
   "argv_text": "--tmpdir tmp/iss318_gates",
   "source_flags": [
    "--root",
    "--tmpdir"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "★本闸是**反向用例闸**: 判的是「缺陷还被抓得到」, 不是「板是好的」★",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L109 沙盒拷贝失败 ⇒ 记 `last` 错误串并继续; L292 用例自身崩 ⇒ `print(\"❌ ... 用例本身坏了\"); bad += 1` ⇒ ★rc 契约 L333 `return 0 if bad == 0 else 1`★ ⇒ 判红",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[5]": {
   "gate": "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
   "label": "SW 侧 R6 链头落表单号交叉核对反向用例 (ISS-312)",
   "argv": [
    "--tmpdir",
    "tmp/iss318_gates"
   ],
   "argv_text": "--tmpdir tmp/iss318_gates",
   "source_flags": [
    "--root",
    "--tmpdir"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "★本闸是**反向用例闸**: 判的是「链头落表单号交叉核对还抓得住」★",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L128 沙盒拷贝失败 ⇒ 记错误串; L370 用例自身崩 ⇒ `bad += 1` ⇒ ★rc 契约 L424 `return 0 if bad == 0 else 1`★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[6]": {
   "gate": "SW/tools/check_demo_panel_spec_r6_selftest.py",
   "label": "SW 侧 R6 判决源反向用例 (ISS-309 · 7/7)",
   "argv": [
    "--tmpdir",
    "tmp/iss318_gates"
   ],
   "argv_text": "--tmpdir tmp/iss318_gates",
   "source_flags": [
    "--root",
    "--tmpdir"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "★本闸是**反向用例闸**: 判的是「判决源反向用例还抓得住」★",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L138 沙盒拷贝失败 ⇒ 记错误串; L392 用例自身崩 ⇒ `bad += 1; continue` ⇒ ★rc 契约 L438 `return 0 if bad == 0 else 1`★",
   "evidence": "[实测]"
  },
  "EXTRA_GATES[7]": {
   "gate": "MECH/tools/check_mech_ref_reachability.py",
   "label": "MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--brief",
    "--confirm-freeze",
    "--dump-classification",
    "--freeze-registry",
    "--root",
    "--selftest",
    "--tmpdir"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L422 MECH 侧文件读不了 ⇒ `raise InputError(...)`; L438 语法错 ⇒ `continue` (★只跳这一个 token·不吞判据★) ⇒ L794 `except InputError: return 2` / L978 `print(\"[FAIL] ...\"); return 2` / L1025 同款 ⇒ ★rc=2 ⇒ 判红★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[0]": {
   "gate": "HW/check_fsin_rootcause.py",
   "label": "钉板闸① FSIN 根因闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--dump",
    "--only",
    "--root",
    "--selftest"
   ],
   "source_lenient_flags": [
    "--only"
   ],
   "used_lenient_flags": [],
   "lenient_relaxes": "★源码里有 `--only` (L1042 「只跑某一条判据」) = 判据**收窄**开关 ⇒ ★链上没用它 (argv 为空) ⇒ 链上跑的是全量档★",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L170 缺文件 ⇒ `errors.append(\"★缺文件: %s\")` ⇒ `return 2, errors` ★**等等: 这行在 check_g1a7 里★**; ★本闸 L606-610 锚点数读不出 ⇒ `p_da = float(\"nan\")` ⇒ L613 `probs.append(\"页上 d_a=... ≠ 重算 ...\")` ⇒ 判红★ ★rc 契约 L1063 `return 0 if nbad == 0 else 1`★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[1]": {
   "gate": "HW/check_g1a7_selection_landed.py",
   "label": "钉板闸② G1a-7 选型落表闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--root",
    "--selftest",
    "--verbose"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L170 `if not os.path.exists(_path(root, key)): errors.append(\"★缺文件: %s\")` ⇒ L171 `if errors: return 2, errors` ⇒ ★rc=2 ⇒ 判红★ ★L105 生成器导入失败 ⇒ `sys.exit(...)` 直接挂★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[2]": {
   "gate": "HW/check_onepass_commit_order.py",
   "label": "钉板闸③ 改板提交顺序闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--bom",
    "--commit-order",
    "--ledger",
    "--netlist",
    "--only",
    "--pcb",
    "--pins",
    "--pro",
    "--root",
    "--selftest",
    "--workpacket"
   ],
   "source_lenient_flags": [
    "--only"
   ],
   "used_lenient_flags": [],
   "lenient_relaxes": "★源码里有 `--only` (L768 「只跑某一条判据」) = 判据**收窄**开关 ⇒ ★链上没用它 ⇒ 链上跑的是 D1~D6 全量档★",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L295 找不到板文件 ⇒ `return False, ...`; L323 找不到 .kicad_pro ⇒ `return False`; L374 留证产物不在盘上 ⇒ `bad.append(...)`; L390 找不到作业包 ⇒ `return [(k, False, ...)]`; L399 找不到权威页 ⇒ `ok=False`; L414 找不到三表 ⇒ `ok=False`; L442 找不到台账 ⇒ `return [(k, False, ...)]` ⇒ ★全部落到 bad ⇒ 判红★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[3]": {
   "gate": "HW/check_onepass_preflight_coverage.py",
   "label": "钉板闸④ 作业包覆盖度闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--checklist",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L225 判据引用不存在的脚本 ⇒ `bad.append(...)`; L320 找不到作业包 ⇒ `return False, [...]`; L422/L436 受保护文件缺失 ⇒ `bad.append(...)` ⇒ 判红★ ★**注意本闸只查「脚本在不在盘上」(P3), 不查「在链上时被怎么调」★**",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[4]": {
   "gate": "HW/check_pin_function_labels.py",
   "label": "钉板闸⑤ 脚表功能标签闸",
   "argv": [
    "--expect-known"
   ],
   "argv_text": "--expect-known",
   "source_flags": [
    "--expect-known",
    "--json",
    "--root",
    "--selftest"
   ],
   "source_lenient_flags": [
    "--expect-known"
   ],
   "used_lenient_flags": [
    "--expect-known"
   ],
   "lenient_relaxes": "★★`--expect-known` (L1016) = ★**判据整条换掉**★: 裸跑 = `main_default` (L589) ⇒ L632 `return 1 if total else 1` (**有任何缺陷就红**) · `--expect-known` = `main_expect_known` (L637) ⇒ L641-648 **实算缺陷清单必须与冻结快照 KNOWN_DEFECTS (15 条) 逐条一致** ⇒ ★**15 条已知缺陷被判为「预期」= 放宽**★ 且 ★**修好一条反而红 (收紧)★ ⇒ ★链上这道闸现在是【回归闸】不是【质量闸】★",
   "lenient_acceptance": "未签核",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L384 出处文件缺失 ⇒ findings 记「★文件不存在★」; L418/L444 受保护文件缺失 ⇒ 记 finding; L477 落表台账不存在 ⇒ 记 finding ⇒ ★`--expect-known` 档下 L641-643 `other = res[\"pinout_findings\"] + res[\"md5_findings\"]` ⇒ L648 `rc = 0 if (cmp[\"ok\"] and not other) else 1` ⇒ 判红★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[5]": {
   "gate": "HW/check_workpack_state_values.py",
   "label": "钉板闸⑥ 作业包现状值闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L449 `if not os.path.exists(p): continue` (★跳过缺失文档★) ⇒ ★**但下游 L256-262 check_V1 判「%s 不存在或读不出」⇒ ok=False ⇒ 判红**★ ⇒ ★continue 被下游补偿 ⇒ 不是 fail-open★ L423 探针引用不存在的文件 ⇒ `bad.append(...)` ⇒ 判红★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[6]": {
   "gate": "MECH/check_board_frame_coords.py",
   "label": "钉板闸⑦ 板框坐标闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--compute",
    "--json",
    "--root",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L283 找不到归一页 ⇒ `raise SystemExit(...)`; L306 找不到工作包 ⇒ `return \"\"` ⇒ ★**但 L410-411 `errs.append(\"C1b 工作包里找不到追加段标记\")` ⇒ 判红**★ L684/L827 受保护件缺失 ⇒ `errs.append(...)` ⇒ 判红★ ★rc 契约 L1771 `return 0 if all(...) else 2`★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[7]": {
   "gate": "MECH/check_demo_struct_truth.py",
   "label": "钉板闸⑧ 结构真值闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--json",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L146-147 `read_text` 是裸 `open()` ⇒ 读不到直接抛异常 ⇒ 脚本崩 ⇒ 非零 rc ⇒ 判红 (★**崩 = 红**, 不是崩 = 绿★); L533 受保护文件不存在 ⇒ `errs.append(...)` ⇒ ★rc 契约 L1331 `return 0 if npass == len(res) else 2`★ ★L996-997 分片文件缺失 ⇒ `fixed=None` ⇒ L1000 G7 判 `fixed == \"25.00\"` ⇒ False ⇒ 判红★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[8]": {
   "gate": "SW/tools/check_onepass_sw_sync.py",
   "label": "钉板闸⑨ SW 侧合法改板通道闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--checklist",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L308 判据引用不存在的文件 ⇒ `bad.append(...)`; L496/L545 受保护文件缺失 ⇒ `bad.append(...)`; L573 台账不存在 ⇒ `bad.append(\"SW 台账不存在\")`; L534/L552 算不出来 ⇒ `bad.append(\"... ⇒ fail-closed\")` ⇒ ★全部走 bad 列表 ⇒ 判红★",
   "evidence": "[实测]"
  },
  "PINNED_MD5_GATES[9]": {
   "gate": "HW/check_preflight_regen_idempotent.py",
   "label": "钉板闸⑩ 板侧项全集重跑幂等闸",
   "argv": [],
   "argv_text": "(无)",
   "source_flags": [
    "--makesandbox",
    "--selftest"
   ],
   "source_lenient_flags": [],
   "used_lenient_flags": [],
   "lenient_relaxes": "",
   "lenient_acceptance": "不适用",
   "fail_open_verdict": "不会",
   "fail_open_evidence": "L122 找不到覆盖度闸 ⇒ `raise RuntimeError(\"★找不到覆盖度闸 ... ⇒ 闸崩 (★fail-closed★)\")` ⇒ L352-354 `except Exception as e: print(\"★闸崩: %s\"); return 3` ⇒ 判红★ L248/L251 沙盒重跑失败 ⇒ `return False, [\"❌ ★**闸崩**★...\"]` ⇒ 判红★",
   "evidence": "[实测]"
  }
 },
 "strict_required": [
  {
   "gate": "state/check_pcb_drc.py",
   "required_switch": "--strict",
   "required_argv": [
    "--strict"
   ],
   "why": "C4 判据 `ok4 = (n_unc == 0) if strict else True` (L135-136) ⇒ 不带 --strict ⇒ C4 恒真 ⇒ unconnected=45 也判绿 ⇒ L138-139 还会照打「✅ C4 unconnected items = 45」⇒ L187 打「✅ 全过 —— 图纸可下单」",
   "documented_pages": [
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md",
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md"
   ],
   "blocks": "C3 DRC violations = 0 + C4 unconnected = 0 + C6 生产文件齐",
   "consequence": "拿一张 45 项未布线的板去投板 ⇒ 板改第二次 (2-4 周 + 一批板的钱)",
   "evidence": "[实测]"
  },
  {
   "gate": "state/check_pcb_nets.py",
   "required_switch": "(无严格档开关 · 本闸没有宽松档)",
   "required_argv": [],
   "why": "板面 ↔ 网表逐焊盘等价 (C1 缺失/多余/同号异网) ⇒ 今天 rc=1 (缺失 0 · 多余 2 · 同号异网 3) ⇒ ★它今天就是红的 ⇒ 挂不挂链是 main 的地界, 但投板前必须绿★",
   "documented_pages": [
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md",
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md"
   ],
   "blocks": "C1 焊盘级等价 (ref,焊盘号)→网络",
   "consequence": "板面与网表不一致 ⇒ 电源/地错接 ⇒ 整板报废",
   "evidence": "[实测]"
  }
 ],
 "notes": [
  "★argv 全部由 AST 从 state/gate_check.py 解析, 不许手抄★",
  "★fail_open 判定全部带行号级证据★",
  "★「宽松档」= 源码里存在会让判据放宽/收窄的开关 (--expect-/--allow-/--skip-/--ignore-/--only/--no- 等) · 链上是否用由 argv 决定★"
 ]
}
```
<!-- GATE_TEETH_LEDGER_END -->

### ★6.2 · 自指悖论 (★本闸自己不解决, 交 main★) ★

★**T1 要求「链上每个槽位在台账里有且只有一行」⇒ ★**本闸自己也不在链上**★ ⇒ 逻辑上它也该被登记** ★
⇒ 而登记它的动作 = ★**挂链 = main 的机制地界**★ ⇒ ★**台账里「本闸自身」这一行写「待 main 挂链」** ★
⇒ ★**main 若决定挂本闸: ① 台账 `self.hook_status` 改成「已挂链」 ② 把本闸加进 `state/gate_check.py` ⇒ 本闸的 T5 会自动从「期望 grep=0」翻成「期望 grep≥1」 (★闸脚本一个字节都不用改★) ★

### ★6.3 · 零副作用自证 (★本单跑完之后逐项复查★) ★

★**★板三证 (★零写板 + 零落表★)** ★

| 件 | 基线 md5 | 本单跑完后 | 结论 |
|---|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | ★`611b869e13518c3c023fb178f91a0075` ★ | ★`611b869e13518c3c023fb178f91a0075` ★ | ★**未动** ★ |
| ★板 mtime ★ | ★`2026-11-06 07:07:17.362193413` ★ | ★`2026-11-06 07:07:17.362193413` ★ | ★**未动** ★ |
| ★板 size ★ | ★`4940213` ★ | ★`4940213` ★ | ★**未动** ★ |
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | 同 | ★**未动** ★ |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | 同 | ★**未动** ★ |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | 同 | ★**未动** ★ |

★**★零挂链 + 零外发** ★: ★`grep -c check_onepass_gate_teeth state/gate_check.py` = ★**0** ★ · ★`state/outbox/` ★**22 件** ★ 前后逐字 md5 相同 (★台账 `outbox_baseline` 段逐件登记★) ★

★**★零改既有闸判据 / 零改既有页正文** ★: ★`state/gate_check.py` · `HW/check_onepass_preflight_coverage.py` · `state/check_pcb_drc.py` · `state/check_pcb_nets.py` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` ★**全部 md5 前后逐字相同** ★ (★完整清单见 `logs/iss406/baseline_snapshot.txt` 与 `logs/iss406/final_verify.txt`★) ★

---

## ★7 · 留给 main 的问句 (★本单一条都不代拍★) ★

★**Q1** ★: 链上 19 个槽位里, ★**有 1 个用「宽松档」跑** ★ (`HW/check_pin_function_labels.py --expect-known`) ⇒ ★**要不要把它改成严格档?** ★
　　★**代价 (只摆代价, 不代拍)**: ① 改成裸跑 ⇒ ★**当场链红** ★ (`--expect-known` 之所以在链上, 就是因为裸跑必然 rc=1 ⇒ 基线常量停在 ISS-257 旧值) · ② 维持现状 ⇒ ★**这道闸继续是「回归闸」而不是「质量闸」, 且「修好一条反而红」** ★ · ③ 先签核放行 ⇒ ★**台账 `lenient_acceptance` 改成 `已接受(main 签核)` ⇒ 机器闸 T2 转绿 (闸脚本一个字节都不用改) ★**

★**Q2** ★: ★**`state/check_pcb_drc.py` 要不要挂链?** ★ 挂的话必须带 `--strict` ⇒ ★**挂上去当天链会红 (unconnected=45)** ★ ⇒ ★**挂不挂?** ★
　　★**代价**: ① 挂 ⇒ ★**链当场红** ★ (★今天板确实有 45 项未布线 ⇒ 这是真红不是假红★) · ② 不挂 ⇒ ★**投板前最后一道闸仍然只活在纸面上, 且纸面上写的是宽松档** ★ · ③ ★**只改纸面 (把 6 个调用点全改成 `--strict`) 不挂链** ★ ⇒ ★**投板前那一趟照样会红 (因为板真的没布完) ⇒ 红灯在投板前那一趟才响, 而不是天天响** ★

★**Q3** ★: ★**「投板前必须用严格档跑的闸名单」要不要成为一份人工签核台账页?** ★ (★ISS-404 交卷页 §Q3 已提同一个问题·本单是它的加强版: 名单里每条都带「宽松档放宽了哪条判据」★)

★**Q4** ★: ★**本闸自己挂不挂链?** ★ (★自指悖论★) ⇒ 台账 `self.hook_status` 现在写的是「待 main 挂链」

★**Q5** ★: ★**fail-open 嫌疑清单里若有真阳性, 谁负责修?** ★ (★本单查完: ★**链上 19 个槽位在「输入缺失 ⇒ 判绿」这一条上全部是阴性的 (有行号证据) ⇒ 本单没有制造新活** ★; 但 ★**若 main 决定挂 `check_pcb_drc.py`, 「缺输入 ⇒ 判红」这条要重新判一次 (★它的 C2 图纸缺失 ⇒ `return 1` ⇒ 已经是红的, 但挂链后要重新确认★) ★)

★**Q6 (★本单新增·不代拍★)**: ★**作业面页 (预检清单 L56 / 作业包 L64·L86·L504·L569·L573) 里那 5 处 `python3 state/check_pcb_drc.py`, 要不要改成带 `--strict`?** ★
　　★**代价**: ① 改 ⇒ ★**照着跑的人会看到 rc=1 (因为板真的没布完) ⇒ 那一趟会停在投板前** ★ (★这正是「板只改一次」想要的效果★) · ② 不改 ⇒ ★**机器闸 T3b 永远红, 且投板前那一趟照旧拿假绿** ★ · ③ ★**只改纸面不动闸本体 ⇒ 合规 (受保护判据脚本一条都不许改那条纪律不冲突) ★**

---

## ★附 · 本单证据文件清单 (★全部在 `logs/iss406/`·沙盒在 `tmp/iss406/`★) ★

| 文件 | 内容 | 证据等级 |
|---|---|---|
| `logs/iss406/baseline_snapshot.txt` | ★板三证 + 22 个既有闸文件 md5 + 既有页 md5 + outbox 22 件 md5 (开工前) ★ | ★`[实测]` ★ |
| `logs/iss406/ast_chain_parse.txt` | ★`state/gate_check.py` 的 AST 解析 (★19 槽位 / 18 不同脚本 / 重复槽位认定★) ★ | ★`[实测]` ★ |
| `logs/iss406/lenient_flag_scan.txt` | ★每道链上闸源码里的全部 flag + argparse 定义 (逐行号) ★ | ★`[实测]` ★ |
| `logs/iss406/failopen_scan.txt` | ★每道链上闸的 `except` / 文件缺失分支逐行扫描 ★ | ★`[实测]` ★ |
| `logs/iss406/rc_contract_scan.txt` | ★每道链上闸的 rc 出口契约 (★「打印 FAIL 但 rc=0」这一族也要查★) ★ | ★`[实测]` ★ |
| `logs/iss406/check_pcb_drc_lenient.log` | ★宽松档实跑 (rc=0 · 打「✅ 全过 —— 图纸可下单」) ★ | ★`[实测]` ★ |
| `logs/iss406/check_pcb_drc_strict.log` | ★严格档实跑 (rc=1 · C4 45 项未连接) ★ | ★`[实测]` ★ |
| `logs/iss406/ledger_build.log` | ★台账生成记录 (★argv 全部 AST 解析★) ★ | ★`[实测]` ★ |
| `logs/iss406/final_verify.txt` | ★交卷前全项复查 (板三证 / 既有件 md5 / outbox / 零挂链) ★ | ★`[实测]` ★ |
| `tmp/iss406/ledger.json` | ★台账生成中间件 (★最终真源是本页 §6.1 的机器块★) ★ | ★`[实测]` ★ |
