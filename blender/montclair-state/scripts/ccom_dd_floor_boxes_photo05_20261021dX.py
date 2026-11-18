"""2026-10-21 session dX (~12:27 PM ET). Joe's photo 05 shows round flush brushed-metal floor boxes (power/data, ~0.15 m) on the
rug beside each dining table. Adds 2 per dd dining table, on the floor at the table's two short ends +0.95 m from its centre along
the long axis (positions photo-approximated, UNVERIFIED +/-0.3 m). obj prop dX2_new; REVERT=1 deletes; SAVE=1 saves."""
import bpy, bmesh, os, math, re
from mathutils import Vector, Matrix
for o in [o for o in bpy.data.objects if 'dX2_new' in o]:
    me=o.data; bpy.data.objects.remove(o)
    if me.users==0: bpy.data.meshes.remove(me)
n=0
if os.environ.get('REVERT')!='1':
    mat=bpy.data.materials['CCOM_dc_chrome']
    for t in [o for o in bpy.data.objects if re.match(r'dd_[A-Z0-9]+_table_\d+$', o.name)]:
        P=[t.matrix_world@Vector(c) for c in t.bound_box]; c=sum(P,Vector())/8
        seg,i=re.match(r'dd_([A-Z0-9]+)_table_(\d+)$',t.name).groups()
        legs=[o for o in bpy.data.objects if o.name.startswith('dd_%s_tped_%s'%(seg,i))]
        fl=min((l.matrix_world@Vector(cc)).z for l in legs for cc in l.bound_box)
        # long axis of the top in world XY
        M3=t.matrix_world.to_3x3(); ax=[M3.col[0].xy, M3.col[1].xy]
        ext=[max(abs((p.xy-c.xy).dot(a.normalized())) for p in P) for a in ax]
        a=ax[0].normalized() if ext[0]>ext[1] else ax[1].normalized()
        for s in (-1,1):
            q=c.xy+a*s*(max(ext)+0.25)
            bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=24,radius1=0.075,radius2=0.07,depth=0.006)
            me=bpy.data.meshes.new('dd_%s_floorbox_%s_%d_dX'%(seg,i,s)); bm.to_mesh(me); bm.free(); me.materials.append(mat)
            o=bpy.data.objects.new(me.name,me); o.location=(q.x,q.y,fl+0.003+0.0125); o['dX2_new']=1
            # sit on rug (rug top = floor+0.012)
            t.users_collection[0].objects.link(o); n+=1
print('DX2 floor boxes', n, flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('DX2_SAVED', flush=True)
