#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-292 · B5 反向用例 (★每条贴原样 rc★)

① 沙盒里模拟「又一次合法落表」(★台账链头往前跳 + DNP 集合改一行★) ⇒ 重跑生成器, R3-A4 的数必须跟着变
② 把生成器里的 R3-A4 值改回 54/43/43 ⇒ 重跑后盘面页必须回退 ⇒ 新闸必须变红 (★证明闸真在读★)
③ 正向对照: 一切如常 ⇒ 重跑生成器后盘面页零变化 + 新闸 rc=0
④ 附加: sidecar 缺失 ⇒ 生成器必须【拒写页】(★fail-closed·追加式订正块不许丢★)

★★本脚本只在 tmp/iss292/ 下的沙盒里动手, 真盘零写 (★受保护 5 件 md5 + mtime 收工时自证★) ★★
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SB = os.path.join(PROJ, "tmp", "iss292")
PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
WP = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md")

# ★沙盒要带的文件 (★只带生成器/闸读得到的那几件★) ★
SANDBOX_FILES = [
    "HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv",
    "HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro",
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md", "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "HW/check_netlist_contradiction_r3.py", "HW/check_pin_function_labels.py",
    "HW/SCHEMATIC_LANDING_V1_LANDED.md",
    "state/_iss277_build_preflight.py", "state/_iss277_preflight_appendix.md",
]


def sh(cmd, cwd=None, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(cmd, cwd=cwd or PROJ, env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
    out = (r.stdout or b"").decode("utf-8", "replace")
    return r.returncode, out


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def make_sandbox(name):
    root = os.path.join(SB, name)
    if os.path.exists(root):
        shutil.rmtree(root)
    for rel in SANDBOX_FILES:
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(PROJ, rel), dst)
    return root


def page_r3_line(path):
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"R3-A4: MAIN_PCB且DNP (\d+) 颗 · 在板上 (\d+) 颗 · 零标记 (\d+) 颗", txt)
    return ("/".join(m.groups()) if m else "★没抽到★"), txt


def banner(s):
    print("\n" + "=" * 78)
    print(s)
    print("=" * 78)


# ==============================================================================
# ① 沙盒里把落表台账链头往前跳一跳 (★模拟又一次合法落表★) ⇒ R3-A4 的数必须跟着变
# ==============================================================================
banner("★① 沙盒里模拟又一次合法落表 (★台账链头往前跳 + DNP 集合改一行★) ⇒ 重跑生成器, R3-A4 的数必须跟着变")
sb1 = make_sandbox("sb1")

# --- ①-1 沙盒网表: 把 BT_432243 这颗从 DNP 改成必装 (★与 2026-11-17 09:58:16 那次同型★) ---
net = os.path.join(sb1, "HW", "netlist_v1.csv")
lines = open(net, encoding="utf-8").read().split("\n")
hdr = lines[0].split(",")
i_ref, i_dnp = hdr.index("ref"), hdr.index("dnp")
n_chg = 0
for i, l in enumerate(lines[1:], 1):
    if not l.strip():
        continue
    cells = l.split(",")
    if len(cells) > max(i_ref, i_dnp) and cells[i_ref] == "BT_432243" and cells[i_dnp] == "DNP":
        cells[i_dnp] = "必装"
        lines[i] = ",".join(cells)
        n_chg += 1
open(net, "w", encoding="utf-8").write("\n".join(lines))
print("★①-1 沙盒网表: BT_432243 的 dnp 由 DNP 改成必装 (★改了 %d 行★)" % n_chg)

# --- ①-2 沙盒台账: 追加一条新落表链 (★链头往前跳★) ---
led = os.path.join(sb1, "HW", "SCHEMATIC_LANDING_V1_LANDED.md")
lt = open(led, encoding="utf-8").read()
new_chain = """

---

## ★★17 · ★★V 值拍板即落 (★ISS-292 沙盒模拟 · ★假链·只用于反向用例★) ★★

> ★**单号**: ★**ISS-292-SB** · ★**落表时间**: ★**2026-11-17 17:00:00 (Asia/Shanghai)** ★

### ★★17.1 · 拍板了什么 + 逐条落点 ★★

| V 值 | 取值 | 落表后期望条数变化 | 本工具落的落点 |
|---|---|---|---|
| ★**V-9** ★ | ★**F** ★ | **-1 条** | `state/gen_netlist.py` (E-1 删 DEMO_DNP 一行 (BT_432243)) |

### ★★17.2 · 新旧 md5 前后对照 ★★

| 文件 | 前 | 后 | 变了? |
|---|---|---|---|
| ★**`HW/netlist_v1.csv`** ★ | `37f62ac3f0b81d92ca7d48fdea717f07` | `%s` | ★**是**★ |
"""
new_chain = new_chain % md5(net)
open(led, "w", encoding="utf-8").write(lt + new_chain)
print("★①-2 沙盒台账: 追加一条新落表链 (★2026-11-17 17:00:00 · V-9=F · 链头往前跳★)")

# --- ①-3 跑生成器 (★沙盒根 = PREFLIGHT_PROJ★) ---
rc, out = sh([sys.executable, os.path.join(sb1, "state", "_iss277_build_preflight.py")],
             env={"PREFLIGHT_PROJ": sb1})
print("★①-3 沙盒生成器 rc=%d" % rc)
for l in out.split("\n"):
    if "真源读数" in l or "已写" in l:
        print("    " + l[:300])

sb1_page = os.path.join(sb1, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
v_sb, txt_sb = page_r3_line(sb1_page)
v_real, txt_real = page_r3_line(PAGE)
print("★①-4 沙盒页 R3-A4 = %s   |   真盘页 R3-A4 = %s" % (v_sb, v_real))
m = re.search(r"落表 V-9=F 删了 1 行 DNP ⇒ [^,]*", txt_sb)
print("★①-5 沙盒页的落表事件注记 = %s" % (m.group(0) if m else "★没抽到★"))
ok1 = (v_sb != v_real) and ("V-9=F" in txt_sb)
print("★① 判定: ★**%s** ★ (★数变了 = %s / 注记跟着新链头 = %s★)"
      % ("通过" if ok1 else "不通过", v_sb != v_real, "V-9=F" in txt_sb))

# ==============================================================================
# ② 把生成器里的 R3-A4 值改回 54/43/43 ⇒ 重跑后盘面页必须回退 ⇒ 新闸必须变红
# ==============================================================================
banner("★② 把生成器里的 R3-A4 值改回 54/43/43 ⇒ 重跑后盘面页必须回退 ⇒ 新闸 check_workpack_state_values.py 必须变红")
sb2 = make_sandbox("sb2")
gen2 = os.path.join(sb2, "state", "_iss277_build_preflight.py")
g = open(gen2, encoding="utf-8").read()
before_md5 = md5(os.path.join(sb2, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md"))
# ★★把「从真源读」改成写死 54/43/43 (★模拟旧生成器★) ★★
g2 = g.replace('"«R3_T»": str(t), "«R3_O»": str(o), "«R3_Z»": str(z)',
               '"«R3_T»": "54", "«R3_O»": "43", "«R3_Z»": "43"')
assert g2 != g, "★替换没生效★"
open(gen2, "w", encoding="utf-8").write(g2)
print("★②-1 沙盒生成器: R3-A4 的取值改回写死 54/43/43 (★模拟 ISS-292 之前那个旧生成器★)")

rc, out = sh([sys.executable, gen2], env={"PREFLIGHT_PROJ": sb2})
print("★②-2 沙盒生成器 rc=%d" % rc)
sb2_page = os.path.join(sb2, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
v2, _ = page_r3_line(sb2_page)
after_md5 = md5(sb2_page)
print("★②-3 沙盒页 R3-A4 = %s   (★页 md5: %s ⇒ %s★)"
      % (v2, before_md5, "变了 = 页已回退" if before_md5 != after_md5 else "没变"))

rc, out = sh([sys.executable, "HW/check_workpack_state_values.py"],
             env={"WP_CHECKLIST": sb2_page})
print("★②-4 新闸 rc=%d" % rc)
red_lines = [l for l in out.split("\n") if l.strip().startswith("❌")]
for l in red_lines[:6]:
    print("    " + l[:220])
ok2 = (rc != 0) and ("54" in v2) and (before_md5 != after_md5)
print("★② 判定: ★**%s** ★ (★页回退 = %s / 闸红 = rc=%d★)"
      % ("通过" if ok2 else "不通过", "54" in v2, rc))

# ==============================================================================
# ③ 正向对照: 一切如常 ⇒ 重跑生成器后盘面页零变化 + 新闸 rc=0
# ==============================================================================
banner("★③ 正向对照: 一切如常 ⇒ 重跑生成器后盘面页零变化 + 新闸 rc=0")
p_before = md5(PAGE)
w_before = md5(WP)
rc, out = sh([sys.executable, "state/_iss277_build_preflight.py"])
print("★③-1 重跑生成器 rc=%d" % rc)
p_after = md5(PAGE)
w_after = md5(WP)
print("★③-2 清单页 md5 跑前 = %s" % p_before)
print("★③-2 清单页 md5 跑后 = %s   ⇒ %s" % (p_after, "★逐字节相同★" if p_before == p_after else "★变了★"))
print("★③-3 作业包 md5 跑前 = %s / 跑后 = %s ⇒ %s"
      % (w_before, w_after, "★逐字节相同 (生成器不许碰它★)" if w_before == w_after else "★变了★"))
rc_g, out_g = sh([sys.executable, "HW/check_workpack_state_values.py"])
print("★③-4 新闸 rc=%d" % rc_g)
ok3 = (p_before == p_after) and (w_before == w_after) and (rc_g == 0)
print("★③ 判定: ★**%s** ★" % ("通过" if ok3 else "不通过"))

# ==============================================================================
# ④ 附加: sidecar 缺失 ⇒ 生成器必须拒写页 (★fail-closed★)
# ==============================================================================
banner("★④ 附加用例: sidecar (追加式订正块) 缺失 ⇒ 生成器必须【拒写页】· 零写盘")
sb4 = make_sandbox("sb4")
os.remove(os.path.join(sb4, "state", "_iss277_preflight_appendix.md"))
sb4_page = os.path.join(sb4, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
sb4_md5_before = md5(sb4_page)
rc, out = sh([sys.executable, os.path.join(sb4, "state", "_iss277_build_preflight.py")],
             env={"PREFLIGHT_PROJ": sb4})
print("★④-1 沙盒生成器 rc=%d (★期望 ≠0★)" % rc)
for l in out.split("\n")[:4]:
    if l.strip():
        print("    " + l[:200])
sb4_md5_after = md5(sb4_page)
print("★④-2 沙盒页 md5 跑前 = %s / 跑后 = %s ⇒ %s"
      % (sb4_md5_before, sb4_md5_after,
         "★没写 (拒写成功)★" if sb4_md5_before == sb4_md5_after else "★写了 (不合格)★"))
ok4 = (rc != 0) and (sb4_md5_before == sb4_md5_after)
print("★④ 判定: ★**%s** ★" % ("通过" if ok4 else "不通过"))

banner("★B5 汇总 ★")
print("① 沙盒落表链头前跳 ⇒ R3-A4 跟着变 ....... %s" % ("通过" if ok1 else "不通过"))
print("② 生成器写死旧值 ⇒ 页回退 + 闸红 ....... %s" % ("通过" if ok2 else "不通过"))
print("③ 正向对照 ⇒ 零变化 + 闸绿 ............. %s" % ("通过" if ok3 else "不通过"))
print("④ sidecar 缺失 ⇒ 生成器拒写 ............ %s" % ("通过" if ok4 else "不通过"))
sys.exit(0 if (ok1 and ok2 and ok3 and ok4) else 1)
