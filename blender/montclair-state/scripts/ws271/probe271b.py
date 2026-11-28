# ws271 probe (no save): Sprague grandstand lawn (#4). Which objects carry WS86 modifiers, their settings, and the evaluated surface grid.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
hit=[]
for o in OB:
    for m in o.modifiers:
        if 'WS86' in m.name or 'grandstand' in m.name.lower():
            hit.append(o)
            print('P271B MOD',o.name,'|',m.name,m.type,getattr(m,'node_group',None) and m.node_group.name,flush=True)
            if m.type=='NODES':
                for k in m.keys():
                    try: print('P271B  in',k,m[k])
                    except Exception: pass
                ng=m.node_group
                for n in ng.nodes: 
                    if n.type in ('VALUE','MATH','MAP_RANGE','OBJECT_INFO','RAYCAST','PROXIMITY','GEOMETRY_PROXIMITY'):
                        print('P271B  node',n.name,n.type,[ (i.name,getattr(i,'default_value',None) if not hasattr(getattr(i,'default_value',None),'__len__') else tuple(i.default_value)) for i in n.inputs][:6], getattr(n,'operation',''), [o2.default_value for o2 in n.outputs if n.type=='VALUE'])
for o in set(hit):
    print('P271B obj',o.name,'mods',[(m.name,m.type) for m in o.modifiers],flush=True)
t=OB.get('WS86_grandstand_DTM_target')
if t: bb=[t.matrix_world@Vector(c) for c in t.bound_box]; print('P271B target bbox',[round(min(b[i] for b in bb),1) for i in range(3)],[round(max(b[i] for b in bb),1) for i in range(3)],'hide_render',t.hide_render)
# evaluated grid of objects in the grandstand window with modifiers ON for terrain-ish objects that overlap
W=(-262,-222,-162,-120)
cand=[]
for o in OB:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1>W[0] and x0<W[1] and y1>W[2] and y0<W[3] and (x1-x0)>20: cand.append(o)
print('P271B cand',[o.name for o in cand],flush=True)
TER=[o for o in cand if o.name.startswith(('Terrain_LiDAR_DTM_1m',))]
for o in TER:
    for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get()
xs=np.arange(W[0],W[1],0.5); ys=np.arange(W[2],W[3],0.5)
for o in TER:
    oe=o.evaluated_get(dg); me=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not any(W[0]-3<v.co.x<W[1]+3 and W[2]-3<v.co.y<W[3]+3 for v in f.verts)],context='FACES')
    print('P271B eval',o.name,'faces in win',len(bm.faces),flush=True)
    T=BVHTree.FromBMesh(bm)
    Z=np.full((len(ys),len(xs)),np.nan)
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            r=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            if r[0] is not None: Z[j,i]=r[0].z
    bm.free(); oe.to_mesh_clear()
    np.savez_compressed('/workspace/nj-scenes/montclair-state/scripts/ws271/probe271b_%s.npz'%o.name[:20].replace(' ','_'),Z=Z,xs=xs,ys=ys)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('P271B',l.strip())
