import json, re, csv, os
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
# 1) SPEC.json devices
spec=json.load(open(os.path.join(PROJ,"HW","SCHEMATIC_V1_SPEC.json"),encoding="utf-8"))
devs=spec.get("devices") or []
refs=[d.get("ref") for d in devs]
print("SPEC.json devices 条数 =", len(devs))
print("  非空 ref 数 =", len([r for r in refs if r]))
print("  唯一 ref 数 =", len(set(refs)))
enddigit=[r for r in refs if r and r[-1].isdigit()]
print("  末字符是数字的 ref 数 =", len(enddigit))
print("  其中带 _1 后缀(精确) =", len([r for r in enddigit if r.endswith("_1")]))
print("  带 _1 后缀(任意) =", len([r for r in refs if r and "_1" in r]))
print("  样例(末字符数字) 前 40 =", enddigit[:40])
# board assignment per ref
board=collections={}
