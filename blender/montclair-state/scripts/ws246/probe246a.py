# ws246: east stand north-end back: what is the dark wedge? (stand object bboxes + evaluated ground grid behind the stand)
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for o in []:
    if 0:
        M=o.matrix_world; vs=[M@v.co for v in o.data.vertices]
        if not vs: continue
        print('P246 OBJ %-34s v%6d x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f hide%d'%(o.name[:34],len(vs),min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs),min(v.z for v in vs),max(v.z for v in vs),o.hide_render),flush=True)
NAMES=[o.name for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('M3a_','M3b_','Terrain','WS6','WS60','PK_','PZ_'))]
dg=bpy.context.evaluated_depsgraph_get()
BX=[float(v) for v in os.environ.get('PG','-234,-210,108,128').split(',')]
def ev(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    V=[M@v.co for v in me.vertices]
    P=[p.vertices[:] for p in me.polygons if any(BX[0]-3<V[i].x<BX[1]+3 and BX[2]-3<V[i].y<BX[3]+3 for i in p.vertices)]
    t=BVHTree.FromPolygons(V,P); e.to_mesh_clear(); del V; print('P246 ev',o.name[:30],len(P),open('/proc/meminfo').read().split('MemAvailable:')[1].split()[0],flush=True); return t
GR=[ev(bpy.data.objects[n]) for n in NAMES]
ST=[(n,ev(bpy.data.objects[n])) for n in [o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('fse')]]
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('PG','-234,-210,108,128').split(',')]
y=Y1
while y>=Y0:
    row=[]; x=X0
    while x<=X1:
        hh=[t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)[0] for t in GR]; hh=[h.z for h in hh if h]
        sz=[(n,t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)[0]) for n,t in ST]; sz=[(n,h.z) for n,h in sz if h]
        top=max(sz,key=lambda a:a[1]) if sz else None
        row.append('%s/%s'%('%.1f'%max(hh) if hh else '--', ('%.1f%s'%(top[1],top[0][4:6])) if top else '--'))
        x+=2
    print('P246 y=%.0f '%y+' '.join(row),flush=True); y-=1
os._exit(0)
