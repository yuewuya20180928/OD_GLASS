# -*- coding: utf-8 -*-
"""ISS-363 只读探针 (★不写任何真件★)"""
import csv, hashlib, json, os, re, sys, time
PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "SW", "tools"))
import check_demo_panel_spec as dps

FP = "foot" + "print"
TRUTH = [("网表", "HW/netlist_v1.csv"), ("脚表", "HW/netlist_v1_pins.csv"), ("BOM", "HW/BOM_v1.csv")]

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

print("=== [1] 三份真源封装栏 (按表头名定位) ===")
for name, rel in TRUTH:
    with open(os.path.join(PROJ, rel), encoding="utf-8", errors="replace") as f:
        rd = csv.DictReader(f)
        hdr = rd.fieldnames
        idx = hdr.index(FP) if FP in hdr else -1
        rows = list(rd)
    nonempty = sum(1 for r in rows if (r.get(FP) or "").strip())
    empty = len(rows) - nonempty
    print("  %s %-24s 列号=%d (1基=%d) 数据行=%d 非空=%d 空=%d md5=%s"
          % (name, rel, idx, idx + 1, len(rows), nonempty, empty, md5(os.path.join(PROJ, rel))))

print("=== [2] 落表台账链头 (sw_ledger_state) ===")
led = open(dps.LEDGER_CANON, encoding="utf-8", errors="replace").read()
for name, rel in TRUTH:
    st = dps.sw_ledger_state(rel, led)
    print("  %s head=%s iss=%s chain_len=%s why=%s" % (name, st.get("head"), st.get("head_iss"),
          len(st.get("chain") or []), st.get("why")))

print("=== [3] 清单 JSON 块: 条数 / 讲 fp 栏 / 泛提封装 ===")
sync = open(os.path.join(PROJ, "SW", "BOARD_ONEPASS_SW_SYNC.md"), encoding="utf-8", errors="replace").read()
m = re.search(r"```json\s*(\{.*?\})\s*```", sync, re.S)
items = json.loads(m.group(1)).get("items", [])
TOPIC = re.compile(re.escape(FP) + "|封装真值|库封装名|封装栏", re.I)
GEN = re.compile(re.escape(FP) + "|封装", re.I)
cover = [it.get("id") for it in items if TOPIC.search(" ".join(str(it.get(k, "")) for k in ("current_state", "action")))]
gen = [it.get("id") for it in items if GEN.search(" ".join(str(it.get(k, "")) for k in ("current_state", "action")))]
print("  items=%d cover=%d %s generic=%d %s" % (len(items), len(cover), cover, len(gen), gen))
print("  ids=%s" % [it.get("id") for it in items])

print("=== [4] ISS-362 页 H4-REG 登记值 ===")
imp = open(os.path.join(PROJ, "SW", "BOARD_ONEPASS_FP_TRUTH_IMPACT.md"), encoding="utf-8", errors="replace").read()
for k in ("H4-ITEMS", "H4-COVER", "H4-GENERIC"):
    mm = re.search(r"^-\s*%s\s*[:：]\s*(.*)$" % k, imp, re.M)
    print("  %s = %r" % (k, mm.group(1).strip() if mm else None))

print("=== [5] sw.yaml 分片: to=sw-lead 的 need (open/closed) ===")
import yaml
frag = yaml.safe_load(open(os.path.join(PROJ, "state", "fragments", "sw.yaml"), encoding="utf-8"))
needs = frag.get("needs_from") or []
ans_keys = {a.get("key") for a in (frag.get("answers") or [])}
HEX32 = re.compile(r"\b[0-9a-f]{32}\b")
chain_heads = set()
for name, rel in TRUTH:
    st = dps.sw_ledger_state(rel, led)
    if st.get("head"):
        chain_heads.add(st["head"])
print("  chain_heads=%s" % sorted(chain_heads))
openn = []
for n in needs:
    if n.get("to") != "sw-lead":
        continue
    closed = n.get("key") in ans_keys
    item = n.get("item") or ""
    mds = sorted(set(HEX32.findall(item)))
    if not closed:
        openn.append((n.get("key"), mds, n.get("since")))
print("  to=sw-lead 总数=%d · 仍open=%d" % (sum(1 for n in needs if n.get("to") == "sw-lead"), len(openn)))
bad = 0
for k, mds, since in openn:
    print("    open need %-46s since=%s md5=%s" % (k, since, mds))
    for x in mds:
        if x[:12] not in {c[:12] for c in chain_heads}:
            print("      ★≠链头: %s" % x)
            bad += 1
print("  ★仍 open 且引着的 md5 ≠ 链头 的条数 = %d" % bad)
print("  answers 条数=%d (闭合判定用)" % len(ans_keys))
