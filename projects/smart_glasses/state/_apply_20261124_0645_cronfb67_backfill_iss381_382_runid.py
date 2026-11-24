#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回填 ISS-381 / ISS-382 的 session_key / run_id / task_name / dispatched_at 到 dispatch_log
(★零改 issue_log · 零写板 · 只追加 dispatch_log 的两个字段★)"""
import hashlib, os, shutil, sys, time
import yaml
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DLOG=os.path.join(PROJ,"state","dispatch_log.yaml")
STAMP=time.strftime("%Y%m%d_%H%M")
FILLS={
 "ISS-381":{"session_key":"agent:sw-lead:subagent:b55663b5-2cc8-4f58-9e22-00e692911b66",
             "run_id":"1ec626ac-0275-4d52-a8b3-6b7dcf8f28dd","task_name":"queue_iss381",
             "dispatched_at":"2026-11-24 06:44"},
 "ISS-382":{"session_key":"agent:mech-lead:subagent:0fa8bb52-63c9-44f2-ae07-472831cac2f0",
             "run_id":"4f921e70-6d66-4b1a-b08a-a9f1bb7522fa","task_name":"queue_iss382",
             "dispatched_at":"2026-11-24 06:44"},
}
def md5(p):
    h=hashlib.md5()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def main():
    raw=open(DLOG,encoding='utf-8').read(); m0=md5(DLOG)
    d=yaml.safe_load(raw); assert isinstance(d,list)
    n=0
    for e in d:
        if e.get("issue") in FILLS:
            for k,v in FILLS[e["issue"]].items(): e.setdefault(k,v)
            n+=1
    assert n==2, "只找到 %d 条" % n
    bak=DLOG+".bak_%s_cronfb67_runid"%STAMP; shutil.copy2(DLOG,bak)
    tmp=DLOG+".tmp_%d"%os.getpid()
    with open(tmp,'w',encoding='utf-8') as f:
        yaml.safe_dump(d,f,allow_unicode=True,sort_keys=False,default_flow_style=False,width=100000)
        f.flush(); os.fsync(f.fileno())
    if md5(DLOG)!=m0:
        os.unlink(tmp); print("★★中止 (rc=3): dispatch_log 被并发改过"); return 3
    os.replace(tmp,DLOG)
    d2=yaml.safe_load(open(DLOG,encoding='utf-8').read())
    for e in d2:
        if e.get("issue") in FILLS:
            print("★",e["issue"],"← session_key=",e.get("session_key"),"run_id=",e.get("run_id"))
    print("★ dispatch_log 条数 %d · 备份 %s · 新 md5=%s"%(len(d2),os.path.basename(bak),md5(DLOG)))
    return 0
if __name__=="__main__": sys.exit(main())
