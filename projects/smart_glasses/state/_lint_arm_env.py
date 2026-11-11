#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_lint_arm_env.py -- ★★★【★扫所有臂脚本: env 块里的变量名必须是合法标识符★】★★★ ★

★★★**★为什么必须有这个 linter (★2026-11-11 08:1x 实测踩到★)★★★ ★★★
  ★**事故**: ★★**我在 `env` 块里写了带 ★ 的注释行** ★★
    ```
      env PCB_LAYERS=8 ... \\
          ★★★【★唯一变量★】PCB_GRID=0.125 \\
    ```
    ⇒ ★★**bash 把 `★★★【★唯一变量★】PCB_GRID=0.125` 整个当成【变量名】⇒ ⇒ `PCB_GRID` 根本没被设置!** ★★
    ⇒ ★★**⇒ 臂照跑不误 ⇒ 读数也"正常" ⇒ ⇒ 【假结论】(★我还据此写了"窄版直行无效"的铁律★)** ★★★
  ★★★**★铁律: ★【脚本写了 ≠ 传下去了 ≠ 进程收到了】★★★ ★★ ⇒ ★⇒ **必须机器验**: ★★**
    ① ★本 linter: ★**静态扫** env 块里的变量名是否合法 ★★
    ② ★**起臂后查 `/proc/<pid>/environ`**: ★**看进程真正收到的变量名** (★已实测有效: ★它当场抓出了这个 bug★) ★★
    ③ ★**对比 env diff**: ★**起臂后把两臂的 env 全量 diff 一遍** ★★

★**用法**: ★`python3 state/_lint_arm_env.py [state/v76*_arms.sh ...]` (★不给参数 ⇒ 扫 state/ 下所有 *_arms.sh★) ★
★**退出码**: 0 = 全过; 1 = 有臂的 env 块含非法变量名 ★
"""
import glob
import os
import re
import sys

VALID = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def lint(path):
    bad = []
    in_env = False
    with open(path, encoding='utf-8', errors='ignore') as f:
        for ln, line in enumerate(f, 1):
            s = line.strip()
            if not in_env:
                if s.startswith('env ') or s == 'env':
                    in_env = True
                    rest = s[4:].strip() if s.startswith('env ') else ''
                    if rest and not rest.endswith('\\'):
                        in_env = False
                continue
            # 在 env 块里
            if not s.endswith('\\'):
                in_env = False
                continue
            body = s[:-1].strip()
            if not body or body.startswith('#'):
                continue
            tok = body.split()[0] if body.split() else ''
            if '=' not in tok:
                # ★**env 块的最后一行是【命令】(★如 `timeout 21600 bash ...`★) ⇒ 不是变量 ⇒ 跳过★★
                continue
            name = tok.split('=', 1)[0]
            if not VALID.match(name):
                bad.append((ln, name, "★变量名含非法字符 ⇒ bash 会当成别的变量 ⇒ ★★该变量根本没生效★★"))
    return bad


def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v76*_arms.sh")))
    nb = 0
    for p in files:
        bad = lint(p)
        if not bad:
            continue
        nb += 1
        print("❌ %s" % os.path.basename(p))
        for ln, name, why in bad:
            print("     行 %-4d  变量名 = %r" % (ln, name[:60]))
            print("            %s" % why)
    print("── 扫了 %d 个臂脚本 · 有问题的 %d 个" % (len(files), nb))
    return 1 if nb else 0


if __name__ == "__main__":
    sys.exit(main())
