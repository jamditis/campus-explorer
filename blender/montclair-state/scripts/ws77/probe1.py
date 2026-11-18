import bpy
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
objs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot','WS76_accessible_lot','WS76_lot'))]
print('WS77P objs',[o.name[:40] for o in objs],flush=True)
def hits(x,y):
    r=[]
    for o in objs:
        mi=o.matrix_world.inverted(); a=mi@Vector((x,y,300)); b=mi@Vector((x,y,0))
        try: ok,loc,n,i=o.ray_cast(a,(b-a).normalized())
        except Exception: continue
        if ok: r.append((o.name[:22],round((o.matrix_world@loc).z,2)))
    return r
for x in (-254,-245,-237,-228,-218):
    for y in range(-78,-99,-2):
        print('WS77P',x,y,hits(x,y),flush=True)
