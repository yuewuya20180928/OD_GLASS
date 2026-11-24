#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0615_main_iss379_self_contamination_disclosure.py
===================================================================
main (项目总工) · 2026-11-24 06:1x
★★★ 自曝: main 本轮在【自己的复核探针】里污染了 ISS-379 的交付物 (真相页) ★★★
  ⇒ 已逐字节还原 ⇒ 已 clean-state 重验 ⇒ 现在把这件事【追加式】记进台账 + 教训文件 ★★★

★事故经过 (★完整·★不删改·★逐条可复现★):
  ① main 为验证「交卷页 B6 贴的『边界环 12000 格』与闸现读『3010 格』为何对不上」,
     造了一个沙盒: `cp -al HW tmp/iss379_probe` (★-al = 归档+硬链接★)
  ② 沙盒里把页面 FEAS.evidence_json 指针逐个指向四份 JSON 各跑一遍闸
  ③ ★★该脚本用 `open(page,"w")` 写沙盒里的页面 —— ★★但 `cp -al` 造的是【硬链接】★★
     ⇒ ★★`open(w)` 会【截断共享的 inode】⇒ ★★写穿到真件 HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md★★
  ④ 结果: 真件被改成指向最后一份 (modeB 归档件), 字节数 51433 → 51469
  ⑤ ★★main 自己发现了它 (★签收脚本跑完后核对页大小时读到 51469★)★★

★处置 (★已执行★):
  ① 从本会话 05:53 存下的 pristine 副本 (★tmp/iss349 那份, ★当时 md5=8962321c·51433 B★) 逐字节还原
  ② 还原后实测: md5=8962321c2b94630a221b60fdbff4a5b1 · size=51433 · mtime=2026-11-24 05:13:38.788492032 (★与 agent 交付时逐字一致★)
  ③ clean-state 重验: 闸 rc=0 (9/9) · --selftest rc=0 (19/19) · 第三路独立复算 rc=0 ⇒ 与事故前读数【逐字相同】
  ④ 顺带还原了被同一硬链接连带改掉的 tmp/iss349 那份副本
  ⑤ 台账里 ISS-379 的 verify_result 【不含任何页字节数/页 md5】⇒ ★★签收结论本身未被污染★ ⇒ 无需重签

★纪律: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 未替老板拍板
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import yaml

STAMP = time.strftime("%Y%m%d_%H%M")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PAGE = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213
PAGE_MD5 = "8962321c2b94630a221b60fdbff4a5b1"
PAGE_SIZE = 51433


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def ns_of(s):
    import datetime
    base, _, frac = s.partition(".")
    frac = (frac + "000000000")[:9]
    tz8 = datetime.timezone(datetime.timedelta(hours=8))
    dt = datetime.datetime.strptime(base, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz8)
    return int(dt.timestamp()) * 10 ** 9 + int(frac)


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


NOTE = (
    "★2026-11-24 06:1x main 【自曝 · main 自己的复核探针污染了本单的交付物 · 已还原 · 结论不受影响】★★ "
    "★**追加式·★老字一字未删·★不改 status/verify_result**★ ★ "
    "★**① 事故经过 (★完整·★不删改★)★**: main 为核查「交卷页 B6 贴的『边界环 `12000` 格』与闸现读『`3010` 格』为何对不上」, "
    "造沙盒 `cp -al HW tmp/iss379_probe` (★`-al` = 归档 + **硬链接**★) ⇒ 沙盒脚本用 `open(page,\"w\")` 改页面指针 ⇒ "
    "★**`open(w)` 截断【共享的 inode】⇒ 写穿到真件 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md`★** ⇒ ★**真件被改成指向最后那份 (modeB 归档件)·"
    "字节数 51433 → 51469** ⇒ ★**是 main 自己核对页大小时发现并当场还原的 (★不是 agent 的问题★)** ★ "
    "★**② 处置 (★已执行·★逐条可复现★)★**: 从本会话 05:53 存下的 pristine 副本 (★`tmp/iss349/...` 那份·★当时 md5 `8962321c`·51433 B★) "
    "★**逐字节还原** ⇒ 还原后实测 ★**md5 `8962321c2b94630a221b60fdbff4a5b1` · size `51433` · mtime `2026-11-24 05:13:38.788492032`·★"
    "**与 agent 交付时逐字一致**★ ⇒ ★**clean-state 重验: 闸 rc=0 (9/9) · `--selftest` rc=0 (19/19) · 第三路独立复算 rc=0 ⇒ 与事故前读数【逐字相同】**★ ⇒ "
    "★**顺带还原了被同一硬链接连带改掉的 `tmp/iss349` 那份副本** ★ "
    "★**③ 为什么【不用重签】(★这一条是关键★)★**: 本单 `verify_result` 里 ★**不含任何【页字节数】或【页 md5】**★ (★它记的是「交付物在盘 (≥4000 B)」这类判据·★不含指纹★) "
    "⇒ ★**⇒ 签收结论本身从未被污染·★判据与结论全部成立·★故 status 维持 verified·★不重签** ★ "
    "★**④ 顺着这件事追加的一条【真发现】(★事故之外的收获·★独立于事故★)★**: 交卷页 B6 贴的「边界环 `12000` 格」与闸现读「`3010` 格」对不上 ⇒ "
    "★**main 的穷举结论: ① 连跑 3 次闸 ⇒ 逐字都是 `3010` (★确定性成立★) ② 页面指针逐个指向【四份 JSON】各跑一遍 ⇒ **四份全部都是 `3010`** ⇒ "
    "★**这个数与「读哪份 JSON」无关** ⇒ ③ `logs/iss379/gate_run_20261124.txt` (05:17) 落盘的也是 `3010` ⇒ ★**⇒ B6 那段是【追加式留下的老读数】·★"
    "而 B8 段与真相页 §10.1 写的都是 `3010` (★与现读一致★)⇒ ★**⇒ 引用时只准引 `3010`, 不许引 `12000`** ★ "
    "★**⑤ ★★新铁律 (★已写进 `state/LESSONS.md` 的 L-24·★main 独占写★)★★**: ★**沙盒副本一律用【真复制】(`cp -a`·★或 `cp -r`★), "
    "绝不用 `cp -al` 的硬链接版去「写」★ ⇒ ★**硬链接 + `open(w)` = 写穿真件 (★本轮真事故·★代价 = 一件交付物被改 36 字节·★幸而本会话手里有 pristine 副本·★否则不可逆★)** ★"
)

L24 = """

## ★L-24 · ★★沙盒副本不许用硬链接 (`cp -al`) 去「写」⇒ `open(w)` 会截断共享 inode ⇒ 写穿真件★★

★**实测 (2026-11-24 05:4x~06:1x, main 本机实跑 · ISS-379 复核探针 · ★真事故·★已还原★)★**: main 为核查「交卷页贴的读数与闸现读为何对不上」, 造沙盒 `cp -al HW tmp/iss379_probe` (★`-al` = 归档 + **硬链接**★) ⇒ ★**沙盒里的文件与真件【共享同一个 inode】** ★ ⇒ 沙盒脚本用 ★**`open(page, "w")`** 改页面指针 ⇒ ★★`open(w)` 的截断作用在【共享 inode】上 ⇒ ★★真件 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` 被写穿 (★字节数 51433 → 51469, ★内容被改成指向另一份 JSON★)★★ ⇒ ★**是 main 自己核对页大小时发现并当场还原的 (★幸而本会话手里有 pristine 副本·★否则不可逆★)** ★

★**⇒ 通则 ①**: ★**沙盒副本一律用【真复制】(`cp -a` / `cp -r`), 【绝不用 `cp -al` 的硬链接版去「写」】** ⇒ ★**硬链接 + 写操作 = 写穿真件·★而且【静默无报错】·★只有事后核对大小/mtime 才发现** ★
★**⇒ 通则 ②**: ★**★沙盒跑完必须核对【真件指纹未变】(★md5 + mtime + size 三项·★纳秒级★)⇒ 这不是「可选的自证」·★是【沙盒操作的必要收尾】★★ ⇒ ★**本轮正是靠这一步才发现的 (★若没核对 ⇒ 一件交付物带着错指针被签收·★而且外部看不出来★)** ★
★**⇒ 通则 ③**: ★**★`cp -al` 不是不能读·★只读场景它更快更省盘·★但【任何会写它的地方】必须换成真复制★★ ⇒ ★**判据 = 「我会不会对这个副本调 `open(w)` / `write_text` / `>` 重定向」⇒ 会 ⇒ 换成真复制** ★
★**⇒ 通则 ④**: ★**★「我造成的事故」也要追加式留痕 (★台账 note + LESSONS 一条)⇒ 【自曝】是纪律的一部分·★不是可选的自我批评·★因为下一次别人做同样的操作时, 留下的痕迹才是拦它的那道闸★** ★
★**★与 L-21 / L-22 / L-23 合看**: ★**四条都是同一类 —— 【工具/沙盒/闸自己的口径与副作用必须自己写清】·★本条是【副作用】那一面: 前三条讲「怎么判对」·★本条讲「怎么别弄坏东西」★** ★
"""


def main():
    m0, ns0, sz0 = board_fp()
    print("★开工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m0, ns0, sz0))

    # ---- 0. 先断言交付物已回到 agent 交付时的原样 ----
    pm = md5(PAGE)
    ps = os.path.getsize(PAGE)
    print("★交付物当前: md5=%s size=%d (期望 %s / %d)" % (pm, ps, PAGE_MD5, PAGE_SIZE))
    assert pm == PAGE_MD5 and ps == PAGE_SIZE, "★交付物还没还原 ⇒ 中止★"

    # ---- 1. issue_log: ISS-379 追加 note_addendum_2 (追加式) ----
    print("\n" + "=" * 90)
    print("★issue_log.yaml · ISS-379 追加 note_addendum_2 (★追加式·★不改 status/verify_result★)")
    print("=" * 90)
    src = open(LOG, encoding="utf-8").read()
    i = src.find("\n- id: ISS-379")
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    seg = src[i:j]
    anchor = "\n  note_addendum_2:"
    if anchor in seg:
        print("  ★已有 note_addendum_2 ⇒ 跳过")
    else:
        add = "\n  note_addendum_2: '%s'\n" % NOTE.replace("'", "''")
        k = seg.find("\n  dispatched_at:")
        if k < 0:
            raise SystemExit("★找不到 dispatched_at ⇒ 中止★")
        new_seg = seg[:k] + add + seg[k:]
        new_src = src[:i] + new_seg + src[j:]
        bak = LOG + ".bak_%s_main_iss379_disclosure" % STAMP
        shutil.copy2(LOG, bak)
        tmp = LOG + ".tmp_%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(new_src)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, LOG)
        d0 = yaml.safe_load(src)
        d1 = yaml.safe_load(open(LOG, encoding="utf-8"))
        i0 = {x.get("id"): x for x in (d0.get("issues", d0) if isinstance(d0, dict) else d0)}
        i1 = {x.get("id"): x for x in (d1.get("issues", d1) if isinstance(d1, dict) else d1)}
        assert set(i0) == set(i1), "★条目集合变了 ⇒ 中止★"
        for iid in i0:
            a, b = dict(i0[iid]), dict(i1[iid])
            if iid == "ISS-379":
                a.pop("note_addendum_2", None)
                b.pop("note_addendum_2", None)
            assert a == b, "★%s 有别的变化 ⇒ 中止★" % iid
        print("  ★自检: 条目集合不变 + 仅 ISS-379 加了 note_addendum_2 ⇒ ✅")
        print("  ★备份 = %s" % os.path.basename(bak))

    # ---- 2. LESSONS: 追加 L-24 ----
    print("\n" + "=" * 90)
    print("★state/LESSONS.md · 追加 L-24 (★main 独占写·★追加式★)")
    print("=" * 90)
    lsrc = open(LESSONS, encoding="utf-8").read()
    if "L-24" in lsrc:
        print("  ★L-24 已存在 ⇒ 跳过")
    else:
        bak = LESSONS + ".bak_%s_main_l24" % STAMP
        shutil.copy2(LESSONS, bak)
        tmp = LESSONS + ".tmp_%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(lsrc + L24)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, LESSONS)
        assert open(LESSONS, encoding="utf-8").read().startswith(lsrc), "★老字被改 ⇒ 中止★"
        print("  ★备份 = %s" % os.path.basename(bak))
        print("  ★自检: 老字逐字保留 + 只在末尾追加 ⇒ ✅")

    m1, ns1, sz1 = board_fp()
    same = (m0 == m1 == BOARD_MD5 and ns0 == ns1 == ns_of(BOARD_MTIME) and sz0 == sz1 == BOARD_SIZE)
    print("\n★收工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m1, ns1, sz1))
    print("★零写板自证: %s" % ("✅ 三项逐字节未动" if same else "❌"))
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
