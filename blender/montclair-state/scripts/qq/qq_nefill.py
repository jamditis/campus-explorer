# qq_nefill: the pale 'box' at the NE road edge (~(221.5,215.3)) = QJ_NE_seam_fill faces 550/559/562 standing 0.1-0.4 m above
# the draped Roads_OSM asphalt. Lower fill verts that lie under the evaluated road surface (box x 218-225, y 212-218) to road-0.06.
# REVERT=1 restores the recorded vertex z values (data/qq/nefill_prev.json).
import bpy, json, os
from mathutils import Vector
R=os.environ.get('REVERT')=='1'; J='data/qq/nefill_prev.json'
o=bpy.data.objects['QJ_NE_seam_fill_UNVERIFIED']; me=o.data; Mw=o.matrix_world; Mi=Mw.inverted()
if R:
    d=json.load(open(J))
    for k,z in d.items(): me.vertices[int(k)].co.z=z
    me.update(); print('QQN reverted',len(d))
else:
    dg=bpy.context.evaluated_depsgraph_get(); rd=bpy.data.objects['Roads_OSM']; re_=rd.evaluated_get(dg); Ri=rd.matrix_world.inverted()
    prev={}
    for v in me.vertices:
        w=Mw@v.co
        if not (218<=w.x<=225 and 212<=w.y<=218): continue
        best=None
        for dx,dy in ((0,0),(0.25,0),(-0.25,0),(0,0.25),(0,-0.25)):
            ok,loc,n,i=re_.ray_cast(Ri@Vector((w.x+dx,w.y+dy,w.z+6)),Ri.to_3x3()@Vector((0,0,-1)),depsgraph=dg)
            if ok:
                z=(rd.matrix_world@loc).z
                if abs(z-w.z)<1.5: best=z if best is None else min(best,z)
        if best is not None and w.z>best-0.06:
            prev[str(v.index)]=v.co.z; nw=Vector((w.x,w.y,best-0.06)); v.co=Mi@nw
    me.update(); json.dump(prev,open(J,'w')); print('QQN lowered',len(prev))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QQSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('QQSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QQSAVEAS'],copy=True); print('SAVED_AS')
