# ISS-272 · sw-lead 任务书 —— 独立复核 ISS-261 的「投递口径① mode=none 归类」改判 (★验证分离·不替 main 自签★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 04:5x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**本单性质**: ★**内部活 · 门禁/运维工具侧 · 独立复核类 (★零写板 · 零落表 · 零外发 · 零采购★)** ⇒ ★**不是老板级拍板** ★
> ★**老板 2026-11-17 00:43 主线口径**: 「接下来的目标是绘制 PCB 图」 ⇒ ★**本单不在 PCB 主线上 (★是运维工具侧的一条自查单★) ⇒ 不占「板只改一次」那一趟的任何一步** ★
> ★**老板 2026-11-12 02:02 政策**: 不再发信 / 全靠自己查资料 ⇒ ★**零外发** ★

---

## ① 目标 (一句话)

★**独立复核 main 亲手改的 `state/delivery_truth.py` 口径① 归类**: ★**改判对不对 / 反向用例够不够硬 / 有没有把真故障藏起来** ★
★**因为 `state/issue_check.py` 的 C3「验证分离」规定 `verify_by` 不得等于 `owner` ⇒ ISS-261 owner = main ⇒ ★**main 不能自签 verified ⇒ 必须你来签** ★

---

## ② 病灶 (★main 2026-11-17 04:2x~04:5x 本机实跑, 原样输出★)

### ★① ISS-261 登记时点的那句话 (★`state/issue_log.yaml` ISS-261 note 原文★)

> ★**main 2026-11-16 22:4x 实测 (★心跳自检时撞到★)** ⇒ `state/delivery_health.py` 输出 4 行口径①: 「ARS45 状态速报 (每小时推微信)」⇒ ★**送到 0 · 没送到 12 / 12** ★
> ★**实测根因**: 这 4 个 job 的 `delivery.mode` 全是 ★**`none`** ★ ⇒ run 记录里 ★**`status=ok` + `delivery.delivered=false`** 是 ★**预期行为** ★
> ★**口径① (来自 `state/delivery_truth.py`) 没按 mode 过滤 ⇒ 把「本来就关着的推送」算成「没送到」** ★
> ★**修法 (★走 H-1: 脚本 + md5 台账 + 反向用例 + 留痕★)**: ① 口径① 对 `delivery.mode == none` 的 job ⇒ 计成 ★**「本来就不投」** ② ★**不许**改任何告警阈值 / 不许动 A/B/D 三类的判据 ③ ★**反向用例**: 把某个 job 的 mode 临时改成 none ⇒ 那一行必须从「没送到」挪到「本来就不投」★

### ★② main 已经做掉的 (★你不用重做, 但要验★)

- ★**改动**: `state/delivery_truth.py` ⇒ ★**新增纯函数 `classify_run(status, delivered, mode)` + `runs_view(..., mode=None)` + `collect()` 把 `d.get("mode")` 传进去 + 新增 `--selftest`** ★
- ★**分类顺序**: `status=error` ⇒ run_error → `delivered is True` ⇒ delivered → ★**`mode=='none'` ⇒ no_delivery (★修点★)**★ → `delivered is False` ⇒ not_delivered → 其余 ⇒ no_delivery ★
- ★**md5**: 改前 `00ff09721fad2b1fa8621d5af5573f7f` ⇒ 改后 ★**`8dad8b39d873b3d930acb1c076e240cb`** ★ · ★**备份 `state/.bak_delivery_truth_20261117_0435_iss261.py`** ★
- ★**main 自测**: `python3 state/delivery_truth.py --selftest` ⇒ ★**rc=0 · 31 条断言 (7 纯函数 + 4 job × 6 端到端)** ★
- ★**main 的隔离性自证**: ★**同一份真实 run 记录, 修前修后各跑一次 `state/delivery_health.py` ⇒ diff 只有 4 行口径① 变了; A 类 / B 类 / D 类 / 口径② / 结论行 逐字节不变** ★
- ★**交卷单**: ★**`HANDOFF/2026-11-17_main_ISS261_投递口径mode_none归类修复.md`** (B1~B6 六块齐全) ★

---

## ③ 你要交的四件 (★每件都能独立验收★)

1. ★**独立复现 main 的验收**: ★**自己跑一遍 `--selftest` (★rc 必须 = 0★) + 自己跑一遍修前/修后 diff (★自己用备份文件 swap, 不许只信 main 的结论★) + 确认 diff 只涉及口径①** ★ ⇒ ★**结论写清: main 的改判对不对** ★
2. ★**反向用例加压 (★本单最值钱的一件★)**: ★**自己造几条假 run 记录喂给 `classify_run`** ⇒ ★**逐条问自己: 「这个输入下, 真故障会不会被藏起来?」** ★ ⇒ ★**至少覆盖**: ★**① mode=none + status=error (job 自己挂了, 会不会因为 mode=none 而被吞成「本来就不投」? ⇒ 期望: 必须仍是 run_error, 也就是说这个 job 的失败仍然看得见★) ★** · ★**② mode=none 但 delivered=true (历史遗留配置, 真送到了, 会不会被算成「本来就不投」? ⇒ 期望: 必须仍算「送到」) ★** · ★**③ mode 字段整个缺字段 (老 job / 老记录) ⇒ 期望: 按 announce 判, 行为跟改前逐字一致** ★ · ★**④ 一个「mode=announce 但连着 3 轮 delivered=false」的 job ⇒ 期望: 「没送到」= 3, ★**不许因为这次改动被洗成 0** ★ ★
3. ★**假故障会不会被藏起来的判断**: ★**逐条检查 `state/delivery_health.py` 的 A / B / D 三类在改判后是不是还看得见真故障** ⇒ ★**给出结论: 「mode=none 的 job 真的坏了, 老板能不能看见?」** ★ ⇒ ★**这一条不许含糊, 要给「能/不能 + 为什么 + 缺口在哪」★ ★
4. ★**交卷单 + 分片**: ★**交卷单 `HANDOFF/2026-11-17_sw-lead_ISS272_投递口径mode_none归类独立复核.md` (B1~B6 六块齐全)** ★ + ★**分片走 `python3 state/frag_write.py --agent sw-lead` (★不许手改 yaml★)** ★

---

## ④ 必跑的命令 (★全部本机实跑, 输出现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 反向用例
python3 state/delivery_truth.py --selftest; echo "RC=$?"

# ② 修后读数
python3 state/delivery_health.py | head -6

# ③ 自己 swap 修前/修后做 diff (★别用 main 的 /tmp 文件, 自己重跑★)
cp state/delivery_truth.py /tmp/dt_review_new.py
cp state/.bak_delivery_truth_20261117_0435_iss261.py state/delivery_truth.py
python3 state/delivery_health.py > /tmp/dh_rev_before.txt 2>&1
cp /tmp/dt_review_new.py state/delivery_truth.py
python3 state/delivery_health.py > /tmp/dh_rev_after.txt 2>&1
diff /tmp/dh_rev_before.txt /tmp/dh_rev_after.txt
md5sum state/delivery_truth.py   # ★必须回到 8dad8b39d873b3d930acb1c076e240cb★

# ④ 加压用例 (★自己造输入, 不许只跑现成的 selftest★)
python3 - <<'EOF'
import sys; sys.path.insert(0, 'state')
from delivery_truth import classify_run
for args in [("error", False, "none"), ("ok", True, "none"), ("ok", False, None), ("ok", False, "announce")]:
    print(args, "->", classify_run(*args))
EOF

# ⑤ 门禁链
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py && python3 state/stage_gate.py
```

★**★上面第 ③ 步做完必须把 `state/delivery_truth.py` 恢复到新版本 (md5 `8dad8b39d873b3d930acb1c076e240cb`)★** ⇒ ★**跑完必须自己 `md5sum` 确认, 不许假设 copy 一定成功** ★

---

## ⑤ 交卷物

| # | 文件 | 说明 |
|---|---|---|
| ① | `HANDOFF/2026-11-17_sw-lead_ISS272_投递口径mode_none归类独立复核.md` | ★**B1~B6 六块齐全** ★ |
| ② | ★**`state/delivery_truth.py`** | ★**只许加 `--selftest` 的加压用例; 判据一个字不许改 (★除非你发现判据真错了 ⇒ 那就写进交卷单的「我建议改成什么 + 为什么」, 由 main 拍, 不许自己改★)** ★ |
| ③ | `state/fragments/sw.yaml` | ★**只走 `frag_write.py --agent sw-lead`** ★ |
| ④ | ★**复核结论一句话** ★ | ★**「main 的改判 = 对 / 错(错在哪) / 有缺口(缺口是什么)」★ ⇒ ★**main 拿着这句话才能把 ISS-261 从 `fixed` 落 `verified` (★或退回 `fixing`★)** ★ |

---

## ⑥ 边界 (★不许碰★)

- ★**零外发 · 零采购 · 零下单 · 不联系任何供应商** ★
- ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零改 PROJECT_TRACKER.md §0** ★
- ★**不许改 `state/delivery_health.py`** (★A/B/D 三类判据不是本单地界★) ★
- ★**不许自签 `state/issue_log.yaml`** (★issue_log 是 main 地界★) ★
- ★**不许替老板拍板** (★本单全是内部活, 一条老板级都没有★) ★
- ★**不许写别人的分片** (★只走 `frag_write.py --agent sw-lead`★) ★
