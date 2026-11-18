# ws180b: small mulch/worn-soil rings at the Normal Ave N street trees (prep/ws179_mulch/REFS.md §2: 2023 single-return ground intensity
# darker within ~1-1.5 m of each trunk, lawn beyond; 2017 lawn to ~1 m) + trunk nudges to the low class-1 trunk returns (row1, lawn_N),
# applied only if the new spot is lawn/verge (not walk/curb/road). Rings r 0.9 m, feathered, no edging — UNVERIFIED (LiDAR-only).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
PAVE=('curb','sidewalk','walk_','carriageway','road','bridge','spur','proxy')
cand=[o for o in OB if o.type=='MESH' and 'tree' not in o.name.lower() and not o.name.startswith(('SUB174','WS180_ring','UTIL170','WS170_util')) and 'CAM' not in o.name]
TREES=[]
def near(o,x,y,r=6):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return min(c.x for c in bb)-r<x<max(c.x for c in bb)+r and min(c.y for c in bb)-r<y<max(c.y for c in bb)+r
CEN=(-287.0,-250.0); BV=[]
for o in cand:
    if not near(o,*CEN,r=12): continue
    oe=o.evaluated_get(dg); m=oe.to_mesh()
    if len(m.polygons): BV.append((o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons])))
    oe.to_mesh_clear()
def topz(x,y):
    best=None
    for nm,b in BV:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None and (best is None or h[0].z>best[1]): best=(nm,h[0].z)
    return best
def pav(nm): return 'lawn' not in nm.lower() and 'ground' not in nm.lower() and any(k in nm.lower() for k in PAVE)
MOVE={'WS166_tree_NormalAve_N_row1':(-294.5,-252.5),'WS166_tree_lawn_N_of_row':(-282.9,-244.5)}
RING=('WS166_tree_NormalAve_N_row1','WS166_tree_NormalAve_N_row2','WS166_tree_NormalAve_N_row3','WS166_tree_lawn_N_of_row')
mat=bpy.data.materials.get('WS180_mulch_ring_feathered') or bpy.data.materials.new('WS180_mulch_ring_feathered')
mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
o_=nt.nodes.new('ShaderNodeOutputMaterial'); mx=nt.nodes.new('ShaderNodeMixShader'); pb=nt.nodes.new('ShaderNodeBsdfPrincipled'); tr=nt.nodes.new('ShaderNodeBsdfTransparent')
pb.inputs['Base Color'].default_value=(0.045,0.030,0.019,1); pb.inputs['Roughness'].default_value=0.95
tc=nt.nodes.new('ShaderNodeTexCoord'); ln=nt.nodes.new('ShaderNodeVectorMath'); ln.operation='LENGTH'
mr=nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type='SMOOTHSTEP'; mr.inputs['From Min'].default_value=0.35; mr.inputs['From Max'].default_value=0.98
noi=nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value=6.0
ad=nt.nodes.new('ShaderNodeMath'); ad.operation='ADD'; mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=0.25
L=nt.links.new
L(tc.outputs['Object'],ln.inputs[0]); L(noi.outputs['Fac'],mul.inputs[0]); L(ln.outputs['Value'],ad.inputs[0]); L(mul.outputs[0],ad.inputs[1])
L(ad.outputs[0],mr.inputs['Value']); L(mr.outputs['Result'],mx.inputs['Fac']); L(pb.outputs[0],mx.inputs[1]); L(tr.outputs[0],mx.inputs[2]); L(mx.outputs[0],o_.inputs['Surface'])
L(tc.outputs['Object'],noi.inputs['Vector'])
try: mat.blend_method='HASHED'
except Exception: pass
for o in [o for o in OB if o.name.startswith('WS180_ring')]: OB.remove(o)
for o in OB:
    if o.type!='MESH': continue
    for pfx,(nx,ny) in MOVE.items():
        if o.name.startswith(pfx):
            h=topz(nx,ny); h0=topz(o.location.x,o.location.y)
            print('FIX180B move?',o.name[:40],'old',tuple(round(c,2) for c in o.location),h0,'new',(nx,ny),h,flush=True)
            if h and not pav(h[0]): o.location=(nx,ny,h[1]-0.03); print('FIX180B moved',o.name[:40],flush=True)
            else: print('FIX180B NOT moved (paving at new spot)',flush=True)
col=bpy.context.scene.collection
for o in [o for o in OB if o.type=='MESH' and o.name.startswith(RING)]:
    cx,cy=o.location.x,o.location.y; bm=bmesh.new(); R=1.0; rows=[]
    for i,r in enumerate(np.linspace(0.12,R,8)):
        row=[]
        for k in range(32):
            a=2*math.pi*k/32; x=cx+r*math.cos(a); y=cy+r*math.sin(a); h=topz(x,y)
            z=(h[1]+0.010) if h and not pav(h[0]) else ((h[1]-0.03) if h else o.location.z)
            row.append(bm.verts.new((x-cx,y-cy,z-o.location.z)))
        rows.append(row)
    for a,b in zip(rows[:-1],rows[1:]):
        for k in range(32): bm.faces.new((a[k],a[(k+1)%32],b[(k+1)%32],b[k]))
    c=bm.verts.new((0,0,rows[0][0].co.z));
    for k in range(32): bm.faces.new((c,rows[0][k],rows[0][(k+1)%32]))
    me=bpy.data.meshes.new('WS180_ring'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth=True
    r=OB.new('WS180_ring_mulch_r0p9_%s_LiDAR2023int_UNVERIFIED'%o.name[6:30],me); r.location=o.location.copy(); col.objects.link(r)
    # object coords: length 0.92 => fully transparent beyond ~0.9 m
    print('FIX180B ring',r.name,flush=True)
