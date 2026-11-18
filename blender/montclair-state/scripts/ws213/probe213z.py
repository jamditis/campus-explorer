import bpy, json, numpy as np, collections
from mathutils.bvhtree import BVHTree
from mathutils import Vector
F='/workspace/nj-scenes/montclair-state/montclair_state_ws213a.blend'
BB=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
PN=['WS76_lot_zebra_walkway_paint_ortho2020_UNVERIFIED','WS204_lot_entrance_crosswalk_paint_ortho2020_UNVERIFIED_bars']
X0,X1,Y0,Y1=-266,-249,-96,-55
want=[n for n,v in BB.items() if v[0]=='MESH' and not (v[3]<X0 or v[2]>X1 or v[5]<Y0 or v[4]>Y1) and not n.startswith(('Context_skirt','BD_farfield'))]+PN
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in set(want) if n in a.objects]
T=[]
for o in b.objects:
    if o is None or o.name in PN or o.type!='MESH' or 'paint' in o.name.lower() or 'DTM_target' in o.name or o.name.startswith('Terrain_LiDAR') or o.hide_render or len(o.data.polygons)==0: continue
    m=o.matrix_world; V=[m@v.co for v in o.data.vertices]; T.append((o,BVHTree.FromPolygons(V,[p.vertices[:] for p in o.data.polygons])))
out={}
for P in [o for o in b.objects if o and o.name in PN]:
    mw=P.matrix_world; me=P.data
    print('PAINT',P.name,len(me.polygons),[m.name if m else None for m in me.materials],[(m.type,m.name) for m in P.modifiers])
    res=collections.Counter(); dz=collections.defaultdict(list)
    for p in me.polygons:
        c=mw@p.center; best=None
        for o,t in T:
            h=t.ray_cast(Vector((c.x,c.y,c.z+3)),Vector((0,0,-1)),10)
            if h[0] is not None and (best is None or h[0].z>best[0]):
                best=(h[0].z,o.name,o.data.materials[o.data.polygons[h[2]].material_index].name if o.data.materials else None)
        k=(best[1],best[2]) if best else (None,None); res[k]+=1
        if best: dz[k].append(c.z-best[0])
    for k,v in res.most_common(): print('HITZ',P.name[:20],k,v,round(float(np.median(dz[k])),3) if dz[k] else None)
    out[P.name]={'V':[(mw@v.co)[:] for v in me.vertices],'P':[list(p.vertices) for p in me.polygons],'M':[p.material_index for p in me.polygons],'mats':[m.name if m else None for m in me.materials]}
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws213/zebra.json','w'))
mm=bpy.data.materials.get('KY_college_ave_asphalt_UNVERIFIED')
if mm:
    bs=[n for n in mm.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]; print('KYBSDF',bs.name,[ (l.from_node.name,l.from_socket.name) for l in bs.inputs['Base Color'].links],[(l.from_node.name) for l in bs.inputs['Roughness'].links])
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM',l.strip())
