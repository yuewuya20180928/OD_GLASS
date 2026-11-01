【ARS45 · 周交付窗口 (2026-11-01) · 项目总工 moli 派 · agent=hw-lead · 角色=硬件总工】

目标: 完成你本周的周更新落盘 + 自证。这是本周你唯一的写会话窗口, 做完没有第二窗口。

★★ 硬边界 (违反 = 数据静默蒸发, 项目已栽过)
1. 写分片只能用 `python3 state/frag_write.py --agent hw-lead` (原子写); **禁止** open(p,"w") / yaml.safe_dump 直接覆盖分片。
2. 只写: 自己的分片 `state/fragments/hw.yaml` / `state/issue_log.yaml` 里 owner==hw-lead 的 issue / 自己的产出目录 `HW/` / `HANDOFF/` 下的交接单。
3. 不许改: `PROJECT_TRACKER.md` (尤其 §0 锁死变量表) / `STATE.yaml` / 别人的分片 / 别人的 issue。
4. 不许对外联系 (邮件/询价/采购一律经项目总工); 草稿放 `state/outbox/` 即可。
5. 本窗口期间不接临时活。
6. ★ 队列自动派活 cron (fb67af40) 我已在窗口期间暂停, 窗口结束恢复 ⇒ 窗口期间你只会有"我派的这一条会话" + 你自己已在跑的那条, 不会有第三条。

★ 四件事 (交卷标准)
① 分片更新 (frag_write.py 原子写)
   - status: `--status 'phase=... progress_pct=N health=green|yellow|red summary="一句话说清你现在到哪了"'`
   - answers: 本周新增的答复, 每条 `--add-answer 'key=... to=... value="..." ref="..."'` —— key 必须和对方 needs_from 里的 key 对得上, 合并器靠 key 配对, 对不上等于没答。
   - interface_claims: 新增或变更的 `--add-claim 'key=... value="..." note="..."'` —— **变更必须写清 旧值→新值**, 不写合并器不会替你纠错。
   - needs_from: 需要别人配合的 `--add-need 'key=... to=... item="..." since=...'` + due (due 必填; 等老板/原厂/模组厂的写清 waiting_on)。
   - 基准 (窗口开始时快照): answers=11 条 / interface_claims=90 条 / artifacts=19 / needs_from=35 / blockers=7
② issue_log.yaml: 更新 owner==hw-lead 的 issue
   - 开工 → `fixing`; 修好 → `fixed`, **必须填 fix_ref** (指向你的产出文件+章节, 别人能一条命令复算)
   - **verify_by 必须填另一个总工或 main** —— 自己修的必须别人验; verify_by==owner 直接算违规。
   - 写 issue_log.yaml 也必须原子写 (tmp + fsync + os.replace), 照抄 `MECH/_frag_update_iss092.py` 的写法。
   - 你名下本周未闭环 issue (窗口开始时快照), 逐条给状态变化:
     · ISS-043 open  充电状态读取接口未确认 → 充电时禁 OD 门禁可能无法实现 (due 11-05)
     · ISS-079 open  情报检索: 采用 ARS45 的 AI 翻译眼镜拆解 + 酷芯微港交所招股书 PHIP 直链 (封装/走线/供应链/交付) (due 11-05)
     · ISS-105 open  ★更正 hw-lead 分片过期值: pcb_outline 50×12 → **60×15mm**; chg_input_limit 1.07-1.30A(300Ω) → **390Ω 档 (ICHG 0.82A / 单 pin 0.411A)**; J_CHG 实物是**一对**(框侧座+脚侧座)→ 备料口径改; 机械防呆升为硬判据 (due 11-05)
     · ISS-111 open  ★EVT 可靠性实测项清单 (跌落/振动/弯折/热) 文件缺失 —— 补交 `HW/EVT_RELIABILITY_TEST_ITEMS.md` (被 HW/RELIABILITY_ABSMAX_DERATING_V2.md 三处悬空引用) (due 11-05)
     · ISS-121 fixing ★MEMS 麦克风 vs 检修口磁铁 (N35 ⌀4×1) 磁场/位置复核 —— **due 11-02 (明天)**, 队列已先派过活给你, 接着做完
   - 本周做不完的保持 `open` 并写清卡在哪个客观条件上 —— **不许留在 fixing 却不给 fix_ref** (那是僵尸 fixing)。
③ 交接单: `HANDOFF/2026-11-01_hw-lead_<主题>.md`, B1-B6 结构照旧 (本周进展小节追加在末尾, 结构不变):
   B1 结论摘要 (一句话 + 关键数字) / B2 验收标准自评 (逐条 通过|不通过|**未验**) / B3 证据分级 ([实测]/[官方]/[推算]/[0数据]) / B4 接口取值声明 (interface_claims, 短规范值) / B5 未决项+卡点 (waiting_on + due) / B6 自证复现命令
④ 自证 (必须实跑, 把输出贴进回复)
   cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
   python3 state/merge.py        # rc 必须 0 (rc=2 = 快照不完整, 自己修到 0 再交)
   python3 state/gate_check.py   # 把 Q1-Q4 数字贴出来
   python3 state/daily_check.py  # 能跑也跑一遍

★ 交付要求
- 至少覆盖上面每条 issue 的状态变化 —— **你可以补充我没要求但你觉得关键的** (超出 = 总工的盲区, 加分项)。
- [推算] 不许冒充实测; 没数据就写 [0数据]。
- 你报的每个数都要能被别人一条命令复算。
- ★ ISS-105 尤其优先: 那两个过期值就在你自己的分片里, 不改对 ⇒ 合并器的冲突检测会拿过期值去判冲突, 后面所有人的裁决都建在错值上。

★ 回复格式 (严格 ≤5 行, 不要客套不要展开)
status: <phase> / <progress_pct>% / <health>
answers新增: <n> (累计 <m>)
claims总数: <n> (本周 +k)
未闭环issue: <n> (IDs: ...)
merge rc: <rc> | gate: Q1 <..> Q2 <..> Q3 <..> Q4 <..>
