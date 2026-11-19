# ws233 probe b: what surface meets Stone Hall's ESE wall (x~146-150, y 205-232)? vertical ray stacks at 0.2..4 m out from the wall
import bpy,sys,os,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
BB=json.load(open(M+'scripts/ws205/bbox205.json'))
want=[n for n,v in BB.items() if v[0]=='MESH' and not v[1] and not n.startswith(('T_','WQ_south_wood_tree','WM_south_wood_tree')) and not (v[3]<140 or v[2]>156 or v[5]<205 or v[4]>235)]
with bpy.data.libraries.load(M+os.environ.get('PF','montclair_state.blend'),link=False) as (src,dst):
    dst.objects=[n for n in want if n in src.objects]
O=[o for o in dst.objects if o]
for o in O: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); B={}
for o in O:
    e=o.evaluated_get(dg); mm=e.to_mesh()
    if len(mm.polygons): B[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
    e.to_mesh_clear()
# wall line through (149.58,230.92) dir (0.4,0.92), outward normal (0.92,-0.4)
for s in (-8,-4,0,-12):
    base=Vector((149.58+0.4*s,230.92+0.92*s,0))
    for off in (0.1,0.3,0.6,1.0,1.5,2.5,4.0):
        p=base+Vector((0.92*off,-0.4*off,0)); st=[]
        for n,b in B.items():
            z=400
            for _ in range(4):
                h=b.ray_cast(Vector((p.x,p.y,z)),Vector((0,0,-1)))
                if h[0] is None: break
                st.append((round(h[0].z,2),n[:40])); z=h[0].z-0.01
        st.sort(reverse=True)
        print('P233B s',s,'off',off,[round(p.x,1),round(p.y,1)],st[:6],flush=True)
sys.stdout.flush(); os._exit(0)
