#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-338 · 正确的 KiCad s-expression 解析 (只读) ⇒ 每网 pads/segments/vias"""
import re, sys
P="HW/PCB/demo_mainboard.kicad_pcb"
src=open(P,encoding="utf-8",errors="replace").read()
# tokenizer
def tokenize(s):
    i=0; n=len(s); out=[]
    while i<n:
        c=s[i]
        if c=='(' or c==')':
            out.append(c); i+=1
        elif c=='"':
            j=i+1; buf=[]
            while j<n:
                if s[j]=='\\':
                    buf.append(s[j:j+2]); j+=2; continue
                if s[j]=='"': break
                buf.append(s[j]); j+=1
            out.append(('str',''.join(buf))); i=j+1
        elif c.isspace():
            i+=1
        else:
            j=i
            while j<n and not s[j].isspace() and s[j] not in '()': j+=1
            out.append(('sym',s[i:j])); i=j
    return out
def parse(toks):
    stack=[[]]
    for t in toks:
        if t=='(':
            new=[]; stack[-1].append(new); stack.append(new)
        elif t==')':
            stack.pop()
        else:
            stack[-1].append(t)
    return stack[0]
root=parse(tokenize(src))
# root = [ [ 'kicad_pcb', <children...> ] ]
KICAD = root[0] if root and isinstance(root[0], list) else root
print("top node:", KICAD[0][1] if isinstance(KICAD[0],tuple) else KICAD[0])
def name(node):
    if node and isinstance(node[0],tuple) and node[0][0]=='sym': return node[0][1]
    return None
nets={}   # netname -> dict(pads, segs, vias)
def touch(n):
    nets.setdefault(n, {'pads':0,'segs':0,'vias':0,'padlist':[]})
    return nets[n]
for top in KICAD[1:]:
    if not isinstance(top,list): continue
    nm=name(top)
    if nm=='net':
        # (net N "NAME")
        for x in top[1:]:
            if isinstance(x,tuple) and x[0]=='str':
                touch(x[1]); break
    elif nm=='footprint':
        ref=None
        for p in top[1:]:
            if isinstance(p,list) and name(p)=='property':
                vals=[q for q in p if isinstance(q,tuple)]
                if len(vals)>=2 and vals[0][1]=='Reference': ref=vals[1][1]
            if isinstance(p,list) and name(p)=='fp_text':
                vals=[q for q in p if isinstance(q,tuple)]
                if len(vals)>=2 and vals[0][1]=='reference': ref=vals[1][1]
            if isinstance(p,list) and name(p)=='pad':
                nn=None
                for q in p[1:]:
                    if isinstance(q,list) and name(q)=='net':
                        for s2 in q[1:]:
                            if isinstance(s2,tuple) and s2[0]=='str': nn=s2[1]; break
                if nn:
                    d=touch(nn); d['pads']+=1
                    pnum = p[1][1] if len(p)>1 and isinstance(p[1],tuple) else '?'
                    d['padlist'].append(f"{ref}.{pnum}")
                else:
                    d=touch(nn) if nn in nets else None
    elif nm=='segment':
        nn=None
        for q in top[1:]:
            if isinstance(q,list) and name(q)=='net':
                for s2 in q[1:]:
                    if isinstance(s2,tuple) and s2[0]=='str': nn=s2[1]; break
        if nn: touch(nn)['segs']+=1
    elif nm=='via':
        nn=None
        for q in top[1:]:
            if isinstance(q,list) and name(q)=='net':
                for s2 in q[1:]:
                    if isinstance(s2,tuple) and s2[0]=='str': nn=s2[1]; break
        if nn: touch(nn)['vias']+=1
print(f"total nets parsed = {len(nets)}")
print(f"{'net':<18}{'pads':>6}{'segs':>7}{'vias':>6}   pads")
ORDER=["LED_B","LED_B_D","LED_R","LED_R_D","LED_G","LED_G_D","USB_CC1","USB_CC2","J_USB_C","CAM_RESET_N","FSIN_OUT","JTAG_TDI","LED_G_D","SPI_MISO_BOOT","SPI_MOSI_BOOT","SPI_SCLK_BOOT","UART_RX","USB_CC2",
       "LED_G","FSIN","SPI_MISO","SPI_MOSI","SPI_SCLK","SPI_CSn","JTAG_TDI_SOC","JTAG_TCK_SOC","JTAG_TMS_SOC","JTAG_TDO_SOC",
       "JTAG_TCK","JTAG_TMS","JTAG_TDO","UART_TX","USB_CC1","RESET_N","GND"]
for n in ORDER:
    d=nets.get(n)
    if not d: print(f"{n:<18}{'MISSING':>6}"); continue
    print(f"{n:<18}{d['pads']:>6}{d['segs']:>7}{d['vias']:>6}   {','.join(d['padlist'])}")
tot_seg=sum(d['segs'] for d in nets.values()); tot_via=sum(d['vias'] for d in nets.values()); tot_pad=sum(d['pads'] for d in nets.values())
print(f"\nTOTAL pads={tot_pad} segments={tot_seg} vias={tot_via}  (ISS-334 口径: 834 焊盘 / 18092 段 / 433 孔)")
zc=sorted([n for n,d in nets.items() if d['pads']>=2 and d['segs']==0])
print(f"\n零铜网 (pad>=2 & seg=0) = {len(zc)}:")
for n in zc: print("  ",n, nets[n]['pads'], "pads")
