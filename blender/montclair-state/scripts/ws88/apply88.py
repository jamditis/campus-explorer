# ws88: bend "Plaza long arched wall" (Cole arcade) into a quarter-circle arc (Joe 9:20/9:55/9:56 AM Nov 12: arcade
# follows the curved steps, quarter circle from the gazebo to Cole's wing, convex toward the road/SW) and move the
# WS87 statues to the INNER (concave, terrace) side. Endpoints kept at the LiDAR-measured line ends; curvature UNVERIFIED.
import bpy,math,os,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
W=[o for o in bpy.data.objects if o.name.startswith('Plaza long arched wall')][0]
print('A88 wall',W.name,'users',W.data.users,'mods',[m.type for m in W.modifiers],'parent',W.parent,'children',[c.name for c in W.children])
D=bpy.data.objects['COLE_plaza_deck_bs']
De=D.evaluated_get(dg); me=De.to_mesh()
bvh=BVHTree.FromPolygons([De.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); De.to_mesh_clear()
def dz(x,y):
    r=bvh.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))
    return r[0].z if r[0] else None
if W.data.users>1: W.data=W.data.copy()
Mw=W.matrix_world; Mi=Mw.inverted()
import bmesh
A0=Vector((-182.8,-73.9)); B0=Vector((-173.1,-95.2)); d=(B0-A0).normalized()
bm=bmesh.new(); bm.from_mesh(W.data); bm.transform(Mw)
us0=[(v.co.xy-A0).dot(d) for v in bm.verts]; k=min(us0)+0.4
while k<max(us0):
    g=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=g,dist=0.0005,plane_co=Vector((A0.x,A0.y,0))+Vector((d.x,d.y,0))*k,plane_no=Vector((d.x,d.y,0)))
    k+=0.4
bm.transform(Mi); bm.to_mesh(W.data); bm.free(); print('A88 bisected verts',len(W.data.vertices))
P=[Mw@v.co for v in W.data.vertices]
A0=Vector((-182.8,-73.9)); B0=Vector((-173.1,-95.2)); d=(B0-A0).normalized()
e=Vector((-d.y,d.x)); e=e if e.x>0 else -e
us=[(p.xy-A0).dot(d) for p in P]; tmin,tmax=min(us),max(us); L=tmax-tmin
phi=math.radians(float(os.environ.get('PHI','45'))); r=L/(2*math.sin(phi))
M=A0+d*(tmin+L/2); C=M+e*(r*math.cos(phi))
print('A88 L',round(L,2),'r',round(r,2),'sag',round(r*(1-math.cos(phi)),2),'C',tuple(round(c,2) for c in C))
zmin=min(p.z for p in P); nb=0
newP=[]
for p,u in zip(P,us):
    w=(p.xy-A0).dot(e)
    a=-phi+2*phi*(u-tmin)/L
    q=C+(r-w)*(-e*math.cos(a)+d*math.sin(a))
    z0=dz(p.x,p.y); z1=dz(q.x,q.y)
    z=p.z+((z1-z0) if (z0 is not None and z1 is not None) else 0)
    if p.z<zmin+0.08 and z1 is not None: z=min(z,z1-0.03); nb+=1
    newP.append(Vector((q.x,q.y,z)))
for v,q in zip(W.data.vertices,newP): v.co=Mi@q
W.data.update()
W.name='Plaza long arched wall ARC_ws88_JOE20261112_quartercircle_UNVERIFIED_radius'
print('A88 base verts seated',nb,'of',len(P))
# statues to the inner side
st=sorted([o for o in bpy.data.objects if o.name.startswith('WS87_Cole_terrace_statue')],key=lambda o:o.name)
random.seed(88)
spots=[(0.18,1.5),(0.32,2.6),(0.46,1.3),(0.60,2.2),(0.75,1.6)]
for o,(f,off) in zip(st,spots):
    a=-phi+2*phi*f; rad=(-e*math.cos(a)+d*math.sin(a))
    q=C+(r-0.6-off)*rad          # wall half-thickness ~0.3 + clearance
    z=dz(q.x,q.y) or o.location.z
    tang=Vector((rad.y,-rad.x))
    o.location=(q.x,q.y,z-0.01)
    o.rotation_euler=(0,0,math.atan2(tang.y,tang.x)-math.pi/2+random.choice((0,math.pi))+random.uniform(-0.5,0.5))
    o.name=o.name.replace('WS87_Cole_terrace_statue','WS88_Cole_statue_INNER_arc') if 'WS88' not in o.name else o.name
    print('A88 statue',o.name[:28],round(q.x,2),round(q.y,2),round(z,2))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A88 saved')
