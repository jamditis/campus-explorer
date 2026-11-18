# qc: SW skirt bank edge west of Feliciano. The pz slope and the 3DEP skirt are within ~1-3 cm of each other near
# x -266 (probe data/qc/skprobe.log), so their crossing line is a hard tone edge (dark skirt green vs the lighter qb-faded grass).
# Strengthen the qb fade right at the crossing: the noise floor of the fade (Map Range To Min 0.72) is raised to QC_TOMIN and
# the tint is pulled toward the skirt's rendered tone (QC_TINT); the same applies only where qb_fade ~1, so the far slope is
# unchanged. Old values stored on the material; REVERT=1 restores them exactly. UNVERIFIED (tone only, no geometry).
import bpy, os
REV=os.environ.get('REVERT')=='1'
TM=float(os.environ.get('QC_TOMIN','0.95')); TT=tuple(float(x) for x in os.environ.get('QC_TINT','0.045,0.10,0.04').split(','))
for mn in ('QB_PZ_feather_skirt_fade_UNVERIFIED','QB_PK_fill_skirt_fade_UNVERIFIED'):
    m=bpy.data.materials[mn]; N=m.node_tree.nodes
    mr=[n for n in N if n.type=='MAP_RANGE' and abs(n.inputs['From Min'].default_value-0.35)<1e-6][0]
    mx=N['QB_fade_mix']; B=[x for x in mx.inputs if x.identifier=='B_Color'][0]
    if 'qc_prev' in m:
        p=list(m['qc_prev']); mr.inputs['To Min'].default_value=p[0]; B.default_value=p[1:5]; del m['qc_prev']
        if 'UNVERIFIED_qc' in m: del m['UNVERIFIED_qc']
        print('REVERTED_QC_SKIRTEDGE',mn)
    if REV: continue
    m['qc_prev']=[mr.inputs['To Min'].default_value]+list(B.default_value)
    mr.inputs['To Min'].default_value=TM; B.default_value=TT+(1.0,)
    m['UNVERIFIED_qc']='qc (Nov 2 2026): fade noise floor %.2f, tint %s at the skirt crossing'%(TM,TT)
    print('QC_SKIRTEDGE',mn,TM,TT)
