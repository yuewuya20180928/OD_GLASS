#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0545_main_iss372_cont3_spec_correction.py
=============================================================
main (项目总工) · 2026-11-24 05:4x
★给 sw-lead 的【第 6 件规格】补一条实测出来的自指陷阱 + 追加一段 L-23 教训★

★背景: main 05:3x 已裁 U8/U9/U10 并把答案落进 pm.yaml; 但 main 随后又自己在沙盒里
  测出【那条规格里有一处自指陷阱】⇒ 如果不补, sw-lead 照那条规格写工具 ⇒ 工具一落盘
  自守闸当场红 ⇒ 又一次「误读成板坏了」⇒ 所以必须现在就补上。

★纪律: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 未替老板拍板
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import frag_write  # ★只用它的原子写 ★

STAMP = "20260724_0545"
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


APPEND_U8 = (
    " ★★【main 追加式订正 2026-11-24 05:4x·★老字一字未删·★补的是上面那段规格里的一处【自指陷阱】★】★★ "
    "★**★陷阱: 新写的「§1 真件重生成工具」自己会被 H1 当成【新的引用面命中】⇒ 工具一落盘自守闸当场红 (★实测★)★** ⇒ "
    "★**main 2026-11-24 05:4x 沙盒实跑 (★tmp/iss372_verify2·★已清理★)★**: 在 `SW/tools/` 下造两个候选工具 ⇒ "
    "**候选 A (源码里直接写 `PREFIX = \"611b869e\"`) ⇒ 自守闸 H1 当场红: 「扫描到 SW/tools/regen_manifest_literal.py:2 (命中 1 处) "
    "但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红」** ⇒ **候选 B (源码里拆两段 `PREFIX = \"611b\" + \"869e\"`) ⇒ H1 绿 (★零命中★)** ⇒ "
    "★**⇒ 那条工具规格必须再加一条硬约束: 【工具源码里不许出现板 md5 的字面量前缀·★必须像自守闸自己那样拆成两段 (★`\"611b\" + \"869e\"`★)·★"
    "否则工具自己把 H1 打红·★而这恰好发生在批次落盘那一刻 ⇒ 又一次「误读成板坏了」】★** ⇒ "
    "★**⇒ 同理: 工具自己也不许被当成「钉板 md5 的闸」而漏登记 (★自守闸 H4 的类 A 判据只看 32 位字面量·★拆两段就既不是类 A·"
    "工具又不是闸·★不参与 H4 判定·★天然安全★)★** ⇒ "
    "★**⇒ 补完的第 6 件规格 (★以这条为准·★上面的规格其余部分不变★)★**: 重生成工具必须① 从 SW 域真扫 (★不许手写行号★) "
    "② 源码里【不许出现板 md5 字面量前缀·★必须拆两段★】 ③ 回写清账页的 §1 机器块 (MANIFEST_BEGIN/END 之间) "
    "④ 同时逐行同步 §1 表格里的行号列 ⑤ 重生成后自守闸 rc=0 且 §1 表格与机器块【逐条一致】 "
    "⑥ **★落盘后自守闸必须仍是 rc=0 (★自己不许把自己打红·★这是工具的验收线之一★)** ⑦ 批次内 5 条补丁落完 ⇒ 重生成一次 ⇒ "
    "【不许手工改行号】★"
)

L23 = """

## ★L-23 · ★★写「清单/引用面重生成工具」时, 工具自己会被那份清单的扫描网扫到 ⇒ 工具源码里不许出现被扫的关键词★★

★**实测 (2026-11-24 05:4x, main 本机沙盒 `tmp/iss372_verify2` 实跑 · 已清理)★**: ISS-372 自守闸的 H1 扫 SW 域用的是 8 位前缀 `611b869e` ⇒ ★**在 `SW/tools/` 下造两个候选工具** ★
★**候选 A (源码里直接写 `PREFIX = "611b869e"`) ⇒ 自守闸 H1 当场红**: 「★扫描到 SW/tools/regen_manifest_literal.py:2 (命中 1 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★」 ★
★**候选 B (源码里拆两段 `PREFIX = "611b" + "869e"`) ⇒ H1 绿 (★零命中★)** ★
★**⇒ 通则 ①**: ★**凡是要写「扫引用面 / 重建清单」的工具 ⇒ 工具源码里【不许出现被扫的那个关键词】⇒ 必须拆成两段 (★闸自己就是这么干的: `NEEDLE_PREFIX = "611b" + "869e"`★)·★否则工具一落盘就把自己的扫描网打红 ⇒ 而那恰好发生在批次落盘那一刻 ⇒ 现场最容易误读成「板坏了」★** ★
★**⇒ 通则 ②**: ★**★工具的验收线必须包含「工具落盘后, 那道扫它的闸仍然是绿的」★★ (★不是「工具自己跑通了」·★是「闸没被工具打红」·★两者是不同的事★) ★
★**⇒ 通则 ③**: ★**与 L-21 / L-22 合看: 三条同属一类 —— 【闸的扫描面会扫到自己人】·★新写的工具/新写的闸/新写的清单, 都可能落到别人的扫描网里 ⇒ "
    "★落盘前先问一句「我这个东西会不会被现有闸扫到」·★被扫到就得按现有闸的排除口径走 (★拆关键词·★进排除清单·★或登记在册★)★** ★
"""


def main():
    m0, ns0, sz0 = board_fp()
    print("★开工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m0, ns0, sz0))
    assert m0 == BOARD_MD5 and sz0 == BOARD_SIZE, "★板已被改 ⇒ 中止★"

    # ---------------- pm.yaml: 就地扩写 U8 答案 ----------------
    print("\n" + "=" * 88)
    print("★pm.yaml · 就地扩写 U8 答案 (★追加式·★不造重名 key★)")
    print("=" * 88)
    before = md5(PM)

    def mutate(d):
        ans = d.setdefault("answers", [])
        for e in ans:
            if isinstance(e, dict) and e.get("key") == "iss372_need_main_batch_channel_patches":
                old = str(e.get("value") or "")
                if "自指陷阱" in old:
                    print("  ★已有本次订正, 跳过")
                    return
                e["value"] = old + APPEND_U8
                print("  ✅ 就地扩写 answer: iss372_need_main_batch_channel_patches")
                return
        raise SystemExit("★找不到 U8 的 answer key ⇒ 中止★")

    frag_write.update_fragment("main", mutate)
    print("  ★pm.yaml 写前 md5 = %s" % before)
    print("  ★pm.yaml 写后 md5 = %s" % md5(PM))

    # ---------------- LESSONS: 追加 L-23 ----------------
    print("\n" + "=" * 88)
    print("★state/LESSONS.md · 追加 L-23 (★main 独占写★)")
    print("=" * 88)
    src = open(LESSONS, encoding="utf-8").read()
    if "L-23" in src:
        print("  ★L-23 已存在 ⇒ 跳过")
    else:
        bak = LESSONS + ".bak_%s_main_l23" % STAMP
        shutil.copy2(LESSONS, bak)
        tmp = LESSONS + ".tmp_%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(src + L23)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, LESSONS)
        assert open(LESSONS, encoding="utf-8").read().startswith(src), "★老字被改 ⇒ 中止★"
        print("  ★LESSONS 写前 md5 = %s" % md5(bak))
        print("  ★LESSONS 写后 md5 = %s" % md5(LESSONS))
        print("  ★备份 = %s" % os.path.basename(bak))

    # ---------------- issue_log: 追加式补一条 ----------------
    print("\n" + "=" * 88)
    print("★issue_log.yaml · ISS-372 追加第 2 条 note (★追加式★)")
    print("=" * 88)
    raw = open(LOG, encoding="utf-8").read()
    i = raw.find("\n- id: ISS-372")
    j = raw.find("\n- id: ", i + 10)
    if j < 0:
        j = len(raw)
    seg = raw[i:j]
    NOTE = (
        "★2026-11-24 05:4x main 【第 6 件规格的追加式订正】★★ ★**老字一字未删★** ★ "
        "★**main 05:3x 裁完 U8/U9/U10 之后, 又在沙盒里测出【那条规格里有一处自指陷阱】⇒ 现补上 (★不补 ⇒ sw-lead 照写 ⇒ "
        "工具一落盘自守闸当场红 ⇒ 又一次「误读成板坏了」★)★** ⇒ ★**陷阱: 新写的「§1 真件重生成工具」自己会被 H1 当成【新的引用面命中】"
        "⇒ 沙盒实测 (★tmp/iss372_verify2·★已清理★): 候选 A 源码直接写 `PREFIX = \"611b869e\"` ⇒ H1 当场红「漏登记」; "
        "候选 B 拆两段 `PREFIX = \"611b\" + \"869e\"` ⇒ H1 绿 ⇒ ★**⇒ 工具规格加一条硬约束: 源码里不许出现板 md5 字面量前缀·★必须拆两段·★"
        "且工具的验收线要含「落盘后自守闸仍 rc=0」★** ★ "
        "★**★同时补两条实测事实 (★main 本机本趟亲跑★)★**: ① 本单签收闸重跑会报红 1 条「别人的分片零本单登记条目 — 越界 6」⇒ "
        "★**逐条查实: 那 6 条全是【main 自己】11-23 22:55 写进 pm.yaml 的答案 (key = `iss372_need_main_*`·★机制上正常·★不是 sw-lead 越界★) "
        "⇒ 该判据把「main 答过 need」误判成「agent 越界」⇒ 同类判据在其他单上会误报·★已登记待修★** ★ "
        "② cont3 交卷页里同一批受保护件出现 **15 / 18 / 19 / 20 / 22** 五个不同件数 (★留证文件两段标题写「20 件」「3 件」, 实际列出 19 条与 4 条★) "
        "⇒ ★**24 条 md5 逐条实测全同 ⇒ 边界结论成立·★只是计数标签乱 ⇒ 引用时只准引 md5, 不准引件件数★** ★ "
        "★**板三项 (md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size 4940213) 逐字节未动 "
        "⇒ G1 仍开, 不许投板 ★**"
    )
    anchor = "\n  note_addendum:"
    k = seg.find(anchor)
    if k < 0:
        raise SystemExit("★ISS-372 段里找不到 note_addendum ⇒ 中止★")
    # ★追加到已有 note_addendum 之后 (★同段第二个字段·★追加式★)★
    end = seg.find("\n", k + len(anchor))
    # ★YAML 单行标量 ⇒ 只能在行尾追加, 写成 note_addendum_2 更安全 (★不改已有那一条★)★
    add = "\n  note_addendum_2: '%s'\n" % NOTE.replace("'", "''")
    new_seg = seg[:end] + add + seg[end:]
    new_raw = raw[:i] + new_seg + raw[j:]

    bak = LOG + ".bak_%s_main_iss372_cont3_spec" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new_raw)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LOG)

    import yaml
    d0 = yaml.safe_load(raw)
    d1 = yaml.safe_load(open(LOG, encoding="utf-8"))
    i0 = {x.get("id"): x for x in (d0.get("issues", d0) if isinstance(d0, dict) else d0)}
    i1 = {x.get("id"): x for x in (d1.get("issues", d1) if isinstance(d1, dict) else d1)}
    assert set(i0) == set(i1), "★条目集合变了 ⇒ 中止★"
    for iid in i0:
        a = dict(i0[iid])
        b = dict(i1[iid])
        if iid == "ISS-372":
            a.pop("note_addendum_2", None)
            b.pop("note_addendum_2", None)
        assert a == b, "★%s 除 note_addendum_2 外还有别的变化 ⇒ 中止★" % iid
    print("  ★issue_log 自检: 条目集合不变 + 除 ISS-372.note_addendum_2 外零变化 ⇒ ✅")
    print("  ★备份 = %s" % os.path.basename(bak))

    m1, ns1, sz1 = board_fp()
    same = (m0 == m1 == BOARD_MD5 and ns0 == ns1 and sz0 == sz1 == BOARD_SIZE)
    print("\n★收工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m1, ns1, sz1))
    print("★零写板自证: %s" % ("✅ 三项逐字节未动" if same else "❌"))
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
