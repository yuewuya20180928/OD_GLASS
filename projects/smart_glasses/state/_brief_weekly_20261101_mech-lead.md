【ARS45 · 周交付窗口 (2026-11-01) · 项目总工 moli 派 · agent=mech-lead · 角色=结构总工(带散热)】

目标: 完成你本周的周更新落盘 + 自证。这是本周你唯一的写会话窗口, 做完没有第二窗口。

★★ 硬边界 (违反 = 数据静默蒸发, 项目已栽过)
1. 写分片只能用 `python3 state/frag_write.py --agent mech-lead` (原子写); **禁止** open(p,"w") / yaml.safe_dump 直接覆盖分片。
2. 只写: 自己的分片 `state/fragments/mech.yaml` / `state/issue_log.yaml` 里 owner==mech-lead 的 issue / 自己的产出目录 `MECH/` / `HANDOFF/` 下的交接单。
3. 不许改: `PROJECT_TRACKER.md` (尤其 §0 锁死变量表) / `STATE.yaml` / 别人的分片 / 别人的 issue。
4. 不许对外联系 (邮件/询价/采购一律经项目总工); 草稿放 `state/outbox/` 即可。
5. 本窗口期间不接临时活。
6. ★ 队列自动派活 cron (fb67af40) 我已在窗口期间暂停, 窗口结束恢复 ⇒ 窗口期间你只会有"我派的这一条会话" + 你自己已在跑的那条, 不会有第三条。

★ 四件事 (交卷标准)
① 分片更新 (frag_write.py 原子写)
   - status: `--status 'phase=... progress_pct=N health=green|yellow|red summary="一句话说清你现在到哪了"'`
   - answers: 本周新增的答复, 每条 `--add-answer 'key=... to=... value="..." ref="..."'` —— key 必须和对方 needs_from 里的 key 对得上, 对不上等于没答。
   - interface_claims: 新增或变更的 `--add-claim 'key=... value="..." note="..."'` —— **变更必须写清 旧值→新值**。
   - needs_from: 需要别人配合的 `--add-need 'key=... to=... item="..." since=...'` + due (due 必填; 等老板/原厂/模组厂的写清 waiting_on)。
   - 基准 (窗口开始时快照): answers=17 条 / interface_claims=141 (全项目最多) / artifacts=36 / needs_from=62 (全项目最多) / blockers=10
② issue_log.yaml: 更新 owner==mech-lead 的 issue
   - 开工 → `fixing`; 修好 → `fixed`, **必须填 fix_ref** (指向你的产出文件+章节, 别人能一条命令复算)
   - **verify_by 必须填另一个总工或 main** —— 自己修的必须别人验; verify_by==owner 直接算违规。
   - 写 issue_log.yaml 也必须原子写 (tmp + fsync + os.replace), 照抄 `MECH/_frag_update_iss092.py` 的写法。
   - 你名下本周未闭环 issue (窗口开始时快照), 逐条给状态变化:
     · ISS-017 fixing ★P2S 打印件实测尺寸 0 件 + 彩虹纹指标缺失 —— **现在是 fixing 但 verify_by 和 fix_ref 都是空 = 僵尸 fixing**。本周窗口必须给它一个明确归宿: 要么补齐 fix_ref + verify_by 转 fixed, 要么**明确回滚成 open** 并写清卡在哪个客观条件上 (打印机 192.168.1.68 跨网段不可达 / 本机无切片器量具)。**不许再挂着 fixing 而不给 fix_ref。** 队列已先派过活给你, 接着做完。
     · ISS-024 open  材料选型与表面耐受缺失 (汗液/化妆品/酒精/UV 全未考虑) (due 11-05)
     · ISS-025 open  结构 DFM 评审缺失 (P2S 打印件 → 量产开模件的可制造性差异) (due 11-05)
     · ISS-047 open  ★口径混用: 『对角半角』 vs 『垂直半视场』 (MECH §1.5 那张 ≤40° 的表) —— 影响全项目 FOV 表 (due 11-05)
     · ISS-066 open  测量清单补 H14 (temple_cage 上的 ⌀2.4 PCB 定位间隙孔独立量测行) + measurements.yaml (due 11-05)
     · ISS-076 open  新容量口径的尾巴 3 处 (3.1 对标表重量分两配置 / verify_budget.py 的 DOC_WEIGHT ...) (due 11-05)
     · ISS-103 open  ★镜框开导光孔/导光柱 (充电灯装充电板靠 Type-C 座, 老板拍板关机时充电灯要亮) (due 11-05)
   - 本周做不完的保持 `open` 并写清卡在哪个客观条件上 —— **不许留在 fixing 却不给 fix_ref**。
③ 交接单: `HANDOFF/2026-11-01_mech-lead_<主题>.md`, B1-B6 结构照旧 (本周进展小节追加在末尾, 结构不变):
   B1 结论摘要 (一句话 + 关键数字) / B2 验收标准自评 (逐条 通过|不通过|**未验**) / B3 证据分级 ([实测]/[官方]/[推算]/[0数据]) / B4 接口取值声明 (interface_claims, 短规范值) / B5 未决项+卡点 (waiting_on + due) / B6 自证复现命令
④ 自证 (必须实跑, 把输出贴进回复)
   cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
   python3 state/merge.py        # rc 必须 0 (rc=2 = 快照不完整, 自己修到 0 再交)
   python3 state/gate_check.py   # 把 Q1-Q4 数字贴出来
   python3 state/daily_check.py  # 能跑也跑一遍

★ 交付要求
- 至少覆盖上面每条 issue 的状态变化 —— **你可以补充我没要求但你觉得关键的** (超出 = 总工的盲区, 加分项)。
- [推算] 不许冒充实测; 没数据就写 [0数据]。★你尤其容易把"设计态几何+公差栈"写成实测 —— 那类必须标 [推算], 实物 [实测] = 0 条就写 0 条。
- 你报的每个数都要能被别人一条命令复算。
- ★ 你本周的两个"结构性"重点:
  (a) **ISS-017 的僵尸 fixing** —— 全项目 issue_check 会按 "status=fixing 但 fix_ref 空" 判僵尸, 你挂着不动就一直扣分; 给它归宿。
  (b) **ISS-047 口径混用** —— 这是跨三方的公共口径 (sw-lead 的 120° 采集 / hw-lead 的 JBD 走鹃Ⅱ 30° FOV 都要用), 你给准确定义就能一次解三方的争; 给不了就把两个口径各自的**适用范围**写清并登记 needs_from。

★ 回复格式 (严格 ≤5 行, 不要客套不要展开)
status: <phase> / <progress_pct>% / <health>
answers新增: <n> (累计 <m>)
claims总数: <n> (本周 +k)
未闭环issue: <n> (IDs: ...)
merge rc: <rc> | gate: Q1 <..> Q2 <..> Q3 <..> Q4 <..>
