# ws170: UNIFY #74 part 1 — overhead utility line on the S verge of Normal Ave W (x -349.5 .. -271).
# Evidence: 2023 NJ LiDAR class-1 wire returns (prep/ws163_lot3S/las163.npy) along y = -260 + (x+331.7)*(-0.25):
#  top conductor 15.4-15.6 m above the class-2 DTM at x -317.5 and -271 (local maxima = attachment points), sagging to
#  ~14.1 m / ~12.6-13.0 m mid-span; second wire level 13.7-14.1 m; lowest 12.6-13.0 m. Cross-section: top wire d -0.5 m, lower d +0.4 m.
#  2020 NJOGIS ortho: pole shadow/top on the road at x ~-318 (consistent). W pole at x -349.5 = scene edge (UNVERIFIED +-3 m).
# Built: 3 wood poles (60 ft class, ~16 m out of ground), 2.4 m crossarm with 3 primaries, neutral 1.4 m below, one comm cable at 12.8 m.
# Pole heights / crossarm / wire count = typical PSE&G-style distribution build (UNVERIFIED); positions + wire heights = LiDAR.
import bpy, bmesh, math, numpy as np
from mathutils import Vector, Matrix
OB=bpy.data.objects
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/dtm163.npy')[0]; X0,Y0,R=-350.0,-290.0,0.5
def gz(x,y):
    i=int((x-X0)/R); j=int((y-Y0)/R); sub=D[max(j-3,0):j+4,max(i-3,0):i+4]; return float(np.nanmedian(sub))
for o in [o for o in OB if o.name.startswith('WS170_util')]: OB.remove(o)
col=bpy.data.collections.get('WS170_Normal_Ave_W_utility_line')
if col is None:
    col=bpy.data.collections.new('WS170_Normal_Ave_W_utility_line'); bpy.context.scene.collection.children.link(col)
def mat(name,rgb,rough,metal=0.0):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*rgb,1); return m
MW=mat('WS170_pole_wood_weathered',(0.055,0.045,0.035),0.85)
MA=mat('WS170_crossarm_wood',(0.10,0.08,0.06),0.8)
MI=mat('WS170_insulator_grey_polymer',(0.45,0.47,0.48),0.5)
MC=mat('WS170_conductor_aluminium_dull',(0.12,0.12,0.115),0.75,0.3)
MK=mat('WS170_cable_black_jacket',(0.03,0.03,0.03),0.6)
def line_y(x): return -260.0+(x+331.7)*(-0.25)
PX=[-347.0,-317.5,-271.0]
PY={-347.0:-256.6}  # W pole: wire line meets the curb here -> set 0.45 m behind the curb back (UNVERIFIED, scene edge)
dirv=Vector((1,-0.25,0)).normalized(); perp=Vector((-dirv.y,dirv.x,0))  # perp points N-ish
TOP=15.9; ARM=15.15
poles=[]
for k,x in enumerate(PX):
    y=PY.get(x,line_y(x)); z0=gz(x,y); poles.append((x,y,z0))
    bm=bmesh.new()
    bmesh.ops.create_cone(bm,cap_ends=True,segments=14,radius1=0.16,radius2=0.11,depth=TOP+0.3)
    bmesh.ops.translate(bm,verts=bm.verts,vec=(0,0,(TOP+0.3)/2-0.3))
    me=bpy.data.meshes.new('WS170_util_pole_%d'%k); bm.to_mesh(me); bm.free(); me.materials.append(MW)
    for p in me.polygons: p.use_smooth=True
    o=OB.new('WS170_util_pole_%d_LiDAR_x%.1f'%(k,x),me); o.location=(x,y,z0); col.objects.link(o)
    # crossarm (along perp), braces, insulators, neutral bracket, comm bracket
    bm=bmesh.new(); ang=math.atan2(perp.y,perp.x)
    def box(cx,cy,cz,sx,sy,sz,rot=ang):
        r=bmesh.ops.create_cube(bm,size=1.0)['verts']
        bmesh.ops.scale(bm,verts=r,vec=(sx,sy,sz)); bmesh.ops.rotate(bm,verts=r,matrix=Matrix.Rotation(rot,3,'Z')); bmesh.ops.translate(bm,verts=r,vec=(cx,cy,cz))
    box(0,0,ARM,2.44,0.095,0.12)
    for s in (-1,1):  # flat steel braces approximated as thin boxes
        r=bmesh.ops.create_cube(bm,size=1.0)['verts']; bmesh.ops.scale(bm,verts=r,vec=(0.75,0.02,0.04))
        bmesh.ops.rotate(bm,verts=r,matrix=Matrix.Rotation(s*0.6,3,'Y')); bmesh.ops.rotate(bm,verts=r,matrix=Matrix.Rotation(ang,3,'Z'))
        bmesh.ops.translate(bm,verts=r,vec=(perp*(s*0.33)+Vector((0,0,ARM-0.25)))[:])
    box(0,0,ARM-1.4,0.25,0.08,0.08)   # neutral rack
    box(0,0,12.8,0.30,0.06,0.06)      # comm clamp
    me=bpy.data.meshes.new('WS170_util_arm_%d'%k); bm.to_mesh(me); bm.free(); me.materials.append(MA)
    o=OB.new('WS170_util_crossarm_%d'%k,me); o.location=(x,y,z0); col.objects.link(o)
    bm=bmesh.new()
    for t in (-1.05,0.0,1.05):
        r=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.06,radius2=0.04,depth=0.28)['verts']
        bmesh.ops.translate(bm,verts=r,vec=(perp*t+Vector((0,0,ARM+0.2+(0.12 if t==0 else 0))))[:])
    me=bpy.data.meshes.new('WS170_util_ins_%d'%k); bm.to_mesh(me); bm.free(); me.materials.append(MI)
    o=OB.new('WS170_util_insulators_%d'%k,me); o.location=(x,y,z0); col.objects.link(o)
# wires: catenary-ish parabola between attachments
WIRES=[(-1.05,ARM+0.34,0.0125,MC,'A'),(0.0,ARM+0.46,0.0125,MC,'B'),(1.05,ARM+0.34,0.0125,MC,'C'),
       (0.12,ARM-1.4,0.011,MC,'N'),(-0.15,12.8,0.02,MK,'COM')]
SAG={0:1.4,1:1.5}
for (t,h,rad,m,tag) in WIRES:
    cu=bpy.data.curves.new('WS170_util_wire_'+tag,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=rad; cu.bevel_resolution=1
    sp=cu.splines.new('POLY'); pts=[]
    for k in range(len(poles)-1):
        (xa,ya,za),(xb,yb,zb)=poles[k],poles[k+1]
        A=Vector((xa,ya,za+h))+perp*t; B=Vector((xb,yb,zb+h))+perp*t
        sag=SAG[k]*(0.85 if tag=='COM' else 1.0)
        n=24
        for i in range(n+(1 if k==len(poles)-2 else 0)):
            u=i/n; p=A.lerp(B,u); p.z-=4*sag*u*(1-u); pts.append(p)
    sp.points.add(len(pts)-1)
    for i,p in enumerate(pts): sp.points[i].co=(p.x,p.y,p.z,1)
    cu.materials.append(m)
    o=OB.new('WS170_util_wire_'+tag,cu); col.objects.link(o)
print('UTIL170 poles',[(round(x,1),round(y,2),round(z,2)) for x,y,z in poles],'wires',len(WIRES),flush=True)
