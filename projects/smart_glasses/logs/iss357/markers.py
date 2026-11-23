import yaml,re,json
d=yaml.safe_load(open('state/fragments/sw.yaml'))
nf=d['needs_from']
pats=['已结','已闭合','已消化','已闭环','已关闭','已退休','已取代','已被','不再重复','留档','作废','已答','已落地','已交付','已批准','已签','已落 verified','零重复']
out=[]
for i,n in enumerate(nf):
    it=n.get('item') or ''
    hit=[p for p in pats if p in it]
    # position of first marker
    pos=min([it.find(p) for p in hit]) if hit else 9999
    out.append((i,n.get('key'),n.get('to'),n.get('waiting_on'),hit,pos,len(it)))
print('idx  key | to | wo | markers | firstpos/len')
for r in out:
    if r[4]:
        print(f"{r[0]:3d} {r[1]:45s} {r[2]:10s} {str(r[3]):8s} {r[4]} @{r[5]}/{r[6]}")
