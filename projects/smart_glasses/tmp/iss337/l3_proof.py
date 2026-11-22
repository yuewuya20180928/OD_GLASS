#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★L3 决定性实验: 用【真生成器的真函数】_merge_collinear (只读 import, 不改真件) ★
   把官方板的 18092 段碎片按【官方路径顺序】还原成 path, 再分别喂 merge_fix=False / True
   ⇒ 看段数塌成多少 ⇒ 直接证明「段数差 = 共线合并粒度差」"""
import sys, re, math, collections, importlib.util, os

# --- 只读 import 真生成器的 _merge_collinear (不写真件) ---
spec = importlib.util.spec_from_file_location("realRT", os.path.join(os.getcwd(),"state/gen_pcb_routing.py"))
# gen_pcb_routing 需要 pcbnew ⇒ 用 KiCad 的 python
print("NOTE: 需 pcbnew ⇒ 走 pcbnew_py.sh", file=sys.stderr)

def segs_of(p):
    out=[];cur={};x1=y1=x2=y2=w=None;layer=None;net=None
    for ln in open(p,encoding="utf-8",errors="ignore"):
        s=ln.strip()
        if s=="(segment":cur={"k":"seg"};x1=y1=x2=y2=w=layer=net=None
        elif s.startswith("(start "):
            m=re.match(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)',s);x1,y1=float(m.group(1)),float(m.group(2))
        elif s.startswith("(end "):
            m=re.match(r'\(end\s+([-\d.]+)\s+([-\d.]+)\)',s);x2,y2=float(m.group(1)),float(m.group(2))
        elif s.startswith("(width "):w=float(re.match(r'\(width\s+([-\d.]+)\)',s).group(1))
        elif s.startswith("(layer "):layer=s.split('"')[1] if '"' in s else None
        elif s.startswith("(net "):
            m=re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"',s);net=m.group(1) if m else None
        elif s==")":
            if cur.get("k")=="seg" and None not in (x1,y1,x2,y2):out.append((x1,y1,x2,y2,w or 0.25,layer,net))
            cur={}
    return out

def build_paths(segs):
    """把碎片还原成路径链: 同(net,layer,width) 内按端点连通走链 (端点度1 = 链端)"""
    by=collections.defaultdict(list)
    for i,(x1,y1,x2,y2,w,l,n) in enumerate(segs):
        by[(l,n,round(w,4))].append(i)
    paths=[]; used=set()
    for key,idxs in by.items():
        adj=collections.defaultdict(list)
        for i in idxs:
            x1,y1,x2,y2,w,l,n=segs[i]
            adj[(round(x1,4),round(y1,4))].append(i)
            adj[(round(x2,4),round(y2,4))].append(i)
        for i in idxs:
            if i in used: continue
            # 从端点开始 (度1)
            chain=[i]; used.add(i)
            # 前向
            for direction in (0,1):
                cur=chain[-1]
                while True:
                    x1,y1,x2,y2,w,l,n=segs[cur]
                    p1=(round(x1,4),round(y1,4)); p2=(round(x2,4),round(y2,4))
                    head = p2 if direction==0 else p1
                    cands=[j for j in adj[head] if j not in used]
                    if not cands: break
                    nxt=cands[0]; used.add(nxt); chain.append(nxt); cur=nxt
            paths.append([segs[i] for i in chain])
    return paths

if __name__=="__main__":
    board=sys.argv[1]
    segs=segs_of(board)
    paths=build_paths(segs)
    print("board=%s raw_segs=%d reconstructed_paths=%d" % (board,len(segs),len(paths)))
    import pickle
    with open(sys.argv[2],"wb") as f:
        pickle.dump({"board":board,"raw":len(segs),"paths":paths}, f)
    print("pickled -> %s" % sys.argv[2])
