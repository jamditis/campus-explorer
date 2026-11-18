# pj (B): Feliciano N/W/S-west foot: the LiDAR DTM has a hole along the wall base (rays 0.8 m out hit the 4 km context skirt
# ~1.1-1.8 m below) -> black band at grade in the NW view. Adds PJ_Feliciano_foot_apron_UNVERIFIED: per gap wall face a stucco
# skirt from the wall bottom to 0.4 m under the apron and a 0.6 m mulch strip from the wall out to (and 0.3 m under) the DTM edge.
# Mulch bed is UNVERIFIED (typical foundation planting bed, no photo). REVERT=1 deletes the object.
import bpy,bmesh,os,sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PJ_Feliciano_foot_apron_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m)
if REV:
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
    print('PJA_REVERTED',len(bpy.data.objects)); raise SystemExit(0)
s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); D=Vector((0,0,-1))
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
ws=[mw@v.co for v in w.data.vertices]; C=Vector(((min(v.x for v in ws)+max(v.x for v in ws))/2,(min(v.y for v in ws)+max(v.y for v in ws))/2,0))
def dtm(p):
    h=s.ray_cast(dg,Vector((p.x,p.y,p.z+6)),D,distance=40)
    return (h[1].z, h[4].name.startswith('Terrain_LiDAR')) if h[0] else (None,False)
bm=bmesh.new(); nf=0; widths=[]
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
            zz,ok=dtm(v+nh*d)
            if ok: z=zz; break
            d+=0.2
        ends.append((d,z))
    if all(e[1] is not None and e[0]<=0.31 for e in ends): continue   # DTM reaches the wall: no hole
    if any(e[1] is None for e in ends): continue
    nf+=1; widths+= [e[0] for e in ends]
    za=ends[0][1]; zb=ends[1][1]; zmin=min(a.z,b.z,za,zb)
    # mulch strip: inner edge at the wall (just below the DTM-edge height), outer edge 0.3 m past the DTM edge and 3 cm under it
    ia=Vector((a.x,a.y,za-0.04))+nh*0.01; ib=Vector((b.x,b.y,zb-0.04))+nh*0.01
    oa=Vector((a.x,a.y,za-0.03))+nh*(ends[0][0]+0.3); ob_=Vector((b.x,b.y,zb-0.03))+nh*(ends[1][0]+0.3)
    f=bm.faces.new([bm.verts.new(q) for q in (ia,ib,ob_,oa)]); f.material_index=1
    # skirt: wall plane from the wall bottom down to 0.4 m under the strip (only where the wall stops above it)
    if a.z>za-0.04 or b.z>zb-0.04:
        f=bm.faces.new([bm.verts.new(q) for q in (Vector((a.x,a.y,za-0.45)),Vector((b.x,b.y,zb-0.45)),Vector((b.x,b.y,b.z+0.02)),Vector((a.x,a.y,a.z+0.02)))]); f.material_index=0
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED'])
mn=[m.name for m in bpy.data.materials if 'mulch' in m.name.lower()]
print('PJA mulch mats',mn[:8])
me.materials.append(bpy.data.materials[sorted(mn,key=len)[0]] if mn else bpy.data.materials['North_Feliciano_caststone_base'])
o=bpy.data.objects.new(ON,me); w.users_collection[0].objects.link(o)
o['UNVERIFIED']='fills a DTM hole along the Feliciano wall base: stucco skirt + mulch planting strip, no photo'
print('PJA faces',nf,'polys',len(me.polygons),'max width',round(max(widths),2) if widths else None, 'mat',me.materials[1].name)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PJA_DONE',len(bpy.data.objects))
