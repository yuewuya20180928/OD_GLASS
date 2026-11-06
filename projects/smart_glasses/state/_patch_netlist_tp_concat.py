#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
_patch_netlist_tp_concat.py —— 修第二批补丁留下的**节点串拼接**事故 (2026-11-03 10:0x)

★★ 事故复盘 (★写下来是因为它暴露了门禁的一个洞):
  · `_patch_netlist_fpc_pins.py` 的测试点改挂用 `old[:old.rfind('"')] + new + '"'` 做替换
  · ★**rfind 找的是整条 tuple 的最后一个引号, 不是第 3 个字段的引号** ⇒ 结果拼出
    `"CONN_CAM pin11"CONN_CAM pin20"` 这种**两个节点串粘在一起**的垃圾节点
  · ★**为什么门禁没抓住**: 新写的 `check_netlist_pins.py` 用正则 `^REF pin\d+$` 解析节点
    ⇒ 垃圾串**匹配不上** ⇒ 被当成"不是针脚"⇒ **静默漏过**
  ⇒ ⇒ 本次同时补一条 **C6 节点串格式门禁**: 任何节点串里出现第二个 "pin" 组 ⇒ 立即报错

修法: 把 13 处粘连串还原成"新针脚"那个 (`"REF pinN"REF pinM"` → `"REF pinM"`)
"""
import ast
import os
import re
import sys

GEN = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/gen_netlist.py'


def main():
    src = open(GEN, encoding='utf-8').read()
    pat = re.compile(r'"([A-Za-z_0-9]+) pin(\d+)\1 pin(\d+)"')
    hits = pat.findall(src)
    print(f'发现粘连节点串 {len(hits)} 处:')
    for a, b, c in hits:
        print(f'   {a} pin{b} + {a} pin{c}  ⇒  {a} pin{c}')
    src2 = pat.sub(lambda m: f'"{m.group(1)} pin{m.group(3)}"', src)
    # 还要检查有没有三个一组的
    pat3 = re.compile(r'"([A-Za-z_0-9]+) pin(\d+)\1 pin(\d+)\1 pin(\d+)"')
    src2 = pat3.sub(lambda m: f'"{m.group(1)} pin{m.group(4)}"', src2)
    ast.parse(src2)
    open(GEN, 'w', encoding='utf-8').write(src2)
    print(f'✅ 已修复并落盘 {GEN} (语法自检通过)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
