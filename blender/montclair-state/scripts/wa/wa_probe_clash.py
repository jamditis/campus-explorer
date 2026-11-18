# wa: 4a clash probe — VW overlay boxes vs Bohn masses/shafts (point-in-mesh via ray parity), read-only
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT='/workspace/nj-scenes/montclair-state/data/wa'
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh()
    vs=[o.matrix_world@v.co for v in me.vertices]; ps=[list(p.vertices) for p in me.polygons]
    t=BVHTree.FromPolygons(vs,ps); e.to_mesh_clear(); return t
def inside(t,p):
    n=0; o=Vector(p); d=Vector((0.0123,0.0071,1)).normalized()
    while n<20:
        h=t.ray_cast(o,d)
        if h[0] is None: break
        n+=1; o=h[0]+d*1e-4
    return n%2==1
res={}
shafts=[o for o in bpy.data.objects if o.name.startswith('TP_Bohn_shaft_') and o.type=='MESH' and 'coping' not in o.name]
masses=[bpy.data.objects[n] for n in ('TL_Bohn_Hall_L1_0_rect_UNVERIFIED','TL_Bohn_Hall_L2_0_rect_UNVERIFIED','TL_Bohn_Hall_L3_0_rect_UNVERIFIED','TL_Bohn_Hall_L4_0_rect_UNVERIFIED','TK_Bohn_Hall_232853538_base_UNVERIFIED')]
trees={o.name:bvh(o) for o in shafts+masses}
for vn in ('VW_Bohn_W_piers_bands_UNVERIFIED','VW_Bohn_W_glass_UNVERIFIED'):
    o=bpy.data.objects[vn]; me=o.data; mw=o.matrix_world
    nb=len(me.polygons)//6; st={'boxes':nb}
    for k,t in trees.items():
        part=0; full=0; ex=[]
        for b in range(nb):
            ps=me.polygons[b*6:(b+1)*6]
            vids=set(i for p in ps for i in p.vertices)
            ins=[inside(t,mw@me.vertices[i].co) for i in vids]
            if all(ins): full+=1
            elif any(ins):
                part+=1
                if len(ex)<8:
                    c=sum((mw@me.vertices[i].co for i in vids),Vector())/len(vids); ex.append([round(c.x,2),round(c.y,2),round(c.z,2),sum(ins)])
        st[k]=dict(full_inside=full,partial=part,examples=ex)
    res[vn]=st
json.dump(res,open(OUT+'/clash_probe.json','w'),indent=1)
for vn,st in res.items():
    print('CL',vn,st['boxes'])
    for k,v in st.items():
        if k!='boxes' and (v['full_inside'] or v['partial']): print('CL  ',k,v['full_inside'],v['partial'],v['examples'][:4])
