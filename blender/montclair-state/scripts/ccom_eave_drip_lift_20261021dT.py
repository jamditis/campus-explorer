# Session dT: after ccom_north_wall_and_corner_rooms_20261021dT.py raised CCOM's ragged wall tops to the
# eave, the 3g "Eave drip / moss streaks" decal still hung at the OLD wall top (a faint wavy line mid-wall).
# Shift each decal vertex up by the raise of the nearest raised wall-top vertex (xy < 0.8 m). Idempotent
# (attribute dT_orig_z). SAVE=1 saves, REVERT=1 restores.
import bpy, os
from mathutils import kdtree, Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
D=bpy.data.objects['Eave drip / moss streaks on stucco (3g)']; dm=D.data
a=dm.attributes.get('dT_orig_z')
if a is not None:
    for v,x in zip(dm.vertices,a.data):
        if x.value>-1e8: v.co.z=x.value
    dm.attributes.remove(a); dm.update(); print('reverted decal')
if not REVERT:
    W=bpy.data.objects['School of Communication and Media walls']; wa=W.data.attributes['dT_orig_z']
    pts=[(v.co.copy(),v.co.z-x.value) for v,x in zip(W.data.vertices,wa.data) if x.value>-1e8]
    kd=kdtree.KDTree(len(pts))
    for i,(c,_) in enumerate(pts): kd.insert(Vector((c.x,c.y,0)),i)
    kd.balance()
    mw=D.matrix_world; inv=mw.inverted()
    a=dm.attributes.new('dT_orig_z','FLOAT','POINT')
    n=0
    for v,x in zip(dm.vertices,a.data):
        x.value=-1e9
        w=mw@v.co; co,i,d=kd.find(Vector((w.x,w.y,0)))
        if d<0.8 and pts[i][1]>0.3:
            x.value=v.co.z; w.z+=pts[i][1]; v.co=inv@w; n+=1
    dm.update(); print('decal verts lifted',n,'of',len(dm.vertices))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
