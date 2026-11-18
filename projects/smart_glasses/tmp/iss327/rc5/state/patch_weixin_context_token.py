#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_weixin_context_token.py —— 给微信 channel 打补丁: 定时/无入站上下文的投递也要带上 context_token

══════ 为什么要打这个补丁 (2026-11-02 18:4x 老板报"手机端微信查看不到终端的状态") ══════
现象: cron 的 announce 投递 **delivered=true**, 但老板在手机微信里看不到这条状态。
根因: 插件的 `sendWeixinOutbound()` 只用 `params.contextToken` —— 那个值来自**入站消息**。
      定时任务没有入站消息 ⇒ contextToken 为空 ⇒ 走 "sending without context" 分支
      ⇒ 微信侧没有会话上下文 ⇒ 消息落不到老板那个会话 (日志: "contextToken missing for to=...")。
      ★**入站时 context token 已按 (accountId, userId) 落盘** (accounts/<id>.context-tokens.json),
      插件也提供了 `getContextToken(accountId, userId)` —— 只是 outbound 这条路没去查。

修法: outbound 缺 token 时, 按 (accountId, to) 反查存储补上。

★**幂等**: 打过补丁后再跑本脚本不会重复打 (靠 PATCH_MARK 判定)。
★**可重放**: 插件被 npm 更新覆盖后, 重跑本脚本即可恢复。
★**风险**: 改的是 vendor 代码 (dist/src/channel.js)。改动只有一处, 不改协议不改加密;
  若插件升级, 以新版为准, 本补丁会被覆盖 —— 所以本脚本必须留在仓库里 (随项目走)。

用法: python3 state/patch_weixin_context_token.py [--check]
"""
import os
import re
import sys

HOME = os.path.expanduser("~")
TARGET = os.path.join(HOME, ".openclaw/npm/node_modules/@tencent-weixin/openclaw-weixin/dist/src/channel.js")
MARK = "★PATCH(2026-11-02 moli: contextToken fallback)"

OLD = """    if (!params.contextToken) {
        aLog.warn(`sendWeixinOutbound: contextToken missing for to=${params.to}, sending without context`);
    }"""

NEW = """    // {MARK}
    // 定时/cron 投递没有入站消息 => params.contextToken 为空 => 消息"不带 context"发出,
    // 微信侧落不到对应会话 (老板手机上看不到状态)。缺 token 时按 (accountId, to) 反查存储补上。
    let contextToken = params.contextToken;
    if (!contextToken) {
        contextToken = getContextToken(account.accountId, params.to);
        if (contextToken) {
            aLog.info(`sendWeixinOutbound: contextToken resolved from store for to=${params.to}`);
        }
        else {
            aLog.warn(`sendWeixinOutbound: contextToken missing for to=${params.to}, sending without context`);
        }
    }""".replace("{MARK}", MARK)

OLD_CALL = """                contextToken: params.contextToken,
                accountId: account.accountId,"""
NEW_CALL = """                contextToken: contextToken,
                accountId: account.accountId,"""


def main():
    check_only = "--check" in sys.argv
    if not os.path.exists(TARGET):
        print(f"[FAIL] 找不到插件源码: {TARGET}")
        return 1
    src = open(TARGET, encoding="utf-8").read()

    if MARK in src:
        print(f"[OK] 补丁已存在 (无需重打) :: {TARGET}")
        return 0
    if check_only:
        print("[CHECK] 未打补丁")
        return 2
    if OLD not in src:
        print("[FAIL] 找不到目标代码块 —— 插件版本可能变了, 需要人工看 (不要盲改)")
        return 1
    if "getContextToken" not in src:
        print("[FAIL] channel.js 里没有 getContextToken 的引用, 无法安全打补丁")
        return 1

    src = src.replace(OLD, NEW, 1)
    if OLD_CALL not in src:
        print("[WARN] 没找到 contextToken: params.contextToken 的调用点, 已只改警告段 —— 需要人工复核")
    else:
        src = src.replace(OLD_CALL, NEW_CALL, 1)

    backup = TARGET + ".bak-pre-ctx-token-patch"
    if not os.path.exists(backup):
        open(backup, "w", encoding="utf-8").write(open(TARGET, encoding="utf-8").read())
        print(f"[backup] {backup}")

    open(TARGET, "w", encoding="utf-8").write(src)
    print(f"[OK] 已打补丁 :: {TARGET}")
    print("★**需要重启网关才生效**: openclaw gateway restart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
