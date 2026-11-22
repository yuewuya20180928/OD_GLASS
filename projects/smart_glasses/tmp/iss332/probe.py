import importlib.util, json, os, sys, collections

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
V2 = os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability_v2.py")


def load():
    spec = importlib.util.spec_from_file_location("v2", V2)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


g = load()
res = g.analyze(PROJ)
print("TOKENS_N =", res["tokens_n"], "missing_total =", res["missing_total"],
      "baseline_count =", res["baseline_count"], "baseline_ok =", res["baseline_ok"])
by = collections.Counter(r["cls"] for r in res["rows"])
print("CLASS COUNTS:", dict(by))
byrule = collections.Counter(r["rule"] for r in res["rows"])
print("RULE COUNTS:", dict(sorted(byrule.items())))

print("\n=== per-rule token lists ===")
for rule in sorted(byrule):
    toks = [r["token"] for r in res["rows"] if r["rule"] == rule]
    print("%-4s (%2d): %s" % (rule, len(toks), " ".join(sorted(toks))))

print("\n=== registry coverage ===")
live_ok = [r["token"] for r in res["rows"] if r["cls"] == "DESIGNATOR_OK"]
reg = set(g.DESIGNATOR_REGISTRY)
not_in_reg = sorted(t for t in live_ok if t not in reg)
print("DESIGNATOR_OK n=%d ; not in registry: %d -> %s" % (len(live_ok), len(not_in_reg), not_in_reg))
print("registry size =", len(reg))
print("live_refs n =", len(res["live_refs"]), " board_refs_n =", res["board_refs_n"],
      " netlist_refs_n =", res["netlist_refs_n"])
print("U_TEMP in registry:", "U_TEMP" in reg, " U_TEMP in live:", "U_TEMP" in res["live_refs"])
print("U_TEMP_1 in registry:", "U_TEMP_1" in reg, " U_TEMP_1 in live:", "U_TEMP_1" in res["live_refs"])

print("\n=== MISSING rows ===")
for r in res["rows"]:
    if r["cls"] == "DESIGNATOR_MISSING":
        print(" ", r["token"], r["rule"], "in_baseline=", r["token"] in g.BASELINE_TOKENS)

print("\n=== env_keys / anchors / doc_files sizes ===")
occ, ndocs = g.collect_doc_tokens(PROJ)
print("docs scanned:", ndocs, "tokens:", len(occ))
df, an, ek = g.build_aux_index(PROJ)
print("doc_files:", len(df), "anchors:", len(an), "env_keys:", len(ek), sorted(ek)[:20])

print("\n=== shape-rule-hit tokens (C7,C8,C9,C10,C11,C12,C13) ===")
shape = [r for r in res["rows"] if r["rule"] in ("C7", "C8", "C9", "C10", "C11", "C12", "C13")]
for r in sorted(shape, key=lambda x: x["rule"]):
    print("  %-4s %-28s %s" % (r["rule"], r["token"], r["note"][:70]))

json.dump({"rows": [{"t": r["token"], "c": r["cls"], "r": r["rule"]} for r in res["rows"]]},
          open(os.path.join(PROJ, "tmp", "iss332", "real_class.json"), "w"), indent=0)
