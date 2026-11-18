import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; return BVHTree.FromObject(o,dg)
bt=bvh('Terrain_LiDAR_DTM_1m'); bs=bvh('Context_skirt_3DEP_ortho_4km'); bf=bvh('QJ_NE_seam_fill_UNVERIFIED')
DN=Vector((0,0,-1))
def gz(x,y):
    r=[]
    for b in (bt,bf,bs):
        h=b.ray_cast(Vector((x,y,500)),DN)[0]; r.append(None if h is None else round(h.z,2))
    return r
for n in ('Roads_OSM','Footpaths_OSM'):
    o=bpy.data.objects[n]
    print(n,[(m.name,m.type,m.show_render,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers], 'mats',[m.name for m in o.data.materials if m], 'verts',len(o.data.vertices))
    e=o.evaluated_get(dg); me=e.to_mesh(); W=o.matrix_world
    V=np.array([tuple(W@v.co) for v in me.vertices])
    sel=np.nonzero((V[:,0]>195)&(V[:,0]<240)&(V[:,1]>185)&(V[:,1]<225))[0]
    print(' sel verts',len(sel))
    out=[]
    for i in sel:
        x,y,z=V[i]; g=gz(x,y); gg=[a for a in g if a is not None]
        top=max(gg) if gg else None
        out.append((round(x,1),round(y,1),round(z,2),g, None if top is None else round(z-top,2)))
    out.sort(key=lambda t:-(t[4] or -99))
    for t in out[:6]: print('  ',t)
    d=[t[4] for t in out if t[4] is not None]
    if d: print(' dz stats >0.3:',sum(1 for a in d if a>0.3),'< -0.3:',sum(1 for a in d if a<-0.3),'n',len(d))
    # face normals: count near-vertical faces (curtains) in region
    nv=0
    for p in me.polygons:
        c=W@p.center
        if 195<c.x<240 and 185<c.y<225 and abs(p.normal.z)<0.3: nv+=1
    print(' vertical-ish faces in region',nv,'of',len(me.polygons))
    e.to_mesh_clear()
