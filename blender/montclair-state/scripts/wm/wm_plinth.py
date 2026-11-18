"""wm: stepped concrete foundation reveal around Stone Hall lower volume (UNVERIFIED, generic).
Top = ground envelope +0.10, quantised to 0.2 m steps (global grid), min run 1 m; band 1.5 cm proud of wall, 3 cm cap."""
import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line
dg=bpy.context.evaluated_depsgraph_get()
GN=['QW_DTM_north_edge_ramp_UNVERIFIED','WV_stone_west_LiDAR_patch_UNVERIFIED','Context_skirt_3DEP_ortho_4km','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m']
trees={}
for n in GN:
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh()
    bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    trees[n]=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear()
def gz(x,y):
    best=None
    for t in trees.values():
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
    return best
J=json.load(open('scripts/wm/stone_base.json'))
sills=bpy.data.objects['TR_Stone_window_sills_UNVERIFIED']
sv=[sills.matrix_world@v.co for v in sills.data.vertices]
# window bottoms: also look at lower mesh? use sills z
Q=0.2; Z0=130.7; OFF=0.015; CAP=0.03
bm=bmesh.new()
stats=[]
for E in J['edges']:
    a=Vector(E['a']); b=Vector(E['b']); n=Vector(E['n']).normalized()
    L=(b-a).length; d=(b-a)/L
    # sill limit near this wall
    lim=999
    for p in sv:
        q=Vector((p.x,p.y)); c,f=intersect_point_line(q,a,b)
        if -0.05<=f<=1.05 and abs((q-c).dot(n))<0.4: lim=min(lim,p.z)
    k=max(4,int(L/0.25)); xs=[i/k*L for i in range(k+1)]
    raw=[]
    for s in xs:
        p=a+d*s+n*0.12; g=gz(p.x,p.y); raw.append(g)
    if any(g is None for g in raw): continue
    env=[max(raw[max(0,i-2):i+3])+0.10 for i in range(len(raw))]
    top=[Z0+math.ceil((e-Z0)/Q)*Q for e in env]
    # min run 1 m: merge short runs up to neighbour max
    step=L/k; minrun=max(1,int(1.0/step))
    for _ in range(3):
        i=0
        while i<len(top):
            j=i
            while j+1<len(top) and abs(top[j+1]-top[i])<1e-6: j+=1
            if j-i+1<minrun:
                nb=[top[x] for x in (i-1,j+1) if 0<=x<len(top)]
                v=max(nb+[top[i]])
                for x in range(i,j+1): top[x]=v
            i=j+1
    if lim<999: top=[min(t,lim-0.12) for t in top]
    gmin=min(raw)
    # segments of constant top
    segs=[];i=0
    while i<len(top):
        j=i
        while j+1<len(top) and abs(top[j+1]-top[i])<1e-6: j+=1
        s0=xs[i]-(step/2 if i>0 else OFF); s1=xs[j]+(step/2 if j<len(top)-1 else OFF)
        t=top[i]; ok=t-max(raw[i:j+1])>0.03 and t-min(raw[i:j+1])<0.8
        if ok: segs.append((s0,s1,t))
        i=j+1
    for s0,s1,t in segs:
        zb=min(gmin-0.4,t-0.3)
        p0=a+d*s0; p1=a+d*s1
        o0=p0+n*OFF; o1=p1+n*OFF
        def V(p,z): return bm.verts.new((p.x,p.y,z))
        # front face, cap, ends
        f0b=V(o0,zb);f1b=V(o1,zb);f1t=V(o1,t);f0t=V(o0,t)
        w0t=V(p0-n*0.01,t);w1t=V(p1-n*0.01,t)
        w0b=V(p0-n*0.01,zb);w1b=V(p1-n*0.01,zb)
        bm.faces.new((f0b,f1b,f1t,f0t))
        bm.faces.new((f0t,f1t,w1t,w0t))
        bm.faces.new((w0b,f0b,f0t,w0t))
        bm.faces.new((f1b,w1b,w1t,f1t))
    exp=[t-r for t,r in zip(top,raw)]
    stats.append((E['poly'],round(L,1),len(segs),round(min(exp),2),round(max(exp),2),round(lim,2) if lim<999 else None))
    print('EDGE',stats[-1],flush=True)
me=bpy.data.meshes.new('WM_Stone_foundation_reveal_UNVERIFIED')
bm.normal_update(); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=False
ob=bpy.data.objects.new('WM_Stone_foundation_reveal_UNVERIFIED',me)
coll=bpy.data.objects['TI_Stone_Hall_313028565_lower_UNVERIFIED'].users_collection[0]
coll.objects.link(ob)
# material
mat=bpy.data.materials.get('WM_foundation_concrete_UNVERIFIED') or bpy.data.materials.new('WM_foundation_concrete_UNVERIFIED')
mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=6; nz.inputs['Detail'].default_value=8
nz2=nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=60; nz2.inputs['Detail'].default_value=4
nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(tc.outputs['Object'],nz2.inputs['Vector'])
cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.35; cr.color_ramp.elements[0].color=(0.30,0.295,0.28,1); cr.color_ramp.elements[1].position=0.7; cr.color_ramp.elements[1].color=(0.46,0.45,0.42,1)
nt.links.new(nz.outputs['Fac'],cr.inputs['Fac'])
# splash grime: darker toward bottom of each band (world z rel. local ground unknown -> use generated Z per object is global; use noise only + AO)
ao=nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value=0.4
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=0.6
nt.links.new(cr.outputs['Color'],mx.inputs[6]); nt.links.new(ao.outputs['Color'],mx.inputs[7])
nt.links.new(mx.outputs[2],bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value=0.88
bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.25; bp.inputs['Distance'].default_value=0.003
nt.links.new(nz2.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],bs.inputs['Normal'])
nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
me.materials.append(mat)
print('OBJ',ob.name,len(me.vertices),len(me.polygons),'objs',len(bpy.data.objects),flush=True)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
