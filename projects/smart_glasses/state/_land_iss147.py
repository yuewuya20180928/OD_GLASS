#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss147.py —— ISS-147 收口 + 修 ISS-145 规格里的两处错 + 新开 ISS-157 (rknn_bench 缓存静默错数) + demo 模型定案

sw-lead 交卷 (ISS-147, 1h22m): 工具链已恢复 (conda env ~/miniconda3/envs/rknn: python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / torch 2.4.0+cpu),
仓库脚本零改动跑通转换四步, 校准集与 COCO val2017 已恢复 ⇒ A2 路线成本 3~5 人天 → ~1 人天。
★核心结论: **rk3572 不是任何已发布版 toolkit2 的合法 target_platform** (2.3.2 与最新 2.5.0 都抛 ValueError; 官方 Support Platform 列表也没有) ⇒
  ISS-145 的 M1 "直接复用 A7S 的 .rknn, 零转换" 前提不成立 ⇒ 必须重转 ⇒ 替代路线 = target_platform='rk3576' (同代 RKNPU v2, 算力不等) [推算, 板端待验]。
★sw-lead 指出 ISS-145 (它自己写的) 两处错: ①核法 `RKNN.RKNN_TARGET_PLATFORM` 属性在 2.3.2 **不存在** (hasattr=False), 且目标列表在编译后的 .so 里 ⇒ 正确核法是直接 config() 试
  ②"yolov5n 少 ~4 点 mAP50" 不成立 ⇒ 实测同图集只差 **0.0090 F1** (yolov5s 0.3017 vs yolov5n 0.2927) ⇒ 本单一并订正。
★N16: `rknn_bench.py` 的 cut 模型缓存不失效 ⇒ 换模型重测会**静默跑出上一个模型的数字** (实测两次结果逐字节相同) ⇒ 新开 ISS-157。
"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

# ══════ ① 修 ISS-145 规格里的两处错 (sw-lead 自己写的文件, 项目总工代改) ══════
SPEC = f'{PROJ}/SW/DEMO_OD_PIPELINE_SPEC.md'
s = open(SPEC, encoding='utf-8').read()
old1 = ('在构建机上: `python -c "from rknn.api import RKNN; print(RKNN.RKNN_TARGET_PLATFORM)"` + `grep -n "rk3572\\|rk3576" <site-packages>/rknn/api/rknn.py`。'
        '★若 2.3.2 不含 rk3572 ⇒ 需升级 toolkit2 版本 **[待核]**')
new1 = ('★★**已核 (ISS-147, 2026-11-02 20:3x)**: `rk3572` **不是任何已发布版 toolkit2 的合法 target** —— 实测 2.3.2 与最新 **2.5.0** 都抛 '
        '`ValueError: Invalid target_platform \'rk3572\'!`, 而 `target_platform=\'rk3576\'` **rc=0**。'
        '★**正确核法 = 直接 config() 试** (`RKNN.RKNN_TARGET_PLATFORM` 属性在 2.3.2 **不存在**, hasattr=False; 且目标列表在编译后的 `rknn_base*.so` 里, 只 grep 源码不够)。'
        '⇒ ★**"升级到某版本就有 rk3572"这个选项不存在** ⇒ 本行不再是 [待核], 而是**已定的阻塞** ⇒ 替代路线见 ISS-155。')
assert old1 in s, 'ISS-145 §2.3 那行没找到'
s = s.replace(old1, new1, 1)

old1b = ('构建机上 `from rknn.api import RKNN; print(RKNN.RKNN_TARGET_PLATFORM)` + grep `rknn/api/rknn.py`')
new1b = ('★★**已核**: 直接 `config(target_platform=\'rk3572\')` 试 → ValueError; 同段 `rk3576` rc=0 ⇒ ★**rk3572 不合法, M1 零转换优势归零** (ISS-147/ISS-155)')
assert old1b in s, 'ISS-145 附录 P0-1 那行没找到'
s = s.replace(old1b, new1b, 1)

old2 = '精度要重评 (比 yolov5s 少 ~4 点 mAP50)'
new2 = ('★★**精度已实测 (ISS-147)**: 同一图集 (COCO val2017 + 100 张校准集) 下 **yolov5s F1 0.3017 vs yolov5n F1 0.2927, 只差 0.0090** ⇒ '
        '★**"少 ~4 点 mAP50"在本项目口径下不成立, 已订正** ⇒ ★**demo 第一版定 yolov5n** (60ms 余量最大 + 误检少 263 个 + 产物小一半; 代价召回低 0.0291)')
assert old2 in s, 'ISS-145 M2 那行没找到'
s = s.replace(old2, new2, 1)
open(SPEC, 'w', encoding='utf-8').write(s)
print('[1] SW/DEMO_OD_PIPELINE_SPEC.md: 两处错已订正 (核法 + F1 差值) + demo 模型定 yolov5n')

# ══════ ② issue_log ══════
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-147']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'sw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('SW/RKNN_BUILD_ENV_RECOVERY.md (911 行: 本机现状实测/核心一问/模型选择/恢复路径/复现命令/18 条待核) · '
                'state/fragments/sw.yaml (原子写) · 环境: ~/miniconda3/envs/rknn (python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / torch 2.4.0+cpu)')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 20:3x 交卷并收口**: ★**工具链已恢复** (conda env `~/miniconda3/envs/rknn`; ★**路径与 `rknn_bench.py` 硬编码的 `RKNN_PY` 一致 ⇒ 仓库脚本零改动可跑**), "
    "★**仓库脚本全链原样跑通** (probe/calib/convert/acc 四步 rc=0, 真落盘) ⇒ ★**A2 路线 (重新导出) 成本从 3~5 人天降到 ~1 人天**。"
    "★**校准集与 COCO val2017 已恢复** ⇒ 精度可比。"
    "★**核心结论 (P0)**: ★★**`rk3572` 不是任何已发布版 toolkit2 的合法 target_platform** —— 实测 2.3.2 与最新 **2.5.0** 都抛 `ValueError: Invalid target_platform 'rk3572'!`, "
    "而 `target_platform='rk3576'` **rc=0**; `rknn/api/rknn.py` 的目标列表里 rk3572 出现 **0 次** (含 .so 二进制 grep 也 0 命中), 官方 README 的 Support Platform 列表也没有 RK3572 "
    "⇒ ★★**不存在\"升级到某版本就有 rk3572\"这个选项** ⇒ ★**ISS-145 的 M1「直接复用 A7S 的 .rknn, 零转换成本」前提不成立, 必须重转** ⇒ 替代路线 (rk3576 target 转换) 在 ISS-155。"
    "★**模型选择已定 (demo 第一版 = yolov5n)**: 实测同图集 **yolov5s F1 0.3017 vs yolov5n F1 0.2927 (只差 0.0090)** ⇒ 选 n (60ms 余量最大 + 误检少 263 个 + 产物小一半), 代价召回低 0.0291。"
    "★**它同时订正了 ISS-145 规格的两处错** (已由项目总工代改): ①核法 `RKNN.RKNN_TARGET_PLATFORM` 属性在 2.3.2 **不存在**, 且目标列表在编译后的 .so 里 ⇒ 正确核法是直接 `config()` 试 "
    "②\"yolov5n 少 ~4 点 mAP50\" **不成立** (实测只差 0.0090 F1)。")

# ISS-155 追加结论
i = by.get('ISS-155')
if i:
    i['note'] = (i.get('note') or '') + (
        " ★★**2026-11-02 20:3x ISS-147 已实测闭合**: ★**`rk3572` 不是任何已发布版 toolkit2 的合法 target_platform** (2.3.2 与最新 2.5.0 都抛 ValueError; 官方 Support Platform 列表也没有) ⇒ "
        "★**不存在\"升级 toolkit 就有 rk3572\"这条路** ⇒ 唯一可行 = **用 `target_platform='rk3576'` 转换** (RK3572 与 RK3576 同代 RKNPU v2; ★**算力不等: 4 vs 6 TOPS** ⇒ [推算], 板端需实测验证 N1)。"
        "★**卡点未变**: 验证需要一块能跑的 RK3572 板 ⇒ ★**Radxa 板当前不可达 (No route to host + ARP FAILED)** ⇒ ★**必须用公开在售的 RK357x 板** ⇒ ★**与 demo Step1 载板合流 (Forlinx OK3572-C 首选) ⇒ 一举两得: 验证 target + 跑 demo 链路**。")

# ══════ 新开 ISS-157: rknn_bench 缓存静默错数 ══════
if not any(x['id'] == 'ISS-157' for x in iss):
    iss.append({
        'id': 'ISS-157',
        'title': '★★[软件] rknn_bench.py 的 cut 模型缓存不失效 ⇒ 换模型重测会静默跑出上一个模型的数字 (实测两次结果逐字节相同)',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 20:3x ISS-147 交卷时实测发现 (sw-lead 报告, main 转登记): ★**`SW/tools/rknn_bench.py` 的 cut 模型缓存不失效** ⇒ '
            '★**换模型 (yolov5s ⇄ yolov5n) 后重测, 会静默跑出上一个模型的数字** —— 实测两次结果**逐字节相同**。'
            '⇒ ★**这是"结果看起来正常但其实是旧数据"的那类缺陷**: 比报错更危险 (门禁会显示绿灯, 数字却是错的)。'
            '⇒ ★**修法**: ①切模型时**必须删** `/tmp/rknn_bench/yolov5s_heads.onnx` (sw-lead 已在文档里写, 但要变成**脚本自动行为**: 按模型名/哈希决定缓存键) '
            '②★**更稳的修法 = 缓存键带上模型指纹** (权重路径 + mtime/sha256 + 尺寸), 模型一变缓存自动失效 ⇒ ★**根治"忘了删"** '
            '③★**加一条自检**: 输出里打印"本次用的权重 + 缓存命中/未命中", 让人一眼看出是不是旧数据。'
            '⇒ ★**影响面**: 所有用 rknn_bench 出的精度数字 (含我们刚定的 yolov5n F1 0.2927 与 yolov5s 0.3017 —— ★**这两个数是在"换模型前先删了缓存"的前提下测的, 但脚本本身没有保护**) ⇒ ★**修完要把两个数重测一遍确认**。'),
        'owner': 'sw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-05',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'SW/tools/rknn_bench.py (缓存键) · SW/RKNN_BUILD_ENV_RECOVERY.md §5 (复刻隐形坑)',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 20:3x。★**优先级高于其它软件单**: 这是"绿灯假数据"型缺陷, 一旦踩中, 后面所有精度结论都不可信。'
                 '★**改完必须重测 yolov5n / yolov5s 两个 F1** 并把数写回 ISS-145 §1 表格。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[2] issue_log: ISS-147 fixed / ISS-155 note 追加 / 新开 ISS-157')

# ══════ ③ tracker: (1.63) ══════
TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
anchor = "#### (1.62) ★★★★ 2026-11-02 19:45:"
sec = """#### (1.63) ★★★★ 2026-11-02 20:3x: 软件侧构建环境恢复 + ★★**rk3572 不是 toolkit2 的合法 target** ⇒ demo 模型定 yolov5n

> **落账**: `SW/RKNN_BUILD_ENV_RECOVERY.md` (911 行, ISS-147) · `SW/DEMO_OD_PIPELINE_SPEC.md` 两处订正 · **ISS-147 fixed** · **ISS-155** 追加结论 · 新开 **ISS-157** (rknn_bench 缓存静默错数)

**★ 好消息 (软件侧不再卡)**: ★**工具链已恢复** (conda env `~/miniconda3/envs/rknn`: python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / torch 2.4.0+cpu; ★**路径与 `rknn_bench.py` 硬编码一致 ⇒ 仓库脚本零改动可跑**) ⇒ ★**probe/calib/convert/acc 四步原样跑通** ⇒ ★**A2 路线 (重新导出 ONNX) 成本 3~5 人天 → ~1 人天** ⇒ ★**校准集与 COCO val2017 已恢复** ⇒ 精度可比。

**★ P0 结论 (会改方案的一条)**: ★★**`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— 实测 **2.3.2 与最新 2.5.0 都抛 `ValueError: Invalid target_platform 'rk3572'!`**, 而 `rk3576` **rc=0**; 目标列表里 rk3572 出现 **0 次** (含 .so 二进制), 官方 Support Platform 列表也没有 ⇒ ★★**不存在"升级 toolkit 就有 rk3572"这条路** ⇒ ★**ISS-145 的 M1「直接复用 A7S 的 .rknn, 零转换成本」前提不成立** ⇒ 唯一可行 = **用 `target_platform='rk3576'` 转换** (同代 RKNPU v2; ★**算力不等 4 vs 6 TOPS ⇒ [推算], 板端必须实测**) ⇒ **ISS-155**。

**★ 顺带订正 ISS-145 的两处错 (sw-lead 自己指出, 项目总工代改)**: ①核法 `RKNN.RKNN_TARGET_PLATFORM` 属性在 2.3.2 **不存在**, 目标列表在编译后的 .so 里 ⇒ **正确核法是直接 `config()` 试** ②**"yolov5n 少 ~4 点 mAP50" 不成立** ⇒ 实测同图集 **yolov5s F1 0.3017 vs yolov5n F1 0.2927 (只差 0.0090)** ⇒ ★**demo 第一版定 yolov5n** (60ms 余量最大 + 误检少 263 个 + 产物小一半; 代价召回低 0.0291)。

**★ 新开的 ISS-157 (绿灯假数据型缺陷)**: `rknn_bench.py` 的 **cut 模型缓存不失效** ⇒ ★**换模型重测会静默跑出上一个模型的数字** (实测两次结果逐字节相同) ⇒ ★**比报错更危险** ⇒ 修法 = **缓存键带模型指纹 (权重路径+mtime/sha256)** + 输出打印"本次权重 + 缓存命中/未命中" ⇒ 修完**重测两个 F1**。

**★ 现在的硬卡点只有一个**: ★**验证 `rk3576` target 的 .rknn 能不能被 RK3572 的 `librknnrt.so` 加载, 需要一块能跑的 RK3572 板** ⇒ ★**Radxa 板当前不可达 (No route to host + ARP FAILED)** ⇒ ★**必须用公开在售的 RK357x 板** ⇒ ★**与 demo Step1 载板合流** (Forlinx OK3572-C 首选) ⇒ ★**一举两得: 验证 target + 跑 demo 链路**。

"""
t = t.replace(anchor, sec + anchor, 1)
open(TP, 'w', encoding='utf-8').write(t)
print('[3] tracker: (1.63) 已写')

# ══════ ④ 分片 ══════
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("rknn_target_platform", "rk3576_for_rk3572",
        "★★2026-11-02 20:3x 实测 (ISS-147): **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 target_platform** (2.3.2 与最新 2.5.0 都抛 ValueError; rknn/api/rknn.py 与编译后 .so 里 rk3572 命中 0; 官方 Support Platform 无 RK3572) ⇒ **不存在升级 toolkit 就有 rk3572 的路** ⇒ RK3572 上只能用 `target_platform='rk3576'` 转 (同代 RKNPU v2, 算力不等 4 vs 6 TOPS ⇒ [推算], 板端须实测) ⇒ ISS-145 的 M1「零转换复用 A7S 的 .rknn」不成立。",
        "ISS-155 + SW/RKNN_BUILD_ENV_RECOVERY.md §2")
    add("demo_model_choice", "yolov5n",
        "★demo 第一版定 **yolov5n@640 INT8**: 实测同图集 (COCO val2017 + 100 张校准集) yolov5s F1 0.3017 vs yolov5n F1 0.2927 ⇒ **只差 0.0090** (★**订正了原规格『少 ~4 点 mAP50』的错误说法**) ⇒ 选 n (60ms 余量最大 + 误检少 263 个 + 产物小一半), 代价召回低 0.0291。★⚠️ 该数需在 ISS-157 (缓存键) 修完后**重测确认**。",
        "ISS-147 + SW/DEMO_OD_PIPELINE_SPEC.md §1")
    add("rknn_build_env", "restored",
        "★RKNN 构建环境已恢复 (ISS-147): conda env `~/miniconda3/envs/rknn` (python 3.10.22 / rknn-toolkit2 2.3.2 / onnx 1.16.1 / numpy 1.26.4 / protobuf 4.25.4 / torch 2.4.0+cpu) ⇒ ★**路径与 `rknn_bench.py` 硬编码的 RKNN_PY 一致 ⇒ 仓库脚本零改动可跑** ⇒ probe/calib/convert/acc 四步 rc=0 真落盘; ★校准集与 COCO val2017 已恢复 ⇒ A2 路线成本 3~5 人天 → ~1 人天。",
        "SW/RKNN_BUILD_ENV_RECOVERY.md §1/§4/§5")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("sw-lead", mutate)
print('[4] sw.yaml 已更新 (3 claims)')
