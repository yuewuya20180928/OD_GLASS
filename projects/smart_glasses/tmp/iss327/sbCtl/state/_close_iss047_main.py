#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""close_iss047.py —— ISS-047 验收收口 + 新开 ISS-143 (边框遮挡口径)"""
import yaml

P = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/issue_log.yaml'
d = yaml.safe_load(open(P, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

NOTE_ADD = (
    " ★**2026-11-02 18:4x main 验收通过** (自证脚本 rc=0 / FAIL 0 / WARN 0; 文档一致性 220/220; "
    "关键数与 SW fov_scale_check.py 三方一致: 垂直半 31.80° / 水平半 50.88° / f=3.2432mm)。"
    " ★**并裁决其提出的未决口径**: 取 **判据 B' (有效余量 ≥4°, 即扣掉边框遮挡角) ⇒ 俯角上限 ≤25.89°, 设计点 25°** "
    "—— 理由: 遮挡是实物必然 (凹进 0 也要占窗口座沉孔 0.35mm), 名义余量留不住; 且与 LENS_SELECTION §B6.3「推荐按 ≤25° 设计」一致。"
    " ★**作废**: 旧「俯角 20-32° 不可回避」(32° 名义 −0.20° 掉出画面; 30° 扣遮挡后 −0.11° 正前方被上沿遮掉)。"
    " ★**新硬上限**: 零余量位 29.89° ⇒ h_max(d=35)=20.12mm > 旧 MECH 上界 20mm ⇒ 零余量做不到。"
    " ★**h_max(d=30/32/35) = 13.99/14.92/16.32mm**。"
)

i = by['ISS-047']
i['status'] = 'verified'
i['verify_by'] = 'main'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('MECH/ISS047_FOV_TABLE.md · MECH/iss047_fov_table.py (rc=0, FAIL0/WARN0) · '
                'MECH/iss047_doc_check.py (220/220) · MECH/CAMERA_WINDOW_SPEC.md §B5 · '
                'MECH/MECH_BUDGET.md §1.5/§1.5.1/§1.5.2/§4(c) · '
                'HANDOFF/2026-11-02_mech-lead_ISS047_FOV俯角表复核.md')
i['note'] = (i.get('note') or '') + NOTE_ADD

if not any(x['id'] == 'ISS-143' for x in iss):
    iss.append({
        'id': 'ISS-143',
        'title': '★★结构侧新口径: 边框遮挡角必须进 FOV 余量账 (凹进 1.0mm = 1.91° 遮挡, 吃掉"正前方那一侧") ⇒ 镜框上沿沉孔/凹进量要重定',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 ISS-047 验收时发现 (mech-lead 交卷, main 验收): **边框遮挡吃的是「正前方那一侧」** —— '
            '摄像头装镜框上沿、光轴朝下俯, 正前方对应画面**上半部**, 而镜框上沿正好挡住上半部 ⇒ '
            '★**前顶点凹进量直接吃掉「正前方在画面内」的余量** (凹进 1.0mm = 1.91°)。'
            '⇒ ★**旧口径只算名义余量, 没算遮挡** ⇒ 俯角 30° 名义 +1.80° 看着 OK, 扣掉遮挡后 −0.11° ⇒ 正前方其实被镜框上沿遮掉了。'
            '⇒ ★**要做的**: ①把「有效余量 = 名义余量 − 遮挡角」写进结构侧镜框上沿的设计判据 (ISS-047 已落进 MECH); '
            '②★**镜框上沿的沉孔/凹进量要重定**: 改成有效余量口径后, 凹进量与 h_max 要一起重算 '
            '(h_max(d=35) = 16.32mm; 判据B\' 余量口径 16.99mm; 零余量位 20.12mm > 旧上界 20mm); '
            '③★**这条会改结构件尺寸 ⇒ 要在开模前定** (ISS-047 结论: 三档预留只差 ≤0.9mm, 可先按预留值开孔, 但凹进量要留出调整余量)。'),
        'owner': 'mech-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-09',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'MECH/ISS047_FOV_TABLE.md §B1.5 · MECH/CAMERA_WINDOW_SPEC.md §B5',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 18:4x。★**这是 ISS-047 验收时顺手挖出来的真缺陷, 单独立项** —— 不立项它就会丢在交接单里没人管。'
                 '★**与 ISS-052 (结构开模) 的关系**: 结构侧说「三档预留只差 ≤0.9mm, 可先按预留值开孔」⇒ '
                 '★**本单只要在开模前给出凹进量的调整余量口径, 不阻塞开孔** ⇒ 优先级中。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(P, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('ok, issues =', len(iss))
