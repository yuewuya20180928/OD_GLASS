#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_restore_sw_docs_20261118_1445.py —— 把 2026-11-18 14:25 那次「软链沙盒写穿真件」的位号改名【原样回退】

★事故 (★main 本机实读 · 2026-11-18 14:38~14:47)★:
  · ISS-327 (sw-lead · 兄弟 job fb67af40 14:21 派出) 的沙盒造场脚本
    `logs/iss327/iss327_sb_make.py`:
      ② SW 目录:  ★**`SW/*.md` 全部 `os.symlink()` 软链到真件** (★只有 `SW/tools/` 用真拷贝★)
      ⑤ `build_sw_docs()`: ★**直接 `open(root/SW/<name>.md, "w")` 写那个软链路径** ⇒ ★写穿到真件★
    ⇒ 后果: ★**真件 `SW/*.md` 42 份 / 781 处被改成「改名后」位号 (旧名 + "_1")** ★
    ⇒ 而板/网表/脚表/BOM 走的是 `replace()` (先删软链再写真文件) ⇒ ★那四件真源没被动 (md5 实测未变)★
    ⇒ ★**后果: 板还是旧名 · 文档先变成新名 ⇒ ISS-318「SW 侧位号引用可达性闸」红 (58 真隐患) ⇒ gate_check rc=1**
      (★该闸 14:23 是绿的: `logs/iss327/01_baseline/check_sw_ref_reachability.txt` rc=0 · MISSING=3·OK=78·DRIFT=0★)

★为什么回退是对的 (★不是掩盖·是恢复项目既定口径★):
  ① ISS-321 (verified) 自己写下: 「★**改名方案文档本身会把 ISS-318 漂移闸带红** ⇒ 正解 = ★**清单进 `logs/` (闸不扫) + 不写死改名后名**★」
  ② ISS-323 (verified) 第 7 件只交【DRY-RUN 清单】(`logs/iss323/14_rename_sw_docs_dryrun.txt`) ⇒ ★**没落地**★
  ③ 「板只改一次」铁律: ★**位号改名必须板/网表/脚表/BOM/SW 文档【同批】落地** ⇒ 文档先改名 = 板与文档分叉★
  ⇒ ★**所以真件 SW 文档的正确状态 = 旧名 + 闸绿** ⇒ 本脚本把它恢复回去 ★

★回退手法 (★精确逆运算·不是拍脑袋改★):
  · 映射来源 = `tmp/iss327/rename_map_iss327.json` 的 `rename` (186 条 old→new)
  · 逆映射 = new→old (186 条) ★**逐字唯一·可逆**★ (★所有 new 形如 old+"_1" · old 形如 R_PU_PG 无数字尾 ⇒ 无歧义★)
  · 替换算法 = ★**与事故脚本逐字同款**: 词边界 `(?<![A-Za-z0-9_])NAME(?![A-Za-z0-9_])` + 键按长度倒序★
  · 覆盖范围 = `SW/*.md` (★与事故脚本第 ⑤ 步逐字同范围★)
  · 先备份 (★`logs/iss327/04_renamed_docs_backup/` ★保留事故现场·不销毁证据★)

★边界: ★零写板 · 零落表 · 零改闸 · 零改闸脚本 · 只动 `SW/*.md` 的【被写穿的那部分内容】★ · 零外发 ★
"""
import json
import os
import re
import shutil
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SW = os.path.join(PROJ, "SW")
MAP = os.path.join(PROJ, "tmp", "iss327", "rename_map_iss327.json")
BAK = os.path.join(PROJ, "logs", "iss327", "04_renamed_docs_backup")


def main() -> int:
    data = json.load(open(MAP, encoding="utf-8"))
    ren = data.get("rename") or {}
    if not ren:
        print("[FAIL] 映射为空")
        return 2
    inv = {new: old for old, new in ren.items() if new != old}
    keys = sorted(inv.keys(), key=len, reverse=True)
    print("★映射: rename=%d 条 · 逆映射=%d 条 (new→old)" % (len(ren), len(inv)))

    # ---- ① 备份事故现场 (★真件现状 = 改名后★) ----
    os.makedirs(BAK, exist_ok=True)
    n_bak = 0
    for name in sorted(os.listdir(SW)):
        if not name.endswith(".md"):
            continue
        shutil.copyfile(os.path.join(SW, name), os.path.join(BAK, name))
        n_bak += 1
    print("★备份: %d 份真件 SW/*.md → %s (★事故现场留证·不销毁★)" % (n_bak, os.path.relpath(BAK, PROJ)))

    # ---- ② 精确逆运算 ----
    total = 0
    touched = []
    for name in sorted(os.listdir(SW)):
        if not name.endswith(".md"):
            continue
        p = os.path.join(SW, name)
        txt = open(p, encoding="utf-8", errors="replace").read()
        orig = txt
        hits = 0
        for new in keys:
            old = inv[new]
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(new) + r"(?![A-Za-z0-9_])")
            txt, c = pat.subn(old, txt)
            hits += c
        if hits:
            with open(p, "w", encoding="utf-8", errors="replace") as f:
                f.write(txt)
            total += hits
            touched.append((name, hits))
    print("★回退: %d 份文件 / %d 处位号引用改回旧名" % (len(touched), total))
    for name, hits in touched:
        print("   · %-46s %4d 处" % (name, hits))

    # ---- ③ 自检: 新名一个都不该剩 ----
    left = 0
    for name in sorted(os.listdir(SW)):
        if not name.endswith(".md"):
            continue
        txt = open(os.path.join(SW, name), encoding="utf-8", errors="replace").read()
        for new in keys:
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(new) + r"(?![A-Za-z0-9_])")
            left += len(pat.findall(txt))
    print("★自检: 真件里残留的「改名后位号」token = %d (★期望 0★)" % left)
    return 0 if left == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
