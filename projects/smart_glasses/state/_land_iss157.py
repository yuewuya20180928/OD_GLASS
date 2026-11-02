#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss157.py —— ISS-157 收口 + 判据冲突 SW-Q5 升级给老板 + tracker 落账"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-157']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'hw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('SW/tools/rknn_bench.py (11 处: 模型指纹 sha256(权重路径+内容sha256+mtime+尺寸+保留输出名+cut工具) / 指纹缓存键 / HIT-MISS 打印 / 多指纹自检 / --onnx 换权重重测 / --force-recut) · '
                'SW/DEMO_OD_PIPELINE_SPEC.md (§1.4 四轮实测表 + target 写死 rk3576 + 判据冲突提请) · SW/RKNN_BENCH.md (§7.5) · state/fragments/sw.yaml')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 18:4x 交卷并验收通过 (main 抽查: 指纹函数在位 / 两份不同指纹缓存并存 / 旧假缓存已清 / 两个 F1 已进规格)**。"
    "★**三条硬验收全过**: ①同权重两次结果**逐位相同** (含一次删缓存 MISS) ②换权重结果**必须不同** (yolov5n 494/765/1623/0.29265 ≠ yolov5s 565/1028/1588/0.30166) ③两个 F1 重测 = **0.3017 / 0.2927**, 与 ISS-147 首测**逐位一致** (首测本是'人记得删缓存'跑对的, 现在这个前提变成脚本自动行为)。"
    "★★**物证 (已写进 RKNN_BENCH §7.5.1)**: 旧缓存 `yolov5s_heads.onnx` 与 `yolov5n-sim_heads_*.onnx` **sha16 逐字节相同 (adac68f888bf61c2 / 7,520,239 B)** ⇒ **文件名叫 yolov5s 的里面装的是 yolov5n 的图** ⇒ 这就是'绿灯假数据'的实物 ⇒ 已删。"
    "★**待办已由项目总工当场收掉两条**: ①`.rknn` 产物名带源权重 stem (已改 rknn_bench.py) ②`RKNN_BUILD_ENV_RECOVERY.md` 里'换模型前必做 rm -f .../yolov5s_heads.onnx' 已过期 (缓存现在自动失效) 已更正。"
    "★**剩两条**: ③**判据冲突 SW-Q5 升级给老板** (见 ISS-164) ④板端验证 (ISS-155) 卡在 Radxa A7S 不可达 ⇒ 需另取一块 RK357x 板 (与 demo 载板同一块解决)。")

if not any(x['id'] == 'ISS-164' for x in iss):
    iss.append({
        'id': 'ISS-164',
        'title': '★★[等老板一句] demo 精度验收线: yolov5n F1 0.2927 差 0.0073 不达 0.30 门槛, 换 yolov5s 过线但 60ms 退到 62.67~64.18ms ⇒ 两条路都不平',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 18:4x ISS-157 复测后暴露的**真冲突** (sw-lead 提请, main 复核): '
            '`SW/DEMO_OD_PIPELINE_SPEC.md` §6.2 判据②写的是 **"离线 F1 ≥ 0.30"** (那是**量产放行门 G3 的量级**, A7S 实测 0.3139) ⇒ '
            '而 ★**demo 第一版选的 yolov5n 实测 F1 = 0.2927, 差 0.0073 不达标**; ★**换 yolov5s (0.3017) 过线, 但 60ms 余量从 52.91ms 退到 62.67~64.18ms ⇒ 超线** ⇒ ★**两条路都不平**。'
            '⇒ ★**两条出路 (请你选一句)**: '
            '**① (项目总工建议)**: ★**demo 阶段把判据②改成 "F1 ≥ 0.25 + 80 类 ID 全域覆盖 + 在线/离线框 IoU > 0.95"** ⇒ ★**理由: demo 的目的是"链路跑通 + 框画得出来 + 延迟有数"; ★**精度门槛属整机/产品阶段** (那时才有真实眼镜场景集, 见规格 RT-1) ⇒ ★**这样保住 yolov5n (端到端 52.91ms, 60ms 余量最大)**。'
            '**②**: ★**坚持 F1 ≥ 0.30** ⇒ demo 必须换 yolov5s ⇒ ★**端到端 62.67~64.18ms ⇒ 60ms 硬指标顺延到整机阶段** (demo 阶段只记录不设限)。'
            '⇒ ★**无论选哪条, 都要把"demo 阶段的精度线"与"量产放行线"明确分开写** —— ★**现在这两条混在同一份规格里, 才会打架**。'
            '⇒ ★**本单是决策单, 改一行判据即可收口**。'),
        'owner': 'boss', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-03',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'SW/DEMO_OD_PIPELINE_SPEC.md §6.2 判据② + §1.4 + SW/RKNN_BENCH.md §7.5',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 18:4x。★**建议默认 = ①** (demo 线降到 0.25, 保住 yolov5n 与 60ms 余量)。'
                 '★**选完立刻收口**: 改规格 §6.2 判据② + 同步 `state/fragments/sw.yaml` 的 demo_model_choice claim + 关闭 SW-Q5。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-157 fixed + ISS-164 新开')

TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
anchor = '#### (1.69) ★★★★ 2026-11-02 18:4x:'
sec = '''#### (1.70) ★★★★ 2026-11-02 18:4x: ★**ISS-157 闭环 ("绿灯假数据"根治)** + 浮出一条真冲突 (SW-Q5 / ISS-164)

> **落账**: `SW/tools/rknn_bench.py` (指纹缓存) · `SW/DEMO_OD_PIPELINE_SPEC.md` §1.4 (四轮实测) · `SW/RKNN_BENCH.md` §7.5 · ISS-157 **fixed** · 新开 **ISS-164** (判据冲突, 等老板一句)

★★ **"绿灯假数据"的物证 (已写进 RKNN_BENCH §7.5.1)**: 旧缓存 `yolov5s_heads.onnx` 与 `yolov5n-sim_heads_*.onnx` **sha16 逐字节相同 (adac68f888bf61c2 / 7,520,239 B)** ⇒ ★**文件名叫 yolov5s 的, 里面装的是 yolov5n 的图** ⇒ 这就是"换模型重测静默跑出上一个模型的数字"的实物。
⇒ ★**修法**: 缓存键 = **sha256(权重路径 + 内容sha256 + mtime + 尺寸 + 保留输出名 + cut工具)** ⇒ **模型一换缓存自动失效**; ★**输出打印"本次权重 + HIT/MISS"**; ★**自检发现多指纹即提示清理**; ★**cut 失败直接抛错** (不再静默回退)。
⇒ ★**三条硬验收全过**: 同权重两次**逐位相同** / 换权重**必须不同** / 两个 F1 重测 = **0.3017 (s) vs 0.2927 (n)**, 与首测**逐位一致** ⇒ ★**现在这两个数可信了**。

★★ **顺带浮出一条真冲突 (ISS-164, 等老板一句)**: 规格 §6.2 判据②写 **"离线 F1 ≥ 0.30"** (那是**量产放行门 G3 的量级**) ⇒ ★**demo 选的 yolov5n = 0.2927 差 0.0073 不达标**; ★**换 yolov5s 过线但端到端退到 62.67~64.18ms 超 60ms** ⇒ ★**两条路都不平** ⇒ ★**根因是"demo 精度线"与"量产放行线"混在同一份规格里**。
⇒ ★**项目总工建议**: ★**demo 阶段判据②改成 "F1 ≥ 0.25 + 80 类 ID 全域覆盖 + 在线/离线框 IoU > 0.95"** (demo 的目的 = 链路跑通 + 框画得出 + 延迟有数; ★**精度门槛归整机阶段**, 那时才有真实眼镜场景集) ⇒ ★**保住 yolov5n 与 60ms 余量**。⇒ ★**另一条**: 坚持 0.30 ⇒ 用 yolov5s ⇒ **60ms 硬指标顺延到整机阶段**。

'''
t = t.replace(anchor, sec + anchor, 1)
open(TP, 'w', encoding='utf-8').write(t)
print('[tracker] (1.70) ok')


def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(k, v, n, r):
        for c in claims:
            if c.get("key") == k:
                c.update({"value": v, "note": n, "ref": r}); return
        claims.append({"key": k, "value": v, "note": n, "ref": r})
    add("rknn_cut_cache_key", "sha256_fingerprint",
        "★★ISS-157 已修 (18:4x): cut 模型缓存键 = **sha256(权重绝对路径|内容sha256[:16]|mtime(ns)|大小|输入尺寸|保留输出名|cut工具sha256[:16])[:16]** ⇒ **模型一换缓存自动失效** + 输出打印 HIT/MISS + 多指纹自检 + cut 失败直接抛错。★**物证**: 旧 `yolov5s_heads.onnx` 实装的是 yolov5n 的图 (sha16 adac68f888bf61c2 逐字节相同) ⇒ 这就是'绿灯假数据'。★三条验收全过 (同权重逐位一致/换权重必不同/两个 F1 重测 0.3017 vs 0.2927)。",
        "SW/tools/rknn_bench.py + SW/RKNN_BENCH.md §7.5")
    add("demo_precision_line", "F1>=0.25_recommended",
        "★★SW-Q5 / ISS-164 待老板一句: demo 判据② 'F1 ≥ 0.30' (那是量产放行线) 与 yolov5n 实测 0.2927 冲突 (差 0.0073); 换 yolov5s 过线但端到端退到 62.67~64.18ms 超 60ms ⇒ 两条路都不平。★**建议: demo 线降到 F1 ≥ 0.25 + 80 类 ID 全域覆盖 + IoU > 0.95 ⇒ 保住 yolov5n 与 60ms 余量; 精度门槛归整机阶段**。",
        "ISS-164 + SW/DEMO_OD_PIPELINE_SPEC.md §6.2")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("sw-lead", mutate)
print('[sw.yaml] ok')
