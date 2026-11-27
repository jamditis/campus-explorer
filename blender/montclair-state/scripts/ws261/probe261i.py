# ws261 M2c review (merge208 CHAIN on main, base meshes, NO SAVE): north-file grass scatter point sets gb_grass_slope_points and
# gd_grass_police_lawn_points. Append them into this throwaway session, report what they are (verts/edges/faces, modifiers + GN groups,
# particle systems, who instances them in north), their z vs main's base top surface, and main's own grass/lawn scatter in the bbox.
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='P261I'; NF='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
names=['gb_grass_slope_points','gd_grass_police_lawn_points']
with bpy.data.libraries.load(NF,link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n in names]
for o in dst.objects:
    if o is None: continue
    bpy.context.scene.collection.objects.link(o)
    me=o.data; mw=o.matrix_world; V=np.array([tuple(mw@v.co) for v in me.vertices]) if o.type=='MESH' else np.zeros((0,3))
    print(TAG,o.name,o.type,'v',len(me.vertices) if o.type=='MESH' else '-','e',len(me.edges) if o.type=='MESH' else '-','f',len(me.polygons) if o.type=='MESH' else '-',
          'hide_render',o.hide_render,'mods',[(m.name,m.type,getattr(getattr(m,'node_group',None),'name',None),m.show_render) for m in o.modifiers],
          'psys',[p.settings.name for p in getattr(o,'particle_systems',[])],'parent',o.parent.name if o.parent else None,'inst',o.instance_type,flush=True)
    if not len(V): continue
    x0,y0=V[:,:2].min(0); x1,y1=V[:,:2].max(0)
    print(TAG,'bbox x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(x0,x1,y0,y1,V[:,2].min(),V[:,2].max()),flush=True)
    objs=[]; grass=[]
    for q in bpy.data.objects:
        if q.type!='MESH' or q is o or q.name in names or q.name.startswith(('T_','TREE','Context_','Roof_vent')): continue
        bb=[q.matrix_world@Vector(c) for c in q.bound_box]
        if max(v.x for v in bb)<x0 or min(v.x for v in bb)>x1 or max(v.y for v in bb)<y0 or min(v.y for v in bb)>y1: continue
        if any(k in q.name.lower() for k in ('grass','tuft','lawn_scatter','blade','clover')): grass.append((q.name[:60],len(q.data.vertices),[m.name for m in q.modifiers][:3],q.hide_render))
        if q.hide_render: continue
        W=q.matrix_world; QV=[W@v.co for v in q.data.vertices]; P=[tuple(p.vertices) for p in q.data.polygons]
        if P: objs.append((q.name,BVHTree.FromPolygons(QV,P)))
    print(TAG,'main meshes in bbox',len(objs),'main grass-like objs',len(grass),grass[:12],flush=True)
    idx=np.random.default_rng(1).choice(len(V),min(800,len(V)),replace=False); dz=[]; tops={}
    for i in idx:
        x,y,z=V[i]; best=None
        for n,t in objs:
            h=t.ray_cast(Vector((x,y,z+60)),Vector((0,0,-1)),120)
            if h[0] is not None and (best is None or h[0].z>best[1]): best=(n,h[0].z)
        if best: dz.append(z-best[1]); tops[best[0][:40]]=tops.get(best[0][:40],0)+1
    dz=np.array(dz)
    if len(dz): print(TAG,'z - main top: n',len(dz),'p5/p50/p95 %.2f %.2f %.2f'%tuple(np.percentile(dz,[5,50,95])),'below -0.1',int((dz<-0.1).sum()),'above +0.3',int((dz>0.3).sum()),flush=True)
    print(TAG,'top objects',sorted(tops.items(),key=lambda kv:-kv[1])[:8],flush=True)
# who uses them in north? (GN Object Info / particle instance) - scan node groups that came along
for ng in bpy.data.node_groups:
    for nd in ng.nodes:
        if nd.bl_idname=='GeometryNodeObjectInfo':
            ob=nd.inputs[0].default_value
            if ob is not None and ob.name in names: print(TAG,'used by node group',ng.name,flush=True)
print(TAG,'done',flush=True); os._exit(0)
