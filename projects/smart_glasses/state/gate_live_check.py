#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_live_check.py -- ★【闸的【真路由器】体检: 开臂前必跑】★★★

★★**它要拦什么 (★2026-11-11 02:4x 今晚连中两次★)** ★★
  · ★**形态①**: 闸真的生效, 但作用在【每一个同排邻脚网】身上 ⇒ ⇒ 扰动全板 ⇒ ⇒ 板级净账 0 ★★
  · ★**形态② (★最隐蔽★)**: 闸【根本没生效】⇒ 两臂等价 ⇒ ⇒ 白跑一小时 ★★
    ⇒ ★★**⇒ 根因: 单测用的是【替身】(Fake) ⇒ 单测全绿 ≠ 闸在真板上生效** ★★
    ⇒ ★★**⇒ 本脚本用【真 `GridRouter` + 真板 + 【臂上的真实 env】】调那个函数 ⇒ ⇒ 它返回几就是几** ★★

★★**它怎么知道"臂上的真实 env"** ★★
  · 从 `state/v76mw_arms.sh` 这类臂脚本里【抠出 PCB_* 环境】⇒ ⇒ 用【臂的 env】而不是【当前 shell 的 env】 ★★
  · ★★**⇒ 因为 `PCB_W_MIN` / `PCB_HALO_MARGIN` 会直接改 `_need` ⇒ ⇒ 用错 env 算出来的数不是臂上的数** ★★

用法:
  bash state/pcbnew_py.sh state/gate_live_check.py --arm-script state/v76mw_arms.sh
      ★从臂脚本抠 env ⇒ 在真路由器上调闸 ⇒ 打印"闸返回几步" ⇒
      ★**返回 0 ⇒ 闸在这个臂上【不生效】⇒ 不许开臂** ★★
  bash state/pcbnew_py.sh state/gate_live_check.py --arm-script <脚本> --net <受害网> --aggr <抢路网> --pad <ref>.<num>
      ★指定要查的那一对 (★默认: 扫全部同排邻脚对·列出【哪些对会触发】★)★
"""
import os
import re
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
BOARD = PROJ + "/HW/PCB/demo_mainboard.kicad_pcb"


def env_from_arm_script(path):
    """★从臂脚本里抠出 PCB_* 环境 (★用臂的 env·不用当前 shell★)"""
    env = {}
    try:
        s = open(path, encoding="utf-8").read()
    except OSError:
        return env
    # ★形如 `PCB_XXX=值 \` 的连续块
    for m in re.finditer(r"(PCB_[A-Z0-9_]+)=([^\s\\]+)", s):
        env[m.group(1)] = m.group(2)
    # ★`run_arm "$OUT1" "$LOG1" "PCB_YIELD_STRAIGHT=1 PCB_YIELD_VICTIMS=BOOT_N"` 这种
    for m in re.finditer(r'"(PCB_[A-Z0-9_]+=[^"]*)"', s):
        for kv in m.group(1).split():
            if "=" in kv:
                k, v = kv.split("=", 1)
                env[k] = v
    return env


def main():
    argv = sys.argv[1:]
    if "--arm-script" not in argv:
        print(__doc__)
        return 2
    arm = argv[argv.index("--arm-script") + 1]
    env = env_from_arm_script(arm)
    # ★把抠出来的 env 应用到【本进程】⇒ 让路由器读到 ★
    for k, v in env.items():
        os.environ[k] = v
    print("═══ 闸的真路由器体检 ═══")
    print("  臂脚本 : %s" % os.path.basename(arm))
    print("  ★抠到的 env (★%d 个★):" % len(env))
    for k in sorted(env):
        if k.startswith("PCB_YIELD") or k in ("PCB_W_MIN", "PCB_HALO_MARGIN", "PCB_GRID"):
            print("     %s = %s" % (k, env[k]))
    if "PCB_YIELD_STRAIGHT" not in env or env.get("PCB_YIELD_STRAIGHT") != "1":
        print("\n  ★★**⇒ 该臂【没开让路闸】⇒ ⇒ 无需体检 (★闸关臂·本来就是对照★)** ★★")
        return 0

    sys.path.insert(0, PROJ + "/state")
    import gen_pcb_routing as R
    import pcbnew

    print("\n  ★**闸的 env**: YIELD_STRAIGHT=%s · YIELD_VICTIMS=%s" % (R.YIELD_STRAIGHT, R.YIELD_VICTIMS))
    print("  ★**`_need`** = CLEAR + W_CLS[1]/2 + W_CLS[1]/2 + HALO_MARGIN = **%.4f** (★W_CLS[1]=%.3f · HALO_MARGIN=%.4f★)"
          % (R.CLEAR + R.W_CLS[1] / 2.0 + R.W_CLS[1] / 2.0 + R.HALO_MARGIN, R.W_CLS[1], R.HALO_MARGIN))

    b = pcbnew.LoadBoard(BOARD)
    r = R.GridRouter(b)

    # ★★**★2026-11-11 04:2x 【★加"谁掐谁"全表 (★扩名单用·不用再手写脚本★)】★★★★ ★★
    #   ★**输出每个受害网被【哪些抢路者】掐 + 【需要直行几步】⇒ ⇒ 扩名单时直接照着挑** ★★
    need = R.CLEAR + R.W_CLS[1] / 2.0 + R.W_CLS[1] / 2.0 + R.HALO_MARGIN
    who = {}
    for _net, _pads in r.net_pads.items():
        for _pad in _pads:
            _ref, _num, _cx, _cy, _l = _pad
            try:
                _st = r.escape_stub(_net, (_ref, _num, _cx, _cy, (0,)))
            except Exception:
                _st = None
            if not _st:
                continue
            _dy = _st[1] - _cy
            _dj = 1 if _dy > 1e-9 else (-1 if _dy < -1e-9 else 0)
            if _dj == 0:
                continue
            for _vnet, _vpads in r.net_pads.items():
                if _vnet == _net:
                    continue
                for (_vref, _vnum, _vx, _vy, _vl) in _vpads:
                    if abs(_vy - _cy) > 0.2:
                        continue
                    _dx = _vx - _cx
                    if not (0.3 <= abs(_dx) <= 1.05):
                        continue
                    _gx = r._cx(r._ci(_vx))
                    _gy = r._cy(r._cj(_vy + _dj * R.ESC_LEN))
                    _k = 12
                    for _kk in range(0, 13):
                        _ty = _cy + _dj * (R.ESC_LEN + _kk * r.g)
                        _sg = [(_cx, _cy, _cx, _cy + _dj * R.ESC_LEN),
                               (_cx, _cy + _dj * R.ESC_LEN, _cx, _ty)]
                        _c2, _c3, _sgn = _cx, _ty, (1 if _dx > 0 else -1)
                        for _ in range(40):
                            _nx = _c2 + _sgn * 0.25
                            if _sgn * (_nx - _gx) > 0:
                                break
                            _ny = _c3 + _dj * 0.25
                            _sg.append((_c2, _c3, _nx, _c3))
                            _sg.append((_nx, _c3, _nx, _ny))
                            _c2, _c3 = _nx, _ny
                        _sg.append((_c2, _c3, _gx, _c3))
                        _d = min(R._pt_seg_dist(_gx, _gy, _a, _b, _c, _e) for (_a, _b, _c, _e) in _sg)
                        if _d >= need - 1e-9:
                            _k = _kk
                            break
                    if _k > 0:
                        who.setdefault(_vnet, []).append((_net, _k))
    print("\n  ★★**【谁掐谁】全表 (★k = 需要直行几步·★k=12 = 上限⇒ 让路解不了⇒ 是差分配对问题★)** ★★")
    for _v in sorted(who, key=lambda z: -len(who[z])):
        print("    ★受害网 %-18s ← %s" % (_v, ", ".join("%s(k=%d)" % (a, c) for (a, c) in who[_v][:5])))

    fired = []
    total = 0
    for net, pads in r.net_pads.items():
        for pad in pads:
            ref, num, cx, cy, _l = pad
            try:
                st = r.escape_stub(net, (ref, num, cx, cy, (0,)))
            except Exception:
                st = None
            if not st:
                continue
            dx = st[0] - cx
            dy = st[1] - cy
            di = 1 if dx > 1e-9 else (-1 if dx < -1e-9 else 0)
            dj = 1 if dy > 1e-9 else (-1 if dy < -1e-9 else 0)
            if dj == 0:
                continue                     # ★只处理垂直出脚 ★
            total += 1
            try:
                steps = r._yield_straight_steps(net, (ref, num, cx, cy, (0,)), di, dj)
            except Exception as e:
                steps = -1
                print("    ⚠️ %s.%s 抛异常: %s" % (ref, num, e))
            if steps:
                fired.append((net, ref, num, cx, cy, steps))

    print("\n  ★**扫了 %d 个垂直出脚的焊盘, 其中 %d 个会被闸约束**" % (total, len(fired)))
    for (net, ref, num, cx, cy, steps) in fired:
        print("    ★ %-16s %s.%-3s @ (%.2f,%.2f) ⇒ 【先直行 %d 步】" % (net, ref, num, cx, cy, steps))

    if not fired:
        print("\n  ❌❌ **★闸【不会生效】(★没有任何一对会触发★) ⇒ ⇒ 两臂会等价 ⇒ ⇒ 不许开臂!** ★★")
        print("  ★**排查顺序**: ① env 抠对了吗 ② `_need` 用的是臂上的 W_CLS/HALO_MARGIN 吗")
        print("     ③ 受害网在 `PCB_YIELD_VICTIMS` 名单里吗 ④ 模型算出来的距离真的 < `_need` 吗")
        return 1
    print("\n  ✔ **闸在真路由器上【确实生效】(★%d 处会约束★) ⇒ ⇒ 可以开臂**" % len(fired))
    return 0


if __name__ == "__main__":
    sys.exit(main())
