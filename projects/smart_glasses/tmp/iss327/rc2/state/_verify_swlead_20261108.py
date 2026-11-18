#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sw-lead 独立验证写回器 (ISS-147 / ISS-151 / ISS-164)
=====================================================
铁律:
  ① 用 state/.issue_log.lock 的 flock, 锁内重读
  ② 只碰这 3 个 id 的行 (行级文本编辑, 不做 YAML 整体重排 ⇒ 别人的行一个字节都不动)
  ③ verify_result / verify_date 只有验证方写
  ④ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
"""
from __future__ import annotations

import fcntl
import os
import re
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-08"

TARGETS = ("ISS-147", "ISS-151", "ISS-164")


def block_ranges(lines):
    """返回 {id: (start_idx, end_idx)} (0-based, end 不含), end = 下一个 '- id:' 之前"""
    starts = []
    for i, l in enumerate(lines):
        m = re.match(r"^- id: (\S+)\s*$", l)
        if m:
            starts.append((m.group(1), i))
    out = {}
    for k, (iid, s) in enumerate(starts):
        e = starts[k + 1][1] if k + 1 < len(starts) else len(lines)
        out[iid] = (s, e)
    return out


def set_scalar(lines, rng, key, new_value, quoted=False):
    """在 block 内替换 `  key: ...` 行的值; 返回是否命中"""
    s, e = rng
    for i in range(s, e):
        if lines[i].startswith(f"  {key}:"):
            val = f"'{new_value}'" if quoted else new_value
            lines[i] = f"  {key}: {val}"
            return True
    return False


def append_note(lines, rng, text):
    """在 block 内 note 行的单引号标量末尾追加 text (不破坏 YAML 引号规则)"""
    s, e = rng
    for i in range(s, e):
        if lines[i].startswith("  note:"):
            line = lines[i]
            assert line.rstrip().endswith("'"), f"note 行不是单引号标量结尾: {line[-40:]!r}"
            assert "'" not in text, "追加文本里含 ASCII 单引号, 会破坏 YAML"
            lines[i] = line.rstrip()[:-1] + text + "'"
            return True
    return False


def apply_updates(updates, tag):
    """updates: {id: {'status':..., 'verify_result':..., 'verify_date':..., 'note_append':...}}"""
    with open(LOCK, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)          # ① flock
        try:
            with open(LOG, encoding="utf-8") as f:
                before_text = f.read()
            before = yaml.safe_load(before_text)
            before_by_id = {it.get("id"): it for it in before["issues"]}

            lines = before_text.split("\n")
            ranges = block_ranges(lines)
            touched = []
            for iid, u in updates.items():
                assert iid in TARGETS, f"越权: 试图改 {iid}"
                rng = ranges[iid]
                if u.get("status"):
                    assert set_scalar(lines, rng, "status", u["status"]), f"{iid} status 未命中"
                if u.get("verify_result"):
                    assert set_scalar(lines, rng, "verify_result", u["verify_result"]), f"{iid} verify_result 未命中"
                if u.get("verify_date"):
                    assert set_scalar(lines, rng, "verify_date", u["verify_date"], quoted=True), f"{iid} verify_date 未命中"
                if u.get("note_append"):
                    assert append_note(lines, rng, u["note_append"]), f"{iid} note 未命中"
                touched.append(iid)

            after_text = "\n".join(lines)
            after = yaml.safe_load(after_text)
            after_by_id = {it.get("id"): it for it in after["issues"]}

            # ② 只允许这 3 条发生变化 (逐字段对比)
            assert set(before_by_id) == set(after_by_id), "issue 集合变了"
            for iid in before_by_id:
                if iid in TARGETS:
                    continue
                if before_by_id[iid] != after_by_id[iid]:
                    for k in before_by_id[iid]:
                        if before_by_id[iid].get(k) != after_by_id[iid].get(k):
                            raise AssertionError(f"越权改动: {iid}.{k}")

            # 原子写
            d = os.path.dirname(LOG)
            fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(after_text)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, LOG)
            except Exception:
                if os.path.exists(tmp):
                    os.unlink(tmp)
                raise
            dfd = os.open(d, os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)

            print(f"[{tag}] 已写: {touched}")
            for iid in touched:
                it = after_by_id[iid]
                print(f"   {iid}: status={it.get('status')} verify_result={it.get('verify_result')} "
                      f"verify_date={it.get('verify_date')} owner={it.get('owner')} verify_by={it.get('verify_by')}")
            # 行数对比 (确认没有结构性变化)
            print(f"   行数 {len(before_text.split(chr(10)))} -> {len(after_text.split(chr(10)))}")
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)       # ① 解锁


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "phase1":
        apply_updates({
            "ISS-147": {
                "status": "verified",
                "verify_result": "pass",
                "verify_date": TODAY,
                "note_append": (
                    "★★**2026-11-08 23:3x sw-lead 独立验证 (verify_by) ⇒ PASS** ★**不是看标题, 是把本单的硬核命令重跑了一遍**: "
                    "①`~/miniconda3/envs/rknn/bin/python` 实跑 `config(target_platform=...)` ⇒ **rk3572 → ValueError: Invalid target_platform rk3572!** "
                    "(与 `SW/RKNN_BUILD_ENV_RECOVERY.md` §2.2 L190 的实测输出逐字一致) · **rk3576 → rc=0** ⇒ ★**P0-1 结论被独立复现 (不是转述别人写的)** "
                    "②env 指纹实测 = python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / numpy 1.26.4 / protobuf 4.25.4 / torch 2.4.0+cpu / setuptools 80.10.2 "
                    "⇒ **与 fix_ref 写的指纹逐项一致** "
                    "③产物核对 = 该文档 **911 行** (mtime 11-02 23:49) + §6 待核清单 **N1~N18 18 条齐全** (L770) + `state/fragments/sw.yaml` 的 `rknn_target_platform` claim 已落账且与 §2 结论一致 "
                    "④F1 0.3017 / 0.2927 被 `SW/DEMO_OD_PIPELINE_SPEC.md` §1.4 (L84~L135) 的**四轮逐位实测表**独立交叉印证 "
                    "(A/C/D 三轮逐位相同 + B 轮不同 ⇒ 缓存自动失效确实生效)。"
                    "★**对 desc 的唯一偏差 (判为不构成不通过)**: desc ④写「校准集 = OD 场景实拍 300 张覆盖 80 类」, 交付的是 **COCO val2017 100 张** ⇒ "
                    "文档 §4.2/§4.3 (L468) 已**明确事实性纠正** (COCO 任意 100/300 张不可能覆盖 80 类; 校准只要求 ≥100 张) 并把眼镜场景实拍推迟到整机阶段 RT-1 "
                    "⇒ 属**有据的纠偏, 不是偷工**。"
                    "★**⇒ verify_result=pass, status: fixed→verified (不进 closed)**: ★**残项 = desc ⑤ 后半段「板端 acc 复现链跑通」** —— "
                    "板子物理不在线 (文档 §1.5 实测 SSH No route to host + ARP FAILED), 且 ★**老板 11-04 订正「不拿现成开发板当载体, demo 唯一载体 = 自研主板」** "
                    "(见 `DECISION_PENDING_2026-11-04.md` §1 第 ② 行) ⇒ 该残项**已改挂 ISS-155 (板端验证, 仍 open) / ISS-169 (板可制造性, 仍 open)**, "
                    "不是本单能自闭环的欠账 ⇒ 故停在 verified。"
                ),
            },
            "ISS-151": {
                "status": "verified",
                "verify_result": "pass",
                "verify_date": TODAY,
                "note_append": (
                    "★★**2026-11-08 23:3x sw-lead 独立验证 (verify_by) ⇒ PASS**: "
                    "①**结构核对**: `HW/PART_ALTERNATIVES_REGISTRY.md` **266 行** (mtime 11-02 22:56) · desc 点名的 **7 类全部到位** = "
                    "§1 主控载体 (L18) / §2 camera 模组 (L37) / §3 屏幕模组 (L56) / §4 sensor 裸件 (L109) / §5 FPC 连接器与排线 (L124) / "
                    "§6 电源 (L138) / §7 调试与接口 (L198); ★**每类候选数 = 5 / 6 / 5 / 4 / 5 / 5 / 4, 全部 ≥3** ✔ "
                    "②**字段核对**: 每行都带 desc 要求的 8 列 (类别 / 候选名 / 公开在售渠道(链接) / 关键规格 / ①能否满足 demo 硬指标 / ②数据来源 D1~D5 / 已试-未试 / 备注) ✔ "
                    "③**纪律逐条核对**: ①链接逐条标注实测 HTTP 状态 ✔ ②未查的写「未查」不猜价格库存 (FH35C 额定电流与弯折寿命 = 未查 · AR0521 电源轨 = 未查 · Forlinx 逐针表 = 未查) ✔ "
                    "③**全文无「联系厂家」动作** ✔ ④**已试/未试栏真的动了** + §8 (L209) 给了判定口径与汇总表 + L3 自评 (全库零采购记录 ⇒ L3 门槛未到 ⇒ L4 不该触发) ✔ "
                    "⑤§9 (L230) 给了 C1~C7 可执行结论。"
                    "★**§3 是本单最硬的一块**: 79 个 panel 文件逐个列目录 ⇒ ST7701/ST7703/ILI9881C/NV3052C 确有现成驱动, "
                    "★**同时诚实写出反例 EK79007/EK73217/NV3049 内核里没有** ⇒ 推翻老板原假设但没粉饰。"
                    "★**我本机 11-08 抽验链接可达性**: forlinx OK3572-C 页 **200** ✔ · docs.radxa.com camera-4k **200** ✔ · wiki.dfrobot.com/dfr1218 **200** ✔ · "
                    "waveshare 4.3inch DSI wiki **200** ✔ · ti.com TPS7A20 **200** ✔ · hirose 产品页 **403** (文档标 200 —— 当日 Cloudflare 拦 curl, "
                    "同一文档另一条 hirose 链接本就标 403 ⇒ 判为**UA/时段敏感, 非编造**, 不影响结论)。"
                    "★**唯一偏差**: fix_ref 写「9 章」, 现文件 **10 章** (§10 为 ISS-158 后补的针位表补充, L247) ⇒ 是**超集不是缺项**。"
                    "★**⇒ verify_result=pass, status: fixed→verified**。"
                ),
            },
            "ISS-164": {
                "status": "verified",
                "verify_result": "pass",
                "verify_date": TODAY,
                "note_append": (
                    "★★**2026-11-08 23:3x sw-lead 独立验证 (verify_by) ⇒ PASS**: "
                    "①**fix_ref 三处逐行核对** (`SW/DEMO_OD_PIPELINE_SPEC.md`, 675 行, mtime 11-03 01:06): "
                    "★**§1.4 L84~L135**, 其末尾 **L128** 「判据冲突已裁决 (2026-11-03 01:0x, ISS-164 收口)」写明"
                    "**已拆分 demo 线 (F1 ≥ 0.25 + 80 类 ID 全域覆盖 + IoU > 0.95, §6.6) / 量产线 (F1 ≥ 0.30, §6.2)**; "
                    "★**§6.2 L488**, 判据② 行 **L495** 已把 F1 ≥ 0.30 **明确标注为【量产/整机阶段】放行线, 不再用于 demo 判定**, 并写明代价 "
                    "(若坚持 0.30 ⇒ 换 yolov5s ⇒ 端到端 62.67~64.18ms 超 60ms ⇒ 60ms 顺延到整机阶段); "
                    "★**§6.6 L532**, 总表 ② 行 **L537** 一句话写死 demo 判据 = ID∈[0,79] 全域覆盖 + 离线 F1 ≥ 0.25 (yolov5n 实测 0.2927 ✔) + 在线框 = 离线框 IoU > 0.95 "
                    "⇒ ★**desc 的硬要求「demo 精度线与量产放行线必须明确分开写」= 已满足, 且三处口径互相一致**。"
                    "②**数字可复算**: 0.3017 / 0.2927 来自 §1.4 的四轮逐位实测表 (TP/FP/FN = 565/1028/1588 与 494/765/1623), 与 ISS-147 的重建实测**逐位一致** "
                    "⇒ 0.25 这条线与实测值的关系真实, 不是拍出来的。③§6.5 判据⑤ 与 §6.2/§6.6 口径一致 (60ms 留整机阶段)。"
                    "★**残项 (不阻塞本单, 但必须留痕)**: ★**共享状态里 SW-Q5 仍写着「待老板一句」没有关** —— "
                    "`STATE.yaml` L4147 (open_questions 里 SW-Q5.to=main, 原文「请老板拍板哪条」) + `state/fragments/sw.yaml` 的 interface_claim `demo_precision_line` "
                    "仍是 `F1>=0.25_recommended` + 注里「待老板一句」 + `demo_model_choice` 的注仍留着「已登记 SW-Q5 待老板裁决」 "
                    "⇒ ★**裁决本身已由项目总工 11-03 01:0x 落进规格并执行 (本单按 0.25), 是账目同步没跟上 (owner=main), 不是本单产物有缺陷**。"
                    "★**⇒ verify_result=pass, status: fixed→verified (不进 closed)**: 残项 = SW-Q5 关闭 + fragments 同步 + boss 知悉/拍板 ⇒ 闭环前不发 closed。"
                ),
            },
        }, "phase1")
    elif which == "phase2":
        apply_updates({
            "ISS-151": {
                "status": "closed",
                "note_append": (
                    "★2026-11-08 23:4x 复核残项: 本单**在自身范围内无后续动作** (交付物 = 清单本体, 已全部交付并逐条核过; "
                    "后续「取 Forlinx 引脚定义表 / 采购 / 画板」均属 ISS-158 / ISS-162 / ISS-165 等别的 issue 的活) "
                    "⇒ ★**status: verified→closed** (C3 全满足: verify_result=pass · verify_by=sw-lead ≠ owner=main · 有 fix_ref)。"
                ),
            },
        }, "phase2")
    else:
        raise SystemExit("usage: phase1 | phase2")
