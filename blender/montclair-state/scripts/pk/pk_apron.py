# pk: Feliciano wall-base DTM hole (black band at grade, N/W views). Faster rewrite of pj_apron: a BVHTree built only from
# Terrain_LiDAR_DTM_1m polygons near Feliciano replaces scene.ray_cast. Adds PK_Feliciano_foot_apron_UNVERIFIED:
# per gap wall face a stucco skirt (wall bottom -> 0.45 m under the strip) + a mulch planting strip from the wall out to
# 0.3 m past (and 3 cm under) the DTM edge. Mulch bed UNVERIFIED (typical foundation bed, no photo). REVERT=1 deletes it.
import bpy,bmesh,os,sys,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t0=time.time()
REV=os.environ.get('REVERT')=='1'; ON='PK_Feliciano_foot_apron_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m)
if REV:
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
    print('PKA_REVERTED',len(bpy.data.objects)); raise SystemExit(0)
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
ws=[mw@v.co for v in w.data.vertices]
X0=min(v.x for v in ws)-10; X1=max(v.x for v in ws)+10; Y0=min(v.y for v in ws)-10; Y1=max(v.y for v in ws)+10
C=Vector(((X0+X1)/2,(Y0+Y1)/2,0))
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; tv=[tm@v.co for v in T.data.vertices]
ins=[X0<=v.x<=X1 and Y0<=v.y<=Y1 for v in tv]
polys=[list(p.vertices) for p in T.data.polygons if any(ins[i] for i in p.vertices)]
used=sorted({i for p in polys for i in p}); remap={o:n for n,o in enumerate(used)}
bvh=BVHTree.FromPolygons([tv[i] for i in used],[[remap[i] for i in p] for p in polys])
print('PKA bvh polys',len(polys),'t',round(time.time()-t0,1))
D=Vector((0,0,-1))
def dtm(p):
    h=bvh.ray_cast(Vector((p.x,p.y,p.z+6)),D,40)
    return h[0].z if h[0] is not None else None
bm=bmesh.new(); nf=0; widths=[]; nsk=0
for p in w.data.polygons:
    n=(R@p.normal).normalized(); pc=mw@p.center
    if abs(n.z)>0.2: continue
    if Vector((n.x,n.y,0)).dot(Vector((pc.x-C.x,pc.y-C.y,0)))<0: n=-n
    nh=Vector((n.x,n.y,0)).normalized()
    a,b=sorted([mw@w.data.vertices[v].co for v in p.vertices],key=lambda v:v.z)[:2]
    if (a-b).length<0.2 or abs(a.z-b.z)>1.0: continue
    ends=[]
    for v in (a,b):
        d=0.3; z=None
        while d<=6.0:
            z=dtm(v+nh*d)
            if z is not None: break
            d+=0.1
        ends.append((d,z))
    if all(e[1] is not None and e[0]<=0.31 and e[1]>=min(a.z,b.z)-0.15 for e in ends): continue
    if any(e[1] is None for e in ends): continue
    # skip faces that are high up (upper storey wall bottoms, not at grade)
    if min(a.z,b.z)-max(ends[0][1],ends[1][1])>2.5: continue
    nf+=1; widths+=[e[0] for e in ends]
    za=ends[0][1]; zb=ends[1][1]
    ia=Vector((a.x,a.y,za-0.04))+nh*0.01; ib=Vector((b.x,b.y,zb-0.04))+nh*0.01
    oa=Vector((a.x,a.y,za-0.03))+nh*(ends[0][0]+0.3); ob_=Vector((b.x,b.y,zb-0.03))+nh*(ends[1][0]+0.3)
    f=bm.faces.new([bm.verts.new(q) for q in (ia,ib,ob_,oa)]); f.material_index=1
    if a.z>za-0.45 or b.z>zb-0.45:
        nsk+=1
        f=bm.faces.new([bm.verts.new(q) for q in (Vector((a.x,a.y,za-0.45))+nh*0.005,Vector((b.x,b.y,zb-0.45))+nh*0.005,Vector((b.x,b.y,b.z+0.02))+nh*0.005,Vector((a.x,a.y,a.z+0.02))+nh*0.005)]); f.material_index=0
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
for f in bm.faces:
    if f.normal.z<0 and f.material_index==1: f.normal_flip()
me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED'])
mn=sorted([m.name for m in bpy.data.materials if 'mulch' in m.name.lower()],key=len)
print('PKA mulch mats',mn[:8])
me.materials.append(bpy.data.materials[mn[0]] if mn else bpy.data.materials['North_Feliciano_caststone_base'])
o=bpy.data.objects.new(ON,me); w.users_collection[0].objects.link(o)
o['UNVERIFIED']='fills a DTM hole along the Feliciano wall base: stucco skirt + mulch planting strip, no photo'
print('PKA faces',nf,'skirts',nsk,'polys',len(me.polygons),'max width',round(max(widths),2) if widths else None,'mat',me.materials[1].name,'t',round(time.time()-t0,1))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PKA_DONE',len(bpy.data.objects))
