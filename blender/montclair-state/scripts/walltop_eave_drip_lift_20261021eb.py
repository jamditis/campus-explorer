# Session eb: after walltop_gap_audit_fix_20261021eb.py (FIX=1) raised wall tops (Life Hall, Morehead, Schmitt,
# Memorial Aud., SCM small seams), lift the 3g "Eave drip / moss streaks" decal by the raise of the nearest raised
# wall-top vertex (xy < 0.8 m, raise > 0.3 m) so the streaks hang from the eave, not the old top (dT method).
# Idempotent (decal attribute 'eb_orig_z'). SAVE=1 saves, REVERT=1 restores.
import bpy, os
from mathutils import kdtree, Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
BLD=['School of Communication and Media','Life Hall','Morehead Hall','Finley Hall','Memorial Auditorium','Schmitt Hall','Speech Building']
D=bpy.data.objects['Eave drip / moss streaks on stucco (3g)']; dm=D.data
a=dm.attributes.get('eb_orig_z')
if a is not None:
    for v,x in zip(dm.vertices,a.data):
        if x.value>-1e8: v.co.z=x.value
    dm.attributes.remove(a); dm.update(); print('reverted decal')
    if 'eb_drip_lift' in D: del D['eb_drip_lift']
if not REVERT:
    pts=[]
    for b in BLD:
        W=bpy.data.objects.get(b+' walls')
        if not W or 'eb_orig_z' not in W.data.attributes: continue
        M=W.matrix_world
        for v,x in zip(W.data.vertices,W.data.attributes['eb_orig_z'].data):
            if x.value>-1e8:
                w=M@v.co; pts.append((w,w.z-x.value,x.value))
    kd=kdtree.KDTree(max(1,len(pts)))
    for i,(c,_,_) in enumerate(pts): kd.insert(Vector((c.x,c.y,0)),i)
    kd.balance()
    mw=D.matrix_world; inv=mw.inverted()
    a=dm.attributes.new('eb_orig_z','FLOAT','POINT'); n=0
    for v,x in zip(dm.vertices,a.data):
        x.value=-1e9
        if not pts: continue
        w=mw@v.co; co,i,d=kd.find(Vector((w.x,w.y,0)))
        if d<0.8 and pts[i][1]>0.3 and w.z<=pts[i][2]+0.05:
            x.value=v.co.z; w.z+=pts[i][1]; v.co=inv@w; n+=1
    dm.update(); D['eb_drip_lift']=n; print('decal verts lifted',n,'of',len(dm.vertices))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
