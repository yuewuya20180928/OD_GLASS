#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arm_net_set_diff.py —— ★★臂 vs 基线【未连接网名集合】的差集 (★列出救回/新断的具体网名)★★

★★★**★为什么要有它 (★2026-11-09 21:5x)★★★**:
  ★**`compare_arm_baseline.sh` 只给"交集/仅A/仅B"的个数** ⇒ ★**看不出【谁被救回】和【谁被打断】**
  ⇒ ★**而"哪几个网"才是判读的关键** (★例: `JTAG_TDO`/`JTAG_TMS` 救回 vs `JTAG_TDI` 被打断 ⇒ 净 +1)
  ⇒ ★★**⇒ 这个工具把差集列成名单** ★★

★★★**★口径 (★必须写清, ★别读成"条目数")★★★**:
  · ★**一个"未连接条目" = `unconnected_items` 里的一项** (★官方板 45 条 ⇒ 涉及 43 个网)
  · ★**"网名签名" = 这条未连接涉及的所有网名 (★排序去重) 的元组** ⇒ ★**绝大多数是单网 (⇒ 签名=网名)**
  · ★**"仅A" = 只有基线有 ⇒ 候选把它【救回】了** · ★**"仅B" = 只有候选有 ⇒ 候选【打断】了它** ★★

用法:
  python3 state/arm_net_set_diff.py <基线.drc.json> <候选.drc.json>
  ⇒ rc=0 (只打印) · 打印完给一行"净账: 救回 X / 新断 Y"
"""
import json
import re
import sys


def nets_of(path):
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for it in (d.get("unconnected_items") or []):
        s = json.dumps(it, ensure_ascii=False)
        out.append(tuple(sorted(set(re.findall(r"\[([A-Za-z0-9_]+)\]", s)))))
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    a = nets_of(sys.argv[1])
    b = nets_of(sys.argv[2])
    sa, sb = set(a), set(b)
    print("基线: unc 条目 %d · 网名签名 %d" % (len(a), len(sa)))
    print("候选: unc 条目 %d · 网名签名 %d" % (len(b), len(sb)))
    only_a = sorted(sa - sb)
    only_b = sorted(sb - sa)
    print("\n★仅基线有 (★候选救回) %d:" % len(only_a))
    for x in only_a:
        print("    ✔ %s" % " + ".join(x))
    print("\n★仅候选有 (★候选打断) %d:" % len(only_b))
    for x in only_b:
        print("    ✘ %s" % " + ".join(x))
    print("\n★交集 %d · 净账: 救回 %d / 新断 %d ⇒ ★净 %+d"
          % (len(sa & sb), len(only_a), len(only_b), len(only_b) - len(only_a)))
    # ★★★★**★2026-11-10 00:6x 【★修: ★★"变小"≠"是子集" ⇒ ★★】★★★★ ★★★
    #   ★**旧写法**: ★`sb < sa` ⇒ ★**Python 的集合 `<` = 【严格子集】⇒ ★★**候选网名变少但换了一批 ⇒ 也判不过**
    #     ⇒ ★**实测**: ★v76rs 网名签名 42 → 40 (★★**变小了**★★) 却报"不通过 (★集合没变小★)" ⇒ ★**读数自相矛盾** ★★
    #   ★**文档口径** (★`compare_arm_baseline.sh` 头注 + CURRENT_TASK): ★**"网名集合必须【变小】(★不许变大/不变★)"**
    #     ⇒ ★**⇒ 判据 = 【大小】(len) ⇒ ★**改这一处** ★★
    #   ★**注意**: ★**本脚本只打印, ★不改任何闸门 rc** ⇒ ★**改它不改变任何臂的判定** ★★
    _smaller = len(sb) < len(sa)
    print("★★**判据① (网名集合必须变小 ★按【大小】★) ⇒ %s**"
          % ("通过 ✔ (★%d → %d★)" % (len(sa), len(sb)) if _smaller
             else "不通过 ✘ (★%d → %d★ ★集合没变小 ⇒ 不晋级★)" % (len(sa), len(sb))))
    print("   ★(附: ★**是不是基线的严格子集** = %s ★★⇒ ★【子集】是【更严】的口径, ★【变小】是文档口径 ★★)"
          % ("是 ✔" if sb < sa else "否 ✘ (★候选有 %d 个网名基线里没有★)" % len(only_b)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
