# ws189: list every object (incl. hidden) whose geometry lies within 0-7 m ahead of the Lot 36 W eye camera, NO depsgraph eval
import bpy, numpy as np
from mathutils import Vector
def hwm():
    for l in open('/proc/self/status'):
        if l.startswith(('VmHWM','VmRSS')): print('MEM189',l.strip(),flush=True)
hwm()
X0,X1,Y0,Y1=-338.5,-328.0,-233.5,-228.5
vl=bpy.context.view_layer
def colvis(o):
    return [(c.name,c.hide_viewport,c.hide_render) for c in o.users_collection]
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','EMPTY'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    info=''
    if o.type=='MESH' and len(o.data.vertices)<3_000_000:
        n=len(o.data.vertices); co=np.empty(n*3,dtype=np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)
        M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
        k=(w[:,0]>X0)&(w[:,0]<X1)&(w[:,1]>Y0)&(w[:,1]<Y1)
        info=f'nv={n} inreg={int(k.sum())}'+(f' z={w[k,2].min():.2f}..{w[k,2].max():.2f}' if k.any() else '')
    mods=[(m.type,m.name,m.show_viewport,m.show_render) for m in o.modifiers]
    psys=len(o.particle_systems) if o.type=='MESH' else 0
    print('OBJ189',o.name,o.type,'hv',o.hide_viewport,'hr',o.hide_render,'hget',o.hide_get(view_layer=vl) if o.name in vl.objects else 'notinVL',info,'ps',psys,'mods',mods,'cols',colvis(o),flush=True)
hwm()
