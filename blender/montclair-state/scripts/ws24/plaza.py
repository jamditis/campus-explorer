"""ws24: asphalt plaza/turnaround in front of the RED HAWK COUNTRY wall (Annex west), island curb,
row of concrete flower planters + 2 access plates. Sources: Joe's Nov 8 photo (asphalt + planters,
his photos override older data per Joe Nov 10) + USGS NAIP clip data/ws24/naip_grid.png (extent).
Counts/sizes of planters UNVERIFIED (from photo by eye)."""
import bpy, bmesh, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(24)
sc=bpy.context.scene
P=[(-97.3,303.5),(-97.3,341),(-98.5,346),(-101,353),(-102,360),(-117,360),(-116,353),(-119,348),(-125,342),(-138,339.5),(-138,336.5),(-128,335.5),(-120,333.5),(-115,330),(-112.8,325),(-112.6,319),(-113.5,314),(-112,309),(-111.5,304),(-108,302.5),(-101,302.8)]
ISL=[(-138,336.5),(-128,335.5),(-120,333.5),(-115,330),(-112.8,325),(-112.6,319),(-113.5,314),(-117,312.2)]
def inside(x,y,poly=P):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
# ground BVH
dg=bpy.context.evaluated_depsgraph_get()
gro=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('Context_skirt') or o.name.startswith('SA_ground_lower_patch') or o.name.startswith('SB_footway') or o.name.startswith('SB_pedestrian') or o.name.startswith('SC_soil_edge'))]
trees=[]
for o in gro:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-145 or min(v.x for v in bb)>-90 or max(v.y for v in bb)<295 or min(v.y for v in bb)>365: continue
    ev=o.evaluated_get(dg); me=ev.to_mesh()
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    trees.append((o.name,BVHTree.FromBMesh(bm))); bm.free(); ev.to_mesh_clear()
print('ground objs',[t[0] for t in trees])
def gz(x,y):
    best=None
    for n,t in trees:
        h=t.ray_cast(Vector((x,y,170)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
    return best
col=bpy.data.collections.new('WS24_AnnexWest_asphalt_plaza_planters_20261110ws24'); sc.collection.children.link(col)
def mat(name,col_lin,rough,noise=0.0,bump=0.0,scale=8.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value=rough
    if noise>0:
        tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=8
        nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB'); r=ramp.color_ramp
        r.elements[0].color=[c*(1-noise) for c in col_lin]+[1]; r.elements[1].color=[min(1,c*(1+noise)) for c in col_lin]+[1]
        nt.links.new(nz.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],b.inputs['Base Color'])
        if bump>0:
            n2=nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=220; n2.inputs['Detail'].default_value=4
            nt.links.new(tc.outputs['Object'],n2.inputs['Vector'])
            bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=bump; bp.inputs['Distance'].default_value=0.004
            nt.links.new(n2.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    else:
        b.inputs['Base Color'].default_value=list(col_lin)+[1]
    return m
M_asph=mat('WS24_asphalt_weathered_JoePhoto',(0.080,0.080,0.084),0.9,noise=0.22,bump=0.4,scale=1.2)
M_curb=mat('WS24_curb_concrete_UNVERIFIED',(0.42,0.41,0.39),0.8,noise=0.1,bump=0.2,scale=6)
M_plant=mat('WS24_planter_cast_concrete_grey_JoePhoto',(0.36,0.36,0.36),0.75,noise=0.12,bump=0.25,scale=10)
M_soil=mat('WS24_planter_soil',(0.05,0.035,0.025),0.95)
M_leaf=mat('WS24_planter_foliage_green',(0.04,0.12,0.03),0.6,noise=0.35,scale=14)
M_fr=mat('WS24_flower_red',(0.55,0.03,0.05),0.5); M_fm=mat('WS24_flower_magenta',(0.42,0.04,0.30),0.5); M_fp=mat('WS24_flower_pink',(0.7,0.25,0.4),0.5)
M_plate=mat('WS24_access_plate_galv',(0.3,0.29,0.27),0.55,noise=0.2,scale=30); M_plate.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0.6
# ---- asphalt surface: densify outline, fill, subdivide, drape
bm=bmesh.new(); vs=[]
for i in range(len(P)):
    a=Vector(P[i]); b=Vector(P[(i+1)%len(P)]); n=max(1,int((b-a).length/0.6))
    for k in range(n): q=a.lerp(b,k/n); vs.append(bm.verts.new((q.x,q.y,0)))
for i in range(len(vs)): bm.edges.new((vs[i],vs[(i+1)%len(vs)]))
bmesh.ops.triangle_fill(bm,use_beauty=True,use_dissolve=False,edges=bm.edges[:])
for it in range(4):
    long=[e for e in bm.edges if e.calc_length()>1.0]
    if not long: break
    bmesh.ops.subdivide_edges(bm,edges=long,cuts=1,use_grid_fill=False)
    bmesh.ops.triangulate(bm,faces=bm.faces[:])
bmesh.ops.beautify_fill(bm,faces=bm.faces[:],edges=bm.edges[:])
miss=0
for v in bm.verts:
    z=gz(v.co.x,v.co.y)
    if z is None: z=140.3; miss+=1
    v.co.z=z+0.035
for it in range(3):
    nz={v:sum(e.other_vert(v).co.z for e in v.link_edges)/len(v.link_edges) for v in bm.verts if v.link_edges}
    for v,z in nz.items():
        if not v.is_boundary: v.co.z=max(v.co.z-0.02, 0.5*v.co.z+0.5*z)
print('asphalt verts',len(bm.verts),'faces',len(bm.faces),'miss',miss)
me=bpy.data.meshes.new('WS24_asphalt'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new('WS24 Annex west asphalt plaza (NAIP extent + Joe photo Nov 8)',me); col.objects.link(ob); me.materials.append(M_asph)
# ---- island curb (15 cm reveal, 15 cm wide), outside face on plaza side
bm=bmesh.new(); pts=[]
for i in range(len(ISL)-1):
    a=Vector(ISL[i]); b=Vector(ISL[i+1]); n=max(1,int((b-a).length/0.5))
    for k in range(n): pts.append(a.lerp(b,k/n))
pts.append(Vector(ISL[-1]))
prev=None
for i,p in enumerate(pts):
    d=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized(); nrm=Vector((-d.y,d.x))
    # island is on the left/west side when walking ISL order? test which side is inside plaza
    t=p+nrm*0.5
    if inside(t.x,t.y): nrm=-nrm   # nrm points into island
    z=(gz(p.x,p.y) or 140.3)+0.035
    o=p-nrm*0.02; i_=p+nrm*0.15
    ring=[bm.verts.new((o.x,o.y,z-0.1)),bm.verts.new((o.x,o.y,z+0.15)),bm.verts.new((i_.x,i_.y,z+0.15)),bm.verts.new((i_.x,i_.y,z-0.05))]
    if prev:
        for k in range(3): bm.faces.new((prev[k],prev[k+1],ring[k+1],ring[k]))
    prev=ring
me=bpy.data.meshes.new('WS24_curb'); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new('WS24 turnaround island curb (NAIP light edge; profile UNVERIFIED)',me); col.objects.link(ob); me.materials.append(M_curb)
bev=ob.modifiers.new('bev','BEVEL'); bev.width=0.012; bev.segments=2; bev.limit_method='ANGLE'
# ---- planters: tapered bowl, rim, soil, foliage mound, flower heads
def planter(cx,cy,idx):
    z0=gz(cx,cy) or 140.3; z0+=0.035
    bm=bmesh.new(); N=24
    prof=[(0.26,0.0),(0.30,0.04),(0.40,0.50),(0.44,0.56),(0.44,0.62),(0.39,0.62),(0.37,0.56)]
    rings=[]
    for r,h in prof: rings.append([bm.verts.new((cx+r*math.cos(2*math.pi*k/N),cy+r*math.sin(2*math.pi*k/N),z0+h)) for k in range(N)])
    for a,b in zip(rings,rings[1:]):
        for k in range(N): bm.faces.new((a[k],a[(k+1)%N],b[(k+1)%N],b[k]))
    bm.faces.new(rings[0][::-1])
    me=bpy.data.meshes.new(f'WS24_planter_{idx}'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    o=bpy.data.objects.new(f'WS24 planter {idx:02d} (Joe photo; UNVERIFIED count/size)',me); col.objects.link(o); me.materials.append(M_plant)
    # soil + foliage mound
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=(cx,cy,z0+0.58))
    f=bpy.context.active_object; f.name=f'WS24 planter {idx:02d} foliage'; f.scale=(0.42,0.42,0.30+random.uniform(0,0.12))
    for c in f.users_collection: c.objects.unlink(f)
    col.objects.link(f); f.data.materials.append(M_leaf)
    dsp=f.modifiers.new('d','DISPLACE'); tx=bpy.data.textures.get('WS24_leafnoise') or bpy.data.textures.new('WS24_leafnoise','CLOUDS'); tx.noise_scale=0.12; dsp.texture=tx; dsp.strength=0.12; dsp.texture_coords='GLOBAL'
    for p in f.data.polygons: p.use_smooth=True
    # flower heads
    fm=[M_fr,M_fm,M_fp][idx%3] if idx%4 else M_fr
    bm=bmesh.new()
    for k in range(70):
        a=random.uniform(0,2*math.pi); rr=0.42*math.sqrt(random.random())
        hz=z0+0.58+ (0.30+0.06)*math.sqrt(max(0,1-(rr/0.44)**2)) + random.uniform(0.0,0.10)
        bmesh.ops.create_icosphere(bm,subdivisions=1,radius=random.uniform(0.025,0.045),matrix=__import__('mathutils').Matrix.Translation((cx+rr*math.cos(a),cy+rr*math.sin(a),hz)))
    me=bpy.data.meshes.new(f'WS24_flowers_{idx}'); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(f'WS24 planter {idx:02d} flowers',me); col.objects.link(o); me.materials.append(fm)
ys=[305.4+2.4*i for i in range(9)]
for i,y in enumerate(ys): planter(-99.6+random.uniform(-0.15,0.15) if y>303.6 else -98.9, y, i+1)
# ---- access plates (two, like photo)
for i,(x,y) in enumerate([(-104.5,316.0),(-102.2,326.5)]):
    z=(gz(x,y) or 140.3)+0.038
    bpy.ops.mesh.primitive_plane_add(size=0.6,location=(x,y,z)); p=bpy.context.active_object; p.name=f'WS24 access plate {i+1} (Joe photo; position UNVERIFIED)'
    for c in p.users_collection: c.objects.unlink(p)
    col.objects.link(p); p.data.materials.append(M_plate); p.rotation_euler.z=math.radians(3)
# ---- remove lawn grass points under the asphalt
removed=0
for o in bpy.data.objects:
    if o.type=='MESH' and 'grass' in o.name.lower() and len(o.data.polygons)==0 and o.name!='mi_grass_annex_west_bed_points (ornamental grass stand-in; UNVE'[:0]+o.name and not o.name.startswith('mi_grass_annex_west_bed'):
        mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
        kill=[v for v in bm.verts if inside(*(mw@v.co).xy)]
        if kill:
            removed+=len(kill); print('grass pts',o.name,len(kill)); bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data)
        bm.free()
print('grass removed',removed)
bpy.ops.wm.save_mainfile()
print('SAVED')
