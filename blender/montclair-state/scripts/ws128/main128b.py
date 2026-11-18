# ws128 self-review fix: drive N curb ends stood up as open white blocks at the brick crossing / construction end -> taper reveal to flush over ~1.2 m (W) / 0.8 m (E), cap the ends
import bpy, bmesh, os
SAVE=os.environ.get('SAVE','0')=='1'
o=next(o for o in bpy.data.objects if o.name.startswith('WS128_Chapin_S_drive_N_curb'))
me=o.data; n=len(me.vertices)//4; REV=0.14
if not o.get('tapered'):
    for k in range(n):
        f=min(1.0,k/3.0,(n-1-k)/2.0)
        for i in (1,2): me.vertices[4*k+i].co.z-=REV*(1-f)
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    for k in (0,n-1):
        try: bm.faces.new([bm.verts[4*k+i] for i in range(4)])
        except ValueError: pass
    bm.normal_update(); bm.to_mesh(me); bm.free(); o['tapered']=1
print('M128b curb rings',n,'tapered')
if SAVE: bpy.ops.wm.save_mainfile(); print('M128b SAVED')
