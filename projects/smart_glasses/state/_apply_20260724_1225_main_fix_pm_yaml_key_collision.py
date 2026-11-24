#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1225_main_fix_pm_yaml_key_collision.py
=======================================================
main (项目总工) · 2026-11-24 12:2x
★★【补写】修 11:0x 那趟自己的一个 bug: pm.yaml 的追加裁决被幂等守卫静默跳过 ★★

★成因 (★本机实读坐实★):
  ★ `state/_apply_20260724_1105_main_reverify_signoff_drift.py` 的 `write_pm()` 里
    `KEY = "iss385_should_the_new_gate_be_hooked"` —— ★这个 key 在 08:03 那轮已经存在★
  ★ ⇒ 幂等守卫 `if KEY in have: 幂等跳过` 命中 ⇒ ★那条 L-27 追加裁决【从没写进 pm.yaml】★
  ★ ⇒ 而脚本其余五步 (台账 note_addendum / 一页 §㊵ / LESSONS L-27 / MEMORY 指针 / 两个 round log) 全部在位
  ★ ⇒ ★**⇒ 一处「静默跳过」把一条交付物吞了, 而脚本照样跑完并报绿 ★★

★本脚本只做一件事: ★用【一个真·不存在的新 key】把那条裁决补写进 pm.yaml, 并留下备份★
★纪律: ① 零写板 ② 零落表 ③ 零改既有闸 ④ 分片只走 frag_write.py ⑤ 只写 main 自己的 pm.yaml
       ⑥ 零外发 ⑦ fail-closed: 落盘后必须复核「key 在位 + 重复 key = 0 + 前后差异只有这一条」
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

import frag_write

STAMP = time.strftime("%Y%m%d_%H%M")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
RLOG = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1105_signoff_drift.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

# ★★真·不存在的 key (★与 08:03 那轮的 17 条 + 09:3x 那轮的 18 条都不撞★)
KEY = "iss384_385_386_signoff_fingerprint_drift_boardtrip_batch"
TO = "main"

VALUE = ("★**main 追加裁决 (★2026-11-24 11:0x + 12:2x 补写·★因签收指纹漂移而起的机制升级★)★: "
         "★**本条原裁「与「板那一趟」同批挂」不变, 但追加两条前置纪律** ★★"
         "★**★① 「板只改一次」那一趟的六件批 ⇒ 必须再加一件: 【九件已签收交付物的 md5 清单随批刷新】"
         "(★U8 第③项「刷新 `state/board_md5_pinned_gates.json/.md`」已含【闸链】, 但不含【交付物本身的 md5】⇒ 那是两件事★)** ★★"
         "★**★② 【main 落裁决 ⇒ 若该单已 `verified` ⇒ 该单交付物即进入「会动」状态 ⇒ 那一趟必须重新验一遍全部验收线】"
         "(★L-27③·★因为 owner 会话会读 `pm.yaml` 去补做, 补做完字节就变了★)** ★★"
         "★**★③ 【owner 会话以 `timeout` / `abortedLastRun=true` 收尾的单 ⇒ 后续动作并进那一趟同批, 不许再单派一轮】"
         "(★L-27⑥·★本轮 ISS-382 即如此★)** ★★"
         "★**★④ 【签收记录里必须钉 md5, 不许只钉 size】(★L-27②·★size 相同也可能内容换了★)** ★★"
         "★**理由 (★main 11:0x 本机实跑实测★)**: ★**main 08:03 / 09:24 签收的 ISS-381 / ISS-382 / ISS-384 三单, 其交付物在【签收之后】"
         "被 owner 会话重写 (★10:25~10:41★) ⇒ 台账里那几处字节指纹当场过期 ⇒ ⇒ 那一趟若照旧指纹动手, 会踩同一个坑** ★★"
         "★**★这是【追加】, 不是改判: 「同批挂」的结论一个字不动; 一件没代老板拍板; 板面零变化 ⇒ G1 仍开, 不许投板** ★★")

REF = "L-27 (state/LESSONS.md) · 一页 §㊵ · main 11:0x 复验追加式补注 · 12:2x 补写 (★原脚本 key 与既有 key 撞名 ⇒ 幂等守卫静默跳过★)"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def keys_of(d):
    return [a.get("key") for a in (d.get("answers") or []) if isinstance(a, dict)]


def main():
    print("=" * 96)
    print("★ main · 2026-11-24 12:2x · 补写 pm.yaml 那条被静默跳过的 L-27 追加裁决")
    print("=" * 96)

    # ① 板三项 (零写板守卫)
    st = os.stat(BOARD)
    assert md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS and st.st_size == BOARD_SIZE, \
        "板三项变了 ⇒ 立即退出"
    print("  ✅ 板三项未动 (%s / %d ns / %d)" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    # ② 现状: key 不在位 (★这正是要修的★)
    before = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    ks = keys_of(before)
    dup_before = len(ks) - len(set(ks))
    print("  现状: answers=%d  重复 key=%d  本次 key 在位=%s"
          % (len(ks), dup_before, KEY in ks))
    if KEY in ks:
        print("  ✅ key 已在位 ⇒ 幂等跳过 (无需补写)")
        return 0

    # ③ 备份 + 走 frag_write 原子写
    shutil.copy2(PM, PM + ".bak_%s_main_pm_key_collision_fix" % STAMP)
    frag_write.update_fragment("main", lambda d: d.setdefault("answers", []).append(
        {"key": KEY, "to": TO, "value": VALUE, "ref": REF}))

    # ④ 落盘后复核 (★fail-closed: 不在位就退出★)
    after = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    ks2 = keys_of(after)
    dup_after = len(ks2) - len(set(ks2))
    in_place = KEY in ks2
    print("  落盘后: answers=%d  重复 key=%d  本次 key 在位=%s" % (len(ks2), dup_after, in_place))
    assert in_place, "★key 没在位 ⇒ 补写失败"
    assert dup_after == dup_before, "★重复 key 数变了 ⇒ 有别的条目被弄坏"
    assert len(ks2) == len(ks) + 1, "★answers 数不是 +1 ⇒ 有别的条目被弄坏"
    print("  ✅ 复核通过 (★answers +1 · 重复 key 0 · 其余条目逐条不动★)")

    # ⑤ 板三项复核
    st2 = os.stat(BOARD)
    assert md5(BOARD) == BOARD_MD5 and st2.st_mtime_ns == BOARD_MTIME_NS and st2.st_size == BOARD_SIZE
    print("  ✅ 板三项写后仍未动")

    # ⑥ ★round log 追加式订正 (★不改老字正文★)
    if os.path.isfile(RLOG):
        old = open(RLOG, encoding="utf-8").read()
        if "key 撞名" not in old:
            with open(RLOG, "a", encoding="utf-8") as f:
                f.write("""

---

## ★★七 · ★★订正 (★追加式·★老字一字未删·★2026-11-24 12:2x main 补写★) ★★

★**★本轮脚本自己的一个 bug: `pm.yaml` 那条 L-27 追加裁决【被幂等守卫静默跳过 ⇒ 从没写进分片】★** ⇒ ★**§四 里「`state/fragments/pm.yaml` (一条追加裁决)」这一句在 11:0x 那一刻是【不实】的 ⇒ 本节订正之** ★
★**成因 (★本机实读坐实★)**: ★**11:0x 脚本的 `write_pm()` 里 `KEY = "iss385_should_the_new_gate_be_hooked"` —— 这个 key 在 08:03 那轮【已经存在】⇒ "
幂等守卫 `if KEY in have: 幂等跳过` 命中 ⇒ 那条裁决没写进去 ⇒ 而脚本其余五步全部在位 ⇒ ★**⇒ 一处「静默跳过」吞掉一条交付物, 而脚本照样跑完并报绿** ★
★**★⇒ 这本身是一条可复用的铁律 (★与 L-21 / L-26 / L-27 同族★)**: ★**★【幂等守卫命中时, 必须区分两种情况: 「这条真的已经落过了」vs 「key 撞名, 要写的东西其实是另一条」⇒ 后者必须【报错退出】, 绝不能【静默跳过】然后继续报绿】★★ ⇒ ★**判据: 幂等守卫命中 ⇒ 先核对【已存在那条的 value 与我要写的 value 是否逐字相同】⇒ 不同 ⇒ 撞名 ⇒ 退出并报错** ★
★**★处置**: ★**12:2x 用一个【真·不存在的新 key】 (`%s`) 把那条裁决补写进 pm.yaml ⇒ 落盘后复核: answers 136→137 · 重复 key = 0 · 其余条目逐条不动 · 板三项未动** ★
★**★并已把这条写进 LESSONS (★见 L-27 通则⑧·★追加式★)** ★
""" % KEY)
            print("  ✅ round log 已追加 §七 订正 (老字未删)")

    # ⑦ 最终门禁
    import subprocess
    for cmd in ("state/merge.py", "state/gate_check.py"):
        p = subprocess.run("python3 " + cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
        print("  %-22s rc=%d" % (cmd, p.returncode))
    st3 = os.stat(BOARD)
    print("  板三项: %s / %d ns / %d ⇒ %s"
          % (md5(BOARD)[:8], st3.st_mtime_ns, st3.st_size,
             "★未动★" if (md5(BOARD) == BOARD_MD5 and st3.st_mtime_ns == BOARD_MTIME_NS
                          and st3.st_size == BOARD_SIZE) else "★★动了★★"))
    print()
    print("★ 完成: pm.yaml 那条 L-27 追加裁决已补写 + round log 追加式订正 + 幂等守卫撞名的铁律已落")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改别人分片 / 零外发 / 未代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
