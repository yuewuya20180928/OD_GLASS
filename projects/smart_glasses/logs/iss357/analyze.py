import yaml, json
from collections import Counter, defaultdict
FILE_OF={'main':'pm.yaml','hw-lead':'hw.yaml','sw-lead':'sw.yaml','mech-lead':'mech.yaml'}
frs={a:yaml.safe_load(open('state/fragments/'+f)) for a,f in FILE_OF.items()}
ga=defaultdict(set); gn=defaultdict(dict); author=defaultdict(set)
for aid,d in frs.items():
    for a in (d.get('answers') or []):
        if a.get('key') and a.get('to'):
            ga[a['to']].add(a['key']); author[a['key']].add(aid)
    for n in (d.get('needs_from') or []):
        if n.get('key'): gn[n['key']][aid]=n.get('to')
sw=frs['sw-lead']['needs_from']
print('sw needs_total',len(sw))
cat=Counter(); rows=[]
for i,n in enumerate(sw):
    k=n.get('key'); t=n.get('to'); wo=n.get('waiting_on')
    ext = (wo or 'agent')!='agent'
    merge_answered = t in frs and k in author and t in author[k]
    gate_ans = k in ga['sw-lead']
    state = 'pending' if not ext else ('waiting_external' if not merge_answered else 'answered')
    rows.append(dict(i=i,key=k,to=t,wo=wo,since=n.get('since'),due=n.get('due'),
                     merge_answered=merge_answered, gate_ans=gate_ans, state=state))
    cat[(t,wo or '-',state)]+=1
for k,v in sorted(cat.items(), key=lambda x:(str(x[0][0]),str(x[0][1]))):
    print(k,v)
print()
print('answered_incoming(gate) =',sum(1 for r in rows if r['gate_ans']))
print('merge_answered =',sum(1 for r in rows if r['merge_answered']))
print('pending (real_open contributors) =',sum(1 for r in rows if r['state']=='pending'))
json.dump(rows,open('logs/iss357/_needs_dump.json','w'),ensure_ascii=False,indent=1)
# main's answers for the 3 merge-closed but not gate-answered
for kk in ('iss285_sw_apply_after_iss283_verified','iss288_sw_timing_check_patch_landed','iss288_main_verify_sign_issue_log'):
    for a in (frs['main'].get('answers') or []):
        if a.get('key')==kk: print('MAIN ANSWER',kk,'to=',a.get('to'))
