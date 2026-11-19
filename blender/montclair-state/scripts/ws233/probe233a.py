# ws233 probe a: W53o Stone Hall lower volume - window faces vs EVALUATED ground just outside the wall
import bpy,sys,os,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    if not (-278<x<278 and -278<y<278): return float('nan')
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch','QW_DTM_north_edge_ramp_UNVERIFIED','QM_terrain_band_underlay_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED']
BB=json.load(open(M+'scripts/ws205/bbox205.json'))
near=[n for n,v in BB.items() if v[0]=='MESH' and not (v[3]<128 or v[2]>182 or v[5]<208 or v[4]>306) and ('Stone' in n or 'stone' in n or n.startswith(('WV','WN','wm','WM')))]
print('P233 near',near,flush=True)
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst):
    dst.objects=[n for n in set(G+near) if n in src.objects]
O=[o for o in dst.objects if o]
for o in O: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); GB=[]
for o in O:
    e=o.evaluated_get(dg); mm=e.to_mesh(); Mw=o.matrix_world
    print('P233 obj',o.name,len(mm.polygons),[m.name for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots],flush=True)
    if o.name in G or 'patch' in o.name.lower() or 'DTM' in o.name or 'grade' in o.name.lower():
        if len(mm.polygons): GB.append((o.name,BVHTree.FromPolygons([Mw@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])))
    e.to_mesh_clear()
def top(x,y):
    best=None
    for n,b in GB:
        h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best[0]): best=(h[0].z,n)
    return best
mt=bpy.data.materials.get('TR_Stone_brick_detail_UNVERIFIED')
for nd in mt.node_tree.nodes:
    vals=[(i.name,round(i.default_value,3)) for i in nd.inputs if not i.is_linked and hasattr(i,'default_value') and isinstance(i.default_value,float)]
    print('P233N',nd.name,nd.type,getattr(nd,'operation',''),getattr(nd,'attribute_name',''),vals[:6])
for l in mt.node_tree.links: print('P233L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
SH=[o for o in O if o.name.startswith('TI_Stone_Hall')]
out=[]
for o in SH:
    e=o.evaluated_get(dg); mm=e.to_mesh(); Mw=o.matrix_world; N=Mw.to_3x3()
    mats=[s.material.name if s.material else '' for s in o.material_slots]
    for p in mm.polygons:
        mn=mats[p.material_index] if p.material_index<len(mats) else ''
        n=(N@p.normal).normalized()
        if abs(n.z)>0.3: continue
        vs=[Mw@mm.vertices[i].co for i in p.vertices]; c=Mw@p.center
        zlo=min(v.z for v in vs); zhi=max(v.z for v in vs)
        q=c+n*0.8; g=top(q.x,q.y)
        out.append(dict(o=o.name,m=mn,c=[round(c.x,2),round(c.y,2)],n=[round(n.x,2),round(n.y,2)],zlo=round(zlo,2),zhi=round(zhi,2),area=round(p.area,2),g=None if g is None else round(g[0],2),gn=None if g is None else g[1],dep=round(p3(q.x,q.y),2)))
    e.to_mesh_clear()
json.dump(out,open(M+'scripts/ws233/probe233a.json','w'))
from collections import Counter
print('P233 faces',len(out),Counter(f['m'] for f in out).most_common(12))
for mname in set(f['m'] for f in out):
    fs=[f for f in out if f['m']==mname and f['g'] is not None]
    bur=[f for f in fs if f['zlo']<f['g']-0.05]
    print('P233 mat',mname,'n',len(fs),'zlo<ground',len(bur),'zhi<ground',sum(1 for f in fs if f['zhi']<f['g']),flush=True)
sys.stdout.flush(); os._exit(0)
