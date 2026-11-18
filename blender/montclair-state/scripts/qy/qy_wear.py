# qy (Nov 3 2026 ~3:40 AM ET, MAIN, day 7 Richardson/W lawn). ALL UNVERIFIED, reversible: REVERT=1.
# Darker foot-traffic wear at walk junctions: where OSM footway/path/pedestrian ways meet in the box x -60..180 / y 218..352,
# a 2.4 m-radius draped decal (8 mm over the top-most walk/ground surface, no shadows) with a noisy radial grime alpha.
import bpy, bmesh, os, json, math
from mathutils import Vector
COL='QY_walk_junction_wear_UNVERIFIED'; MN='QY_walk_junction_wear_UNVERIFIED'
def revert():
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('QY_wear') and m.users==0]: bpy.data.meshes.remove(me)
    m=bpy.data.materials.get(MN)
    if m and m.users==0: bpy.data.materials.remove(m)
    print('QYW reverted')
revert()
if os.environ.get('REVERT')=='1':
    if os.environ.get('QYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
X0,X1,Y0,Y1=-60,180,218,352
D=json.load(open('data/scene_data.json'))
ways=[[Vector((p[0],p[1])) for p in f['pts']] for f in D['features'] if f.get('tags',{}).get('highway') in ('footway','path','pedestrian','steps') ]
ways=[w for w in ways if any(X0<=p.x<=X1 and Y0<=p.y<=Y1 for p in w)]
def segd(p,a,b):
    ab=b-a; t=max(0,min(1,(p-a).dot(ab)/max(ab.length_squared,1e-9))); return (p-(a+ab*t)).length
J=[]
for i,w in enumerate(ways):
    for p in w:
        if not (X0<=p.x<=X1 and Y0<=p.y<=Y1): continue
        hit=False
        for k,w2 in enumerate(ways):
            if k==i: continue
            if any(segd(p,a,b)<0.6 for a,b in zip(w2,w2[1:])): hit=True; break
        if hit and all((p-q).length>3.0 for q in J): J.append(p)
print('QYW junctions',len(J))
dg=bpy.context.evaluated_depsgraph_get()
names=['Footpaths_OSM','Roads_OSM','Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','QW_DTM_north_edge_ramp_UNVERIFIED','QJ_NE_seam_fill_UNVERIFIED']
for cn in ('QS_Richardson_walks_UNVERIFIED','QW_Richardson_walk_ext_UNVERIFIED','QX_StudentCenter_plaza_paving_UNVERIFIED','QY_plaza_rim_band_UNVERIFIED'):
    c=bpy.data.collections.get(cn)
    if c: names+= [o.name for o in c.all_objects if o.type=='MESH' and 'grass' not in o.name.lower()]
S=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in names if n in bpy.data.objects]
def gz(x,y):
    b=None
    for e,mw in S:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z; b=z if b is None or z>b else b
    return b
m=bpy.data.materials.new(MN); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links; N.clear()
out=N.new('ShaderNodeOutputMaterial'); bs=N.new('ShaderNodeBsdfPrincipled'); L.new(bs.outputs[0],out.inputs[0])
bs.inputs['Base Color'].default_value=(0.035,0.03,0.024,1); bs.inputs['Roughness'].default_value=0.7
at=N.new('ShaderNodeAttribute'); at.attribute_name='qy_w'; tc=N.new('ShaderNodeTexCoord')
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.6; nz.inputs['Detail'].default_value=10; nz.inputs['Roughness'].default_value=0.65
L.new(tc.outputs['Object'],nz.inputs['Vector'])
mr=N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.30; mr.inputs['From Max'].default_value=0.60; L.new(nz.outputs['Fac'],mr.inputs['Value'])
m1=N.new('ShaderNodeMath'); m1.operation='MULTIPLY'; L.new(at.outputs['Fac'],m1.inputs[0]); L.new(mr.outputs[0],m1.inputs[1])
m2=N.new('ShaderNodeMath'); m2.operation='MULTIPLY'; m2.inputs[1].default_value=0.85; L.new(m1.outputs[0],m2.inputs[0]); L.new(m2.outputs[0],bs.inputs['Alpha'])
try: m.blend_method='HASHED'
except Exception: pass
col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
R=2.4; NR=8; NS=28; bm=bmesh.new(); w=bm.verts.layers.float.new('qy_w'); nd=0
for c in J:
    z0=gz(c.x,c.y)
    if z0 is None: continue
    ring=[]
    cv=bm.verts.new((c.x,c.y,z0+0.008)); cv[w]=1.0
    for r in range(1,NR+1):
        rr=R*r/NR; row=[]
        for s in range(NS):
            a=2*math.pi*s/NS; x=c.x+rr*math.cos(a); y=c.y+rr*math.sin(a); z=gz(x,y)
            v=bm.verts.new((x,y,(z if z is not None else z0)+0.008)); t=rr/R; v[w]=max(0.0,1-t*t) ; row.append(v)
        ring.append(row)
    for s in range(NS): bm.faces.new((cv,ring[0][s],ring[0][(s+1)%NS]))
    for r in range(NR-1):
        for s in range(NS): bm.faces.new((ring[r][s],ring[r+1][s],ring[r+1][(s+1)%NS],ring[r][(s+1)%NS]))
    nd+=1
me=bpy.data.meshes.new('QY_wear_junctions'); bm.to_mesh(me); bm.free()
o=bpy.data.objects.new('QY_walk_junction_wear_decals_UNVERIFIED',me); col.objects.link(o); me.materials.append(m)
o.visible_shadow=False
print('QYW decals',nd,'faces',len(me.polygons))
if os.environ.get('QYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
