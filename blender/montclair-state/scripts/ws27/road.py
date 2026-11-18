"""ws27: College Ave carriageway (6.5 m), concrete curbs + gutter pans, 2 brick crosswalk bands, by Kasser / Red Hawk end, MAIN x>-252.
Sources: OSM way 232844571 (centreline, oneway); NJ 2020 natural ortho (maps.nj.gov Orthos_Natural_2020_NJ_WM, data/ws27/nj2020_zoom.jpg):
width ~6.5 m from luminance profiles at x-235/-225 and y-110/-130/-150; north stretch shifted +1.5 m north to match the ortho.
Curb height/profile, gutter width and crosswalk band width UNVERIFIED."""
import bpy, bmesh, math, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene
w=json.load(open(R+'/data/ws23/osm_redhawk_ways.json'))
pts=[p for p in w['232844571']['pts']]
# keep from (-258.9,-55.2) eastward/south
i0=[i for i,p in enumerate(pts) if p[0]==-258.9][0]
P=list(reversed(pts[:i0+1]))  # from west (-258.9,-55.2) ... to (-217,-159.9)
def shift(p):
    x,y=p
    if y>-70 and x<-211: return (x,y+1.5)
    if y>-72: return (x,y+1.1)
    if y>-76: return (x,y+0.5)
    return (x,y)
P=[shift(p) for p in P]
# Chaikin smoothing keep ends
for it in range(3):
    Q=[P[0]]
    for a,b in zip(P[:-1],P[1:]):
        Q.append((0.75*a[0]+0.25*b[0],0.75*a[1]+0.25*b[1])); Q.append((0.25*a[0]+0.75*b[0],0.25*a[1]+0.75*b[1]))
    Q.append(P[-1]); P=Q
# resample every 0.5 m
C=[Vector(P[0])]; acc=0
pv=[Vector(p) for p in P]
seg=[]
L=sum((b-a).length for a,b in zip(pv[:-1],pv[1:]))
n=int(L/0.5)
def at(s):
    for a,b in zip(pv[:-1],pv[1:]):
        l=(b-a).length
        if s<=l: return a.lerp(b,s/l)
        s-=l
    return pv[-1]
C=[at(L*k/n) for k in range(n+1)]
# clip to MAIN terrain x>-249
C=[c for c in C if c.x>-249.3]
T=[]
for k in range(len(C)):
    a=C[max(0,k-1)]; b=C[min(len(C)-1,k+1)]; t=(b-a).normalized(); T.append(t)
N=[Vector((-t.y,t.x)) for t in T]  # left normal
print('centre pts',len(C),'len %.1f'%(0.5*len(C)))
dg=bpy.context.evaluated_depsgraph_get()
def bvh(name):
    o=bpy.data.objects[name]; ev=o.evaluated_get(dg); me=ev.to_mesh()
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); ev.to_mesh_clear(); return t
TER=bvh('Terrain_LiDAR_DTM_1m')
def gz(x,y):
    h=TER.ray_cast(Vector((x,y,170)),Vector((0,0,-1)))
    return h[0].z if h[0] else None
# ---- remove Roads_OSM faces under the new road
ro=bpy.data.objects['Roads_OSM']; me=ro.data
bm=bmesh.new(); bm.from_mesh(me)
cl=[(c.x,c.y) for c in C]
def dist(x,y):
    return min((x-a)**2+(y-b)**2 for a,b in cl[::2])**0.5
dele=[]
for f in bm.faces:
    cc=ro.matrix_world@f.calc_center_median()
    if cc.x>-252 and -163<cc.y<-48 and (dist(cc.x,cc.y)<5.0 or (cc.y>-75 and cc.x<-212 and dist(cc.x,cc.y)<6.5)): dele.append(f)
print('Roads_OSM faces removed',len(dele),'of',len(bm.faces))
bmesh.ops.delete(bm,geom=dele,context='FACES'); bm.to_mesh(me); bm.free()
# ---- materials
def nm(name):
    m=bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(name); m.use_nodes=True; return m,m.node_tree
def noisy(name,base,var,rough,scale,bump,bscale=180):
    m,nt=nm(name); b=nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value=rough
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=8
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB'); r=ramp.color_ramp
    r.elements[0].color=[c*(1-var) for c in base]+[1]; r.elements[1].color=[min(1,c*(1+var)) for c in base]+[1]
    nt.links.new(nz.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],b.inputs['Base Color'])
    n2=nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=bscale; n2.inputs['Detail'].default_value=4
    nt.links.new(tc.outputs['Object'],n2.inputs['Vector'])
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=bump; bp.inputs['Distance'].default_value=0.004
    nt.links.new(n2.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
M_as=noisy('WS27_CollegeAve_asphalt_2020ortho',(0.10,0.10,0.105),0.25,0.88,0.9,0.45)
nt=M_as.node_tree; b=nt.nodes['Principled BSDF']; ramp=[n for n in nt.nodes if n.type=='VALTORGB'][0]
tc=[n for n in nt.nodes if n.type=='TEX_COORD'][0]
# aggregate speckle + sparse sealed cracks + broad patching (all procedural, UNVERIFIED pattern)
sp=nt.nodes.new('ShaderNodeTexNoise'); sp.inputs['Scale'].default_value=900; sp.inputs['Detail'].default_value=2
nt.links.new(tc.outputs['Object'],sp.inputs['Vector'])
spr=nt.nodes.new('ShaderNodeMapRange'); spr.inputs['From Min'].default_value=0.55; spr.inputs['From Max'].default_value=0.75
nt.links.new(sp.outputs['Fac'],spr.inputs['Value'])
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='LIGHTEN'
nt.links.new(spr.outputs['Result'],mx.inputs['Factor']); nt.links.new(ramp.outputs['Color'],mx.inputs['A']); mx.inputs['B'].default_value=(0.2,0.195,0.19,1)
vo=nt.nodes.new('ShaderNodeTexVoronoi'); vo.feature='DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value=0.22
wn=nt.nodes.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value=0.6; wn.inputs['Detail'].default_value=3
vm=nt.nodes.new('ShaderNodeVectorMath'); vm.operation='ADD'
sc_=nt.nodes.new('ShaderNodeVectorMath'); sc_.operation='SCALE'; sc_.inputs['Scale'].default_value=1.6
nt.links.new(wn.outputs['Color'],sc_.inputs[0]); nt.links.new(tc.outputs['Object'],vm.inputs[0]); nt.links.new(sc_.outputs['Vector'],vm.inputs[1])
nt.links.new(tc.outputs['Object'],wn.inputs['Vector']); nt.links.new(vm.outputs['Vector'],vo.inputs['Vector'])
cr=nt.nodes.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value=0.0; cr.inputs['From Max'].default_value=0.011; cr.inputs['To Min'].default_value=0.6; cr.inputs['To Max'].default_value=0.0
nt.links.new(vo.outputs['Distance'],cr.inputs['Value'])
mx2=nt.nodes.new('ShaderNodeMix'); mx2.data_type='RGBA'
nt.links.new(cr.outputs['Result'],mx2.inputs['Factor']); nt.links.new(mx.outputs['Result'],mx2.inputs['A']); mx2.inputs['B'].default_value=(0.05,0.05,0.052,1)
nt.links.new(mx2.outputs['Result'],b.inputs['Base Color'])
rr=nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value=0.88; rr.inputs['To Max'].default_value=0.6
nt.links.new(cr.outputs['Result'],rr.inputs['Value']); nt.links.new(rr.outputs['Result'],b.inputs['Roughness'])
M_gu=noisy('WS27_gutter_pan_concrete_UNVERIFIED',(0.30,0.29,0.27),0.18,0.75,6,0.25)
M_cu=noisy('WS27_curb_concrete_UNVERIFIED',(0.42,0.41,0.385),0.12,0.7,8,0.2)
# brick crosswalk
m,nt=nm('WS27_brick_crosswalk_2020ortho'); b=nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value=0.85
tc=nt.nodes.new('ShaderNodeTexCoord'); br=nt.nodes.new('ShaderNodeTexBrick')
br.inputs['Scale'].default_value=1.0; br.inputs['Brick Width'].default_value=0.2; br.inputs['Row Height'].default_value=0.1; br.inputs['Mortar Size'].default_value=0.008
br.inputs['Color1'].default_value=(0.30,0.095,0.055,1); br.inputs['Color2'].default_value=(0.24,0.08,0.05,1); br.inputs['Mortar'].default_value=(0.25,0.23,0.21,1)
br.offset=0.5; nt.links.new(tc.outputs['Object'],br.inputs['Vector']); nt.links.new(br.outputs['Color'],b.inputs['Base Color'])
bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.35; bp.inputs['Distance'].default_value=0.005; bp.invert=True
nt.links.new(br.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
M_br=m
col=bpy.data.collections.get('WS27_CollegeAve_Kasser_carriageway_curbs_20261110ws27') or bpy.data.collections.new('WS27_CollegeAve_Kasser_carriageway_curbs_20261110ws27')
if col.name not in sc.collection.children: sc.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o)
HW=3.25
# chainage of crosswalks (ortho brick bands near y-96 and y-139)
def chain_near(y):
    return min(range(len(C)),key=lambda k:abs(C[k].y-y))
XW=[chain_near(-96.5),chain_near(-139.5)]
print('crosswalk idx',XW,[tuple(round(v,1) for v in C[k]) for k in XW])
# ---- carriageway
offs=[-HW,-HW+0.40,-1.6,0,1.6,HW-0.40,HW]
bm=bmesh.new(); rows=[]
basez=[]
for k,c in enumerate(C):
    zs=[gz(*(c+N[k]*o)) for o in offs]
    zc=[z for z in zs if z is not None]; zm=sum(zc)/len(zc)
    zs=[z if z is not None else zm for z in zs]
    # crown: centre +2 cm
    row=[]
    for j,o in enumerate(offs):
        q=c+N[k]*o; dz=0.035+0.02*(1-abs(o)/HW)
        row.append(bm.verts.new((q.x,q.y,zs[j]+dz)))
    rows.append(row); basez.append((zs[0]+0.035,zs[-1]+0.035))
# smooth along length
for it in range(2):
    for j in range(len(offs)):
        zz=[rows[k][j].co.z for k in range(len(rows))]
        for k in range(1,len(rows)-1): rows[k][j].co.z=(zz[k-1]+2*zz[k]+zz[k+1])/4
uv=[]
for k in range(len(rows)-1):
    for j in range(len(offs)-1):
        f=bm.faces.new((rows[k][j],rows[k][j+1],rows[k+1][j+1],rows[k+1][j]))
        mi=1 if j in (0,len(offs)-2) else 0
        if any(abs(k-x)<=7 for x in XW) and mi==0: mi=2
        f.material_index=mi
EZ=[(r[0].co.z,r[-1].co.z) for r in rows]
me=bpy.data.meshes.new('WS27_CollegeAve_carriageway'); bm.to_mesh(me); bm.free()
o=bpy.data.objects.new('WS27_CollegeAve_carriageway_2020ortho',me); col.objects.link(o)
for m_ in (M_as,M_gu,M_br): me.materials.append(m_)
for p in me.polygons: p.use_smooth=True
# ---- curbs: profile (lateral from edge outward, dz relative)
def curb(side,name):
    bm=bmesh.new(); rows2=[]
    for k,c in enumerate(C):
        zb=EZ[k][0 if side<0 else 1]
        out=c+N[k]*(side*(HW+0.45)); zg=gz(out.x,out.y) or zb
        dk=min(abs(k-x) for x in XW); f=0.0 if dk<=7 else min(1.0,(dk-7)/5.0)  # flush curb ramps at the brick crosswalks
        h=0.02+0.13*f
        prof=[(0.0,zb-0.01),(0.0,zb+h),(0.03,zb+h+0.015*f),(0.15,zb+h+0.015*f),(0.17,zb+h+0.005*f),(0.45,max(zg-0.02,zb-0.05))]
        row=[]
        for (l,z) in prof:
            q=c+N[k]*(side*(HW+l)); row.append(bm.verts.new((q.x,q.y,z)))
        rows2.append(row)
    for k in range(len(rows2)-1):
        for j in range(len(rows2[0])-1):
            vs=(rows2[k][j],rows2[k][j+1],rows2[k+1][j+1],rows2[k+1][j])
            bm.faces.new(vs if side>0 else vs[::-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); me.materials.append(M_cu)
curb(-1,'WS27_CollegeAve_curb_right_UNVERIFIED')
curb(+1,'WS27_CollegeAve_curb_left_UNVERIFIED')
print('built',len(C))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
